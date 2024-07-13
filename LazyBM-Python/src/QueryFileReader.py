from FileManager import FileManager


class QueryFileReader(object):

    def __init__(self):
        fileManager = FileManager()
        queriesStr = fileManager.readFile("eff-10K-queries.txt")
        lines = queriesStr.splitlines()
        self.queries = dict()
        for line in lines:
            data = line.split(":")
            self.queries[data[0]] = data[1]

    def getTwoTermQueries(self):
        result = dict()
        for key in self.queries.keys():
            data = self.queries[key].split()
            if len(data) == 2:
                result[key] = [data[0], data[1]]
        return result

    def getThreeTermQueries(self):
        result = dict()
        for key in self.queries.keys():
            data = self.queries[key].split()
            if len(data) == 3:
                result[key] = [data[0], data[1], data[2]]
        return result
