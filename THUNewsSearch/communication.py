import eel
import os
from words_cut import wordsCut
from Search import SearchAndRank


@eel.expose
def getSuggest(curInput):
    wordsSuggest = SearchAndRank.keywordsSuggest(curInput)
    return wordsSuggest


@eel.expose
def getResult(query):
    #print(query)
    query = query.strip().lower()
    if query == "":
        return {"resultNews": [], "correctedQuery":'', "resultLen": 0, "searchTime": 0.000}
    correctQuery = SearchAndRank.correctKeywords([query])[0]
    print(correctQuery)
    iniQueryWords = wordsCut.sentence_seg(correctQuery)
    queryWords = []
    for word in iniQueryWords:
        if word != ' ':
            queryWords.append(word)
    SearchResult = SearchAndRank.Search(query,correctQuery,queryWords)
    #print(SearchResult)
    return SearchResult


web_app_options = {
    'mode': '',
    'host': 'localhost',
    'port': 8000,
    'chromeFlags': []
}


if __name__ == '__main__':
    eel.init('front')
    eel.start('index.html', options=web_app_options)