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
                btns.append([mls.UI_CORP_CREATEALLIANCE,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            btns.append([mls.UI_CMD_EDITALLIANCE,
             self.EditAllianceForm,
             None,
             None])
            btns.append([mls.UI_CMD_DECLAREWAR,
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
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=mls.UI_CORP_OWNERNOTINANYALLIANCE % {'owner': cfg.eveowners.Get(eve.session.corpid).ownerName})
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
             'label': mls.UI_GENERIC_DETAILS,
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
             'label': mls.UI_INFOWND_SETTLEDSYSTEMS,
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
            subcontent.append(listentry.Get('Generic', {'label': mls.UI_SHARED_ALLIANCEHASNOSYSTEM}))
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
                    eHint = mls.UI_CORP_HINT7
            if not eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                eHint = mls.UI_CORP_HINT8
            sm.GetService('corpui').LoadTop('ui_7_64_6', mls.UI_GENERIC_ALLIANCES, eHint)
            scrolllist = []
            hint = mls.UI_CORP_NODETAILSFOUND
            if self is None or self.destroyed:
                log.LogInfo('ShowMembers Destroyed or None')
                hint = '\xfe\xfa s\xe1st mig ekki.'
            elif eve.session.allianceid is None:
                hint = mls.UI_CORP_OWNERNOTINANYALLIANCEATM % {'owner': cfg.eveowners.Get(eve.session.corpid).ownerName}
            else:
                rec = sm.GetService('alliance').GetAlliance()
                owners = [rec.allianceID, rec.creatorCorpID, rec.creatorCharID]
                if rec.executorCorpID is not None:
                    owners.append(rec.executorCorpID)
                if len(owners):
                    cfg.eveowners.Prime(owners)
                label = mls.UI_CORP_ALLIANCENAME
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
                        label = mls.UI_CORP_EXECUTOR
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
                        label = mls.UI_CORP_SHORTNAME
                        text = value
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    elif columnName == 'url' and value:
                        label = mls.UI_GENERIC_URL
                        text = value
                        if text:
                            text = util.FormatUrl(text)
                        params = {'line': 1,
                         'label': label,
                         'text': '<url=%s>%s</url>' % (text, text)}
                    elif columnName == 'description' and value:
                        label = mls.UI_GENERIC_DESCRIPTION
                        text = value
                        params = {'line': 1,
                         'label': label,
                         'text': text}
                    elif columnName == 'creatorCorpID':
                        label = mls.UI_CORP_CREATEDBYCORP
                        text = cfg.eveowners.Get(value).ownerName
                        params = {'line': 1,
                         'label': label,
                         'text': text,
                         'typeID': const.typeCorporation,
                         'itemID': value}
                    elif columnName == 'creatorCharID':
                        label = mls.UI_CORP_CREATEDBY
                        text = cfg.eveowners.Get(value).ownerName
                        params = {'line': 1,
                         'label': label,
                         'text': text,
                         'typeID': const.typeCharacterAmarr,
                         'itemID': value}
                    elif columnName == 'dictatorial':
                        label = mls.UI_CORP_DICTATORIAL
                        text = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][value]
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
         'setvalue': mls.UI_CORP_NAMEALLIANCE % {'name': cfg.eveowners.Get(eve.session.corpid).ownerName},
         'key': 'allianceName',
         'label': mls.UI_GENERIC_NAME,
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
         'label': mls.UI_CORP_SHORTNAME,
         'required': 1,
         'frame': 1,
         'maxlength': 5})
        format.append({'type': 'btnonly',
         'frame': 1,
         'buttons': [{'caption': mls.UI_CMD_SUGGEST,
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
         'label': mls.UI_GENERIC_URL,
         'frame': 1,
         'maxLength': 2048})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'description',
         'label': mls.UI_GENERIC_DESCRIPTION,
         'frame': 1,
         'maxLength': 5000})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, mls.UI_CORP_CREATEALLIANCE, 1, None, uiconst.OKCANCEL, [left, top], 500, unresizeAble=1, ignoreCurrent=0)
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
         'text': mls.UI_CORP_SELECTSHORTNAME,
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
        retval = uix.HybridWnd(format, mls.UI_CORP_SUGGESTSHORTNAME, 1, None, uiconst.OKCANCEL, [left, top], 300, unresizeAble=1)
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
             'label': mls.UI_GENERIC_URL,
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
             'label': mls.UI_GENERIC_DESCRIPTION,
             'frame': 1,
             'maxLength': 5000,
             'height': 130})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
            retval = uix.HybridWnd(format, mls.UI_CORP_UPDATEALLIANCE, 1, None, uiconst.OKCANCEL, [left, top], 500, 150, unresizeAble=1)
            if retval is None:
                return 
            url = retval['url']
            description = retval['description']
            sm.GetService('alliance').UpdateAlliance(description, url)

        finally:
            self.openingEditForm = False




    def DeclareWarForm(self, *args):
        dlg = sm.GetService('window').GetWindow('CorporationOrAlliancePickerDailog', create=1, ignoreCurrent=1, warableEntitysOnly=True)
        dlg.ShowModal()
        againstID = dlg.ownerID
        if not againstID:
            return 
        cost = sm.GetService('war').GetCostOfWarAgainst(againstID)
        if eve.Message('WarDeclareConfirm', {'corporalliance': mls.UI_GENERIC_ALLIANCE,
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
                btns.append([mls.UI_CORP_CREATEALLIANCE,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            btns.append([mls.UI_CORP_ADDBULLETIN,
             self.AddBulletin,
             None,
             None])
        if len(btns):
            buttons = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer)
        self.toolbarContainer.height = 20 if not len(btns) else buttons.height
        import draw
        bulletinParent = uicls.Container(name='bulletinParent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=bulletinParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        self.messageArea = uicls.Edit(parent=bulletinParent, readonly=1, hideBackground=1)
        self.messageArea.AllowResizeUpdates(1)
        if session.allianceid is not None:
            self.LoadBulletins()



    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=True)



    def LoadBulletins(self):
        txt = sm.GetService('corp').GetFormattedBulletins(isAlliance=True)
        self.messageArea.LoadHTML(txt)




