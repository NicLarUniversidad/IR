import re

from FileManager import FileManager


class QueryFileReader(object):

    def __init__(self):
        fileManager = FileManager()
        queriesStr = fileManager.readFile("queries.doctrain.tsv")
        lines = queriesStr.splitlines()
        self.queries = dict()
        for line in lines:
            data = line.split()
            query_terms = ""
            for i in range(1, len(data)):
                query_terms += re.sub(r'\W+', '', data[i]) + " "
            self.queries[data[0]] = query_terms[:-1]

    def getQueries(self):
        return self.queries
