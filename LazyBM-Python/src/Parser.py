import re

import nltk
from nltk import SnowballStemmer
from nltk import LancasterStemmer


# REEMPLAZAR_CARACTERES = {
#
#    'a': ['ā', 'á', 'ǎ', 'à', 'â', 'ã', 'ä'],
#    'e': ['é', 'ě', 'è', 'ê', 'ë'],
#    'i': ['í', 'ǐ', 'ì', 'î', 'ï'],
#    'o': ['ó', 'ǒ', 'ò', 'ô', 'ö'],
#    'u': ['ú', 'ü','ǘ', 'ǚ', 'ǔ', 'ǜ', 'ù', 'û'],
#    'n': ['ñ'],
#    'ss': ['ß'],
#    ' ':['¬', '…'],
#    'c': ['ç']
# }


# PATRONES = {
#    'mail': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
#    'url': '(?:https:\/\/|http:\/\/)(?:www\.)?[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9]{2,}(?:\/[a-zA-Z0-9-._~:?#[@!$&'()*+,;=%]*)?',
#    'telefono': '(\+?54)[ -]*[9][ -]*[0-9]{2,4}[ -]*[0-9]{2,4}[ -]*[0-9]{4,4}',
#    'nombre': '[A-Z][a-z]+(?:(?:\s*|\s*\n\s*) [a-z]{1,3} [a-z]{1,3}? [A-Z][a-z]+)*'
# }

class Parser(object):

    def __init__(self):
        nltk.download('stopwords')
        self.stopwords = list(nltk.corpus.stopwords.words('spanish')) + list(nltk.corpus.stopwords.words('english'))
        self.stemmer = SnowballStemmer('spanish')
        self.stemmerLancaster = LancasterStemmer()
        self.minLength = 3
        self.maxLength = 15
#       self._reemplazar_caracteres = REEMPLAZAR_CARACTERES
#       self._patrones = PATRONES

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
                    if formattedWord not in termIndexes:
                        termCount += 1
                        termIndexes[formattedWord] = termCount
                        termIndexesInverse[termCount] = formattedWord
                        termKey = termCount
                    else:
                        termKey = termIndexes[formattedWord]
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
