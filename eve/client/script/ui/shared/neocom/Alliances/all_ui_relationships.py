import blue
import uthread
import util
import xtriui
import uix
import uiutil
import form
import string
import listentry
import time
import types
import uicls
import uiconst
import log

class FormAlliancesRelationships(uicls.Container):
    __guid__ = 'form.AlliancesRelationships'
    __nonpersistvars__ = []

    def init(self):
        self.sr.viewType = None



    def CreateWindow(self):
        self.sr.headers = [mls.UI_GENERIC_TOPERSON, mls.UI_GENERIC_TYPE]
        if eve.session.allianceid is not None:
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOTOP, parent=self, left=const.defaultPadding, top=const.defaultPadding)
            if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                btns = [[mls.UI_CORP_SETRELATIONSHIP,
                  self.SetRelationshipForm,
                  None,
                  None]]
                t = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer, line=0)
            else:
                t = uicls.Label(text=mls.UI_CORP_HINT18, parent=self.toolbarContainer, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
            self.toolbarContainer.height = t.height
        self.sr.scroll = uicls.Scroll(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        if eve.session.allianceid is None:
            self.sr.scroll.Load(contentList=[], noContentHint=mls.UI_CORP_OWNERNOTINANYALLIANCE % {'owner': cfg.eveowners.Get(eve.session.corpid).ownerName})
            return 
        self.ShowRelationships()



    def SetType(self, viewType):
        self.sr.viewType = viewType



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowRelationships(self):
        log.LogInfo('ShowRelationships')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            hint = mls.UI_CORP_NORELATIONSHIPSFOUND
            if self is None or self.destroyed:
                log.LogInfo('ShowMyApplications Destroyed or None')
            else:
                relationships = sm.GetService('alliance').GetRelationships()
                log.LogInfo('ShowRelationships len(relationships):', len(relationships))
                owners = []
                for relationship in relationships.itervalues():
                    if relationship.toID not in owners:
                        owners.append(relationship.toID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for relationship in relationships.itervalues():
                    self._FormAlliancesRelationships__AddToList(relationship, scrolllist)

                _scrolllist = []
                for s in scrolllist:
                    for i in range(len(_scrolllist)):
                        _s = _scrolllist[i]
                        if _s.label > s.label:
                            _scrolllist.insert(i, s)
                            break
                    else:
                        _scrolllist.append(s)


                scrolllist = _scrolllist
            self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers, noContentHint=hint)

        finally:
            sm.GetService('corpui').HideLoad()




    def __GetRelationshipStr(self, relationship):
        string = ''
        if relationship == const.allianceRelationshipNAP:
            string = mls.UI_CORP_NONAGGRESSIONPACT
        elif relationship == const.allianceRelationshipFriend:
            string = mls.UI_CORP_FRIEND
        elif relationship == const.allianceRelationshipCompetitor:
            string = mls.UI_CORP_COMPETITOR
        elif relationship == const.allianceRelationshipEnemy:
            string = mls.UI_CORP_ENEMY
        return string



    def __AddToList(self, relationship, scrolllist):
        if relationship.relationship != self.sr.viewType:
            return 
        data = util.KeyVal()
        typeStr = self._FormAlliancesRelationships__GetRelationshipStr(relationship.relationship)
        data.label = '%s<t>%s' % (cfg.eveowners.Get(relationship.toID).ownerName, typeStr)
        data.OnDblClick = self.SelectRelationshipType
        data.GetMenu = self.GetRelationshipMenu
        data.relationship = relationship
        scrolllist.append(listentry.Get('Generic', data=data))



    def GetEntry(self, toID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.relationship.toID == toID:
                return entry




    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        log.LogInfo('OnAllianceRelationshipChanged allianceID', allianceID, 'toID', toID, 'change', change)
        if self is None or self.destroyed:
            log.LogInfo('OnAllianceRelationshipChanged self is None or self.destroyed')
            return 
        if not self.sr.Get('scroll') or self.sr.scroll is None:
            log.LogInfo('OnAllianceRelationshipChanged no scroll')
            return 
        bAdd = 1
        bRemove = 1
        for (old, new,) in change.itervalues():
            if old is None and new is None:
                continue
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('applications::OnAllianceRelationshipChanged WTF')
        if 'relationship' in change:
            (old, new,) = change['relationship']
            if new == self.sr.viewType:
                bAdd = True
                bRemove = False
            elif old == self.sr.viewType:
                bAdd = False
                bRemove = True
        if bAdd:
            log.LogInfo('OnAllianceRelationshipChanged adding relationship')
            relationship = sm.GetService('alliance').GetRelationships()[toID]
            if relationship.relationship != self.sr.viewType:
                return 
            self.SetHint()
            scrolllist = []
            self._FormAlliancesRelationships__AddToList(relationship, scrolllist)
            if len(self.sr.scroll.sr.headers) > 0:
                self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
        elif bRemove:
            log.LogInfo('OnAllianceRelationshipChanged removing application')
            entry = self.GetEntry(toID)
            if entry is not None:
                self.sr.scroll.RemoveEntries([entry])
        else:
            log.LogInfo('OnAllianceRelationshipChanged updating application')
            entry = self.GetEntry(toID)
            relationship = sm.GetService('alliance').GetRelationships()[toID]
            if entry is None and relationship.relationship == self.sr.viewType:
                self.SetHint()
                scrolllist = []
                self._FormAlliancesRelationships__AddToList(relationship, scrolllist)
                if len(self.sr.scroll.sr.headers) > 0:
                    self.sr.scroll.AddEntries(-1, scrolllist)
                else:
                    self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
            if entry is not None and relationship.relationship != self.sr.viewType:
                self.sr.scroll.RemoveEntries([entry])



    def SetRelationshipForm(self, *args):
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'edit',
         'setvalue': '',
         'key': 'corpName',
         'readonly': 1,
         'label': mls.UI_CORP_DECLARE,
         'required': 1,
         'frame': 1,
         'maxlength': 100})
        format.append({'type': 'btnonly',
         'frame': 1,
         'height': 27,
         'buttons': [{'caption': mls.UI_CMD_PICK,
                      'align': 'right',
                      'btn_default': 1,
                      'function': self.PickCorporationOrAlliance}]})
        format.append({'type': 'data',
         'data': {'corpID': None}})
        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        format.append({'type': 'bbline'})
        relationshipTypes = [[const.allianceRelationshipNAP, mls.UI_CORP_NONAGGRESSIONPACT],
         [const.allianceRelationshipFriend, mls.UI_CORP_FRIEND],
         [const.allianceRelationshipCompetitor, mls.UI_CORP_COMPETITOR],
         [const.allianceRelationshipEnemy, mls.UI_CORP_ENEMY]]
        for (value, relationshipName,) in relationshipTypes:
            format.append({'type': 'checkbox',
             'setvalue': value == self.sr.viewType,
             'key': value,
             'label': '',
             'text': relationshipName,
             'frame': 1,
             'group': 'relationship'})

        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, mls.UI_CORP_SETRELATIONSHIP, 1, None, uiconst.OKCANCEL, [left, top], 300, 175)
        if retval is None:
            return 
        toID = retval['corpID']
        relationship = retval['relationship']
        sm.GetService('alliance').SetRelationship(relationship, toID)



    def PickCorporationOrAlliance(noargs, window, *args):
        while window.name != 'form':
            window = window.parent

        dlg = sm.GetService('window').GetWindow('CorporationOrAlliancePickerDailog', create=1, ignoreCurrent=1, warableEntitysOnly=False)
        dlg.ShowModal()
        if dlg.ownerID:
            window.sr.corpName.SetValue(cfg.eveowners.Get(dlg.ownerID).ownerName)
            wnd = uix.GetWindowAbove(window)
            for each in wnd.retfields:
                if type(each) == types.DictType and each.has_key('corpID'):
                    each['corpID'] = dlg.ownerID
                    break




    def SelectRelationshipType(self, entry):
        toID = entry.sr.node.relationship.toID
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        format = []
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        relationshipTypes = [[const.allianceRelationshipFriend, mls.UI_CORP_FRIEND],
         [const.allianceRelationshipNAP, mls.UI_CORP_NONAGGRESSIONPACT],
         [const.allianceRelationshipCompetitor, mls.UI_CORP_COMPETITOR],
         [const.allianceRelationshipEnemy, mls.UI_CORP_ENEMY]]
        for (value, relationshipName,) in relationshipTypes:
            format.append({'type': 'checkbox',
             'setvalue': value == self.sr.viewType,
             'key': value,
             'label': '',
             'text': relationshipName,
             'frame': 1,
             'group': 'relationship'})

        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, mls.UI_CORP_CHANGERELATIONSHIPTYPE, 1, None, uiconst.OKCANCEL, [left, top])
        if retval is None:
            return 
        relationship = retval['relationship']
        sm.GetService('alliance').SetRelationship(relationship, toID)



    def DeleteRelationship(self, toID):
        sm.GetService('alliance').DeleteRelationship(toID)



    def ShowInfo(self, orgOrCharID):
        entity = cfg.eveowners.Get(orgOrCharID)
        sm.StartService('info').ShowInfo(int(entity.Type()), orgOrCharID)



    def GetRelationshipMenu(self, entry):
        toID = entry.sr.node.relationship.toID
        return [[mls.UI_CMD_SHOWINFO, self.ShowInfo, [toID]],
         None,
         [mls.UI_CMD_CHANGE, self.SelectRelationshipType, [entry]],
         [mls.UI_CMD_DELETE, [[mls.UI_CMD_DELETE, self.DeleteRelationship, [toID]]]]]




