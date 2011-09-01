import xtriui
import uix
import uiutil
import util
import listentry
import uicls
import blue
import uiconst

class ShipScan(uicls.Window):
    __guid__ = 'form.ShipScan'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        shipID = attributes.shipID
        self.SetCaption('%s SCAN RESULTS' % cfg.evelocations.Get(shipID).name)
        self.SetMinSize([200, 200])
        self.SetWndIcon('ui_3_64_10', mainTop=-13)
        self.DefineButtons(uiconst.CLOSE)
        self.sr.capacityText = uicls.Label(text=' ', name='capacityText', parent=self.sr.topParent, left=8, top=4, align=uiconst.TOPRIGHT, autoheight=1, autowidth=1, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1)
        self.sr.gaugeParent = uicls.Container(name='gaugeParent', align=uiconst.TOPRIGHT, parent=self.sr.topParent, left=const.defaultPadding, height=7, width=100, state=uiconst.UI_DISABLED, top=self.sr.capacityText.top + self.sr.capacityText.textheight + 1)
        uicls.Frame(parent=self.sr.gaugeParent, color=(0.5, 0.5, 0.5, 0.3))
        self.sr.gauge = uicls.Container(name='gauge', align=uiconst.TOLEFT, parent=self.sr.gaugeParent, state=uiconst.UI_PICKCHILDREN, width=0)
        uicls.Fill(parent=self.sr.gaugeParent, color=(0.0, 0.521, 0.67, 0.1), align=uiconst.TOALL)
        uicls.Fill(parent=self.sr.gauge, color=(0.0, 0.521, 0.67, 0.6))
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        t = uicls.Label(text=mls.UI_INFLIGHT_MODULESFITTED, parent=self.sr.topParent, left=8, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, align=uiconst.BOTTOMLEFT)



    def LoadResult(self, capacitorCharge, capacitorCapacity, moduleList):
        (total, full,) = (capacitorCapacity, capacitorCharge)
        if total:
            proportion = min(1.0, max(0.0, full / float(total)))
        else:
            proportion = 1.0
        self.sr.gauge.width = int(proportion * self.sr.gaugeParent.width)
        self.sr.capacityText.text = '%s/%s %s' % (util.FmtAmt(full, showFraction=1), util.FmtAmt(total, showFraction=1), cfg.dgmunits.Get(const.unitCapacitorUnits).displayName)
        scrolllist = []
        for info in moduleList:
            if type(info) == type(()):
                (typeID, quantity,) = info
            else:
                (typeID, quantity,) = (info.typeID, info.stacksize)
            invtype = cfg.invtypes.Get(typeID)
            if invtype.categoryID == const.categoryCharge:
                quantity = 1
            for i in range(quantity):
                data = util.KeyVal()
                data.label = invtype.name
                data.itemID = None
                data.typeID = typeID
                data.getIcon = 1
                scrolllist.append(listentry.Get('Item', data=data))


        self.sr.scroll.Load(contentList=scrolllist)
        if len(scrolllist) == 0:
            self.SetHint(mls.UI_INFLIGHT_NOMODULESDETECTED)
        else:
            self.SetHint(None)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)




class CargoScan(uicls.Window):
    __guid__ = 'form.CargoScan'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        shipID = attributes.shipID
        cargoList = attributes.cargoList
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        slimItem = bp.slimItems[shipID]
        shipName = uix.GetSlimItemName(slimItem)
        self.SetCaption(mls.UI_INFLIGHT_CARGOSCANRESULT2 % {'name': shipName,
         'num': len(cargoList)})
        self.SetMinSize([200, 200])
        self.SetWndIcon('ui_3_64_11', mainTop=-13)
        self.DefineButtons(uiconst.CLOSE)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        t = uicls.Label(text=mls.UI_GENERIC_ITEMSINCONTAINER, parent=self.sr.topParent, left=8, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, align=uiconst.BOTTOMLEFT)



    def ShowInfo(self, typeID, isCopy):
        abstractInfo = util.KeyVal(categoryID=const.categoryBlueprint, isCopy=isCopy)
        sm.GetService('info').ShowInfo(typeID)



    def LoadResult(self, cargoList):
        scrolllist = []
        for (typeID, quantity,) in cargoList:
            invType = cfg.invtypes.Get(typeID)
            qty = quantity if quantity > 0 else 1
            data = util.KeyVal()
            isCopy = False
            if invType.categoryID == const.categoryBlueprint:
                if quantity == -const.singletonBlueprintCopy:
                    typeName = '%s (<color=0xff999999><b>%s</b></color>)' % (invType.name, mls.UI_GENERIC_COPY)
                    quantity = 1
                    isCopy = True
                else:
                    typeName = '%s (<color=0xff55bb55><b>%s</b></color>)' % (invType.name, mls.UI_GENERIC_ORIGINAL)
            else:
                typeName = invType.name
            data.label = '%d %s' % (qty, typeName)
            data.itemID = None
            data.typeID = typeID
            data.isCopy = isCopy
            data.getIcon = True
            if invType.categoryID == const.categoryBlueprint:
                data.abstractinfo = util.KeyVal(categoryID=const.categoryBlueprint, isCopy=data.isCopy)
            data.GetMenu = lambda x: []
            scrolllist.append(listentry.Get('Item', data=data))

        self.sr.scroll.Load(contentList=scrolllist, noContentHint=mls.UI_GENERIC_NOITEMSFOUND)




