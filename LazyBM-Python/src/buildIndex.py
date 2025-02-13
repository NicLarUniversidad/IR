from FileManager import FileManager
from FolderReader import FolderReader
from IdManager import IdManager
from IndexManager import IndexManager
from Parser import Parser
from PostingListVectorialFactory import PostingListVectorialFactory

reader = FolderReader("ms-marco")
files = reader.findTxtAndHtmlFiles()

filesOnMemory = int(len(files) / 20)

indexManager = IndexManager()
indexManager.fileIndex, indexManager.fileIndexInverse = IdManager().assignIdToFiles(files)
fileManager = FileManager()
parser = Parser()
print("Se guardan índices con frecuencias")
indexFactory = PostingListVectorialFactory(int(filesOnMemory))
fileId = 1
fileLengths = dict()
for file in files:
    fileContent = fileManager.readFile(file)
    fileTermDict, indexManager.termIndex, indexManager.termIndexInverse = parser.customParse(fileContent, indexManager.termIndex, indexManager.termIndexInverse)
    indexFactory.add(fileTermDict, fileId, indexManager.termIndexInverse)
    fileLengths[fileId] = len(fileTermDict)
    fileId += 1
averageLength = sum(fileLengths.values()) / len(fileLengths)
indexFactory.flush(indexManager.termIndexInverse)
indexFactory.mergePostingLists(indexManager.termIndexInverse)
indexFactory.finish()
fileManager.writeDict("termIndex.txt", indexManager.termIndex)
fileManager.writeDict("fileIndex.txt", indexManager.fileIndex)
fileManager.writeDict("fileLengths.txt", fileLengths)
