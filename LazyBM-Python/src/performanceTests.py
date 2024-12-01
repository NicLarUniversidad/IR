import learn
from sklearn.ensemble import RandomForestClassifier

from IndexFactory import IndexFactory
from MemoryBlockMaxIndex import MemoryBlockMaxIndex
from QueryFileReader import QueryFileReader
from SearchManager import SearchManager



indexFactory = IndexFactory("files")

indexFactory.buildMemoryIndex()
# Remover comentario para ver cómo queda el índice
for key in indexFactory.memoryIndex.postingLists:

    postingList = indexFactory.memoryIndex.postingLists[key]
    term = list(indexFactory.termKeyDic.keys())[list(indexFactory.termKeyDic.values()).index(postingList.termId)]
    print(f"TermID {postingList.termId}, término: {term}. Doc IDs: {postingList.docIdList}. Scores: {postingList.scores}")
# Recupero queries
blockMaxIndex = MemoryBlockMaxIndex(indexFactory.memoryIndex)
queries = QueryFileReader().queries

termsDict = indexFactory.termKeyDic
# postingLists -> dict: term id -> PostingLists
searchManager = SearchManager(termDict=termsDict, postingLists=indexFactory.memoryIndex.postingLists, blockMaxIndex=blockMaxIndex)

searchManager.search("softwar produccion tecnologia incorpor libr", 2)
