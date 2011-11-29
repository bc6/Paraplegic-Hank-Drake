import uicls
import uiconst
import trinity
import uiutil
import bluepy

class Frame(uicls.TexturedBase):
    __guid__ = 'uicls.FrameCore'
    __renderObject__ = trinity.Tr2Sprite2dFrame
    default_name = 'framesprite'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_align = uiconst.TOALL
    default_frameConst = uiconst.FRAME_BORDER1_CORNER0
    default_state = uiconst.UI_DISABLED
    default_offset = 0
    default_cornerSize = 6
    default_fillCenter = True
    default_filter = False

    def PrepareProperties(self):
        self._offset = 0
        self._cornerSize = 0



    def ApplyAttributes(self, attributes):
        self.offset = self.default_offset
        self.cornerSize = self.default_cornerSize
        self.fillCenter = attributes.get('fillCenter', self.default_fillCenter)
        uicls.TexturedBase.ApplyAttributes(self, attributes)
        texturePath = attributes.get('texturePath', self.default_texturePath)
        if texturePath:
            self.cornerSize = attributes.get('cornerSize', self.default_cornerSize)
            self.offset = attributes.get('offset', self.default_offset)
        else:
            self.LoadFrame(attributes.get('frameConst', self.default_frameConst))



    @apply
    def cornerSize():
        doc = ''

        def fget(self):
            return self._cornerSize



        def fset(self, value):
            self._cornerSize = value
            ro = self.renderObject
            if ro:
                ro.cornerSize = value


        return property(**locals())



    @apply
    def fillCenter():
        doc = 'If True, the center of the frame is filled - otherwise it is left blank'

        def fget(self):
            return self._fillCenter



        def fset(self, value):
            self._fillCenter = value
            ro = self.renderObject
            if ro:
                ro.fillCenter = value


        return property(**locals())



    @apply
    def offset():
        doc = '\n        Offset the frame. Positive values will make it smaller, and negative bigger.\n        '

        def fget(self):
            return self._offset



        def fset(self, value):
            self._offset = value
            ro = self.renderObject
            if ro:
                ro.offset = value
            self.FlagAlignmentDirty()


        return property(**locals())



    def LoadFrame(self, frameConst = None):
        frameConst = frameConst or uiconst.FRAME_BORDER1_CORNER0
        if len(frameConst) == 4:
            (iconNo, cornerSize, offset, fillCenter,) = frameConst
            self.fillCenter = fillCenter
        else:
            (iconNo, cornerSize, offset,) = frameConst
            self.fillCenter = True
        if 'ui_' in iconNo:
            resPath = iconNo.replace('ui_', 'res:/ui/texture/icons/') + '.png'
        else:
            resPath = iconNo
        self.SetTexturePath(resPath)
        self.cornerSize = cornerSize
        self.offset = offset



    def SetOffset(self, offset):
        self.offset = offset



    def GetOffset(self):
        return self.offset



    def SetCornerSize(self, cornerSize = 0):
        self.cornerSize = cornerSize



    def GetCornerSize(self):
        return self.cornerSize




