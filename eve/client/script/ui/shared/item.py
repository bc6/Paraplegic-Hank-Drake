import uix
import uiutil
import xtriui
import util
import uiconst
import uicls
import log
import trinity

class InvItem(uicls.Container):
    __guid__ = 'xtriui.InvItem'
    __groups__ = []
    __categories__ = []
    __notifyevents__ = ['ProcessSessionChange', 'OnSessionChanged', 'OnLockedItemChangeUI']
    default_name = 'InvItem'
    default_left = 64
    default_top = 160
    default_width = 64
    default_height = 88
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.ConstructLayout()



    def ConstructLayout(self):
        dot = uicls.Sprite(parent=self, name='dot', pos=(0, 0, 64, 64), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/shapeDot.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.sr.dot = dot
        topoverlays = uicls.Container(parent=self, name='topoverlays', state=uiconst.UI_PICKCHILDREN)
        self.sr.topoverlays = topoverlays
        align = uicls.Container(parent=topoverlays, name='align', width=32, padBottom=25, align=uiconst.TORIGHT, state=uiconst.UI_PICKCHILDREN)
        qtypar = uicls.Container(parent=align, name='qtypar', pos=(0, 0, 0, 11), align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN)
        underlay = uicls.Frame(parent=qtypar, name='underlay', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/InvItem/quantityUnderlay.png', cornerSize=2, offset=0, color=util.Color.BLACK)
        flags = uicls.Container(parent=align, name='flags', pos=(0, 0, 0, 16), align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, padding=(0, 0, 0, 0))
        self.sr.flags = flags
        slotSize = uicls.Icon(parent=flags, name='slotSize', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, hint=mls.UI_SHARED_FITTINGCONSTRAINTS, state=uiconst.UI_HIDDEN)
        self.sr.slotsize_icon = slotSize
        ammoSize = uicls.Sprite(parent=flags, name='ammoSize', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/InvItem/ammoSize.png', hint=mls.UI_SHARED_AMMOSIZECONSTRAINT, state=uiconst.UI_HIDDEN, rectWidth=16, rectHeight=16)
        self.sr.ammosize_icon = ammoSize
        contrabandIcon = uicls.Sprite(parent=flags, name='contrabandIcon', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/InvItem/contrabandIcon.png', hint=mls.UI_SHARED_THISITEMISCONTRABAND, state=uiconst.UI_HIDDEN)
        self.sr.contraband_icon = contrabandIcon
        self.sr.icon = uicls.Icon(parent=self, name='pic', pos=(0, 0, 64, 64), state=uiconst.UI_DISABLED)
        shadow = uicls.Sprite(parent=self, name='shadow', pos=(-13, -6, 90, 90), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/shapeShadow.png')
        self.sr.shadow = shadow
        self.sr.temp = uicls.Container(parent=self, name='temp', state=uiconst.UI_DISABLED)



    def ProcessSessionChange(self, isRemote, session, change):
        if not self.destroyed and self.sr and self.sr.node:
            if 'shipid' in change and getattr(self, 'isShip', 0) and self and not self.destroyed:
                self.Load(self.sr.node)



    def OnSessionChanged(self, isRemote, session, change):
        if not self.destroyed and self.sr and self.sr.node:
            if 'shipid' in change and getattr(self, 'isShip', 0) and self and not self.destroyed:
                self.Load(self.sr.node)



    def OnLockedItemChangeUI(self, itemID, ownerID, locationID, change):
        if not self.destroyed and self.sr.node:
            if itemID == self.id:
                item = None
                if self.rec:
                    item = self.rec
                elif self.sr.node.item:
                    item = self.sr.node.item
                if item is None:
                    log.LogInfo('Lock issue item is None')
                else:
                    locked = item.flagID == const.flagLocked or sm.GetService('corp').IsItemLocked(item)
                    log.LogInfo('Locked:', locked, 'item:', item)
                    self.SetLockState(locked)



    def init(self):
        self.typeID = None
        self.subTypeID = None
        self.id = None
        self.powerType = None
        self.sr.quantity_label = uicls.Label(text='', parent=uiutil.GetChild(self, 'qtypar'), left=4, top=1, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, idx=0, singleline=1)
        self.sr.name_label = self.sr.label = uicls.Label(text='', parent=self, left=0, top=66, width=64, autowidth=False, state=uiconst.UI_DISABLED, idx=3, maxlines=2)
        self.sr.icon = uiutil.GetChild(self, 'pic')
        self.sr.contraband_icon = uiutil.GetChild(self, 'contrabandIcon')
        self.sr.contraband_icon.sr.hint = mls.UI_SHARED_THISITEMISCONTRABAND
        self.sr.contraband_icon.state = uiconst.UI_HIDDEN
        self.sr.slotsize_icon = uiutil.GetChild(self, 'slotSize')
        self.sr.slotsize_icon.sr.hint = mls.UI_SHARED_FITTINGCONSTRAINTS
        self.sr.slotsize_icon.state = uiconst.UI_HIDDEN
        self.sr.temp = uiutil.GetChild(self, 'temp')
        self.sr.ammosize_icon = uiutil.GetChild(self, 'ammoSize')
        self.sr.ammosize_icon.sr.hint = mls.UI_SHARED_AMMOSIZECONSTRAINT
        self.sr.ammosize_icon.state = uiconst.UI_HIDDEN
        self.sr.topoverlays = uiutil.GetChild(self, 'topoverlays')
        self.sr.flags = uiutil.GetChild(self, 'flags')
        self.sr.dot = uiutil.GetChild(self, 'dot')
        self.sr.shadow = uiutil.GetChild(self, 'shadow')
        self.sr.node = None
        self.sr.tlicon = None
        self.sr.selection = None
        self.sr.hilite = None
        self.highlightable = True
        sm.RegisterNotify(self)



    def SetState(self, state):
        self.viewOnly = self.Draggable_blockDrag = state
        if self.sr.node:
            self.sr.node.viewOnly = self.sr.node.Draggable_blockDrag = state



    def SetLockState(self, locked):
        self.SetState(min(1, locked))
        self.sr.icon.color.a = [1.0, 0.25][min(1, locked)]



    def Reset(self):
        self.viewOnly = 0
        self.subTypeID = None
        self.sr.ammosize_icon.state = uiconst.UI_HIDDEN
        self.sr.slotsize_icon.state = uiconst.UI_HIDDEN
        self.sr.icon.state = uiconst.UI_HIDDEN



    def PreLoad(node):
        if node.viewMode in ('list', 'details'):
            label = uix.GetItemLabel(node.item, node)



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.node.__guid__ = self.__guid__
        self.sr.node.itemID = node.item.itemID
        self.id = node.item.itemID
        self.rec = node.item
        self.typeID = node.item.typeID
        self.isShip = self.rec.categoryID == const.categoryShip and self.rec.singleton
        self.isStation = self.rec.categoryID == const.categoryStation and self.rec.groupID == const.groupStation
        self.isContainer = self.rec.groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer) and self.rec.singleton
        self.isHardware = node.invtype.Group().Category().IsHardware()
        self.sr.node.isBlueprint = node.invtype.Group().categoryID == const.categoryBlueprint
        if self.sr.node.isBlueprint:
            self.sr.node.isCopy = self.sr.node.isBlueprint and self.rec.singleton == const.singletonBlueprintCopy
        if self.sr.node is None:
            return 
        self.sr.temp.Flush()
        self.Reset()
        self.name = uix.GetItemName(node.item, self.sr.node)
        self.quantity = self.rec.stacksize
        listFlag = self.sr.node.viewMode in ('list', 'details')
        if eve.session.shipid == self.sr.node.item.itemID:
            left = [-7, -4][listFlag]
            top = [-7, 1][listFlag]
            uicls.Frame(parent=self.sr.temp, weight=2, idx=0, padding=(left,
             top,
             left,
             top))
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        attribs = node.Get('godmaattribs', {})
        self.powerType = None
        if self.isHardware:
            if self.sr.node.viewMode != 'list':
                if attribs.has_key(const.attributeChargeSize):
                    self.sr.ammosize_icon.rectLeft = [0,
                     16,
                     32,
                     48,
                     64][(int(attribs[const.attributeChargeSize]) - 1)]
                    self.sr.ammosize_icon.state = uiconst.UI_DISABLED
                elif attribs.has_key(const.attributeRigSize):
                    self.sr.ammosize_icon.rectLeft = [0,
                     16,
                     32,
                     48,
                     64][(int(attribs[const.attributeRigSize]) - 1)]
                    self.sr.ammosize_icon.state = uiconst.UI_DISABLED
            for effect in cfg.dgmtypeeffects.get(self.rec.typeID, []):
                if effect.effectID in (const.effectRigSlot,
                 const.effectHiPower,
                 const.effectMedPower,
                 const.effectLoPower):
                    if self.sr.node.viewMode != 'list':
                        effinfo = cfg.dgmeffects.Get(effect.effectID)
                        iconNo = {const.effectRigSlot: 'ui_38_16_124',
                         const.effectHiPower: 'ui_38_16_123',
                         const.effectMedPower: 'ui_38_16_122',
                         const.effectLoPower: 'ui_38_16_121'}[effect.effectID]
                        self.sr.slotsize_icon.LoadIcon(iconNo, ignoreSize=True)
                        self.sr.slotsize_icon.state = uiconst.UI_DISABLED
                    self.powerType = effect.effectID
                    continue
                if self.sr.node.viewMode != 'list' and effect.effectID == const.effectSubSystem and const.attributeSubSystemSlot in attribs:
                    subsystemFlag = attribs.get(const.attributeSubSystemSlot, None)
                    iconNo = 'ui_38_16_42'
                    self.sr.slotsize_icon.LoadIcon(iconNo, ignoreSize=True)
                    self.sr.slotsize_icon.state = uiconst.UI_DISABLED

        elif self.rec.groupID == const.groupVoucher:
            if self.rec.typeID != const.typeBookmark:
                self.subTypeID = self.sr.node.voucher.GetTypeInfo()[1]
        elif self.rec.categoryID == const.categoryCharge and attribs.has_key(const.attributeChargeSize):
            self.sr.ammosize_icon.state = uiconst.UI_DISABLED
            self.sr.ammosize_icon.rectLeft = [0,
             16,
             32,
             48,
             64][(int(attribs[const.attributeChargeSize]) - 1)]
        self.sr.contraband_icon.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[(0 < len(self.sr.node.invtype.Illegality()) and self.sr.node.invtype.Illegality().get(sm.GetService('map').GetItem(eve.session.solarsystemid2).factionID, None) is not None)]
        if listFlag:
            self.sr.name_label.top = 4
            self.sr.name_label.width = uicore.desktop.width
        else:
            self.sr.name_label.top = 66
            self.sr.name_label.width = 64
        if self.sr.node.viewMode in ('icons', 'details'):
            if self.sr.node.viewMode == 'details':
                self.sr.name_label.left = 46
                self.sr.topoverlays.align = uiconst.RELATIVE
                self.sr.topoverlays.left = 5
                self.sr.topoverlays.top = 3
                self.sr.topoverlays.width = self.sr.topoverlays.height = 32
                self.sr.flags.top = 16
            else:
                self.sr.topoverlays.align = uiconst.TOALL
                self.sr.topoverlays.padLeft = 1
                self.sr.topoverlays.padTop = 2
                self.sr.topoverlays.padRight = 1
                self.sr.topoverlays.padBottom = 4
            self.sr.icon.LoadIconByTypeID(typeID=self.rec.typeID, ignoreSize=True, isCopy=self.sr.node.isBlueprint and self.sr.node.isCopy)
            if self.sr.node.viewMode == 'icons':
                self.sr.icon.SetSize(64, 64)
            else:
                self.sr.icon.SetSize(32, 32)
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.dot.state = uiconst.UI_DISABLED
            self.sr.shadow.state = uiconst.UI_DISABLED
        else:
            self.sr.ammosize_icon.state = uiconst.UI_HIDDEN
            self.sr.flags.top = 0
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.dot.state = uiconst.UI_HIDDEN
            self.sr.shadow.state = uiconst.UI_HIDDEN
            self.sr.name_label.left = 12
        self.UpdateLabel()
        self.LoadTechLevelIcon(node.item.typeID)
        locked = node.Get('locked', 0)
        viewOnly = node.Get('viewOnly', 0)
        self.SetLockState(locked)
        if not locked:
            self.SetState(viewOnly)
        if self.isStation:
            self.Draggable_blockDrag = 1
        elif node.Get('Draggable_blockDrag', None):
            self.Draggable_blockDrag = node.Draggable_blockDrag



    def LoadTechLevelIcon(self, typeID = None):
        offset = [-1, 0][(self.sr.node.viewMode == 'details')]
        tlicon = uix.GetTechLevelIcon(self.sr.tlicon, offset, typeID)
        if tlicon is not None and util.GetAttrs(tlicon, 'parent') is None:
            self.sr.tlicon = tlicon
            self.sr.topoverlays.children.insert(0, tlicon)



    def UpdateLabel(self, new = 0):
        label = uix.GetItemLabel(self.rec, self.sr.node, new)
        if not self.sr.quantity_label or self.sr.quantity_label.destroyed:
            return 
        if self.sr.node.viewMode in ('list', 'details'):
            self.sr.label.singleline = 1
            self.sr.label.text = label
            self.sr.quantity_label.parent.state = uiconst.UI_HIDDEN
        else:
            self.sr.label.singleline = 0
            self.sr.name_label.text = label
            if self.rec.singleton or self.rec.typeID in (const.typeBookmark,):
                self.sr.quantity_label.parent.state = uiconst.UI_HIDDEN
            else:
                self.sr.quantity_label.text = '%s' % uix.GetItemQty(self.sr.node, 'ss')
                self.sr.quantity_label.parent.state = uiconst.UI_DISABLED



    def GetMenu(self):
        if self.sr.node:
            containerMenu = []
            if hasattr(self.sr.node.scroll.sr.content, 'GetMenu'):
                containerMenu = self.sr.node.scroll.sr.content.GetMenu()
            selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
            args = []
            for node in selected:
                if node.item:
                    args.append((node.item, node.Get('viewOnly', 0), node.Get('voucher', None)))

            return sm.GetService('menu').InvItemMenu(args) + [None] + containerMenu
        else:
            return sm.GetService('menu').InvItemMenu(self.rec, self.viewOnly)



    def GetHeight(self, *args):
        (node, width,) = args
        if node.viewMode in ('details', 'assets'):
            node.height = 42
        else:
            node.height = 21
        return node.height



    def Select(self):
        if self.sr.node is not None:
            listFlag = self.sr.node.viewMode in ('list', 'details')
            left = [-3, 0][listFlag]
            top = [-3, 1][listFlag]
            if self.sr.selection is None:
                self.sr.selection = uicls.Fill(parent=self, padding=(left,
                 top,
                 left,
                 top))
            else:
                self.sr.selection.left = left
                self.sr.selection.top = top
            self.sr.selection.state = uiconst.UI_DISABLED



    def Deselect(self):
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)
            else:
                self.sr.node.scroll.SelectNode(self.sr.node)
                eve.Message('ListEntryClick')



    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn:
            return 
        self.sr.hint = ''
        wnd = sm.GetService('window').GetWindow('fitting')
        if wnd is not None:
            if getattr(self, 'rec', None):
                wnd.HiliteFitting(self.rec)
        if self.sr.node:
            if self.sr.node.viewMode == 'icons':
                self.sr.hint = '%s%s' % ([uix.GetItemQty(self.sr.node, 'ln') + ' - ', ''][bool(self.rec.singleton)], uix.GetItemName(self.sr.node.item, self.sr.node))
            else:
                eve.Message('ListEntryEnter')
            self.Hilite()



    def Hilite(self):
        if not self.highlightable:
            return 
        listFlag = self.sr.node.viewMode in ('list', 'details')
        left = [-3, 0][listFlag]
        top = [-3, 1][listFlag]
        if self.sr.hilite is None:
            self.sr.hilite = uicls.Fill(parent=self, padding=(left,
             top,
             left,
             top))
        else:
            self.sr.hilite.SetPadding(left, top, left, top)
        self.sr.hilite.state = uiconst.UI_DISABLED



    def Lolite(self):
        if self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_HIDDEN



    def OnMouseExit(self, *args):
        self.Lolite()
        if getattr(self, 'Draggable_dragging', 0):
            return 
        wnd = sm.GetService('window').GetWindow('fitting')
        if wnd is not None:
            wnd.HiliteFitting(None)



    def OnDblClick(self, *args):
        if self.sr.node and self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
        elif not self.viewOnly:
            if self.isShip:
                self.OpenCargo()
            elif self.isContainer:
                self.OpenContainer()



    def OnMouseDown(self, *args):
        if getattr(self, 'powerType', None):
            wnd = sm.GetService('window').GetWindow('fitting')
            if wnd is not None:
                wnd.HiliteFitting(self.rec)
        uicls.Container.OnMouseDown(self, *args)



    def GetDragData(self, *args):
        if not self.sr.node:
            return 
        nodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        return nodes



    def OnMouseUp(self, btn, *args):
        if uicore.uilib.mouseOver != self:
            if getattr(self, 'powerType', None):
                main = sm.GetService('station').GetSvc('fitting')
                if main is not None:
                    main.Hilite(None)
        uicls.Container.OnMouseUp(self, btn, *args)



    def OpenCargo(self):
        if not self.rec.ownerID == eve.session.charid:
            eve.Message('CantDoThatWithSomeoneElsesStuff')
            return 
        name = self.sr.node.name
        if sm.StartService('menu').CheckSameLocation(self.rec):
            sm.GetService('window').OpenCargo(self.rec.itemID, name, "%s's cargo" % name, self.rec.typeID)



    def OpenContainer(self):
        if self.rec.ownerID not in (eve.session.charid, eve.session.corpid):
            eve.Message('CantDoThatWithSomeoneElsesStuff')
            return 
        name = self.sr.node.name
        if self.rec.typeID == const.typePlasticWrap:
            sm.GetService('window').OpenContainer(self.rec.itemID, name, "%s's container" % name, self.rec.typeID, hasCapacity=0)
        elif sm.StartService('menu').CheckSameLocation(self.rec):
            sm.GetService('window').OpenContainer(self.rec.itemID, name, "%s's container" % name, self.rec.typeID, hasCapacity=1)
        else:
            location = self.rec.locationID
            if not session.stationid or util.IsStation(location) and location != session.stationid:
                log.LogInfo('Trying to open a container in', location, 'while actor is in', session.stationid)
                return 
            inventory = eve.GetInventoryFromId(location)
            if not inventory:
                return 
            item = inventory.GetItem()
            if not item:
                return 
            category = getattr(item, 'categoryID', None)
            if category == const.categoryShip and item.locationID == session.stationid:
                sm.GetService('window').OpenContainer(self.rec.itemID, name, "%s's container" % name, self.rec.typeID, hasCapacity=1)



    def OnDropData(self, dragObj, nodes):
        if len(nodes) and nodes[0].scroll:
            nodes[0].scroll.ClearSelection()
            if not nodes[0].rec:
                return 
            if not hasattr(nodes[0].rec, 'locationID'):
                return 
            if nodes[0].rec.locationID != self.rec.locationID and not sm.GetService('consider').ConfirmTakeFromContainer(nodes[0].rec.locationID):
                return 
        mergeToMe = []
        notUsed = []
        addToShip = []
        addToContainer = []
        sourceID = None
        for node in nodes:
            if node.Get('__guid__', None) not in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem'):
                notUsed.append(node)
                continue
            if node.item.itemID == self.sr.node.item.itemID:
                notUsed.append(node)
                continue
            if cfg.IsContainer(self.sr.node.item):
                if node.Get('__guid__', None) in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem'):
                    addToContainer.append(node.itemID)
            if self.isShip:
                addToShip.append(node.item.itemID)
            elif node.item.typeID == self.sr.node.item.typeID and not isinstance(self.sr.node.item.itemID, tuple):
                mergeToMe.append(node.item)
            else:
                notUsed.append(node)
            if sourceID is None:
                sourceID = node.rec.locationID

        if sourceID is None:
            log.LogInfo('OnDropData: Moot operation with ', nodes)
            return 
        if self.isShip and addToShip:
            if self.rec.ownerID != session.charid and eve.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return 
            ship = eve.GetInventoryFromId(self.rec.itemID)
            if ship:
                ship.MultiAdd(addToShip, sourceID, flag=const.flagCargo)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        mergeData = []
        stateMgr = sm.StartService('godma').GetStateManager()
        singletons = []
        for invItem in mergeToMe:
            if invItem.stacksize == 1:
                quantity = 1
            elif shift:
                ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, 'Stack items')
                if ret is not None:
                    quantity = ret['qty']
                else:
                    quantity = None
            else:
                quantity = invItem.stacksize
            if not quantity:
                continue
            if quantity > 0:
                mergeData.append((invItem.itemID,
                 self.rec.itemID,
                 quantity,
                 invItem))
            if type(invItem.itemID) is tuple:
                flag = invItem.itemID[1]
                chargeIDs = stateMgr.GetSubLocationsInBank(invItem.itemID)
                if chargeIDs:
                    for chargeID in chargeIDs:
                        charge = stateMgr.GetItem(chargeID)
                        if charge.flagID == flag:
                            continue
                        mergeData.append((charge.itemID,
                         self.rec.itemID,
                         charge.stacksize,
                         charge))

            else:
                crystalIDs = stateMgr.GetCrystalsInBank(invItem.itemID)
                if crystalIDs:
                    for crystalID in crystalIDs:
                        if crystalID == invItem.itemID:
                            continue
                        crystal = stateMgr.GetItem(crystalID)
                        if crystal.singleton:
                            singletons.append(crystalID)
                        else:
                            mergeData.append((crystal.itemID,
                             self.rec.itemID,
                             crystal.stacksize,
                             crystal))


        if singletons and util.GetAttrs(self, 'sr', 'node', 'rec', 'flagID'):
            flag = self.sr.node.rec.flagID
            inv = eve.GetInventoryFromId(self.rec.locationID)
            if inv:
                inv.MultiAdd(singletons, sourceID, flag=flag, fromManyFlags=True)
        if mergeData and util.GetAttrs(self, 'sr', 'node', 'container', 'MultiMerge'):
            self.sr.node.container.MultiMerge(mergeData, sourceID)
        if addToContainer:
            flag = settings.user.ui.Get('defaultContainerLock_%s' % self.sr.node.item.itemID, None)
            if flag is None:
                flag = const.flagLocked
            eve.GetInventoryFromId(self.sr.node.item.itemID).MultiAdd(addToContainer, sourceID, flag=flag)
        elif notUsed and util.GetAttrs(self, 'sr', 'node', 'container', 'OnDropData'):
            self.sr.node.container.OnDropData(dragObj, notUsed)




class Item(InvItem):
    __guid__ = 'listentry.InvItem'

    def ConstructLayout(self):
        dot = uicls.Frame(parent=self, pos=(4, 4, 34, 34), name='dot', texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=6, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        topoverlays = uicls.Container(parent=self, padding=(1, 2, 1, 3), name='topoverlays', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL)
        flags = uicls.Container(parent=topoverlays, pos=(0, 0, 100, 16), name='flags', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPRIGHT)
        slotSize = uicls.Icon(parent=flags, pos=(0, 0, 16, 16), name='slotSize', state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        ammoSize = uicls.Sprite(parent=flags, name='ammoSize', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/InvItem/ammoSize.png', hint=mls.UI_SHARED_AMMOSIZECONSTRAINT, state=uiconst.UI_HIDDEN, rectWidth=16, rectHeight=16)
        contrabandIcon = uicls.Sprite(parent=flags, name='contrabandIcon', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/InvItem/contrabandIcon.png', hint=mls.UI_SHARED_THISITEMISCONTRABAND, state=uiconst.UI_HIDDEN)
        container = uicls.Container(parent=self, pos=(21, 20, 16, 16), name='container', state=uiconst.UI_PICKCHILDREN, align=uiconst.RELATIVE)
        underlay = uicls.Container(parent=container, name='underlay', state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        pic = uicls.Icon(parent=self, pos=(5, 4, 32, 32), name='pic', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        qtypar = uicls.Container(parent=self, pos=(46, 24, 100, 10), name='qtypar', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        shadow = uicls.Sprite(parent=self, name='shadow', pos=(-1, 2, 45, 45), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/shapeShadow.png')
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, idx=1)
        temp = uicls.Container(parent=self, name='temp', state=uiconst.UI_DISABLED, align=uiconst.TOALL)




class InvBlueprintItem(Item):
    __guid__ = 'listentry.InvBlueprintItem'

    def UpdateLabel(self, new = 0):
        xtriui.InvItem.UpdateLabel(self, new)
        blueprint = self.sr.node.blueprint
        labeltext = self.sr.label.text
        isCopy = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][blueprint.copy]
        ml = blueprint.materialLevel
        pl = blueprint.productivityLevel
        lprr = blueprint.licensedProductionRunsRemaining
        if lprr == -1:
            lprr = ''
        label = '<t>%s<t>%s<t>%s<t>%s' % (isCopy,
         ml,
         pl,
         lprr)
        if self.sr.node.viewMode in ('list', 'details'):
            self.sr.label.text += label
            label = self.sr.label.text
        else:
            self.sr.name_label.text += label
            label = self.sr.name_label.text
        self.sr.node.label = label




class ItemWithVolume(Item):
    __guid__ = 'listentry.InvItemWithVolume'

    def UpdateLabel(self, new = 0):
        xtriui.InvItem.UpdateLabel(self, new)
        if util.GetAttrs(self, 'sr', 'node', 'remote'):
            return 
        volume = cfg.GetItemVolume(self.rec)
        self.sr.node.Set('sort_%s' % mls.UI_GENERIC_VOLUME, volume)
        unit = Tr(cfg.eveunits.Get(const.unitVolume).displayName, 'dbo.eveUnits.displayName', const.unitVolume)
        label = '<t>%s %s' % (util.FmtAmt(volume), unit)
        if self.sr.node.viewMode in ('list', 'details'):
            self.sr.label.text += label
            label = self.sr.label.text
        else:
            self.sr.name_label.text += label
            label = self.sr.name_label.text
        self.sr.node.label = label




class ItemCheckbox(Item):
    __guid__ = 'listentry.ItemCheckbox'

    def Startup(self, *args):
        cbox = uicls.Checkbox(align=uiconst.TOPLEFT, pos=(4, 4, 0, 0), callback=self.CheckBoxChange)
        cbox.data = {}
        self.children.insert(0, cbox)
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_DISABLED
        self.sr.dot.left = 20
        self.sr.shadow.left = 16
        self.sr.icon.left = 20
        self.sr.flags.left = -18
        self.sr.flags.top = 18



    def Load(self, args):
        xtriui.InvItem.Load(self, args)
        if self.sr.tlicon is not None:
            self.sr.tlicon.left = 16
            self.sr.tlicon.top = 0
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 6
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data.update({'key': data.cfgname,
         'retval': data.retval})
        if not data.OnChange:
            data.OnChange = self.OnChange
        if self.sr.tlicon:
            self.sr.tlicon.left += 1
            self.sr.tlicon.top += 2



    def OnChange(self, checkbox):
        pass



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)



    def OnClick(self, *args):
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        if self.sr.checkbox.groupName is None:
            self.sr.checkbox.SetChecked(not self.sr.checkbox.checked)
            return 
        for node in self.sr.node.scroll.GetNodes():
            if node.Get('__guid__', None) == 'listentry.Checkbox' and node.Get('group', None) == self.sr.checkbox.groupName:
                if node.panel:
                    node.panel.sr.checkbox.SetChecked(0, 0)
                    node.checked = 0
                else:
                    node.checked = 0

        if not self.destroyed:
            self.sr.checkbox.SetChecked(1)




class InvBlueprintCheckbox(ItemCheckbox):
    __guid__ = 'listentry.InvBlueprintCheckbox'

    def UpdateLabel(self, new = 0):
        xtriui.InvItem.UpdateLabel(self, new)
        hideColumns = self.sr.node.Get('hideColumns', [])
        blueprint = self.sr.node.blueprint
        label = ''
        if mls.UI_GENERIC_COPY not in hideColumns:
            isCopy = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][blueprint.copy]
            self.sr.node.Set('sort_%s' % mls.UI_GENERIC_COPY, isCopy)
            label += '<t>%s' % isCopy
        if mls.UI_RMR_ML not in hideColumns:
            ml = blueprint.materialLevel
            self.sr.node.Set('sort_%s' % mls.UI_RMR_ML, ml)
            label += '<t>%s' % ml
        if mls.UI_RMR_PL not in hideColumns:
            pl = blueprint.productivityLevel
            self.sr.node.Set('sort_%s' % mls.UI_RMR_PL, pl)
            label += '<t>%s' % pl
        if mls.UI_GENERIC_RUNS not in hideColumns:
            lprr = blueprint.licensedProductionRunsRemaining
            if lprr == -1:
                lprr = ''
            self.sr.node.Set('sort_%s' % mls.UI_GENERIC_RUNS, lprr)
            label += '<t>%s' % lprr
        if self.sr.node.viewMode in ('list', 'details'):
            if mls.UI_GENERIC_QTY in hideColumns:
                self.sr.label.text = self.sr.label.text.replace('<right><t>', '')
            self.sr.label.text += label
            label = self.sr.label.text
        elif mls.UI_GENERIC_QTY in hideColumns:
            self.sr.name_label.text = self.sr.name_label.text.replace('<right><t>', '')
        self.sr.name_label.text += label
        label = self.sr.name_label.text
        self.sr.node.label = label




class InvAssetItem(Item):
    __guid__ = 'listentry.InvAssetItem'

    def OnDropData(self, dragObj, nodes):
        pass




class InvFittingItem(InvItem):
    __guid__ = 'listentry.InvFittingItem'

    def ApplyAttributes(self, attributes):
        InvItem.ApplyAttributes(self, attributes)
        dot = uicls.Frame(parent=self, pos=(4, 3, 34, 34), name='dot', texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=6, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        topoverlays = uicls.Container(parent=self, pos=(1, 2, 1, 3), name='topoverlays', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL)
        flags = uicls.Container(parent=topoverlays, pos=(0, 0, 100, 16), name='flags', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPRIGHT)
        slotSize = uicls.Sprite(parent=flags, pos=(0, 0, 16, 16), name='slotSize', state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        ammoSize = uicls.Sprite(parent=flags, pos=(0, 0, 16, 16), name='ammoSize', state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        contrabandIcon = uicls.Sprite(parent=flags, pos=(0, 0, 16, 16), name='contrabandIcon', state=uiconst.UI_NORMAL, align=uiconst.TORIGHT)
        container = uicls.Container(parent=self, pos=(21, 20, 16, 16), name='container', state=uiconst.UI_PICKCHILDREN, align=uiconst.RELATIVE)
        underlay = uicls.Container(parent=container, name='underlay', state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        pic = uicls.Sprite(parent=self, pos=(5, 4, 32, 32), name='pic', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        qtypar = uicls.Container(parent=self, pos=(46, 24, 100, 10), name='qtypar', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        shadow = uicls.Sprite(parent=self, pos=(-2, -1, 45, 45), name='shadow', state=uiconst.UI_DISABLED, rectWidth=64, rectHeight=64, texturePath='res:/UI/Texture/Shared/bigButtonShadow.png', align=uiconst.RELATIVE)
        temp = uicls.Container(parent=self, name='temp', state=uiconst.UI_DISABLED, align=uiconst.TOALL)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, idx=1)
        self.sr.fitIcon = uicls.Icon(icon='ui_38_16_184', parent=self, size=16, idx=0, align=uiconst.BOTTOMRIGHT)
        self.sr.fitIcon.OnClick = self.FitToActiveOrUnfit
        self.sr.fitIcon.hint = mls.UI_CMD_FITTOACTIVESHIP
        self.sr.fitIcon.OnMouseEnter = self.OnMouseEnter
        self.sr.fitIcon.OnMouseExit = self.OnMouseExit
        self.sr.fitIcon.top = 4



    def UpdateLabel(self, new = 0):
        name = uix.GetItemName(self.rec, self.sr.node)
        self.sr.label.text = name + '<br>%s: %s' % (mls.UI_GENERIC_QTY, uix.GetItemQty(self.sr.node, 'ss') or 1)
        self.sr.quantity_label.parent.state = uiconst.UI_HIDDEN
        if self.sr.node.Get('showFitIcon', 1) and (self.isHardware or self.sr.node.invtype.Group().Category().id == const.categoryCharge):
            if self.rec.flagID not in (const.flagHangar, const.flagCargo):
                self.sr.fitIcon.LoadIcon('ui_38_16_184')
                self.sr.fitIcon.hint = mls.UI_CMD_REMOVE
                self.sr.fitIcon.state = uiconst.UI_NORMAL
            elif self.rec.flagID in (const.flagDroneBay,):
                self.sr.fitIcon.state = uiconst.UI_HIDDEN
        else:
            self.sr.fitIcon.state = uiconst.UI_HIDDEN



    def FitToActiveOrUnfit(self, *args):
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        if selected:
            args = []
            for node in selected:
                if node.item:
                    args.append(node.item)

            if self.sr.node.item not in args:
                args.append(self.sr.node.item)
        else:
            args = [self.sr.node.item]
        if len(args) == 0:
            return 
        sourceLocationID = args[0].locationID
        if self.rec.flagID not in (const.flagHangar, const.flagCargo):
            if eve.session.stationid is not None:
                eve.GetInventory(const.containerHangar).MultiAdd([ rec.itemID for rec in args ], sourceLocationID, flag=const.flagHangar)
            else:
                eve.GetInventoryFromId(eve.session.shipid).MultiAdd([ rec.itemID for rec in args ], sourceLocationID, flag=const.flagCargo)
        else:
            sm.GetService('menu').TryFit(args)




