import os
import struct

from termcolor import colored

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
        blockMaxMetadataRecordFormat = 'Q Q Q Q Q'  # term id, block size, block count, doc-id count, offset
        blockMaxMetadataRecordSize = struct.calcsize(blockMaxMetadataRecordFormat)
        metadataUnpack = struct.Struct(blockMaxMetadataRecordFormat).unpack_from
        offset = (termId - 1) * blockMaxMetadataRecordSize
        if offset > os.path.getsize('blockMaxIndexMetadata.dat') - blockMaxMetadataRecordSize:
            print(colored(f'Se intentó acceder al byte {offset}, pero el archivo tiene{os.path.getsize("blockMaxIndexMetadata.dat")} bytes', 'red'))
            # Si el offset es más grande que el archivo, entocnes se está buscando un ID que no existe en el índice
            return None
        else:
            blockMaxIndexMetadataFile = open('blockMaxIndexMetadata.dat', 'rb')
            if offset > os.path.getsize('blockMaxIndexMetadata.dat'):
                print(f"Term id {termId} ")
                print(f"Block-size {blockMaxMetadataRecordSize} ")
                print(f"File too shot: offset {offset}, file size {os.path.getsize('blockMaxIndexMetadata.dat')}")
            blockMaxIndexMetadataFile.seek(offset)
            data = blockMaxIndexMetadataFile.read(blockMaxMetadataRecordSize)
            blockMaxIndexMetadataFile.close()
            return metadataUnpack(data)

    def getBlockByDocId(self, termId, pivotDocId, block=None):
        if block is not None:
            blockNumber = block.blockNumber
        else:
            blockNumber = 1
        metadataRecord = self.getBlockMaxIndexMetadata(termId)

        blockSize = metadataRecord[1]
        blockCount = metadataRecord[2]
        docIdCount = metadataRecord[3]
        offset = metadataRecord[4]

        recordFormat = f"Id{blockSize}I{blockSize}d"
        recordSize = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from
        offset = offset + (blockNumber - 1) * recordSize

        blockMaxIndexFile = open('blockMaxIndex.dat', 'rb')
        lastBlock = 0
        founded = 0
        record = []
        skipped = -1
        while not founded and not lastBlock:
            blockNumber + 1
            if offset <= os.path.getsize("blockMaxIndex.dat") - recordSize:
                blockMaxIndexFile.seek(offset)
                data = blockMaxIndexFile.read(recordSize)
                record = recordUnpack(data)
                founded = record[0] > pivotDocId
                lastBlock = blockNumber < blockCount
                offset += recordSize
                skipped += 1
            else:
                print(f"Se quizo acceder al offset {offset} bytes en el archivo blockMaxIndex.dat")
                lastBlock = True
                skipped += 1
        blockMaxIndexFile.close()

        if founded:
            block = Block(record, blockSize, blockCount, block.blockNumber + 1, docIdCount)

        return block, founded, skipped

    def getBlocksByDocId(self, termId):
        metadataRecord = self.getBlockMaxIndexMetadata(termId)
        blockSize = metadataRecord[1]
        blockCount = metadataRecord[2]
        docIdCount = metadataRecord[3]
        offset = metadataRecord[4]
        blocks = []
        blockMaxIndexFile = open('blockMaxIndex.dat', 'rb')
        recordFormat = f"Id{blockSize}I{blockSize}d"
        recordSize = struct.calcsize(recordFormat)
        recordUnpack = struct.Struct(recordFormat).unpack_from
        for i in range(blockSize):
            blockMaxIndexFile.seek(offset)
            data = blockMaxIndexFile.read(recordSize)
            record = recordUnpack(data)
            offset += recordSize
            block = Block(record, blockSize, blockCount, 1 + i, docIdCount)
            blocks.append(block)
        blockMaxIndexFile.close()

        return blocks



