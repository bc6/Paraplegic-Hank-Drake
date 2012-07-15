#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/corp_ui_member_tracking.py
import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import uiconst
import uicls
import localization

class CorpMemberTracking(uicls.Container):
    __guid__ = 'form.CorpMemberTracking'
    __nonpersistvars__ = []

    def Load(self, args):
        toparea = sm.GetService('corpui').LoadTop('ui_7_64_11', localization.GetByLabel('UI/Corporations/BaseCorporationUI/MemberList'), localization.GetByLabel('UI/Corporations/Common/UpdateDelay'))
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=18, top=10)
            viewOptionsList2 = [(localization.GetByLabel('UI/Common/All'), None)]
            self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
            for grp in self.sr.roleGroupings.itervalues():
                if grp.roleGroupID in (1, 2):
                    for c in grp.columns:
                        role = c[1][0][1]
                        viewOptionsList2.append([role.shortDescription, role.roleID])

            i = 0
            self.sr.fltRole = uicls.Combo(label=localization.GetByLabel('UI/Corporations/Common/Role'), parent=toppar, options=viewOptionsList2, name='rolegroup', callback=self.OnFilterChange, width=146, pos=(5, 0, 0, 0))
            i += 1
            self.sr.fltOnline = c = uicls.Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/OnlineOnly'), parent=toppar, configName='online', retval=1, checked=0, align=uiconst.TOPLEFT, callback=self.OnFilterChange, pos=(self.sr.fltRole.width + 16,
             0,
             250,
             0))
            memberIDs = sm.GetService('corp').GetMemberIDs()
            cfg.eveowners.Prime(memberIDs)
            self.sr.scroll = uicls.Scroll(name='member_tracking', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.ShowMemberTracking()

    def OnFilterChange(self, *args):
        self.ShowMemberTracking()

    def OnReturn(self, *args):
        uthread.new(self.ShowMemberTracking)

    def GetLastLoggedOnText(self, numHours):
        if numHours == None:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/MoreThanAMonth')
        elif numHours < 0:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/Online')
        elif numHours < 1:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LessThanAnHour')
        elif numHours < 24:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/Hours', hourCount=int(numHours), hours=numHours)
        elif numHours < 168:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LastWeek')
        elif numHours < 720:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LastMonth')
        else:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/MoreThanAMonth')

    def ShowMemberTracking(self):
        fltRole = self.sr.fltRole.GetValue()
        fltOnline = self.sr.fltOnline.GetValue()
        scrolllist = []
        header = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/LastOnlineColumnHeader'),
         localization.GetByLabel('UI/Corporations/Common/Title'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/JoinedColumnHeader')]
        if eve.session.corprole & const.corpRoleDirector > 0:
            header.extend([localization.GetByLabel('UI/Common/Ship'),
             localization.GetByLabel('UI/Common/Location'),
             localization.GetByLabel('UI/Common/Online'),
             localization.GetByLabel('UI/Common/Offline')])
        sm.GetService('loading').Cycle('Loading')
        try:
            if eve.session.corprole & const.corpRoleDirector != const.corpRoleDirector and 0:
                header = []
                scrolllist.append(listentry.Get('Text', {'text': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/AccessDeniedDirectorRoleRequired'),
                 'line': 1}))
            else:
                memberTracking = sm.GetService('corp').GetMemberTrackingInfo()
                for member in memberTracking:
                    if fltRole and not (member.roles & fltRole > 0 or member.grantableRoles & fltRole > 0 or member.roles & const.corpRoleDirector > 0):
                        continue
                    if fltOnline > 0:
                        if member.lastOnline == None or member.lastOnline >= 0:
                            continue
                    base = ''
                    if member.baseID:
                        base = cfg.evelocations.Get(member.baseID).locationName
                    name = cfg.eveowners.Get(member.characterID).ownerName
                    label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                     self.GetLastLoggedOnText(member.lastOnline),
                     member.title,
                     base,
                     util.FmtDate(member.startDateTime, 'ln'))
                    if eve.session.corprole & const.corpRoleDirector > 0:
                        shipTypeName = localization.GetByLabel('UI/Generic/None')
                        if member.shipTypeID is not None:
                            shipTypeName = cfg.invtypes.Get(member.shipTypeID).typeName
                        locationName = localization.GetByLabel('UI/Generic/Unknown')
                        if member.locationID is not None:
                            locationName = cfg.evelocations.Get(member.locationID).locationName
                        label += '<t>%s<t>%s<t>%s<t>%s' % (shipTypeName,
                         locationName,
                         util.FmtDate(member.logonDateTime, 'ls') if member.logonDateTime is not None else localization.GetByLabel('UI/Generic/Unknown'),
                         util.FmtDate(member.logoffDateTime, 'ls') if member.logoffDateTime is not None else localization.GetByLabel('UI/Generic/Unknown'))
                    data = util.KeyVal()
                    data.charID = member.characterID
                    data.corporationID = member.corporationID
                    if eve.session.corprole & const.corpRoleDirector > 0:
                        data.logonDateTime = member.logonDateTime
                        data.logoffDateTime = member.logoffDateTime
                    data.label = label
                    data.showinfo = True
                    data.typeID = const.typeCharacterAmarr
                    data.itemID = member.characterID
                    data.slimuser = True
                    data.Set('sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/LastOnlineColumnHeader'), member.lastOnline)
                    scrolllist.append(listentry.Get('MemberTracking', data=data))

            if 0 == len(scrolllist):
                header = []
                scrolllist.append(listentry.Get('Text', {'text': localization.GetByLabel('UI/Common/NoDataAvailable'),
                 'line': 1}))
        finally:
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'member_tracking'
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, headers=header)
            sm.GetService('loading').StopCycle()

    def OnMemberMenu(self, entry):
        selected = self.sr.scroll.GetSelected()
        sel = []
        if selected:
            sel = [ (each.charID, each.corporationID) for each in selected if hasattr(each, 'charID') ]
        return sm.StartService('menu').CharacterMenu(sel)


class MemberTracking(listentry.User):
    __guid__ = 'listentry.MemberTracking'

    def Startup(self, *args):
        listentry.User.Startup(self, *args)
        self.sr.label = self.sr.namelabel
        self.sr.label.maxLines = 1
        self.sr.namelabel.left = const.defaultPadding
        self.sr.picture.state = uiconst.UI_HIDDEN
        self.sr.statusIcon.SetAlign(uiconst.CENTERRIGHT)
        self.sr.statusIcon.top = 0

    def Load(self, *args):
        listentry.User.Load(self, *args)
        self.sr.label.left = self.sr.namelabel.left = const.defaultPadding

    def GetHeight(self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 6
        return node.height

    def GetMenu(self):
        m = listentry.User.GetMenu(self)
        return m