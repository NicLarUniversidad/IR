import os

class FileManager(object):

    def readFile(self, filename):
        f = open(filename, "r", encoding="utf8")
        content = f.read()
        f.close()
        return content

    def writeFile(self, filename, content):
        if os.path.isfile(filename):
            f = open(filename, 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        f = open(filename, "w", encoding="utf8")
        f.write(content)
        f.close()

    def writeDict(self, filename, dictData):
        if os.path.isfile(filename):
            f = open(filename, 'wb+')
            f.truncate(0)  # need '0' when using r+
            f.close()
        f = open(filename, "w", encoding="utf8")
        for key in dictData.keys():
            line = f"{key}:{dictData[key]}\n"
            f.write(line)
        f.close()
