#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/upgradeEntry.py
import localization
import uix
import xtriui
import util
import uiconst
import uicls
import blue

class BaseUpgradeEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.BaseUpgradeEntry'
    __nonpersistvars__ = ['selection', 'id']

    def Startup(self, *args):
        self.sr.main = uicls.Container(name='main', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.main.OnDropData = self.OnDropData
        uicls.Line(parent=self.sr.main, align=uiconst.TOBOTTOM)
        self.sr.icons = uicls.Container(name='icons', parent=self.sr.main, align=uiconst.TOLEFT, pos=(0, 0, 40, 0), padding=(1, 0, 2, 0))
        self.sr.textstuff = uicls.Container(name='textstuff', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.infoIcons = uicls.Container(name='textstuff', parent=self.sr.main, align=uiconst.TORIGHT, pos=(0, 0, 20, 0), padding=(0, 0, 0, 0))
        self.sr.status = uicls.Container(name='status', parent=self.sr.icons, align=uiconst.TOLEFT, pos=(0, 0, 18, 0), padding=(0, 0, 0, 0))
        self.sr.icon = uicls.Container(name='icon', parent=self.sr.icons, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.name = uicls.Container(name='name', parent=self.sr.textstuff, align=uiconst.TOTOP, pos=(0, 0, 0, 16), padding=(0, 0, 0, 0))
        self.sr.level = uicls.Container(name='level', parent=self.sr.textstuff, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.nameLabel = uicls.EveLabelMedium(text='', parent=self.sr.name, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.levelLabel = uicls.EveLabelMedium(text='', parent=self.sr.level, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.infoicon = uicls.InfoIcon(size=16, left=0, top=0, parent=self.sr.infoIcons, idx=0, align=uiconst.CENTERRIGHT, name='infoicon')
        self.sr.infoicon.OnClick = self.ShowInfo

    def Load(self, data):
        uix.Flush(self.sr.icon)
        uix.Flush(self.sr.status)
        self.typeID = data.typeInfo.typeID
        self.typeInfo = data.typeInfo
        self.item = data.typeInfo.item
        self.hubID = data.hubID
        if self.item is None:
            self.itemID = None
            self.online = None
        else:
            self.itemID = self.item.itemID
            self.online = self.item.online
        if data.Get('selected', 0):
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        sovSvc = sm.GetService('sov')
        self.sr.nameLabel.text = '%s' % self.typeInfo.typeName
        info = sovSvc.GetUpgradeLevel(self.typeID)
        if info is None:
            levelText = ''
        else:
            levelText = localization.GetByLabel('UI/InfrastructureHub/LevelX', level=sovSvc.GetUpgradeLevel(self.typeID).level)
        self.sr.levelLabel.text = levelText
        typeIcon = uicls.Icon(parent=self.sr.icon, align=uiconst.CENTER, pos=(0, 0, 24, 24), ignoreSize=True, typeID=self.typeID, size=24)
        hint = ''
        if self.item is not None:
            statusIconPath = 'ui_38_16_193'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeAlreadyInstalled')
        elif self.typeInfo.canInstall:
            statusIconPath = 'ui_38_16_195'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeMeetsRequirements')
        else:
            statusIconPath = 'ui_38_16_194'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeRequirementsNotMet')
        statusIcon = uicls.Icon(icon=statusIconPath, parent=self.sr.status, align=uiconst.CENTER, pos=(0, 0, 16, 16))
        statusIcon.hint = hint
        self.SetOnline(self.online)
        hinttext = localization.GetByLabel('UI/InfrastructureHub/PrereqsShort', level=sovSvc.GetUpgradeLevel(self.typeID).level)
        preReqs = sovSvc.GetPrerequisite(self.typeID)
        if preReqs is not None:
            hinttext = localization.GetByLabel('UI/InfrastructureHub/PrereqsLong', level=sovSvc.GetUpgradeLevel(self.typeID).level, preReqs=preReqs)
        self.hint = hinttext

    def GetHeight(self, *args):
        node, width = args
        node.height = 32
        return node.height

    def ShowInfo(self, *args):
        sm.StartService('info').ShowInfo(self.typeID, self.itemID)

    def SetOnline(self, online):
        if online is None:
            if self.sr.Get('onlinestatus', None):
                self.sr.onlinestatus.state = uiconst.UI_HIDDEN
        else:
            if not self.sr.Get('onlinestatus', None):
                col = uicls.Sprite(parent=self.sr.name, align=uiconst.TOPRIGHT, pos=(20, 10, 10, 10), texturePath='res:/UI/Texture/classes/Chat/Status.png')
                self.sr.onlinestatus = col
            color = self.GetOnlineColor(online)
            self.sr.onlinestatus.SetRGB(*color)
            if online:
                self.sr.onlinestatus.hint = localization.GetByLabel('UI/InfrastructureHub/Online')
            else:
                self.sr.onlinestatus.hint = localization.GetByLabel('UI/InfrastructureHub/Offline')
            self.sr.onlinestatus.state = uiconst.UI_NORMAL

    def GetOnlineColor(self, online):
        if online:
            return (0.0, 0.75, 0.0)
        else:
            return (0.75, 0.0, 0.0)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)
        sm.ScatterEvent('OnEntrySelected', self.typeID)

    def OnMouseEnter(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            eve.Message('ListEntryEnter')
            self.sr.selection.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]

    def OnDropData(self, dragObj, nodes):
        itemlist = [ item for item in nodes if getattr(item, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem') and cfg.invtypes.Get(item.rec.typeID).categoryID == const.categoryStructureUpgrade ]
        if itemlist:
            itemsLocation = itemlist[0].rec.locationID
            sov = sm.GetService('sov')
            days, amountPerDay = sov.CalculateUpgradeCost(eve.session.locationid, [ item.rec.typeID for item in itemlist ])
            amount = amountPerDay * days
            mlsMsg = 'SovConfirmUpgradeDrop'
            if amount > 0:
                mlsMsg += 'WithCharge'
            if eve.Message(mlsMsg, {'amount': (AMT3, amount),
             'days': days}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                sm.GetService('sov').AddUppgrades(self.hubID, [ item.itemID for item in itemlist ], itemsLocation)
        elif nodes:
            eve.Message('SovInvalidHubUpgrade')

    def GetMenu(self):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(self.itemID, self.typeID, ignoreMarketDetails=0)
        return m