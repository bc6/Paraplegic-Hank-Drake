
def RunUnitTestsIfRequired(moduleName):
    import blue
    import os
    import yaml
    import time
    DLL_UNIT_TESTS_LOG_FILE = 'dllUnitTests.log'
    if not blue.pyos.packaged:
        moduleObj = __import__(moduleName)
        dllName = os.path.split(moduleObj.__file__)[-1]
        filePath = blue.rot.PathToFilename('cache:/%s' % DLL_UNIT_TESTS_LOG_FILE)
        if os.path.exists(filePath):
            f = open(filePath, 'r')
            data = yaml.load(f)
            f.close()
        else:
            data = {}
        if type(data) != dict:
            data = {}
        if dllName in data and data[dllName] == time.ctime(os.path.getmtime(blue.os.binpath + dllName)):
            return False
        print 'Running',
        print dllName,
        print 'Unittests...'
        allTestsPassed = moduleObj.RunUnitTests()
        if allTestsPassed:
            f = open(filePath, 'w')
            data[dllName] = time.ctime(os.path.getmtime(blue.os.binpath + dllName))
            yaml.dump(data, f, default_flow_style=False)
            f.close()



