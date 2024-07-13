from QueryManager import QueryManager
from LazyBM import LazyBM

searcher = LazyBM()
queryManager = QueryManager()
topK = 5
continues = 1
while continues:
    query = input("Ingrese una query o EXIT para salir\n")
    if query == "EXIT":
        continues = 0
    else:
        r = searcher.search(query, topK)
        print(f"Resultados en el top {topK}:\n")
        for i in range(0, len(r.rank)):
            print(f"Doc: {r.rank[i]}, score:{r.scores[i]}")
