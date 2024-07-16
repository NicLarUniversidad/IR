import time

from BlockService import BlockService
from PostingListVectorialManager import PostingListVectorialManager
from QueryManager import QueryManager
from TopK import TopK


class BMM(object):

    def __init__(self, termDict=None):
        self.postingLists = dict()
        self.queryManager = QueryManager()
        self.postingListManager = PostingListVectorialManager()
        self.infinite = -1
        self.termDict = termDict
        self.processTime = 0
        self.sizes = []

    # TODO: implementar LBMM (Lazy Block Max MaxScore)
    def processQuery(self, queryTerms, k):
        initTime = time.time()
        # La clase top K representa un heap de tamaño K
        topK = TopK(k)
        # Al instanciar un blockService, se buscan los primeros bloques y hay un ordenamiento (ver constructor)
        # Get candidate doc id list
        blockService = BlockService(queryTerms, self.termDict)
        # Se obtienen los upper bounds acomulados según el orden calculado
        P = blockService.computePrefixSum()
        # Se separan en términos esenciales y opcionales según theta
        tOpt, tEss = blockService.getOptionalsAndEssentials(P, topK.getTheta())
        # Mientras haya un siguiente DOC-ID válido en el conjunto de bloques...
        while blockService.nextDocWithinEssentialBlock(tEss):
            pivotDocId = blockService.pivotDocId

            P = blockService.computePrefixSum()
            tOpt, tEss = blockService.getOptionalsAndEssentials(P, topK.getTheta())

            score = self.s(pivotDocId)
            for t in tEss:
                if blockService.getCurrentDocId(t) == pivotDocId:
                    score += blockService.getCurrentScore(t)

            for t in tOpt:

                if score > topK.getTheta() or score + P[t] < topK.getTheta():
                    break

                if blockService.getCurrentDocId(t) < pivotDocId:
                    blockService.skipTo(t, pivotDocId)

                if blockService.getCurrentDocId(t) == pivotDocId:
                    score += blockService.getCurrentScore(t)

            if score > topK.getTheta():
                topK.insert(pivotDocId, score)

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
