# Comparación LazyBM vs LBMM vs LBMW

Para ejecutar las pruebas primero se debe indexar una colección.
Se pueden indexar una colección, agregando sus archivos en la carpeta /files.
Se dejan archivos de ejemplos.

Para indexar, se debe ejecutar el script "buildIndex.py".
Se crearán varios archivos:
- blockMaxIndex.dat: índice
- blockMaxIndexMetadata.dat: metadata del índice con los offset de los bloques
- fileIndex.txt: pares <id doc>: <nombre archivo>
- fileLengths.txt: tamaños de los archivos necesarios en BM25
- termIndex.txt: pares <id término>: <string del término>

Una vez indexada la colección, se puede probar a ejecutar queries en el script "searcher.py".
