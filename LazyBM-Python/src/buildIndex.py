import argparse
import struct

from FileManager import FileManager
from FolderReader import FolderReader
from IdManager import IdManager
from IndexManager import IndexManager
from Parser import Parser
from BlockMaxIndexFactory import BlockMaxIndexFactory

parser = argparse.ArgumentParser()
parser.add_argument("-files-on-memory", dest="filesOnMemory",
                    help="Indica la cantidad de archivos que se van a procesar antes de guardar parcialmente el índice",
                    type=int)
args = parser.parse_args()

filesOnMemory = args.filesOnMemory

reader = FolderReader("files")
files = reader.findTxtAndHtmlFiles()
idManager = IdManager()

if args.filesOnMemory is None:
    filesOnMemory = int(len(files) / 10)
    print("No se asignó un número máximo de archivos a procesar en memoria. Se puede asignar manualmente con el "
          + "parámetro -files-on-memory. Se van a asignar automáticamente un 10% de los archivos "
          + f" que estén en la carpeta \\files (10% = {filesOnMemory} archivos)")
else:
    print(f"Se hará volvado cada {filesOnMemory} archivos")

indexManager = IndexManager()
indexManager.fileIndex, indexManager.fileIndexInverse = idManager.assignIdToFiles(files)
fileManager = FileManager()
parser = Parser()
print("Se guardan índices con frecuencias")
blockMaxIndexFactory = BlockMaxIndexFactory(int(filesOnMemory))
fileId = 1
fileLengths = dict()
blockMaxIndexFactory.startCount()
for file in files:
    fileContent = fileManager.readFile(file)
    fileTermDict, indexManager.termIndex, indexManager.termIndexInverse = parser.customParse(fileContent,
                                                                                             indexManager.termIndex,
                                                                                             indexManager.termIndexInverse)
    blockMaxIndexFactory.add(fileTermDict, fileId, indexManager.termIndexInverse)
    fileLengths[fileId] = len(fileTermDict)
    fileId += 1
averageLength = sum(fileLengths.values()) / len(fileLengths)
blockMaxIndexFactory.flush(indexManager.termIndexInverse)
blockMaxIndexFactory.mergePostingLists(indexManager.termIndexInverse, len(files), averageLength, fileLengths)
blockMaxIndexFactory.finish()
print(
    f"Total tiempo procesamiento: {blockMaxIndexFactory.totalProcessTime} s, indexación: {blockMaxIndexFactory.getIndexTime()} s, merge: {blockMaxIndexFactory.mergeTime} s")
fileManager.writeDict("termIndex.txt", indexManager.termIndex)
# fileManager.writeDict("termIndexInverse.txt", indexManager.termIndexInverse)
fileManager.writeDict("fileIndex.txt", indexManager.fileIndex)
# fileManager.writeDict("fileIndexInverse.txt", indexManager.fileIndexInverse)
fileManager.writeDict("fileLengths.txt", fileLengths)

metadataFile = open('blockMaxIndexMetadata.dat', 'rb')
bmFile = open('blockMaxIndex.dat', 'rb')
metadataFormat = 'Q Q Q Q Q'
metadataLength = struct.calcsize(metadataFormat)
metadataUnpack = struct.Struct(metadataFormat).unpack_from
data = metadataFile.read(metadataLength)
while data:
    record = metadataUnpack(data)
    print(f"term id: {record[0]}, block size: {record[1]}, block count: {record[2]}, doc id count: {record[3]}, offset: {record[4]}")
    bmFormat = "Id" + str(record[1]) + "I" + str(record[1]) + "d"
    bmLength = struct.calcsize(bmFormat)
    bmUnpack = struct.Struct(bmFormat).unpack_from
    bmFile.seek(record[4])
    for i in range(record[2]):
        bmData = bmFile.read(bmLength)
        bmRecord = bmUnpack(bmData)
        print(f"\t\t\tmax doc id: {bmRecord[0]}, max score: {bmRecord[1]}")
    data = metadataFile.read(metadataLength)
metadataFile.close()
bmFile.close()
