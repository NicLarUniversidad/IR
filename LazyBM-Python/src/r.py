from SearchManager import SearchManager
from MetadataFilesManager import MetadataFilesManager
from QueryFileReader import QueryFileReader
from QueryManager import QueryManager

queryFileReader = QueryFileReader()
queries = queryFileReader.getQueries()
metadataManager = MetadataFilesManager()
termsDict = metadataManager.getTermsMetadata()
searchManager = SearchManager(termDict=termsDict)
queryManager = QueryManager()
topK = 100
file = open("results.txt", "w")
for queryId in queries:
    print(f"Procesando query {queryId}: '{queries[queryId]}', con un top k = {topK}")
    newLine = "{"

    results = searchManager.search(query=queries[queryId], topK=topK)

    for result in results:
        statistics = results[result][1]
        statistics["process_time"] = results[result][2]
        newLine += f'"{result}":' + "{" + f"{statistics}"
        newLine += "},"
    newLine = newLine[:-1]
    newLine += "}\n"
    file.write(newLine)
file.close()
