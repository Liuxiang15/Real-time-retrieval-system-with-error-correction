import pymongo as pm
import jieba.analyse
import json

class Trie:
    root = {}
    END = -1
    
    @classmethod
    def insert(cls, word):
        curNode = cls.root
        for c in word:
            if c not in curNode:
                curNode[c] = {}
            curNode = curNode[c]
        curNode[cls.END] = True
    
    @classmethod
    def search(cls, word):
        curNode = cls.root
        for c in word:
            if c not in curNode:
                return False
            curNode = curNode[c]    
        # Doesn't end here
        if cls.END not in curNode:
            return False
        return True

    @classmethod
    def startsWith(cls, prefix):
        """
        Returns if there is any word in the trie that starts with the given prefix.
        """
        curNode = cls.root
        for c in prefix:
            if c not in curNode:
                return False
            curNode = curNode[c]
        return True

    @classmethod
    def getStartsWith(cls, prefix):
        def get_key(pre,node):
            words = []
            if cls.END in node:
                words.append(pre)
            for c in node.keys():
                if c != cls.END:
                    words.extend(get_key(pre + str(c), node[c]))
            return words
        
        resultWords = []
        if prefix == "":
            return resultWords
        if not cls.startsWith(prefix):
            return resultWords
        curNode = cls.root
        for c in prefix:
            curNode = curNode[c]
        return get_key(prefix,curNode)


client = pm.MongoClient('127.0.0.1',27017)
db = client.test
collection = db.col
obj = Trie()

singleWords = []
wordsFreq = {}
doc_num = 0

for data in collection.find():
    doc_num+=1
    print(doc_num)
    singleWords = data["keywords"].split(',')
    keywords = jieba.analyse.extract_tags(data["content"].lower(), topK=10, withWeight=True, allowPOS=())
    for item in keywords:
        if item[0] not in singleWords:
            singleWords.append(item[0])
    for word in singleWords:
        if word not in wordsFreq:
            wordsFreq[word] = 1
            obj.insert(word)
        else:
            wordsFreq[word] += 1

file1 = open('trieTree.json','w')
file1.write(json.dumps(obj.root))
file1.close()

file2 = open('trieTreeFreq.json','w')
file2.write(json.dumps(wordsFreq))
file2.close()
