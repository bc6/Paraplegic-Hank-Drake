#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/warReport.py
import localization
import uix
import uiutil
import util
import uiconst
import listentry
import uicls
import blue
import moniker
import form
import math
import facwarCommon
import uthread
from collections import defaultdict
ATTACKER_COLOR = facwarCommon.COLOR_FOE_BAR
DEFENDER_COLOR = facwarCommon.COLOR_FRIEND_BAR

class WarReportWnd(uicls.Window):
    __guid__ = 'form.WarReportWnd'
    __notifyevents__ = []
    default_windowID = 'WarReportWnd'
    default_width = 550
    default_height = 640
    default_minSize = (default_width, default_height)
    default_iconNum = 'ui_1337_64_2'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.war = None
        self.warID = attributes.Get('warID', None)
        self.attackerID = attributes.Get('attackerID', None)
        self.defenderID = attributes.Get('defenderID', None)
        self.shipGroupByGroup = None
        self.shipGroupNames = None
        self.warNegotiationID = None
        self.loading = False
        self.shipGroupList = []
        self.maxKills = 0
        self.killsLoaded = False
        self.graphLoaded = False
        self.killsByShipGroup = defaultdict(lambda : util.KeyVal(attackerKills=0, defenderKills=0, attackerKillsIsk=0, defenderKillsIsk=0))
        self.SetCaption(localization.GetByLabel('UI/Corporations/Wars/WarReport'))
        self.SetTopparentHeight(0)
        self.GetShipGroupList()
        self.ConstructLayout()

    def GetWarStatisticMoniker(self, warID):
        self.warStatisticMoniker = moniker.GetWarStatistic(warID)
        self.warStatisticMoniker.Bind()
        return self.warStatisticMoniker

    def ConstructLayout(self):
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=135, clipChildren=True, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.loadingCont = uicls.Container(name='loadingCont', parent=self.sr.main, align=uiconst.TOALL)
        self.loadingText = uicls.EveCaptionMedium(text='', parent=self.loadingCont, align=uiconst.CENTER)
        self.loadingCont.display = True
        self.historyCont = uicls.Container(name='historyCont', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding * 2,
         const.defaultPadding,
         const.defaultPadding))
        self.historyCont.display = False
        line = uicls.Line(parent=topCont, align=uiconst.TOBOTTOM)
        textCont = uicls.Container(name='textCont', parent=topCont, align=uiconst.TOTOP, height=35)
        self.warDateLabel = uicls.EveLabelMedium(text='', parent=textCont, align=uiconst.CENTER)
        self.mutualWarLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/Wars/MutualWar'), parent=textCont, align=uiconst.CENTER)
        self.mutualWarLabel.display = False
        warInfoCont = uicls.Container(name='buttonCont', parent=topCont, align=uiconst.TOBOTTOM, height=33)
        self.surrenderBtn = uicls.ButtonIcon(name='surrenderBtn', parent=warInfoCont, align=uiconst.TOLEFT, width=24, iconSize=24, texturePath='res:/UI/Texture/Icons/Surrender_64.png', func=self.OpenSurrenderWnd)
        self.surrenderBtn.display = False
        self.allyBtn = uicls.ButtonIcon(name='allyBtn', parent=warInfoCont, align=uiconst.TORIGHT, width=24, iconSize=24, texturePath='res:/UI/Texture/Icons/Mercenary_64.png', func=self.OpenAllyWnd)
        warCont = uicls.Container(name='warCont', parent=topCont, align=uiconst.TOALL)
        attackerCont = uicls.Container(name='attackerCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.45)
        attackerLogoCont = uicls.Container(name='attackerLogoCont', parent=attackerCont, align=uiconst.TORIGHT, width=64)
        self.attackerLogoDetailed = uicls.Container(name='attackerLogoDetailed', parent=attackerLogoCont, align=uiconst.TOPRIGHT, width=64, height=64)
        attackerTextCont = uicls.Container(name='attackerTextCont', parent=attackerCont, align=uiconst.TOALL, padding=(4, 0, 8, 4))
        self.attackerNameLabel = uicls.EveLabelLarge(text='', parent=attackerTextCont, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
        self.attackerISKLostLabel = uicls.EveLabelMedium(text='', parent=attackerTextCont, align=uiconst.CENTERRIGHT, height=16)
        self.attackerShipsLostLabel = uicls.EveLabelMedium(text='', parent=attackerTextCont, align=uiconst.BOTTOMRIGHT)
        centerCont = uicls.Container(name='centerCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.1)
        iconSize = 24
        swords = uicls.Icon(name='warIcon', parent=centerCont, align=uiconst.CENTER, size=iconSize, ignoreSize=True, state=uiconst.UI_NORMAL)
        swords.LoadIcon('res:/UI/Texture/Icons/swords.png')
        swords.SetAlpha(0.7)
        swords.hint = localization.GetByLabel('UI/Corporations/Wars/Vs')
        defenderCont = uicls.Container(name='defenderCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.45)
        defenderLogoCont = uicls.Container(name='defenderLogoCont', parent=defenderCont, align=uiconst.TOLEFT, width=64)
        self.defenderLogoDetailed = uicls.Container(name='defenderLogoDetailed', parent=defenderLogoCont, align=uiconst.TOPLEFT, width=64, height=64)
        defenderTextCont = uicls.Container(name='defenderTextCont', parent=defenderCont, align=uiconst.TOALL, padding=(8, 0, 4, 4))
        self.defenderNameLabel = uicls.EveLabelLarge(text='', parent=defenderTextCont, state=uiconst.UI_NORMAL)
        self.defenderISKKilledLabel = uicls.EveLabelMedium(text='', parent=defenderTextCont, align=uiconst.CENTERLEFT, height=16)
        self.defenderShipsKilledLabel = uicls.EveLabelMedium(text='', parent=defenderTextCont, align=uiconst.BOTTOMLEFT)
        killsFilterCont = uicls.Container(name='killsFilterCont', parent=self.historyCont, align=uiconst.TOTOP, height=24)
        killOptions = [(localization.GetByLabel('UI/Corporations/Wars/ShowAllKills'), None), (localization.GetByLabel('UI/Corporations/Wars/ShowAggressorKills'), 'attacker'), (localization.GetByLabel('UI/Corporations/Wars/ShowDefenderKills'), 'defender')]
        comboSetting = settings.user.ui.Get('killComboValue', 0)
        self.killsFilterCombo = uicls.Combo(name='killsFilterCombo', parent=killsFilterCont, options=killOptions, adjustWidth=True, select=comboSetting, callback=self.OnKillComboChange)
        showGraph = settings.user.ui.Get('killShowGraph', 0)
        self.showGraph = uicls.Checkbox(text=localization.GetByLabel('UI/Corporations/Wars/ShowGraph'), parent=killsFilterCont, padLeft=self.killsFilterCombo.width + const.defaultPadding, checked=showGraph, callback=self.ShowGraph)
        self.killsParent = uicls.Container(name='killsParent', parent=self.historyCont, align=uiconst.TOALL)
        self.killsScroll = uicls.Scroll(name='killsScroll', parent=self.killsParent)
        self.killsByGroupParent = uicls.Container(name='killsByGroupParent', parent=self.historyCont, align=uiconst.TOALL)
        killGroupsCont = uicls.Container(name='killsFilterCont', parent=self.killsByGroupParent, align=uiconst.TOTOP, height=188)
        self.killGroupsTextCont = uicls.Container(name='killGroupsTextCont', parent=killGroupsCont, align=uiconst.TOLEFT, width=90)
        self.killGroupsLegendCont = uicls.Container(name='killGroupsTextCont', parent=killGroupsCont, align=uiconst.TOBOTTOM, height=20)
        self.killGroupsDataCont = uicls.Container(name='killGroupsDataCont', parent=killGroupsCont, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         0,
         const.defaultPadding), bgColor=util.Color.GetGrayRGBA(0.4, 0.2))
        self.killGroupsScroll = uicls.Scroll(name='killGroupsScroll', parent=self.killsByGroupParent)
        self.LoadInfo(self.warID)

    def SetAllyBtnIcon(self):
        if len(self.allies):
            texturePath = 'res:/UI/Texture/Icons/Mercenary_Ally_64.png'
        elif self.IsOpenForAllies():
            texturePath = 'res:/UI/Texture/Icons/Mercenary_Add_64.png'
        else:
            texturePath = 'res:/UI/Texture/Icons/Mercenary_64.png'
        self.allyBtn.icon.LoadIcon(texturePath)

    def _ShowInvContLoadingWheel(self):
        blue.synchro.SleepWallclock(500)
        wheel = uicls.LoadingWheel(parent=self.loadingCont, align=uiconst.CENTER)
        while self.loading:
            blue.synchro.Yield()

        wheel.Close()

    def ShowLoading(self):
        self.loading = True
        uthread.new(self._ShowInvContLoadingWheel)
        self.loadingCont.display = True
        self.historyCont.display = False

    def HideLoading(self):
        self.loading = False
        self.loadingCont.display = False
        self.historyCont.display = True

    def IsOpenForAllies(self):
        return self.war.openForAllies

    def LoadInfo(self, warID):
        uthread.new(self.LoadInfo_thread, warID)

    def LoadInfo_thread(self, warID):
        if warID == self.warID:
            if self.showGraph.checked:
                if self.graphLoaded:
                    return
            elif self.killsLoaded:
                return
        self.warStatisticMoniker = self.GetWarStatisticMoniker(warID)
        self.war, shipsKilled, iskKilled, self.allies = self.warStatisticMoniker.GetBaseInfo()
        attackerID, defenderID = self.war.declaredByID, self.war.againstID
        if self.war.mutual:
            self.warDateLabel.top = -6
            self.mutualWarLabel.top = 8
            self.mutualWarLabel.display = True
        else:
            self.warDateLabel.top = 0
            self.mutualWarLabel.top = 0
            self.mutualWarLabel.display = False
        if not len(self.allies):
            self.allyBtn.Disable()
            self.allyBtn.hint = localization.GetByLabel('UI/Corporations/Wars/DefenderHasNoAllies')
        else:
            self.allyBtn.Enable()
            self.allyBtn.hint = localization.GetByLabel('UI/Corporations/Wars/DefenderHasNumAllies', num=len(self.allies))
        self.SetAllyBtnIcon()
        self.attackerLogoDetailed.Flush()
        self.defenderLogoDetailed.Flush()
        self.killsByShipGroup.clear()
        self.killsLoaded = False
        self.graphLoaded = False
        requesterID = session.allianceid or session.corpid
        if requesterID in (attackerID, defenderID) and self.war.retracted is None:
            if const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector:
                self.surrenderBtn.display = True
                self.surrenderBtn.hint = localization.GetByLabel('UI/Corporations/Wars/OffereToSurrender')
                surrenders = sm.GetService('war').GetSurrenderNegotiations(warID)
                for surrender in surrenders:
                    iskValue = surrender.iskValue
                    self.warNegotiationID = surrender.warNegotiationID
                    corpName = cfg.eveowners.Get(surrender.ownerID1).name
                    self.surrenderBtn.hint = localization.GetByLabel('UI/Corporations/Wars/OfferedToSurrender', amount=iskValue, corpName=corpName)

        shipsKilledByID = dict(shipsKilled)
        iskKilledByID = dict(iskKilled)
        if warID != self.warID:
            self.warID = warID
        if attackerID != self.attackerID:
            self.attackerID = attackerID
        if defenderID != self.defenderID:
            self.defenderID = defenderID
        self.warDateLabel.text = self.GetWarDateText()
        uicls.Frame(parent=self.attackerLogoDetailed, color=ATTACKER_COLOR)
        if util.IsCorporation(self.attackerID):
            attackerLinkType = const.typeCorporation
        else:
            attackerLinkType = const.typeAlliance
        attackerLogo = uiutil.GetLogoIcon(itemID=self.attackerID, parent=self.attackerLogoDetailed, acceptNone=False, align=uiconst.TOPRIGHT, height=64, width=64, state=uiconst.UI_NORMAL, ignoreSize=True)
        attackerLogo.OnClick = (self.ShowInfo, self.attackerID, attackerLinkType)
        attackerName = cfg.eveowners.Get(self.attackerID).name
        attackerLogo.hint = '%s<br>%s' % (attackerName, localization.GetByLabel('UI/Corporations/Wars/Offender'))
        attackerNameLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=attackerName, info=('showinfo', attackerLinkType, self.attackerID))
        self.attackerNameLabel.text = attackerNameLabel
        self.attackerShipsLostLabel.text = localization.GetByLabel('UI/Corporations/Wars/NumShipsKilled', ships=util.FmtAmt(shipsKilledByID.get(self.attackerID, 0)))
        self.attackerISKLostLabel.text = localization.GetByLabel('UI/Corporations/Wars/ISKKilled', iskAmount=util.FmtISK(iskKilledByID.get(self.attackerID, 0), 0))
        uicls.Frame(parent=self.defenderLogoDetailed, color=DEFENDER_COLOR)
        if util.IsCorporation(self.defenderID):
            defenderLinkType = const.typeCorporation
        else:
            defenderLinkType = const.typeAlliance
        defenderLogo = uiutil.GetLogoIcon(itemID=self.defenderID, parent=self.defenderLogoDetailed, acceptNone=False, align=uiconst.TOPLEFT, height=64, width=64, state=uiconst.UI_NORMAL, ignoreSize=True)
        defenderLogo.OnClick = (self.ShowInfo, self.defenderID, defenderLinkType)
        defenderName = cfg.eveowners.Get(self.defenderID).name
        defenderLogo.hint = '%s<br>%s' % (defenderName, localization.GetByLabel('UI/Corporations/Wars/Defender'))
        defenderNameLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=defenderName, info=('showinfo', defenderLinkType, self.defenderID))
        self.defenderNameLabel.text = defenderNameLabel
        self.defenderShipsKilledLabel.text = localization.GetByLabel('UI/Corporations/Wars/NumShipsKilled', ships=util.FmtAmt(shipsKilledByID.get(self.defenderID, 0)))
        self.defenderISKKilledLabel.text = localization.GetByLabel('UI/Corporations/Wars/ISKKilled', iskAmount=util.FmtISK(iskKilledByID.get(self.defenderID, 0), 0))
        self.ShowLoading()
        self.GetMaxKills()
        self.ShowGraph()
        self.HideLoading()

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def OpenAllyWnd(self, *args):
        form.AllyWnd.CloseIfOpen()
        form.AllyWnd.Open(war=self.war, allies=self.allies)

    def OpenSurrenderWnd(self, *args):
        if self.warNegotiationID:
            form.WarSurrenderWnd.CloseIfOpen()
            form.WarSurrenderWnd.Open(warNegotiationID=self.warNegotiationID, isRequest=False)
        else:
            form.WarSurrenderWnd.CloseIfOpen()
            requesterID = session.corpid if session.allianceid is None else session.allianceid
            form.WarSurrenderWnd.Open(war=self.war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)

    def GetWarDateText(self):
        war = self.war
        date = util.FmtDate(war.timeDeclared, 'sn') if war.timeDeclared else localization.GetByLabel('UI/Common/Unknown')
        warFinished = util.FmtDate(war.timeFinished, 'sn') if war.timeFinished else None
        warRetracted = util.FmtDate(war.retracted, 'sn') if war.retracted is not None else None
        warMutual = war.mutual
        if blue.os.GetWallclockTime() <= war.timeStarted:
            fightTime = util.FmtDate(war.timeStarted, 'ns')
            timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedCanFightDetailed', date=date, time=fightTime)
        elif warFinished:
            if blue.os.GetWallclockTime() < war.timeFinished:
                endTime = util.FmtDate(war.timeFinished, 'ns')
                timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedEndsAt', date=date, time=endTime)
            else:
                timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedAndFinished', startDate=date, finishDate=warFinished)
        elif warRetracted:
            timeText = localization.GetByLabel('UI/Corporations/Wars/WarStartedWarRetracted', date=date, endDate=warRetracted)
        else:
            timeText = localization.GetByLabel('UI/Corporations/Wars/WarStarted', date=date)
        return timeText

    def GetKills(self, scroll, shipGroup = None):
        sortedScrolllist = []
        myDate = None
        killValue = self.killsFilterCombo.GetValue()
        kills = self.warStatisticMoniker.GetKills(killValue, shipGroup)
        validGroupIDs = None
        if shipGroup is not None:
            validGroupIDs = cfg.GetShipGroupByClassType()[shipGroup]
        for kill in kills:
            if self.attackerID in (kill.finalCorporationID, kill.finalAllianceID):
                attackerKill = True
            else:
                attackerKill = False
            if killValue == 'attacker' and attackerKill == False:
                continue
            elif killValue == 'defender' and attackerKill == True:
                continue
            data = util.KeyVal()
            data.label = ''
            data.killID = kill.killID
            data.killTime = kill.killTime
            data.finalCharacterID = kill.finalCharacterID
            data.finalCorporationID = kill.finalCorporationID
            data.finalAllianceID = kill.finalAllianceID
            data.victimCharacterID = kill.victimCharacterID
            data.victimCorporationID = kill.victimCorporationID
            data.victimAllianceID = kill.victimAllianceID
            data.victimShipTypeID = kill.victimShipTypeID
            data.attackerKill = attackerKill
            data.mail = kill
            sortedScrolllist.append((kill.killTime, listentry.Get('WarKillEntry', data=data)))

        sortedScrolllist = uiutil.SortListOfTuples(sortedScrolllist, reverse=True)
        scrolllist = []
        for entry in sortedScrolllist:
            if myDate is None or myDate != util.FmtDate(entry.killTime, 'sn'):
                scrolllist.append(listentry.Get('Header', {'label': util.FmtDate(entry.killTime, 'sn')}))
                myDate = util.FmtDate(entry.killTime, 'sn')
            scrolllist.append(entry)

        scroll.Load(contentList=scrolllist, headers=[], noContentHint=localization.GetByLabel('UI/Corporations/Wars/NoKillsFound'))

    def OnKillComboChange(self, *args):
        comboSetting = settings.user.ui.Get('killComboValue', 0)
        comboValue = self.killsFilterCombo.GetValue()
        if comboValue == comboSetting:
            return
        settings.user.ui.Set('killComboValue', comboValue)
        groupID = settings.user.ui.Get('killGroupDisplayed', 0)
        self.GetKills(self.killGroupsScroll, groupID)
        self.GetKills(self.killsScroll)
        self.DrawKillsByGroup()

    def DrawKillsByGroup(self):
        self.killGroupsTextCont.Flush()
        self.killGroupsDataCont.Flush()
        self.killGroupsLegendCont.Flush()
        top = 2
        self.groupLabels = []
        for shipGroup in self.shipGroupList:
            killsByShipGroup = self.GetKillsByGroup(shipGroup)
            labelText = self.GetShipGroupName(shipGroup)
            groupLabel = uicls.EveLabelSmall(text=localization.GetByLabel(labelText), parent=self.killGroupsTextCont, top=top, left=const.defaultPadding, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
            groupLabel.OnClick = (self.GetBarAndClick, shipGroup)
            if killsByShipGroup.attackerKills == 0 and killsByShipGroup.defenderKills == 0:
                groupLabel.SetAlpha(0.5)
            top += 18
            self.groupLabels.append(groupLabel)
            self.CreateBarContainer(shipGroup, killsByShipGroup.attackerKills, killsByShipGroup.defenderKills, killsByShipGroup.attackerKillsIsk, killsByShipGroup.defenderKillsIsk)

        w, h = self.killGroupsDataCont.GetAbsoluteSize()
        l = 0.1
        max = 1.0
        legendmin = uicls.EveLabelSmall(parent=self.killGroupsLegendCont, text=localization.GetByLabel('UI/Corporations/Wars/Legend', legend=util.FmtISK(0)), align=uiconst.TOPLEFT)
        legendmax = uicls.EveLabelSmall(parent=self.killGroupsLegendCont, text=localization.GetByLabel('UI/Corporations/Wars/Legend', legend=util.FmtISK(self.maxKills)), align=uiconst.TOPRIGHT)
        while l <= max:
            lineCont = uicls.Container(parent=self.killGroupsDataCont, align=uiconst.TOPLEFT_PROP, width=l, height=h)
            uicls.Line(parent=lineCont, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.1))
            l += 0.1

        self.displayGroup = settings.user.ui.Get('killGroupDisplayed', const.GROUP_CAPSULES)
        maxWidth = self.GetGroupLabelWidth()
        self.killGroupsTextCont.width = maxWidth + 10
        self.GetBarAndClick(self.displayGroup)
        self.graphLoaded = True

    def GetGroupLabelWidth(self):
        maxWidth = 0
        for label in self.groupLabels:
            maxWidth = max(maxWidth, label.textwidth)

        return maxWidth

    def CreateBarContainer(self, groupID, attackerKills, defenderKills, attackerKillsIsk, defenderKillsIsk):
        killValue = self.killsFilterCombo.GetValue()
        if killValue == 'defender':
            attackerKills = 0
        elif killValue == 'attacker':
            defenderKills = 0
        contName = 'group_%d' % groupID
        barCont = uicls.KillsBarContainer(name=contName, parent=self.killGroupsDataCont, attackerID=self.attackerID, defenderID=self.defenderID, attackerKills=attackerKills, defenderKills=defenderKills, attackerKillsIsk=attackerKillsIsk, defenderKillsIsk=defenderKillsIsk, groupID=groupID, maxKills=self.maxKills)
        setattr(self.sr, contName, barCont)
        barCont.OnClick = (self.BarOnClick, groupID, barCont)

    def GetBarAndClick(self, groupID, *args):
        groupName = 'group_%d' % groupID
        bar = getattr(self.sr, groupName, None)
        self.BarOnClick(groupID, bar)

    def BarOnClick(self, groupID, container, *args):
        settings.user.ui.Set('killGroupDisplayed', groupID)
        self.displayGroup = groupID
        for i in xrange(0, len(self.shipGroupList)):
            cont = self.sr.Get('group_%d' % i)
            cont.sr.selected.state = uiconst.UI_HIDDEN

        container.sr.selected.state = uiconst.UI_DISABLED
        self.GetKills(self.killGroupsScroll, groupID)

    def GetKillsByGroup(self, shipGroupID = None):
        self.PrimeKillsByGroup()
        if shipGroupID is not None:
            return self.killsByShipGroup[shipGroupID]
        else:
            return self.killsByShipGroup

    def PrimeKillsByGroup(self):
        if self.killsByShipGroup == {}:
            killsByGroup = self.warStatisticMoniker.GetKillsByGroup()
            for groupID, groupInfo in killsByGroup.iteritems():
                classTypeID = cfg.GetShipClassTypeByGroupID(groupID)
                self.killsByShipGroup[classTypeID].attackerKills += groupInfo['defenderShipLoss']
                self.killsByShipGroup[classTypeID].defenderKills += groupInfo['attackerShipLoss']
                self.killsByShipGroup[classTypeID].attackerKillsIsk += groupInfo['defenderIskLoss']
                self.killsByShipGroup[classTypeID].defenderKillsIsk += groupInfo['attackerIskLoss']

    def GetMaxKills(self):
        killsByGroup = self.GetKillsByGroup()
        if not killsByGroup:
            return 10
        maxKills = max((max(kills.attackerKillsIsk, kills.defenderKillsIsk) for kills in self.GetKillsByGroup().itervalues()))
        if maxKills < 10:
            return 10
        exp = math.ceil(math.log(maxKills, 10))
        self.maxKills = 10 ** exp
        if float(maxKills) / self.maxKills < 0.5:
            self.maxKills = self.maxKills * 0.5
        self.maxKills = max(10, self.maxKills)

    def GetShipGroupName(self, shipGroup):
        if self.shipGroupNames is None:
            self.shipGroupNames = {const.GROUP_CAPSULES: 'UI/Corporations/Wars/ShipGroups/Capsules',
             const.GROUP_FRIGATES: 'UI/Corporations/Wars/ShipGroups/Frigate',
             const.GROUP_DESTROYERS: 'UI/Corporations/Wars/ShipGroups/Destroyers',
             const.GROUP_CRUISERS: 'UI/Corporations/Wars/ShipGroups/Cruisers',
             const.GROUP_BATTLECRUISERS: 'UI/Corporations/Wars/ShipGroups/Battlecruisers',
             const.GROUP_BATTLESHIPS: 'UI/Corporations/Wars/ShipGroups/Battleships',
             const.GROUP_CAPITALSHIPS: 'UI/Corporations/Wars/ShipGroups/CapitalShips',
             const.GROUP_INDUSTRIALS: 'UI/Corporations/Wars/ShipGroups/IndustrialShips',
             const.GROUP_POS: 'UI/Corporations/Wars/ShipGroups/POS'}
        return self.shipGroupNames[shipGroup]

    def GetShipGroupList(self):
        if self.shipGroupList == []:
            self.shipGroupList.append(const.GROUP_CAPSULES)
            self.shipGroupList.append(const.GROUP_FRIGATES)
            self.shipGroupList.append(const.GROUP_DESTROYERS)
            self.shipGroupList.append(const.GROUP_CRUISERS)
            self.shipGroupList.append(const.GROUP_BATTLESHIPS)
            self.shipGroupList.append(const.GROUP_BATTLECRUISERS)
            self.shipGroupList.append(const.GROUP_CAPITALSHIPS)
            self.shipGroupList.append(const.GROUP_INDUSTRIALS)
            self.shipGroupList.append(const.GROUP_POS)

    def ShowGraph(self, *args):
        showGraph = self.showGraph.checked
        settings.user.ui.Set('killShowGraph', showGraph)
        if showGraph:
            uicore.animations.FadeOut(self.killsParent, duration=0.3)
            self.killsParent.Disable()
            uicore.animations.FadeIn(self.killsByGroupParent, duration=0.3)
            self.killsByGroupParent.Enable()
            if not self.graphLoaded:
                self.DrawKillsByGroup()
                self.graphLoaded = True
        else:
            uicore.animations.FadeOut(self.killsByGroupParent, duration=0.3)
            self.killsByGroupParent.Disable()
            uicore.animations.FadeIn(self.killsParent, duration=0.3)
            self.killsParent.Enable()
            if not self.killsLoaded:
                self.GetKills(self.killsScroll)
                self.killsLoaded = True


class WarKillEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.WarKillEntry'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.copyicon = uicls.Icon(icon='ui_73_16_1', parent=self, pos=(3, 3, 16, 16), align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/Control/Entries/CopyKillInfo'))
        self.copyicon.OnClick = self.GetCombatText
        iconCont = uicls.Container(parent=self, align=uiconst.TOLEFT, width=40)
        self.shipCont = uicls.Container(parent=iconCont, align=uiconst.CENTER, width=32, height=32)
        self.shipFrame = uicls.Frame(parent=self.shipCont)
        self.shipIcon = uicls.Icon(parent=self.shipCont, align=uiconst.TOALL, size=256, ignoreSize=True)
        self.shipIcon.cursor = uiconst.UICURSOR_MAGNIFIER
        self.shipIcon.OnClick = (self.OnPreviewClick, self.shipIcon)
        self.shipIcon.OnMouseEnter = self.OnControlEnter
        self.shipIcon.OnMouseExit = self.OnControlExit
        self.techIcon = uicls.Sprite(name='techIcon', parent=self.shipCont, align=uiconst.RELATIVE, width=16, height=16, idx=0, left=1, top=1)
        self.techIcon.OnMouseEnter = self.OnControlEnter
        self.techIcon.OnMouseExit = self.OnControlExit
        self.timeCont = uicls.Container(parent=self, align=uiconst.TORIGHT, width=35, padRight=6)
        self.textCont = uicls.Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self.victimLabel = uicls.EveLabelMedium(text='', parent=self.textCont, left=5, top=3, state=uiconst.UI_NORMAL, maxLines=1)
        self.killerLabel = uicls.EveLabelMedium(text='', parent=self.textCont, left=5, top=20, state=uiconst.UI_NORMAL, maxLines=1)
        self.dateLabel = uicls.EveLabelMedium(text='', parent=self.timeCont, align=uiconst.TOPRIGHT, top=20)
        self.victimLabel.OnMouseEnter = self.OnControlEnter
        self.victimLabel.OnMouseExit = self.OnControlExit
        self.killerLabel.OnMouseEnter = self.OnControlEnter
        self.killerLabel.OnMouseExit = self.OnControlExit
        self.hilite = uicls.Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.1), idx=0)
        self.hilite.display = False

    def Load(self, node):
        self.sr.node = node
        self.killID = node.killID
        self.killTime = node.killTime
        self.finalCharacterID = node.finalCharacterID
        self.finalCorporationID = node.finalCorporationID
        self.finalAllianceID = node.finalAllianceID
        self.victimCharacterID = node.victimCharacterID
        self.victimCorporationID = node.victimCorporationID
        self.victimAllianceID = node.victimAllianceID
        self.victimShipTypeID = node.victimShipTypeID
        self.attackerKill = node.attackerKill
        self.DisplayInfo()

    def DisplayInfo(self):
        uix.GetTechLevelIcon(self.techIcon, 0, self.victimShipTypeID)
        self.shipIcon.LoadIconByTypeID(typeID=self.victimShipTypeID)
        self.shipIcon.typeID = self.victimShipTypeID
        self.shipIcon.hint = cfg.invtypes.Get(self.victimShipTypeID).typeName
        if self.attackerKill:
            color = ATTACKER_COLOR
        else:
            color = DEFENDER_COLOR
        self.shipFrame.color = color
        try:
            victimName = cfg.eveowners.Get(self.victimCharacterID).name
            victimInfo = ('showinfo', const.typeCharacterGallente, self.victimCharacterID)
        except:
            victimName = cfg.invtypes.Get(self.victimShipTypeID).typeName
            victimInfo = ('showinfo', self.victimShipTypeID)

        victimCorp = cfg.eveowners.Get(self.victimCorporationID).name
        victimCorpInfo = ('showinfo', const.typeCorporation, self.victimCorporationID)
        if self.victimAllianceID:
            victimAlliance = cfg.eveowners.Get(self.victimAllianceID).name
            victimAllianceInfo = ('showinfo', const.typeAlliance, self.victimAllianceID)
            victimLabel = localization.GetByLabel('UI/Corporations/Wars/KillVictimInAlliance', victimName=victimName, victimInfo=victimInfo, victimCorp=victimCorp, victimCorpInfo=victimCorpInfo, victimAlliance=victimAlliance, victimAllianceInfo=victimAllianceInfo)
        else:
            victimLabel = localization.GetByLabel('UI/Corporations/Wars/KillVictim', victimName=victimName, victimInfo=victimInfo, victimCorp=victimCorp, victimCorpInfo=victimCorpInfo)
        self.victimLabel.text = victimLabel
        killerName = cfg.eveowners.Get(self.finalCharacterID).name
        killerInfo = ('showinfo', const.typeCharacterGallente, self.finalCharacterID)
        killerCorp = cfg.eveowners.Get(self.finalCorporationID).name
        killerCorpInfo = ('showinfo', const.typeCorporation, self.finalCorporationID)
        if self.finalAllianceID:
            killerAlliance = cfg.eveowners.Get(self.finalAllianceID).name
            killerAllianceInfo = ('showinfo', const.typeAlliance, self.finalAllianceID)
            killerLabel = localization.GetByLabel('UI/Corporations/Wars/KillKillerInAlliance', killerName=killerName, killerInfo=killerInfo, killerCorp=killerCorp, killerCorpInfo=killerCorpInfo, killerAlliance=killerAlliance, killerAllianceInfo=killerAllianceInfo)
        else:
            killerLabel = localization.GetByLabel('UI/Corporations/Wars/KillKiller', killerName=killerName, killerInfo=killerInfo, killerCorp=killerCorp, killerCorpInfo=killerCorpInfo)
        self.killerLabel.text = killerLabel
        self.dateLabel.text = util.FmtDate(self.killTime, 'ns')

    def GetHeight(self, *args):
        node, width = args
        node.height = 41
        return node.height

    def OnPreviewClick(self, obj, *args):
        sm.GetService('preview').PreviewType(getattr(obj, 'typeID'))

    def OnMouseEnter(self, *args):
        self.hilite.display = True

    def OnMouseExit(self, *args):
        self.hilite.display = False

    def OnControlEnter(self, *args):
        self.hilite.display = True

    def OnControlExit(self, *args):
        self.hilite.display = False

    def GetFullKillReport(self):
        hashValue = util.GetKillReportHashValue(self.sr.node.mail)
        return sm.RemoteSvc('warStatisticMgr').GetKillMail(self.killID, hashValue)

    def OnDblClick(self, *args):
        kill = self.GetFullKillReport()
        if kill is not None:
            wnd = form.KillReportWnd.GetIfOpen()
            if wnd:
                wnd.LoadInfo(killmail=kill)
                wnd.Maximize()
            else:
                form.KillReportWnd.Open(create=1, killmail=kill)

    def GetCombatText(self, *args):
        kill = self.GetFullKillReport()
        ret = util.CombatLog_CopyText(kill)
        blue.pyos.SetClipboardData(util.CleanKillMail(ret))

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes


class KillsBarContainer(uicls.Container):
    __guid__ = 'uicls.KillsBarContainer'
    default_height = 18
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.attackerID = attributes.get('attackerID', None)
        self.defenderID = attributes.get('defenderID', None)
        self.attackerKills = attributes.get('attackerKills', 0)
        self.defenderKills = attributes.get('defenderKills', 0)
        self.attackerKillsIsk = attributes.get('attackerKillsIsk', 0)
        self.defenderKillsIsk = attributes.get('defenderKillsIsk', 0)
        self.groupID = attributes.get('groupID', None)
        self.maxKills = attributes.get('maxKills', 0)
        self.ConstructLayout()

    def ConstructLayout(self):
        contName = 'group_%d' % self.groupID
        self.sr.selected = uicls.Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.15), state=uiconst.UI_HIDDEN)
        self.sr.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.1), state=uiconst.UI_HIDDEN)
        self.OnMouseEnter = self.BarOnMouseEnter
        self.OnMouseExit = self.BarOnMouseExit
        attackerName = cfg.eveowners.Get(self.attackerID).name
        defenderName = cfg.eveowners.Get(self.defenderID).name
        hintText = localization.GetByLabel('UI/Corporations/Wars/AggressorDefenderKillsHint', aggressorName=attackerName, aggressorKillsIsk=util.FmtISK(self.attackerKillsIsk, 0), aggressorKills=util.FmtAmt(self.attackerKills), defenderName=defenderName, defenderKillsIsk=util.FmtISK(self.defenderKillsIsk, 0), defenderKills=util.FmtAmt(self.defenderKills))
        self.hint = hintText
        topbar = uicls.Container(name='topbar', parent=self, align=uiconst.TOTOP, height=5, padTop=4)
        try:
            redwith = float(self.attackerKillsIsk) / float(self.maxKills)
        except:
            redwith = 0.0

        redbar = uicls.Container(parent=topbar, align=uiconst.TOLEFT_PROP, width=redwith, height=5, bgColor=ATTACKER_COLOR)
        bottombar = uicls.Container(name='bluebar', parent=self, align=uiconst.TOBOTTOM, height=5, padBottom=4)
        try:
            bluewith = float(self.defenderKillsIsk) / float(self.maxKills)
        except:
            bluewith = 0.0

        bluebar = uicls.Container(parent=bottombar, align=uiconst.TOLEFT_PROP, width=bluewith, height=5, bgColor=DEFENDER_COLOR)

    def BarOnMouseEnter(self, *args):
        self.sr.hilite.state = uiconst.UI_DISABLED

    def BarOnMouseExit(self, *args):
        self.sr.hilite.state = uiconst.UI_HIDDEN