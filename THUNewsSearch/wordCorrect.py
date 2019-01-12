import re
from collections import Counter
from pypinyin import lazy_pinyin,pinyin

class correctENG:

    def words(text): 
        return re.findall(r'\w+', text.lower())

    WORDS = Counter(words(open('big.txt').read()))

    @classmethod
    def P(cls,word, N=sum(WORDS.values())):
        "Probability of `word`."
        return cls.WORDS[word] / N

    @classmethod
    def correction(cls,word):
        "Most probable spelling correction for word."
        return max(cls.candidates(word), key=cls.P)

    @classmethod
    def candidates(cls,word):
        "Generate possible spelling corrections for word."
        return (cls.known([word]) or cls.known(cls.edits1(word)) or cls.known(cls.edits2(word)) or [word])

    @classmethod
    def known(cls,words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in cls.WORDS)

    @classmethod
    def edits1(cls,word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @classmethod
    def edits2(cls,word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in cls.edits1(word) for e2 in cls.edits1(e1))


class correctCHN:

    @classmethod
    def correctionCHN(cls, singleQuery):
        with open('TsinghuaDict.txt','r',encoding='utf-8') as file:
            thu_words = [line.strip() for line in file.readlines()]
            thu_words_pinyin = []
            for thuWord in thu_words:
                thu_words_pinyin.append('/'.join(lazy_pinyin(thuWord)))
            if singleQuery in thu_words:
                wordCorrected = singleQuery
            else:
                singleQuery_pinyin = '/'.join(lazy_pinyin(singleQuery))
                try:
                    wordCorrected = thu_words[thu_words_pinyin.index(singleQuery_pinyin)]
                except ValueError:
                    wordCorrected = singleQuery
            return wordCorrected
