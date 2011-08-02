
def KillOldCursor():
    import trinity
    from util import ResFile
    dev = trinity.device
    sur = dev.CreateOffscreenPlainSurface(32, 32, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SCRATCH)
    sur.LoadSurfaceFromFile(ResFile('res:/uicore/cursors/cursor10.dds'))
    uicore.uilib.SetCursorProperties(16, 15, sur)


LOR = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent nisl eros, iaculis nec congue id, sollicitudin ac velit. Morbi sed diam neque. Etiam nec lobortis dui. Nam magna nulla, eleifend sed bibendum et, pellentesque vestibulum mi. In et lectus mi, id elementum nulla. Etiam faucibus felis sed leo lobortis dignissim at eget ligula. Vivamus condimentum, neque vel vulputate dignissim, lectus ligula pharetra odio, vitae venenatis erat augue vehicula odio. Aliquam erat volutpat. Fusce a odio a quam bibendum luctus placerat quis orci. Quisque ac auctor dui. Suspendisse consequat volutpat porttitor.\n\nEtiam sed orci nec risus accumsan fringilla quis nec leo. Aliquam risus nisl, imperdiet a pulvinar ut, aliquet ut arcu. Integer in nibh purus, non aliquet dolor. Etiam euismod tortor ac dui suscipit scelerisque. Mauris lacus augue, dapibus ac mattis a, sollicitudin vitae augue. Mauris pulvinar laoreet aliquam. Aliquam tristique tempor lacus, viverra dictum ligula vehicula ac. Aliquam pharetra, mi vitae ullamcorper bibendum, purus nisi pulvinar orci, nec placerat leo orci a ipsum. Quisque eget tortor sit amet nunc aliquam pellentesque gravida et eros. Vivamus in quam semper est eleifend fringilla. Proin rutrum consectetur erat, id lobortis tortor feugiat eget.\n\nAenean mi risus, mattis sed semper eget, euismod vel dui. Morbi pellentesque dignissim mi, viverra porttitor felis facilisis eget. Praesent ac nunc nisl, id accumsan risus. Donec laoreet, velit ac scelerisque sodales, libero risus mollis massa, et semper velit mi vel sem. Etiam aliquet, lorem quis sagittis consequat, nulla ipsum vulputate lorem, ut placerat lectus tortor nec sapien. Nullam tempor, eros dictum egestas ullamcorper, nibh ligula posuere dui, eu suscipit quam eros sit amet metus. Nullam varius convallis libero non mollis. Aliquam id justo a sem consequat commodo vel eget justo. Duis nec erat in justo iaculis rutrum. In mollis placerat lorem ultricies rutrum. Aliquam bibendum placerat dolor et lacinia. Cras magna lectus, hendrerit a dignissim eu, accumsan at augue. Quisque tempus, arcu sit amet tempor condimentum, massa turpis bibendum quam, vitae venenatis orci felis a tortor. Curabitur condimentum pellentesque tempus. Aenean id urna felis, vitae bibendum ligula. Fusce a neque dui.\n\nPellentesque nec dolor ligula. Pellentesque ante nisl, vehicula id tristique sit amet, lobortis vel tortor. Integer at erat vel massa tempor hendrerit et id risus. Vivamus facilisis massa purus. Pellentesque vitae est mi. Etiam neque massa, venenatis sed iaculis vitae, venenatis et enim. Nulla porta accumsan est id congue. Donec non leo turpis. Cras varius lectus quis massa elementum malesuada. Nullam in orci id ante interdum feugiat. Sed leo elit, congue ut tincidunt sed, dapibus at orci. Etiam condimentum facilisis scelerisque. Praesent eu scelerisque nulla. Proin ac odio arcu, eu pellentesque mauris. Phasellus feugiat arcu ac massa ullamcorper dictum. Mauris lectus nisi, dignissim eu lobortis ullamcorper, mattis vitae dolor. Aenean suscipit eleifend libero, vitae mattis tellus hendrerit eu. Duis in erat orci. Praesent pretium libero at nunc placerat id viverra felis sollicitudin. Vestibulum in nisi ante.\n\nNulla tristique gravida gravida. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aenean consectetur pretium lacus eget aliquam. Nulla ut purus sit amet nulla varius sollicitudin quis non dui. Integer at consequat sapien. Vestibulum a nibh odio, sed aliquam justo. In eget dui tellus. Nulla vitae arcu neque, et ullamcorper massa. Curabitur tincidunt mi ac enim pretium interdum. Curabitur neque lorem, aliquam id porttitor vitae, mollis eget nibh. Aliquam mauris libero, luctus eu dictum eleifend, mattis sed erat. In nec ligula ut eros luctus tempus vulputate sed augue.\n\nNullam laoreet massa non velit lacinia quis rhoncus justo tristique. Etiam pellentesque eros ac nulla mattis in molestie leo cursus. Nam consectetur pretium nulla, non vehicula tellus ultrices et. Duis scelerisque, risus sed adipiscing mollis, purus enim facilisis velit, in porta elit metus sit amet nisl. Quisque pellentesque rhoncus gravida. Ut id rutrum metus. Sed id lacus sit amet odio suscipit iaculis in convallis elit. Vestibulum blandit sem sed leo tincidunt mollis. Nullam id viverra arcu. Sed ante leo, aliquam eu volutpat sed, tempus vitae mi. Morbi rutrum lectus quis augue luctus in commodo massa suscipit. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In ultricies tellus ac risus scelerisque in interdum quam tempor. Suspendisse potenti. Nunc condimentum diam ut elit placerat vel rhoncus eros iaculis. Nam eget sapien odio, et auctor eros. Etiam vulputate quam lacus, in dapibus dolor.\n\nNunc molestie sapien enim. Morbi felis nibh, rhoncus sit amet eleifend id, gravida vitae tellus. Morbi ullamcorper ante vitae ipsum blandit at adipiscing velit accumsan. In hac habitasse platea dictumst. Nulla facilisi. Morbi semper sapien vitae purus vehicula semper. Aliquam egestas mattis massa, et rhoncus lacus accumsan id. Curabitur arcu sapien, mattis eu semper ut, luctus tempus massa. Praesent quis dui ut velit vulputate laoreet vel eu lectus. Cras at elit nunc. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam iaculis, urna at condimentum tempor, quam. '

def TextRenderTest():
    import uiconst
    import uicls
    import uiutil
    import trinity
    import blue
    ftime = blue.os.GetTime(1)
    uicore.desktop.Flush()
    print 'flushtime',
    print blue.os.TimeDiffInMs(ftime)
    uicore.ul = 0
    ctime = blue.os.GetTime(1)
    words = LOR.split(' ')
    maxWidth = 0
    topShift = 0
    leftShift = 0
    i = 0
    for word in words:
        l = uicls.Label(text=word, autowidth=1, autoheight=1, align=uiconst.RELATIVE, parent=uicore.desktop, pos=(leftShift,
         topShift,
         0,
         0), name=str(i))
        topShift += l.textheight
        maxWidth = max(maxWidth, l.textwidth)
        if topShift >= trinity.device.height:
            leftShift += maxWidth
            maxWidth = 0
            topShift = 0
        i += 1

    print 'uicore.ul',
    print len(words)
    print 'createtime',
    print blue.os.TimeDiffInMs(ctime)



def DoTarget(amt = 1):
    import trinity
    import uiconst
    import uicls
    import uthread
    import blue
    uicore.desktop.Flush()
    for i in xrange(amt):
        blue.pyos.synchro.Sleep(333)
        _AddTarget()




def AddBinding(sourceObject, sourceAttribute, destObject, destAttribute, curveSet):
    binding = trinity.TriValueBinding()
    binding.sourceObject = sourceObject
    binding.sourceAttribute = sourceAttribute
    binding.destinationObject = destObject
    binding.destinationAttribute = destAttribute
    curveSet.bindings.append(binding)
    return binding



def CreateScalarCurve(destObject, sourceAttr, destAttr, curveSet, length = 1.0, startValue = 0.0, endValue = 0.0, cycle = False, startTangent = 0.0, endTangent = 0.0):
    curve = trinity.Tr2ScalarCurve()
    curve.length = length
    curve.cycle = cycle
    curve.startValue = startValue
    curve.endValue = endValue
    curve.interpolation = 2
    curve.startTangent = startTangent
    curve.endTangent = endTangent
    curveSet.curves.append(curve)
    binding = AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
    return (curve, binding)



def CreateColorCurve(destObject, curveSet, length = 1.0, startValue = (1, 1, 1, 1), endValue = (1, 1, 1, 0), cycle = False):
    curve = trinity.Tr2ColorCurve()
    curve.length = length
    curve.cycle = cycle
    curve.startValue = startValue
    curve.endValue = endValue
    curve.interpolation = 1
    curveSet.curves.append(curve)
    binding = AddBinding(curve, 'currentValue', destObject, 'color', curveSet)
    return (curve, binding)



def _AddTarget():
    import trinity
    import uiconst
    import random
    import uicls
    par = uicls.Container(parent=uicore.desktop, left=256, top=random.randint(1, 500), align=uiconst.RELATIVE, width=300, height=128)
    curveSet = par.CreateCurveSet()
    curveSet.scale = 1.0
    curve = trinity.TriPerlinCurve()
    curve.scale = 1000.0
    curve.offset = -0.0
    curve.N = 2
    curve.speed = 1.0
    curve.alpha = 1000.0
    curve.beta = 5000.0
    curveSet.curves.append(curve)
    binding = trinity.TriValueBinding()
    binding.sourceObject = curve
    binding.sourceAttribute = 'value'
    binding.destinationObject = par
    binding.destinationAttribute = 'displayY'
    binding.scale = 1
    curveSet.bindings.append(binding)
    curve = trinity.TriPerlinCurve()
    curve.scale = 1200.0
    curve.offset = -300.0
    curve.N = 2
    curve.speed = 1.0
    curve.alpha = 1200.0
    curve.beta = 8000.0
    curveSet.curves.append(curve)
    binding = trinity.TriValueBinding()
    binding.sourceObject = curve
    binding.sourceAttribute = 'value'
    binding.destinationObject = par
    binding.destinationAttribute = 'displayX'
    binding.scale = 1
    curveSet.bindings.append(binding)
    inTime = 0.5
    mainParent = uicls.Container(parent=par, name='mainParent', align=uiconst.RELATIVE, width=200, height=64, top=32, left=96)
    maintext = uicls.Sprite(parent=mainParent, texturePath='res:/UICore/texture/text.dds', left=96.0, width=200, height=64, effect=trinity.S2D_RFX_BLUR)
    caption = uicls.Sprite(parent=mainParent, texturePath='res:/UICore/texture/caption.dds', left=50, top=56, width=160, height=32, effect=trinity.S2D_RFX_BLUR)
    bracket = uicls.Sprite(parent=mainParent, texturePath='res:/UICore/texture/brackettext.dds', left=200, top=56, width=100, height=32, effect=trinity.S2D_RFX_BLUR)
    scrolltext = uicls.Label(parent=mainParent, text='0123456789', align=uiconst.TOPLEFT, left=237, top=7, font='res:/UI/Fonts/HelveticaNeueLTStd-Bd.otf', fontsize=9, color=(1.0, 1.0, 1.0, 0.5))
    (curve, binding,) = CreateColorCurve(bracket, curveSet, length=0.5, startValue=(1, 1, 1, 1), endValue=(1, 1, 1, 0), cycle=True)
    curve.AddKey(0.0, (1, 1, 1, 0.0))
    curve.AddKey(0.1, (1, 1, 1, 1))
    curve.AddKey(0.5, (1, 1, 1, 0.0))
    AddBinding(curve, 'currentValue', caption, 'color', curveSet)
    (curve, binding,) = CreateScalarCurve(caption, 'currentValue', 'blurFactor', curveSet, length=inTime * 0.5, startValue=5.0, endValue=0.0, cycle=False)
    AddBinding(curve, 'currentValue', bracket, 'blurFactor', curveSet)
    AddBinding(curve, 'currentValue', maintext, 'blurFactor', curveSet)
    (curve, binding,) = CreateScalarCurve(mainParent, 'currentValue', 'displayX', curveSet, length=inTime, startValue=-500.0, endValue=0.0, endTangent=-1000.0, cycle=False)
    correction = -0.5
    curve = trinity.TriPerlinCurve()
    curve.scale = 400.0
    curve.offset = 200.0
    curveSet.curves.append(curve)
    innerTransform = trinity.Tr2Sprite2dTransform()
    innerTransform.translation = (0, 0)
    innerTransform.rotationCenter = (64, 64)
    par.children.insert(0, innerTransform)
    inner = trinity.Tr2Sprite2d()
    innerTransform.children.append(inner)
    inner.displayWidth = inner.displayHeight = 128
    inner.displayX = correction
    inner.displayY = correction
    inner.texturePrimary = trinity.Tr2Sprite2dTexture()
    inner.texturePrimary.resPath = 'res:/uicore/Texture/innercircles.dds'
    inner.effect = trinity.S2D_RFX_BLUR
    inner.blurFactor = 0.1
    binding = trinity.TriValueBinding()
    binding.sourceObject = curve
    binding.sourceAttribute = 'value'
    binding.destinationObject = innerTransform
    binding.destinationAttribute = 'rotation'
    binding.scale = 0.025
    curveSet.bindings.append(binding)
    curve = trinity.TriSineCurve()
    curve.scale = 500.0
    curve.offset = 300.0
    curve.speed = 0.3
    curveSet.curves.append(curve)
    outerTransform = trinity.Tr2Sprite2dTransform()
    outerTransform.translation = (0, 0)
    outerTransform.rotationCenter = (64, 64)
    par.children.insert(0, outerTransform)
    outer = trinity.Tr2Sprite2d()
    outerTransform.children.append(outer)
    outer.displayWidth = outer.displayHeight = 128
    outer.displayX = correction
    outer.displayY = correction
    outer.texturePrimary = trinity.Tr2Sprite2dTexture()
    outer.texturePrimary.resPath = 'res:/uicore/Texture/outercircles.dds'
    outer.effect = trinity.S2D_RFX_BLUR
    outer.blurFactor = 0.1
    binding = trinity.TriValueBinding()
    binding.sourceObject = curve
    binding.sourceAttribute = 'value'
    binding.destinationObject = outerTransform
    binding.destinationAttribute = 'rotation'
    binding.scale = 0.00125
    curveSet.bindings.append(binding)
    curveSet.Play()


import blue
import trinity
import random
import uthread
import geo2
iconFiles = ['02', '16', '32']

def CreateRandomIcon():
    sprite = trinity.Tr2Sprite2d()
    name = iconFiles[random.randint(0, len(iconFiles) - 1)]
    size = 64
    name = 'res:/UI/Texture/Icons/icons' + name + '.dds'
    tex = trinity.Tr2Sprite2dTexture()
    tex.resPath = name
    sprite.texturePrimary = tex
    sprite.displayWidth = size
    sprite.displayHeight = size
    sprite.color = (1, 1, 1, 1)
    return sprite



def SetupLotsOfIcons(parent, curveSet, n):
    for i in xrange(n):
        sprite = CreateRandomIcon()
        curve = trinity.TriPerlinCurve()
        curve.scale = 100.0
        curve.offset = 0.0
        curve.speed = random.random()
        binding = trinity.TriValueBinding()
        binding.sourceObject = curve
        binding.sourceAttribute = 'value'
        binding.destinationObject = sprite
        binding.destinationAttribute = 'displayX'
        curveSet.curves.append(curve)
        curveSet.bindings.append(binding)
        curve = trinity.TriPerlinCurve()
        curve.scale = 100.0
        curve.offset = 0.0
        curve.speed = random.random()
        binding = trinity.TriValueBinding()
        binding.sourceObject = curve
        binding.sourceAttribute = 'value'
        binding.destinationObject = sprite
        binding.destinationAttribute = 'displayY'
        curveSet.curves.append(curve)
        curveSet.bindings.append(binding)
        sprite.color = (random.random(),
         random.random(),
         random.random(),
         1.0)
        parent.children.append(sprite)




def CreateEaseInCurve(length):
    curve = trinity.Tr2ScalarCurve()
    curve.AddKey(0, 0)
    curve.AddKey(length, 1)
    curve.interpolation = trinity.TR2CURVE_HERMITE
    return curve



def CreateEaseOutCurve(length):
    curve = trinity.Tr2ScalarCurve()
    curve.AddKey(0, 1)
    curve.AddKey(length, 0)
    curve.interpolation = trinity.TR2CURVE_HERMITE
    return curve



class EventHandler:

    def __init__(self, scene, owner):
        self.scene = scene
        self.owner = owner
        self.fadeDuration = 0.5



    def __call__(self, name):
        print name,
        print self.owner.name
        if name.startswith(u'Fade'):
            self.HandleFade(name)
        elif name.startswith(u'Blur'):
            self.HandleBlur(name)
        elif name.startswith(u'Display'):
            self.HandleDisplay(name)



    def HandleFade(self, name):
        cs = trinity.TriCurveSet()
        cs.name = str(name)
        curve = self.CreateCurveFromName(name)
        binding = self.CreateBinding(curve, 'color.a')
        cs.curves.append(curve)
        cs.bindings.append(binding)
        uthread.new(self.AddCurveSet_t, cs)



    def HandleBlur(self, name):
        cs = trinity.TriCurveSet()
        cs.name = str(name)
        curve = self.CreateCurveFromName(name)
        binding = self.CreateBinding(curve, 'blurFactor')
        cs.curves.append(curve)
        cs.bindings.append(binding)
        uthread.new(self.AddCurveSet_t, cs)



    def HandleDisplay(self, name):
        if name.endswith(u'On'):
            self.owner.display = True
        elif name.endswith(u'Off'):
            self.owner.display = False



    def AddCurveSet_t(self, cs):
        cs.Play()
        cs.StopAfter(self.fadeDuration)
        self.scene.curveSets.append(cs)



    def CreateBinding(self, curve, attribute):
        binding = trinity.TriValueBinding()
        binding.sourceObject = curve
        binding.sourceAttribute = 'currentValue'
        binding.destinationObject = self.owner
        binding.destinationAttribute = attribute
        return binding



    def CreateCurveFromName(self, name):
        if name.endswith(u'In'):
            return CreateEaseInCurve(self.fadeDuration)
        if name.endswith(u'Out'):
            return CreateEaseOutCurve(self.fadeDuration)




def SetupAnimation(scene):
    layer1 = trinity.Tr2Sprite2dLayer()
    layer1.name = u'Layer 1'
    layer1.displayX = 80
    layer1.displayY = 80
    layer1.displayWidth = 400
    layer1.displayHeight = 200
    layer1.color = (1.0, 1.0, 1.0, 1.0)
    layer1.backgroundColor = (1.0, 0.2, 0.2, 0.5)
    layer1.clearBackground = True
    layer1.blendMode = trinity.TR2_SBM_BLEND
    for i in xrange(10):
        sprite = CreateRandomIcon()
        sprite.displayX = random.randint(0, 100)
        sprite.displayY = random.randint(0, 100)
        layer1.children.append(sprite)

    cs = trinity.TriCurveSet()
    SetupLotsOfIcons(layer1, cs, 20)
    scene.children.append(layer1)
    scene.curveSets.append(cs)
    cs.Play()
    layer2 = trinity.Tr2Sprite2dLayer()
    layer2.name = 'Layer 2'
    layer2.displayX = 40
    layer2.displayY = 40
    layer2.displayWidth = 400
    layer2.displayHeight = 200
    layer2.color = (1.0, 1.0, 1.0, 1.0)
    layer2.backgroundColor = (0.2, 1.0, 0.2, 1.0)
    layer2.clearBackground = True
    layer2.blendMode = trinity.TR2_SBM_BLEND
    for i in xrange(10):
        sprite = CreateRandomIcon()
        sprite.displayX = random.randint(0, 100)
        sprite.displayY = random.randint(0, 100)
        layer2.children.append(sprite)

    scene.children.append(layer2)
    ec1 = trinity.TriEventCurve()
    ec1.eventListener = blue.BlueEventToPython()
    ec1.eventListener.handler = EventHandler(scene, layer1)
    ec1.AddKey(1.0, u'FadeIn')
    ec1.AddKey(5.0, u'FadeOut')
    ec1.AddKey(6.0, u'DisplayOff')
    ec1.AddKey(6.1, u'End')
    ec2 = trinity.TriEventCurve()
    ec2.eventListener = blue.BlueEventToPython()
    ec2.eventListener.handler = EventHandler(scene, layer2)
    ec2.AddKey(1.0, u'BlurIn')
    ec2.AddKey(5.0, u'BlurOut')
    ec2.AddKey(6.0, u'DisplayOff')
    ec2.AddKey(6.1, u'End')
    cs = trinity.TriCurveSet()
    cs.name = 'Events'
    cs.curves.append(ec1)
    cs.curves.append(ec2)



def CreateScene3d(tex):
    scene = trinity.Tr2InteriorScene()
    room = trinity.Load('res:/Graphics/Interior/Unique/Test/Test1/Test1WodInteriorStatic.red')
    cell = trinity.Tr2InteriorCell()
    scene.cells.append(cell)
    room.rotation = (0.0, -0.44663557410240173, 0.0, 0.8947159647941589)
    scene.sunDirection = (0.4367, -0.3684, 0.8207)
    scene.shadowCubeMap.enabled = True
    lightSource = trinity.Tr2InteriorLightSource()
    lightSource.radius = 12.0
    lightSource.falloff = 0.6
    lightSource.position = (1.308, 1.7335, 1.4637)
    lightSource.color = (306.0 / 255.0, 238.79999999999998 / 255.0, 212.4 / 255.0)
    scene.AddLightSource(lightSource)
    lightSource = trinity.Tr2InteriorLightSource()
    lightSource.radius = 12.0
    lightSource.falloff = 0.6
    lightSource.position = (1.7305, 2.0731, -1.7867)
    lightSource.color = (266.4 / 255.0, 279.59999999999997 / 255.0, 306.0 / 255.0)
    scene.AddLightSource(lightSource)
    lightSource = trinity.Tr2InteriorLightSource()
    lightSource.radius = 12.0
    lightSource.falloff = 0.6
    lightSource.position = (-1.7793, 1.016, 0.1315)
    lightSource.color = (115.19999999999999 / 255.0, 147.6 / 255.0, 222.0 / 255.0)
    scene.AddLightSource(lightSource)
    scene.sunDiffuseColor = (44.0 / 255.0,
     35.0 / 255.0,
     35.0 / 255.0,
     1.0)
    scene.ambientColor = (0.0 / 255.0, 0.0 / 255.0, 0.0 / 255.0)
    screen = trinity.Tr2InteriorPlaceable()
    screen.placeableResPath = 'res:/Graphics/Placeable/UI/SimpleQuad/SimpleQuad.red'
    texParams = screen.placeableRes.Find('trinity.TriTexture2DParameter')
    diffuseMap = None
    for each in texParams:
        if each.name == 'DiffuseMap':
            diffuseMap = each
            break

    if diffuseMap:
        diffuseMap.SetResource(tex)
    screen.translation = (1, 2, 0)
    screen.rotation = geo2.QuaternionRotationSetYawPitchRoll(-0.6, 0.3, 0.1)
    scene.AddDynamic(screen)
    return (scene, screen)



def CreateRenderJob(scene):
    rj = trinity.CreateRenderJob()
    rj.name = '3D scene'
    return rj



def CreateSceneWithUI():
    del trinity.device.scheduledRecurring[:]
    scene2d = trinity.Tr2Sprite2dScene()
    scene2d.width = 512
    scene2d.height = 512
    scene2d.clearBackground = True
    scene2d.isFullScreen = False
    tex = trinity.device.CreateTexture(512, 512, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_DEFAULT)
    (scene, screen,) = CreateScene3d(tex)
    scene2d.translation = screen.translation
    scene2d.rotation = screen.rotation
    scene2d.scaling = screen.scaling
    SetupAnimation(scene2d)
    rj = trinity.CreateRenderJob()
    rj.name = 'Scene with UI'
    rj.Update(scene).name = 'Update 3D scene'
    rj.Update(scene2d).name = 'Update 2D scene'
    rj.SetRenderTarget(tex.GetSurfaceLevel(0)).name = 'Set texture as render target'
    rj.RenderScene(scene2d).name = 'Render 2D scene'
    rj.SetRenderTarget(trinity.device.GetBackBuffer()).name = 'Set framebuffer as render target'
    rj.RenderScene(scene).name = 'Render 3D scene'
    rj.ScheduleRecurring()
    picker = Scene2dPicker(scene2d)
    trinity.device.tickInterval = 0


exports = {'uitest.TextRenderTest': TextRenderTest,
 'uitest.DoTarget': DoTarget,
 'uitest.KillOldCursor': KillOldCursor,
 'uitest.CreateScalarCurve': CreateScalarCurve,
 'uitest.CreateSceneWithUI': CreateSceneWithUI}

