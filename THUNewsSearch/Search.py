import pymongo as pm
import re
import json
import jieba
import time
from bson import ObjectId
from words_cut import wordsCut
from wordCorrect import correctENG,correctCHN


def jsonStartsWith(trieJson, prefix):
    """
    Returns if there is any word in the trie that starts with the given prefix.
    """
    curNode = trieJson
    for c in prefix:
        if c not in curNode:
            return False
        curNode = curNode[c]
    return True


def jsonGetStartsWith(trieJson, prefix):
    def get_key(pre,node):
        words = []
        if "-1" in node:
            words.append(pre)
        for c in node.keys():
            if c != "-1":
                words.extend(get_key(pre + str(c), node[c]))
        return words
    
    resultWords = []
    if prefix == "":
        return resultWords
    if not jsonStartsWith(trieJson, prefix):
        return resultWords
    curNode = trieJson
    for c in prefix:
        curNode = curNode[c]
    return get_key(prefix,curNode)


class SearchAndRank:
    client = pm.MongoClient('127.0.0.1',27017)
    db = client.test
    collection = db.col

    file1 = open('trieTree.json','r')
    trieJson = json.loads(file1.read())
    file1.close()

    file2 = open('trieTreeFreq.json','r')
    trieFreq = json.loads(file2.read())
    file2.close()


    @classmethod
    def isEnglish(cls,word):
        for c in word:
            if ord(c) > 127 or ord(c) in range(48,58):
                return False
        return True

    @classmethod
    def keywordsSuggest(cls,curInput):
        curInput = curInput.strip().lower()
        words = jsonGetStartsWith(cls.trieJson, curInput)
        word_freq = []
        for word in words:
            word_freq.append([word,cls.trieFreq[word]])
        wordsTop10 = []
        for word,freq in sorted(word_freq,key = lambda word_freq: word_freq[1],reverse=True)[:10]:
            wordsTop10.append(word)
        return wordsTop10

    @classmethod
    def getAbstract(cls, text, queryWords):
        text = text.replace('\n','')
        wordsCount = text.count(queryWords[0])
        parts = text.split(queryWords[0], (wordsCount // 2) + 1)
        if len(parts) <= (wordsCount // 2) + 1:
            position = -1
        position = len(text)-len(parts[-1])-len(queryWords[0])
        startPos = max(position-35, 0)
        endPos = min(position + len(queryWords[0]) + 35, len(text))
        content = text[startPos:endPos]
        return content

    @classmethod
    def correctKeywords(cls,queryWords):
        corrected = []
        for word in queryWords:
            if cls.isEnglish(word):
                corrected.append(correctENG.correction(word))
            else:
                corrected.append(correctCHN.correctionCHN(word))
        return corrected

    @classmethod
    def Search(cls,query,correctQuery,queryWords):
        startTime = time.time()
        correctedQuery = ""
        if query != correctQuery:
            correctedQuery = correctQuery
        queryWordsCorrected = cls.correctKeywords(queryWords)
        if ' '.join(queryWordsCorrected) != ' '.join(queryWords):
            correctedQuery = ' '.join(queryWordsCorrected)
        
        resultNews = []
        if len(queryWordsCorrected) == 1:
            word_weight = []
            for data in cls.collection.find({"$or": [{'title':re.compile(queryWordsCorrected[0])},{'content':re.compile(queryWordsCorrected[0])}]}):
                titleOccurs = data["title"].lower().count(queryWordsCorrected[0])
                contentOccurs = data["content"].lower().count(queryWordsCorrected[0])
                weight = 5 * titleOccurs + contentOccurs
                word_weight.append([data, weight])
            for data,weight in sorted(word_weight,key = lambda word_weight: word_weight[1],reverse=True)[:10]:
                content = cls.getAbstract(data["content"],queryWordsCorrected)
                resultNews.append({
                    "url":data["url"],
                    "title":data["title"],
                    "date":data["date"],
                    "content":content
                    })
        else:
            searchExpr = []
            article_count_weight = []
            for word in queryWordsCorrected:
                searchExpr.append({'title': re.compile(word)})
                searchExpr.append({'content': re.compile(word)})
            #print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")

            for singleRelated in cls.collection.find({"$or": searchExpr}):
                count = 0
                total_weight = 0
                for word in queryWordsCorrected:
                    titleOccurs = singleRelated["title"].lower().count(word)
                    contentOccurs = singleRelated["content"].lower().count(word)
                    weight = 5 * titleOccurs + contentOccurs
                    if weight > 0:
                        count+=1
                        total_weight+=weight
                article_count_weight.append((singleRelated,count,total_weight))
            
            #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            #print(article_count_weight)
            for singleRelated,count,total_weight in sorted(article_count_weight, key = lambda x:(x[1],x[2]), reverse = True)[:10]:
                content = cls.getAbstract(singleRelated["content"],queryWordsCorrected)
                resultNews.append({
                    "url":singleRelated["url"],
                    "title":singleRelated["title"],
                    "date":singleRelated["date"],
                    "content":content
                })
        
        endTime = time.time()
        searchTime = ("%.3f" % (endTime-startTime))
        SearchResult = {
            "resultNews": resultNews,
            "correctedQuery": correctedQuery,
            "resultLen": len(resultNews),
            "searchTime": searchTime,
            "highLightWords": queryWordsCorrected
        }
        return SearchResult