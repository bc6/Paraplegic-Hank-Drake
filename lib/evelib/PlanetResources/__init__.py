
def __UpdateBinaries():
    import blue
    import os
    import sys
    if sys.platform == 'win32':
        print 'Clearing _PlanetResources.dll and _PlanetResources_d.dll binaries from application directory'
        binpath = blue.os.binpath
        try:
            os.remove(binpath + '_PlanetResources.dll')
        except:
            sys.exc_clear()
        try:
            os.remove(binpath + '_PlanetResources_d.dll')
        except:
            sys.exc_clear()
        autoBinariesPath = os.path.normpath(os.path.join(blue.os.binpath, 'autobuild/win32/'))
        copyCommand = 'copy /Y "' + autoBinariesPath + '\\_PlanetResources*" "' + binpath + '"'
        os.system(copyCommand)


PR_LUT_RESULUTION = 2048
import log

def PrintSH(sh):
    print '-' * 60
    for i in xrange(sh.GetNumCoefficients()):
        print '%03d: %f' % (i, sh.GetCoefficient(i))



from _PlanetResources import *
log.LogInfo('PlanetResources: Creating default SHBuilder instance')
builder = SHBuilder()
log.LogInfo('PlanetResources: Generating LUT tables with resolution of', PR_LUT_RESULUTION)
builder.GenerateLookUpTables(PR_LUT_RESULUTION)

