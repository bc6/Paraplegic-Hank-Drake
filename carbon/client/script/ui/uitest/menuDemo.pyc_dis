#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/uitest/menuDemo.py
import uiconst
import uicls
import uiutil
import trinity
import blue
import cameras

class MenuDemo(uicls.Container):
    __guid__ = 'uicls.MenuDemo'
    default_name = 'MenuDemo'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        import ccConst
        uicore.desktop3D.depthMin = -50
        uicore.desktop3D.depthMax = 50
        uicore.layer.menu3d.depthMin = -1
        uicore.layer.menu3d.depthMax = 1
        self.depthMin = -1
        self.depthMax = 1
        for i in xrange(6):
            btn = Button(parent=self, left=20, top=i * 40 + 250)
            shadow = uicls.Frame(name='shadow', parent=self, frameConst=uiconst.FRAME_FILLED_CORNER8, align=uiconst.CENTERTOP, pos=(20,
             i * 40 + 254,
             btn.width,
             btn.height), depth=0.25, color=(0, 0, 0, 0.25))

        self.sr.menuParent = uicls.Container(parent=self, pos=(50, 0, 700, 500), align=uiconst.CENTERRIGHT, depthMin=1.0, depthMax=1.0)
        uicls.Frame(parent=self.sr.menuParent, name='background', state=uiconst.UI_DISABLED, frameConst=uiconst.FRAME_FILLED_CORNER3, color=(0, 0, 0, 0.25))
        uicls.Fill(parent=self)
        self._AddTarget()

    def _AddTarget(self, dock = False, flush = False):
        import random
        dockCounter = 0
        if flush:
            for each in self.children[:]:
                if isinstance(each, uicls.StretchLine) or each.name == 'targetTest':
                    each.Close()
                else:
                    for child in each.children[:]:
                        if child.name == 'targetTest':
                            child.Close()

            for each in self.children[:]:
                if each.name == 'targetTest':
                    each.Close()

        else:
            for each in self.parent.children:
                if each.name == 'targetTest':
                    dockCounter += 1

        inTime = 0.5
        curveSet = trinity.TriCurveSet()
        curveSet.scale = 1.0
        par = uicls.Container(parent=self, name='targetTest', left=100, top=0, align=uiconst.TOPLEFT, width=300, height=128, idx=0)
        mainParent = uicls.Container(parent=par, name='mainParent', align=uiconst.RELATIVE, width=200, height=64, top=32, left=96)
        maintext = uicls.Sprite(parent=mainParent, texturePath='res:/ui/sprite/carbontest/text.dds', left=96.0, width=200, height=64, effect=trinity.S2D_RFX_BLUR)
        caption = uicls.Sprite(parent=mainParent, texturePath='res:/ui/sprite/carbontest/caption.dds', left=50, top=56, width=160, height=32, effect=trinity.S2D_RFX_BLUR)
        bracket = uicls.Sprite(parent=mainParent, texturePath='res:/ui/sprite/carbontest/brackettext.dds', left=200, top=56, width=100, height=32, effect=trinity.S2D_RFX_BLUR)
        scrolltext = uicls.Label(parent=mainParent, text='0123456789', align=uiconst.TOPLEFT, left=237, top=7, fontsize=9, color=(1.0, 1.0, 1.0, 0.5))
        curve, binding = self.CreateColorCurve(bracket, curveSet, length=0.5, startValue=(1, 1, 1, 1), endValue=(1, 1, 1, 0), cycle=True)
        curve.AddKey(0.0, (1, 1, 1, 0.0))
        curve.AddKey(0.1, (1, 1, 1, 1))
        curve.AddKey(0.5, (1, 1, 1, 0.0))
        self.AddBinding(curve, 'currentValue', caption, 'color', curveSet)
        curve, binding = self.CreateScalarCurve(mainParent, 'currentValue', 'displayX', curveSet, length=inTime, startValue=-500.0, endValue=0.0, endTangent=-1000.0, cycle=False)
        correction = 0.0
        innerTransform = uicls.Transform(parent=par, idx=0, left=8, top=8)
        innerTransform.rotationCenter = (64, 64)
        inner = uicls.Sprite(parent=innerTransform, pos=(0, 0, 128, 128), texturePath='res:/ui/sprite/carbontest/innercircles.dds', blurFactor=0.1, filter=True)
        curve, binding = self.CreatePerlinCurve(innerTransform, 'value', 'rotation', curveSet, scale=10.025)
        outerTransform = uicls.Transform(parent=par, idx=0, left=8, top=8)
        outerTransform.rotationCenter = (64, 64)
        outer = uicls.Sprite(parent=outerTransform, pos=(0, 0, 128, 128), texturePath='res:/ui/sprite/carbontest/outercircles.dds', blurFactor=0.1, filter=True)
        curve, binding = self.CreatePerlinCurve(outerTransform, 'value', 'rotation', curveSet, scale=10.00125)
        uicore.desktop.GetRenderObject().curveSets.append(curveSet)
        curveSet.Play()

    def CreateColorCurve(self, destObject, curveSet, length = 1.0, startValue = (1, 1, 1, 1), endValue = (1, 1, 1, 0), cycle = False):
        curve = trinity.Tr2ColorCurve()
        curve.length = length
        curve.cycle = cycle
        curve.startValue = startValue
        curve.endValue = endValue
        curve.interpolation = 1
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, 'currentValue', destObject, 'color', curveSet)
        return (curve, binding)

    def CreateScalarCurve(self, destObject, sourceAttr, destAttr, curveSet, length = 1.0, startValue = 0.0, endValue = 0.0, cycle = False, startTangent = 0.0, endTangent = 0.0):
        curve = trinity.Tr2ScalarCurve()
        curve.length = length
        curve.cycle = cycle
        curve.startValue = startValue
        curve.endValue = endValue
        curve.interpolation = 2
        curve.startTangent = startTangent
        curve.endTangent = endTangent
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)

    def CreatePerlinCurve(self, destObject, sourceAttr, destAttr, curveSet, scale = 1000.0, offset = 0.0, N = 2, speed = 1.0, alpha = 1000.0, beta = 5000.0):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.N = N
        curve.speed = speed
        curve.alpha = alpha
        curve.beta = beta
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)

    def CreateSineCurve(self, destObject, sourceAttr, destAttr, curveSet, scale = 1.0, offset = 0.0, speed = 1.0):
        curve = trinity.TriSineCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)

    def AddBinding(self, sourceObject, sourceAttribute, destObject, destAttribute, curveSet):
        binding = trinity.TriValueBinding()
        binding.sourceObject = sourceObject
        binding.sourceAttribute = sourceAttribute
        binding.destinationObject = destObject.GetRenderObject()
        binding.destinationAttribute = destAttribute
        curveSet.bindings.append(binding)
        return binding


class Button(uicls.Container):
    __guid__ = 'uicls.MenuDemoButton'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.align = uiconst.CENTERTOP
        self.height = 32
        self.width = 300
        self.state = uiconst.UI_NORMAL
        self.depthMin = 0
        self.depthMax = 0
        self.animation = None
        self.sr.label = uicls.Label(text='SOME BUTTON', align=uiconst.CENTER, parent=self, fontsize=18, shadow=None)
        uicls.Frame(parent=self, name='background', state=uiconst.UI_DISABLED, frameConst=uiconst.FRAME_BORDER2_CORNER6, color=(1.0, 1.0, 1.0, 0.5), depth=1)
        uicls.Frame(parent=self, name='background', state=uiconst.UI_DISABLED, frameConst=uiconst.FRAME_FILLED_CORNER6, color=(1.0, 1.0, 1.0, 0.25), depth=1)

    def OnMouseEnter(self, *args):
        if self.animation:
            trinity.device.curveSets.fremove(self.animation)
        self.depthMin = -0.25
        self.depthMax = -0.25
        self.sr.label.glowFactor = 1.0
        self.sr.label.glowColor = (0.25, 0.25, 0.25, 1.0)
        self.sr.label.shadowOffset = (1, 1)
        self.sr.label.shadowColor = (0, 0, 0, 0.5)
        self.PlayHighlightAnimation()

    def OnMouseExit(self, *args):
        if self.animation:
            trinity.device.curveSets.fremove(self.animation)
        self.depthMin = 0.0
        self.depthMax = 0.0
        self.sr.label.glowFactor = 0.0
        self.sr.label.glowExpand = 0.0
        self.sr.label.shadowOffset = (0, 0)
        self.PlayUnhighlightAnimation()

    def PlayHighlightAnimation(self):
        cs = trinity.TriCurveSet()
        expandCurve = trinity.Tr2ScalarCurve()
        expandCurve.interpolation = trinity.TR2CURVE_HERMITE
        expandCurve.length = 0.3
        expandCurve.startValue = 0.0
        expandCurve.endValue = 100.0
        cs.curves.append(expandCurve)
        trinity.CreateBinding(cs, expandCurve, 'currentValue', self.sr.label.GetRenderObject(), 'glowExpand')
        alphaCurve = trinity.Tr2ScalarCurve()
        alphaCurve.interpolation = trinity.TR2CURVE_HERMITE
        alphaCurve.length = 0.3
        alphaCurve.startValue = 1.0
        alphaCurve.endValue = 0.0
        cs.curves.append(alphaCurve)
        trinity.CreateBinding(cs, alphaCurve, 'currentValue', self.sr.label.GetRenderObject(), 'glowColor.a')
        depthCurve = trinity.Tr2ScalarCurve()
        depthCurve.interpolation = trinity.TR2CURVE_HERMITE
        depthCurve.length = 0.3
        depthCurve.startValue = 0
        depthCurve.endValue = -0.25
        cs.curves.append(depthCurve)
        trinity.CreateBinding(cs, depthCurve, 'currentValue', self.GetRenderObject(), 'depthMin')
        trinity.CreateBinding(cs, depthCurve, 'currentValue', self.GetRenderObject(), 'depthMax')
        cs.Play()
        cs.StopAfter(cs.GetMaxCurveDuration())
        trinity.device.curveSets.append(cs)
        self.animation = cs

    def PlayUnhighlightAnimation(self):
        cs = trinity.TriCurveSet()
        depthCurve = trinity.Tr2ScalarCurve()
        depthCurve.interpolation = trinity.TR2CURVE_HERMITE
        depthCurve.length = 0.3
        depthCurve.startValue = -0.25
        depthCurve.endValue = 0
        cs.curves.append(depthCurve)
        trinity.CreateBinding(cs, depthCurve, 'currentValue', self.GetRenderObject(), 'depthMin')
        trinity.CreateBinding(cs, depthCurve, 'currentValue', self.GetRenderObject(), 'depthMax')
        cs.Play()
        cs.StopAfter(cs.GetMaxCurveDuration())
        trinity.device.curveSets.append(cs)
        self.animation = cs