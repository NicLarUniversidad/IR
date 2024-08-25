class MaxScore(object):

    def DAAT_maxscore(lists, topk):    
        scoringOps = 0
        #
        ub_lists = sortListsByUB(lists)    
        # Acumulo los UB
        n  = len(ub_lists)
        ub = [0] * n
        ub[0] = ub_lists[0][0]    
        for i in range(1, len(ub_lists)):
            ub[i] = ub[i-1] + ub_lists[i][0]
        #   
        theta = 0
        pivot = 0    
        current  = MinimumDocID(lists)
        infinite = MaximumDocID(lists)+1
        
        while (pivot < n and current < infinite):
            score = 0
            nextd = infinite
            #
            for i in range(pivot, n):
                if lists[i].getCurrentDocID() == current:
                    score = score + lists[i].getCurrentScore()
                    scoringOps += 1
                    lists[i].next()
                if lists[i].getCurrentDocID() < nextd and lists[i].getCurrentDocID() != math.inf:
                    nextd = lists[i].getCurrentDocID()                       
            #
            for i in range(pivot-1, -1, -1):
                if (score + ub[i]) <= theta:
                    break
                lists[i].nextge(current)
                if lists[i].getCurrentDocID() == current:
                    score = score + lists[i].getCurrentScore()
                    scoringOps = scoringOps + 1
            #
            if topk.put(score, current):
                theta = topk.getMinScore()
                while pivot < n and ub[pivot] <= theta:
                    pivot = pivot + 1
            #
            current = nextd
            #               
        return scoringOps