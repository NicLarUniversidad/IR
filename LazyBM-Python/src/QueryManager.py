import re

import nltk
from nltk import SnowballStemmer
from nltk.corpus import stopwords

class QueryManager(object):

    def __init__(self):
        nltk.download('stopwords')
        self.stopwords = list(stopwords.words('spanish')) + list(nltk.corpus.stopwords.words('english'))
        self.stemmer = SnowballStemmer('english')

    def parseQuery(self, query):
        query = query.lower()
        query = re.sub(r'[àáâãäå]', 'a', query)
        query = re.sub(r'[èéêë]', 'e', query)
        query = re.sub(r'[ìíîï]', 'i', query)
        query = re.sub(r'[òóôõö]', 'o', query)
        query = re.sub(r'[ùúûü]', 'u', query)

        queryTerms = query.split()
        result = dict()
        for term in queryTerms:
            term = re.sub(r'\W', '', term)
            qTerm = self.stemmer.stem(term)
            if qTerm not in result:
                result[qTerm] = 1
            else:
                result[qTerm] += 1
        return result
