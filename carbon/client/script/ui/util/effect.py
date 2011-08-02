import uiutil
import uthread
import blue
import mathUtil
import log
import math

class UIEffects:
    __guid__ = 'uicls.UIEffects'

    def StopBlink(self, sprite):
        if not getattr(self, 'blink_running', False):
            return 
        if not hasattr(self, 'remPending'):
            self.remPending = []
        self.remPending.append(id(sprite))



    def BlinkSpriteA(self, sprite, a, time = 1000.0, maxCount = 10, passColor = 1, minA = 0.0):
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        key = id(sprite)
        self.blinksA[key] = (sprite,
         a,
         minA,
         time,
         maxCount,
         passColor)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread).context = 'UIObject::effect._BlinkThread'



    def BlinkSpriteRGB(self, sprite, r, g, b, time = 1000.0, maxCount = 10, passColor = 1):
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        key = id(sprite)
        self.blinksRGB[key] = (sprite,
         r,
         g,
         b,
         time,
         maxCount,
         passColor)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread).context = 'UIObject::effect._BlinkThread'



    def _BlinkThread(self):
        start = blue.os.GetTime()
        countsA = {}
        countsRGB = {}
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        try:
            while 1:
                if not self:
                    return 
                diff = blue.os.TimeDiffInMs(start)
                rem = []
                for (key, each,) in self.blinksA.iteritems():
                    (sprite, a, minA, time, maxCount, passColor,) = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.a = minA or a
                        continue
                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(a, minA, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(minA, a, ndt)
                    if key not in countsA:
                        countsA[key] = blue.os.GetTime()
                    if maxCount and blue.os.TimeDiffInMs(countsA[key]) / time > maxCount:
                        rem.append(key)
                        color.a = minA or a
                        if key in countsA:
                            del countsA[key]

                for each in rem:
                    if each in self.blinksA:
                        del self.blinksA[each]

                rem = []
                for (key, each,) in self.blinksRGB.iteritems():
                    (sprite, r, g, b, time, maxCount, passColor,) = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        continue
                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(r, 0.0, ndt)
                        color.g = mathUtil.Lerp(g, 0.0, ndt)
                        color.b = mathUtil.Lerp(b, 0.0, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(0.0, r, ndt)
                        color.g = mathUtil.Lerp(0.0, g, ndt)
                        color.b = mathUtil.Lerp(0.0, b, ndt)
                    if key not in countsRGB:
                        countsRGB[key] = blue.os.GetTime()
                    if maxCount and blue.os.TimeDiffInMs(countsRGB[key]) / time > maxCount:
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        if key in countsRGB:
                            del countsRGB[key]

                for each in rem:
                    if each in self.blinksRGB:
                        del self.blinksRGB[each]

                self.remPending = []
                if not len(self.blinksA) and not len(self.blinksRGB) or not self.blink_running:
                    self.blinksA = {}
                    self.blinksRGB = {}
                    self.blink_running = False
                    break
                blue.pyos.synchro.Yield()

        except Exception:
            self.blink_running = False
            log.LogException()



    def Fade(self, fr, to, object, time = 500.0):
        affectOpacity = hasattr(object, 'opacity')
        ndt = 0.0
        start = blue.os.GetTime(1)
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start) / time, 1.0)
            if affectOpacity:
                object.opacity = mathUtil.Lerp(fr, to, ndt)
            else:
                object.SetAlpha(mathUtil.Lerp(fr, to, ndt))
            blue.pyos.synchro.Yield()
            if not object or getattr(object, 'destroyed', False):
                return 




    def FadeRGB(self, fr, to, sprite, time = 500.0):
        ndt = 0.0
        start = blue.os.GetTime(1)
        while ndt != 1.0:
            ndt = min(float(blue.os.TimeDiffInMs(start)) / float(time), 1.0)
            sprite.SetRGB(mathUtil.Lerp(fr[0], to[0], ndt), mathUtil.Lerp(fr[1], to[1], ndt), mathUtil.Lerp(fr[2], to[2], ndt))
            blue.pyos.synchro.Yield()
            if not object or getattr(object, 'destroyed', False):
                return 




    def Rotate(self, uitransform, time = 1.0, fromRot = 360.0, toRot = 0.0):
        uthread.new(self._Rotate, uitransform, time, fromRot, toRot).context = 'UIObject::effect._Rotate'



    def _Rotate(self, uitransform, time, fromRot, toRot):
        time *= 1000
        i = 0
        (start, ndt,) = (blue.os.GetTime(), 0.0)
        while ndt != 1.0 and not uitransform.destroyed:
            ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            deg = mathUtil.Lerp(fromRot, toRot, ndt)
            rad = mathUtil.DegToRad(deg)
            uitransform.SetRotation(rad)
            blue.pyos.synchro.Yield()




    def CombineEffects(self, item, opacity = None, alpha = None, left = None, top = None, width = None, height = None, rgb = None, _11 = None, _12 = None, time = 250.0, closeWhenDone = False, abortFunction = None, callback = None, doneCallback = None):
        sOpacity = None
        if opacity is not None and hasattr(item, 'opacity'):
            sOpacity = item.opacity
        sAlpha = None
        if alpha is not None and hasattr(item, 'GetAlpha'):
            sAlpha = item.GetAlpha()
        s_11 = None
        if _11 is not None and hasattr(item, 'transform'):
            s_11 = item.transform._11
        s_12 = None
        if _12 is not None and hasattr(item, 'transform'):
            s_12 = item.transform._12
        sLeft = None
        if left is not None:
            sLeft = item.left
        sTop = None
        if top is not None:
            sTop = item.top
        sWidth = None
        if width is not None:
            sWidth = item.width
        sHeight = None
        if height is not None:
            sHeight = item.height
        sR = sG = sB = None
        if rgb is not None and hasattr(item, 'GetRGB'):
            (sR, sG, sB,) = item.GetRGB()
            (r, g, b,) = rgb
        (start, ndt,) = (blue.os.GetTime(), 0.0)
        while ndt != 1.0:
            if item.destroyed:
                return 
            try:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            except:
                log.LogWarn('CombineEffects::Failed getting time diff. Diff should not exceed %s but is %s' % (time, start - blue.os.GetTime(1)))
                ndt = 1.0
            if sOpacity is not None:
                item.opacity = mathUtil.Lerp(sOpacity, opacity, ndt)
            if sAlpha is not None:
                item.SetAlpha(mathUtil.Lerp(sAlpha, alpha, ndt))
            _r = None
            if sR is not None:
                _r = mathUtil.Lerp(sR, r, ndt)
            _g = None
            if sG is not None:
                _g = mathUtil.Lerp(sG, g, ndt)
            _b = None
            if sB is not None:
                _b = mathUtil.Lerp(sB, b, ndt)
            if _r is not None or _g is not None or _b is not None:
                item.SetRGB(_r, _g, _b)
            if sLeft is not None:
                item.left = int(mathUtil.Lerp(sLeft, left, ndt))
            if sTop is not None:
                item.top = int(mathUtil.Lerp(sTop, top, ndt))
            if sWidth is not None:
                item.width = int(mathUtil.Lerp(sWidth, width, ndt))
            if sHeight is not None:
                item.height = int(mathUtil.Lerp(sHeight, height, ndt))
            if s_11 is not None:
                item.transform._11 = mathUtil.Lerp(s_11, _11, ndt)
            if s_12 is not None:
                item.transform._12 = mathUtil.Lerp(s_12, _12, ndt)
            if callback:
                callback(item)
            blue.pyos.synchro.Yield()
            if abortFunction and abortFunction():
                if closeWhenDone and not item.destroyed:
                    item.Close()
                return 

        if doneCallback and not item.destroyed:
            doneCallback(item)
        if closeWhenDone and not item.destroyed:
            item.Close()



    def MorphUI(self, item, attrname, tval, time = 500.0, newthread = 1, ifWidthConstrain = 1, maxSteps = 100, float = 0, endState = None):
        cval = getattr(item, attrname, None)
        if cval is None:
            log.LogError('Attribute not found %s' % attrname)
            return 
        if cval == tval:
            return 
        if newthread:
            return uthread.new(self.MorphUI, item, attrname, tval, time, 0, ifWidthConstrain, maxSteps, float, endState=None)
        (start, ndt,) = (blue.os.GetTime(), 0.0)
        steps = 0
        while ndt != 1.0:
            if steps > maxSteps:
                log.LogWarn('MorphUI::Exceeded maxSteps')
                setattr(item, attrname, tval)
                if attrname == 'width' and ifWidthConstrain:
                    setattr(item, 'height', tval)
                break
            try:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            except:
                log.LogWarn('MorphUI::Failed getting time diff. Diff should not exceed %s but is %s' % (time, start - blue.os.GetTime(1)))
                ndt = 1.0
            if ndt < 0.0:
                log.LogWarn('MorphUI::Got fubar TimeDiffInMs, propably because of the timesync... ignoring', start, time)
                setattr(item, attrname, tval)
                if attrname == 'width' and ifWidthConstrain:
                    setattr(item, 'height', tval)
                break
            val = mathUtil.Lerp(cval, tval, ndt)
            if not float:
                val = int(val)
            setattr(item, attrname, val)
            if attrname == 'width' and ifWidthConstrain:
                setattr(item, 'height', val)
            blue.pyos.synchro.Yield()
            steps += 1

        if endState is not None:
            item.state = endState



    def Morph(self, func, time = 500.0, newthread = 1):
        if newthread:
            uthread.new(self.Morph, func, time, newthread=0).context = 'UIObject::effect.Morph'
            return 
        (start, ndt,) = (blue.os.GetTime(), 0.0)
        while ndt != 1.0:
            try:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            except:
                ndt = 1.0
            if ndt < 0.0:
                break
            val = mathUtil.Lerp(0.0, 1.0, ndt)
            func(val)
            blue.pyos.synchro.Yield()




    def MorphUIMassSpringDamper(self, item, attrname = None, newVal = 1.0, newthread = 1, float = 1, minVal = -10000000000.0, maxVal = 10000000000.0, dampRatio = 0.11, frequency = 20.0, initSpeed = 0.0, maxTime = 1.0, callback = None, initVal = None):
        if newthread:
            return uthread.new(self._MorphUIMassSpringDamper, item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal)
        self._MorphUIMassSpringDamper(item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal)



    def _MorphUIMassSpringDamper(self, item, attrname, newVal, newthread, float, minVal, maxVal, dampRatio, frequency, initSpeed, maxTime, callback, initVal = None):
        if initVal is None and attrname is not None:
            initVal = getattr(item, attrname)
        if initVal == newVal:
            initVal += 1e-05
        t0 = blue.os.GetTime()
        xn = newVal - initVal
        x0 = -xn
        w0 = frequency
        L = dampRatio
        if math.fabs(L) >= 1.0:
            L = 0.99
        wd = w0 * math.sqrt(1.0 - L ** 2)
        A = x0
        v0 = initSpeed
        B = (L * w0 * x0 + v0) / wd
        t = 0.0
        val = 0.0
        stopCount = 0
        while t < maxTime:
            t = blue.os.TimeDiffInMs(t0) / 1000.0
            C = -L * w0 * t
            val = math.exp(C) * (A * math.cos(wd * t) + B * math.sin(wd * t)) + xn
            val = max(minVal - initVal, min(val, maxVal - initVal))
            if math.fabs(val + initVal - newVal) / math.fabs(initVal - newVal) < 0.02:
                stopCount += 1
            if stopCount >= 5:
                break
            setVal = val + initVal
            if not float:
                setVal = int(setVal)
            if attrname and item:
                setattr(item, attrname, setVal)
            if callback:
                callback(item, setVal)
            blue.pyos.synchro.Yield()
            if item and item.destroyed:
                break

        newVal = max(minVal, min(newVal, maxVal))
        if not float:
            newVal = int(newVal)
        if attrname and item:
            setattr(item, attrname, newVal)
        if callback:
            if item and item.destroyed:
                return 
            callback(item, newVal)




