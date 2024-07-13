import re

import nltk
from nltk import SnowballStemmer
from nltk import LancasterStemmer


class Parser(object):

    def __init__(self):
        nltk.download('stopwords')
        self.stopwords = list(nltk.corpus.stopwords.words('spanish')) + list(nltk.corpus.stopwords.words('english'))
        self.stemmer = SnowballStemmer('spanish')
        self.stemmerLancaster = LancasterStemmer()
        self.minLength = 3
        self.maxLength = 15

    def customParse(self, text, termIndexes=None, termIndexesInverse=None):
        if termIndexes is None:
            termIndexes = dict()
        if termIndexesInverse is None:
            termIndexesInverse = dict()
        termCount = len(termIndexes)
        text = text.lower()
        text = re.sub(r'[àáâãäå]', 'a', text)
        text = re.sub(r'[èéêë]', 'e', text)
        text = re.sub(r'[ìíîï]', 'i', text)
        text = re.sub(r'[òóôõö]', 'o', text)
        text = re.sub(r'[ùúûü]', 'u', text)
        words = text.split()
        textTerms = dict()
        for word in words:
            formattedWord = self.stemmer.stem(word)
            formattedWord = re.sub(r'\W', '', formattedWord)
            if len(formattedWord) > self.minLength & len(formattedWord) < self.maxLength:
                if formattedWord not in self.stopwords:
                    termKey = ""
                    if formattedWord not in termIndexes:
                        termCount += 1
                        termIndexes[formattedWord] = termCount
                        termIndexesInverse[str(termCount)] = formattedWord
                        termKey += str(termCount)
                    else:
                        termKey = str(termIndexes[formattedWord])
                    # Si ya está en la posting list, no se guarda de nuevo
                    if termKey not in textTerms.keys():
                        textTerms[termKey] = 1
                    else:
                        textTerms[termKey] += 1
        return textTerms, termIndexes, termIndexesInverse  # Se devuelve: ID Término -> Frecuencia


    def customParseEnglishStemmer(self, text, termIndexes=None, termIndexesInverse=None):
        if termIndexes is None:
            termIndexes = dict()
        if termIndexesInverse is None:
            termIndexesInverse = dict()
        termCount = len(termIndexes)
        text = text.lower()
        text = re.sub(r'[àáâãäå]', 'a', text)
        text = re.sub(r'[èéêë]', 'e', text)
        text = re.sub(r'[ìíîï]', 'i', text)
        text = re.sub(r'[òóôõö]', 'o', text)
        text = re.sub(r'[ùúûü]', 'u', text)
        words = text.split()
        textTerms = dict()
        for word in words:
            formattedWord = self.stemmerLancaster.stem(word)
            formattedWord = re.sub(r'\W', '', formattedWord)
            if len(formattedWord) > self.minLength & len(formattedWord) < self.maxLength:
                if formattedWord not in self.stopwords:
                    termKey = ""
                    if formattedWord not in termIndexes:
                        termCount += 1
                        termIndexes[formattedWord] = termCount
                        termIndexesInverse[str(termCount)] = formattedWord
                        termKey += str(termCount)
                    else:
                        termKey = str(termIndexes[formattedWord])
                    # Si ya está en la posting list, no se guarda de nuevo
                    if termKey not in textTerms.keys():
                        textTerms[termKey] = 1
                    else:
                        textTerms[termKey] += 1
        return textTerms  # Se devuelve: ID Término -> Frecuencia
