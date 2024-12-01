import math

from MemoryBlockMax import MemoryBlockMax


class MemoryBlockMaxPostingList(object):

    def __init__(self, termId, postingList):
        self.blocks = []
        self.termId = termId
        self.blockSize = int(math.sqrt(len(postingList.docIdList)))
        docIdList = []
        scoreList = []
        self.count = 0
        for i in range(len(postingList.docIdList)):
            if len(docIdList) >= self.blockSize:
                self.addBlock(docIdList, scoreList)
                docIdList = []
                scoreList = []
            docIdList.append(postingList.docIdList[i])
            scoreList.append(postingList.scores[postingList.docIdList[i]])
        if len(docIdList) > 0:
            self.addBlock(docIdList, scoreList)

    def addBlock(self, docIdList, scoreList):
        newBlock = MemoryBlockMax()
        newBlock.docIdList = docIdList
        newBlock.scores = scoreList
        newBlock.docIdUpperbound = max(docIdList)
        newBlock.frequencyUpperbound = max(scoreList)
        newBlock.idx = self.count
        self.count += 1
        self.blocks.append(newBlock)

    def skipTo(self, block, pivotDocId):
        if pivotDocId <= block.docIdUpperbound:
            docIdSkipped = block.skipTo(pivotDocId)
        else:
            docIdSkipped = 0
            blockIdx = block.idx
            while pivotDocId > block.docIdUpperbound:
                blockIdx += 1
                if blockIdx >= len(block.docIdList):
                    nextBlock = self.getNextBlock(blockIdx)
                    if nextBlock is None:
                        break
                    else:
                        block = nextBlock
                docIdSkipped = block.skipTo(pivotDocId)
                block = self.blocks[blockIdx]
        return block, docIdSkipped

    def getNextBlock(self, idx):
        if idx < len(self.blocks):
            return self.blocks[idx]
        else:
            return None

    def next(self, block):
        nextDocId = block.next()
        if nextDocId == -1:
            nextBlock = self.getNextBlock(block.idx + 1)
            if nextBlock is None:
                return -1
            block = nextBlock
            nextDocId = block.getCurrentDocId()
        return nextDocId


