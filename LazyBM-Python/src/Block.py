class Block(object):

    def __init__(self, record, blockSize, blockCount, blockNumber, docIdCount):
        self.record = record
        self.blockSize = blockSize
        self.currentIdx = 0
        self.blockCount = blockCount
        self.blockNumber = blockNumber
        self.docIdCount = docIdCount

    def getUb(self):
        return self.record[1]

    def getMaxDocId(self):
        return self.record[0]

    def getCurrentDocId(self):
        return self.record[1 + self.currentIdx]

    def getCurrentScore(self):
        return self.record[1 + self.blockSize + self.currentIdx]

    def next(self):
        if self.currentIdx < self.blockSize:
            self.currentIdx += 1
            return 1
        else:
            return 0

    def getNextDocId(self):
        flag = self.next()
        if flag == 1:
            return self.getCurrentDocId()
        else:
            return -1

    def skipTo(self, pivoteDocId):
        hasNextDocId = 1
        while self.getMaxDocId() < pivoteDocId and hasNextDocId:
            hasNextDocId = self.next()
            if not hasNextDocId:
                # TODO: ¿recuperar siguiente bloque?
                pass

    def hasNextBlock(self):
        return self.blockCount > self.blockNumber
