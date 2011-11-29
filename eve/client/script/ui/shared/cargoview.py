import form
import localization
import log
import uicls
import uiconst
import uiutil
import uthread
import util

class ShipCargoView(form.VirtualInvWindow):
    __guid__ = 'form.ShipCargoView'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        self.locationFlag = const.flagCargo
        self.hasCapacity = 1



    def List(self):
        try:
            return self.GetShell().ListCargo()
        except UserError:
            self.Close()
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            raise 



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.flagID == const.flagCargo



    def DoGetShell(self):
        try:
            return sm.GetService('invCache').GetInventoryFromId(self.itemID, locationID=session.stationid2)
        except UserError:
            self.Close()
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            raise 



    def OnItemDropBookmark(self, node):
        return True




class DockedCargoView(ShipCargoView):
    __guid__ = 'form.DockedCargoView'

    def ApplyAttributes(self, attributes):
        form.ShipCargoView.ApplyAttributes(self, attributes)
        id_ = attributes._id
        name = attributes.displayName
        self.Startup(id_, name)



    def Startup(self, id_, name):
        self.itemID = id_
        self.displayName = localization.GetByLabel('UI/Cargo/SomeonesCargoHoldLabel', possessiveName=name)
        self.scope = 'station'
        ShipCargoView.Startup(self)




class InflightCargoView(ShipCargoView):
    __guid__ = 'form.InflightCargoView'

    def ApplyAttributes(self, attributes):
        ShipCargoView.ApplyAttributes(self, attributes)
        self.displayName = localization.GetByLabel('UI/Cargo/MyCargoLabel')
        self.scope = 'inflight'
        self.itemID = eve.session.shipid
        ShipCargoView.Startup(self)




class LootCargoView(form.VirtualInvWindow):
    __guid__ = 'form.LootCargoView'
    __notifyevents__ = ['OnSessionChanged',
     'OnPostCfgDataChanged',
     'DoBallRemove',
     'DoBallClear',
     'OnItemChange',
     'OnSlimItemChange']

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id = attributes._id
        name = attributes.displayName
        hasCapacity = attributes.hasCapacity or False
        locationFlag = attributes.locationFlag
        isWreck = attributes.isWreck or False
        typeID = sm.GetService('invCache').GetInventoryFromId(id).typeID
        if typeID:
            icon = cfg.invtypes.Get(typeID).Icon()
            if icon and icon.iconFile:
                windowIcon = icon.iconFile
                self.default_windowIcon = windowIcon
        self.hasCapacity = 1
        self.locationFlag = None
        self.Startup(id, name, hasCapacity, locationFlag, isWreck)



    def Startup(self, id_, name, hasCapacity = 0, locationFlag = None, isWreck = False):
        self.id = self.itemID = id_
        self.isWreck = isWreck
        self.displayName = name
        self.scope = ['station', 'inflight'][(eve.session.stationid is None)]
        self.hasCapacity = hasCapacity
        self.locationFlag = locationFlag
        form.VirtualInvWindow.Startup(self)
        bp = sm.GetService('michelle').GetBallpark()
        item = bp.GetInvItem(self.itemID) if bp else None
        if item and item.groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupSpawnContainer):
            lootAllBtnGrp = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Inventory/LootAll'),
              self.LootAll,
              (),
              None]], parent=self.GetMainArea(), align=uiconst.CENTERBOTTOM, idx=0)
            self.sr.scroll.padBottom = lootAllBtnGrp.height + 4
            self.SetMinSize((256, 200))



    def DoGetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)



    def LootAll(self, *args):
        thisInv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        shipInv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        items = thisInv.List()
        if len(items) > 0 and sm.GetService('consider').ConfirmTakeFromContainer(self.itemID):
            if sm.GetService('consider').ConfirmTakeIllicitGoods(items):
                if len(items) > 1:
                    shipInv.MultiAdd([ item.itemID for item in items ], self.itemID, flag=const.flagCargo)
                else:
                    shipInv.Add(items[0].itemID, self.itemID, flag=const.flagCargo)



    def List(self):
        try:
            ret = self.GetShell().List()
        except UserError:
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            self.Close()
            raise 
        if self.isWreck:
            sm.GetService('wreck').MarkViewed(self.id, True)
        if self.locationFlag is not None:
            return [ row for row in ret if row.flagID == self.locationFlag ]
        return ret



    def IsMine(self, rec):
        if self.locationFlag is not None:
            return rec.locationID == self.itemID and rec.flagID == self.locationFlag
        else:
            return rec.locationID == self.itemID



    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem is None:
            log.LogWarn('DoBallRemove::lootcargoview slimItem is None')
            return 
        if ball:
            log.LogInfo('DoBallRemove::lootcargoview', ball.id)
        if slimItem.itemID == self.itemID and slimItem.itemID != util.GetActiveShip():
            uthread.new(self.CloseByUser)


    DoBallRemove = uiutil.ParanoidDecoMethod(DoBallRemove, ('sr',))

    def DoBallClear(self, solitem):
        if self.itemID != util.GetActiveShip() or self.locationFlag != const.flagShipHangar:
            uthread.new(self.CloseByUser)


    DoBallClear = uiutil.ParanoidDecoMethod(DoBallClear, ('sr',))

    def OnSlimItemChange(self, oldItem, newItem):
        if oldItem.itemID == self.itemID and newItem.isEmpty and not oldItem.isEmpty:
            self.CloseByUser()


    OnSlimItemChange = uiutil.ParanoidDecoMethod(OnSlimItemChange, ('sr',))

    def OnItemChange(self, item, change):
        if item.itemID == self.itemID and item.stacksize == 0:
            self.CloseByUser()


    OnItemChange = uiutil.ParanoidDecoMethod(OnItemChange, ('sr',))

    def DBLessLimitationsCheck(self, errorName, item):
        if errorName in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload'):
            eve.Message('ItemMoveGoesThroughFullCargoHold', {'itemType': item.typeID})
            return True
        return False



    def OnItemDropBookmark(self, node):
        if self.isWreck:
            return False
        else:
            if self.locationFlag == const.flagShipHangar:
                return False
            return True




class DroneBay(form.VirtualInvWindow):
    __guid__ = 'form.DroneBay'
    default_windowIcon = 'ui_11_64_16'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id = attributes._id
        name = attributes.displayName
        self.locationFlag = const.flagDroneBay
        self.hasCapacity = 1
        self.Startup(id, name)



    def Startup(self, id_, name):
        self.itemID = id_
        self.displayName = localization.GetByLabel('UI/Cargo/SomeonesDroneBayLabel', possessiveName=name)
        self.scope = 'station'
        form.VirtualInvWindow.Startup(self)



    def DoGetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.flagID == const.flagDroneBay




class SpecialCargoBay(form.VirtualInvWindow):
    __guid__ = 'form.SpecialCargoBay'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id = attributes._id
        name = attributes.displayName
        locationFlag = attributes.locationFlag
        self.locationFlag = None
        self.hasCapacity = 1
        self.Startup(id, name, locationFlag)



    def Startup(self, id_, name, locationFlag):
        self.itemID = id_
        self.displayName = name
        self.locationFlag = locationFlag
        self.scope = 'station'
        form.VirtualInvWindow.Startup(self)



    def DoGetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.flagID == self.locationFlag




