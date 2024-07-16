from BMM import BMM
from BMW import BMW
from LazyBM import LazyBM
from QueryManager import QueryManager
from TopkAlgorithms import TopkAlgorithms


class SearchManager(object):

    def __init__(self, algorithm=None, termDict=None):
        self.algorithms = dict()
        if algorithm is not None:

            if algorithm == TopkAlgorithms.LAZY_BM:
                self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)

            if algorithm == TopkAlgorithms.BMM:
                self.algorithms[TopkAlgorithms.BMM] = BMM(termDict)

            if algorithm == TopkAlgorithms.BMW:
                self.algorithms[TopkAlgorithms.BMW] = BMW(termDict)

        if algorithm is None or len(self.algorithms) == 0:
            self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)
            self.algorithms[TopkAlgorithms.BMM] = BMM(termDict)
            self.algorithms[TopkAlgorithms.BMW] = BMW(termDict)

        self.queryManager = QueryManager()
        self.termDict = termDict

    def search(self, query, topK):
        queryTerms = self.queryManager.parseQuery(query)
        results = dict()
        if len(queryTerms) > 0:
            for algorithm in self.algorithms:
                searcher = self.algorithms[algorithm]
                ranking, blockService = searcher.processQuery(queryTerms, topK)
                results[algorithm] = (ranking, blockService.getStatistics(), searcher.processTime)
        return results
