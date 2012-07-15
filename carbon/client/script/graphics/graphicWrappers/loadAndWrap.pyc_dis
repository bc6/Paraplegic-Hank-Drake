#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicWrappers/loadAndWrap.py
import graphicWrappers
import trinity
import log
import weakref
loadedObjects = weakref.WeakKeyDictionary()

def LoadAndWrap(resPath, urgent = False, convertSceneType = True):
    resPath = str(resPath)
    if urgent:
        triObject = trinity.LoadUrgent(resPath)
    else:
        triObject = trinity.Load(resPath)
    if triObject:
        return Wrap(triObject, resPath, convertSceneType=convertSceneType)
    log.LogError('Unable to load', resPath)


def Wrap(triObject, resPath = None, convertSceneType = True):
    resPath = str(resPath)
    wrapper = getattr(graphicWrappers, triObject.__typename__, None)
    if hasattr(wrapper, 'ConvertToInterior'):
        triObject = wrapper.ConvertToInterior(triObject, resPath)
        wrapper = getattr(graphicWrappers, triObject.__typename__, None)
    if wrapper:
        obj = wrapper.Wrap(triObject, resPath)
        if getattr(prefs, 'http', False):
            loadedObjects[obj] = True
        return obj


def GetLoadedObjects():
    return loadedObjects


exports = {'graphicWrappers.LoadAndWrap': LoadAndWrap,
 'graphicWrappers.Wrap': Wrap,
 'graphicWrappers.GetLoadedObjects': GetLoadedObjects}