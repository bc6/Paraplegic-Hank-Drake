#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/infrastructureHub.py
import localization
import uix
import uiutil
import util
import uiconst
import listentry
import uicls
import log
import form
UPGRADE_ALL = 0
UPGRADE_LOCKED = 1
UPGRADE_UNLOCKED = 2
UPGRADE_INSTALLED = 3
FILLED_COLOR = (1.0,
 1.0,
 1.0,
 0.5)
EMPTY_COLOR = (0.15,
 0.15,
 0.15,
 0.5)
PARTIAL_COLOR = (0.5,
 0.5,
 0.5,
 0.5)
LEVEL_SIZE = 20

class InfrastructureHubWnd(uicls.Window):
    __guid__ = 'form.InfrastructureHubWnd'
    __notifyevents__ = ['OnItemChange', 'OnEntrySelected', 'OnBallparkCall']
    default_width = 320
    default_height = 70
    default_windowID = 'infrastructhubman'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        hubID = attributes.hubID
        self.devIndices = sm.RemoteSvc('devIndexManager').GetDevelopmentIndicesForSystem(session.solarsystemid2)
        self.SetCaption(localization.GetByLabel('UI/InfrastructureHub/InfrastructureHubManagement'))
        self.SetMinSize([440, 320])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.id = self.hubID = hubID
        self.upgradeListMode = UPGRADE_ALL
        self.CreateUpgradeCache()
        self.ConstructLayout()

    def ConstructLayout(self):
        if eve.session.corprole & const.corpRoleDirector > 0:
            self.SetHeaderIcon()
            hicon = self.sr.headerIcon
            hicon.GetMenu = self.OpenMenu
            hicon.expandOnLeft = 1
            hicon.hint = localization.GetByLabel('UI/InfrastructureHub/HubSettings')
            hicon.name = 'ihHeaderIcon'
            self.sr.presetMenu = hicon
        self.sr.upgradesTab = uicls.Container(name='upgradesTab', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.index = uicls.Container(name='hubs', parent=self.sr.upgradesTab, align=uiconst.TOLEFT, pos=(0, 0, 155, 0), padding=(0, 0, 2, 0))
        self.sr.index.state = uiconst.UI_NORMAL
        self.sr.upgrades = uicls.Container(name='upgrades', parent=self.sr.upgradesTab, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.upgrades.state = uiconst.UI_NORMAL
        uicls.Line(parent=self.sr.upgrades, align=uiconst.TOLEFT)
        uicls.Line(parent=self.sr.index, align=uiconst.TORIGHT)
        self.sr.infoContainer = uicls.Container(name='infoContainer', parent=self.sr.upgrades, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 90), padding=(0, 5, 0, 0))
        self.sr.upgradesContainer = uicls.Container(name='upgradesContainer', parent=self.sr.upgrades, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.hubs = uicls.Container(name='hubs', parent=self.sr.index, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.DrawUpgrades()
        self.DrawIndex(localization.GetByLabel('UI/Sovereignty/Strategic'), const.attributeDevIndexSovereignty)
        self.DrawIndex(localization.GetByLabel('UI/Sovereignty/Military'), const.attributeDevIndexMilitary)
        self.DrawIndex(localization.GetByLabel('UI/Sovereignty/Industry'), const.attributeDevIndexIndustrial)
        self.DrawInfo()

    def DrawUpgrades(self):
        comboBoxContainer = uicls.Container(name='comboBoxContainer', parent=self.sr.upgradesContainer, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(10, 10, 10, 0))
        text = uicls.Container(name='text', parent=self.sr.upgradesContainer, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(10, 4, 10, 0))
        t = uicls.EveLabelMedium(text=localization.GetByLabel('UI/InfrastructureHub/DropUpgrades'), parent=text, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        updatesScrollContainer = uicls.Container(name='updatesScrollContainer', parent=self.sr.upgradesContainer, align=uiconst.TOALL, padding=(10, 0, 10, 0))
        self.sr.scroll = uicls.Scroll(name='scroll', parent=updatesScrollContainer)
        comboValues = ((localization.GetByLabel('UI/InfrastructureHub/AllUpgrades'), UPGRADE_ALL),
         (localization.GetByLabel('UI/InfrastructureHub/InstalledUpgrades'), UPGRADE_INSTALLED),
         (localization.GetByLabel('UI/InfrastructureHub/UnlockedUpgrades'), UPGRADE_UNLOCKED),
         (localization.GetByLabel('UI/InfrastructureHub/LockedUpgrades'), UPGRADE_LOCKED))
        self.upgradeListMode = settings.user.ui.Get('InfrastructureHubUpgradeCombo', UPGRADE_ALL)
        combo = uicls.Combo(parent=comboBoxContainer, name='combo', select=self.upgradeListMode, align=uiconst.TOALL, callback=self.OnComboChange, options=comboValues, idx=0)
        self.UpdateUpgrades()

    def CreateUpgradeCache(self):
        upgradeGroups = {}
        sovSvc = sm.GetService('sov')
        itemData = sovSvc.GetInfrastructureHubItemData(self.hubID)
        for g in cfg.invgroups:
            if g.categoryID == const.categoryStructureUpgrade and g.published:
                upgradeGroups[g.groupID] = util.KeyVal(groupID=g.groupID, groupName=g.groupName, types=[])

        for t in cfg.invtypes:
            if t.groupID in upgradeGroups and t.published:
                typeInfo = util.KeyVal(typeID=t.typeID, typeName=t.typeName)
                typeInfo.item = itemData.get(t.typeID, None)
                if typeInfo.item is None:
                    typeInfo.canInstall = sovSvc.CanInstallUpgrade(t.typeID, self.hubID, devIndices=self.devIndices)
                    if typeInfo.canInstall:
                        typeInfo.state = UPGRADE_UNLOCKED
                    else:
                        typeInfo.state = UPGRADE_LOCKED
                else:
                    typeInfo.state = UPGRADE_INSTALLED
                    typeInfo.canInstall = None
                upgradeGroups[t.groupID].types.append(typeInfo)

        self.upgradeGroups = upgradeGroups.values()
        self.upgradeGroups.sort(key=lambda g: g.groupName)
        for groupInfo in self.upgradeGroups:
            groupInfo.types.sort(key=lambda t: t.typeName)

    def GetTypesInStateForGroup(self, groupID, state):
        types = []
        groupInfo = None
        for g in self.upgradeGroups:
            if g.groupID == groupID:
                groupInfo = g
                break
        else:
            return types

        if state == UPGRADE_ALL:
            types = groupInfo.types
        else:
            for typeInfo in groupInfo.types:
                if typeInfo.state == state:
                    types.append(typeInfo)

        return types

    def UpdateUpgrades(self):
        scrolllist = []
        for group in self.upgradeGroups:
            types = self.GetTypesInStateForGroup(group.groupID, self.upgradeListMode)
            data = {'GetSubContent': self.GetSubContent,
             'label': group.groupName,
             'id': ('upgrades', group.groupID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0,
             'groupID': group.groupID,
             'types': types,
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist)

    def GetSubContent(self, groupData, *args):
        scrolllist = []
        for typeInfo in groupData.types:
            data = {}
            data['typeInfo'] = typeInfo
            data['hubID'] = self.hubID
            scrolllist.append(listentry.Get('BaseUpgradeEntry', data))

        return scrolllist

    def DrawIndex(self, indexName = None, indexID = None):
        container = uicls.Container(name='container', parent=self.sr.hubs, align=uiconst.TOTOP, pos=(0, 0, 0, 40), padding=(10, 10, 10, 0))
        leftContainer = uicls.Container(name='leftContainer', parent=container, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        rightContainer = uicls.Container(name='rightContainer', parent=container, align=uiconst.TORIGHT, pos=(0, 0, 20, 20), padding=(0, 0, 0, 0))
        topContainer = uicls.Container(name='topContainer', parent=leftContainer, align=uiconst.TOPLEFT, pos=(0,
         0,
         LEVEL_SIZE * 5 + 14,
         10), padding=(0, 0, 0, 0))
        bottomContainer = uicls.Container(name='bottomContainer', parent=leftContainer, align=uiconst.BOTTOMLEFT, pos=(0,
         0,
         LEVEL_SIZE * 5 + 14,
         LEVEL_SIZE + 4), padding=(0, 0, 0, 0))
        uicls.Line(parent=bottomContainer, align=uiconst.TOTOP, color=FILLED_COLOR)
        uicls.Line(parent=bottomContainer, align=uiconst.TOBOTTOM, color=FILLED_COLOR)
        uicls.Line(parent=bottomContainer, align=uiconst.TOLEFT, color=FILLED_COLOR)
        uicls.Line(parent=bottomContainer, align=uiconst.TORIGHT, color=FILLED_COLOR)
        topLeftContainer = uicls.Container(name='topLeftContainer', parent=topContainer, align=uiconst.TOLEFT, pos=(0, 0, 30, 0), padding=(0, 0, 0, 0))
        topRightContainer = uicls.Container(name='topRightContainer', parent=topContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 2, 0))
        devIndex = self.devIndices.get(indexID, None)
        indexInfo = sm.GetService('sov').GetLevelForIndex(indexID, devIndex=devIndex)
        t = uicls.EveLabelMedium(text=indexName, parent=topLeftContainer, state=uiconst.UI_DISABLED)
        t2 = uicls.EveLabelMedium(text=localization.GetByLabel('UI/InfrastructureHub/LevelX', level=indexInfo.level), parent=topRightContainer, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        if indexID == const.attributeDevIndexSovereignty:
            indexList = [ str(v) for v in sm.GetService('sov').GetTimeIndexValuesInDays() ]
        iconPath = 'ui_73_16_211'
        hintTextChangeIcon = localization.GetByLabel('UI/InfrastructureHub/ValueChangeUp')
        for i in range(1, 6):
            if i == 1:
                leftPadding = 2
            else:
                leftPadding = 1
            if i == 5:
                rightPadding = 2
            else:
                rightPadding = 1
            level = uicls.Container(name='level%d' % i, parent=bottomContainer, align=uiconst.TOLEFT, pos=(0,
             0,
             LEVEL_SIZE,
             LEVEL_SIZE), padding=(leftPadding,
             2,
             rightPadding,
             2))
            level.state = uiconst.UI_NORMAL
            if indexID == const.attributeDevIndexSovereignty:
                hintText = localization.GetByLabel('UI/InfrastructureHub/LevelNeedsSovForDays', level=i, days=int(indexList[i - 1]))
            else:
                hintText = localization.GetByLabel('UI/InfrastructureHub/LevelX', level=i)
            level.hint = hintText
            if i <= indexInfo.level:
                uicls.Fill(parent=level, color=FILLED_COLOR)
            elif i == indexInfo.level + 1 and indexInfo.remainder > 0:
                uicls.Fill(parent=level, color=EMPTY_COLOR)
                levelPart = uicls.Container(name='levelPartial', parent=level, align=uiconst.TOLEFT, pos=(0,
                 0,
                 int(indexInfo.remainder * LEVEL_SIZE),
                 0), idx=0)
                levelPart.state = uiconst.UI_NORMAL
                perc = indexInfo.remainder * 100
                levelPart.hint = localization.GetByLabel('UI/InfrastructureHub/PercentageOfLevel', perc=int(perc), level=i)
                if not indexInfo.increasing:
                    iconPath = 'ui_73_16_212'
                    hintTextChangeIcon = localization.GetByLabel('UI/InfrastructureHub/ValueChangeDown')
                uicls.Fill(parent=levelPart, color=PARTIAL_COLOR)
            else:
                uicls.Fill(parent=level, color=EMPTY_COLOR)

        if indexID != const.attributeDevIndexSovereignty and indexInfo.remainder != 0.0 and indexInfo.level != 0:
            changeIcon = uicls.Icon(icon=iconPath, parent=rightContainer, align=uiconst.CENTER, pos=(4, 8, 16, 16))
            changeIcon.hint = hintTextChangeIcon

    def DrawInfo(self):
        self.sr.info = uicls.Container(name='info', parent=self.sr.infoContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(10, 2, 10, 10))
        self.sr.icon = uicls.Container(name='icon', parent=self.sr.info, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0, 0, 0, 0))
        self.sr.desc = uicls.EditPlainText(parent=self.sr.info, readonly=1)
        self.sr.desc.HideBackground()
        self.sr.desc.RemoveActiveFrame()

    def OnComboChange(self, combo, key, value, *args):
        self.upgradeListMode = value
        settings.user.ui.Set('InfrastructureHubUpgradeCombo', value)
        self.UpdateUpgrades()

    def OnItemChange(self, item, change):
        if self.hubID in (item.itemID, item.locationID):
            log.LogInfo('InfrastructureHub hub item changed')
            self.CreateUpgradeCache()
            self.UpdateUpgrades()

    def OnEntrySelected(self, typeID):
        uix.Flush(self.sr.icon)
        typeIcon = uicls.Icon(parent=self.sr.icon, align=uiconst.TOPLEFT, pos=(0, 10, 64, 64), ignoreSize=True, typeID=typeID, size=64)
        text = cfg.invtypes.Get(typeID).description
        info = localization.GetByLabel('UI/InfrastructureHub/EntryDescription', item=typeID, description=text)
        self.sr.desc.SetValue(info)

    def OpenSettings(self, *args):
        form.InfrastructureHubManagementWnd.CloseIfOpen()
        wnd = form.InfrastructureHubManagementWnd.Open(hubID=self.hubID)
        return wnd

    def OpenMenu(self, *args):
        m = []
        m.append((uiutil.MenuLabel('UI/InfrastructureHub/HubSettings'), self.OpenSettings))
        return m

    def OnBallparkCall(self, functionName, args):
        if functionName == 'WarpTo':
            self.Close()


class InfrastructureHubManagementWnd(uicls.Window):
    __guid__ = 'form.InfrastructureHubManagementWnd'
    default_windowID = 'infrastructhubsettings'
    default_width = 230
    default_height = 70

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        hubID = attributes.hubID
        self.SetCaption(localization.GetByLabel('UI/InfrastructureHub/HubSettings'))
        self.SetMinSize([230, 70])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.hubID = hubID
        self.corpID = eve.session.corpid
        self.ConstructLayout()

    def ConstructLayout(self):
        self.sr.timeCont = uicls.Container(name='timeCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 25), padding=(8, 5, 8, 0))
        self.sr.buttonCont = uicls.Container(name='buttonCont', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(0, 0, 0, 0))
        self.sr.bottomRight = uicls.Container(name='bottomRight', parent=self.sr.timeCont, align=uiconst.TORIGHT, pos=(0, 0, 60, 0), padding=(0, 0, 0, 0))
        self.sr.bottomLeft = uicls.Container(name='bottomLeft', parent=self.sr.timeCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        btn = uicls.Button(parent=self.sr.buttonCont, label=localization.GetByLabel('UI/Common/CommandSet'), className='Button', align=uiconst.CENTER)
        btn.OnClick = self.Update
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/InfrastructureHub/ReinforcedModeExitTime'), parent=self.sr.bottomLeft, left=0, top=2, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, maxLines=1)
        self.sr.comboTime = uicls.Combo(parent=self.sr.bottomRight, name='comboTime', select=self.GetTime(), width=50, align=uiconst.TOPRIGHT, options=self.GetHours(), idx=0)

    def GetHours(self):
        chinaOffset = 0
        if boot.region == 'optic':
            chinaOffset = 8
        hours = []
        for i in xrange(24):
            text = ''
            if i < 10:
                text = '0%s:00' % i
            else:
                text = '%s:00' % i
            value = (i - chinaOffset) % 24
            hours.append((text, value))

        return hours

    def GetTime(self):
        svc = sm.GetService('michelle')
        svc2 = svc.GetBallpark()
        park = svc2.remoteBallpark
        self.time = park.GetSovStructExitTime(self.hubID) / 100
        return self.time

    def Update(self, *args):
        oldTimeValue = self.GetTime()
        timeValue = self.sr.comboTime.GetValue()
        if timeValue == oldTimeValue:
            return
        svc = sm.GetService('michelle')
        svc2 = svc.GetBallpark()
        self.park = svc2.remoteBallpark
        if timeValue != oldTimeValue:
            if eve.Message('ChangingTimeForIH', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.UpdateTime(oldTimeValue, timeValue)
                self.CloseByUser()

    def UpdateTime(self, oldTime, newTime):
        self.park.CmdChangeSovStructExitTime(self.hubID, oldTime * 100, newTime * 100)