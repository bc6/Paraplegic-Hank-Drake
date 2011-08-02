import xtriui
import uix
import uthread
import form
import dbg
import log
import uiutil

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
            self.SelfDestruct()
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            raise 



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.flagID == const.flagCargo



    def DoGetShell(self):
        try:
            return eve.GetInventoryFromId(self.itemID)
        except UserError:
            self.SelfDestruct()
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
        self.displayName = mls.UI_SHARED_SOMEONESCARGOHOLD2 % {'name': uix.Possessive(name)}
        self.scope = 'station'
        ShipCargoView.Startup(self)




class InflightCargoView(ShipCargoView):
    __guid__ = 'form.InflightCargoView'

    def ApplyAttributes(self, attributes):
        ShipCargoView.ApplyAttributes(self, attributes)
        self.displayName = mls.UI_SHARED_MYCARGO
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



    def DoGetShell(self):
        return eve.GetInventoryFromId(self.itemID)



    def List(self):
        try:
            ret = self.GetShell().List()
        except UserError:
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            self.SelfDestruct()
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
        if slimItem.itemID == self.itemID:
            uthread.new(self.CloseX)


    DoBallRemove = uiutil.ParanoidDecoMethod(DoBallRemove, ('sr',))

    def DoBallClear(self, solitem):
        uthread.new(self.CloseX)


    DoBallClear = uiutil.ParanoidDecoMethod(DoBallClear, ('sr',))

    def OnSlimItemChange(self, oldItem, newItem):
        if oldItem.itemID == self.itemID and newItem.isEmpty and not oldItem.isEmpty:
            self.CloseX()


    OnSlimItemChange = uiutil.ParanoidDecoMethod(OnSlimItemChange, ('sr',))

    def OnItemChange(self, item, change):
        if item.itemID == self.itemID and item.stacksize == 0:
            self.CloseX()


    OnItemChange = uiutil.ParanoidDecoMethod(OnItemChange, ('sr',))

    def DBLessLimitationsCheck(self, errorName, item):
        if errorName in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload'):
            eve.Message('ItemMoveGoesThroughFullCargoHold', {'itemType': cfg.invtypes.Get(item.typeID).name})
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
        if name != 'My':
            name = '%s' % uix.Possessive(name)
        self.displayName = mls.UI_SHARED_SOMEONESDRONEBAY % {'name': name}
        self.scope = 'station'
        form.VirtualInvWindow.Startup(self)



    def DoGetShell(self):
        return eve.GetInventoryFromId(self.itemID)



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
        return eve.GetInventoryFromId(self.itemID)



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.flagID == self.locationFlag




class PlanetInventory(form.VirtualInvWindow):
    __guid__ = 'form.PlanetInventory'
    __notifyevents__ = ['OnBallparkCall']

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        _id = attributes._id
        name = attributes.displayName
        self.locationFlag = None
        self.hasCapacity = 1
        self.Startup(_id, name)



    def Startup(self, id_, name):
        self.id = self.itemID = id_
        self.displayName = name
        self.locationFlag = None
        self.scope = 'inflight'
        form.VirtualInvWindow.Startup(self)



    def List(self):
        try:
            ret = self.GetShell().List()
        except UserError:
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.sr.cookie)
            self.SelfDestruct()
            raise 
        return ret



    def DoGetShell(self):
        return eve.GetInventoryFromId(self.itemID)



    def IsMine(self, rec):
        return rec.locationID == self.itemID and rec.ownerID == session.charid



    def OnBallparkCall(self, functionName, args):
        if self is None or self.destroyed:
            return 
        if functionName == 'WarpTo':
            warpingObjectID = args[0]
            if warpingObjectID == session.shipid:
                self.SelfDestruct()




