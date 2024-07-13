import math
import os
import struct
import time

from VectorialPostingList import VectorialPostingList
from Bm25Calculator import Bm25Calculator


class BlockMaxIndexFactory(object):

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
                    self.postingLists[int(term)] = VectorialPostingList(term)
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

    def getPostingListsFromDisk(self, partNumber, termId, postingList):
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
                    for i in range(0, size):
                        docIds.append(record[1 + i])
                    for i in range(size, size*2):
                        frequencies.append(record[1 + i])
                    postingList = self.addByFileId(postingList, termId, docIds, frequencies)
            metadataFile.close()
            postingListFile.close()

        return postingList

    def deleteFiles(self):
        if os.path.isfile('blockMaxIndex.dat'):
            f = open('blockMaxIndex.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        if os.path.isfile('blockMaxIndexMetadata.dat'):
            f = open('blockMaxIndexMetadata.dat', 'wb+')
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

    def mergePostingLists(self, termIndex, N, averageLength, fileLengths):
        print("Merge de bloques")
        self.deleteFiles()
        blockMaxIndexFile = open('blockMaxIndex.dat', 'wb')
        blockMaxIndexMetadataFile = open('blockMaxIndexMetadata.dat', 'wb')
        offset = 0
        infiniteValue = 0
        blockMaxMetadataRecordFormat = 'Q Q Q Q Q'  # term id, block size, block count, doc-id count, offset
        bm25Calculator = Bm25Calculator(N)
        for termId in termIndex:
            termIdInt = int(termId)
            postingListDict = dict()
            for part in range(1, self.parts + 1):
                postingListDict = self.getPostingListsFromDisk(part, termIdInt, postingListDict)

            if termIdInt in postingListDict:
                docIdList = []
                scoreList = []
                for tuple0 in postingListDict[termIdInt]:
                    docId = tuple0[0]
                    docIdList.append(docId)
                    score = bm25Calculator.calculateBij(tuple0[1], fileLengths[int(docId)], averageLength)
                    scoreList.append(score)

                # Armo índice BlockMax
                postingListSize = len(docIdList)
                blocksCount = int(math.sqrt(postingListSize))
                blockSize = int(postingListSize / blocksCount)
                if postingListSize / blocksCount > blockSize:
                    blocksCount += 1
                blockMaxRecord = struct.pack(blockMaxMetadataRecordFormat, int(termId), blockSize, blocksCount, postingListSize, offset)
                blockMaxIndexMetadataFile.write(blockMaxRecord)
                for i in range(blocksCount):
                    firstDocId = i * blockSize
                    blockDocIds = []
                    blockScores = []

                    for j in range(blockSize):
                        if firstDocId + j < len(docIdList):
                            blockDocIds.append(docIdList[firstDocId + j])
                            blockScores.append(scoreList[firstDocId + j])
                        else:
                            blockDocIds.append(-1)
                            blockScores.append(0)

                    while len(blockDocIds) < blockSize:
                        blockDocIds.append(infiniteValue)
                        blockScores.append(0)

                    maxDocId = max(blockDocIds)
                    maxFrequency = max(blockScores)

                    blockMaxRecordFormat = "Id" + str(blockSize) + "I" + str(blockSize) + "d"  # Max Doc-id, Max Freq, doc-ids, frequencies
                    blockMaxRecordSize = struct.calcsize(blockMaxRecordFormat)
                    blockMaxRecord = struct.pack(blockMaxRecordFormat, maxDocId, float(maxFrequency), *blockDocIds, *blockScores)
                    blockMaxIndexFile.write(blockMaxRecord)
                    offset += blockMaxRecordSize

        blockMaxIndexFile.close()
        blockMaxIndexMetadataFile.close()
        self.deleteParts(self.parts)

    def startCount(self):
        self.startTime = time.time()

    def finish(self):
        self.totalProcessTime = time.time() - self.startTime

    def getIndexTime(self):
        return self.totalProcessTime - self.mergeTime

    def deleteParts(self, partsCount):
        for partNumber in range(1, partsCount + 1):
            if os.path.isfile(f"postingListsMetadata-part{partNumber}.dat") and os.path.isfile(f"postingLists-part{partNumber}.dat"):
                os.remove(f"postingLists-part{partNumber}.dat")
                os.remove(f"postingListsMetadata-part{partNumber}.dat")
