import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import uiutil
import log
import uicls
import uiconst
import localization
ALLIANCETEXT = 'Alliance'

class FormAlliancesHome(uicls.Container):
    __guid__ = 'form.AlliancesHome'
    __nonpersistvars__ = []

    def init(self):
        pass



    def CreateWindow(self):
        btns = []
        self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        if eve.session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
            if corporation.ceoID == eve.session.charid:
                createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
                btns.append([createAllianceLabel,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            editAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/EditAlliance')
            declareWarLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DeclareWar')
            btns.append([editAllianceLabel,
             self.EditAllianceForm,
             None,
             None])
            btns.append([declareWarLabel,
             self.DeclareWarForm,
             None,
             None])
        if len(btns):
            buttons = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer)
        self.toolbarContainer.height = 20 if not len(btns) else buttons.height
        self.sr.scroll = uicls.Scroll(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        if eve.session.allianceid is None:
            corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
            return 
        self.LoadScroll()



    def LoadScroll(self):
        if self is None or self.destroyed:
            return 
        if not self.sr.Get('scroll'):
            return 
        try:
            try:
                scrolllist = []
                sm.GetService('corpui').ShowLoad()
                self.ShowMyAllianceDetails(scrolllist)
                self.ShowMyAllianceSystems(scrolllist)
                self.sr.scroll.Load(contentList=scrolllist)
            except:
                log.LogException()
                sys.exc_clear()

        finally:
            sm.GetService('corpui').HideLoad()




    def ShowMyAllianceDetails(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.ShowDetails,
             'label': localization.GetByLabel('UI/Common/Details'),
             'groupItems': None,
             'id': ('alliance', 'details'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('alliance', 'details'), 1)

        finally:
            sm.GetService('corpui').HideLoad()




    def ShowMyAllianceSystems(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.GetSubContentMyAllianceSystems,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SettledSystems'),
             'groupItems': None,
             'id': ('alliance', 'systems'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('alliance', 'systems'), 0)

        finally:
            sm.GetService('corpui').HideLoad()




    def GetSubContentMyAllianceSystems(self, nodedata, *args):
        subcontent = []
        systems = sm.RemoteSvc('stationSvc').GetSystemsForAlliance(session.allianceid)
        if systems:
            map = sm.GetService('map')
            toPrime = set()
            systemInfoList = []
            for row in systems:
                hierarchy = map.GetItem(row.solarSystemID, True).hierarchy
                toPrime.update(set(hierarchy))
                systemInfoList.append(hierarchy)

            cfg.evelocations.Prime(list(toPrime))
            for (regionID, constellationID, solarSystemID,) in systemInfoList:
                solarSystemName = cfg.evelocations.Get(solarSystemID).name
                regionName = cfg.evelocations.Get(regionID).name
                constellationName = cfg.evelocations.Get(constellationID).name
                label = '%s / %s / %s' % (regionName, constellationName, solarSystemName)
                subcontent.append(listentry.Get('Generic', {'label': label,
                 'solarSystemID': solarSystemID,
                 'GetMenu': self.GetAllianceSystemMenu}))

        if len(subcontent) == 0:
            noSettledSystemsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NoSettledSystems')
            subcontent.append(listentry.Get('Generic', {'label': noSettledSystemsLabel}))
        else:
            subcontent.sort(key=lambda x: x.label)
        return subcontent



    def GetAllianceSystemMenu(self, entry):
        return sm.GetService('menu').CelestialMenu(entry.sr.node.solarSystemID)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowDetails(self, nodedata, *args):
        log.LogInfo('ShowDetails')
        try:
            sm.GetService('corpui').ShowLoad()
            eHint = ''
            if eve.session.allianceid is None:
                corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
                if corporation.ceoID != eve.session.charid:
                    eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CEODeclareWarOnlyHint')
            if not eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DirectorsCanEdit')
            alliancesLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances')
            sm.GetService('corpui').LoadTop('ui_7_64_6', alliancesLabel, eHint)
            scrolllist = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NoDetailsFound')
            if self is None or self.destroyed:
                log.LogInfo('ShowMembers Destroyed or None')
                hint = '\xfe\xfa s\xe1st mig ekki.'
            elif eve.session.allianceid is None:
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAllianceATM', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            else:
                rec = sm.GetService('alliance').GetAlliance()
                owners = [rec.allianceID, rec.creatorCorpID, rec.creatorCharID]
                if rec.executorCorpID is not None:
                    owners.append(rec.executorCorpID)
                if len(owners):
                    cfg.eveowners.Prime(owners)
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AllianceName')
                text = cfg.eveowners.Get(rec.allianceID).ownerName
                params = {'line': 1,
                 'label': label,
                 'text': text,
                 'typeID': const.typeAlliance,
                 'itemID': rec.allianceID}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                for columnName in rec.header:
                    value = getattr(rec, columnName)
                    if columnName == 'executorCorpID':
                        label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Executor')
                        executor = cfg.eveowners.GetIfExists(value)
                        if executor is not None:
                            text = executor.ownerName
                            params = {'line': 1,
                             'label': label,
                             'text': text,
                             'typeID': const.typeCorporation,
                             'itemID': value}
                        else:
                            text = '-'
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    elif columnName == 'shortName':
                        label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName')
                        text = value
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    elif columnName == 'url' and value:
                        label = localization.GetByLabel('UI/Common/URL')
                        text = value
                        if text:
                            text = util.FormatUrl(text)
                        params = {'line': 1,
                         'label': label,
                         'text': '<url=%s>%s</url>' % (text, text)}
                    elif columnName == 'description' and value:
                        label = localization.GetByLabel('UI/Common/Description')
                        text = value
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    elif columnName == 'creatorCorpID':
                        label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedByCorporation')
                        text = cfg.eveowners.Get(value).ownerName
                        params = {'line': 1,
                         'label': label,
                         'text': text,
                         'typeID': const.typeCorporation,
                         'itemID': value}
                    elif columnName == 'creatorCharID':
                        label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedBy')
                        text = cfg.eveowners.Get(value).ownerName
                        params = {'line': 1,
                         'label': label,
                         'text': text,
                         'typeID': const.typeCharacterAmarr,
                         'itemID': value}
                    elif columnName == 'dictatorial':
                        label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Dictatorial')
                        yesLabel = localization.GetByLabel('UI/Common/Buttons/Yes')
                        noLabel = localization.GetByLabel('UI/Common/Buttons/No')
                        text = [noLabel, yesLabel][value]
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    else:
                        continue
                    scrolllist.append(listentry.Get('LabelTextTop', params))

            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'alliances_members'
            if not scrolllist:
                self.SetHint(hint)
            return scrolllist

        finally:
            sm.GetService('corpui').HideLoad()




    def OnAllianceChanged(self, allianceID, change):
        log.LogInfo('OnAllianceChanged allianceID', allianceID, 'change', change)
        if eve.session.allianceid != allianceID:
            return 
        if self.state != uiconst.UI_NORMAL:
            log.LogInfo('OnAllianceChanged state != UI_NORMAL')
            return 
        if self.sr.scroll is None:
            log.LogInfo('OnAllianceChanged no scroll')
            return 
        self.ShowDetails()



    def CreateAllianceForm(self, *args):
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'setvalue': '%s %s ' % (cfg.eveowners.Get(eve.session.corpid).ownerName, ALLIANCETEXT),
         'key': 'allianceName',
         'label': localization.GetByLabel('UI/Common/Name'),
         'required': 1,
         'frame': 1,
         'maxlength': 100})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'setvalue': '',
         'key': 'shortName',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName'),
         'required': 1,
         'frame': 1,
         'maxlength': 5})
        format.append({'type': 'btnonly',
         'frame': 1,
         'buttons': [{'caption': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SuggestCommand'),
                      'align': 'right',
                      'btn_default': 1,
                      'function': self.GetSuggestedTickerNames}]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'url',
         'label': localization.GetByLabel('UI/Common/URL'),
         'frame': 1,
         'maxLength': 2048})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'description',
         'label': localization.GetByLabel('UI/Common/Description'),
         'frame': 1,
         'maxLength': 5000})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
        retval = uix.HybridWnd(format, createAllianceLabel, 1, None, uiconst.OKCANCEL, [left, top], 500, unresizeAble=1, ignoreCurrent=0)
        if retval is None:
            return 
        allianceName = retval['allianceName']
        shortName = retval['shortName']
        url = retval['url']
        description = retval['description']
        uthread.new(sm.GetService('sessionMgr').PerformSessionChange, 'alliance.addalliance', sm.GetService('corp').CreateAlliance, allianceName, shortName, description, url)



    def GetSuggestedTickerNames(noarg, window):
        while window.name != 'form':
            window = window.parent

        allianceNameEdit = window.sr.allianceName
        shortNameEdit = window.sr.shortName
        if len(allianceNameEdit.GetValue()) == 0:
            return 
        shortNames = sm.GetService('corp').GetSuggestedAllianceShortNames(allianceNameEdit.GetValue())
        format = []
        stati = {}
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SelectShortName'),
         'frame': 1})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        selected = 1
        for shortNameRow in shortNames:
            shortName = shortNameRow.shortName
            if shortName is None:
                continue
            format.append({'type': 'checkbox',
             'setvalue': selected,
             'key': shortName,
             'label': '',
             'text': shortName,
             'frame': 1,
             'group': 'shortNames'})
            selected = 0

        format.append({'type': 'btline'})
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        suggestedShortNameLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SuggestedShortName')
        retval = uix.HybridWnd(format, suggestedShortNameLabel, 1, None, uiconst.OKCANCEL, [left, top], 300, unresizeAble=1)
        if retval is not None:
            window.sr.shortName.SetValue(retval['shortNames'])



    def EditAllianceForm(self, *args):
        if getattr(self, 'openingEditForm', False):
            return 
        self.openingEditForm = True
        try:
            left = uicore.desktop.width / 2 - 500 / 2
            top = uicore.desktop.height / 2 - 400 / 2
            alliance = sm.GetService('alliance').GetAlliance()
            format = []
            format.append({'type': 'btline'})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'edit',
             'key': 'url',
             'setvalue': alliance.url,
             'label': localization.GetByLabel('UI/Common/URL'),
             'frame': 1,
             'maxLength': 2048})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'btline'})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'textedit',
             'key': 'description',
             'setvalue': alliance.description,
             'label': localization.GetByLabel('UI/Common/Description'),
             'frame': 1,
             'maxLength': 5000,
             'height': 130})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
            updateAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/UpdateAlliance')
            retval = uix.HybridWnd(format, updateAllianceLabel, 1, None, uiconst.OKCANCEL, [left, top], 500, 150, unresizeAble=1)
            if retval is None:
                return 
            url = retval['url']
            description = retval['description']
            sm.GetService('alliance').UpdateAlliance(description, url)

        finally:
            self.openingEditForm = False




    def DeclareWarForm(self, *args):
        dlg = form.CorporationOrAlliancePickerDailog.Open(warableEntitysOnly=True)
        dlg.ShowModal()
        againstID = dlg.ownerID
        if not againstID:
            return 
        cost = sm.GetService('war').GetCostOfWarAgainst(againstID)
        allianceLabel = localization.GetByLabel('UI/Common/Alliance')
        if eve.Message('WarDeclareConfirm', {'corporalliance': allianceLabel,
         'against': cfg.eveowners.Get(againstID).ownerName,
         'price': util.FmtISK(cost, showFractionsAlways=0)}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('alliance').DeclareWarAgainst(againstID)




class FormAlliancesBulletins(uicls.Container):
    __guid__ = 'form.AlliancesBulletins'
    __nonpersistvars__ = []

    def CreateWindow(self):
        btns = []
        self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        if eve.session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
            if corporation.ceoID == eve.session.charid:
                createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
                btns.append([createAllianceLabel,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            addBulletinLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AddBulletin')
            btns.append([addBulletinLabel,
             self.AddBulletin,
             None,
             None])
        if len(btns):
            buttons = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer)
        self.toolbarContainer.height = 20 if not len(btns) else buttons.height
        bulletinParent = uicls.Container(name='bulletinParent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=bulletinParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        self.messageArea = uicls.Scroll(parent=bulletinParent)
        self.messageArea.HideBackground()
        self.messageArea.RemoveActiveFrame()
        if session.allianceid is not None:
            self.LoadBulletins()



    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=True)



    def LoadBulletins(self):
        scrollEntries = sm.GetService('corp').GetBulletinEntries(isAlliance=True)
        self.messageArea.LoadContent(contentList=scrollEntries, noContentHint=localization.GetByLabel('UI/Corporations/BaseCorporationUI/NoBulletins'))




