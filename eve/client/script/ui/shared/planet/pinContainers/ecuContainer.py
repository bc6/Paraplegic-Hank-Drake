import xtriui
import uix
import uiconst
import util
import planetCommon
import math
import uicls
import planet
import blue
import uthread
import const
import uiutil
import listentry
import localization
import form

class ECUContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.ECUContainer'
    default_name = 'ECUContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)



    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_SURVEYFORDEPOSITS, panelCallback=self.OpenSurveyWindow), util.KeyVal(id=planetCommon.PANEL_PRODUCTS, panelCallback=self.PanelShowProducts)]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns



    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(70, 'infoCont', padding=(p,
         p,
         p,
         p))
        self.currDepositTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/Extracting'), top=0)
        self.timeToDeplTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/TimeToDepletion'), top=40)
        left = self.infoContRightColAt
        self.currCycleGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), cyclic=True)
        self.currCycleGauge.left = left
        self.currCycleOutputTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/CurrentCycleOutput'), top=40, left=left)
        return infoCont



    def _UpdateInfoCont(self):
        currentTime = blue.os.GetWallclockTime()
        if self.pin.programType is not None and self.pin.qtyPerCycle > 0 and self.pin.expiryTime > currentTime:
            timeToDepletion = self.pin.GetTimeToExpiry()
            qtyRemaining = int(timeToDepletion / self.pin.GetCycleTime()) * self.pin.qtyPerCycle
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(localization.GetByLabel('UI/PI/Common/TimeToDepletion'))
            if totalTimeLeft < DAY:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=long(totalTimeLeft))
            else:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeWritten', time=long(totalTimeLeft))
            deposName = cfg.invtypes.Get(self.pin.programType).name
            if self.pin.activityState < planet.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
                currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
            else:
                currCycle = currentTime - self.pin.lastRunTime
            currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            cycleTime = self.pin.GetCycleTime()
            currCycleOutput = localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.GetProgramOutput(blue.os.GetWallclockTime()))
        else:
            currCycle = 0L
            totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=0L)
            currCycleProportion = 0.0
            cycleTime = 0L
            deposName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
            qtyRemaining = 0
            currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
        self.currDepositTxt.SetIcon(self.pin.programType)
        self.currDepositTxt.SetSubtext(deposName)
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            self.timeToDeplTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=currCycle, totalTime=cycleTime))
        self.currCycleOutputTxt.SetSubtext(currCycleOutput)



    def OpenSurveyWindow(self):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            sm.GetService('planetUI').myPinManager.EnterSurveyMode(self.pin.id)
            self.CloseByUser()
            return 
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        editBox = self._DrawEditBox(cont, localization.GetByLabel('UI/PI/Common/CantSurveyInEditMode'))
        cont.height = editBox.height + 4
        return cont



    def GetStatsEntries(self):
        scrolllist = planet.ui.BasePinContainer.GetStatsEntries(self)
        if self.pin.programType is not None:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), cfg.invtypes.Get(self.pin.programType).name)
            scrolllist.append(listentry.Get('Generic', {'label': label}))
        else:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), localization.GetByLabel('UI/PI/Common/NothingExtracted'))
            scrolllist.append(listentry.Get('Generic', {'label': label}))
        return scrolllist



    def _DecommissionSelf(self, *args):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            surveyWnd = form.PlanetSurvey.GetIfOpen()
            if surveyWnd and surveyWnd.ecuPinID == self.pin.id:
                sm.GetService('planetUI').ExitSurveyMode()
        planet.ui.BasePinContainer._DecommissionSelf(self)




