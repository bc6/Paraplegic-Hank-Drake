import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import uicls
import uiconst
import log

class FormAlliancesRankings(uicls.Container):
    __guid__ = 'form.AlliancesRankings'
    __nonpersistvars__ = []

    def CreateWindow(self):
        self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        buttonOptions = [[mls.UI_CORP_RANKEDALLIANCES_SHOWALL,
          self.ShowRankings,
          (0,),
          81]]
        btns = uicls.ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
        self.toolbarContainer.height = btns.height
        self.sr.mainBtns = btns
        self.sr.scroll = uicls.Scroll(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ShowRankings()



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowRankings(self, maxLen = 100):
        log.LogInfo('ShowRankings', maxLen)
        sm.GetService('corpui').LoadTop('ui_7_64_6', mls.UI_GENERIC_ALLIANCES, mls.UI_CORP_RANKCACHED5)
        if maxLen == 0 and eve.Message('ConfirmShowAllRankedAlliances', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        try:
            sm.GetService('corpui').ShowLoad()
            headers = [mls.UI_GENERIC_NAME,
             mls.UI_CORP_EXECUTORCORP,
             mls.UI_CORP_SHORTNAME,
             mls.UI_CORP_CREATED,
             mls.UI_GENERIC_MEMBERS,
             mls.UI_GENERIC_CORPSTANDING]
            scrolllist = []
            hint = mls.UI_CORP_NORANKINGSFOUND
            if self is None or self.destroyed:
                log.LogInfo('ShowRankings Destroyed or None')
            else:
                data = sm.GetService('alliance').GetRankedAlliances(maxLen)
                rows = data.alliances
                owners = []
                for row in rows:
                    if row.executorCorpID not in owners:
                        owners.append(row.executorCorpID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for row in rows:
                    standing = data.standings.get(row.allianceID, 0)
                    self._FormAlliancesRankings__AddToList(row, standing, scrolllist)

            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'alliances_rankings'
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_CORP_NORANKINGSFOUND)

        finally:
            sm.GetService('corpui').HideLoad()




    def __GetLabel(self, row, standing):
        executor = None
        if row.executorCorpID is not None:
            executor = cfg.eveowners.GetIfExists(row.executorCorpID)
        if executor is not None:
            executorCorpName = executor.ownerName
        else:
            executorCorpName = ''
        if standing is None:
            standing = mls.UI_GENERIC_NOTSET
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (row.allianceName,
         executorCorpName,
         row.shortName,
         util.FmtDate(row.startDate, 'ls'),
         row.memberCount,
         standing)
        return label



    def __AddToList(self, ranking, standing, scrolllist):
        data = util.KeyVal()
        data.label = self._FormAlliancesRankings__GetLabel(ranking, standing)
        data.ranking = ranking
        data.GetMenu = self.GetRankingMenu
        scrolllist.append(listentry.Get('Generic', data=data))



    def GetRankingMenu(self, entry):
        allianceID = entry.sr.node.ranking.allianceID
        res = sm.GetService('menu').GetMenuFormItemIDTypeID(allianceID, const.typeAlliance)
        if eve.session.allianceid is None:
            res.append([mls.UI_CMD_APPLYTOJOIN, [[mls.UI_CMD_APPLYTOJOIN, self.ApplyToJoin, [allianceID]]]])
        elif allianceID != eve.session.allianceid:
            res.append([mls.UI_CMD_DECLAREWAR, [[mls.UI_CMD_DECLAREWAR, self.DeclareWarAgainst, [allianceID]]]])
        return res



    def ApplyToJoin(self, allianceID):
        sm.GetService('corpui').ApplyToJoinAlliance(allianceID)



    def DeclareWarAgainst(self, allianceID):
        cost = sm.GetService('war').GetCostOfWarAgainst(allianceID)
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        cost = sm.GetService('war').GetCostOfWarAgainst(allianceID)
        if eve.Message('WarDeclareConfirm', {'corporalliance': mls.UI_GENERIC_ALLIANCE,
         'against': cfg.eveowners.Get(allianceID).ownerName,
         'price': util.FmtISK(cost, showFractionsAlways=0)}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('alliance').DeclareWarAgainst(allianceID)




