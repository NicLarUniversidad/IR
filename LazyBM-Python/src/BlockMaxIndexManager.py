import struct

from Block import Block


class BlockMaxIndexManager(object):

    def __init__(self):
        #TODO: Implementar cache
        self.maxRAM = 0

    def getFirstBlocks(self, termIdList):
        block = dict()
        for termId in termIdList:
            tId = int(termId)
            termBlock = self.getFirstBlock(tId)
            block[tId] = termBlock

        return block

    def getFirstBlock(self, termId):
        metadataRecord = self.getBlockMaxIndexMetadata(termId)

        blockSize = metadataRecord[1]
        blockCount = metadataRecord[2]
        docIdCount = metadataRecord[3]
        offset = metadataRecord[4]

        blockMaxIndexFile = open('blockMaxIndex.dat', 'rb')
        recordFormat = f"Id{blockSize}I{blockSize}d"
        recordSize = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from

        blockMaxIndexFile.seek(offset)
        data = blockMaxIndexFile.read(recordSize)
        record = recordUnpack(data)
        termBlock = Block(record, blockSize, blockCount, 1, docIdCount)

        blockMaxIndexFile.close()

        return termBlock

    def getNextBlock(self, termId, block):
        metadataRecord = self.getBlockMaxIndexMetadata(termId)

        blockSize = metadataRecord[1]
        blockCount = metadataRecord[2]
        docIdCount = metadataRecord[3]
        offset = metadataRecord[4]

        recordFormat = f"Id{blockSize}I{blockSize}d"
        recordSize = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from
        offset = offset + block.blockNumber * recordSize

        blockMaxIndexFile = open('blockMaxIndex.dat', 'rb')
        blockMaxIndexFile.seek(offset)
        data = blockMaxIndexFile.read(recordSize)
        record = recordUnpack(data)
        termBlock = Block(record, blockSize, blockCount, block.blockNumber + 1, docIdCount)

        blockMaxIndexFile.close()

        return termBlock

    def getBlockMaxIndexMetadata(self, termId):
        blockMaxIndexMetadataFile = open('blockMaxIndexMetadata.dat', 'rb')
        blockMaxMetadataRecordFormat = 'Q Q Q Q Q'  # term id, block size, block count, doc-id count, offset
        blockMaxMetadataRecordSize = struct.calcsize(blockMaxMetadataRecordFormat)
        metadataUnpack = struct.Struct(blockMaxMetadataRecordFormat).unpack_from
        offset = (termId - 1) * blockMaxMetadataRecordSize
        blockMaxIndexMetadataFile.seek(offset)
        data = blockMaxIndexMetadataFile.read(blockMaxMetadataRecordSize)
        blockMaxIndexMetadataFile.close()
        return metadataUnpack(data)

    def getBlockByDocId(self, termId, pivotDocId, block=None):
        if block is not None:
            blockNumber = block.blockNumber
        else:
            blockNumber = 0
        metadataRecord = self.getBlockMaxIndexMetadata(termId)

        blockSize = metadataRecord[1]
        blockCount = metadataRecord[2]
        docIdCount = metadataRecord[3]
        offset = metadataRecord[4]

        recordFormat = f"Id{blockSize}I{blockSize}d"
        recordSize = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from
        offset = offset + blockNumber * recordSize

        blockMaxIndexFile = open('blockMaxIndex.dat', 'rb')
        lastBlock = 0
        founded = 0
        record = []
        skipped = -1
        while not founded and not lastBlock:
            blockNumber + 1
            blockMaxIndexFile.seek(offset)
            data = blockMaxIndexFile.read(recordSize)
            record = recordUnpack(data)
            founded = record[0] > pivotDocId
            lastBlock = blockNumber < blockCount
            offset += recordSize
            blockCount += 1
            skipped += 1
        blockMaxIndexFile.close()

        if founded:
            block = Block(record, blockSize, blockCount, block.blockNumber + 1, docIdCount)

        return block, founded, skipped


