import util
import planetCommon
import uicls
import planet
import blue

class ExtractorContainer(planet.ui.ObsoletePinContainer):
    __guid__ = 'planet.ui.ExtractorContainer'
    default_name = 'ExtractorContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)



    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(95, 'infoCont', padding=(p,
         p,
         p,
         p))
        self.currDepositTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_EXTRACTING, top=0)
        self.depositsLeftTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_TOTALAMOUNTLEFT, top=40)
        self.timeToDeplTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_TIMETODEPLETION, top=70)
        left = self.infoContRightColAt
        self.currCycleGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=mls.UI_PI_CURRENTCYCLE, cyclic=True)
        self.currCycleGauge.left = left
        self.amountPerCycleTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_OUTPUTPERCYCLE, top=40, left=left)
        self.amountPerHourTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_OUTPUTPERHOUR, top=70, left=left)
        return infoCont



    def _UpdateInfoCont(self):
        if self.pin.depositType is not None and self.pin.depositQtyPerCycle > 0:
            timeToDepletion = self.pin.GetTimeToDepletion()
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(mls.UI_PI_TIMETODEPLETION)
            if totalTimeLeft < DAY:
                totalTimeLeft = util.FmtTime(float(totalTimeLeft))
            else:
                totalTimeLeft = util.FmtTimeInterval(long(totalTimeLeft), breakAt='hour')
            deposName = cfg.invtypes.Get(self.pin.depositType).name
            if self.pin.activityState < planet.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
            else:
                currCycle = blue.os.GetTime() - self.pin.lastRunTime
            currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            cycleTime = self.pin.GetCycleTime()
        else:
            currCycle = 0
            totalTimeLeft = util.FmtTime(0)
            currCycleProportion = 0.0
            cycleTime = 0
            deposName = '<color=red>%s<color>' % mls.UI_GENERIC_NOTHING
        self.currDepositTxt.SetIcon(self.pin.depositType)
        self.currDepositTxt.SetSubtext(deposName)
        self.depositsLeftTxt.SetSubtext('%s %s' % (self.pin.depositQtyRemaining, mls.UI_GENERIC_UNITS))
        if self.pin.IsInEditMode():
            self.currCycleGauge.SetSubText(mls.UI_PI_INACTIVE_REASON % {'reason': mls.UI_PI_GENERIC_EDITMODE})
            self.timeToDeplTxt.SetSubtext(mls.UI_PI_INACTIVE_REASON % {'reason': mls.UI_PI_GENERIC_EDITMODE})
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText('%s / %s' % (util.FmtTime(currCycle), util.FmtTime(cycleTime)))
        self.amountPerCycleTxt.SetSubtext('%s %s' % (self.pin.depositQtyPerCycle, mls.UI_GENERIC_UNITS))
        attr = cfg.dgmattribs.GetIfExists(const.attributeLogisticalCapacity)
        self.amountPerHourTxt.SetSubtext(sm.GetService('info').GetFormatAndValue(attr, self.pin.GetOutputVolumePerHour()))




