from FileManager import FileManager


class MetadataFilesManager(object):

    def __init__(self):
        self.fileManager = FileManager()

    def fileToDict(self, fileName):
        content = self.fileManager.readFile(fileName)
        lines = content.splitlines()
        data = dict()
        for line in lines:
            recordId = line.split(":")[0]
            recordStr = line.split(":")[1]
            data[recordId] = recordStr
        return data

    def getFilesMetadata(self):
        return self.fileToDict("fileIndex.txt")

    def getTermsMetadata(self):
        return self.fileToDict("termIndex.txt")
