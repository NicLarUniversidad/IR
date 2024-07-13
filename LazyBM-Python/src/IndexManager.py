class IndexManager(object):

    def __init__(self):
        self.termIndex = dict()
        self.termIndexInverse = dict()
        self.fileIndex = dict()
        self.fileIndexInverse = dict()

    def toString(self, aDict):
        result = ""
        for key in aDict.keys():
            result += f"{key}:{aDict[key]}\n"
        return result

    def termIndexToString(self):
        return self.toString(self.termIndex)

    def termIndexInverseToString(self):
        return self.toString(self.termIndexInverse)

    def fileIndexToString(self):
        return self.toString(self.fileIndex)

    def fileIndexInverseToString(self):
        return self.toString(self.fileIndexInverse)
