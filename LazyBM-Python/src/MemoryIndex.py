from PostingList import PostingList


class MemoryIndex:

    def __init__(self):
        self.postingLists = dict()

    def add(self, fileTermDict, fileId):

        if fileTermDict is not None:
            for term in fileTermDict:
                if int(term) not in self.postingLists:
                    self.postingLists[int(term)] = PostingList(term)
                self.postingLists[int(term)].addDocId(fileId, fileTermDict[term])
