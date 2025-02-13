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
        upperBoundList = dict()
        for l in lists:
            upperBoundList[l.termId] = l.getUB()
        n = len(lists)
        #
        while True:
            pivot = 0
            cumub = 0
            pivote = -1
        # TODO: Revisar condición de corte y valor infinito en el pivote
            for a in range(0, n):
                pivote += 1
                #if lists[pivot].getCurrentId2() >= infinite or lists[pivot].getCurrentId2() == -1:
                if lists[pivote].getCurrentId2() == -1:
                    pivote -= 1
                    break
                #cumub = cumub + ulists[pivot]
                cumub += upperBoundList[lists[pivote].termId]
                if cumub > theta:
                    break
            # if cumub == 0:
            #     break
            if pivote == -1:
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
                    lists[i].next3()
                    scoringOps = scoringOps + 1
                #
                topk.put(pivot_id, score)
                theta = topk.getTheta()
                lists = self.sortListsByDocId(lists)
            else:
                for i in range(0, pivote):
                    if lists[i].getCurrentId2() < pivot_id:
                        nextDocId, skipped0 = lists[i].nextge3(pivot_id)
                        skipped += skipped0
                # while lists[pivot].getCurrentId2() == pivot_id:
                #     pivot = pivot - 1
                # nextDocId, skipped0 = lists[pivot].nextge3(pivot_id)
                # skipped += skipped0
                #lists, ulists = self.swapDown(lists, pivot)
                lists = self.sortListsByDocId(lists)
            #

        for i in range(0, n):
            if lists[i].getCurrentId2() != -1:
                nextDocId, skipped0 = lists[i].nextge3(infinite)
                skipped += skipped0
        #
        return topk, skipped

    def processQuery2(self, lists0, topk):
        skipped = 0
        theta = 0
        hasNextDocIdToProcess = True
        while hasNextDocIdToProcess:
            cumub = 0
            pivot = -1
            lists = self.swapListsByDocId(lists0)
            #ulists = self.makeUBList(lists)
            n = len(lists)
            for i in range(0, n):
                pivot += 1
                if lists[pivot].getCurrentId2() == -1:
                    pivot -= 1
                    hasNextDocIdToProcess = False
                cumub = cumub + lists[pivot].getUB()
                if cumub > theta:
                    break

            if cumub <= theta or cumub == 0 or lists[0].getCurrentId2() == -1:
                hasNextDocIdToProcess = False

            if hasNextDocIdToProcess:

                pivot_id = lists[pivot].getCurrentId2()
                if pivot_id != lists[0].getCurrentId2():
                    for i in range(0, pivot):
                        if pivot_id != lists[i].getCurrentId2():
                            nextDocId, skipped0 = lists[i].nextge3(pivot_id)
                            skipped += skipped0

                score = 0
                for i in range(0, n):
                    if lists[i].getCurrentId2() != pivot_id:
                        break
                    #if lists[i].getCurrentId2() == pivot_id:
                    score = score + lists[i].getCurrentScore()
                    lists[i].next3()
                #
                topk.put(pivot_id, score)
                theta = topk.getTheta()
                #lists = self.sortListsByDocId(lists)
                # else:
                #     while lists[pivot].getCurrentId2() == pivot_id:
                #         pivot = pivot - 1
                #     nextDocId, skipped0 = lists[pivot].nextge3(pivot_id)
                #     skipped += skipped0
                #     lists, ulists = self.swapDown(lists, pivot)
                #
                # for i in range(0, n):
                #     if lists[i].getCurrentId2() < pivot_id:
                #         nextDocId, skipped0 = lists[i].nextge3(pivot_id)
                #         skipped += skipped0

        for i in range(0, len(lists0)):
            if lists0[i].getCurrentId2() != -1:
                nextDocId, skipped0 = lists0[i].nextge3(lists0[i].getMaxDocID() + 1)
                skipped += skipped0

        return topk, skipped

    def sortListsByDocId(self, lists) -> List:
        lists.sort(key=lambda x: x.getCurrentId2())
        listProcessed = []
        for i in range(0, len(lists)):
            if lists[i].getCurrentId2() == -1:
                listProcessed.append(lists[i])
        for list00 in listProcessed:
            lists.remove(list00)
            lists.append(list00)
        return lists

    def swapListsByDocId(self, lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentId2()
            #if (cdoc != math.inf):
            if (cdoc != -1):
                slists.append((cdoc, i))
        slists = sorted(slists, key=lambda x: x[0])
        #
        newLists = []
        for i in range(0, len(slists)):#len(lists)):
            j = slists[i][1]
            newLists.append(lists[j])
        #
        lists = newLists
        return lists

    def sortListsByUB(self, lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentId2()
            #if (cdoc != math.inf):
            if (cdoc != -1):
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
