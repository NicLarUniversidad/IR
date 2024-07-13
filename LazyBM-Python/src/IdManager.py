class IdManager(object):

    def assignIdToFiles(self, files):
        fileIds = dict()
        fileIdInverse = dict()
        fileId = 1
        for file in files:
            fileIds[fileId] = file
            fileIdInverse[file] = fileId
            fileId += 1
        return fileIds, fileIdInverse
