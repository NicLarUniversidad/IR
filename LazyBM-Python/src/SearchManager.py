from BMM import BMM
from BMW import BMW
from LazyBM import LazyBM
from MaxScore import MaxScore
from QueryManager import QueryManager
from TopK import TopK
from TopkAlgorithms import TopkAlgorithms
from Wand import Wand


class SearchManager(object):

    def __init__(self, algorithm=None, termDict=None, postingLists=None):
        if postingLists is None:
            postingLists = dict()
        if postingLists is None:
            postingLists = []
        self.algorithms = dict()
        # if algorithm is not None:
        #
        #     if algorithm == TopkAlgorithms.LAZY_BM:
        #         self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)
        #
        # if algorithm is None or len(self.algorithms) == 0:
            #self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)
        self.algorithms[TopkAlgorithms.MAX_SCORE] = MaxScore(termDict)
        self.algorithms[TopkAlgorithms.WAND] = Wand(termDict)

        self.queryManager = QueryManager()
        self.termDict = termDict
        if postingLists is None:
            postingLists = dict()
        self.postingLists = postingLists

    def search(self, query, topKN):
        queryTerms = self.queryManager.parseQuery(query)
        queryTermIds = []
        for term in queryTerms:
            if term in self.termDict:
                queryTermIds.append(self.termDict[term])
        results = dict()
        if len(queryTerms) > 0:
            for algorithm in self.algorithms:
                searcher = self.algorithms[algorithm]
                queryPostingsLists = []
                for termId in queryTermIds:
                    if termId in self.postingLists:
                        self.postingLists[termId].index = 0
                        self.postingLists[termId].infinite = 0
                        self.postingLists[termId].currentDocId = self.postingLists[termId].docIdList[0]
                        queryPostingsLists.append(self.postingLists[termId])
                topK = TopK(topKN)
                ranking, blockService = searcher.processQuery(queryPostingsLists, topK)
                print("Resultado")
                for i in range(0, len(topK.rank)):
                    print(f" DocID: {topK.rank[i]}, Score: {topK.scores[i]}")
                #results[algorithm] = (ranking, blockService.getStatistics(), searcher.processTime)
        return results
