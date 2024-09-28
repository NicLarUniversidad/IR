from IndexFactory import IndexFactory
from QueryFileReader import QueryFileReader

indexFactory = IndexFactory("files")

indexFactory.buildMemoryIndex()
# Remover comentario para ver cómo queda el índice
# for key in indexFactory.memoryIndex.postingLists:
#
#     postingList = indexFactory.memoryIndex.postingLists[key]
#     term = list(indexFactory.termKeyDic.keys())[list(indexFactory.termKeyDic.values()).index(postingList.termId)]
#     print(f"TermID {postingList.termId}, término: {term}. Posting List: {postingList.docIdList}")
# Recupero queries
queries = QueryFileReader().queries

