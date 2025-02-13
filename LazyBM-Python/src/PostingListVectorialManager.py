import os
import struct

from PostingList import PostingList


class PostingListVectorialManager(object):

    def getPostingListByTermId(self, termId):
        postingList = PostingList(termId)
        termMetadata = self.loadMetadata(termId)
        if termMetadata is not None:
            offset = termMetadata[1]
            postingListSize = termMetadata[2]
            postingListFile = open('postingLists.dat', 'rb')
            recordFormat = 'I' + str(postingListSize) + "I" + str(postingListSize) + "I"
            recordLength = struct.calcsize(recordFormat)
            recordUnpack = struct.Struct(recordFormat).unpack_from
            postingListFile.seek(offset)
            data = postingListFile.read(recordLength)
            record = recordUnpack(data)
            docIdList = []
            i = 1
            for k in range(0, postingListSize):
                docIdList.append(record[i + k])
            frequencies = dict()
            i += postingListSize
            for k in range(0, postingListSize):
                frequencies[docIdList[k]] = record[i + k]
            postingListFile.close()
            postingList.docIdList = docIdList
            postingList.scores = frequencies
            return postingList
        else:
            return None

    def loadMetadata(self, termId):
        metadataFile = open('postingListsMetadata.dat', 'rb')
        metadataFormat = 'I Q Q'  # u-int, u-long-long, u-long-long -> id, start-at-byte, size
        metadataLength = struct.calcsize(metadataFormat)
        metadataUnpack = struct.Struct(metadataFormat).unpack_from
        offset = metadataLength * (termId - 1)
        if offset >= (os.path.getsize('postingListsMetadata.dat') - metadataLength):
            record = None
        else:
            metadataFile.seek(offset)
            data = metadataFile.read(metadataLength)
            record = metadataUnpack(data)
        metadataFile.close()
        return record
        # offset = metadataLength * (termId - 1)
        # metadataFile.seek(offset)
        # data = metadataFile.read(metadataLength)
        # record = metadataUnpack(data)
        # metadataFile.close()
        # return record
