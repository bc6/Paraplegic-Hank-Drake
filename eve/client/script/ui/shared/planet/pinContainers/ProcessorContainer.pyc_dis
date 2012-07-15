#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/pinContainers/ProcessorContainer.py
import uix
import uiconst
import util
import planetCommon
import uicls
import planet
import blue
from service import ROLE_GML
import uthread
import const
import listentry
import uiutil
import localization

class ProcessorContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.ProcessorContainer'
    default_name = 'ProcessorContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)
        self.currentSchematicID = None

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_SCHEMATICS, panelCallback=self.PanelShowSchematics), util.KeyVal(id=planetCommon.PANEL_PRODUCTS, panelCallback=self.PanelShowProducts)]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns

    def PanelShowSchematics(self):
        self.schematicsCont = cont = uicls.Container(parent=self.actionCont, name='schematicsCont', pos=(0, 0, 0, 155), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.schematicsScroll = uicls.Scroll(parent=cont, name='schematicsScroll', align=uiconst.TOTOP, height=148)
        self.schematicsScroll.Startup()
        self.schematicsScroll.sr.id = 'planetProcessorSchematicsScroll'
        self.schematicsScroll.multiSelect = False
        self.schematicsScroll.HideUnderLay()
        self.schematicsScroll.OnSelectionChange = self.OnSchematicScrollSelectionChange
        uicls.Frame(parent=self.schematicsScroll, color=(1.0, 1.0, 1.0, 0.2))
        self.LoadSchematicsScroll()
        self.selectedSchematicCont = uicls.Container(parent=cont, name='selectedSchematicCont', pos=(0, 0, 0, 0), padding=(0, 7, 0, 0), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        return cont

    def LoadSchematicsScroll(self):
        scrolllist = []
        for schematic in planetCommon.GetSchematicData(self.pin.typeID):
            data = util.KeyVal(label=schematic.name, schematic=schematic, itemID=None, typeID=schematic.outputs[0].typeID, getIcon=True, OnClick=None, OnDblClick=self.InstallSchematic)
            sortBy = schematic.name
            scrolllist.append((sortBy, listentry.Get('Item', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.schematicsScroll.Load(contentList=scrolllist, headers=[])

    def OnSchematicScrollSelectionChange(self, entries):
        if not entries:
            return
        entry = entries[0]
        newSchematicID = entry.schematic.schematicID
        if newSchematicID == self.currentSchematicID:
            return
        self.currentSchematicID = newSchematicID
        self.uiEffects.MorphUI(self.selectedSchematicCont, 'opacity', 0.0, time=125.0, float=1, newthread=0, maxSteps=1000)
        if not self or self.destroyed or self.selectedSchematicCont.destroyed:
            return
        self.selectedSchematicCont.Flush()
        cont = self.SubPanelSelectedSchematic(self.selectedSchematicCont, entry.schematic)
        newHeight = 295
        self.schematicsCont.height = newHeight
        self.ResizeActionCont(newHeight)
        if not self or self.destroyed:
            return
        self.uiEffects.MorphUI(self.selectedSchematicCont, 'opacity', 1.0, time=125.0, float=1, newthread=0, maxSteps=1000)

    def SubPanelSelectedSchematic(self, parent, schematic):
        cont = uicls.Container(parent=parent, pos=(0, 0, 0, 140), align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        left = self.infoContRightColAt
        output = schematic.outputs[0]
        schematicTxt = localization.GetByLabel('UI/PI/Common/ItemAmount', amount=int(output.quantity), itemName=output.name)
        planet.ui.CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/OutputProduct'), subtext=schematicTxt, iconTypeID=output.typeID, left=5, top=0)
        planet.ui.CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/CycleTime'), subtext=localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=schematic.cycleTime * SEC), left=5, top=40)
        outputVolumeTxt = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=schematic.outputVolume)
        planet.ui.CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), subtext=outputVolumeTxt, left=5, top=80)
        for i, input in enumerate(schematic.inputs):
            topPos = i * 40
            caption = localization.GetByLabel('UI/PI/Common/InputNumberX', inputNum=i + 1)
            subtext = localization.GetByLabel('UI/PI/Common/ItemAmount', amount=int(input.quantity), itemName=cfg.invtypes.Get(input.typeID).name)
            planet.ui.CaptionAndSubtext(parent=cont, caption=caption, subtext=subtext, iconTypeID=input.typeID, left=left, top=topPos)

        btns = [[localization.GetByLabel('UI/PI/Common/InstallSchematic'), self.InstallSchematic, ()]]
        self.buttons = uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        return cont

    def InstallSchematic(self, *args):
        entries = self.schematicsScroll.GetSelected()
        if not entries:
            return
        entry = entries[0]
        schematicID = entry.schematic.schematicID
        self.planetUISvc.myPinManager.InstallSchematic(self.pin.id, schematicID)
        self.RenderIngredientGauges()
        self.ShowPanel(self.PanelShowProducts, localization.GetByLabel('UI/PI/Common/Products'))

    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(95, 'infoCont', padding=(p,
         p,
         p,
         p))
        self.currProductTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/Producing'))
        self.ingredientsTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/SchematicInput'), top=50)
        self.ingredientsTxt.state = uiconst.UI_DISABLED
        self.ingredientCont = uicls.Container(parent=infoCont, pos=(0, 63, 100, 0), state=uiconst.UI_PICKCHILDREN)
        self.RenderIngredientGauges()
        left = self.infoContRightColAt
        self.currCycleGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, left=left)
        self.amountPerCycleTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/OutputPerCycle'), left=left, top=40)
        self.amountPerHourTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), left=left, top=70)
        return infoCont

    def RenderIngredientGauges(self):
        self.ingredientCont.Flush()
        self.ingredientGauges = {}
        i = 0
        for typeID, amount in self.pin.GetConsumables().iteritems():
            gauge = planet.ui.ProcessorGauge(parent=self.ingredientCont, iconTypeID=typeID, maxAmount=amount, top=0, left=i * 24)
            self.ingredientGauges[typeID] = gauge
            i += 1

        if not self.pin.GetConsumables():
            self.ingredientsTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/NoSchematicSelected'))
        else:
            self.ingredientsTxt.SetSubtext('')

    def _UpdateInfoCont(self):
        if self.pin.schematicID:
            schematicObj = cfg.schematics.Get(self.pin.schematicID)
            schematicName = schematicObj.schematicName
            for t in cfg.schematicstypemap.get(self.pin.schematicID, []):
                if not t.isInput:
                    outputPerCycle = t.quantity
                    outputTypeID = t.typeID

            if self.pin.activityState < planet.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                status = localization.GetByLabel('UI/Common/Inactive')
            elif self.pin.IsActive():
                nextCycle = self.pin.GetNextRunTime()
                if nextCycle is None or nextCycle < blue.os.GetWallclockTime():
                    status = localization.GetByLabel('UI/PI/Common/ProductionCompletionImminent')
                else:
                    status = localization.GetByLabel('UI/PI/Common/InProduction')
                currCycle = self.pin.GetCycleTime() - (self.pin.GetNextRunTime() - blue.os.GetWallclockTime())
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            else:
                status = localization.GetByLabel('UI/PI/Common/WaitingForResources')
                currCycle = 0
                currCycleProportion = 0.0
        else:
            schematicName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
            status = localization.GetByLabel('UI/Common/Inactive')
            currCycleProportion = 0.0
            currCycle = 0
            outputPerCycle = 0
            outputTypeID = None
        for typeID, amountNeeded in self.pin.GetConsumables().iteritems():
            amount = self.pin.GetContents().get(typeID, 0)
            gauge = self.ingredientGauges.get(typeID)
            if not gauge:
                continue
            gauge.SetValue(float(amount) / amountNeeded)
            name = cfg.invtypes.Get(typeID).name
            gauge.hint = localization.GetByLabel('UI/PI/Common/ProductionGaugeHint', resourceName=name, amount=amount, amountNeeded=amountNeeded)

        self.currProductTxt.SetSubtext(schematicName)
        if self.pin.schematicID:
            if self.pin.activityState < planet.STATE_IDLE:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            else:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=long(currCycle), totalTime=self.pin.GetCycleTime()))
        self.currProductTxt.SetIcon(outputTypeID)
        self.currCycleGauge.SetValueInstantly(currCycleProportion)
        self.currCycleGauge.SetText(status)
        self.amountPerCycleTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=outputPerCycle))
        self.amountPerHourTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=self.pin.GetOutputVolumePerHour()))


class ProcessorGaugeContainer(uicls.Container):
    __guid__ = 'planet.ui.ProcessorGauge'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_name = 'ProcessorGauge'
    default_left = 0
    default_top = 0
    default_width = 20
    default_height = 30

    def ApplyAttributes(self, attributes):
        self.uiEffects = uicls.UIEffects()
        uicls.Container.ApplyAttributes(self, attributes)
        self.value = attributes.Get('value', 0.0)
        self.left = attributes.Get('left', 0)
        self.top = attributes.Get('top', 0)
        self.typeID = iconTypeID = attributes.Get('iconTypeID', 6)
        color = planetCommon.PLANET_COLOR_USED_PROCESSOR
        bgColor = (255 / 255.0,
         128 / 255.0,
         0 / 255.0,
         0.15)
        self.icon = uicls.Icon(parent=self, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, typeID=iconTypeID, size=16, ignoreSize=True)
        gaugeCont = uicls.Container(parent=self, pos=(0,
         0,
         self.width,
         self.width), align=uiconst.TOPLEFT)
        self.gauge = uicls.Fill(parent=gaugeCont, align=uiconst.TOLEFT, width=0, color=color, state=uiconst.UI_DISABLED)
        uicls.Fill(parent=gaugeCont, color=bgColor, state=uiconst.UI_DISABLED)
        self.subText = uicls.EveLabelSmall(text='', parent=self, top=22, state=uiconst.UI_DISABLED)
        self.busy = False
        self.SetValue(self.value)

    def SetValue(self, value, frequency = 8.0):
        if self.busy or value == self.value:
            return
        if value > 1.0:
            value = 1.0
        uthread.new(self._SetValue, value, frequency)
        self.subText.text = '%i%%' % (value * 100)

    def _SetValue(self, value, frequency):
        if not self or self.destroyed:
            return
        self.busy = True
        self.value = value
        self.uiEffects.MorphUIMassSpringDamper(self.gauge, 'width', int(self.width * value), newthread=0, float=0, dampRatio=0.6, frequency=frequency, minVal=0, maxVal=self.width, maxTime=1.0)
        if not self or self.destroyed:
            return
        self.busy = False

    def GetMenu(self):
        ret = [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.typeID])]
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        return ret

    def GetGMMenu(self):
        return [('TypeID: %s' % self.typeID, blue.pyos.SetClipboardData, [str(int(self.typeID))]), ('Add commodity to pin', self.AddCommodity, [])]

    def AddCommodity(self):
        pinID = sm.GetService('planetUI').currentContainer.pin.id
        sm.GetService('planetUI').planet.GMAddCommodity(pinID, self.typeID)