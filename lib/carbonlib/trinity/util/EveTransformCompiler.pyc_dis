#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\trinity\util\EveTransformCompiler.py
import trinity
import blue
CAMERA_ROTATION_ALIGNED = 100
CAMERA_ROTATION = 103
EVE_SIMPLE_HALO = 102
EVE_BOOSTER = 101

def ConvertTransforms(transformArray, parent, t, transformationsLookupDict):
    if t.display == False:
        print 'Did not convert:', t.name, 'as it is invisible'
        return
    if t.modifier not in [0,
     EVE_BOOSTER,
     CAMERA_ROTATION_ALIGNED,
     CAMERA_ROTATION,
     EVE_SIMPLE_HALO]:
        print "Couldn't convert:", t.name, 'as it is not a default transform (' + str(t.modifier) + ')'
        return
    if t.useDistanceBasedScale:
        print 'Ignoring distance based scaling in:', t.name
    newTransform = trinity.EveTransformItem()
    if parent is not None:
        parent.children.append(newTransform)
    else:
        transformArray.transformations.append(newTransform)
    transformationsLookupDict[t] = newTransform
    newTransform.scale = t.scaling
    newTransform.translation = t.translation
    newTransform.rotation = t.rotation
    newTransform.name = t.name
    newTransform.modifier = trinity.EveTransformItemModifier.EVE_TOM_NONE
    if t.modifier == CAMERA_ROTATION_ALIGNED:
        newTransform.modifier = trinity.EveTransformItemModifier.EVE_TOM_CAMERA_ALIGNED_WITH_SCALE
    elif t.modifier == EVE_SIMPLE_HALO:
        newTransform.modifier = trinity.EveTransformItemModifier.EVE_TOM_CAMERA_ALIGNED_Z_MODULATED
    if t.mesh:
        renderableMesh = trinity.EveRenderableMesh()
        renderableMesh.mesh = t.mesh
        if t.mesh.name:
            renderableMesh.name = t.mesh.name
        else:
            renderableMesh.name = t.name
        renderableMesh.transform = newTransform
        transformArray.meshes.append(renderableMesh)
    for i in t.children:
        ConvertTransforms(transformArray, newTransform, i, transformationsLookupDict)

    return newTransform


def ConvertSpaceObject(o):
    transformArray = trinity.EveTransformArray()
    transformLookup = {}
    for i in o.children:
        ConvertTransforms(transformArray, None, i, transformLookup)

    for cs in o.curveSets:
        for b in cs.bindings:
            if b.destinationObject in transformLookup:
                if b.destinationAttribute == 'scaling':
                    b.destinationAttribute = 'scale'
                b.destinationObject = transformLookup[b.destinationObject]

    o.children.removeAt(-1)
    transformArray.RebuildTransformations()
    o.children.append(transformArray)


def AreSineCurvesTheSame(a, b):
    if a is b:
        return True
    return a.scale == b.scale and a.offset == b.offset and a.speed == b.speed


def AreSineCurvesOffset(a, b):
    return a.scale == b.scale and a.speed == b.speed


def AreSineCurvesScaled(a, b):
    return a.offset == b.offset and a.speed == b.speed


def AreColorstheSame(a, b):
    return a.r == b.r and a.g == b.g and a.b == b.b and a.a == b.a


def AreVectorsTheSame(a, b):
    return a.x == b.x and a.y == b.y and a.z == b.z


def AreColorCurvesTheSame(a, b):
    if a is b:
        return True
    elif a.length == b.length and a.extrapolation == b.extrapolation and len(a.keys) == len(b.keys):
        keysTheSame = True
        for key1, key2 in zip(a.keys, b.keys):
            if key1.time != key2.time:
                return False
            if key1.interpolation != key2.interpolation:
                return False
            if not AreColorstheSame(key1.value, key2.value):
                return False

        return True
    else:
        return False


def AreVectorCurvesTheSame(a, b):
    if a is b:
        return True
    elif a.length == b.length and a.extrapolation == b.extrapolation and len(a.keys) == len(b.keys):
        keysTheSame = True
        for key1, key2 in zip(a.keys, b.keys):
            if key1.time != key2.time:
                return False
            if key1.interpolation != key2.interpolation:
                return False
            if not AreVectorsTheSame(key1.value, key2.value):
                return False
            if not AreVectorsTheSame(key1.left, key2.left):
                return False
            if not AreVectorsTheSame(key1.right, key2.right):
                return False

        return True
    else:
        return False


def SquashCurves(curveSet):
    curves = curveSet.curves
    curvesByType = {}
    removableCurveMappings = {}
    for curve in curves:
        if curve.__bluetype__ not in curvesByType:
            curvesByType[curve.__bluetype__] = []
        curvesByType[curve.__bluetype__].append(curve)

    if 'trinity.TriSineCurve' in curvesByType:
        uniqueSineCurves = set()
        for sineCurve in curvesByType['trinity.TriSineCurve']:
            exists = False
            for uc in uniqueSineCurves:
                if AreSineCurvesTheSame(uc, sineCurve):
                    exists = True
                    removableCurveMappings[sineCurve] = uc
                    break

            if not exists:
                uniqueSineCurves.add(sineCurve)

        print 'Unique Sine Curves', len(uniqueSineCurves)
    if 'trinity.TriColorCurve' in curvesByType:
        uniqueCurves = set()
        for curve in curvesByType['trinity.TriColorCurve']:
            exists = False
            for uc in uniqueCurves:
                if AreColorCurvesTheSame(curve, uc):
                    removableCurveMappings[curve] = uc
                    exists = True
                    break

            if not exists:
                uniqueCurves.add(curve)

        print 'Unique Color Curves', len(uniqueCurves)
    if 'trinity.TriVectorCurve' in curvesByType:
        uniqueCurves = set()
        for curve in curvesByType['trinity.TriVectorCurve']:
            exists = False
            for uc in uniqueCurves:
                if AreVectorCurvesTheSame(curve, uc):
                    removableCurveMappings[curve] = uc
                    exists = True
                    break

            if not exists:
                uniqueCurves.add(curve)

        print 'Unique Vector Curves', len(uniqueCurves)
    print 'Total curves', len(curveSet.curves)
    print 'Removing', len(removableCurveMappings), 'curves'
    for curve in removableCurveMappings:
        while True:
            try:
                curveSet.curves.remove(curve)
            except:
                break

    for curve in removableCurveMappings.values():
        if curve not in curveSet.curves:
            curveSet.curves.append(curve)

    print 'Pruned Curves', len(curveSet.curves)
    for binding in curveSet.bindings:
        if binding.sourceObject in removableCurveMappings:
            binding.sourceObject = removableCurveMappings[binding.sourceObject]