import math


class Bm25Calculator(object):

    def __init__(self, N, b=0.75, k1=1):
        self.b = b
        self.k1 = k1
        self.N = N

    def calculateBij(self, frequency, docLength, averageLength):
        return ((self.k1 + 1) * frequency) / (self.k1 * ((1 - self.b) + self.b * docLength/averageLength) + frequency)

    def bm25dq(self, frequency, docLength, averageLength, ni):
        bij = self.calculateBij(frequency, docLength, averageLength)
        return bij * math.log((self.N - ni + 0.5) / ni + 0.5)
