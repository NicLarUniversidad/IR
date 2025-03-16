import bisect
import math


class PostingList(object):

    def __init__(self, termId):
        self.termId = termId
        self.docIdList = []
        self.scores = dict()
        self.index = 0
        self.dGaps = []
        self.currentDocId = 0
        self.infinite = 0

    def addDocId(self, docId, frequency):
        bisect.insort(self.docIdList, docId)
        self.scores[int(docId)] = frequency

    def reset(self):
        self.index = 0
        if len(self.dGaps) > 0:
            self.currentDocId = self.dGaps[0]

    def getCurrent(self):
        docId = self.docIdList[self.index]
        score = self.scores[int(docId)]
        return docId, score

    def advanceIndex(self):
        if (len(self.docIdList) > self.index or len(self.dGaps) > self.index) and self.index != -1:
            self.index += 1
        else:
            self.infinite = -1

    def advanceIndex2(self):
        self.index += 1

    def next(self):
        if self.index < len(self.docIdList) - 1:
            self.advanceIndex()
        else:
            self.infinite = -1
        if self.currentDocId < len(self.docIdList):
            self.currentDocId += 1
        return self.getCurrent()

    def next2(self):
        self.advanceIndex()
        #return self.getCurrent()

    def next3(self):
        self.advanceIndex2()

    def loadDeltaGaps(self):
        self.dGaps = []
        lastDocId = 0
        for docId in self.docIdList:
            if len(self.dGaps) == 0:
                self.dGaps.append(docId)
            else:
                dGap = lastDocId - docId
                self.dGaps.append(dGap)
            lastDocId = docId

    def setDeltaGaps(self, deltaGaps):
        self.dGaps = deltaGaps

    def restoreWithDeltaGaps(self, dGaps, frequencies):
        self.dGaps = dGaps
        self.scores = frequencies
        self.docIdList.clear()
        docId = 0
        for delta in self.dGaps:
            docId += delta
            self.docIdList.append(docId)

    def getSortedScores(self):
        result = []
        for docId in self.docIdList:
            result.append(self.scores[int(docId)])
        return result

    def getCurrentByDGap(self):
        return self.currentDocId

    def advanceDelta(self):
        self.advanceIndex()
        self.currentDocId += self.docIdList[self.index]

    def jump(self, index, docId):
        if len(self.dGaps) > index:
            self.index = index
            self.currentDocId = docId

    def restoreWithRawData(self, docIdList, frequencies):
        self.scores = dict()
        self.docIdList = docIdList
        i = 0
        while i < len(docIdList):
            self.scores[int(docIdList[i])] = frequencies[i]
            i += 1

    def merge(self, postingList):
        i = 0
        while i < len(postingList.docIdList):
            self.addDocId(postingList.docIdList[i], postingList.scores[int(postingList.docIdList[i])])
            i += 1

    def getCurrentDocID(self):
        return self.docIdList[self.index]

    def getCurrentDocID2(self):
        if self.index < len(self.docIdList):
            return self.docIdList[self.index]
        else:
            return -1

    def getCurrentScore(self):
        return self.scores[self.docIdList[self.index]]

    def getUB(self):
        ub = 0
        for docId in self.scores:
            if self.scores[docId] > ub:
                ub = self.scores[docId]
        return ub

    def getMaxDocID(self):
        maxDocId = 0
        for docId in self.docIdList:
            if docId > maxDocId:
                maxDocId = docId
        return maxDocId

    def nextge(self, _docid):
        try:
            current = self.getCurrentDocID()
            skipped = 0
            hasNext = True
            while current < _docid and hasNext:
                self.next2()
                try:
                    current = self.getCurrentDocID()
                    skipped += 1
                except:
                    self.index -= 1
                    hasNext = False
                #hasNext = current != self.getCurrentDocID()
            return current, skipped
        except:
            return -1, 0

    def nextge2(self, _docid):
        try:
            current = self.getCurrentDocID()
            skipped = 0
            hasNext = True
            while current < _docid and hasNext:
                self.next2()
                try:
                    current = self.getCurrentDocID()
                    skipped += 1
                except:
                    #self.index -= 1
                    hasNext = False
                #hasNext = current != self.getCurrentDocID()
            return current, skipped
        except:
            return -1, 0

    def nextge3(self, _docid):
        try:
            current = self.getCurrentDocID()
            skipped = 0
            hasNext = True
            while current < _docid and hasNext:
                self.index += 1
                if self.index < len(self.docIdList) and self.index != -1:
                    current = self.getCurrentDocID()
                    skipped += 1
                else:
                    hasNext = False
                #hasNext = current != self.getCurrentDocID()
            return current, skipped
        except:
            return -1, 0

    def noCountNextge3(self, _docid):
        try:
            current = self.getCurrentDocID()
            skipped = 0
            hasNext = True
            while current < _docid and hasNext:
                self.index += 1
                if self.index < len(self.docIdList) and self.index != -1:
                    current = self.getCurrentDocID()
                    skipped += 1
                else:
                    hasNext = False
                #hasNext = current != self.getCurrentDocID()
            return current, skipped
        except:
            return -1, 0

    def hasNotNext(self):
        return self.index >= len(self.docIdList)

    def getCurrentId2(self):
        if self.index < len(self.docIdList) and self.index >= 0:
            return self.docIdList[self.index]
        else:
            return -1
        #return self.docIdList[self.index] if (self.index <= len(self.docIdList)) else -1
