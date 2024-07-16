import time

from BlockService import BlockService
from PostingListVectorialManager import PostingListVectorialManager
from QueryManager import QueryManager
from TopK import TopK


class BMW(object):
    def __init__(self, termDict=None):
        self.postingLists = dict()
        self.queryManager = QueryManager()
        self.postingListManager = PostingListVectorialManager()
        self.infinite = -1
        self.termDict = termDict
        self.processTime = 0
        self.sizes = []

    # TODO: implementar LBMW (Lazy Block Max WAND)
    def processQuery(self, queryTerms, k):
        initTime = time.time()
        # La clase top K representa un heap de tamaño K
        topK = TopK(k)
        # Al instanciar un blockService, se buscan los primeros bloques y hay un ordenamiento (ver constructor)
        # Get candidate doc id list
        blockService = BlockService(queryTerms, self.termDict)
        # Se separan en términos esenciales y opcionales según theta
        terms = blockService.termList
        # Mientras haya un siguiente DOC-ID válido en el conjunto de bloques...
        while blockService.nextDocWithinEssentialBlock(terms):
            # Compute prefix sum
            pivotDocId = blockService.pivotDocId
            # Se obtiene P(t|c)
            ub = self.s(pivotDocId)
            for t in terms:
                if blockService.getCurrentDocId(t) == pivotDocId:
                    ub += blockService.getUb(t)

            if ub > topK.getTheta():
                score = self.s(pivotDocId)
                for t in terms:
                    if blockService.getCurrentDocId(t) == pivotDocId:
                        score += blockService.getCurrentScore(t)

                if score > topK.getTheta():
                    topK.insert(pivotDocId, score)
            else:
                blockService.docIdSkippedWithUb += 1

        finishTime = time.time()
        self.processTime = finishTime - initTime
        self.sizes = blockService.sizes
        return topK, blockService

    def search(self, query, topK):
        queryTerms = self.queryManager.parseQuery(query)
        if len(queryTerms) > 0:
            ranking, blockService = self.processQuery(queryTerms, topK)
            return ranking, blockService

    def s(self, pivotDocId):
        # TODO: recuperar probabilidad del término en la colección
        return 0

    def getSizes(self):
        return self.sizes

