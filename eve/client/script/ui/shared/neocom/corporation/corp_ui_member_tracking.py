import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import draw
import uiconst
import uicls

class CorpMemberTracking(uicls.Container):
    __guid__ = 'form.CorpMemberTracking'
    __nonpersistvars__ = []

    def Load(self, args):
        toparea = sm.GetService('corpui').LoadTop('ui_7_64_11', mls.UI_CORP_MEMBERLIST, mls.UI_CORP_DELAYED5MINUTES)
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=18, top=10)
            viewOptionsList2 = [(mls.UI_CONTRACTS_ALL, None)]
            self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
            for grp in self.sr.roleGroupings.itervalues():
                if grp.roleGroupID in (1, 2):
                    for c in grp.columns:
                        role = c[1][0][1]
                        viewOptionsList2.append([role.shortDescription, role.roleID])


            i = 0
            self.sr.fltRole = uicls.Combo(label=mls.UI_GENERIC_ROLE, parent=toppar, options=viewOptionsList2, name='rolegroup', callback=self.OnFilterChange, width=146, pos=(5, 0, 0, 0))
            i += 1
            self.sr.fltOnline = c = uicls.Checkbox(text=mls.UI_GENERIC_ONLINEONLY, parent=toppar, configName='online', retval=1, checked=0, align=uiconst.TOPLEFT, callback=self.OnFilterChange, pos=(self.sr.fltRole.width + 16,
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
            return mls.UI_CORP_MORETHANAMONTH
        else:
            if numHours < 0:
                return mls.UI_GENERIC_ONLINE
            if numHours < 1:
                return mls.UI_CONTRACTS_LESSTHANANHOUR
            if numHours < 24:
                return '%s %s' % (numHours, mls.UI_GENERIC_HOUR if numHours == 1 else mls.UI_GENERIC_HOURS)
            if numHours < 168:
                return mls.UI_CORP_LASTWEEK
            if numHours < 720:
                return mls.UI_CORP_LASTMONTH
            return mls.UI_CORP_MORETHANAMONTH



    def ShowMemberTracking(self):
        fltRole = self.sr.fltRole.GetValue()
        fltOnline = self.sr.fltOnline.GetValue()
        scrolllist = []
        header = [mls.NAME,
         mls.UI_GENERIC_LASTONLINE,
         mls.UI_CORP_TITLE,
         mls.UI_GENERIC_BASE,
         mls.UI_CORP_JOINED]
        if eve.session.corprole & const.corpRoleDirector > 0:
            header.extend([mls.UI_GENERIC_SHIP,
             mls.LOCATION,
             mls.UI_GENERIC_ONLINE,
             mls.UI_GENERIC_OFFLINE])
        sm.GetService('loading').Cycle('Loading')
        try:
            if eve.session.corprole & const.corpRoleDirector != const.corpRoleDirector and 0:
                header = []
                scrolllist.append(listentry.Get('Text', {'text': mls.UI_CORP_ACCESSDENIED8,
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
                    label = name
                    label += '<t>%s' % self.GetLastLoggedOnText(member.lastOnline)
                    label += '<t>%s' % member.title
                    label += '<t>%s' % base
                    label += '<t>%s' % util.FmtDate(member.startDateTime, 'ln')
                    if eve.session.corprole & const.corpRoleDirector > 0:
                        label += '<t>%s' % cfg.invtypes.Get(member.shipTypeID).typeName
                        label += '<t>%s' % cfg.evelocations.Get(member.locationID).locationName
                        label += '<t>%s' % util.FmtDate(member.logonDateTime, 'ls')
                        label += '<t>%s' % util.FmtDate(member.logoffDateTime, 'ls')
                    data = util.KeyVal()
                    data.charID = member.characterID
                    data.corporationID = member.corporationID
                    data.logonDateTime = member.logonDateTime
                    data.logoffDateTime = member.logoffDateTime
                    data.label = label
                    data.showinfo = True
                    data.typeID = const.typeCharacterAmarr
                    data.itemID = member.characterID
                    data.slimuser = True
                    data.Set('sort_%s' % mls.UI_GENERIC_LASTONLINE, member.lastOnline)
                    scrolllist.append(listentry.Get('MemberTracking', data=data))

            if 0 == len(scrolllist):
                header = []
                scrolllist.append(listentry.Get('Text', {'text': mls.UI_GENERIC_NODATAAVAIL,
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
        self.sr.label.singleline = 1
        self.sr.namelabel.left = const.defaultPadding
        self.sr.picture.state = uiconst.UI_HIDDEN



    def Load(self, *args):
        listentry.User.Load(self, *args)
        self.sr.label.left = self.sr.namelabel.left = const.defaultPadding



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 6
        return node.height



    def GetMenu(self):
        m = listentry.User.GetMenu(self)
        return m




