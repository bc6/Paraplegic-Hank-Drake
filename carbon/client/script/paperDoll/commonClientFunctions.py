import trinity
import util
import const
import bluepy
import blue
import weakref
INTERIOR_FEMALE_GEOMETRY_RESPATH = const.DEFAULT_FEMALE_PAPERDOLL_MODEL
INTERIOR_MALE_GEOMETRY_RESPATH = const.DEFAULT_MALE_PAPERDOLL_MODEL
DEFAULT_FEMALE_ANIMATION_RESPATH = const.MORPHEMEPATH
DRAPE_TUCK_NAMES = ('DrapeShape', 'TuckShape')
HAIR_MESH_SHAPE = 'HairMeshShape'
TRANSLATION = intern('translation')
ROTATION = intern('rotation')

def CreateRandomDoll(name, factory, outResources = None):
    import paperDoll as PD
    dollRand = PD.DollRandomizer(factory)
    doll = dollRand.GetDoll()
    doll.name = name
    return doll



def CheckDuplicateMeshes(meshes):
    meshCount = len(meshes)
    for i in xrange(meshCount):
        for x in xrange(i + 1, meshCount):
            if meshes[i].name == meshes[x].name and meshes[i].geometryResPath == meshes[x].geometryResPath:
                raise Exception('Duplicate meshes!\n Mesh name:%s Mesh Geometry Respath:%s' % (meshes[i].name, meshes[i].geometryResPath))





def GetEffectsFromAreaList(areas):
    effects = []
    for each in iter(areas):
        effects.append(each.effect)

    return effects



def MeshAreaIterator(mesh):
    for areaList in MeshAreaListIterator(mesh):
        for area in iter(areaList):
            yield area





def MeshAreaListIterator(mesh, includePLP = False):
    yield mesh.opaqueAreas
    yield mesh.decalAreas
    yield mesh.depthAreas
    yield mesh.transparentAreas
    yield mesh.additiveAreas
    yield mesh.pickableAreas
    yield mesh.mirrorAreas
    if includePLP:
        yield mesh.decalNormalAreas
        yield mesh.depthNormalAreas
        yield mesh.opaquePrepassAreas
        yield mesh.decalPrepassAreas



@bluepy.CCP_STATS_ZONE_FUNCTION
def GetEffectsFromMesh(mesh):
    effects = []
    if type(mesh) is trinity.Tr2ClothingActor:
        if hasattr(mesh, 'effect') and mesh.effect is not None:
            effects.append(mesh.effect)
        if hasattr(mesh, 'effectReversed') and mesh.effectReversed is not None:
            effects.append(mesh.effectReversed)
    elif type(mesh) is trinity.Tr2Mesh:
        for area in MeshAreaListIterator(mesh):
            effects += GetEffectsFromAreaList(area)

    elif type(mesh) is trinity.Tr2InteriorStatic:
        for area in mesh.enlightenAreas:
            effects.append(area.effect)

    effects = [ effect for effect in effects if effect if type(effect) != trinity.Tr2ShaderMaterial ]
    return effects



def MoveAreas(fromAreaList, toAreaList):
    for area in iter(fromAreaList):
        toAreaList.append(area)

    del fromAreaList[:]



def SetOrAddMap(effect, mapName, mapPath = None):
    for res in effect.resources:
        if res.name == mapName:
            if mapPath:
                res.resourcePath = mapPath
            return res

    map = trinity.TriTexture2DParameter()
    map.name = mapName
    if mapPath:
        map.resourcePath = mapPath
    effect.resources.append(map)
    return map



def FindOrAddMat4(effect, name):
    for r in effect.parameters:
        if r.name == name:
            return r

    p = trinity.Tr2Matrix4Parameter()
    p.name = name
    effect.parameters.append(p)
    return p



def FindOrAddVec4(effect, name):
    for r in effect.parameters:
        if r.name == name:
            return r

    p = trinity.Tr2Vector4Parameter()
    p.name = name
    effect.parameters.append(p)
    return p



def __WeakBlueRemoveHelper(weakInstance, dictionaryName, weakObjectKey):
    if weakInstance():
        dictionary = getattr(weakInstance(), dictionaryName)
        if dictionary is not None:
            dictionary.pop(weakObjectKey, None)
    if weakObjectKey:
        weakObjectKey.callback = None



def AddWeakBlue(classInstance, dictionaryName, blueObjectKey, value):
    dictionary = getattr(classInstance, dictionaryName)
    if dictionary is None:
        return 
    for key in dictionary.iterkeys():
        if key.object == blueObjectKey:
            dictionary[key] = value
            return 

    weakInstance = weakref.ref(classInstance)
    weakObjectKey = blue.BluePythonWeakRef(blueObjectKey)
    weakObjectKey.callback = lambda : __WeakBlueRemoveHelper(weakInstance, dictionaryName, weakObjectKey)
    dictionary[weakObjectKey] = value



def DestroyWeakBlueDict(dictionary):
    for weakObjectKey in dictionary.iterkeys():
        if weakObjectKey:
            weakObjectKey.callback = None




def IsBeard(areaMesh):
    return areaMesh.effect is not None and 'furshell' in areaMesh.effect.effectFilePath.lower()



def IsSkin(fx):
    fxName = fx.name.lower()
    return fxName.startswith('c_skin') and 'tearduct' not in fxName



def IsGlasses(areaMesh):
    return areaMesh.effect is not None and 'glassshader' in areaMesh.effect.effectFilePath.lower()



def StripDigits(name):
    return ''.join((letter.lower() for letter in name if not letter.isdigit()))



def PutMeshToLookup(lookup, m):
    meshName = StripDigits(m.name)
    c = 0
    try:
        c = int(m.name.split(meshName)[-1])
    except ValueError:
        c = 0
    meshName = StripDigits(m.name)
    lookup[meshName] = max([c, lookup.get(meshName)]) + 1


exports = util.AutoExports('paperDoll', globals())

