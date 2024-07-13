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
        return self.record[1 + self.blockSize + self.currentIdx]

    def next(self):
        self.currentIdx += 1

    def getNextDocId(self):
        self.next()
        return self.getCurrentDocId()

    def skipTo(self, pivoteDocId):
        hasNextDocId = 1
        while self.getMaxDocId() < pivoteDocId and hasNextDocId:
            hasNextDocId = self.next()
            if not hasNextDocId:
                # TODO: ¿recuperar siguiente bloque?
                pass

    def hasNextBlock(self):
        return self.blockCount > self.blockNumber
