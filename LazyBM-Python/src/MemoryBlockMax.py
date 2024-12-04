class MemoryBlockMax(object):
    def __init__(self):
        self.docIdList = []
        self.scores = []
        self.docIdUpperbound = 0
        self.frequencyUpperbound = 0
        self.currentDocId = 0
        self.idx = 0

    def getCurrentDocId(self):
        if self.currentDocId < len(self.docIdList):
            return self.docIdList[self.currentDocId]
        else:
            return -1

    def next(self):
        self.currentDocId += 1
        return self.getCurrentDocId()

    def getUb(self):
        return self.frequencyUpperbound

    def getUbScore(self):
        return self.frequencyUpperbound

    def skipTo(self, pivotDocId):
        skipped = 0
        if pivotDocId <= self.docIdUpperbound:
            while pivotDocId > self.getCurrentDocId() and self.getCurrentDocId() != -1:
                self.next()
                skipped += 1
        # else:
        #     while self.getCurrentDocId() <= self.docIdUpperbound:
        #         if self.next() != -1:
        #             skipped += 1
        return skipped

    def getCurrentScore(self):
        if self.currentDocId < len(self.docIdList):
            return self.scores[self.currentDocId]
        else:
            return 0
