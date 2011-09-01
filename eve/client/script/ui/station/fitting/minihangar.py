import uix
import xtriui
import uthread
import util
import uicls
import uiconst

class Slots(uicls.Container):
    __guid__ = 'xtriui.Slots'

    def Startup(self, *args):
        (flag, iconpath, name,) = args
        self.flag = flag
        self.sr.color = '<color=0xcfffffff>'
        self.sr.icon = uicls.Icon(parent=self, size=32, state=uiconst.UI_DISABLED, icon=iconpath, ignoreSize=True)
        self.sr.hint = name
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.sr.textCont = uicls.Container(name='textCont', align=uiconst.TOPLEFT, parent=self, left=32, width=self.width - 32, top=0, clipChildren=0, height=self.height)
        self.sr.text = uicls.Label(text=name, parent=self.sr.textCont, align=uiconst.TOALL, top=4, left=8, fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, uppercase=1)
        self.sr.status = uicls.Label(text='', parent=self, width=self.width - 32, color=None, autowidth=False, top=16, left=40, state=uiconst.UI_DISABLED)



    def OnMouseEnter(self, *args):
        if not eve.dragData:
            self.Hilite(1)



    def OnMouseExit(self, *args):
        if not eve.dragData:
            self.Hilite(0)



    def Hilite(self, state):
        self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]




class FittingSlot(Slots):
    __guid__ = 'xtriui.Minihangar'

    def IsMine(self, item):
        return item.flagID == self.flag and item.locationID == eve.session.shipid



    def Startup(self, flag, iconpath, name):
        xtriui.Slots.Startup(self, flag, iconpath, name)
        self.sr.multiplier = 1.0
        uicls.Line(parent=self, align=uiconst.RELATIVE, width=1, height=32, left=32, top=0)
        sm.GetService('inv').Register(self)
        uthread.new(self.UpdateCargo)
        self.invReady = 1



    def UpdateCargo(self):
        cap = self.GetCapacity()
        if not cap:
            return 
        if not self or self.destroyed:
            return 
        cap2 = round(cap.capacity * self.sr.multiplier)
        self.sr.status.text = '%i/%s%i m3' % (cap.used, self.sr.color, cap2)



    def GetCapacity(self):
        ship = self.GetShell()
        if not ship:
            self.sr.status.text = '-'
            return 
        return ship.GetCapacity(self.flag)



    def SetMultiply(self, color, multiplier):
        self.sr.color = color
        self.sr.multiplier = multiplier
        self.UpdateCargo()



    def GetShell(self):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        return ship



    def AddItem(self, item):
        self.UpdateCargo()



    def UpdateItem(self, item, *etc):
        self.UpdateCargo()



    def RemoveItem(self, item):
        self.UpdateCargo()



    def OnClick(self, *args):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if self.flag == const.flagDroneBay:
            sm.GetService('menu').OpenDroneBay([ship])
        else:
            sm.GetService('menu').OpenCargohold([ship])



    def OnDragEnter(self, dragObj, drag, *args):
        if drag is None:
            return 0
        for each in drag:
            if getattr(each, '__guid__', None) not in ('xtriui.InvItem', 'listentry.InvItem'):
                return 0
            if self.flag == const.flagDroneBay and each.rec.categoryID != const.categoryDrone:
                return 0

        self.Hilite(1)
        return 1



    def OnDragExit(self, *args):
        self.Hilite(0)



    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)
        itemlist = [ item for item in nodes if getattr(item, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem') if not (self.flag == const.flagDroneBay and item.rec.categoryID != const.categoryDrone) ]
        if len(itemlist) == 0:
            return 
        itemLocation = itemlist[0].item.locationID
        if len(itemlist) == 1:
            qty = getattr(itemlist[0].rec, 'quantity', 1)
            if uicore.uilib.Key(uiconst.VK_SHIFT) and qty > 1:
                ret = uix.QtyPopup(qty, 1, 1, None)
                if ret is None:
                    return 
                qty = ret['qty']
            return eve.GetInventoryFromId(eve.session.shipid).Add(itemlist[0].itemID, itemLocation, qty=qty, flag=self.flag)
        return eve.GetInventoryFromId(eve.session.shipid).MultiAdd([ item.itemID for item in itemlist ], itemLocation, flag=self.flag)




class CargoSlots(uicls.Container):
    __guid__ = 'xtriui.CargoSlots'

    def Startup(self, name, iconpath, flag, dogmaLocation):
        self.flag = flag
        self.sr.icon = uicls.Icon(parent=self, size=32, state=uiconst.UI_DISABLED, ignoreSize=True, icon=iconpath)
        self.sr.hint = name
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', align=uiconst.RELATIVE, state=uiconst.UI_HIDDEN, idx=-1, width=32, height=self.height)
        self.sr.icon.color.a = 0.8
        uicls.Container(name='push', parent=self, align=uiconst.TOLEFT, width=32)
        self.sr.statusCont = uicls.Container(name='statusCont', parent=self, align=uiconst.TOLEFT, width=50)
        self.sr.statustext1 = uicls.Label(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=2, idx=0, state=uiconst.UI_DISABLED, mousehilite=1, align=uiconst.TOPRIGHT)
        self.sr.statustext2 = uicls.Label(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=14, idx=0, state=uiconst.UI_DISABLED, mousehilite=1, align=uiconst.TOPRIGHT)
        m3TextCont = uicls.Container(name='m3Cont', parent=self, align=uiconst.TOLEFT, width=12)
        self.sr.m3Text = uicls.Label(text='m3', parent=m3TextCont, name='m3', left=4, top=14, idx=0, state=uiconst.UI_NORMAL, mousehilite=1)
        self.dogmaLocation = dogmaLocation
        sm.GetService('inv').Register(self)
        self.invReady = 1



    def IsMine(self, item):
        return item.flagID == self.flag and item.locationID == eve.session.shipid



    def AddItem(self, item):
        self.Update()



    def UpdateItem(self, item, *etc):
        self.Update()



    def RemoveItem(self, item):
        self.Update()



    def OnMouseEnter(self, *args):
        if not eve.dragData:
            self.DoMouseEntering()



    def OnMouseEnterDrone(self, *args):
        if eve.session.stationid:
            self.DoMouseEntering()



    def DoMouseEntering(self):
        self.Hilite(1)
        self.sr.statustext1.OnMouseEnter()
        self.sr.statustext2.OnMouseEnter()
        self.sr.m3Text.OnMouseEnter()



    def OnMouseExit(self, *args):
        if not eve.dragData:
            self.Hilite(0)
            self.sr.statustext1.OnMouseExit()
            self.sr.statustext2.OnMouseExit()
            self.sr.m3Text.OnMouseExit()
            uthread.new(self.Update)



    def Hilite(self, state):
        self.sr.icon.color.a = [0.8, 1.0][state]



    def SetStatusText(self, text1, text2, color):
        self.sr.statustext1.text = text1
        self.sr.statustext2.text = '/ %s%s' % (color, text2)
        self.sr.statusCont.width = max(0, self.sr.statustext1.textwidth, self.sr.statustext2.textwidth)



    def GetCapacity(self, flag = None):
        ship = sm.StartService('godma').GetItem(eve.session.shipid)
        if not ship:
            self.sr.status.text = '-'
            return 
        return ship.GetCapacity(flag)



    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)
        itemlist = [ item for item in nodes if getattr(item, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem') if not (self.flag == const.flagDroneBay and item.rec.categoryID != const.categoryDrone) ]
        if len(itemlist) == 0:
            return 
        itemLocation = itemlist[0].item.locationID
        shipID = util.GetActiveShip()
        inventory = sm.GetService('invCache').GetInventoryFromId(shipID, session.stationid2)
        if len(itemlist) == 1:
            qty = getattr(itemlist[0].rec, 'quantity', 1)
            if uicore.uilib.Key(uiconst.VK_SHIFT) and qty > 1:
                ret = uix.QtyPopup(qty, 1, 1, None)
                if ret is None:
                    return 
                qty = ret['qty']
            return inventory.Add(itemlist[0].itemID, itemLocation, qty=qty, flag=self.flag)
        return inventory.MultiAdd([ item.itemID for item in itemlist ], itemLocation, flag=self.flag)



    def Update(self, multiplier = 1.0):
        cap = self.GetCapacity(self.flag)
        if not cap:
            return 
        if not self or self.destroyed:
            return 
        cap2 = cap.capacity * multiplier
        color = '<color=0xc0ffffff>'
        if multiplier != 1.0:
            color = '<color=0xffffff00>'
        used = util.FmtAmt(cap.used, showFraction=1)
        cap2 = util.FmtAmt(cap2, showFraction=1)
        self.SetStatusText(used, cap2, color)




class CargoDroneSlots(CargoSlots):
    __guid__ = 'xtriui.CargoDroneSlots'

    def GetCapacity(self, flag = None):
        return self.dogmaLocation.GetCapacity(util.GetActiveShip(), const.attributeDroneCapacity, const.flagDroneBay)




class CargoCargoSlots(CargoSlots):
    __guid__ = 'xtriui.CargoCargoSlots'

    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)
        if len(nodes) == 1:
            item = nodes[0].item
            if cfg.IsShipFittingFlag(item.flagID):
                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                shipID = util.GetActiveShip()
                if cfg.IsFittableCategory(item.categoryID):
                    dogmaLocation.UnloadModuleToContainer(shipID, item.itemID, (shipID,))
                    return 
                if item.categoryID == const.categoryCharge:
                    dogmaLocation.UnloadChargeToContainer(shipID, item.itemID, (shipID,), const.flagCargo)
                    return 
        CargoSlots.OnDropData(self, dragObj, nodes)



    def GetCapacity(self, flag = None):
        return self.dogmaLocation.GetCapacity(util.GetActiveShip(), const.attributeCapacity, const.flagCargo)




