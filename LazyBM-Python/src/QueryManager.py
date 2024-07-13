import re

import nltk
from nltk import SnowballStemmer
from nltk.corpus import stopwords

class QueryManager(object):

    def __init__(self):
        nltk.download('stopwords')
        self.stopwords = list(stopwords.words('spanish')) + list(nltk.corpus.stopwords.words('english'))
        self.stemmer = SnowballStemmer('spanish')


    def parseBooleanQuery(self, query):
        query = query.lower()
        query = re.sub(r'[àáâãäå]', 'a', query)
        query = re.sub(r'[èéêë]', 'e', query)
        query = re.sub(r'[ìíîï]', 'i', query)
        query = re.sub(r'[òóôõö]', 'o', query)
        query = re.sub(r'[ùúûü]', 'u', query)
        query = re.sub(' +', ' ', query)
        matches = re.match("(not )?[a-z]+ (and|or) (not )?[a-z]+", query)
        queryType = 1
        if not matches:
            matches = re.match("(not )?[a-z]+ (and|or) (not )?[a-z]+ (and|or) (not )?[a-z]+", query)
            queryType = 2
        if not matches:
            matches = re.match("\((not )?[a-z]+ (and|or) (not )?[a-z]+\) (and|or) (not )?[a-z]+", query)
            queryType = 3
        if not matches:
            matches = re.match("(not )?[a-z]+ (and|or) \((not )?[a-z]+ (and|or) (not )?[a-z]+\)", query)
            queryType = 4

        if matches:
            print("Query válida")
            query = query.replace("(", "")
            query = query.replace(")", "")
            queryTerms = query.split()
            result = []
            for term in queryTerms:
                result.append(self.stemmer.stem(term))
            return result, queryType
        else:
            print("Query no válida")

    def parseQuery(self, query):
        query = query.lower()
        query = re.sub(r'[àáâãäå]', 'a', query)
        query = re.sub(r'[èéêë]', 'e', query)
        query = re.sub(r'[ìíîï]', 'i', query)
        query = re.sub(r'[òóôõö]', 'o', query)
        query = re.sub(r'[ùúûü]', 'u', query)
        query = re.sub(' +', ' ', query)

        queryTerms = query.split()
        result = dict()
        for term in queryTerms:
            qTerm = self.stemmer.stem(term)
            if qTerm not in result:
                result[qTerm] = 1
            else:
                result[qTerm] += 1
        return result
