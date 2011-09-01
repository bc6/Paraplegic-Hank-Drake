import uix
import xtriui
import uthread
import form
import blue
import moniker
import draw
import util
import uicls
import uiconst
import log

class SpyHangar(form.VirtualInvWindow):
    __guid__ = 'form.SpyHangar'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id_ = attributes.id_
        ownerID = attributes.ownerID
        self.scope = 'station'
        self.itemID = eve.session.stationid
        self.oneWay = 1
        self.viewOnly = 1
        self.Startup(id_, ownerID)



    def Startup(self, id_, ownerID):
        self.id = id_
        self.itemID = id_
        self.ownerID = ownerID
        name = cfg.eveowners.Get(ownerID).name
        self.displayName = mls.UI_SHARED_HANGAR_NAME % {'name': name}
        form.VirtualInvWindow.Startup(self)
        self.state = uiconst.UI_NORMAL



    def DoGetShell(self):
        return eve.GetInventoryFromId(self.id)



    def IsMine(self, item):
        return item.locationID == self.id and item.ownerID == self.ownerID



    def OnItemDropBookmark(self, node):
        return False




class ItemHangar(form.VirtualInvWindow):
    __guid__ = 'form.ItemHangar'
    __notifyevents__ = ['OnSessionChanged', 'OnPostCfgDataChanged', 'OnItemNameChange']
    default_left = 135

    def default_top(self):
        dh = uicore.desktop.height
        return dh - self.default_height - 256



    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        self.displayName = mls.UI_GENERIC_ITEMS
        self.scope = 'station'
        self.indexID = 'Items'
        self.locationFlag = const.flagHangar
        sm.RegisterNotify(self)
        self.Startup()



    def Startup(self):
        form.VirtualInvWindow.Startup(self)
        self.SetWndIcon('ui_12_64_3', mainTop=-6, size=128)
        self.SetMainIconSize(44)



    def IsMine(self, rec):
        return rec.locationID == session.stationid2 and rec.ownerID == eve.session.charid and rec.flagID == const.flagHangar and cfg.invtypes.Get(rec.typeID).categoryID != const.categoryShip



    def DoGetShell(self):
        return eve.GetInventory(const.containerHangar)



    def GetContainerArgs(self):
        return (const.containerHangar,)



    def Add(self, itemID, sourceLocation, quantity, dividing = False):
        return self.GetShell().Add(itemID, sourceLocation, qty=quantity, flag=const.flagHangar)



    def OnItemDropBookmark(self, node):
        return True



    def OnItemNameChange(self, *args):
        self.Refresh()




class ShipHangar(form.VirtualInvWindow):
    __guid__ = 'form.ShipHangar'
    __notifyevents__ = ['OnSessionChanged', 'OnPostCfgDataChanged', 'OnItemNameChange']

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        self.displayName = mls.UI_GENERIC_SHIPS
        self.scope = 'station'
        self.locationFlag = const.flagHangar
        sm.RegisterNotify(self)
        self.Startup()



    def Startup(self):
        form.VirtualInvWindow.Startup(self)
        self.SetWndIcon('ui_9_64_5', mainTop=-8, size=128)
        self.SetMainIconSize(48)



    def IsMine(self, rec):
        return rec.locationID == session.stationid2 and rec.ownerID == eve.session.charid and rec.flagID == const.flagHangar and cfg.invtypes.Get(rec.typeID).Group().Category().id == const.categoryShip



    def DoGetShell(self):
        return eve.GetInventory(const.containerHangar)



    def GetContainerArgs(self):
        return (const.containerHangar,)



    def Add(self, itemID, sourceLocation, quantity, dividing = False):
        return self.GetShell().Add(itemID, sourceLocation, qty=quantity, flag=const.flagHangar)



    def OnItemNameChange(self, *args):
        self.Refresh()




class CorpHangar(form.VirtualInvWindow):
    __guid__ = 'form.CorpHangar'
    __notifyevents__ = ['OnSessionChanged',
     'OnPostCfgDataChanged',
     'DoBallRemove',
     'DoBallClear']

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        officeID = attributes.officeID
        name = attributes.displayName or ''
        hasCapacity = attributes.hasCapacity or False
        locationFlag = attributes.locationFlag
        isOffice = attributes.isOffice or True
        self.hasCapacity = hasCapacity
        self.scope = 'station'
        self.displayName = mls.UI_GENERIC_CORPHANGAR
        self.allHangars = None
        self.hangars = None
        self.oneWay = 1
        self.locationFlag = const.flagHangar
        self.noAccessMsg = None
        self.rolesByFlag = {const.flagHangar: (const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
         const.flagCorpSAG2: (const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
         const.flagCorpSAG3: (const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
         const.flagCorpSAG4: (const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
         const.flagCorpSAG5: (const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
         const.flagCorpSAG6: (const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
         const.flagCorpSAG7: (const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
        self.flagsList = self.rolesByFlag.keys()
        self.Startup(officeID, name, hasCapacity, locationFlag, isOffice)



    def OnSessionChanged(self, isRemote, session, change):
        if change.has_key('stationid'):
            if self is not None and not self.destroyed:
                uthread.new(self.SelfDestruct)



    def Startup(self, officeID, name = '', hasCapacity = 0, locationFlag = None, isOffice = True):
        self.SetMinSize((250, 160))
        self.name = 'corpHangar_%s' % officeID
        self.id = self.itemID = officeID
        self.ownerID = self.GetShell().GetItem().ownerID
        form.VirtualInvWindow.Startup(self)
        if eve.session.stationid:
            if const.corpRoleStationManager & eve.session.corprole == const.corpRoleStationManager:
                if sm.GetService('corp').DoesCharactersCorpOwnThisStation():
                    self.allHangars = 1
            if not hasCapacity and isOffice:
                btns = [[[mls.UI_CMD_MEMBERHANGARS, mls.UI_CMD_ALLHANGARS][(not not self.allHangars)],
                  self.ShowHangars,
                  None,
                  None]]
                if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                    btns.append([mls.UI_CMD_UNRENTOFFICE,
                     self.UnrentOffice,
                     None,
                     None])
                uicls.ButtonGroup(btns=btns, parent=self.sr.main, idx=0)
            if session.corprole & const.corpRoleSecurityOfficer == const.corpRoleSecurityOfficer:
                uthread.new(self.InitHangars)
        divisions = sm.GetService('corp').GetDivisionNames()
        scrollIdx = self.sr.scroll.parent.children.index(self.sr.scroll)
        maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        maintabs.Startup([['%s1' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division1',
          self.sr.scroll],
         ['%s2' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division2',
          self.sr.scroll],
         ['%s3' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division3',
          self.sr.scroll],
         ['%s4' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division4',
          self.sr.scroll]], 'corphangarpanel', autoselecttab=0)
        subtabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        subtabs.Startup([['%s5' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division5',
          self.sr.scroll], ['%s6' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division6',
          self.sr.scroll], ['%s7' % mls.UI_GENERIC_DIVISION,
          self.sr.scroll,
          self,
          'division7',
          self.sr.scroll]], 'corphangarpanel', autoselecttab=0)
        for i in xrange(1, 5):
            maintabs.sr.Get('%s%s_tab' % (mls.UI_GENERIC_DIVISION, i), None).OnDropData = getattr(self, 'DropInDivision%s' % i, None)

        for i in xrange(5, 8):
            subtabs.sr.Get('%s%s_tab' % (mls.UI_GENERIC_DIVISION, i), None).OnDropData = getattr(self, 'DropInDivision%s' % i, None)

        self.sr.maintabs = maintabs
        self.sr.subtabs = subtabs
        self.sr.maintabs.AddRow(subtabs)
        self.sr.maintabs.AutoSelect()
        self.SetDivisionalHangarNames(divisions)



    def SetAccess(self):
        role = self.rolesByFlag[self.locationFlag][1]
        shipOwnerID = None
        if getattr(self, 'id', None):
            shipOwnerID = self.GetShell().GetItem().ownerID
        if shipOwnerID == eve.session.charid:
            self.viewOnly = 0
        elif eve.session.corprole & role == role:
            self.viewOnly = 0
        else:
            self.viewOnly = 1



    def SetDivisionalHangarNames(self, divisions):
        for i in xrange(1, 5):
            self.sr.maintabs.sr.Get('%s%s_tab' % (mls.UI_GENERIC_DIVISION, i), None).SetLabel(divisions[i])

        for i in xrange(5, 8):
            self.sr.subtabs.sr.Get('%s%s_tab' % (mls.UI_GENERIC_DIVISION, i), None).SetLabel(divisions[i])




    def DropInDivision1(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagHangar)



    def DropInDivision2(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG2)



    def DropInDivision3(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG3)



    def DropInDivision4(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG4)



    def DropInDivision5(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG5)



    def DropInDivision6(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG6)



    def DropInDivision7(self, dragObj, nodes):
        self.AddWithFlag(nodes, const.flagCorpSAG7)



    def AddWithFlag(self, nodes, flag):
        if nodes is None:
            return 
        itemlist = [ node.rec for node in nodes if node.__guid__ in ('xtriui.InvItem', 'listentry.InvItem') ]
        if not len(itemlist):
            return 
        itemsLocation = itemlist[0].locationID
        if self.oneWay and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        if len(itemlist) == 1:
            qty = itemlist[0].stacksize
            if uicore.uilib.Key(uiconst.VK_SHIFT) and qty > 1:
                ret = uix.QtyPopup(qty, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
                if ret is None:
                    return 
                qty = ret['qty']
            return self.GetShell().Add(itemlist[0].itemID, itemsLocation, qty=qty, flag=flag)
        return self.GetShell().MultiAdd([ item.itemID for item in itemlist ], itemsLocation, flag=flag)



    def Load(self, args):
        log.LogInfo('Load', args)
        flagByTab = {'division1': const.flagHangar,
         'division2': const.flagCorpSAG2,
         'division3': const.flagCorpSAG3,
         'division4': const.flagCorpSAG4,
         'division5': const.flagCorpSAG5,
         'division6': const.flagCorpSAG6,
         'division7': const.flagCorpSAG7}
        if flagByTab.has_key(args):
            self.locationFlag = flagByTab[args]
            self.Refresh()
        else:
            log.LogError('What corp hangar view is', args)



    def CheckRoles(self, flag):
        if self.rolesByFlag.has_key(flag):
            role = self.rolesByFlag[flag][0]
            if eve.session.corprole & role == role:
                return 1
        return 0



    def List(self):
        self.SetAccess()
        if self.CheckRoles(self.locationFlag):
            self.noAccessMsg = None
            res = form.VirtualInvWindow.List(self)
            self.SetHint()
            return res
        else:
            self.noAccessMsg = mls.UI_STATION_HINT1
            self.SetHint(self.noAccessMsg)
            return []



    def SetHint(self, hintstr = None):
        if self is None or self.destroyed:
            return 
        self.hintText = hintstr
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def GetCaption(self, compact = 0):
        hint = ''
        if self.rolesByFlag.has_key(self.locationFlag):
            roles = self.rolesByFlag[self.locationFlag]
            role = eve.session.corprole
            canQuery = role & roles[0] == roles[0]
            canTake = role & roles[1] == roles[1]
            shipOwnerID = None
            if getattr(self, 'id', None):
                if self.scope in sm.GetService('gameui').GetCurrentScope():
                    shipOwnerID = self.GetShell().GetItem().ownerID
                else:
                    log.LogInfo('FIX CODE GetCaption')
            if shipOwnerID == eve.session.charid:
                canQuery = True
                canTake = True
            if canQuery and canTake:
                hint = '- %s' % mls.UI_SHARED_FULLACCESS
            elif canQuery:
                hint = '- %s' % mls.UI_GENERIC_READONLY
            elif canTake:
                hint = ' - %s' % mls.UI_STATION_CANTAKENOTVIEW
            hint = ' - %s' % mls.UI_GENERIC_ACCESSDENIED
        displayName = self.displayName
        if compact:
            displayName = displayName[0]
        if self.noAccessMsg == None:
            if self.quickFilterInput:
                total = self.totalCount
                total = total or '0'
                return '%s [%s/%s] %s' % (displayName,
                 len(filter(None, self.items)),
                 total,
                 hint)
            else:
                return '%s [%s] %s' % (displayName, len(filter(None, self.items)), hint)
        else:
            return '%s %s' % (displayName, hint)



    def InitHangars(self):
        hangars = {}
        try:
            corpMemberIDs = sm.GetService('corp').GetMemberIDs()
            if self.allHangars is not None:
                offices = sm.GetService('corp').GetOffices()
                owners = {}
                for charID in corpMemberIDs:
                    owners[charID] = None

                for each in offices:
                    owners[each.corporationID] = None

                owners = owners.keys()
                cfg.eveowners.Prime(owners)
                for ownerid in owners:
                    owner = cfg.eveowners.Get(ownerid)
                    if ownerid in corpMemberIDs:
                        hangars[(ownerid, ownerid)] = '%s - %s' % (owner.name, mls.UI_STATION_MEMBERSHANGAR)
                    elif owner.typeID == const.typeCorporation:
                        hangars[(ownerid, ownerid)] = '%s - %s' % (owner.name, mls.UI_STATION_OFFICEJUNK)
                    else:
                        hangars[(ownerid, ownerid)] = '%s - %s' % (owner.name, mls.UI_STATION_GUESTHANGAR)

                bListedOutOfficeFolder = 0
                for each in offices:
                    if each.corporationID == eve.session.corpid:
                        continue
                    if bListedOutOfficeFolder == 0:
                        folder = eve.GetInventoryFromId(each.officeFolderID)
                        folder.List()
                        bListedOutOfficeFolder = 1
                    hangars[(each.itemID, each.corporationID)] = '%s - %s' % (cfg.eveowners.Get(each.corporationID).name, mls.UI_GENERIC_OFFICE)

            else:
                cfg.eveowners.Prime(corpMemberIDs)
                for charID in corpMemberIDs:
                    hangars[(charID, charID)] = '%s - %s' % (cfg.eveowners.Get(charID).name, mls.UI_STATION_MEMBERSHANGAR)


        finally:
            self.hangars = hangars




    def ShowHangars(self, *etc):
        try:
            if session.corprole & const.corpRoleSecurityOfficer != const.corpRoleSecurityOfficer:
                raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED13})
            while self.hangars is None:
                blue.pyos.synchro.Sleep(500)

            memberHangars = []
            for each in self.hangars.iteritems():
                hangarName = each[1]
                hangarOwnerTuple = each[0]
                if hangarOwnerTuple[0] == session.charid:
                    continue
                memberHangars.append((hangarName, hangarOwnerTuple))

            ret = uix.ListWnd(memberHangars, 'generic', mls.UI_STATION_SELECTHANGAR, None, 1)
            if ret:
                if ret[1][0] == ret[1][1]:
                    wnd = sm.GetService('window').GetWindow('corpMember_%s' % ret[0])
                    if wnd is not None and not wnd.destroyed:
                        wnd.Maximize()
                    else:
                        sm.GetService('window').GetWindow('corpMember_%s' % ret[0], create=1, maximize=1, decoClass=CorpMemberHangar, id_=ret[1][0], ownerID=ret[1][1])
                else:
                    wnd = sm.GetService('window').GetWindow('spyHangar_%s_%s' % (ret[1][0], ret[1][1]))
                    if wnd is not None and not wnd.destroyed:
                        wnd.Maximize()
                    else:
                        sm.GetService('window').GetWindow('spyHangar_%s_%s' % (ret[1][0], ret[1][1]), create=1, maximize=1, decoClass=SpyHangar, id_=ret[1][0], ownerID=ret[1][1])

        finally:
            pass




    def UnrentOffice(self, *args):
        inv = self.GetShell()
        asked = 0
        if inv and len([ item for item in inv.List() if item.ownerID == eve.session.corpid ]):
            asked = 1
            if eve.Message('crpUnrentOfficeWithContent', {}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        if not asked:
            if eve.Message('crpUnrentOffice', {}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        corpStationMgr.CancelRentOfOffice()



    def DoBallRemove(self, ball, slimItem, terminal):
        if not self or self.destroyed:
            return 
        if slimItem.itemID == self.id:
            uthread.new(self.CloseX)



    def DoBallClear(self, solitem):
        if not self or self.destroyed:
            return 
        if eve.session.shipid != self.id:
            uthread.new(self.CloseX)



    def IsLocatedIn(self, rec):
        return rec.locationID == self.id and (rec.ownerID == eve.session.corpid or eve.session.solarsystemid and rec.ownerID == sm.GetService('michelle').GetBallpark().slimItems[self.id].ownerID and self.CheckRoles(rec.flagID))



    def IsMine(self, rec):
        return rec.locationID == self.id and (rec.ownerID == eve.session.corpid or eve.session.solarsystemid and rec.ownerID == sm.GetService('michelle').GetBallpark().slimItems[self.id].ownerID and rec.flagID == self.locationFlag and self.CheckRoles(rec.flagID))



    def GetShell(self):
        return eve.GetInventoryFromId(self.id)



    def OnItemDropBookmark(self, node):
        return True




class CorpHangarArray(CorpHangar):
    __guid__ = 'form.CorpHangarArray'

    def ApplyAttributes(self, attributes):
        form.CorpHangar.ApplyAttributes(self, attributes)
        self.scope = 'inflight'
        self.hasCapacity = 1



    def GetCapacity(self):
        return self.GetShell().GetCapacity()



    def OnItemDropBookmark(self, node):
        return True




class ShipCorpHangars(CorpHangar):
    __guid__ = 'form.ShipCorpHangars'

    def ApplyAttributes(self, attributes):
        self.scope = 'station_inflight'
        attributes.hasCapacity = True
        form.CorpHangar.ApplyAttributes(self, attributes)



    def Startup(self, officeID, name = '', hasCapacity = 0, locationFlag = None, isOffice = False):
        CorpHangar.Startup(self, officeID, hasCapacity, locationFlag, isOffice=False)
        self.corpID = self.GetCorpIDOfShipHangar()
        if self.id != session.shipid:
            self.scope = ['station', 'inflight'][(eve.session.stationid is None)]



    def GetCorpIDOfShipHangar(self):
        if eve.session.solarsystemid:
            return sm.GetService('michelle').GetBallpark().slimItems[self.id].corpID
        if eve.session.stationid:
            if util.IsCorporation(self.ownerID):
                return self.ownerID
            return eve.session.corpid
        raise RuntimeError('Session has neither stationid nor locationid')



    def GetCapacity(self):
        return self.GetShell().GetCapacity(flag=None, flags=self.flagsList)



    def List(self):
        shipOwnerID = None
        if getattr(self, 'id', None):
            shipOwnerID = self.GetShell().GetItem().ownerID
            if not util.IsCorporation(shipOwnerID):
                self.ownerID = self.GetShell().GetItem(force=True).ownerID
                self.corpID = self.GetCorpIDOfShipHangar()
        return CorpHangar.List(self)



    def CheckRoles(self, flag):
        if self.ownerID == eve.session.charid:
            return 1
        return CorpHangar.CheckRoles(self, flag)



    def IsLocatedIn(self, rec):
        return rec.locationID == self.id and rec.ownerID in (self.ownerID, self.corpID) and self.CheckRoles(rec.flagID)



    def IsMine(self, rec):
        return rec.locationID == self.id and rec.ownerID in (self.ownerID, self.corpID) and rec.flagID == self.locationFlag and self.CheckRoles(rec.flagID)



    def SetDivisionalHangarNames(self, divisions):
        if self.GetCorpIDOfShipHangar() != session.corpid:
            divisions = {1: mls.UI_CORP_DIVISION_FIRSTDIVISION,
             2: mls.UI_CORP_DIVISION_SECONDDIVISION,
             3: mls.UI_CORP_DIVISION_THIRDDIVISION,
             4: mls.UI_CORP_DIVISION_FOURTHDIVISION,
             5: mls.UI_CORP_DIVISION_FIFTHDIVISION,
             6: mls.UI_CORP_DIVISION_SIXTHDIVISION,
             7: mls.UI_CORP_DIVISION_SEVENTHDIVISION}
        CorpHangar.SetDivisionalHangarNames(self, divisions)




class CorpMemberHangar(form.VirtualInvWindow):
    __guid__ = 'form.CorpMemberHangar'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id_ = attributes.id_
        ownerID = attributes.ownerID
        self.scope = 'station'
        self.itemID = eve.session.stationid
        self.oneWay = 1
        self.viewOnly = 1
        self.locationFlag = const.flagHangar
        self.Startup(id_, ownerID)



    def Startup(self, id_, ownerID):
        self.id = id_
        self.ownerID = ownerID
        name = cfg.eveowners.Get(ownerID).name
        self.displayName = mls.UI_SHARED_HANGAR_NAME % {'name': name}
        form.VirtualInvWindow.Startup(self)
        self.state = uiconst.UI_NORMAL
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.ownerID))



    def Refresh(self):
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.ownerID))
        form.VirtualInvWindow.Refresh(self)



    def DoGetShell(self):
        return eve.GetInventory(const.containerHangar, self.id)



    def GetContainerArgs(self):
        return (const.containerHangar, self.id)



    def IsMine(self, item):
        return item.flagID == const.flagHangar and item.locationID == eve.session.stationid and item.ownerID == self.ownerID




class CorpMarketHangar(form.VirtualInvWindow):
    __guid__ = 'form.CorpMarketHangar'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        self.scope = 'station'
        self.itemID = eve.session.stationid
        self.oneWay = 1
        self.indexID = 'Items'
        name = cfg.eveowners.Get(eve.session.corpid).ownerName
        self.displayName = mls.UI_STATION_DELIVERIES_NAME % {'name': name}
        self.locationFlag = const.flagCorpMarket
        self.Startup()



    def DoGetShell(self):
        return eve.GetInventory(const.containerCorpMarket, eve.session.corpid)



    def GetContainerArgs(self):
        return (const.containerCorpMarket, eve.session.corpid)



    def IsMine(self, item):
        return item.flagID == const.flagCorpMarket and item.locationID == eve.session.stationid and item.ownerID == eve.session.corpid



exports = {'form.ItemHangar': ItemHangar,
 'form.ShipHangar': ShipHangar,
 'form.CorpHangar': CorpHangar,
 'form.CorpMemberHangar': CorpMemberHangar,
 'form.SpyHangar': SpyHangar,
 'form.ShipCorpHangars': ShipCorpHangars}

