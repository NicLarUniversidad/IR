class TopK(object):

    def __init__(self, k):
        self.k = k
        self.scores = []
        self.rank = []
        self.theta = 0

    def put(self, docId, score):
        idx = 0
        while len(self.scores) > idx and self.scores[idx] > score:
            idx += 1
        if idx <= self.k:
            self.scores.insert(idx, score)
            self.rank.insert(idx, docId)
            if len(self.rank) > self.k:
                self.scores.remove(self.scores[self.k])
                self.rank.remove(self.rank[self.k])
            if len(self.rank) >= self.k:
                self.theta = self.scores[self.k - 1]
            else:
                self.theta = 0
            return True
        else:
            return False

    def getTheta(self):
        return self.theta

    def getMinScore(self):
        return self.getTheta()
