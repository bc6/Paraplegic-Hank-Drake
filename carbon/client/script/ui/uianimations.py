import trinity
import uicls
import math
import util
import uiconst
import random
import blue
from uiconst import ANIM_REPEAT, ANIM_SMOOTH, ANIM_LINEAR, ANIM_OVERSHOT, ANIM_WAVE, ANIM_RANDOM

class UIAnimations(object):
    __guid__ = 'uicls.UIAnimations'

    def __init__(self):
        self.curves = uicls.UIAnimationCurves()



    def _CreateCurveSet(self):
        curveSet = trinity.TriCurveSet()
        trinity.device.curveSets.append(curveSet)
        return curveSet



    def _Play(self, curve, obj, attrName, loops = 1, callback = None, sleep = False, curveSet = None):
        curve.cycle = loops is ANIM_REPEAT or loops > 1
        if not curveSet:
            curveSet = self._CreateCurveSet()
        curveSet.curves.append(curve)
        if isinstance(obj, uicls.Base):
            obj.AttachAnimationCurveSet(curveSet, attrName)
        else:
            raise ValueError("Can't animate '%s' attribute of %s. Class must inherit from uicls.Base" % (attrName, obj))
        trinity.CreatePythonBinding(curveSet, curve, 'currentValue', obj, attrName)
        curveSet.Play()
        if loops is ANIM_REPEAT:
            return curveSet
        duration = loops * curveSet.GetMaxCurveDuration()
        if callback:
            curveSet.StopAfterWithCallback(duration, callback, ())
        else:
            curveSet.StopAfter(duration)
        if sleep:
            blue.pyos.synchro.Sleep(duration * 1000)
        return curveSet



    def MorphScalar(self, obj, attrName, startVal = 0.0, endVal = 1.0, duration = 0.75, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(startVal, endVal, duration, curveType)
        return self._Play(curve, obj, attrName, loops, callback, sleep)



    def MorphVector2(self, obj, attrName, startVal = (0.0, 0.0), endVal = (1.0, 1.0), duration = 0.75, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetVector2(startVal, endVal, duration, curveType)
        return self._Play(curve, obj, attrName, loops, callback, sleep)



    def FadeTo(self, obj, startVal = 0.0, endVal = 1.0, duration = 0.75, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        if hasattr(obj, 'opacity'):
            curve = self.curves.GetScalar(startVal, endVal, duration, curveType)
            attrName = 'opacity'
        else:
            c = obj.color
            curve = self.curves.GetColor((c.r,
             c.g,
             c.b,
             startVal), (c.r,
             c.g,
             c.b,
             endVal), duration, curveType)
            attrName = 'color'
        return self._Play(curve, obj, attrName, loops, callback, sleep)



    def FadeIn(self, obj, endVal = 1.0, duration = 0.75, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.FadeTo(obj, 0.0, endVal, duration, loops, curveType, callback, sleep)



    def FadeOut(self, obj, duration = 0.75, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        if hasattr(obj, 'opacity'):
            startVal = obj.opacity
        else:
            startVal = obj.color.a
        return self.FadeTo(obj, startVal, 0.0, duration, loops, curveType, callback, sleep)



    def BlinkIn(self, obj, startVal = 0.0, endVal = 1.0, duration = 0.1, loops = 3, curveType = ANIM_LINEAR, callback = None, sleep = False):
        return self.FadeTo(obj, startVal, endVal, duration, loops, curveType, callback, sleep)



    def BlinkOut(self, obj, startVal = 1.0, endVal = 0.0, duration = 0.1, loops = 3, curveType = ANIM_LINEAR, callback = None, sleep = False):
        return self.FadeTo(obj, startVal, endVal, duration, loops, curveType, callback, sleep)



    def MoveTo(self, obj, startPos = None, endPos = None, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        if not startPos:
            startPos = (obj.displayX, obj.displayY)
        if not endPos:
            endPos = (obj.displayX, obj.displayY)
        curve = self.curves.GetScalar(startPos[0], endPos[0], duration, curveType)
        curveSet = self._Play(curve, obj, 'left', loops, callback)
        curve = self.curves.GetScalar(startPos[1], endPos[1], duration, curveType)
        return self._Play(curve, obj, 'top', loops, callback, sleep, curveSet)



    def MoveInFromLeft(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.left - amount, obj.left, duration, curveType)
        return self._Play(curve, obj, 'left', loops, callback, sleep)



    def MoveInFromRight(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.left + amount, obj.left, duration, curveType)
        return self._Play(curve, obj, 'left', loops, callback, sleep)



    def MoveInFromTop(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.top - amount, obj.top, duration, curveType)
        return self._Play(curve, obj, 'top', loops, callback, sleep)



    def MoveInFromBottom(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.top + amount, obj.top, duration, curveType)
        return self._Play(curve, obj, 'top', loops, callback, sleep)



    def MoveOutLeft(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.left, obj.left - amount, duration, curveType)
        return self._Play(curve, obj, 'left', loops, callback, sleep)



    def MoveOutRight(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.left, obj.left + amount, duration, curveType)
        return self._Play(curve, obj, 'left', loops, callback, sleep)



    def MoveOutTop(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.top, obj.top - amount, duration, curveType)
        return self._Play(curve, obj, 'top', loops, callback, sleep)



    def MoveOutBottom(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.top, obj.top + amount, duration, curveType)
        return self._Play(curve, obj, 'top', loops, callback, sleep)



    def Tr2DScaleTo(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetVector2(startScale, endScale, duration, curveType)
        return self._Play(curve, obj, 'scale', loops, callback, sleep)



    def Tr2DScaleIn(self, obj, scaleCenter = (0.0, 0.0), duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        obj.scaleCenter = scaleCenter
        return self.Tr2DScaleTo(obj, (0.0, 0.0), (1.0, 1.0), duration, loops, curveType, callback, sleep)



    def Tr2DScaleOut(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.Tr2DScaleTo(obj, obj.scale, (0.0, 0.0), duration, loops, callback, sleep)



    def Tr2DFlipIn(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        self.Tr2DScaleTo(obj, (1.0, 0.0), (1.0, 1.0), duration, loops, curveType, callback)
        curve = self.curves.GetScalar(0.0, 1.0, duration, curveType)
        return self._Play(curve, obj, 'scalingRotation', loops, callback, sleep)



    def Tr2DFlipOut(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        self.Tr2DScaleTo(obj, (1.0, 1.0), (1.0, 0.0), duration, loops, curveType, callback)
        curve = self.curves.GetScalar(1.0, 0.0, duration, curveType)
        return self._Play(curve, obj, 'scalingRotation', loops, callback, sleep)



    def Tr2DSquashOut(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        obj.scalingRotation = 0.5
        obj.scalingCenter = (0.5, 0.5)
        curve = self.curves.GetVector2((1.0, 1.0), (0.0, 1.0), duration, curveType=uiconst.ANIM_SMOOTH)
        return self._Play(curve, obj, 'scale', loops, callback, sleep)



    def Tr2DSquashIn(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        obj.scalingRotation = 0.5
        obj.scalingCenter = (0.5, 0.5)
        curve = self.curves.GetVector2((0.0, 1.0), (1.0, 1.0), duration, curveType)
        return self._Play(curve, obj, 'scale', loops, callback, sleep)



    def Tr2DRotateTo(self, obj, startAngle = 0.0, endAngle = 2 * math.pi, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(startAngle, endAngle, duration, curveType)
        return self._Play(curve, obj, 'rotation', loops, callback, sleep)



    def SpBlurIn(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.blurFactor, 1.0, duration, curveType)
        return self._Play(curve, obj, 'blurFactor', loops, callback, sleep)



    def SpBlurOut(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetScalar(obj.blurFactor, 0.0, duration, curveType)
        return self._Play(curve, obj, 'blurFactor', loops, callback, sleep)



    def SpColorMorphTo(self, obj, startColor = util.Color.WHITE, endColor = util.Color.BLUE, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        curve = self.curves.GetColor(startColor, endColor, duration, curveType)
        return self._Play(curve, obj, 'color', loops, callback, sleep)



    def SpColorMorphToBlack(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.SpColorMorphTo(obj, obj.GetRGBA(), util.Color.BLACK, duration, loops, curveType, callback, sleep)



    def SpColorMorphToWhite(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.SpColorMorphTo(obj, obj.GetRGBA(), util.Color.WHITE, duration, loops, curveType, callback, sleep)



    def SpGlowFadeTo(self, obj, startColor = (0.8, 0.8, 1.0, 0.3), endColor = (0, 0, 0, 0), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        obj.glowFactor = glowFactor
        obj.glowExpand = glowExpand
        curve = self.curves.GetColor(startColor, endColor, duration, curveType)
        return self._Play(curve, obj, 'glowColor', loops, callback, sleep)



    def SpGlowFadeIn(self, obj, glowColor = (0.8, 0.8, 1.0, 0.3), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.SpGlowFadeTo(obj, (0, 0, 0, 0), glowColor, glowFactor, glowExpand, duration, loops, curveType, callback, sleep)



    def SpGlowFadeOut(self, obj, glowColor = (0.8, 0.8, 1.0, 0.3), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.SpGlowFadeTo(obj, glowColor, (0, 0, 0, 0), glowFactor, glowExpand, duration, loops, curveType, callback, sleep)



    def SpShadowMoveTo(self, obj, startPos = (0.0, 0.0), endPos = (10.0, 10.0), color = None, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        obj.shadowColor = color or (0.0, 0.0, 0.0, 0.5)
        curve = self.curves.GetVector2(startPos, endPos, duration, curveType)
        return self._Play(curve, obj, 'shadowOffset', loops, callback, sleep)



    def SpShadowAppear(self, obj, offset = (10.0, 10.0), color = None, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        color = color or (0.0, 0.0, 0.0, 0.5)
        return self.SpShadowMoveTo(obj, (0.0, 0.0), offset, color, duration, loops, curveType, callback, sleep)



    def SpShadowDisappear(self, obj, duration = 0.5, loops = 1, curveType = ANIM_SMOOTH, callback = None, sleep = False):
        return self.SpShadowMoveTo(obj, obj.shadowOffset, (0.0, 0.0), None, duration, loops, curveType, callback, sleep)



    def SpSecondaryTextureDrift(self, obj, amount = 100.0, scale = 20.0, alpha = 10.0, srcSize = 100.0, duration = 100.0, loops = ANIM_REPEAT, callback = None, sleep = False, **kw):
        textureObj = obj.renderObject.textureSecondary
        textureObj.srcWidth = srcSize
        textureObj.srcHeight = srcSize

        def GetCurve():
            curve = trinity.Tr2ScalarExprCurve()
            curve.expr = '%s * perlin(value + %s, %s, 4.0, 4)' % (scale, random.randint(0, 100), alpha)
            curve.length = duration
            curve.endValue = amount
            return curve


        curveSet = self._Play(GetCurve(), textureObj, 'srcX', loops, callback)
        obj.AttachAnimationCurveSet(curveSet, 'srcX')
        return self._Play(GetCurve(), textureObj, 'srcY', loops, callback, sleep, curveSet)



    def PolyRippleColor(self, obj, duration = 0.25, rippleDuration = 0.15, lowColor = (0.5, 0.5, 0.5, 1), highColor = (1, 1, 1, 1), backwards = False, close = False, callback = None, sleep = False, **kw):
        curveSet = self._CreateCurveSet()

        def CreateRippleCurve(offset):
            curve = trinity.Tr2ColorCurve()
            curve.AddKey(0.0, lowColor)
            if offset > 0.0:
                curve.AddKey(offset, lowColor)
            curve.AddKey(offset + 0.5 * rippleDuration, highColor)
            curve.AddKey(offset + rippleDuration, lowColor)
            if offset + rippleDuration < duration:
                curve.AddKey(duration, lowColor)
            return curve


        ro = obj.GetRenderObject()
        vertCount = len(ro.vertices)
        edgeCount = vertCount / 2
        baseIx = 0
        offset = 0
        step = duration / float(edgeCount)
        if backwards:
            offset = duration - step
            step = -step
        for i in xrange(edgeCount):
            curve = CreateRippleCurve(offset)
            curveSet.curves.append(curve)
            trinity.CreateBinding(curveSet, curve, 'currentValue', ro.vertices[baseIx], 'color')
            trinity.CreateBinding(curveSet, curve, 'currentValue', ro.vertices[(baseIx + 1)], 'color')
            ro.vertices[baseIx].color = lowColor
            ro.vertices[(baseIx + 1)].color = lowColor
            baseIx += 2
            offset += step

        curveSet.Play()
        if callback:
            curveSet.StopAfterWithCallback(curveSet.GetMaxCurveDuration(), callback, obj)
        else:
            curveSet.StopAfter(curveSet.GetMaxCurveDuration())



    def PolyRippleExpand(self, obj, duration = 0.25, rippleDuration = 0.15, expand = 5, backwards = False, callback = False, sleep = False, **kw):
        curveSet = self._CreateCurveSet()

        def CreateRippleCurve(offset):
            curve = trinity.Tr2ScalarCurve()
            curve.interpolation = trinity.TR2CURVE_HERMITE
            curve.AddKey(0.0, 0.0)
            if offset > 0.0:
                curve.AddKey(offset, 0.0)
            curve.AddKey(offset + 0.5 * rippleDuration, expand)
            curve.AddKey(offset + rippleDuration, 0.0)
            if offset + rippleDuration < duration:
                curve.AddKey(duration, 0.0)
            return curve


        ro = obj.GetRenderObject()
        vertCount = len(ro.vertices)
        edgeCount = vertCount / 2
        baseIx = 0
        offset = 0
        step = duration / float(edgeCount)
        if backwards:
            offset = duration - step
            step = -step
        for i in xrange(edgeCount):
            curve = CreateRippleCurve(offset)
            curveSet.curves.append(curve)
            vertex = ro.vertices[baseIx]
            binding = trinity.CreateBinding(curveSet, curve, 'currentValue', vertex, 'position.y')
            binding.offset = (vertex.position[1],
             0,
             0,
             0)
            binding.scale = -1
            vertex = ro.vertices[(baseIx + 1)]
            binding = trinity.CreateBinding(curveSet, curve, 'currentValue', vertex, 'position.y')
            binding.offset = (vertex.position[1],
             0,
             0,
             0)
            baseIx += 2
            offset += step

        curveSet.Play()
        if callback:
            curveSet.StopAfterWithCallback(curveSet.GetMaxCurveDuration(), callback, obj)
        else:
            curveSet.StopAfter(curveSet.GetMaxCurveDuration())




class Curves(object):
    __guid__ = 'uicls.UIAnimationCurves'

    def GetScalar(self, startValue, endValue, duration, curveType = ANIM_SMOOTH):
        if curveType is ANIM_RANDOM:
            curve = trinity.Tr2ScalarExprCurve()
        else:
            curve = trinity.Tr2ScalarCurve()
            curve.startValue = startValue
            curve.endValue = endValue
            curve.length = duration
        if curveType not in (ANIM_LINEAR, ANIM_RANDOM):
            curve.interpolation = trinity.TR2CURVE_HERMITE
        if curveType is ANIM_OVERSHOT:
            keyTime = 0.6 * duration
            keyVal = endValue + 0.1 * (endValue - startValue)
            curve.AddKey(keyTime, keyVal)
        elif curveType is ANIM_WAVE:
            curve.AddKey(0.5 * duration, endValue)
            curve.endValue = startValue
        elif curveType is ANIM_RANDOM:
            curve.expr = 'input1 + input2 * perlin(value, %s, 3.0, 4)' % duration
            curve.input1 = startValue
            curve.input2 = endValue
            curve.startValue = curve.endValue = startValue + (endValue - startValue) / 2
            curve.AddKey(25, endValue)
            curve.length = 50.0
        return curve



    def GetVector2(self, startValue, endValue, duration, curveType = ANIM_SMOOTH):
        curve = trinity.Tr2Vector2Curve()
        curve.length = duration
        curve.startValue = startValue
        curve.endValue = endValue
        if curveType is not ANIM_LINEAR:
            curve.interpolation = trinity.TR2CURVE_HERMITE
        if curveType is ANIM_OVERSHOT:
            keyTime = 0.6 * duration
            keyValX = endValue[0] + 0.1 * (endValue[0] - startValue[0])
            keyValY = endValue[1] + 0.1 * (endValue[1] - startValue[1])
            curve.AddKey(keyTime, (keyValX, keyValY))
        elif curveType is ANIM_WAVE:
            curve.AddKey(0.5 * duration, endValue)
            curve.endValue = startValue
        return curve



    def GetColor(self, startValue, endValue, duration, curveType = ANIM_LINEAR):
        curve = trinity.Tr2ColorCurve()
        curve.length = duration
        curve.startValue = startValue
        curve.endValue = endValue
        return curve




