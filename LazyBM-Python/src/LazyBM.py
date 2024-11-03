import time

from BlockMaxIndexManager import BlockMaxIndexManager
from BlockService import BlockService
from MetadataFilesManager import MetadataFilesManager
from PostingListVectorialManager import PostingListVectorialManager
from QueryManager import QueryManager
from TopK import TopK


class LazyBM(object):

    def __init__(self, termDict=None):
        self.postingLists = dict()
        self.queryManager = QueryManager()
        self.infinite = -1
        self.termDict = termDict
        self.processTime = 0
        self.sizes = []

    # Se implementa el pseudo-código de LazyBM en el siguiente método
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
            # Compute prefix sum
            pivotDocId = blockService.pivotDocId
            # Se obtiene P(t|c)
            ub = self.s(pivotDocId)
            # Se obtienen los upper bounds acomulados según el orden calculado
            P = blockService.computePrefixSum()
            # Se separan en términos esenciales y opcionales según theta (MaxScore)
            # T.opt <- P[t] < theta
            # T.ess <- Q - T.opt
            tOpt, tEss = blockService.getOptionalsAndEssentials(P, topK.getTheta())
            # Se calcula un UB según los máximos scores de los bloques (WAND)
            for t in tEss:
                if blockService.getCurrentDocId(t) == pivotDocId:
                    ub += blockService.getUb(t)
            for t in tOpt:

                if ub > topK.getTheta() or ub + P[t] < topK.getTheta():
                    break

                if blockService.getCurrentDocId(t) < pivotDocId:
                    blockService.skipTo(t, pivotDocId)

                if blockService.getCurrentDocId(t) == pivotDocId:
                    ub += blockService.getUb(t)

            if ub > topK.getTheta():
                score = self.s(pivotDocId)
                for t in tEss:
                    if blockService.getCurrentDocId(t) == pivotDocId:
                        score += blockService.getCurrentScore(t)

                for t in tOpt:

                    if score + blockService.getUb(t) <= topK.getTheta():
                        break

                    if blockService.getCurrentDocId(t) < pivotDocId:
                        blockService.skipTo(t, pivotDocId)

                    if blockService.getCurrentDocId(t) == pivotDocId:
                        score += blockService.getCurrentScore(t)

                if score > topK.getTheta():
                    topK.put(pivotDocId, score)

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

    def getPivot(self, block):
        pivot = self.infinite
        for term in block:
            current = block[term].getCurrentDocId()
            if pivot == self.infinite or current < pivot:
                pivot = current
        return pivot

    def s(self, pivotDocId):
        # TODO: recuperar probabilidad del término en la colección
        return 0

    def getSizes(self):
        return self.sizes

