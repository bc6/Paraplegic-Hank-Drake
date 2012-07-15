#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/pinContainers/ExtractorContainer.py
import util
import planetCommon
import uicls
import planet
import blue
import localization

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
        self.currDepositTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/Extracting'), top=0)
        self.depositsLeftTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/TotalAmountLeft'), top=40)
        self.timeToDeplTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/TimeToDepletion'), top=70)
        left = self.infoContRightColAt
        self.currCycleGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), cyclic=True)
        self.currCycleGauge.left = left
        self.amountPerCycleTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/OutputPerCycle'), top=40, left=left)
        self.amountPerHourTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), top=70, left=left)
        return infoCont

    def _UpdateInfoCont(self):
        if self.pin.depositType is not None and self.pin.depositQtyPerCycle > 0:
            timeToDepletion = self.pin.GetTimeToDepletion()
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(localization.GetByLabel('UI/PI/Common/TimeToDepletion'))
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
                currCycle = blue.os.GetWallclockTime() - self.pin.lastRunTime
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
                cycleTime = self.pin.GetCycleTime()
        else:
            currCycle = 0
            totalTimeLeft = util.FmtTime(0)
            currCycleProportion = 0.0
            cycleTime = 0
            deposName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
        self.currDepositTxt.SetIcon(self.pin.depositType)
        self.currDepositTxt.SetSubtext(deposName)
        self.depositsLeftTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.depositQtyRemaining))
        if self.pin.IsInEditMode():
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            self.timeToDeplTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=long(currCycle), totalTime=long(cycleTime)))
        self.amountPerCycleTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.depositQtyPerCycle))
        attr = cfg.dgmattribs.GetIfExists(const.attributeLogisticalCapacity)
        self.amountPerHourTxt.SetSubtext(sm.GetService('info').GetFormatAndValue(attr, self.pin.GetOutputVolumePerHour()))