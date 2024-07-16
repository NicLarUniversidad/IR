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

    def getQueries(self):
        return self.queries
