import os
import struct
import time

from VectorialPostingListBuilder import VectorialPostingListBuilder


class PostingListVectorialFactory(object):

    def __init__(self, maxSize):
        self.postingLists = dict()
        self.maxSize = maxSize
        self.filesOnMemory = 0
        self.totalProcessTime = 0
        self.mergeTime = 0
        self.startTime = 0
        self.parts = 0

    def loadToMemory(self, termsFromFileDict, fileId):
        if termsFromFileDict is not None:
            for term in termsFromFileDict:
                if int(term) not in self.postingLists:
                    self.postingLists[int(term)] = VectorialPostingListBuilder(term)
                self.postingLists[int(term)].addDocId(fileId, termsFromFileDict[term])

    def saveToDisk(self, vocabulary):
        print("Guardando a disco")
        self.parts += 1
        initMergeTime = time.time()
        name = "postingListsMetadata-part" + str(self.parts)
        metadataFile = open(name + '.dat', 'wb+')
        metadataFile.close()
        metadataFile = open(name + '.dat', 'wb')
        name = "postingLists-part" + str(self.parts)
        postingListFile = open(name + '.dat', 'wb+')
        postingListFile.close()
        postingListFile = open(name + '.dat', 'wb')
        eof = 0
        metadataFile.seek(0)
        for termId in sorted(vocabulary):
            size = 0
            if int(termId) in self.postingLists:
                size = len(self.postingLists[int(termId)].docIdList)
            metadataRecordFormat = 'I Q Q'
            metadataRecord = struct.pack(metadataRecordFormat, int(termId), int(eof), size)
            metadataFile.write(metadataRecord)

            if size > 0:
                postingListToSave = self.postingLists[int(termId)].docIdList
                frequencies = self.postingLists[int(termId)].getSortedScores()
                recordFormat = "I" + str(len(postingListToSave)) + "I" + str(len(postingListToSave)) + "I"
                recordLength = struct.calcsize(recordFormat)
                freqDict = dict()
                for i in range(len(postingListToSave)):
                    freqDict[postingListToSave[i]] = frequencies[i]
                postingListToSave.sort()
                sortedFreq = []
                for docId in postingListToSave:
                    sortedFreq.append(freqDict[docId])
                record = struct.pack(recordFormat, int(termId), *postingListToSave, *sortedFreq)
                postingListFile.write(record)
                eof += recordLength
        metadataFile.close()
        postingListFile.close()

        self.postingLists = dict()
        self.filesOnMemory = 0
        endMergeTime = time.time()
        self.mergeTime += endMergeTime - initMergeTime

    def add(self, termsFromFileDict, fileId, vocabulary):
        if self.filesOnMemory > self.maxSize:
            self.flush(vocabulary)
        self.filesOnMemory += 1
        self.loadToMemory(termsFromFileDict, fileId)

    def flush(self, vocabulary):
        if self.filesOnMemory > 0:
            self.saveToDisk(vocabulary)

    def getPostingListsFromDisk(self, partNumber, termId, postingList, haveNext):
        if os.path.isfile(f"postingListsMetadata-part{partNumber}.dat") and os.path.isfile(f"postingLists-part{partNumber}.dat"):
            # and os.path.getsize("postingListsMetadata-part{partNumber}.dat") > 0):
            metadataFile = open(f"postingListsMetadata-part{partNumber}.dat", 'rb')
            postingListFile = open(f"postingLists-part{partNumber}.dat", 'rb')
            metadataFormat = 'I Q Q'  # u-int, u-long-long, u-long-long, char[15] -> id, start-at-byte, size
            metadataLength = struct.calcsize(metadataFormat)
            metadataUnpack = struct.Struct(metadataFormat).unpack_from
            offset = metadataLength * (int(termId) - 1)
            if offset < os.path.getsize(f"postingListsMetadata-part{partNumber}.dat") - metadataLength:
                haveNext = True
                metadataFile.seek(offset)
                data = metadataFile.read(metadataLength)
                metadataRecord = metadataUnpack(data)
                startAt = metadataRecord[1]
                size = metadataRecord[2]
                if size > 0:
                    postingListFile.seek(startAt)
                    recordFormat = 'I' + str(size) + "I" + str(size) + "I"
                    recordLength = struct.calcsize(recordFormat)
                    recordUnpack = struct.Struct(recordFormat).unpack_from
                    data = postingListFile.read(recordLength)
                    record = recordUnpack(data)
                    docIds = []
                    frequencies = []
                    for i in range(1, size + 1):
                        docIds.append(record[i])
                    for i in range(size + 1, size*2 + 1):
                        frequencies.append(record[i])
                    postingList = self.addByFileId(postingList, termId, docIds, frequencies)
            metadataFile.close()
            postingListFile.close()

        return postingList, haveNext

    def deleteFiles(self):
        if os.path.isfile("postingLists.dat"):
            f = open('postingLists.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        if os.path.isfile("postingListsMetadata.dat"):
            f = open('postingListsMetadata.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        if os.path.isfile("deltaGaps.dat"):
            f = open('deltaGaps.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()

    def addByFileId(self, postingListDict, termId, docIds, frequencies):
        index = 0
        while index < len(docIds):
            if termId in postingListDict:
                postingListDict[termId].append((docIds[index], frequencies[index]))
            else:
                postingListDict[termId] = [(docIds[index], frequencies[index])]
            index += 1
        return postingListDict

    def mergePostingLists(self, termIndex):
        print("Merge de bloques")
        self.deleteFiles()
        postingListFile = open('postingLists.dat', 'wb')
        metadataFile = open('postingListsMetadata.dat', 'wb')
        eof = 0
        for termId in termIndex:
            termIdInt = int(termId)
            postingListDict = dict()
            for part in range(1, self.parts + 1):
                postingListDict = self.getPostingListsFromDisk(part, termIdInt, postingListDict)

            if termIdInt in postingListDict:
                size = len(postingListDict[termIdInt])
                metadataRecordFormat = 'I Q Q'
                #  metadataRecordLength = struct.calcsize(metadataRecordFormat)
                metadataRecord = struct.pack(metadataRecordFormat, int(termIdInt), eof, size)
                metadataFile.write(metadataRecord)
                if size > 0:
                    docIdList = []
                    frequenciesList = []
                    for tuple0 in postingListDict[termIdInt]:
                        docIdList.append(tuple0[0])
                        frequenciesList.append(tuple0[1])

                    postingListFile.seek(eof)
                    recordFormat = "I" + str(size) + "I" + str(size) + "I"
                    recordLength = struct.calcsize(recordFormat)

                    record = struct.pack(recordFormat, int(termIdInt), *docIdList, *frequenciesList)
                    postingListFile.write(record)
                    eof += recordLength
        postingListFile.close()
        metadataFile.close()

    def startCount(self):
        self.startTime = time.time()

    def finish(self):
        self.totalProcessTime = time.time() - self.startTime

    def getIndexTime(self):
        return self.totalProcessTime - self.mergeTime

    def getPostingListsFromDiskOnResume(self, partNumber, termId, postingList, parts):
        if os.path.isfile(f"postingListsMetadata-part{partNumber}.dat") and os.path.isfile(f"postingLists-part{partNumber}.dat"):
            # and os.path.getsize("postingListsMetadata-part{partNumber}.dat") > 0):
            metadataFile = open(f"postingListsMetadata-part{partNumber}.dat", 'rb')
            postingListFile = open(f"postingLists-part{partNumber}.dat", 'rb')
            metadataFormat = 'I Q Q'  # u-int, u-long-long, u-long-long, char[15] -> id, start-at-byte, size
            metadataLength = struct.calcsize(metadataFormat)
            metadataUnpack = struct.Struct(metadataFormat).unpack_from
            offset = metadataLength * (int(termId) - 1)
            if offset < os.path.getsize(f"postingListsMetadata-part{partNumber}.dat") - metadataLength:
                metadataFile.seek(offset)
                data = metadataFile.read(metadataLength)
                metadataRecord = metadataUnpack(data)
                startAt = metadataRecord[1]
                size = metadataRecord[2]
                if size > 0:
                    postingListFile.seek(startAt)
                    recordFormat = 'I' + str(size) + "I" + str(size) + "I"
                    recordLength = struct.calcsize(recordFormat)
                    recordUnpack = struct.Struct(recordFormat).unpack_from
                    data = postingListFile.read(recordLength)
                    record = recordUnpack(data)
                    docIds = []
                    frequencies = []
                    for i in range(1, size + 1):
                        docIds.append(record[i])
                    for i in range(size + 1, size*2 + 1):
                        frequencies.append(record[i])
                    postingList = self.addByFileId(postingList, termId, docIds, frequencies)
            metadataFile.close()
            postingListFile.close()

        return postingList

    def mergeResume(self, lastTermId, parts):
        print("Merge de bloques")
        eof = os.path.getsize('C:\\Users\\Rikudo\\Documents\\GitHub\\IR\\LazyBM-Python\\src\\postingLists.dat')
        postingListFile = open('postingLists.dat', 'r+b')
        postingListFile.seek(eof)
        metadataFile = open('postingListsMetadata.dat', 'r+b')
        metadataFile.seek(os.path.getsize('C:\\Users\\Rikudo\\Documents\\GitHub\\IR\\LazyBM-Python\\src\\postingListsMetadata.dat'))
        termId = lastTermId
        haveNext = True
        while haveNext:
            termId += 1
            haveNext = False
            #print(f"TermId : {termId}, offset : {eof}")
            termIdInt = termId
            postingListDict = dict()
            for part in range(1, parts):
                postingListDict, haveNext = self.getPostingListsFromDisk(part, termIdInt, postingListDict, haveNext)

            if termIdInt in postingListDict:
                size = len(postingListDict[termIdInt])
                metadataRecordFormat = 'I Q Q'
                #  metadataRecordLength = struct.calcsize(metadataRecordFormat)
                metadataRecord = struct.pack(metadataRecordFormat, int(termIdInt), eof, size)
                metadataFile.write(metadataRecord)
                if size > 0:
                    docIdList = []
                    frequenciesList = []
                    for tuple0 in postingListDict[termIdInt]:
                        docIdList.append(tuple0[0])
                        frequenciesList.append(tuple0[1])

                    postingListFile.seek(eof)
                    recordFormat = "I" + str(size) + "I" + str(size) + "I"
                    recordLength = struct.calcsize(recordFormat)

                    record = struct.pack(recordFormat, int(termIdInt), *docIdList, *frequenciesList)
                    postingListFile.write(record)
                    eof += recordLength
        postingListFile.close()
        metadataFile.close()