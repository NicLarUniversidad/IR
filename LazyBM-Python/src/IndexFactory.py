from FileManager import FileManager
from FolderReader import FolderReader
from IdManager import IdManager
from IndexManager import IndexManager
from MemoryBlockMaxIndex import MemoryBlockMaxIndex
from MemoryIndex import MemoryIndex
from Parser import Parser


class IndexFactory(object):

    def __init__(self, folder):
        self.folder = folder
        self.memoryIndex = MemoryIndex()
        self.termKeyDic = dict()

    def buildMemoryIndex(self):
        print("Leyendo archivos...")
        # Busco archivos en la carpeta y cargo las rutas de los archivos .txt y .html
        reader = FolderReader(self.folder)
        files = reader.findTxtAndHtmlFiles()
        # Cargo clases auxiliares
        idManager = IdManager()
        indexManager = IndexManager()
        #     Asigno ID a los archivos
        indexManager.fileIndex, indexManager.fileIndexInverse = idManager.assignIdToFiles(files)
        fileManager = FileManager()
        fileId = 1
        # Parser
        parser = Parser()
        self.memoryIndex = MemoryIndex()

        print("Parseando y construyendo índice invertido...")
        for file in files:
            # Recupero el contenido del archivo
            fileContent = fileManager.readFile(file)
            # Parseo, recupero los términos y armo los pares (DocID, TermID)
            #       La función devuelve:
            #           - Pares (TermID, Frecuencia)
            #           - Diccionario actualizado con: Término -> TermID
            fileTermDict, indexManager.termIndex = parser.customParse(fileContent, indexManager.termIndex)
            print(fileTermDict)
            # Se agregan los pares al índice
            self.memoryIndex.add(fileTermDict, fileId)
            fileId += 1

        self.termKeyDic = indexManager.termIndex

    def buildBlockMaxIndex(self):
        memoryBlockMaxIndex = MemoryBlockMaxIndex()
        for key in self.memoryIndex.postingLists:
            postingList = self.memoryIndex.postingLists[key]

