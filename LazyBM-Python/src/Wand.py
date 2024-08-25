class Wand(object):

    def DAAT_wand(lists, topk):    
        scoringOps = 0
        #
        theta = 0
        infinite = MaximumDocID(lists)+1
        lists  = swapListsByDocId(lists)    
        ulists = makeUBList(lists)
        n = len(lists)
        #
        while True:
            pivot = 0
            cumub = 0
            
            for pivot in range(0, n):
                if lists[pivot].getCurrentDocID() >= infinite or lists[pivot].getCurrentDocID() == -1:
                    break
                cumub = cumub + ulists[pivot]
                if cumub > theta:
                    break

            if cumub <= theta:
                break

            pivot_id = lists[pivot].getCurrentDocID()
            if pivot_id == lists[0].getCurrentDocID():
                score = 0
                for i in range(0, n):
                    if lists[i].getCurrentDocID() != pivot_id:
                        break
                    score = score + lists[i].getCurrentScore()
                    lists[i].next()
                    scoringOps = scoringOps + 1
                #
                topk.put(score, pivot_id)
                theta = topk.getMinScore()
                lists = sortListsByDocId(lists)
            else:     
                while lists[pivot].getCurrentDocID() == pivot_id:
                    pivot = pivot - 1
                lists[pivot].nextge(pivot_id)
                lists, ulists = swapDown(lists, pivot)
            #
        #
        return scoringOps
