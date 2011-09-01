import uicls
import uiconst
import trinity
import types
import weakref
import GameWorld

class TexturedBase(uicls.Base):
    __guid__ = 'uicls.TexturedBase'
    __renderObject__ = None
    default_name = 'TexturedBase'
    default_noScale = 0
    default_texturePath = None
    default_textureSecondaryPath = None
    default_left = 0
    default_top = 0
    default_color = (1, 1, 1, 1)
    default_blendMode = trinity.TR2_SBM_BLEND
    default_blurFactor = 0.0
    default_depth = 0.0
    default_glowFactor = 0.0
    default_glowExpand = 0.0
    default_glowColor = (1, 1, 1, 1)
    default_shadowOffset = (0, 0)
    default_shadowColor = (0, 0, 0, 0.5)
    default_spriteEffect = trinity.TR2_SFX_COPY

    def ApplyAttributes(self, attributes):
        uicls.Base.ApplyAttributes(self, attributes)
        self._color = uicls.UIColor(self)
        self.texture = trinity.Tr2Sprite2dTexture()
        self.blendMode = attributes.get('blendMode', self.default_blendMode)
        self.blurFactor = attributes.get('blurFactor', self.default_blurFactor)
        self.SetTexturePath(attributes.get('texturePath', self.default_texturePath))
        secondaryPath = attributes.get('textureSecondaryPath', self.default_textureSecondaryPath)
        self.textureSecondary = None
        if secondaryPath:
            self.SetSecondaryTexturePath(secondaryPath)
        self.depth = attributes.get('depth', self.default_depth)
        self.glowFactor = attributes.get('glowFactor', self.default_glowFactor)
        self.glowExpand = attributes.get('glowExpand', self.default_glowExpand)
        self.glowColor = attributes.get('glowColor', self.default_glowColor)
        self.shadowOffset = attributes.get('shadowOffset', self.default_shadowOffset)
        self.shadowColor = attributes.get('shadowColor', self.default_shadowColor)
        self.rectLeft = attributes.rectLeft or 0
        self.rectTop = attributes.rectTop or 0
        self.rectWidth = attributes.rectWidth or 0
        self.rectHeight = attributes.rectHeight or 0
        self.spriteEffect = attributes.get('spriteEffect', self.default_spriteEffect)
        color = attributes.get('color', self.default_color)
        if type(color) == types.TupleType:
            self.SetRGB(*color)
        self.__dict__['isReady'] = True



    def Close(self):
        if getattr(self, 'destroyed', False):
            return 
        self.texture = None
        RO = self.GetRenderObject()
        if hasattr(RO, 'texturePrimary'):
            RO.texturePrimary = None
        if hasattr(RO, 'textureSecondary'):
            RO.textureSecondary = None
        if hasattr(RO, 'texture'):
            RO.texture = None
        uicls.Base.Close(self)



    @apply
    def spriteEffect():
        doc = '\n        determines how the primary and secondary textures are blended together. Must be\n        a trinity.TR2_SFX_{X} constant'

        def fget(self):
            return self._spriteEffect



        def fset(self, value):
            self._spriteEffect = value
            ro = self.renderObject
            if ro and hasattr(ro, 'spriteEffect'):
                ro.spriteEffect = self._spriteEffect


        return property(**locals())



    @apply
    def texture():
        doc = 'The primary texture. An instance of trinity.Tr2Sprite2dTexture'

        def fget(self):
            return self._texture



        def fset(self, value):
            self._texture = value
            ro = self.renderObject
            if ro:
                ro.texturePrimary = self._texture


        return property(**locals())



    @apply
    def textureSecondary():
        doc = 'The secondary texture. An instance of trinity.Tr2Sprite2dTexture'

        def fget(self):
            return self._textureSecondary



        def fset(self, value):
            self._textureSecondary = value
            ro = self.renderObject
            if ro and value is not None:
                ro.textureSecondary = self._textureSecondary


        return property(**locals())



    @apply
    def blendMode():
        doc = '\n        Determines how the sprite blends with the background. Must be Must be a \n        trinity.TR2_SBM_{X} constant'

        def fget(self):
            return self._blendMode



        def fset(self, value):
            self._blendMode = value
            ro = self.renderObject
            if ro:
                ro.blendMode = value


        return property(**locals())



    @apply
    def rectLeft():
        doc = 'Manually set left edge of primary texture'

        def fget(self):
            return self._rectLeft



        def fset(self, value):
            self._rectLeft = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcX = value


        return property(**locals())



    @apply
    def rectTop():
        doc = 'Manually set top edge of primary texture'

        def fget(self):
            return self._rectTop



        def fset(self, value):
            self._rectTop = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcY = value


        return property(**locals())



    @apply
    def rectWidth():
        doc = 'Manually set width of primary texture'

        def fget(self):
            return self._rectWidth



        def fset(self, value):
            self._rectWidth = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcWidth = value


        return property(**locals())



    @apply
    def rectHeight():
        doc = 'Manually set height of primary texture'

        def fget(self):
            return self._rectHeight



        def fset(self, value):
            self._rectHeight = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcHeight = value


        return property(**locals())



    @apply
    def color():
        doc = 'Set color as (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            return self._color



        def fset(self, value):
            if type(value) == uicls.UIColor:
                self._color = value
            elif type(value) == types.TupleType:
                self.SetRGB(*value)
            ro = self.renderObject
            if ro:
                ro.color = self._color.GetRGBA()



        def fdel(self):
            self._color = None


        return property(**locals())



    @apply
    def opacity():
        doc = 'opacity [0.0 - 1.0]'

        def fget(self):
            return self.color.a



        def fset(self, value):
            self.color.a = value


        return property(**locals())



    @apply
    def depth():
        doc = 'z-axis offset. Only has meaning when using with 3d rendering'

        def fget(self):
            return self._depth



        def fset(self, value):
            self._depth = value
            ro = self.renderObject
            if ro:
                ro.depth = value


        return property(**locals())



    @apply
    def blurFactor():
        doc = 'Blur effect amount [0.0 - 1.0]'

        def fget(self):
            return self._blurFactor



        def fset(self, value):
            self._blurFactor = value
            ro = self.renderObject
            if ro:
                ro.blurFactor = value


        return property(**locals())



    @apply
    def glowFactor():
        doc = 'Glow effect amount [0.0 - 1.0]'

        def fget(self):
            return self._glowFactor



        def fset(self, value):
            self._glowFactor = value
            ro = self.renderObject
            if ro:
                ro.glowFactor = value


        return property(**locals())



    @apply
    def glowExpand():
        doc = 'Glow effect expand [0.0 - inf]'

        def fget(self):
            return self._glowExpand



        def fset(self, value):
            self._glowExpand = value
            ro = self.renderObject
            if ro:
                ro.glowExpand = value


        return property(**locals())



    @apply
    def glowColor():
        doc = 'Glow effect color tuple (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            return self._glowColor



        def fset(self, value):
            self._glowColor = value
            ro = self.renderObject
            if ro:
                ro.glowColor = value


        return property(**locals())



    @apply
    def shadowOffset():
        doc = 'Shadow effect offset tuple (x,y) [0.0 - inf]'

        def fget(self):
            return self._shadowOffset



        def fset(self, value):
            self._shadowOffset = value
            ro = self.renderObject
            if ro:
                ro.shadowOffset = value


        return property(**locals())



    @apply
    def shadowColor():
        doc = 'Shadow effect color tuple (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            return self._shadowColor



        def fset(self, value):
            self._shadowColor = value
            ro = self.renderObject
            if ro:
                ro.shadowColor = value


        return property(**locals())



    def SetTexturePath(self, texturePath):
        if self.texture:
            self.texture.resPath = str(texturePath or '')


    LoadTexture = SetTexturePath

    def GetTexturePath(self):
        if self.texture:
            return self.texture.resPath


    texturePath = property(GetTexturePath, SetTexturePath)

    def SetSecondaryTexturePath(self, texturePath):
        if not self.textureSecondary:
            self.textureSecondary = trinity.Tr2Sprite2dTexture()
        self.textureSecondary.resPath = str(texturePath or '')



    def GetSecondaryTexturePath(self):
        if self.textureSecondary:
            return self.textureSecondary.resPath



    def SetRect(self, rectLeft, rectTop, rectWidth, rectHeight):
        self.rectLeft = rectLeft
        self.rectTop = rectTop
        self.rectWidth = rectWidth
        self.rectHeight = rectHeight



    def LoadIcon(self, iconNo, ignoreSize = False):
        if self.destroyed:
            return 
        if iconNo.startswith('res:') or iconNo.startswith('cache:'):
            self.LoadTexture(iconNo)
            return 
        while iconNo.find('_0') != -1 or iconNo.find('/0') != -1:
            iconNo = iconNo.replace('_0', '_').replace('/0', '/')

        if iconNo.startswith('ui_'):
            (root, sheetNo, iconSize, icon,) = iconNo.split('_')
            resPath = 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheetNo), int(iconSize), int(icon))
            iconSize = int(iconSize)
            self.LoadTexture(resPath)
            if not ignoreSize and self.GetAlign() != uiconst.TOALL and self.texture.atlasTexture:
                self.width = iconSize
                self.height = iconSize
            return 
        return iconNo



    def SetRGB(self, *color):
        if type(color) != types.TupleType:
            return 
        if not getattr(self, 'color', None):
            self.color = uicls.UIColor(self)
        self.color.SetRGB(*color)


    SetRGBA = SetRGB

    def GetRGB(self):
        return self.color.GetRGB()



    def GetRGBA(self):
        return self.color.GetRGBA()



    def SetAlpha(self, alpha):
        self.color.SetAlpha(alpha)



    def GetAlpha(self):
        return self.color.GetAlpha()




class Sprite(TexturedBase):
    __guid__ = 'uicls.Sprite'
    __renderObject__ = trinity.Tr2Sprite2d
    default_name = 'sprite'
    default_noScale = 0
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_pickRadius = 0

    def ApplyAttributes(self, attributes):
        TexturedBase.ApplyAttributes(self, attributes)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)



    @apply
    def pickRadius():
        doc = 'Pick radius'

        def fget(self):
            return self._pickRadius



        def fset(self, value):
            self._pickRadius = value
            ro = self.renderObject
            if ro and hasattr(ro, 'pickRadius'):
                ro.pickRadius = value or 0.0


        return property(**locals())




class VideoSprite(Sprite):
    __guid__ = 'uicls.VideoSprite'
    __renderObject__ = trinity.Tr2Sprite2d
    __notifyevents__ = ['OnAudioActivated']
    default_name = 'videosprite'
    default_videoPath = ''
    default_videoLoop = False
    default_videoAutoPlay = True
    default_muteAudio = False

    def Close(self, *args, **kwds):
        self.Pause()
        uicore.uilib.GetVideoJob().steps.fremove(self._updateStep)
        if self.positionComponent:
            self.positionComponent.UnRegisterPlacementObserverWrapper(self.positionObserver)
            self.positionComponent = None
            self.positionObserver = None
        self.emitter = None
        self._updateStep = None
        Sprite.Close(self, *args, **kwds)



    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.spriteEffect = trinity.TR2_SFX_BINK
        self._updateStep = None
        RO = self.GetRenderObject()
        if 'videoPath' in attributes:
            tex = trinity.Tr2Sprite2dBinkTexture()
            tempPositionComponent = attributes.get('positionComponent', None)
            (self.emitter, outputChannel,) = sm.GetService('audio').GetAudioBus(is3D=tempPositionComponent is not None)
            tex.outputChannel = outputChannel
            self.positionComponent = self.SetPositionComponent(tempPositionComponent)
            tex.resPath = attributes.get('videoPath', self.default_videoPath)
            if 'pos' in attributes:
                pos = attributes.get('pos', (self.default_left,
                 self.default_top,
                 self.default_width,
                 self.default_height))
                (RO.displayX, RO.displayY, RO.displayWidth, RO.displayHeight,) = pos
            tex.loop = attributes.get('videoLoop', self.default_videoLoop)
            if attributes.get('muteAudio', self.default_muteAudio):
                tex.MuteAudio()
            tex.Play()
            self.texture = tex
            if attributes.get('videoAutoPlay', self.default_videoAutoPlay):
                self._updateStep = uicore.uilib.GetVideoJob().Update(RO.texturePrimary)



    def OnAudioActivated(self):
        if not self.texture:
            return 
        self.Pause()
        if self._updateStep:
            uicore.uilib.GetVideoJob().steps.fremove(self._updateStep)
            self._updateStep = None
        self.emitter = None
        (self.emitter, self.texture.outputChannel,) = sm.GetService('audio').GetAudioBus(is3D=self.positionComponent is not None)
        self.SetVideoPath(self.texture.resPath)
        RO = self.GetRenderObject()
        if RO:
            self._updateStep = uicore.uilib.GetVideoJob().Update(RO.texturePrimary)
        self.Play()



    def SetPositionComponent(self, positionComponent):
        if self.emitter and positionComponent:
            if positionComponent:
                self.positionObserver = GameWorld.PlacementObserverWrapper(self.emitter)
                positionComponent.RegisterPlacementObserverWrapper(self.positionObserver)
                return positionComponent



    def GetVideoSize(self):
        RO = self.GetRenderObject()
        if RO and RO.texturePrimary.atlasTexture:
            return (RO.texturePrimary.atlasTexture.width, RO.texturePrimary.atlasTexture.height)



    def SetVideoPath(self, path):
        RO = self.GetRenderObject()
        if RO:
            RO.texturePrimary.resPath = path



    def Play(self):
        RO = self.GetRenderObject()
        if RO:
            RO.texturePrimary.Play()
            if self._updateStep is None:
                self._updateStep = uicore.uilib.GetVideoJob().Update(RO.texturePrimary)



    def Pause(self):
        RO = self.GetRenderObject()
        if RO:
            RO.texturePrimary.Pause()



    def MuteAudio(self):
        RO = self.GetRenderObject()
        if RO:
            RO.texturePrimary.MuteAudio()



    def UnmuteAudio(self):
        RO = self.GetRenderObject()
        if RO:
            RO.texturePrimary.UnmuteAudio()



    @apply
    def isMuted():
        doc = ''

        def fget(self):
            RO = self.GetRenderObject()
            if RO:
                return RO.texturePrimary.isMuted


        return property(**locals())



    @apply
    def isPaused():
        doc = ''

        def fget(self):
            RO = self.GetRenderObject()
            if RO:
                return RO.texturePrimary.isPaused


        return property(**locals())



    @apply
    def isFinished():
        doc = ''

        def fget(self):
            if self.destroyed:
                return True
            RO = self.GetRenderObject()
            if RO:
                return RO.texturePrimary.isFinished


        return property(**locals())



    @apply
    def videoFps():
        doc = ''

        def fget(self):
            RO = self.GetRenderObject()
            if RO:
                return RO.texturePrimary.videoFps


        return property(**locals())



    @apply
    def currentFrame():
        doc = ''

        def fget(self):
            RO = self.GetRenderObject()
            if RO:
                return RO.texturePrimary.currentFrame


        return property(**locals())




class PyColor(object):
    __guid__ = 'uicls.UIColor'

    def __init__(self, owner, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        self.owner = weakref.ref(owner)
        self._r = r
        self._g = g
        self._b = b
        self._a = a
        self.UpdateOwner()



    def UpdateOwner(self):
        owner = self.owner()
        if owner is not None:
            if owner.renderObject:
                owner.renderObject.color = (self._r,
                 self._g,
                 self._b,
                 self._a)



    @apply
    def r():
        doc = 'Red component of this color'

        def fget(self):
            return self._r



        def fset(self, value):
            self._r = value
            self.UpdateOwner()


        return property(**locals())



    @apply
    def g():
        doc = 'Green component of this color'

        def fget(self):
            return self._g



        def fset(self, value):
            self._g = value
            self.UpdateOwner()


        return property(**locals())



    @apply
    def b():
        doc = 'Blue component of this color'

        def fget(self):
            return self._b



        def fset(self, value):
            self._b = value
            self.UpdateOwner()


        return property(**locals())



    @apply
    def a():
        doc = 'Alpha component of this color'

        def fget(self):
            return self._a



        def fset(self, value):
            self._a = value
            self.UpdateOwner()


        return property(**locals())



    def SetRGB(self, r, g, b, a = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


    SetRGBA = SetRGB

    def GetRGB(self):
        return (self.r, self.g, self.b)



    def GetRGBA(self):
        return (self.r,
         self.g,
         self.b,
         self.a)



    def SetAlpha(self, a):
        self.a = a



    def GetAlpha(self):
        return self.a



    def GetHSV(self):
        return trinity.TriColor(*self.GetRGBA()).GetHSV()



    def SetHSV(self, h, s, v):
        c = trinity.TriColor()
        c.SetHSV(h, s, v)
        self.SetRGB(c.r, c.g, c.b)




