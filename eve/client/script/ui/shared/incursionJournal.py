import uiconst
import uicls
import uiutil
from mapcommon import STARMODE_INCURSION, STARMODE_FRIENDS_CORP
import uix
import util
import taleCommon
import localization

class IncursionTab:
    (GlobalReport, Encounters, LPLog,) = range(3)


class GlobalIncursionReportEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.GlobalIncursionReportEntry'
    MARGIN = 8
    TEXT_OFFSET = 84
    BUTTON_OFFSET = 295

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.iconsize = iconsize = 44
        btnHeight = self.GetHeight() - (iconsize + self.MARGIN)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.75))
        self.factionParent = uicls.Container(name='factionParent', parent=self, align=uiconst.TOLEFT, pos=(0, 0, 64, 64), padding=(self.MARGIN,) * 4)
        middleCont = uicls.Container(parent=self, name='middleContainer', width=200, align=uiconst.TOLEFT, padding=(0,
         self.MARGIN,
         0,
         0), clipChildren=True)
        self.constellationLabel = BigReportLabel(name='constellationName', parent=middleCont, fontsize=20, text='', align=uiconst.RELATIVE, state=uiconst.UI_NORMAL)
        self.statusText = SmallReportLabel(parent=middleCont, align=uiconst.RELATIVE, top=20, text='', uppercase=True)
        SmallReportLabel(name='systemInfluence', parent=middleCont, top=35, text=localization.GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'))
        self.statusBar = uicls.SystemInfluenceBar(parent=middleCont, pos=(0, 50, 200, 16), align=uiconst.RELATIVE, padding=(0, 4, 0, 4))
        self.stagingText = SmallReportLabel(parent=middleCont, align=uiconst.RELATIVE, top=68, text='', state=uiconst.UI_NORMAL)
        self.bossIcon = uicls.IncursionBossIcon(parent=middleCont, left=3, top=3, align=uiconst.TOPRIGHT)
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET, top=btnHeight)
        btn.hint = localization.GetByLabel('UI/Incursion/Journal/ShowActiveCorpMembersInMap')
        btn.sr.icon.LoadIcon('ui_7_64_4', ignoreSize=True)
        uicls.Icon(name='subicon', icon='ui_7_64_6', parent=btn, idx=0, size=32, align=uiconst.BOTTOMRIGHT, ignoreSize=True, color=(1, 1, 1, 0.85), state=uiconst.UI_DISABLED)
        self.corpMapButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET + 50, top=btnHeight)
        btn.hint = localization.GetByLabel('UI/Incursion/Journal/ShowOnStarMap')
        btn.sr.icon.LoadIcon('ui_7_64_4', ignoreSize=True)
        self.mapButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET + 100, top=btnHeight)
        btn.hint = localization.GetByLabel('UI/Incursion/Journal/StagingAsAutopilotDestination')
        btn.sr.icon.LoadIcon('ui_9_64_5', ignoreSize=True)
        self.autopilotButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET, top=self.MARGIN)
        btn.hint = localization.GetByLabel('UI/Incursion/Journal/ViewLoyaltyPointLog')
        btn.sr.icon.LoadIcon('ui_70_64_11', ignoreSize=True)
        self.lpButton = btn
        self.loyaltyPoints = ReportNumber(name='loyaltyPoints', parent=self, pos=(self.BUTTON_OFFSET + 50,
         self.MARGIN,
         100,
         iconsize), number=0, hint=localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointsWin'), padding=(4, 4, 4, 4))



    def Load(self, data):
        iconsize = 48
        self.factionParent.Flush()
        if data.factionID:
            owner = cfg.eveowners.Get(data.factionID)
            uiutil.GetLogoIcon(parent=self.factionParent, align=uiconst.RELATIVE, size=64, itemID=data.factionID, ignoreSize=True, hint=localization.GetByLabel('UI/Incursion/Journal/FactionStagingRuler', faction=owner.ownerName))
        else:
            uicls.Icon(parent=self.factionParent, size=64, icon='ui_94_64_16', ignoreSize=True, hint=localization.GetByLabel('UI/Incursion/Journal/StagingSystemUnclaimed'), align=uiconst.RELATIVE)
        params = {'constellation': data.constellationID,
         'constellationInfo': ('showinfo', const.typeConstellation, data.constellationID)}
        self.constellationLabel.SetText(localization.GetByLabel('UI/Incursion/Journal/ReportRowHeader', **params))
        incursionStateMessages = [localization.GetByLabel('UI/Incursion/Journal/Withdrawing'), localization.GetByLabel('UI/Incursion/Journal/Mobilizing'), localization.GetByLabel('UI/Incursion/Journal/Established')]
        self.statusText.SetText(incursionStateMessages[data.state])
        params = {'color': '<color=' + sm.GetService('map').GetSystemColorString(data.stagingSolarSystemID) + '>',
         'security': data.security,
         'securityColor': sm.GetService('map').GetSystemColorString(data.stagingSolarSystemID),
         'system': data.stagingSolarSystemID,
         'systemInfo': ('showinfo', const.typeSolarSystem, data.stagingSolarSystemID)}
        if data.jumps is None:
            self.stagingText.SetText(localization.GetByLabel('UI/Incursion/Journal/ReportRowWormhole', **params))
        else:
            params['jumps'] = data.jumps
            self.stagingText.SetText(localization.GetByLabel('UI/Incursion/Journal/ReportRow', **params))
        self.statusBar.SetInfluence(taleCommon.CalculateDecayedInfluence(data.influenceData), None, animate=False)
        self.bossIcon.SetBossSpawned(data.hasBoss)
        self.corpMapButton.OnClick = lambda : sm.GetService('viewState').ActivateView('starmap', interestID=data.constellationID, starColorMode=STARMODE_FRIENDS_CORP)
        self.mapButton.OnClick = lambda : sm.GetService('viewState').ActivateView('starmap', interestID=data.constellationID, starColorMode=STARMODE_INCURSION)
        self.autopilotButton.OnClick = lambda : sm.GetService('starmap').SetWaypoint(data.stagingSolarSystemID, clearOtherWaypoints=True)
        self.lpButton.OnClick = lambda : sm.GetService('journal').ShowIncursionTab(flag=IncursionTab.LPLog, taleID=data.taleID, constellationID=data.constellationID)
        self.loyaltyPoints.number.SetText(localization.GetByLabel('UI/Incursion/Journal/NumberLoyaltyPointsAcronym', points=util.FmtAmt(data.loyaltyPoints)))



    def GetHeight(*args):
        return 114




class ReportNumber(uicls.Container):
    __guid__ = 'incursion.ReportNumber'
    default_align = uiconst.RELATIVE
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        number = attributes.Get('number', 0)
        self.number = BigReportLabel(name='bignumber', parent=self, align=uiconst.CENTERRIGHT, text=str(number), fontsize=24, hint=attributes.Get('hint', None))




class SmallReportLabel(uicls.Label):
    default_align = uiconst.RELATIVE
    default_fontsize = 13


class BigReportLabel(uicls.Label):
    __guid__ = 'incursion.ReportLabel'
    default_fontsize = 20
    default_letterspace = 0
    default_align = uiconst.RELATIVE
    default_singleline = False

exports = {'incursion.IncursionTab': IncursionTab}

