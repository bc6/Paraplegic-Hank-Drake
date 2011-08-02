import uiconst
import uicls
import uiutil
from mapcommon import STARMODE_INCURSION, STARMODE_FRIENDS_CORP
import uix
import util
import taleCommon

class IncursionTab:
    (GlobalReport, Encounters, LPLog,) = range(3)

INCURSION_STATE_MESSAGES = [mls.UI_SHARED_INCURSION_STATE_WITHDRAWING, mls.UI_SHARED_INCURSION_STATE_MOBILIZING, mls.UI_SHARED_INCURSION_STATE_ESTABLISHED]

class GlobalIncursionReportEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.GlobalIncursionReportEntry'
    MARGIN = 8
    TEXT_OFFSET = 84
    BUTTON_OFFSET = 295
    INFO_LINK = '<url=showinfo:%d//%d>%s</url>'
    REPORT_HTML = '%(stagingSolarSystem)s:<br><color=%(securityColor)s>\x95 %(security)1.1f<color=0xccffffff> %(systemName)s (%(jumps)s)'

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
        self.statusText = SmallReportLabel(parent=middleCont, align=uiconst.RELATIVE, top=20, text='')
        SmallReportLabel(name='systemInfluence', parent=middleCont, top=35, text=mls.UI_SHARED_INCURSION_HUD_INFLUENCE_TITLE)
        self.statusBar = uicls.SystemInfluenceBar(parent=middleCont, pos=(0, 50, 200, 16), align=uiconst.RELATIVE, padding=(0, 4, 0, 4))
        self.stagingText = SmallReportLabel(parent=middleCont, align=uiconst.RELATIVE, top=68, text='', state=uiconst.UI_NORMAL)
        self.bossIcon = uicls.IncursionBossIcon(parent=middleCont, left=3, top=3, align=uiconst.TOPRIGHT)
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET + 0, top=btnHeight)
        btn.hint = mls.UI_SHARED_INCURSION_REPORT_HINT_MAP_CORP_MATES_ACTIVE
        btn.sr.icon.LoadIcon('ui_7_64_4', ignoreSize=True)
        uicls.Icon(name='subicon', icon='ui_7_64_6', parent=btn, idx=0, size=32, align=uiconst.BOTTOMRIGHT, ignoreSize=True, color=(1, 1, 1, 0.85), state=uiconst.UI_DISABLED)
        self.corpMapButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET + 50, top=btnHeight)
        btn.hint = mls.UI_SHARED_INCURSION_REPORT_HINT_STARMAP
        btn.sr.icon.LoadIcon('ui_7_64_4', ignoreSize=True)
        self.mapButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET + 100, top=btnHeight)
        btn.hint = mls.UI_SHARED_INCURSION_REPORT_HINT_AUTOPILOT
        btn.sr.icon.LoadIcon('ui_9_64_5', ignoreSize=True)
        self.autopilotButton = btn
        btn = uix.GetBigButton(iconsize, self, left=self.BUTTON_OFFSET, top=self.MARGIN)
        btn.hint = mls.UI_SHARED_INCURSION_REPORT_HINT_LPLOG
        btn.sr.icon.LoadIcon('ui_70_64_11', ignoreSize=True)
        self.lpButton = btn
        self.loyaltyPoints = ReportNumber(name='loyaltyPoints', parent=self, pos=(self.BUTTON_OFFSET + 50,
         self.MARGIN,
         100,
         iconsize), number=0, hint=mls.UI_SHARED_INCURSION_REPORT_HINT_LP, padding=(4, 4, 4, 4))



    def Load(self, data):
        starmap = sm.GetService('starmap')
        iconsize = 48
        self.factionParent.Flush()
        if data.factionID:
            owner = cfg.eveowners.Get(data.factionID)
            uiutil.GetLogoIcon(parent=self.factionParent, align=uiconst.RELATIVE, size=64, itemID=data.factionID, ignoreSize=True, hint=mls.UI_SHARED_INCURSION_REPORT_HINT_FACTION % {'faction': owner.ownerName})
        else:
            uicls.Icon(parent=self.factionParent, size=64, icon='ui_94_64_16', ignoreSize=True, hint=mls.UI_INCURSION_REPORT_HINT_UNCLAIMED, align=uiconst.RELATIVE)
        params = {'stagingSolarSystem': mls.UI_SHARED_INCURSION_STAGING_SYSTEM,
         'security': data.security,
         'securityColor': starmap.GetSystemColorString(data.stagingSolarSystemID),
         'systemName': self.INFO_LINK % (const.typeSolarSystem, data.stagingSolarSystemID, data.stagingSolarSystemName),
         'jumps': mls.UI_SHARED_NUM_JUMPS % {'num': data.jumps} if data.jumps is not None else mls.UI_GENERIC_UNREACHABLE.capitalize()}
        self.constellationLabel.SetText(self.INFO_LINK % (const.typeConstellation, data.constellationID, data.constellationName))
        self.statusText.SetText(INCURSION_STATE_MESSAGES[data.state].upper())
        self.stagingText.SetText(self.REPORT_HTML % params)
        self.statusBar.SetInfluence(taleCommon.CalculateDecayedInfluence(data.influenceData), None, animate=False)
        self.bossIcon.SetBossSpawned(data.hasBoss)
        self.corpMapButton.OnClick = lambda : starmap.Open(interestID=data.constellationID, starColorMode=STARMODE_FRIENDS_CORP)
        self.mapButton.OnClick = lambda : starmap.Open(interestID=data.constellationID, starColorMode=STARMODE_INCURSION)
        self.autopilotButton.OnClick = lambda : starmap.SetWaypoint(data.stagingSolarSystemID, clearOtherWaypoints=True)
        self.lpButton.OnClick = lambda : sm.GetService('journal').ShowIncursionTab(flag=IncursionTab.LPLog, taleID=data.taleID, constellationID=data.constellationID)
        self.loyaltyPoints.number.SetText('%s %s' % (util.FmtAmt(data.loyaltyPoints), mls.UI_GENERIC_LP))



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
    default_autoheight = True
    default_autowidth = True
    default_letterspace = 0
    default_align = uiconst.RELATIVE
    default_singleline = False

exports = {'incursion.IncursionTab': IncursionTab}

