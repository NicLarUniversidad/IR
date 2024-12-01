import time

from BlockMaxIndexManager import BlockMaxIndexManager
from BlockService import BlockService
from MetadataFilesManager import MetadataFilesManager
from PostingListVectorialManager import PostingListVectorialManager
from QueryManager import QueryManager
from TopK import TopK


class LazyBM(object):

    def __init__(self, blockMaxIndex, termDict=None):
        self.postingLists = dict()
        self.blockMaxIndex = blockMaxIndex
        self.queryManager = QueryManager()
        self.infinite = -1
        self.termDict = termDict
        self.processTime = 0
        self.sizes = []
        self.pivotDocId = None
        self.skippedDocId = 0

    # Se implementa el pseudo-código de LazyBM en el siguiente método
    def processQuery(self, postingLists, topK):
        # Inicializo contador de DocId salteados
        self.skippedDocId = 0
        # La clase top K representa un heap de tamaño K
        # topK = TopK(k) #  Ya se manda por parámetro
        # Al instanciar un blockService, se buscan los primeros bloques y hay un ordenamiento (ver constructor)
        # Get candidate doc id list
        blocks = self.getFirstBlocks(postingLists)
        # Se obtienen los upper bounds acomulados según el orden calculado
        P = self.computePrefixSum(blocks)
        # Se separan en términos esenciales y opcionales según theta
        tOpt, tEss = self.getOptionalsAndEssentials(P, topK.getTheta())
        self.pivotDocId = 0
        # Mientras haya un siguiente DOC-ID válido en el conjunto de bloques...
        while self.nextDocWithinEssentialBlock(tEss, blocks, postingLists):
            # Compute prefix sum
            pivotDocId = self.pivotDocId
            # Se obtiene P(t|c)
            ub = self.s(pivotDocId)
            # Se obtienen los upper bounds acomulados según el orden calculado
            P = self.computePrefixSum(blocks)
            # Se separan en términos esenciales y opcionales según theta (MaxScore)
            # T.opt <- P[t] < theta
            # T.ess <- Q - T.opt
            tOpt, tEss = self.getOptionalsAndEssentials(P, topK.getTheta())
            # Se calcula un UB según los máximos scores de los bloques (WAND)
            for termId in tEss:
                if blocks[termId].getCurrentDocId() == pivotDocId:
                    ub += blocks[termId].getUb()

            for termId in tOpt:
                if ub > topK.getTheta() or ub + P[termId] < topK.getTheta():
                    break

                if blocks[termId].getCurrentDocId() < pivotDocId:
                    blocks[termId], docIdSkipped = self.getPosting(postingLists, termId).skipTo(blocks[termId], pivotDocId)
                    self.skippedDocId += docIdSkipped

                if blocks[termId].getCurrentDocId() == pivotDocId:
                    ub += blocks[termId].getUb()

            if ub > topK.getTheta():
                score = self.s(pivotDocId)
                for termId in tEss:
                    if blocks[termId].getCurrentDocId() == pivotDocId:
                        score += blocks[termId].getCurrentScore()

                for termId in tOpt:

                    if score + blocks[termId].getUb() <= topK.getTheta():
                        break

                    if blocks[termId].getCurrentDocId() < pivotDocId:
                        blocks[termId], docIdSkipped = self.getPosting(postingLists, termId).skipTo(blocks[termId], pivotDocId)
                        self.skippedDocId += docIdSkipped

                    if blocks[termId].getCurrentDocId() == pivotDocId:
                        score += blocks[termId].getCurrentScore()

                if score > topK.getTheta():
                    topK.put(pivotDocId, score)

        #self.sizes = blockService.sizes
        return topK, self.skippedDocId  #, blockService

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

    def getFirstBlocks(self, postingLists):
        blocks = dict()
        for postingList in postingLists:
            termId = postingList.termId
            firstBlock = postingList.blocks[0]
            blocks[termId] = firstBlock
        return blocks

    def computePrefixSum(self, blocks):
        currentsIds = dict()
        # Ordeno los bloques de acuerdo al DocId actual
        for termId in blocks:
            currentsIds[termId] = blocks[termId].getCurrentDocId()
        currentsIds = dict(sorted(currentsIds.items(), key=lambda item: item[1]))
        # Calculo los Upper Bounds acomulados
        upperBounds = dict()
        accumulatedUB = 0
        for termId in currentsIds:
            accumulatedUB += blocks[termId].getUb()
            upperBounds[termId] = accumulatedUB
        return upperBounds

    def getOptionalsAndEssentials(self, P, theta):
        termEss, termOpt = [], []
        for termId in P:
            if P[termId] <= theta:
                termOpt.append(termId)
            else:
                termEss.append(termId)
        return termOpt, termEss

    def nextDocWithinEssentialBlock(self, tEss, blocks, postingLists):
        minDocId = None
        found = False
        # Busco el mínimo DocId de los términos esenciales
        for termId in tEss:
            currentDocId = blocks[termId].getCurrentDocId()
            if currentDocId == self.pivotDocId:
                #currentDocId = blocks[termId].next()
                currentDocId = self.getPosting(postingLists, termId).next(blocks[termId])
            if minDocId is None or currentDocId < minDocId:
                if currentDocId == -1:
                    postingList = self.getPosting(postingLists, termId)
                    nextBlock = postingList.getNextBlock(blocks[termId].idx + 1)
                    if nextBlock:
                        blocks[termId] = nextBlock
                        currentDocId = blocks[termId].getCurrentDocId()
                if currentDocId != -1:
                    minDocId = currentDocId
                    found = True
        self.pivotDocId = minDocId
        return found

    def getPosting(self, postingLists, termId):
        postingList = None
        for pl in postingLists:
            if pl.termId == termId:
                postingList = pl
        return postingList
