import math
import sys
from typing import List


class MaxScore(object):

    def __init__(self, termDict):
        self.termDict = termDict

    def processQuery(self, lists, topk):
        skipped = 0
        ub_lists = self.sortListsByUB(lists)  #  Lista con tuplas de: UB | ÍNDICE DE lists. Ordenada por UB
        # Acumulo los UB
        n = len(ub_lists)
        ub = [0] * n
        ub[0] = ub_lists[0][0] # Primer índice UB más chico, segundo índice: 0 valor UB, 1 índice
        for i in range(1, len(ub_lists)):
            ub[i] = ub[i - 1] + ub_lists[i][0]
        #   
        theta = 0
        current = self.MinimumDocID(lists)
        infinite = self.MaximumDocID(lists) + 1
        hasNextDocIdInEssentialPostingList = True
        # Guardo listas esenciales (ub por arriba de theta)
        essentialPostingList = []
        for l in ub_lists:
            essentialPostingList.append(lists[l[1]])

        while hasNextDocIdInEssentialPostingList:  # (pivot < n and current < infinite):
            score = 0
            currentDocId = self.getMinimunDocId(essentialPostingList, infinite)
            # Si todas las PL esenciales llegaron al final, termina el procesamiento
            if currentDocId == infinite:
                hasNextDocIdInEssentialPostingList = False
            else:
                # Salteo los doc ID de todas las posting list hasta el doc ID actual
                for i in range(len(ub_lists)):
                    pl = lists[ub_lists[i][1]]
                    nextDocId, skipped0 = pl.nextge3(current)
                    # Cuento los salteados
                    skipped += skipped0

                # Calculo el score del doc ID actual con la frecuencia de todas las listas
                for i in range(len(ub_lists)):
                    pl = lists[ub_lists[i][1]]
                    currentDocInList0 = pl.getCurrentDocID2()
                    # Si llegó al final va a devolver -1
                    if currentDocInList0 != -1:
                        # Si en la posting list está el doc ID actual
                        if currentDocInList0 == currentDocId:
                            # Se suma el score/frecuencia
                            score += pl.getCurrentScore()
                            # Cuando se obtuvo el score, avanzo al siguiente doc ID
                            pl.next2()

                # Se intenta colocar el doc ID si tiene un score mayor a 0
                if score > 0:
                    # Se va a entrar al siguiente if si el score es mayor a theta
                    if topk.put(current, score):
                        theta = topk.getMinScore()

                # Se actualizan posting lists esenciales (acumUb > theta)
                essentialPostingList = self.updateEssentialPostingLists(theta, ub_lists, ub, lists)

                # Si no hay más listas esenciales se termina el procesamiento
                if len(essentialPostingList) == 0:
                    hasNextDocIdInEssentialPostingList = False
                #
        for i in range(0, len(lists)):
            if lists[i].getCurrentId2() != -1:
                nextDocId, skipped0 = lists[i].nextge3(infinite)
                skipped += skipped0
        return topk, skipped

    def processQueryBackup(self, lists, topk):
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
                nextDocId, skipped0 = lists[i].nextge2(current)
                skipped += skipped0
                if lists[i].getCurrentDocID2() == current:
                    score = score + lists[i].getCurrentScore()
                    scoringOps += 1
                    lists[i].next()
                if current < lists[i].getCurrentDocID2() and nextd > lists[i].getCurrentDocID2() and current < lists[i].getCurrentDocID2()!=-1:
                    nextd = lists[i].getCurrentDocID2()
                    #
            for i in range(pivot - 1, -1, -1):
                if (score + ub[i]) <= theta:
                    break
                nextDocId, skipped0 = lists[i].nextge2(current)
                skipped += skipped0
                if lists[i].getCurrentDocID2() == current:
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
        for i in range(0, len(lists)):
            if lists[i].getCurrentId2() != -1:
                nextDocId, skipped0 = lists[i].nextge2(lists[i].getMaxDocID() + 1)
                skipped += skipped0
        return scoringOps, skipped

    def sortListsByDocId(lists: List) -> List:
        lists.sort(key=lambda x: x.getCurrentDocID2())
        return lists

    def swapListsByDocId(lists: List) -> List:
        slists = []
        for i in range(0, len(lists)):
            cdoc = lists[i].getCurrentDocID2()
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
            cdoc = lists[i].getCurrentDocID2()
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
            did.append(l.getCurrentDocID2())
        return (min(did))

    def getMinimunDocId(self, essentialPostingList, infinite):
        minimum = infinite
        for list in essentialPostingList:
            currentDocIdInList = list.getCurrentDocID2()
            if currentDocIdInList != -1:
                if currentDocIdInList < minimum:
                    minimum = currentDocIdInList
        return minimum

    def updateEssentialPostingLists(self, theta, ub_lists, ub, lists):
        essentialPostingList00 = []
        for i in range(len(ub)):
            if ub[i] > theta:
                essentialPostingList00.append(lists[ub_lists[i][1]])
        return essentialPostingList00
