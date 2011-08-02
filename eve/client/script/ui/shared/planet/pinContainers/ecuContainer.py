import xtriui
import uix
import uiconst
import util
import planetCommon
import math
import uicls
import planet
import draw
import blue
import uthread
import const
import uiutil
import listentry

class ECUContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.ECUContainer'
    default_name = 'ECUContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)



    def _GetActionButtons(self):
        btns = [util.KeyVal(name=mls.UI_PI_SURVEYFORDEPOSITS, panelCallback=self.OpenSurveyWindow, icon='ui_44_32_5'), util.KeyVal(name=mls.UI_GENERIC_PRODUCTS, panelCallback=self.PanelShowProducts, icon='ui_44_32_2')]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns



    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(70, 'infoCont', padding=(p,
         p,
         p,
         p))
        self.currDepositTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_EXTRACTING, top=0)
        self.timeToDeplTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_TIMETODEPLETION, top=40)
        left = self.infoContRightColAt
        self.currCycleGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=mls.UI_PI_CURRENTCYCLE, cyclic=True)
        self.currCycleGauge.left = left
        self.currCycleOutputTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_CURRENTCYCLEOUTPUT, top=40, left=left)
        return infoCont



    def _UpdateInfoCont(self):
        currentTime = blue.os.GetTime()
        if self.pin.programType is not None and self.pin.qtyPerCycle > 0 and self.pin.expiryTime > currentTime:
            timeToDepletion = self.pin.GetTimeToExpiry()
            qtyRemaining = int(timeToDepletion / self.pin.GetCycleTime()) * self.pin.qtyPerCycle
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(mls.UI_PI_TIMETODEPLETION)
            if totalTimeLeft < DAY:
                totalTimeLeft = util.FmtTime(float(totalTimeLeft))
            else:
                totalTimeLeft = util.FmtTimeInterval(long(totalTimeLeft), breakAt='hour')
            deposName = cfg.invtypes.Get(self.pin.programType).name
            if self.pin.activityState < planet.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
                currCycleOutput = mls.UI_GENERIC_NONE
            else:
                currCycle = currentTime - self.pin.lastRunTime
            currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            cycleTime = self.pin.GetCycleTime()
            currCycleOutput = '%s %s' % (self.pin.GetProgramOutput(blue.os.GetTime()), mls.UI_GENERIC_UNITS)
        else:
            currCycle = 0
            totalTimeLeft = util.FmtTime(0)
            currCycleProportion = 0.0
            cycleTime = 0
            deposName = '<color=red>%s<color>' % mls.UI_GENERIC_NOTHING
            qtyRemaining = 0
            currCycleOutput = mls.UI_GENERIC_NONE
        self.currDepositTxt.SetIcon(self.pin.programType)
        self.currDepositTxt.SetSubtext(deposName)
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            self.currCycleGauge.SetSubText(mls.UI_PI_INACTIVE_REASON % {'reason': mls.UI_PI_GENERIC_EDITMODE})
            self.timeToDeplTxt.SetSubtext(mls.UI_PI_INACTIVE_REASON % {'reason': mls.UI_PI_GENERIC_EDITMODE})
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText('%s / %s' % (util.FmtTime(currCycle), util.FmtTime(cycleTime)))
        self.currCycleOutputTxt.SetSubtext(currCycleOutput)



    def OpenSurveyWindow(self):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            sm.GetService('planetUI').myPinManager.EnterSurveyMode(self.pin.id)
            self.CloseX()
            return 
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        editBox = self._DrawEditBox(cont, mls.UI_PI_CANTSURVEYINEDITMODE)
        cont.height = editBox.height + 4
        return cont



    def GetStatsEntries(self):
        scrolllist = planet.ui.BasePinContainer.GetStatsEntries(self)
        if self.pin.programType is not None:
            scrolllist.append(listentry.Get('Generic', {'label': '%s<t>%s' % (mls.UI_PI_EXTRACTING, cfg.invtypes.Get(self.pin.programType).name)}))
        else:
            scrolllist.append(listentry.Get('Generic', {'label': '%s<t>%s' % (mls.UI_PI_EXTRACTING, mls.UI_GENERIC_NOTHING)}))
        return scrolllist



    def _DecommissionSelf(self, *args):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            surveyWnd = sm.GetService('window').GetWindow('PlanetSurvey')
            if surveyWnd and surveyWnd.ecuPinID == self.pin.id:
                sm.GetService('planetUI').ExitSurveyMode()
        planet.ui.BasePinContainer._DecommissionSelf(self)




