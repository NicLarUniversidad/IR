import math
from typing import List


class MaxScore(object):

    def __init__(self, termDict):
        self.termDict = termDict

    def processQuery(self, lists, topk):
        scoringOps = 0
        skipped = 0
        #
        ub_lists = self.sortListsByUB(lists)
        # Acumulo los UB
        n = len(ub_lists)
        ub = [0] * n
        ub[0] = ub_lists[0][0]
        for i in range(1, len(ub_lists)):
            ub[i] = ub[i - 1] + ub_lists[i][0]
        #   
        theta = 0
        pivot = 0
        current = self.MinimumDocID(lists)
        infinite = self.MaximumDocID(lists) + 1

        while (pivot < n and current < infinite):
            score = 0
            nextd = infinite
            #
            for i in range(pivot, n):
                nextDocId, skipped0 = lists[i].nextge(current)
                skipped += skipped0
                if lists[i].getCurrentDocID() == current:
                    score = score + lists[i].getCurrentScore()
                    scoringOps += 1
                    lists[i].next()
                if current < lists[i].getCurrentDocID() and nextd > lists[i].getCurrentDocID():
                    nextd = lists[i].getCurrentDocID()
                    #
            for i in range(pivot - 1, -1, -1):
                if (score + ub[i]) <= theta:
                    break
                nextDocId, skipped0 = lists[i].nextge(current)
                skipped += skipped0
                if lists[i].getCurrentDocID() == current:
                    score = score + lists[i].getCurrentScore()
                    scoringOps = scoringOps + 1
            #
            if topk.put(current, score):
                theta = topk.getMinScore()
                while pivot < n and ub[pivot] <= theta:
                    pivot = pivot + 1
            #
            current = nextd
            #               
        return scoringOps, skipped

    def sortListsByDocId(lists: List) -> List:
        lists.sort(key=lambda x: x.getCurrentDocID())
        return lists

    def swapListsByDocId(lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentDocID()
            if (cdoc != math.inf):
                slists.append((cdoc, i))
        slists = sorted(slists)
        #
        newLists = []
        for i in range(0, len(lists)):
            j = slists[i][1]
            newLists.append(lists[j])
        #
        lists = newLists
        return lists

    def sortListsByUB(self, lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentDocID()
            if (cdoc != math.inf):
                absUB = lists[i].getUB()
                slists.append((absUB, i))
        return list(reversed(sorted(slists)))

    def MaximumDocID(self, lists) -> int:
        did = []
        for l in lists:
            did.append(l.getMaxDocID())
        return max(did)

    def MinimumDocID(self, lists) -> int:
        did = []
        for l in lists:
            did.append(l.getCurrentDocID())
        return (min(did))
