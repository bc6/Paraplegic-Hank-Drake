import uicls
import uiconst
import trinity

class WindowUnderlay(uicls.Container):
    __guid__ = 'uicls.WindowUnderlay'
    default_name = 'underlay'
    default_state = uiconst.UI_PICKCHILDREN
    default_padLeft = 1
    default_padTop = 1
    default_padRight = 1
    default_padBottom = 1
    default_transparent = True

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        self.background.append(uicls.Frame(name='base', texturePath='res:/UI/Texture/Shared/windowDOTWithOffset.png', cornerSize=10, offset=-5, spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD, fillCenter=False))
        self.background.append(uicls.WindowBaseColor(name='color', state=uiconst.UI_DISABLED, color=color, transparent=attributes.Get('transparent', self.default_transparent)))




class WindowBaseColor(uicls.Frame):
    __guid__ = 'uicls.WindowBaseColor'
    __notifyevents__ = ['OnUIColorsChanged']
    default_name = 'color'
    default_state = uiconst.UI_DISABLED
    default_transparent = True
    default_frameConst = ('res:/UI/Texture/Shared/windowShapeAndShadow.png', 9, -5)

    def ApplyAttributes(self, attributes):
        uicls.Frame.ApplyAttributes(self, attributes)
        self.transparent = attributes.Get('transparent', self.default_transparent)
        self.OnUIColorsChanged()
        sm.RegisterNotify(self)



    def OnUIColorsChanged(self, *args):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        if self.transparent:
            self.SetRGB(*color)
        else:
            (r, g, b, a,) = color
            self.SetRGB(r * a, g * a, b * a, 1.0)




class BumpedUnderlay(uicls.Frame):
    __guid__ = 'uicls.BumpedUnderlay'
    __notifyevents__ = ['OnUIColorsChanged']
    default_name = 'background'
    default_texturePath = 'res:/UI/Texture/Shared/underlayBumped.png'
    default_cornerSize = 6
    default_state = uiconst.UI_DISABLED
    inLiteMode = False

    def ApplyAttributes(self, attributes):
        uicls.Frame.ApplyAttributes(self, attributes)
        self.OnUIColorsChanged()
        sm.RegisterNotify(self)



    def OnUIColorsChanged(self, *args):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        (r, g, b, a,) = bgColor
        if self.inLiteMode:
            a = max(0.3, a * 0.3)
        self.SetRGB(r, g, b, a)



    def LiteMode(self, liteMode = True):
        self.inLiteMode = liteMode
        self.OnUIColorsChanged()




