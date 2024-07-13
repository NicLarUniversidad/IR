import os


# Clase para recuperar rutas de archivos dentro de una carpeta
class FolderReader(object):
    def __init__(self, folderName):
        self.folderName = folderName

    def run_fast_scandir(self, dir, ext):  # dir: str, ext: list
        folders, files = [], []

        for f in os.scandir(dir):
            if f.is_dir():
                folders.append(f.path)
            if f.is_file():
                if os.path.splitext(f.name)[1].lower() in ext:
                    files.append(f.path)

        for dir in list(folders):
            sf, f = self.run_fast_scandir(dir, ext)
            folders.extend(sf)
            files.extend(f)
        return folders, files

    def findTxtAndHtmlFiles(self):
        sub, files = self.run_fast_scandir(self.folderName, [".html", ".txt"])
        return files
