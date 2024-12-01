from MemoryBlockMaxPostingList import MemoryBlockMaxPostingList


class MemoryBlockMaxIndex:

    def __init__(self, memoryIndex):
        self.index = 0
        self.memoryPostingLists = memoryIndex
        self.postingLists = dict()
        for termId in memoryIndex.postingLists:
            postingList = memoryIndex.postingLists[termId]
            blockMax = MemoryBlockMaxPostingList(termId, postingList)
            self.postingLists[termId] = blockMax

    def getCandidates(self, queryTerms):
        candidates = []
        for termId in queryTerms:
            if termId in self.postingLists:
                candidates.append(self.postingLists[termId])
        return candidates
