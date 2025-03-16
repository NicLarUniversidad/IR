import time

from LazyBM2 import LazyBM
from MaxScore import MaxScore
from MemoryBlockMaxIndex import MemoryBlockMaxIndex
from MemoryBlockMaxPostingList import MemoryBlockMaxPostingList
from MetadataFilesManager import MetadataFilesManager
from PostingList import PostingList
from PostingListVectorialManager import PostingListVectorialManager
from QueryManager import QueryManager
from TopK import TopK
from TopkAlgorithms import TopkAlgorithms
from Wand import Wand


class SearchManager(object):

    def __init__(self, algorithm=None, termDict=None, postingLists=None, blockMaxIndex=None, onDisk = False):
        if postingLists is None:
            postingLists = dict()
        if postingLists is None:
            postingLists = []
        self.blockMaxIndex = blockMaxIndex
        self.algorithms = dict()
        # if algorithm is not None:
        #
        #     if algorithm == TopkAlgorithms.LAZY_BM:
        #         self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)
        #
        # if algorithm is None or len(self.algorithms) == 0:
            #self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(termDict)
        self.algorithms[TopkAlgorithms.MAX_SCORE] = MaxScore(termDict)
        self.algorithms[TopkAlgorithms.WAND] = Wand(termDict)
        if blockMaxIndex is not None or onDisk:
            self.algorithms[TopkAlgorithms.LAZY_BM] = LazyBM(blockMaxIndex)
        self.queryManager = QueryManager()
        self.termDict = termDict
        if postingLists is None:
            postingLists = dict()
        self.postingLists = postingLists
        self.onDisk = onDisk
        self.postingListManager = PostingListVectorialManager()
        if onDisk:
            metadataManager = MetadataFilesManager()
            self.termDict = metadataManager.getTermsMetadata()
            self.blockMaxIndex = MemoryBlockMaxIndex()

    def search(self, query, topKN, queryId = None, countSkipped = True):
        queryTerms = self.queryManager.parseQuery(query)
        queryTermIds = []
        for term in queryTerms:
            if term in self.termDict:
                queryTermIds.append(self.termDict[term])
        results = dict()
        if len(queryTerms) > 0:
            queryPostingsLists = []
            queryBlocks = []
            postingLen = []
            for termId in queryTermIds:
                if self.onDisk:
                    postingList = self.postingListManager.getPostingListByTermId(int(termId))
                    self.postingLists[termId] = postingList
                    if postingList is not None:
                        blockMax = MemoryBlockMaxPostingList(termId, postingList)
                        self.blockMaxIndex.postingLists[termId] = blockMax

                if self.postingLists[termId] is not None:
                    if len(self.postingLists[termId].docIdList) > 0:
                        if termId in self.postingLists:
                            self.postingLists[termId].index = 0
                            self.postingLists[termId].infinite = 0
                            self.postingLists[termId].currentDocId = self.postingLists[termId].docIdList[0]
                            queryPostingsLists.append(self.postingLists[termId])
                            # print(f"Posting term id: {termId}: {self.postingLists[termId].docIdList}")
                            # print(f"        Scores:: {self.postingLists[termId].scores}")
                            postingLen.append(len(self.postingLists[termId].docIdList))
                        if self.blockMaxIndex is not None and termId in self.blockMaxIndex.postingLists:
                            self.blockMaxIndex.postingLists[termId].infinite = 0
                            self.blockMaxIndex.postingLists[termId].index = 0
                            queryBlocks.append(self.blockMaxIndex.postingLists[termId])
                            # print(f"Posting term id: {termId}: ")
                            # for block in self.blockMaxIndex.postingLists[termId].blocks:
                            #     print(f"                            {block.docIdList}")
                            #     print(f"                     Scores:{block.scores}")
            if len(queryPostingsLists) > 0:
                topK = TopK(topKN)
                skipped = 0
                for algorithm in self.algorithms:
                    #lengthPostingList = 0
                    # for termId in self.postingLists:
                    #     if self.postingLists[termId] is not None:
                    #         lengthPostingList += len(self.postingLists[termId].docIdList)
                    # if algorithm == TopkAlgorithms.WAND and lengthPostingList > 100000:
                    #     print(f"Skipping query: {queryId}, large: {lengthPostingList} for WAND")
                    #     results[algorithm] = (topK, skipped, postingLen)
                    #else:
                    searcher = self.algorithms[algorithm]
                    topK = TopK(topKN)

                    for termId in queryTermIds:
                        if termId in self.postingLists and self.postingLists[termId] is not None:
                            self.postingLists[termId].index = 0
                            self.postingLists[termId].infinite = 0
                    initTime =  time.time()
                    if countSkipped:
                        if algorithm != TopkAlgorithms.LAZY_BM:
                            ranking, skipped = searcher.processQuery(queryPostingsLists, topK)
                        else:
                            ranking, skipped = searcher.processQuery(queryBlocks, topK)
                    else:
                        skipped = 0
                        if algorithm != TopkAlgorithms.LAZY_BM:
                            searcher.noCountProcessQuery(queryPostingsLists, topK)
                        else:
                            searcher.noCountProcessQuery(queryBlocks, topK)
                    finishTime = time.time()

                    results[algorithm] = (topK, skipped, postingLen, finishTime - initTime)
            else:
                for algorithm in self.algorithms:
                    results[algorithm] = (TopK(topKN), 0, [], 0)
        return results
