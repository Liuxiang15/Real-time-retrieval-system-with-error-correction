var app = new Vue({
    el: '#app',
    data: {
        searchValue: '',
        correctedValue: '',
        resultLen: 0,
        searchTime: 0.000,
        wordsList:[],
        newsList: [],
        highLightWords: []
    },
    computed: {
        
    },
    methods: {
        clearTimer: function(){
            if (this.timer) {
                clearTimeout(this.timer)
            }
        },
        handleQuery: function() {
            this.clearTimer();
            this.timer = setTimeout(() => {
                getWordsSuggest(document.getElementById("kw").value);
            },800);

        },
        autoSearch: function(wordSuggest) {
            document.getElementById("kw").value = wordSuggest;
            getWordsSuggest("");
            this.beginRecognition();
        },
        beginRecognition: function () {
            var query = document.getElementById("kw").value;
            searchValue = query;
            getWordsSuggest("");
            getSearchResult(query);
        },
        getNewsUrl: function (item){
            window.open(item.url);
        },
        brightenkeywords: function (content){
            content = content + '';
            for(var i = 0; i < this.highLightWords.length; i++){
                if(content.indexOf(this.highLightWords[i]) !== -1){
                    let keywordsReg = new RegExp(this.highLightWords[i], 'g');
                    content = content.replace(keywordsReg, '<font color="#FF0000">' + this.highLightWords[i] + '</font>');
                }
            }
            return content;
            //searchValue = searchValue.replace(/^(\s|\xA0)+|(\s|\xA0)+$/g, '');
            /*if (content.indexOf(searchValue) !== -1 && searchValue !== '') {
                let keywordsReg = new RegExp(searchValue, 'g');
                return content.replace(keywordsReg, '<font color="#FF0000">' + searchValue + '</font>')
            }
            else {
                return content;
            }*/
        }
    }
});

async function getWordsSuggest(curInput) {
    app.wordsList = await eel.getSuggest(curInput)();
}

async function getSearchResult(query) {
    //alert(query);
    let resultJson = await eel.getResult(query)();
    app.newsList = resultJson.resultNews;
    app.correctedValue = resultJson.correctedQuery;
    app.resultLen = resultJson.resultLen;
    app.searchTime = resultJson.searchTime;
    app.highLightWords = resultJson.highLightWords;
}
