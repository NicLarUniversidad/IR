from BlockMaxIndexManager import BlockMaxIndexManager
from MetadataFilesManager import MetadataFilesManager


class BlockService(object):

    def __init__(self, queryTerms, termDict=None):
        self.blocksRead = 0
        self.docIdRead = 0
        self.docIdSkipped = 0
        self.docIdSkippedWithUb = 0
        self.blockSkipped = 0
        self.termList = []
        self.sizes = []
        # Se instancia el objecto blockManager que está encargado de leer el archivo
        self.blockManager = BlockMaxIndexManager()
        # Se obtiene la metadata que contiene el par <id-término>:<string del término>
        if termDict is None:
            metadataManager = MetadataFilesManager()
            self.TermsDict = metadataManager.getTermsMetadata()
        else:
            self.TermsDict = termDict
        # Se buscan en disco los primeros bloques de cada término
        self.block = self.getFirstBlock(queryTerms)
        # Se ordenan por cantidad de DOC-IDs
        self.blockOrder = self.getBlockOrder()
        # Se inicializan atributos
        self.infinite = -1
        self.pivotDocId = 0
        self.processedTerms = []

    def getOptionalsAndEssentials(self, P, theta):
        tOpt = []
        tEss = []
        for term in self.block:
            if P[term] < theta:
                tOpt.append(term)
            else:
                tEss.append(term)
        return tOpt, tEss

    def getFirstBlock(self, queryTerms):
        for term in queryTerms:
            if term in self.TermsDict:
                self.termList.append(int(self.TermsDict[term]))
                self.blocksRead += 1
        blocks = self.blockManager.getFirstBlocks(self.termList)
        for block in blocks:
            self.sizes.append(blocks[block].docIdCount)
        return blocks

    def nextDocWithinEssentialBlock(self, tEss):
        minDocId = self.pivotDocId
        founded = 0
        for term in tEss:
            currentDocId = self.block[term].getCurrentDocId()
            if currentDocId == self.pivotDocId:
                self.block[term].next()
                currentDocId = self.block[term].getCurrentDocId()
            if currentDocId == -1:
                if self.block[term].hasNextBlock():
                    self.blocksRead += 1
                    self.block[term] = self.blockManager.getNextBlock(term, self.block[term])
                    currentDocId = self.block[term].getCurrentDocId()
                    if minDocId == self.pivotDocId:
                        minDocId = currentDocId
                        founded = 1
                    else:
                        if currentDocId < minDocId:
                            minDocId = currentDocId
                            founded = 1
            else:
                if minDocId == self.pivotDocId:
                    minDocId = currentDocId
                    founded = 1
                else:
                    if currentDocId < minDocId:
                        minDocId = currentDocId
                        founded = 1
        self.pivotDocId = minDocId
        return founded == 1

    def computePrefixSum(self):
        P = dict()
        ubSum = 0
        for orderTuple in self.blockOrder:
            term = orderTuple[0]
            ubSum += self.block[term].getUb()
            P[term] = ubSum
        return P

    def getCurrentDocId(self, t):
        self.docIdRead += 1
        return self.block[t].getCurrentDocId()

    def skipTo(self, t, pivotDocId):
        # Si el cursor del índice del término t, no ha llegado al final...
        if t not in self.processedTerms:
            # Si el DOC-ID pivote es más chico que el Máximo DOC-ID del bloque, entonces
            # si el pivote está en el índice, debería estar en este bloque
            if self.block[t].getMaxDocId() <= pivotDocId:
                # Se saltean los DOC-ID hasta un DOC-ID que sea igual o mayor al pivote
                self.docIdSkipped += self.block[t].skipTo(pivotDocId)
            else:
                self.block[t], founded, skipped = self.blockManager.getBlockByDocId(t, pivotDocId, self.block[t])
                self.docIdSkipped += self.block[t].skipTo(pivotDocId)
                self.blockSkipped += skipped
                self.docIdSkipped += skipped * self.block[t].blockSize
                # Si no encuentra el siguiente bloque, es porque el DOC-ID más grande del índice es menor que el
                # DOC-ID pivote, por lo que el pivote no está en el índice
                # Ni tampoco los siguientes DOC-ID pivotes. Por lo que ya no tendría sentido considerar el índice
                # Acá sabríamos que nuestro cursor habría llegado al final del índice del término t
                # Se registra en la lista processedTerms que ya se llegó al final del índice
                if not founded:
                    self.processedTerms.append(t)
                else:
                    self.blocksRead += 1

    def getUb(self, t):
        return self.block[t].getUb()

    def getCurrentScore(self, t):
        return self.block[t].getCurrentScore()

    def getBlockOrder(self):
        order = []
        for term in self.block:
            order.append((term, self.block[term].docIdCount))
        order.sort(key=lambda s: s[1])
        return order

    def getStatistics(self):
        statistics = dict()
        statistics["block_read"] = self.blocksRead
        statistics["doc_id_read"] = self.docIdRead
        statistics["doc_id_skipped"] = self.docIdSkipped
        statistics["doc_id_skipped_with_ub"] = self.docIdSkippedWithUb
        statistics["block_skipped"] = self.blockSkipped
        statistics["posting_list_sizes"] = self.sizes
        if len(self.sizes) > 0:
            statistics["max_posting_size"] = max(self.sizes)
        else:
            statistics["max_posting_size"] = 0
        return statistics
