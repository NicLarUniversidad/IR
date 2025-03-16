class Block(object):

    def __init__(self, record, blockSize, blockCount, blockNumber, docIdCount):
        self.record = record
        self.blockSize = blockSize
        self.currentIdx = 1
        self.blockCount = blockCount
        self.blockNumber = blockNumber
        self.docIdCount = docIdCount

    def getUb(self):
        return self.record[1]

    def getMaxDocId(self):
        return self.record[0]

    def getCurrentDocId(self):
        if self.currentIdx < self.blockSize:
            return self.record[1 + self.currentIdx]
        else:
            return -1

    def getCurrentScore(self):
        idx = 1 + self.blockSize + self.currentIdx
        if idx < len(self.record):
            return self.record[idx]
        else:
            print(f"Se quiso acceder al índice {idx}, máximo {len(self.record)}")
            return 0

    def next(self):
        self.currentIdx += 1

    def getNextDocId(self):
        self.next()
        return self.getCurrentDocId()

    def skipTo(self, pivoteDocId):
        hasNextDocId = 1
        skippedDocIds = 0
        while self.getMaxDocId() < pivoteDocId and hasNextDocId:
            hasNextDocId = self.next()
            skippedDocIds += 1
            if not hasNextDocId:
                # TODO: ¿recuperar siguiente bloque?
                pass
        return skippedDocIds

    def noCountSkipTo(self, pivoteDocId):
        hasNextDocId = 1
        while self.getMaxDocId() < pivoteDocId and hasNextDocId:
            hasNextDocId = self.next()
            if not hasNextDocId:
                # TODO: ¿recuperar siguiente bloque?
                pass

    def hasNextBlock(self):
        return self.blockCount > self.blockNumber

    def getAllDocId(self):
        docIdList = []
        for i in range(self.blockSize):
            docIdList.append(self.record[2 + i])
        return docIdList

    def getAllScores(self):
        scoreList = []
        for i in range(self.blockSize):
            scoreList.append(self.record[2 + self.blockSize + i])
        return scoreList

    def getDeltaGaps(self):
        dGaps = []
        lastDocId = 0
        for docId in self.getAllDocId():
            if len(dGaps) == 0:
                dGaps.append(docId)
            else:
                dGap = lastDocId - docId
                dGaps.append(dGap)
            lastDocId = docId
        return dGaps