#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/extras/lightfxsvc.py
import blue
import service
import uthread
import blue.heapq as heapq
import lightfxConstants
import math
import extensions
LFX_GUID_LOWCAP = 'lightfx.LowCapacitator'
LFX_GUID_JUMPREADY = 'lightfx.JumpEnginesReady'
LFX_GUID_AUTOPILOTWAYPOINT = 'lightfx.AutoPilotWaypointReached'
LFX_GUID_WARPSCRAMBLE = 'lightfx.WarpScrambled'
LFX_GUID_CARGOFULL = 'lightfx.CargoFull'

class LedEffect:
    __guid__ = 'lightfx.LedEffect'

    def __init__(self):
        self.locationMask = lightfxConstants.LFX_ALL
        self.brightness = lightfxConstants.LFX_FULL_BRIGHTNESS
        self.color = lightfxConstants.LFX_BLACK
        self.duration = 0

    def SetManager(self, ledFx):
        self.ledFx = ledFx

    def Update(self, deltaT):
        self.duration = self.duration - deltaT

    def Expired(self):
        return self.duration < 0

    def Render(self):
        colorMask = int(self.brightness) | int(self.color)
        self.ledFx.SetLight(self.locationMask, colorMask)


class BreathingLedEffect(LedEffect):
    __guid__ = 'lightfx.BreathingLedEffect'

    def __init__(self):
        LedEffect.__init__(self)
        self.intensity = 0
        self.step = 1
        self.breathins = 5

    def Update(self, deltaT):
        LedEffect.Update(self, deltaT)
        if self.intensity == 0:
            self.step = 1
        elif self.intensity == 8:
            self.breathins = self.breathins - 1
            self.step = -1
        self.intensity += self.step
        self.brightness = lightfxConstants.LFX_FULL_BRIGHTNESS * 0.125 * self.intensity

    def Expired(self):
        return self.breathins == 0


class BlinkingLedEffect(LedEffect):
    __guid__ = 'lightfx.BlinkingLedEffect'

    def __init__(self):
        LedEffect.__init__(self)
        self.minIntensity = lightfxConstants.LFX_MIN_BRIGHTNESS
        self.maxIntensity = lightfxConstants.LFX_FULL_BRIGHTNESS
        self.brightness = self.minIntensity
        self.repetitions = 10
        self.timeElapsed = 0
        self.needsToBeRendered = True
        self.blinkDelay = 500

    def Update(self, deltaT):
        self.timeElapsed += deltaT
        if self.timeElapsed >= self.blinkDelay:
            self.needsToBeRendered = True
            self.timeElapsed = 0
            LedEffect.Update(self, deltaT)
            if self.brightness == self.minIntensity:
                self.brightness = self.maxIntensity
            elif self.brightness == self.maxIntensity:
                self.brightness = self.minIntensity
                self.repetitions = self.repetitions - 1

    def Render(self):
        if self.needsToBeRendered == True:
            LedEffect.Render(self)
            self.needsToBeRendered = False

    def Expired(self):
        return self.repetitions == 0


class FadeOutEffect(LedEffect):
    __guid__ = 'lightfx.FadeOut'

    def __init__(self):
        LedEffect.__init__(self)
        self.stepping = 0

    def Update(self, deltaT):
        self.brightness = int(255 * math.cos(math.radians(self.stepping))) << 24
        self.stepping += 1

    def Expired(self):
        return self.stepping == 90


class BackgroundLightEffect(LedEffect):
    __guid__ = 'lightfx.BackgroundLightEffect'

    def __init__(self):
        self.locationMask = lightfxConstants.LFX_ALL
        self.brightness = lightfxConstants.LFX_HALF_BRIGHTNESS
        self.color = lightfxConstants.LFX_BLUE
        self.duration = 1

    def Update(self, deltaT):
        pass


class LightFx(service.Service):
    __guid__ = 'svc.lightFx'
    __notifyevents__ = ['OnDamageStateChange',
     'OnCapacitorChange',
     'OnAutoPilotOff',
     'OnEveMessage']
    __startupdependencies__ = ['settings']

    def Run(self, *args):
        if not hasattr(self, 'forceDisabled'):
            if '/nolightfx' in blue.pyos.GetArg():
                self.LogInfo('Not initializing LightFX because /nolightfx was specified.')
                self.forceDisabled = True
        if getattr(self, 'forceDisabled', False):
            sm.UnregisterNotify(self)
            return
        self.messages = {}
        self.delay = 250
        self.step = 1
        self.intensity = 0
        self.effects = []
        self.damageAlertTriggered = [False, False, False]
        self.ledFx = extensions.GetLedFx()
        self.ledFx.Init()
        uthread.new(self.RunLightFxLoop)

    def HasEffect(self, guid):
        for fx in self.effects:
            if fx[1].__guid__ == guid:
                return True

        return False

    def AddEffect(self, effect, priority = lightfxConstants.LFX_NORMAL_PRIORITY):
        if not isinstance(effect, LedEffect):
            raise TypeError('effect must be a LedEffect or a subclass thereof.')
        if not self.Enabled() or not self.IsLightFxSupported():
            return
        effect.SetManager(self.ledFx)
        heapq.heappush(self.effects, (priority, effect))
        self.LogInfo('Adding effect. Total:', len(self.effects))

    def RunLightFxLoop(self):
        if not self.Enabled():
            self.LogInfo('User disabled LightFx support, not initializing service.')
            return
        if not self.IsLightFxSupported():
            self.LogInfo('No DELL LightFx support available')
            return
        self.AddEffect(BackgroundLightEffect(), priority=lightfxConstants.LFX_LOWEST_PRIORITY)
        while self.state == service.SERVICE_RUNNING:
            if session.shipid:
                item = sm.GetService('godma').GetItem(session.shipid)
                if item.warpScrambleStatus > 0 and not self.HasEffect(LFX_GUID_WARPSCRAMBLE):
                    ledFx = BlinkingLedEffect()
                    ledFx.__guid__ = LFX_GUID_WARPSCRAMBLE
                    ledFx.blinkDelay = self.delay
                    ledFx.color = lightfxConstants.LFX_CYAN
                    self.AddEffect(ledFx)
            if len(self.effects) > 0:
                dirty = False
                for effect in self.effects:
                    effect[1].Update(self.delay)
                    if effect[1].Expired():
                        dirty = True
                        break

                self.effects[0][1].Render()
                if dirty:
                    self.LogInfo('Removing expired effects')
                    self.effects = [ (each[0], each[1]) for each in self.effects if each[1].Expired() == False ]
                    heapq.heapify(self.effects)
            blue.pyos.synchro.SleepWallclock(self.delay)

    def IsLightFxSupported(self):
        if getattr(self, 'forceDisabled', False):
            return False
        else:
            return self.ledFx.Available()

    def Enabled(self):
        return settings.user.ui.Get('LightFxEnabled', 1)

    def SetEnabled(self, enabled):
        settings.user.ui.Set('LightFxEnabled', enabled)

    def OnCapacitorChange(self, currentCharge, maxCharge, percentageLoaded):
        self.LogInfo('OnCapacitatorChange currentCharge=', currentCharge, 'maxCharge=', maxCharge, 'percentageLoaded=', percentageLoaded)
        if percentageLoaded < 0.3 and not self.HasEffect(LFX_GUID_LOWCAP) and not getattr(self, 'lowCapTriggered', False):
            ledFx = FadeOutEffect()
            ledFx.__guid__ = LFX_GUID_LOWCAP
            ledFx.color = lightfxConstants.LFX_ORANGE
            self.lowCapTriggered = True
            self.AddEffect(ledFx)
        if percentageLoaded > 0.3 and getattr(self, 'lowCapTriggered', False):
            self.lowCapTriggered = False
        if percentageLoaded < 0.7:
            self.enableJumpDriveNotification = True
        if percentageLoaded > 0.7 and getattr(self, 'enableJumpDriveNotification', False) and not self.HasEffect(LFX_GUID_JUMPREADY):
            ship = sm.GetService('godma').GetItem(session.shipid)
            if getattr(ship, 'canJump', False):
                self.enableJumpDriveNotification = False
                ledFx = BlinkingLedEffect()
                ledFx.__guid__ = LFX_GUID_JUMPREADY
                ledFx.color = lightfxConstants.LFX_GREEN
                self.AddEffect(ledFx)

    def OnEveMessage(self, msgkey):
        if msgkey == 'MiningDronesDeactivatedCargoHoldNowFull':
            self.CargoEffect()

    def CargoEffect(self):
        ship = sm.GetService('godma').GetItem(session.shipid)
        if not ship:
            return
        cargo = ship.GetCapacity()
        if 0 == cargo.capacity:
            return
        if not self.HasEffect(LFX_GUID_CARGOFULL):
            ledFx = FadeOutEffect()
            ledFx.__guid__ = LFX_GUID_CARGOFULL
            ledFx.color = 12079911
            self.AddEffect(ledFx)

    def OnAutoPilotOff(self):
        if not self.HasEffect(LFX_GUID_AUTOPILOTWAYPOINT):
            ledFx = BlinkingLedEffect()
            ledFx.__guid__ = LFX_GUID_AUTOPILOTWAYPOINT
            ledFx.color = lightfxConstants.LFX_BLUE
            ledFx.maxBrightness = int(lightfxConstants.LFX_FULL_BRIGHTNESS / 2)
            ledFx.repetitions = 2
            self.AddEffect(ledFx)

    def OnDamageStateChange(self, shipID, damageState):
        if session.shipid != shipID:
            return
        for i in xrange(0, 3):
            ledFx = None
            enabled = settings.user.notifications.Get(const.soundNotificationVars[i][0], 1)
            if not enabled:
                continue
            shouldNotify = damageState[i] <= settings.user.notifications.Get(const.soundNotificationVars[i][1], const.soundNotificationVars[i][2])
            alreadyNotified = self.damageAlertTriggered[i]
            if shouldNotify and not alreadyNotified:
                self.damageAlertTriggered[i] = True
                ledFx = BlinkingLedEffect()
                colors = (lightfxConstants.LFX_YELLOW, lightfxConstants.LFX_ORANGE, lightfxConstants.LFX_RED)
                ledFx.color = colors[i]
                ledFx.repetitions = 4
            if alreadyNotified:
                self.damageAlertTriggered[i] = shouldNotify
                continue
            if ledFx is not None:
                self.AddEffect(ledFx)


exports = {'lightfxsvc.LedEffect': LedEffect,
 'lightfxsvc.BreathingLedEffect': BreathingLedEffect,
 'lightfxsvc.BlinkingLedEffect': BlinkingLedEffect}