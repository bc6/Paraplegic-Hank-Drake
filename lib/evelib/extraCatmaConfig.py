from catma import enum
from catma import catmaConfig
import logging
logger = logging.getLogger('DUST.CATMA')
GROUPS = enum.Enum('system', 'Generic', 'Physics', 'Content', 'Combat', 'LockOn', 'Logic', 'Misc', 'Engineering', value_type=lambda self, i, k: k)
BUILTIN_GROUP = GROUPS.system
DEFAULT_GROUP = GROUPS.Generic
CUSTOM_FLAGS = enum.Enum('DIRECT_ATTRIB', 'THUNKER_CODE', 'SERVER_UPDATE_ONLY', value_type=lambda self, i, k: 1 << i)
DEFAULT_CUSTOM_FLAGS = 0
DEFAULT_CUSTOM_FLAGS_FOR_CLASS_TYPE = 0
DEPENDENT_MODULES = ['dustAttribs2', 'dustContent']

def EntryPoint(*args, **kwargs):
    import dustAttribs2
    dustAttribs2.PopulateAll(*args, **kwargs)


import os
cachedDB = None

def GetCatmaDB():
    global cachedDB
    if not cachedDB:
        from sake.app import app
        from sake.const import APP_ROLE_CLIENT, APP_ROLE_SERVER
        pickleName = catmaConfig.GetPickleName()
        if app:
            if app.HasRole(APP_ROLE_CLIENT):
                vault = app.GetService('vaultClient')
            elif app.HasRole(APP_ROLE_SERVER):
                vault = app.GetService('vaultServer')
            location = vault.GetFilePath(pickleName)
            if location is None and pickleName == catmaConfig.PICKLE_DEV:
                logger.warn('Development version (%s) of CATMA data cannot be found, resort to normal version (%s)' % (pickleName, catmaConfig.PICKLE_NORMAL))
                pickleName = catmaConfig.PICKLE_NORMAL
                location = vault.GetFilePath(pickleName)
        else:
            rootPath = None
            startLocations = ['', os.path.dirname(__file__)]
            for startLocation in startLocations:
                rootPath = startLocation
                for i in range(100):
                    if os.path.exists(os.path.join(rootPath, 'eve\\common\\common.ini')):
                        break
                    rootPath += '..\\'
                else:
                    rootPath = None

                if rootPath:
                    break

            if not rootPath:
                raise RuntimeError('extraCatmaConfig: Cannot determine branch root from {0}'.format(startLocations))
            location = os.path.join(rootPath, 'eve/dust/ue3/DustGame/vault/%s' % pickleName)
        if not location or not os.path.exists(location):
            raise RuntimeError("Can't find %s in vault folder\n   Possible fixes:\n   1. Run start_vaultgen.bat from eve/server folder. It will auto-generate all cache files.\n   2. Grab the cache files from the latest build and copy it to your vault folder.\n      (i.e. from here \\\\bamboo\\builds\\CN_MAIN\\CN_MAIN_232240_00006\\PC\\ue3\\DustGame\\vault\n   3. Ask someone around you for assistance. Show this error message" % pickleName)
        logger.info('Loading CATMA data from %s' % location)
        with open(location, 'rb') as catmaDBPickle:
            import catma.catmaDB
            cachedDB = catma.catmaDB.LoadData(catmaDBPickle)
        logger.info('CATMA data loaded: %s' % cachedDB)
    return cachedDB



def SetCatmaDB(newCatmaDB):
    global cachedDB
    if newCatmaDB and cachedDB is not newCatmaDB:
        if cachedDB:
            cachedDB.TearOff()
        cachedDB = newCatmaDB



