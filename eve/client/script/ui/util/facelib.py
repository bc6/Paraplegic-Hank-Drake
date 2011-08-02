import uthread
import blue
import sys
currSelection = None
globalParameters = 'res:/Model/Face/SceneOptions/'

def QueryFunctions(list, categories):
    result = []
    entries = list[categories[0]]
    if len(categories) > 1:
        for entry in entries:
            if entry[:1] == [categories[1]]:
                entries = entry[1:][0]

    returnlist = []
    for entry in entries:
        if type(entry[:1][0]) != type(''):
            returnlist.append(entry)

    return returnlist



def readValues(list, categories):
    valuelist = []
    functions = QueryFunctions(list, categories)
    browselist = []
    for function in functions:
        fn = function[0]
        for entry in function[1:]:
            if entry == '':
                result = fn()
            else:
                result = fn(entry)
            if result != None:
                valuelist.append(result)


    return valuelist


scenePathsByID = {}

def FindNodes(source, name, typename):
    tr = source.Find(typename)
    collection = []
    for t in tr:
        if t.name[:len(name)] == name:
            collection.append(t)

    return collection



def GetCharTexture(scene, resolutionX = 128, resolutionY = 128):
    from ui.globals import LogInfo
    st = blue.os.CreateInstance('trinity.TriSceneTexture')
    LogInfo(scene)
    st.scene = scene
    texture = blue.os.CreateInstance('trinity.TriTexture')
    texture.textureTransformFlags = 2
    texture.scaling.x = 0.66
    texture.scaling.y = 0.93
    texture.scaling.z = 1.0
    texture.translation.x = 0.15
    texture.translation.y = 0.05
    texture.translation.z = 1.0
    texture.AttachPixels(st)
    texture.pixelBuffer.zStencilFormat = 80
    texture.pixelBuffer.width = resolutionX
    texture.pixelBuffer.height = resolutionY
    return texture



def GetCharScene(dict):
    global getScene
    bakGetScene = None
    bakGetScene = getScene
    try:
        exceptions = ['.',
         '..',
         'Shared',
         'Template',
         'background',
         'Backdrop',
         'head',
         'optionslist.blue',
         'optionlist.blue',
         'optionsList.blue',
         'options.blue',
         'SceneOptions']
        dict = dict.copy()
        modelRootPath = blue.os.respath + 'Model/Face/'
        rot = blue.os.CreateInstance('blue.Rot')
        modelPath = dict['model']
        from os import listdir
        from ntpath import isdir
        scene = rot.GetCopy('res:/Model/Face/facescene.blue')
        camera = scene.camera
        blue.pyos.synchro.Yield()
        getScene = lambda scene = scene: scene
        pos = camera.rotationAroundParent
        (pos.x, pos.y, pos.z, pos.w,) = dict['cameraPosition']
        del dict['cameraPosition']
        for each in ['face', 'hair']:
            if each == 'face':
                for addLocation in scene.models:
                    if addLocation.name == '__head__':
                        parent = addLocation
                    if addLocation.name == '__hair__':
                        del addLocation.children[:]

            if each == 'hair':
                for addLocation in scene.models:
                    if addLocation.name == '__hair__':
                        parent = addLocation

            modelList = []
            for model in listdir(modelRootPath + modelPath + '/' + each + '/'):
                if model not in exceptions and model[-4:] == 'blue':
                    modelList.append(model)

            if modelList == []:
                print 'No',
                print each,
                print 'found'
                return 
            del parent.children[:]
            modelToAdd = 'res:/Model/Face/' + modelPath + '/' + each + '/' + modelList[0]
            model = rot.GetInstance(modelToAdd)
            tmpPath = modelToAdd[:-5] + str(uthread.uniqueId()) + modelToAdd[-5:]
            model.SaveTo(tmpPath)
            model = rot.GetInstance(tmpPath)
            parent.children.append(model)
            getScene = bakGetScene
            blue.pyos.synchro.Yield()
            getScene = lambda scene = scene: scene

        del dict['model']
        apply(eyePos, dict['eyePosition'])
        del dict['eyePosition']
        if dict.has_key('lights'):
            rot.GetCopy(dict['lights'] + '/lights.blue', scene.lights)
            del dict['lights']
            getScene = bakGetScene
            blue.pyos.synchro.Yield()
            getScene = lambda scene = scene: scene
        if dict.has_key('background'):
            for addLocation in scene.models:
                if addLocation.name == 'background':
                    parent = addLocation
                    break
            else:
                raise RuntimeError('GetCharScene: WTF')

            del parent.children[:]
            background = rot.GetCopy(dict['background'] + '/background.blue')
            parent.children.append(background)
            del dict['background']
            getScene = bakGetScene
            blue.pyos.synchro.Yield()
            getScene = lambda scene = scene: scene
        for each in dict.itervalues():
            setDirAttrib(each)
            getScene = bakGetScene
            blue.pyos.synchro.Yield()
            getScene = lambda scene = scene: scene

        getScene = bakGetScene
        return scene
    except:
        getScene = bakGetScene
        from ui.globals_ import LogError, LogException
        LogError('Something fucked trying to create char!')
        LogException()
        sys.exc_clear()
        return 


policeTex = None

def GetPoliceTexture():
    global policeTex
    try:
        if not policeTex:
            rot = blue.os.CreateInstance('blue.Rot')
            scene = rot.GetCopy('res:/Model/Face/facescene.blue')
            model = rot.GetInstance('res:/Model/Face/NPC/Police/police.blue')
            scene.models.append(model)
            policeTex = GetCharTexture(scene)
    except:
        import log
        log.LogException(log.ui)
        sys.exc_clear()
        return 
    return policeTex



def getHeadParent():
    dev = trinity.device
    scene = dev.scene
    head = None
    for model in scene.models:
        if model.name == '__head__':
            head = model

    return head



def getBackground():
    scene = getScene()
    background = None
    for model in scene.models:
        if model.name == 'background':
            head = model.children[0]

    return head



def getBackgroundParent():
    scene = getScene()
    background = None
    for model in scene.models:
        if model.name == 'background':
            return model




def backgroundMat():
    background = getBackground()
    material = background.object.areas[0].areaMaterials[0]
    return material



def getHairParent():
    hair = None
    for model in getScene().models:
        if model.name == '__hair__':
            hair = model

    return hair



def getCostumeParent():
    costume = None
    for model in getScene().models:
        if model.name == '__costume__':
            costume = model

    return costume



def getAccessoryParent():
    costume = None
    for model in getScene().models:
        if model.name == '__accessories__':
            costume = model

    return costume



def getHair():
    global getHairParent
    hairparent = getHairParent()
    if len(hairparent.children) > 0:
        return hairparent.children[0]



def setHead(transform):
    global getHeadParent
    head = getHeadParent()
    del head.childen[:]
    head.children.append(tranform)



def setHair(transform):
    hair = getHairParent()
    del hair.children[:]
    hair.children.append(transform)



def setCostume(transform):
    costume = getCostumeParent()
    del costume.children[:]
    costume.children.append(transform)



def setAccessory(transform):
    costume = getAccessoryParent()
    del costume.children[:]
    costume.children.append(transform)



def sceneLights(addname = ''):
    scene = getScene()
    lights = []
    for light in scene.lights:
        lights.append(light)

    if addname != 'color':
        return lights
    cleanlightlist = []
    for light in lights:
        cleanlight = light.CopyTo()
        cleanlight.name = light.name + '_color'
        cleanlightlist.append(cleanlight)

    return cleanlightlist



def lightsList():
    return getScene().lights


daScene = []

def HACKgetDevScene():
    if daScene:
        return daScene[-1]
    else:
        return eve.triapp.tridev.scene


getScene = HACKgetDevScene

def sceneCamera():
    return sm.GetService('sceneManager').GetRegisteredCamera()



def sceneTransforms(scene):
    global transformlist
    global addToTransforms
    global CrawlTree
    transformlist = []

    def addToTransforms(transform):
        for entry in transformlist:
            if entry == transform:
                return 

        transformlist.append(transform.name)



    def CrawlTree(transform):
        if transform.__typename__ == 'TriTransform':
            addToTransforms(transform)
            for child in transform.children:
                CrawlTree(child)



    scenemodels = []
    for model in scene.models:
        scenemodels.append(model)

    for model in scenemodels:
        if model:
            CrawlTree(model)

    return transformlist



def transformAreas(transform, list = []):
    if transform.object != None:
        for area in transform.object.areas:
            list.append(area)

    return list



def areaPasses(area, list):
    if area.shader:
        for thepass in area.shader.passes:
            list.append(thepass)

    return list



def areaTextures(area, list):
    for texture in area.areaTextures:
        list.append(texture)

    for texture in area.shader.shaderTextures:
        list.append(texture)

    return list



def areaMaterials(area, list = []):
    for material in area.areaMaterials:
        list.append(material)

    for material in area.shader.shaderMaterials:
        list.append(material)

    return list



class FakeTriArea(object):
    __slots__ = ['shader', 'areaTextures', 'areaMaterials']

    def __init__(self, a):
        self.shader = a.shader
        self.areaTextures = list(a.areaTextures)
        self.areaMaterials = list(a.areaMaterials)




def faceAreas():
    scene = getScene()
    arealist = []
    arealist = []
    for model in scene.models:
        if model.name == '__head__':
            head = model

    areas = head.Find('trinity.TriArea')
    return [ FakeTriArea(a) for a in areas ]



def addToListUnique(entry, list):
    isthere = 0
    for object in list:
        if object == entry:
            isthere = 1

    if isthere == 0:
        list.append(entry)
    return list



def faceTextures():
    areas = faceAreas()
    texturelist = []
    for area in areas:
        for texture in area.areaTextures:
            addToListUnique(texture, texturelist)

        if area.shader != None:
            for texture in area.shader.shaderTextures:
                addToListUnique(texture, texturelist)


    return texturelist



def hairTextures():
    areas = hairAreas()
    texturelist = []
    for area in areas:
        for texture in area.areaTextures:
            addToListUnique(texture, texturelist)

        if area.shader != None:
            for texture in area.shader.shaderTextures:
                addToListUnique(texture, texturelist)


    return texturelist



def facePasses():
    areas = faceAreas()
    passlist = []
    for area in areas:
        shader = area.shader
        for renderpass in shader.passes:
            addToListUnique(renderpass, passlist)


    return passlist



def facePass(name, unique = 0):
    passlist = facePasses()
    for renderpass in passlist:
        if renderpass.name == name:
            if unique == 0:
                return renderpass
            temppass = renderpass.CopyTo()
            if renderpass.textureStage0 != None:
                temppass.textureStage0 = renderpass.textureStage0.CopyTo()
            if renderpass.textureStage1 != None:
                temppass.textureStage1 = renderpass.textureStage1.CopyTo()
            if renderpass.textureStage2 != None:
                temppass.textureStage2 = renderpass.textureStage2.CopyTo()
            if renderpass.textureStage3 != None:
                temppass.textureStage3 = renderpass.textureStage3.CopyTo()
            thelist = {'temppass': temppass,
             'renderpass': renderpass}
            return temppass

    print name,
    print 'not found'



def faceTexture(name):
    textures = faceTextures()
    for texture in textures:
        if texture.name == name:
            return texture

    print name,
    print ' not found'



def faceMaterial(name):
    materials = faceMaterials()
    for material in materials:
        if material.name == name:
            return material

    print name,
    print ' not found'



def faceMaterials():
    areas = faceAreas()
    materiallist = []
    for area in areas:
        for material in area.areaMaterials:
            addToListUnique(material, materiallist)

        if area.shader != None:
            for material in area.shader.shaderMaterials:
                addToListUnique(material, materiallist)


    return materiallist



def getHead():
    scene = getScene()
    tranforms = sceneTransforms(scene)
    headparent = None
    head = None
    for model in scene.models:
        if model.name == '__head__':
            headparent = model

    if headparent != None:
        if len(headparent.children) > 0:
            head = headparent.children[0]
    return head



def getFaceDir():
    facemodel = getHead()
    if facemodel == None:
        return 
    facemodelpath = facemodel.GetRotPath()
    if facemodelpath == None:
        print 'This model has to be saved first on order for me to be able to read it'
        return 
    from string import split, find
    pathsplit = split(facemodelpath, '/')
    dirname = facemodelpath[:(len(facemodelpath) - len(pathsplit[(len(pathsplit) - 1)]))]
    return dirname



def entryDirPick(options, category = []):
    if options == sceneOptions:
        entrydir = globalParameters
    else:
        entrydir = getFaceDir()
    entrydir = options2path(entrydir, category)
    import os
    rot = blue.os.CreateInstance('blue.Rot')
    try:
        entries = os.listdir(rot.PathToFilename(entrydir))
    except:
        sys.exc_clear()
        return 
    cleanlist = []
    for entry in entries:
        if entry[-5:] != '.blue' and entry[-4:] != '.tri':
            cleanlist.append(entry)

    return cleanlist



def options2path(basepath, options):
    basepath = basepath[:-1]
    for option in options:
        basepath = basepath + '/' + option

    return basepath



def faceDirAppend(options, values, listformat):
    if listformat == sceneOptions:
        facedir = globalParameters
    else:
        facedir = getFaceDir()
    facedir = options2path(facedir, options)
    print facedir
    import os
    import string
    rot = blue.os.CreateInstance('blue.Rot')
    try:
        os.makedirs(rot.PathToFilename(facedir))
    except:
        sys.exc_clear()
        return 
    import trinity
    print values
    listofvalues = trinity.TriRenderObjectList()
    for object in values:
        if object.__typename__ == 'List':
            for each in object:
                listofvalues.children.append(each)

        else:
            listofvalues.children.append(object)

    listofvalues.SaveTo(rot.FilenameToPath(facedir + '/default.blue'))
    return 'ok'



def browseRenderObjects(objectlist):
    thelist = blue.os.CreateInstance('trinity.TriRenderObjectList')
    for entry in objectlist:
        if entry != None:
            thelist.children.append(entry)




def AttrPick(optionlist):
    picklist = []
    categories = optionlist.keys()
    for entry in categories:
        is_not_just_an_empty_parent = 0
        for item in optionlist[entry]:
            thetype = item[:1][0]
            if thetype == 'color' or thetype == 'shape' or thetype == 'skin':
                thename = entry + '-' + thetype
                picklist.append(thename)
            else:
                is_not_just_an_empty_parent = 1

        if is_not_just_an_empty_parent == 1:
            picklist.append(entry)

    picklist.reverse()
    try:
        import app
        selection = app.ui.AskList('Pick category', picklist)
    except:
        sys.exc_clear()
        print "Couldn't import app in facelib"
    if selection == None:
        return 
    import string
    resultlist = string.split(picklist[selection], '-')
    return resultlist



def backgroundTexture(name):
    background = getBackground()
    textures = background.object.areas[0].areaTextures
    for texture in textures:
        if texture.name == name:
            return texture




def backgroundPass():
    background = getBackground()
    thepass = background.object.areas[0].shader.passes[0]
    return thepass



def faceModel():
    headparent = getHeadParent()
    if len(headparent.children) > 0:
        head = headparent.children[0]
    faceModel = head.object.vertices
    return faceModel



def entryDirSel(options, listformat = ''):
    if listformat == sceneOptions:
        entrydir = globalParameters
    else:
        entrydir = getFaceDir()
    entrydir = options2path(entrydir, options)
    import os
    rot = blue.os.CreateInstance('blue.Rot')
    if os.path.exists(rot.PathToFilename(entrydir + '/default.blue')):
        entries = rot.GetInstance(rot.FilenameToPath(entrydir + '/' + '/default.blue'))
        return entries
    else:
        return []



def SetSceneGetter(func):
    global getScene
    getScene = func



def setDirAttrib(options, listformat = ''):
    global sceneLights
    sourcelist = entryDirSel(options, listformat)
    destlist = []
    print sourcelist,
    print options
    if type(sourcelist) == type([]):
        return 
    if hasattr(sourcelist, '__typename__'):
        if sourcelist.__typename__ == 'TriTransform':
            if options[0] == 'hair':
                setHair(sourcelist)
                return 
            if options[0] == 'costume':
                setCostume(sourcelist)
                return 
            if options[0].lower() == 'accessories':
                setAccessory(sourcelist)
                return 
            if options[0].lower() == 'background':
                background = getBackgroundParent()
                del background.children[:]
                background.children.append(sourcelist)
        if hasattr(sourcelist, 'children'):
            sourcelist = sourcelist.children
    import string
    blueobject = blue.os.CreateInstance('trinity.TriRenderObjectList')
    for texture in faceTextures():
        destlist.append(texture)

    for material in faceMaterials():
        destlist.append(material)

    for renderpass in facePasses():
        destlist.append(renderpass)

    for light in sceneLights():
        destlist.append(light)

    destlist.append(backgroundTexture('background_tex_1'))
    destlist.append(backgroundTexture('background_tex_2'))
    destlist.append(backgroundPass())
    destlist.append(backgroundMat())
    return setDirAttrib2(options, sourcelist, destlist, listformat)



def setDirAttrib2(options, sourcelist, destlist, listformat = ''):
    blueobject = blue.os.CreateInstance('trinity.TriRenderObjectList')
    for source in sourcelist:
        if type(source) == type(blueobject):
            for dest in destlist:
                if dest != None and source.__typename__ == dest.__typename__:
                    if source.name == dest.name:
                        if source.__typename__ == 'TriTexture':
                            if source.name == 'eye':
                                source.translation = dest.translation
                        source.CopyTo(dest)
                        if source.__typename__ == 'TriTexture':
                            dest.pixels = source.pixels[:-4] + '.dds'
                        if source.__typename__ == 'TriPass':
                            if source.textureStage0 != None:
                                source.textureStage0.CopyTo(dest.textureStage0)
                            if source.textureStage1 != None:
                                source.textureStage1.CopyTo(dest.textureStage1)
                            if source.textureStage2 != None:
                                source.textureStage2.CopyTo(dest.textureStage2)
                            if source.textureStage3 != None:
                                source.textureStage3.CopyTo(dest.textureStage3)
                    if source.__typename__ == 'TriLight':
                        colorlight_name = dest.name + '_color'
                        if colorlight_name == source.name:
                            dest.diffuse = source.diffuse
                            dest.ambient = source.ambient
                            dest.specular = source.specular
                if source.__typename__ == 'List':
                    scene = getScene()
                    del scene.lights[:]
                    for light in source:
                        scene.lights.append(light)

                if source.__typename__ == 'TriTransform':
                    if string.find(source.name.lower(), 'background') > -1:
                        background = getBackgroundParent()
                        del background.children[:]
                        background.children.append(source)
                    else:
                        setHair(source)





def eyePos(x = None, y = None):
    eyetex = faceTexture('eye')
    eyedot = faceTexture('eye_dot')
    if x == None:
        eyepos = [eyetex.translation.x, eyetex.translation.y]
        return eyepos
    eyetex.translation.x = float(x)
    eyetex.translation.y = float(y)
    eyedot.translation = eyetex.translation


faceOptions = {'skin': [[faceTexture,
           'skin',
           'skin_refmap',
           'skin_glossmap'], [faceMaterial, 'skin', 'skin_gloss'], [facePass, 'skin', 'skin_gloss']],
 'eyebrows': [[faceTexture, 'eyebrows'], [facePass, 'eyebrows'], [faceMaterial, 'eyebrows']],
 'beard': [[faceTexture, 'beard'], [facePass, 'beard'], [faceMaterial, 'beard']],
 'makeup': [[faceTexture,
             'makeup',
             'makeup_refmap',
             'makeup_glossmap'], [facePass, 'makeup', 'makeup_gloss'], [faceMaterial, 'makeup', 'makeup_gloss']],
 'deco': [[faceTexture,
           'deco',
           'deco_refmap',
           'deco_glossmap'], [facePass, 'deco', 'deco_gloss'], [faceMaterial, 'deco', 'deco_gloss']],
 'lipstick': [[faceTexture,
               'lipstick',
               'lipstick_refmap',
               'lipstick_glossmap'], [facePass, 'lipstick', 'lipstick_gloss'], [faceMaterial, 'lipstick', 'lipstick_gloss']],
 'eyes': [[faceTexture, 'eye', 'eye_gloss'], [facePass,
           'cornea',
           'sclera',
           'iris',
           'iris_refraction'], [faceMaterial,
           'iris',
           'sclera',
           'cornea_gloss']]}
sceneOptions = {'lights': [[lightsList, '']],
 'background': [[getBackground, '']]}
exports = {}
for (k, v,) in locals().items():
    if k == 'daScene' or type(v) == type(eyePos):
        exports['facelib.%s' % k] = v


