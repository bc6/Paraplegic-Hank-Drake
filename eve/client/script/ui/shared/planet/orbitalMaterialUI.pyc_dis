#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/orbitalMaterialUI.py
import uiconst
import const
import util
import uicls
import uix
import localization
from collections import defaultdict
ICONWIDTH = 74
ICONHEIGHT = 154
ICONPADDING = 4

class OrbitalMaterialUI(uicls.Window):
    __guid__ = 'form.OrbitalMaterialUI'
    __notifyevents__ = ['OnItemChange']
    default_windowID = 'OrbitalMaterialUI'
    default_topParentHeight = 0

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.orbitalID = attributes.orbitalID
        self.hasCapacity = 1
        self.SetCaption(localization.GetByLabel('UI/UpgradeWindow/UpgradeHold'))
        self.SetMinSize([330, 210])
        self.MakeUnResizeable()
        self.Startup(attributes.orbitalID, localization.GetByLabel('UI/UpgradeWindow/OrbitalUpgradeHold'), const.flagSpecializedMaterialBay)
        self.CheckCanUpgrade()

    def Startup(self, id_, name, locationFlag):
        sm.RegisterNotify(self)
        self.itemID = id_
        self.typeID = sm.GetService('invCache').GetInventoryFromId(self.itemID).GetItem().typeID
        self.displayName = name
        self.locationFlag = locationFlag
        self.scope = 'inflight'
        self.AddLayout()
        self.PopulateIcons()

    def AddLayout(self):
        pad = const.defaultPadding
        uicls.WndCaptionLabel(text=cfg.invgroups.Get(cfg.invtypes.Get(self.typeID).groupID).groupName, subcaption=localization.GetByLabel('UI/UpgradeWindow/TypeUpgradesTo', type1=self.typeID, type2=self.GetUpgradeTypeID()), parent=self.sr.topParent, align=uiconst.RELATIVE)
        uicls.Icon(parent=self.sr.topParent, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), padding=(pad,
         pad,
         pad,
         pad), typeID=self.typeID)
        self.sr.footer = uicls.Container(name='footer', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(pad,
         pad,
         pad,
         pad))
        uicls.Line(align=uiconst.TOBOTTOM, parent=self.sr.main)
        self.sr.iconContainer = uicls.Container(name='iconContainer', parent=self.sr.main, align=uiconst.TOALL, padding=(pad + 5,
         pad + 5,
         0,
         0), columns=4)
        self.sr.iconContainer.OnDropData = self.OnDropData
        self.sr.iconContainer.OnDragEnter = self.OnDragEnter
        self.sr.iconContainer.OnDragExit = self.OnDragExit
        btns = [(localization.GetByLabel('UI/UpgradeWindow/StartUpgrade'),
          self.InitiateUpgrade,
          (),
          None)]
        self.buttons = btns = uicls.ButtonGroup(btns=btns, parent=self.sr.footer, line=0)
        self.transferBtn = btns.GetBtnByIdx(0)

    def PopulateIcons(self):
        qtyByTypeID = defaultdict(lambda : util.KeyVal(qty=0, invItems=set()))
        inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        for item in inv.List(flag=const.flagSpecializedMaterialBay):
            qtyByTypeID[item.typeID].qty += item.stacksize
            qtyByTypeID[item.typeID].invItems.add(item)

        self.upgradeIconsByTypeID = {}
        for info in self.GetUpgradeMaterials():
            upgradeIcon = self.upgradeIconsByTypeID[info.materialTypeID] = UpgradeTypeIcon(name='%s' % info.materialTypeID, parent=self.sr.iconContainer, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, typeID=info.materialTypeID, qtyNeeded=info.quantity, qty=qtyByTypeID[info.materialTypeID].qty, invItems=qtyByTypeID[info.materialTypeID].invItems, containerID=self.itemID)
            upgradeIcon.HookInEvents(util.KeyVal(OnDropData=self.OnDropData, OnDragEnter=self.OnDragEnter, OnDragExit=self.OnDragExit))

        self.ArrangeIcons()

    def ArrangeIcons(self):
        containerWidth, containerHeight = self.sr.iconContainer.GetAbsoluteSize()
        iconWidth = ICONWIDTH + ICONPADDING
        iconHeight = ICONHEIGHT + ICONPADDING
        maxRows = containerHeight / iconHeight
        numberOfColumns = (containerWidth - ICONPADDING) / iconWidth
        for i, icon in enumerate(self.upgradeIconsByTypeID.itervalues()):
            column = i % numberOfColumns
            row = i / numberOfColumns
            icon.left = iconWidth * column
            icon.top = iconHeight * row
            icon.width = ICONWIDTH
            icon.height = ICONHEIGHT
            if row < maxRows:
                icon.state = uiconst.UI_NORMAL
            else:
                icon.state = uiconst.UI_HIDDEN
            icon.state = uiconst.UI_NORMAL

    def OnItemChange(self, item, change):
        if const.ixLocationID in change or item.locationID == self.itemID and const.ixStackSize in change:
            if self.itemID in (item.locationID, change.get(const.ixLocationID, None)):
                self.UpdateTypeQuantity(item.typeID)

    def UpdateTypeQuantity(self, typeID):
        inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        qty = 0
        for item in inv.List():
            if item.typeID == typeID:
                qty += item.stacksize

        self.upgradeIconsByTypeID[typeID].SetQuantity(qty)
        self.CheckCanUpgrade()

    def CheckCanUpgrade(self):
        for upgradeIcon in self.upgradeIconsByTypeID.itervalues():
            if upgradeIcon.qtyNeeded > upgradeIcon.qty:
                self.buttons.opacity = 0.5
                return

        self.buttons.opacity = 1.0

    def DoGetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)

    def IsItemHere(self, rec):
        return rec.locationID == self.itemID and rec.flagID == self.locationFlag

    def GetCapacity(self):
        return self.GetShell().GetCapacity(self.locationFlag)

    def InitiateUpgrade(self):
        posMgr = util.Moniker('posMgr', session.solarsystemid)
        posMgr.OnlineOrbital(self.itemID)
        self.Close()

    def GetUpgradeMaterials(self):
        upgradeTypeID = self.GetUpgradeTypeID()
        return cfg.invtypematerials.get(upgradeTypeID, [])

    def GetUpgradeTypeID(self):
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        return int(dogmaStaticSvc.GetTypeAttribute2(self.typeID, const.attributeConstructionType))

    def OnDropData(self, dragObj, nodes):
        itemIDsByLocation = defaultdict(set)
        try:
            for node in nodes:
                if node.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem'):
                    continue
                itemIDsByLocation[node.rec.locationID].add(node.rec.itemID)

            inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
            for locationID, itemIDs in itemIDsByLocation.iteritems():
                inv.MultiAdd(itemIDs, locationID, flag=const.flagSpecializedMaterialBay)

        finally:
            for icon in self.upgradeIconsByTypeID.itervalues():
                self.UpdateTypeQuantity(icon.typeID)

    def OnResizeUpdate(self, *args):
        self.ArrangeIcons()

    def OnDragEnter(self, dragObj, nodes, *args):
        qtyByTypeID = defaultdict(lambda : 0)
        for node in nodes:
            if node.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem'):
                continue
            if node.rec.locationID == self.itemID and node.rec.flagID == const.flagSpecializedMaterialBay:
                continue
            typeID = node.rec.typeID
            qtyByTypeID[typeID] += node.rec.quantity

        for typeID, quantity in qtyByTypeID.iteritems():
            icon = self.upgradeIconsByTypeID.get(typeID, None)
            if icon is None:
                continue
            icon.Hilite(quantity)

    def OnDragExit(self, *args):
        for icon in self.upgradeIconsByTypeID.itervalues():
            icon.Delite()


class UpgradeTypeIcon(uicls.Container):
    __guid__ = 'uicls.UpgradeTypeIcon'
    isDragObject = True
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.animateThread = None
        self.typeID = attributes.typeID
        self.invItems = attributes.invItems
        self.qtyNeeded = attributes.qtyNeeded
        self.containerID = attributes.containerID
        self.AddLayout()
        self.SetQuantity(attributes.qty)

    def AddLayout(self):
        self.sr.main = uicls.Container(name='main', parent=self, align=uiconst.TOPLEFT, height=ICONHEIGHT, width=ICONWIDTH)
        self.sr.background = uicls.Container(name='background', parent=self.sr.main, align=uiconst.TOTOP, height=88)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(name='backgroundUnderlay', parent=self.sr.background)
        self.sr.iconContainer = uicls.Container(name='iconContainer', parent=self.sr.main, align=uiconst.CENTERTOP, pos=(0, 10, 54, 54), idx=0)
        invTypeIcon = cfg.invtypes.Get(self.typeID).Icon()
        self.sr.icon = icon = uicls.Icon(parent=self.sr.iconContainer, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        if invTypeIcon is None:
            icon.ChangeIcon(typeID=self.typeID)
        else:
            icon.LoadIcon(invTypeIcon.iconFile)
        self.sr.quantityContainer = uicls.Container(name='quantityContainer', parent=self.sr.background, align=uiconst.CENTERBOTTOM, height=20, width=ICONWIDTH - 1, idx=0, bgColor=(0, 0, 0, 0.5))
        self.sr.quantityLabel = uicls.EveLabelMedium(text='', parent=self.sr.quantityContainer, align=uiconst.CENTERBOTTOM, left=3, bold=True)
        self.barContainer = uicls.Fill(name='barContainer', parent=self.sr.quantityContainer, align=uiconst.TOPLEFT, color=(1, 1, 1, 0.25), height=20, width=0)
        self.sr.typeNameContainer = uicls.Container(name='typeNameContainer', parent=self.sr.main, align=uiconst.TOALL)
        self.sr.typeName = uicls.LabelLink(text=localization.GetByLabel('UI/UpgradeWindow/CenteredTypeText', type=self.typeID), parent=self.sr.typeNameContainer, align=uiconst.CENTERTOP, maxLines=3, width=ICONWIDTH, func=(sm.GetService('info').ShowInfo, self.typeID), hint=localization.GetByLabel('UI/Commands/ShowInfo'), top=3)
        self.sr.typeName.maxLines = None
        self.sr.frame = uicls.Frame(parent=self, state=uiconst.UI_HIDDEN)

    def HookInEvents(self, events):
        for container in (self, self.sr.typeName):
            container.OnDropData = events.OnDropData
            container.OnDragEnter = events.OnDragEnter
            container.OnDragExit = events.OnDragExit

    def SetQuantity(self, qty):
        self.qty = qty
        self.DisplayQuantity(qty)
        self.hint = localization.GetByLabel('UI/UpgradeWindow/TypeIconToolTip', amount=self.qtyNeeded - self.qty, typeID=self.typeID)

    def DisplayQuantity(self, qty, highlight = False):
        self.AnimateBar(min(int(ICONWIDTH * (float(qty) / self.qtyNeeded)), ICONWIDTH) - 1)
        if qty <= 0:
            self.sr.icon.opacity = 0.2
        else:
            self.sr.icon.opacity = 1.0
        if False and self.qtyNeeded <= self.qty:
            self.sr.quantityLabel.text = localization.GetByLabel('UI/UpgradeWindow/TypeFull')
        else:
            if highlight:
                qty = '<color=yellow>%s</color>' % qty
            self.sr.quantityLabel.text = '%s / %s' % (qty, self.qtyNeeded)

    def AnimateBar(self, width):
        width = int(max(0, width))
        uiEffects = uicls.UIEffects()
        if self.animateThread is not None:
            self.animateThread.kill()
            self.animateThread = None
        uiEffects = uicls.UIEffects()
        self.animateThread = uiEffects.MorphUI(self.barContainer, 'width', width, ifWidthConstrain=0, time=250.0)

    def Hilite(self, quantity):
        totalQuantity = min(self.qty + quantity, self.qtyNeeded)
        self.DisplayQuantity(totalQuantity, highlight=True)

    def Delite(self):
        self.DisplayQuantity(self.qty)

    def GetDragData(self, *args):
        inv = sm.GetService('invCache').GetInventoryFromId(self.containerID)
        return [ uix.GetItemData(item, 'icons') for item in inv.List(const.flagSpecializedMaterialBay) if item.typeID == self.typeID ]