import os
import re
import struct

from bitarray import bitarray

from Block import Block
from BlockMaxIndexManager import BlockMaxIndexManager


class Compressor(object):

    def __init__(self):
        self.postingListManager = BlockMaxIndexManager()

    def compress(self, compressDocId=True, compressDGaps=True):
        print("Comprimiendo...")
        termId = 1
        blocks = self.postingListManager.getBlocksByDocId(termId)
        offset = 0
        dGpasOffset = 0
        self.deleteFiles(compressDocId, compressDGaps)
        compressedFile = None
        metadataCompressedFile = None
        dGapsFile = None
        metadataDGapsFile = None
        if compressDocId:
            compressedFile = open('compressedPostingList.dat', 'wb')
            metadataCompressedFile = open('compressedPostingListMetadata.dat', 'wb')
        if compressDGaps:
            dGapsFile = open('compressedDGaps.dat', 'wb')
            metadataDGapsFile = open('compressedDGapsMetadata.dat', 'wb')
        while blocks:
            print(f"Procesada posting list de term id: {termId}")
            if compressDocId:
                self.saveMetadata(termId, offset, blocks[0], metadataCompressedFile)
            if compressDGaps:
                self.saveMetadata(termId, dGpasOffset, blocks[0], metadataDGapsFile)
            for block in blocks:
                if compressDocId:
                    docIdBytes, scoreBytes = self.compressBlock(block)
                    offset += len(docIdBytes) + len(scoreBytes) + 8  # Add 8 bytes for next block offset
                    self.saveData(docIdBytes, scoreBytes, offset, compressedFile)

                # Delta gaps
                if compressDGaps:
                    docIdBytes, scoreBytes = self.compressBlockDGaps(block)
                    dGpasOffset += len(docIdBytes) + len(scoreBytes) + 8  # Add 8 bytes for next block offset
                    self.saveData(docIdBytes, scoreBytes, dGpasOffset, dGapsFile)

            termId += 1
            blocks = self.postingListManager.getBlocksByDocId(termId)
        if compressDocId:
            compressedFile.close()
            metadataCompressedFile.close()
        if compressDGaps:
            dGapsFile.close()
            metadataDGapsFile.close()

    def decompressD(self):
        print("Decomprimiendo...")
        postingLists = dict()
        termId = 1
        postingList = self.getDocIdPostingList(termId)
        while postingList:
            print("Decomprimiendo posting " + str(termId))
            postingLists[termId] = postingList
            postingList = self.getDocIdPostingList(termId)
            termId += 1
        return postingLists

    def decompressDGaps(self):
        print("Decomprimiendo...")
        postingLists = dict()
        termId = 1
        postingList = self.getDGapsPostingList(termId)
        while postingList:
            print("Decomprimiendo posting " + str(termId))
            postingLists[termId] = postingList
            postingList = self.getDGapsPostingList(termId)
            termId += 1
        return postingLists

    def compressBlock(self, block: Block):

        docIdsBits = ""
        for docId in block.getAllDocId():
            docIdsBits += self.getVByte(docId)

        frequenciesBits = ""
        for frequency in block.getAllScores():
            frequenciesBits += self.getEliasGamma(frequency)
        filling = len(frequenciesBits) % 8
        if filling > 0:
            frequenciesBits += "0" * filling

        fArray = bitarray(docIdsBits)
        docIdBytes = fArray.tobytes()
        fArray = bitarray(frequenciesBits)
        scoreBytes = fArray.tobytes()

        return docIdBytes, scoreBytes

    def compressBlockDGaps(self, block: Block):

        dGaps = block.getDeltaGaps()
        dGapsString = ""
        for dGap in dGaps:
            dGapsString += self.getVByte(dGap)

        frequenciesBits = ""
        for frequency in block.getAllScores():
            frequenciesBits += self.getEliasGamma(frequency)
        filling = len(frequenciesBits) % 8
        if filling > 0:
            frequenciesBits += "0" * filling

        fArray = bitarray(dGapsString)
        docIdBytes = fArray.tobytes()
        fArray = bitarray(frequenciesBits)
        scoreBytes = fArray.tobytes()

        return docIdBytes, scoreBytes

    def getEliasGamma(self, number):
        if number == 0:
            bitStr = "0"
        else:
            bitStr = "1"
            i = 0
            base = 2 ** i
            while base < number:
                bitStr = "0" + bitStr
                i += 1
                base = 2 ** i
            if i > 0:
                base = 2 ** (i - 1)
                bitStr = bitStr[1:]
            rest = number - base
            restBitStr = "0" * rest
            bitStr += restBitStr + "1"
        return bitStr

    def getVByte(self, number):
        bitStr = self.toBitString(number)
        bitStr = bitStr[::-1]
        sevenBitsList = re.findall('..?.?.?.?.?.?', bitStr)
        bitStr = ""
        i = 0
        while i < len(sevenBitsList):
            byteStr = sevenBitsList[i][::-1]
            filling = 7 - len(byteStr)
            if filling > 0:
                byteStr = "0" * filling + byteStr
            if i == 0:
                byteStr = "1" + byteStr
            else:
                byteStr = "0" + byteStr
            bitStr = byteStr + bitStr
            i += 1
        # print(f"getVByte Convertido {number} a {bitStr}")
        return bitStr

    def toBitString(self, number):
        hasNextBit = 1
        bitString = ""
        while hasNextBit:
            mod = number % 2
            number = number // 2
            bitString = str(mod) + bitString
            hasNextBit = number > 0
        return bitString

    def decompressVByte(self, bytesVByte):
        vByteStr = bytesVByte  # bytesVByte.to01()
        parts = self.splitBitString(vByteStr)
        docIdList = []
        docIdBits = ""
        hastNextByte = 1
        for part in parts:
            if not hastNextByte:
                docIdList.append(self.bitArrayToInt(docIdBits))
                docIdBits = ""
            docIdBits = docIdBits + part[1:]
            hastNextByte = part[0] == "1"
        if not hastNextByte:
            docIdList.append(self.bitArrayToInt(docIdBits))
        # print(docIdList)
        return docIdList

    def decompressEliasGama(self, bytesEliasGama):
        vByteStr = bytesEliasGama  # bytesEliasGama.to01()
        parts = vByteStr.split("1")
        i = 1
        docIdList = []
        docId = 0
        for part in parts:
            if i:  # Potencia
                docId = 2 ** len(part)
                i = 0
            else:  # Sumar
                docId += len(part)
                docIdList.append(docId)
                i = 1
        # print(docIdList)
        return docIdList

    def splitBitString(self, bitStr):
        i = 0
        bytesStr = []
        newByte = ""
        while i < len(bitStr):
            newByte += bitStr[i]
            i += 1
            if i % 8 == 0:
                bytesStr.append(newByte)
                newByte = ""
        if len(bytesStr) > 0:
            while len(bytesStr[len(bytesStr) - 1]) < 8:
                bytesStr[len(bytesStr) - 1] = bytesStr[len(bytesStr) - 1] + "0"
        return bytesStr

    def bitArrayToInt(self, bitArray):
        bitArray = bitArray[::-1]
        number = 0
        exponent = 0
        for bit in bitArray:
            if int(bit):
                number += 2 ** exponent
            exponent += 1
        return number

    def deleteFiles(self, compressDocId, compressDGaps):
        if compressDocId:
            f = open('compressedPostingList.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
            f = open('compressedPostingListMetadata.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        if compressDGaps:
            f = open('compressedDGaps.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
            f = open('compressedDGapsMetadata.dat', 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()

    def saveMetadata(self, termID, offset, block: Block, metadataCompressedFile):
        metadataRecordFormat = 'Q Q Q Q Q'   # term id, block size, block quantity, doc-id count, offset
        metadataRecord = struct.pack(metadataRecordFormat, termID, block.blockSize, block.blockCount, block.docIdCount, int(termID))
        metadataCompressedFile.write(metadataRecord)

    def saveData(self, docIdBytes, scoreBytes, offset, compressedFile):
        sizeDocId = len(docIdBytes)
        sizeFrequencies = len(scoreBytes)
        # Next block offset, byte array with doc id, byte array with frequencies
        recordFormat = f'Q{sizeDocId}B{sizeFrequencies}B'
        record = struct.pack(recordFormat, offset, *docIdBytes, *scoreBytes)
        compressedFile.write(record)

    def loadMetadata(self, termId, fileName):
        f = open(fileName, 'rb')
        metadataFormat = 'I Q Q Q'
        metadataLength = struct.calcsize(metadataFormat)
        metadataUnpack = struct.Struct(metadataFormat).unpack_from
        offset = metadataLength * (termId - 1)
        if offset >= (os.path.getsize(fileName) - metadataLength):
            record = None
        else:
            f.seek(offset)
            data = f.read(metadataLength)
            record = metadataUnpack(data)
        f.close()
        return record

    def loadMetadataDGaps(self, termId):
        return self.loadMetadata(termId, 'compressedPostingListMetadata.dat')

    def loadMetadataDodId(self, termId):
        return self.loadMetadata(termId, 'compressedDGapsMetadata.dat')

    def getRecord(self, offset, docIdSize, frequencySize, fileName):
        f = open(fileName, 'rb')
        recordFormat = '=I' + str(docIdSize) + "B" + str(frequencySize) + "B"
        recordLength = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from
        f.seek(offset)
        data = f.read(recordLength)
        record = recordUnpack(data)
        f.close()
        docIds = []
        frequencies = []
        for i in range(1, docIdSize):
            docIds.append(record[i])
        for i in range(docIdSize + 1, frequencySize + docIdSize):
            frequencies.append(record[i])
        return self.listToBitString(docIds), self.listToBitString(frequencies)

    def getDocIdPostingList(self, termId):
        metadata = self.loadMetadataDodId(termId)
        if metadata is None:
            return None
        offset = metadata[1]
        docIdSize = metadata[2]
        frequencySize = metadata[3]
        docIdBytes, frequenciesBytes = self.getRecord(offset, docIdSize, frequencySize, 'compressedPostingList.dat')
        postingList = VectorialPostingList(termId)
        docIdList = self.decompressVByte(docIdBytes)
        postingList.docIdList = docIdList
        frequencies = self.decompressEliasGama(docIdBytes)
        postingList.scores = frequencies
        return postingList

    def getDGapsPostingList(self, termId):
        metadata = self.loadMetadataDGaps(termId)
        if metadata is None:
            return None
        offset = metadata[1]
        docIdSize = metadata[2]
        frequencySize = metadata[3]
        docIdBytes, frequenciesBytes = self.getRecord(offset, docIdSize, frequencySize, 'compressedDGaps.dat')
        postingList = VectorialPostingList(termId)
        dGaps = self.decompressVByte(docIdBytes)
        frequencies = self.decompressEliasGama(docIdBytes)
        postingList.restoreWithDeltaGaps(dGaps, frequencies)
        return postingList

    # def toBitString(self, byteValue):
    #     bitString = ""
    #     for i in range(1, 8):
    #         rest = byteValue % 2
    #         bitString += str(rest)
    #         byteValue //= 2
    #     return bitString

    def listToBitString(self, byteList):
        bitString = ""
        for byte in byteList:
            bitString = self.toBitString(byte) + bitString
        return bitString
