import trinity
AREAS = ('opaqueAreas', 'decalAreas', 'depthAreas', 'transparentAreas', 'additiveAreas', 'pickableAreas', 'mirrorAreas')

def IsTr2EffectLoading(effect):
    for resource in effect.resources:
        if getattr(resource, 'isLoading', False):
            return True

    return False



def IsTr2ShaderMaterialLoading(effect):
    for (name, param,) in effect.parameters.items():
        if hasattr(param, 'resource'):
            if param.resource is not None:
                if getattr(param.resource, 'isLoading', False):
                    return True

    return False



def IsAreaLoading(area):
    if area.effect:
        if type(area.effect) is trinity.Tr2Effect:
            return IsTr2EffectLoading(area.effect)
        else:
            return IsTr2ShaderMaterialLoading(area.effect)
    return False



def IsTr2MeshLoading(mesh):
    if mesh.isLoading:
        return True
    for areaType in AREAS:
        areas = getattr(mesh, areaType)
        for area in areas:
            if IsAreaLoading(area):
                return True


    return False



def IsTr2ModelLoading(model):
    for mesh in model.meshes:
        if IsTr2MeshLoading(mesh):
            return True

    return False



def IsTr2SkinnedModelLoading(model):
    if model.geometryRes and model.geometryRes.isLoading:
        return True
    if IsTr2ModelLoading(model):
        return True
    return False


exports = {'util.IsTr2EffectLoading': IsTr2EffectLoading,
 'util.IsAreaLoading': IsAreaLoading,
 'util.IsTr2MeshLoading': IsTr2MeshLoading,
 'util.IsTr2ModelLoading': IsTr2ModelLoading,
 'util.IsTr2SkinnedModelLoading': IsTr2SkinnedModelLoading}

