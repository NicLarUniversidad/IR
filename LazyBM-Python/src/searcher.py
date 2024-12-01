from MetadataFilesManager import MetadataFilesManager
from QueryManager import QueryManager
from LazyBM import LazyBM

# metadataManager = MetadataFilesManager()
# termsDict = metadataManager.getTermsMetadata()
# searcher = LazyBM(termsDict)
# queryManager = QueryManager()
# topK = 5
# continues = 1
# while continues:
#     query = input("Ingrese una query o EXIT para salir\n")
#     if query == "EXIT":
#         continues = 0
#     else:
#         r, blockService = searcher.search(query, topK)
#         print(f"Resultados en el top {topK}:\n")
#         for i in range(0, len(r.rank)):
#             print(f"Doc: {r.rank[i]}, score:{r.scores[i]}")
#
#         print(f"Se saltaron {blockService.docIdSkipped} con el filtro MaxScore")
#         print(f"Se saltaron {blockService.docIdSkippedWithUb} con el filtro WAND")
#         print(f"Se leyeron {blockService.blocksRead} bloques")
#         print(f"Se leyeron {blockService.docIdRead} veces los DOC-ID")
#         print(f"Se saltaron {blockService.blockSkipped} bloques al saltar DOC-ID con el pivote")
