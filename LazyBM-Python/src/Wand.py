import math
from typing import List


class Wand(object):

    def __init__(self, termDict):
        self.termDict = termDict

    def processQuery(self, lists, topk):
        scoringOps = 0
        skipped = 0
        #
        theta = 0
        infinite = self.MaximumDocID(lists) + 1
        lists = self.swapListsByDocId(lists)
        ulists = self.makeUBList(lists)
        n = len(lists)
        #
        while True:
            pivot = 0
            cumub = 0
        # TODO: Revisar condición de corte y valor infinito en el pivote
            for pivot in range(0, n):
                if lists[pivot].getCurrentId2() >= infinite or lists[pivot].getCurrentId2() == -1:
                    break
                cumub = cumub + ulists[pivot]
                if cumub > theta:
                    break

            if cumub <= theta:
                break

            pivot_id = lists[pivot].getCurrentId2()
            if pivot_id == lists[0].getCurrentId2():
                score = 0
                for i in range(0, n):
                    if lists[i].getCurrentId2() != pivot_id:
                        break
                    score = score + lists[i].getCurrentScore()
                    lists[i].next()
                    scoringOps = scoringOps + 1
                #
                topk.put(pivot_id, score)
                theta = topk.getTheta()
                lists = self.sortListsByDocId(lists)
            else:
                while lists[pivot].getCurrentId2() == pivot_id:
                    pivot = pivot - 1
                nextDocId, skipped0 = lists[pivot].nextge(pivot_id)
                skipped += skipped0
                lists, ulists = self.swapDown(lists, pivot)
            #
        #
        return scoringOps, skipped

    def sortListsByDocId(self, lists) -> List:
        lists.sort(key=lambda x: x.getCurrentId2())
        return lists

    def swapListsByDocId(self, lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentId2()
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
            cdoc = lists[i].getCurrentId2()
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
            did.append(l.getCurrentId2())
        return (min(did))

    def swapDown(self, lists: List, pivot: int):
        for i in range(pivot, len(lists) - 1):
            if (lists[i].getCurrentId2() > lists[i + 1].getCurrentId2()):
                lists[i], lists[i + 1] = lists[i + 1], lists[i]  # swap elements
            else:
                break
        ulist = self.makeUBList(lists)
        return lists, ulist

    def makeUBList(self, lists):
        ublists = []
        for i in range(0, len(lists)):
            ublists.append(lists[i].getUB())
        return (ublists)
