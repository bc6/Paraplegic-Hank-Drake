import blue
import uix
import uiconst
import uthread
import util
import uicls
import listentry
import service
import menu
import contractscommon as cc
from contractutils import GetContractIcon, GetContractTitle, GetContractTimeLeftText, FmtISKWithDescription, GetContractTypeText, GetCurrentBid, CutAt
SECURITY_TEXT = {const.securityClassZeroSec: '<color=0xffdd0000>%s</color>' % mls.UI_GENERIC_NULLSEC,
 const.securityClassLowSec: '<color=0xffbbbb00>%s</color>' % mls.UI_GENERIC_LOWSEC,
 const.securityClassHighSec: '<color=0xff00bb00>%s</color>' % mls.UI_GENERIC_HIGHSEC}

class ContractEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.ContractEntry'

    def init(self):
        self.sr.selection = None
        self.sr.hilite = None
        self.OnSelectCallback = None



    def GetMenu(self):
        m = []
        c = self.sr.node.contract
        node = self.sr.node
        m.append((mls.UI_CONTRACTS_VIEWCONTRACT, self.ViewContract, (node,)))
        if c.startSolarSystemID and c.startSolarSystemID != eve.session.solarsystemid2:
            m.append((mls.UI_CMD_SHOWROUTE, self.ShowRoute, (node,)))
        if c.startStationID:
            typeID = sm.GetService('ui').GetStation(c.startStationID).stationTypeID
            m += [(mls.UI_CONTRACTS_PICKUPSTATION, ('isDynamic', sm.GetService('menu').CelestialMenu, (c.startStationID,
                None,
                None,
                0,
                typeID)))]
        if c.endStationID and c.endStationID != c.startStationID:
            typeID = sm.GetService('ui').GetStation(c.endStationID).stationTypeID
            m += [(mls.UI_CONTRACTS_DROPOFFSTATION, ('isDynamic', sm.GetService('menu').CelestialMenu, (c.endStationID,
                None,
                None,
                0,
                typeID)))]
        if c.type == const.conTypeAuction and c.issuerID != eve.session.charid and c.status == const.conStatusOutstanding and c.dateExpired > blue.os.GetTime():
            m.append((mls.UI_CONTRACTS_PLACEBID, self.PlaceBid, (node,)))
        if self.sr.node.Get('canDismiss', False):
            m.append((mls.UI_CONTRACTS_DISMISS, self.Dismiss, (node,)))
        if self.sr.node.Get('canGetItems', False):
            m.append((mls.UI_CONTRACTS_GETITEMS, self.GetItems, (node,)))
        if self.sr.node.Get('canGetMoney', False):
            m.append((mls.UI_CONTRACTS_GETMONEY, self.GetMoney, (node,)))
        if self.sr.node.Get('canIgnore', True) and c.issuerID != eve.session.charid:
            m.append((mls.UI_CONTRACTS_IGNOREFROMTHIS, self.AddIgnore, (node,)))
        typeID = self.sr.node.Get('typeID', None)
        if typeID and self.sr.node.contract.type != const.conTypeCourier:
            m.append(None)
            m.append((mls.UI_CMD_SHOWINFO, sm.GetService('info').ShowInfo, (typeID,)))
            if cfg.invtypes.Get(typeID).marketGroupID is not None:
                m.append((mls.UI_CMD_VIEWMARKETDETAILS, sm.GetService('marketutils').ShowMarketDetails, (typeID, None)))
        m.append(None)
        if c.issuerID == eve.session.charid:
            m.append((mls.UI_CONTRACTS_DELETE, self.Delete, (node,)))
        if session.role & service.ROLE_GML > 0:
            m.append(('GM - contractID: %s' % node.contract.contractID, blue.pyos.SetClipboardData, (str(node.contract.contractID),)))
            m.append(('GM - issuerID: %s' % node.contract.issuerID, blue.pyos.SetClipboardData, (str(node.contract.issuerID),)))
        return m



    def NoEvent(self, *args):
        pass



    def FindMore(self, typeID, *args):
        sm.GetService('contracts').OpenAvailableTab(7, reset=True, typeID=typeID)



    def ViewContract(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('contracts').ShowContract(node.contract.contractID)



    def ShowRoute(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('map').OpenStarMap()
        sm.GetService('starmap').SetInterest(node.contract.startRegionID)
        sm.GetService('starmap').DrawRouteTo(node.contract.startSolarSystemID)



    def Delete(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('contracts').DeleteContract(node.contract.contractID)



    def PlaceBid(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').PlaceBid(node.contract.contractID):
            self.Reload()



    def Dismiss(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').DeleteNotification(node.contractID, node.Get('forCorp', False)):
            node.scroll.RemoveEntries([node])



    def GetItems(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').FinishAuction(node.contract.contractID, isIssuer=False):
            node.scroll.RemoveEntries([node])



    def GetMoney(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').FinishAuction(node.contract.contractID, isIssuer=True):
            node.scroll.RemoveEntries([node])



    def AddIgnore(self, node = None, *args):
        node = node if node != None else self.sr.node
        issuerID = node.contract.issuerID
        if node.contract.forCorp:
            issuerID = node.contract.issuerCorpID
        sm.GetService('contracts').AddIgnore(issuerID)



    def OnDblClick(self, *args):
        self.ViewContract(*args)



    def GetDragData(self, *args):
        if self and not self.destroyed:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)



    def OnSelect(self, *args):
        if getattr(self, 'OnSelectCallback', None):
            apply(self.OnSelectCallback, args)



    def _OnClose(self, *args):
        self.updatetimer = None



    def OnMouseEnter(self, *args):
        if self.sr.Get('hilite', None) is None:
            self.sr.hilite = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.Get('hilite', None):
            self.sr.hilite.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        self.OnSelect(self)



    def Reload(self, *args):
        contract = sm.GetService('contracts').GetContract(self.sr.node.contractID)
        self.sr.node.contract = contract.contract
        self.sr.node.contractItems = contract.items
        self.sr.node.bids = contract.bids
        self.Load(self.sr.node)




class ContractEntrySmall(ContractEntry):
    __guid__ = 'listentry.ContractEntrySmall'

    def Startup(self, *etc):
        self.sr.label = uicls.Label(text='', parent=self, left=5, state=uiconst.UI_DISABLED, color=None, singleline=1, align=uiconst.CENTERLEFT)
        self.sr.line = uicls.Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)
        uicls.Line(parent=self.sr.line, align=uiconst.TOALL)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))



    def Load(self, node):
        self.sr.node = node
        c = node.contract
        self.sr.node.contractID = c.contractID
        self.sr.node.solarSystemID = c.startSolarSystemID
        items = node.contractItems
        issuerID = [c.issuerID, c.issuerCorpID][(not not c.forCorp)]
        fromName = cfg.eveowners.Get(issuerID).ownerName
        toID = [c.acceptorID, c.assigneeID][(not c.acceptorID)]
        toName = cfg.eveowners.Get(toID).ownerName
        if toID == 0:
            toName = mls.UI_CONTRACTS_NONE
        name = GetContractTitle(c, items)
        if not node.Get('callerdefined', False):
            node.label = '%s<t>%s<t>%s<t>%s%s' % (name,
             GetContractTypeText(c.type),
             fromName,
             toName,
             node.Get('additionalColumns', ''))
        self.sr.label.text = self.sr.node.label = node.label
        self.OnSelectCallback = node.Get('callback', None)
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.Get('selected', 0)]
        self.state = uiconst.UI_NORMAL
        self.sr.claiming = 0
        self.sr.node.name = name
        self.hint = ''
        loc = ''
        if c.startSolarSystemID > 0:
            n = int(sm.GetService('pathfinder').GetJumpCountFromCurrent(c.startSolarSystemID))
            if c.startStationID == eve.session.stationid:
                jmps = mls.UI_GENERIC_CURRENTSTATION
            elif c.startSolarSystemID == eve.session.solarsystemid2:
                jmps = mls.UI_GENERIC_CURRENTSYSTEM
            elif n == 1:
                jmps = mls.UI_CONTRACTS_1_JUMP_AWAY
            else:
                jmps = mls.UI_CONTRACTS_NUM_JUMPS_AWAY % {'numJumps': n}
            loc = '%s (%s)' % (cfg.evelocations.Get(c.startSolarSystemID).name, jmps)
        self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_CONTRACTTYPE, GetContractTypeText(c.type))
        if c.title != '':
            self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_ISSUERDESC, c.title)
        self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_LOCATION, loc)
        if c.type in [const.conTypeAuction, const.conTypeItemExchange] and len(items) > 0:
            strItems = '<b>%s:</b><t>  ' % mls.UI_CONTRACTS_ITEMS
            itemsReq = '<b>%s:</b><t>  ' % mls.UI_CONTRACTS_REQUIREDITEMS
            numItems = 0
            numItemsReq = 0
            for e in items:
                if e.inCrate:
                    strItems += cfg.invtypes.Get(e.itemTypeID).name + ' x ' + str(max(1, e.quantity)) + ', '
                    numItems += 1
                else:
                    itemsReq += cfg.invtypes.Get(e.itemTypeID).name + ' x ' + str(max(1, e.quantity)) + ', '
                    numItemsReq += 1

            if numItems >= 2:
                strItems += mls.UI_GENERIC_MORE + '...'
            else:
                strItems = strItems[:-2]
            if numItemsReq >= 2:
                itemsReq += mls.UI_GENERIC_MORE + '...'
            else:
                itemsReq = itemsReq[:-2]
            if numItems == 0:
                strItems += '(%s)' % mls.UI_GENERIC_NONE
            self.hint += '%s<br>' % strItems
            if numItemsReq > 0:
                self.hint += '%s<br>' % itemsReq
            if numItems >= 2 or numItemsReq >= 2:
                self.hint += '%s<br>' % mls.UI_CONTRACTS_OPENFORITEMS
            if c.assigneeID > 0:
                self.hint += '<b>%s</b>' % mls.UI_CONTRACTS_THISISAPRIVATECONTRACT



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = 19
        return node.height




class ContractItemSelect(listentry.Item):
    __guid__ = 'listentry.ContractItemSelect'

    def init(self):
        self.sr.overlay = uicls.Container(name='overlay', align=uiconst.TOPLEFT, parent=self, height=1)
        self.sr.tlicon = None



    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        cbox = uicls.Checkbox(align=uiconst.TOPLEFT, pos=(6, 4, 0, 0), callback=self.CheckBoxChange)
        cbox.data = {}
        self.children.insert(0, cbox)
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_DISABLED



    def Load(self, args):
        listentry.Item.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data = {'key': data.cfgname,
         'retval': data.retval}
        self.sr.icon.left = 24
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        self.sr.techIcon.left = 24
        self.sr.icon.state = uiconst.UI_PICKCHILDREN
        self.sr.techIcon.state = uiconst.UI_PICKCHILDREN



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)



    def OnClick(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        lastSelected = self.sr.node.scroll.sr.lastSelected
        if lastSelected is None:
            shift = 0
        idx = self.sr.node.idx
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        isIt = not self.sr.checkbox.checked
        self.sr.checkbox.SetChecked(isIt)
        if shift > 0:
            r = [lastSelected, self.sr.node.idx]
            r.sort()
            for node in self.sr.node.scroll.GetNodes():
                if node.idx > r[0] and node.idx <= r[1]:
                    node.checked = isIt
                    d = {'retval': node.retval}
                    kv = util.KeyVal(data=d)
                    node.OnChange(kv)
                    if node.panel:
                        node.panel.sr.checkbox.SetChecked(isIt)

        self.sr.node.scroll.sr.lastSelected = idx



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 28
        return node.height



    def GetMenu(self):
        m = []
        if self.sr.node.quantity > 1:
            m.append((mls.UI_GENERIC_SPLITSTACK, self.SplitStack))
        m.extend(sm.GetService('menu').GetMenuFormItemIDTypeID(self.sr.node.itemID, self.sr.node.typeID))
        return m



    def SplitStack(self):
        maxQty = self.sr.node.quantity
        msg = mls.UI_GENERIC_HOWMANYITEMS
        ret = uix.QtyPopup(int(maxQty), 1, 1, msg)
        if ret:
            sm.GetService('contracts').SplitStack(self.sr.node.stationID, self.sr.node.itemID, ret['qty'], self.sr.node.forCorp, self.sr.node.flag)




class ContractEntrySearch(ContractEntry):
    __guid__ = 'listentry.ContractEntrySearch'
    iconSize = 32
    iconMargin = 2
    lineHeight = 10
    labelMargin = 6
    reqItemEntryHeight = 16
    entryHeight = 10

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.sr.line = uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.hilite = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height, width=5000, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.hilite.state = uiconst.UI_HIDDEN
        self.sr.contractParent = uicls.Container(parent=self, name='contractParent', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, padTop=2)
        self.sr.contractIconParent = uicls.Container(parent=self.sr.contractParent, name='contractIconParent', align=uiconst.TOLEFT, width=self.iconSize + 5)
        self.sr.techIcon = uicls.Icon(parent=self.sr.contractIconParent, pos=(2, 2, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.sr.icon = uicls.Icon(parent=self.sr.contractIconParent, pos=(2, 2, 32, 32), ignoreSize=True, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        subPar = uicls.Container(parent=self.sr.contractParent, name='contractLabelClipper', state=uiconst.UI_DISABLED, align=uiconst.TOALL, clipChildren=True, padLeft=2)
        self.sr.contractLabel = uicls.Label(parent=subPar, left=self.labelMargin, align=uiconst.TOTOP, autowidth=False, padRight=const.defaultPadding)



    def OnClick(self, *args):
        if self.sr.Get('selection', None) is None:
            self.sr.selection = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height - 3, width=5000, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.selection.state = uiconst.UI_DISABLED
        self.sr.node.scroll.SelectNode(self.sr.node)



    def OnMouseEnter(self, *args):
        if self.sr.Get('hilite', None) is None:
            self.sr.hilite = uicls.Fill(parent=self, align=uiconst.TOPLEFT, top=1, height=self.height - 3, width=5000, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.Get('hilite', None):
            self.sr.hilite.state = uiconst.UI_HIDDEN



    def Load(self, node):
        self.sr.node = node
        c = node.contract
        numJumps = node.numJumps
        self.sr.node.contractID = c.contractID
        self.sr.node.solarSystemID = c.startSolarSystemID
        self.sr.node.name = name = GetContractTitle(c, node.contractItems)
        if prefs.GetValue('contractsSimpleView', 0):
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.contractIconParent.width = 6
        else:
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.contractIconParent.width = self.iconSize + 5
        label = '<color=0xFFFFA600>%s</color>' % name
        if len(node.contractItems) == 1:
            item = node.contractItems[0]
            group = cfg.invtypes.Get(item.itemTypeID).Group()
            if group.categoryID == const.categoryBlueprint:
                if item.copy:
                    label += ' (%s)' % mls.UI_GENERIC_COPY.lower()
                else:
                    label += ' (%s)' % mls.UI_GENERIC_ORIGINAL.lower()
        if c.type == const.conTypeAuction:
            label += ' (%s)' % mls.UI_CONTRACTS_AUCTION.lower()
        self.sr.contractLabel.SetText(label)
        if c.type in [const.conTypeAuction, const.conTypeItemExchange] and len(node.contractItems) == 1:
            typeID = node.contractItems[0].itemTypeID
            self.sr.icon.LoadIconByTypeID(typeID=typeID, size=32, ignoreSize=True, isCopy=getattr(node.contractItems[0], 'copy', False))
            if self.sr.icon.state != uiconst.UI_HIDDEN:
                uix.GetTechLevelIcon(self.sr.techIcon, 1, typeID)
        else:
            self.sr.icon.LoadIcon(GetContractIcon(node.contract.type), ignoreSize=True)
            self.sr.techIcon.state = uiconst.UI_HIDDEN
        numJumpsTxt = ''
        if numJumps == 0:
            if c.startStationID == session.stationid:
                numJumpsTxt = mls.UI_GENERIC_CURRENTSTATION
            elif c.startSolarSystemID == session.solarsystemid2:
                numJumpsTxt = mls.UI_GENERIC_CURRENTSYSTEM
        elif numJumps == 1:
            numJumpsTxt = mls.UI_CONTRACTS_1_JUMP_AWAY
        else:
            numJumpsTxt = mls.UI_CONTRACTS_NUM_JUMPS_AWAY % {'numJumps': numJumps}
        if int(node.numJumps) > cc.NUMJUMPS_UNREACHABLE:
            numJumpsTxt = '<color=0xffff6666>%s</color>' % mls.UI_GENERIC_UNREACHABLE.upper()
        self.sr.jumpsLabel.SetText(numJumpsTxt)
        self.sr.timeLeftLabel.SetText(GetContractTimeLeftText(c))
        self.SetHint(node, label)
        if self.sr.Get('selection', None):
            self.sr.selection.state = uiconst.UI_HIDDEN



    def MakeTextLabel(self, name):
        subPar = uicls.Container(name='%sParent' % name, parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        label = uicls.Label(parent=subPar, name='%sLabel' % name, left=self.labelMargin, align=uiconst.TOLEFT, padTop=2)
        subPar.sr.label = label
        setattr(self.sr, '%sLabel' % name, label)



    def GetLocationText(self, solarSystemID, regionID):
        solarSystemName = cfg.evelocations.Get(solarSystemID).name
        dot = sm.GetService('contracts').GetSystemSecurityDot(solarSystemID)
        txt = '%s %s' % (dot, solarSystemName)
        if regionID and regionID != session.regionid:
            txt += '<br><color=0xffff6666>  %s</color>' % cfg.evelocations.Get(regionID).name
        return txt



    def GetMenu(self):
        m = ContractEntry.GetMenu(self)
        m += [(mls.UI_CONTRACTS_FINDRELATED, ('isDynamic', sm.GetService('contracts').GetRelatedMenu, (self.sr.node.contract, self.sr.node.Get('typeID', None), False)))]
        return m



    def SetHint(self, node, label):
        self.sr.node = node
        c = node.contract
        loc = '%s - %s (%s)' % (cfg.evelocations.Get(c.startSolarSystemID).name, cfg.evelocations.Get(c.startRegionID).name, node.numJumps)
        self.hint = ''
        self.hint += '<b>%s</b><br>' % label
        self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_CONTRACTTYPE, GetContractTypeText(c.type))
        self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_LOCATION, loc)
        issuerID = c.issuerCorpID if c.forCorp else c.issuerID
        issuer = cfg.eveowners.Get(issuerID)
        self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_ISSUER, issuer.name)
        if c.type in [const.conTypeAuction, const.conTypeItemExchange] and len(node.contractItems) > 0:
            items = '<b>%s:</b><t>  ' % mls.UI_CONTRACTS_ITEMS
            itemsReq = '<b>%s:</b><t>  ' % mls.UI_CONTRACTS_REQUIREDITEMS
            numItems = 0
            numItemsReq = 0
            for e in node.contractItems:
                if e.inCrate:
                    items += cfg.invtypes.Get(e.itemTypeID).name + ' x ' + str(max(1, e.quantity)) + ', '
                    numItems += 1
                else:
                    itemsReq += cfg.invtypes.Get(e.itemTypeID).name + ' x ' + str(max(1, e.quantity)) + ', '
                    numItemsReq += 1

            if numItems >= 2:
                items += mls.UI_GENERIC_MORE + '...'
            else:
                items = items[:-2]
            if numItemsReq >= 2:
                itemsReq += mls.UI_GENERIC_MORE + '...'
            else:
                itemsReq = itemsReq[:-2]
            if numItems == 0:
                items += '(%s)' % mls.UI_GENERIC_NONE
            self.hint += '%s<br>' % items
            if numItemsReq > 0:
                self.hint += '%s<br>' % itemsReq
            if numItems >= 2 or numItemsReq >= 2:
                self.hint += '%s<br>' % mls.UI_CONTRACTS_OPENFORITEMS
        if c.title != '':
            self.hint += '<b>%s:</b><t>%s<br>' % (mls.UI_CONTRACTS_ISSUERDESC, c.title)



    def OnColumnResize(self, newCols):
        for (container, width,) in zip(self.children[2:], newCols):
            container.width = width
            label = container.sr.label
            if label and label != self.sr.contractLabel:
                label.width = width - 14




    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = [37, 19][prefs.GetValue('contractsSimpleView', 0)]
        return node.height




class ContractEntrySearchItemExchange(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchItemExchange'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('location')
        self.MakeTextLabel('price')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')



    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        p = c.price
        self.sr.locationLabel.text = self.GetLocationText(c.startSolarSystemID, c.startRegionID)
        if p == 0 and c.reward > 0:
            txt = '<color=0xff999999>-%s</color>' % FmtISKWithDescription(c.reward, True)
        else:
            txt = '<color=white>%s</color>' % FmtISKWithDescription(p, True)
        self.sr.priceLabel.SetText(txt)
        if mls.UI_CONTRACTS_WANTTOBUY not in self.sr.contractLabel.text:
            if len([ e for e in node.contractItems if not e.inCrate ]) >= 1:
                self.sr.priceLabel.text += '<br>[%s]' % mls.GENERIC_ITEMS
        if c.type == const.conTypeAuction:
            self.sr.priceLabel.text = '<color=white>%s</color>' % FmtISKWithDescription(GetCurrentBid(c, node.bids), True)
            if c.collateral:
                self.sr.priceLabel.text += '<br>(%s)' % FmtISKWithDescription(c.collateral, True)
            else:
                self.sr.priceLabel.text += '<br>(%s)' % mls.UI_CONTRACTS_NOBUYOUT
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % util.FmtDate(node.dateIssued, 'ss')




class ContractEntrySearchAuction(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchAuction'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('location')
        self.MakeTextLabel('currentBid')
        self.MakeTextLabel('buyout')
        self.MakeTextLabel('bids')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')



    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        p = c.price
        self.sr.locationLabel.text = self.GetLocationText(c.startSolarSystemID, c.startRegionID)
        self.sr.currentBidLabel.text = '<color=white>%s</color>' % FmtISKWithDescription(GetCurrentBid(c, node.bids), True)
        self.sr.buyoutLabel.text = '%s' % ['<color=0xff999999>' + mls.UI_CONTRACTS_NONE + '</color>', '<color=white>' + FmtISKWithDescription(c.collateral, True) + '</color>'][(c.collateral > 0)]
        self.sr.bidsLabel.text = '%s' % node.searchresult.numBids
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % util.FmtDate(node.dateIssued, 'ss')




class ContractEntrySearchCourier(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchCourier'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('to')
        self.MakeTextLabel('volume')
        self.MakeTextLabel('reward')
        self.MakeTextLabel('collateral')
        self.MakeTextLabel('route')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')



    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        self.sr.contractLabel.text = '<color=0xFFFFA600>%s</color>' % self.GetLocationText(c.startSolarSystemID, c.startRegionID)
        self.sr.toLabel.text = '<color=0xFFFFA600>%s</color>' % self.GetLocationText(c.endSolarSystemID, None)
        routeLength = node.routeLength
        self.sr.volumeLabel.text = '%s m\xb3' % util.FmtAmt(c.volume, showFraction=0 if c.volume > 10 else 2)
        self.sr.rewardLabel.text = '<color=white>%s</color>' % [mls.UI_CONTRACTS_NONE, FmtISKWithDescription(c.reward, True)][(c.reward > 0)]
        self.sr.collateralLabel.text = '<color=white>%s</color>' % [mls.UI_CONTRACTS_NONE, FmtISKWithDescription(c.collateral, True)][(c.collateral > 0)]
        if int(routeLength) > cc.NUMJUMPS_UNREACHABLE:
            numJumpsTxt = '<color=0xffff6666>%s</color>' % mls.UI_GENERIC_UNREACHABLE.upper()
        elif routeLength == 0:
            numJumpsTxt = mls.UI_CONTRACTS_SAMESYSTEM
        elif routeLength == 1:
            numJumpsTxt = mls.UI_CONTRACTS_NEXTSYSTEM
        else:
            numJumpsTxt = mls.UI_CONTRACTS_NUM_JUMPS % {'numJumps': routeLength}
        self.sr.routeLabel.text = '<color=white>%s</color>' % numJumpsTxt
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % util.FmtDate(node.dateIssued, 'ss')




