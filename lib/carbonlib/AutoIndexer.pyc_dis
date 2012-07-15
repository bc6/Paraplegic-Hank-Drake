#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\AutoIndexer.py
import os
INDEX_FILENAME = 'index_TEST.txt'

class AutoIndexer:

    def __init__(self, directoryList):
        self.directoryList = directoryList
        self.MakeTreeIterators()
        self.IterateDirectories()

    def FilterFileNames(self, fileNames):
        fileNames = [ filename for filename in fileNames if self.IsFileNameValid(filename) ]
        return fileNames

    def FilterFolderNames(self, folderNames):
        folderNames = [ foldername for foldername in folderNames if self.IsFolderNameValid(foldername) ]
        return folderNames

    def IsFileNameValid(self, filename):
        return filename.endswith('.py') and not filename.startswith('_')

    def IsFolderNameValid(self, foldername):
        return not foldername.startswith('_')

    def IterateDirectories(self):
        for tree in self.treeList:
            for folderName, subfolders, files in tree:
                subfolders = self.FilterFolderNames(subfolders)
                files = self.FilterFileNames(files)
                self.WriteIndex(folderName, subfolders, files)

    def WriteIndex(self, folderName, subfolders, files):
        indexFileName = os.path.join(os.path.abspath(folderName), INDEX_FILENAME)
        fileHandler = open(indexFileName, 'w')
        for subfolder in subfolders:
            fileHandler.write(subfolder)
            fileHandler.write('/\n')

        for file in files:
            fileHandler.write(file)
            fileHandler.write('\n')

    def MakeTreeIterators(self):
        self.treeList = []
        for directory in self.directoryList:
            self.treeList.append(os.walk(directory))


directoryList = ['../../../wod/client/script', '../']
macro = AutoIndexer(directoryList)