from Parser import Parser

parser = Parser()

textoPrueba = "ola mundo cafe pepe informatica"
textoPrueba2 = "ola mundo cafe pepe informatica hardware software"

algo = parser.customParse(textoPrueba)
algo2 = parser.customParse(textoPrueba2, algo[1], algo[2])

print(algo2)

