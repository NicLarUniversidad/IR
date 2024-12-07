from IndexFactory import IndexFactory
from MemoryBlockMaxIndex import MemoryBlockMaxIndex
from QueryFileReader import QueryFileReader
from SearchManager import SearchManager

top_k = 5
folderName = "wiki-large"
indexFactory = IndexFactory(folderName)

indexFactory.buildMemoryIndex()
blockMaxIndex = MemoryBlockMaxIndex(indexFactory.memoryIndex)
queries = QueryFileReader().queries

termsDict = indexFactory.termKeyDic
searchManager = SearchManager(termDict=termsDict, postingLists=indexFactory.memoryIndex.postingLists, blockMaxIndex=blockMaxIndex)
print("Generando los rankings")
f_ranking = open(f"ranking_{folderName}.txt", "w", encoding="utf-8")
f_skipped = open(f"skipped_{folderName}.txt", "w", encoding="utf-8")
f_skipped.write("QueryId,Algorithm,DocIdSkipped\n")
f_posting_length = open(f"posting_length_{folderName}.txt", "w", encoding="utf-8")
for queryIdx in queries:
    query = queries[queryIdx]
    results = searchManager.search(query, top_k)
    for result in results:
        topK = results[result][0]
        skipped = results[result][1]
        postingListsLength = results[result][2]
        ranking_str = f"{queryIdx},{result},"
        for i in range(0, len(topK.rank)):
            ranking_str += str(topK.rank[i]) + "," + str(topK.scores[i]) + ","
        f_ranking.write(ranking_str[:-1] + "\n")
        f_skipped.write(f"{queryIdx},{result},{str(skipped)}\n")
        posting_length_str = f"{queryIdx},{result},"
        for i in range(0, len(postingListsLength)):
            posting_length_str += str(postingListsLength[i]) + ","
        if len(postingListsLength) == 0:
            posting_length_str += ","
        f_posting_length.write(posting_length_str[:-1] + "\n")
f_ranking.close()
f_skipped.close()
f_posting_length.close()
