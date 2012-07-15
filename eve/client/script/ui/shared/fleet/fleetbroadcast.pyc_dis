#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/fleet/fleetbroadcast.py
import blue
import listentry
import uix
import uiutil
import uthread
import util
import xtriui
import fleetbr
import math
import datetime
import dbg
import sys
import chat
import types
import form
import uicls
from fleetcommon import *
import uiconst
import localization

class FleetBroadcastView(uicls.Container):
    __guid__ = 'form.FleetBroadcastView'
    __notifyevents__ = ['OnFleetBroadcast_Local',
     'OnSpeakingEvent_Local',
     'OnFleetLootEvent_Local',
     'OnFleetBroadcastFilterChange',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnFleetMemberChanged_Local']

    def PostStartup(self):
        sm.RegisterNotify(self)
        self.sr.broadcastHistory = []
        self.broadcastMenuItems = []
        header = self
        header.baseHeight = header.height
        self.panelHistory = uicls.Container(name='panelHistory', parent=self, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding, height=const.defaultPadding)
        historyType = settings.user.ui.Get('fleetHistoryFilter', 'all')
        comboPar = uicls.Container(parent=self.panelHistory, align=uiconst.TOTOP, height=36)
        ops = [(localization.GetByLabel('UI/Common/All'), 'all'),
         (localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastHistory'), 'broadcasthistory'),
         (localization.GetByLabel('UI/Fleet/FleetBroadcast/VoiceHistory'), 'voicehistory'),
         (localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistory'), 'memberhistory'),
         (localization.GetByLabel('UI/Fleet/FleetBroadcast/LootHistory'), 'loothistory')]
        self.combo = uicls.Combo(label=localization.GetByLabel('UI/Fleet/FleetBroadcast/Filters'), parent=comboPar, options=ops, name='filter', select=historyType, callback=self.LoadHistory, pos=(0, 12, 0, 0), width=110)
        self.clearBtn = uicls.Button(parent=comboPar, label=localization.GetByLabel('UI/Fleet/FleetBroadcast/ClearHistory'), func=self.OnClear, align=uiconst.BOTTOMRIGHT, top=const.defaultPadding)
        self.scrollHistory = uicls.Scroll(name='allHistoryScroll', parent=self.panelHistory, align=uiconst.TOALL)

    def ClearHistory(self, args):
        fleetSvc = sm.GetService('fleet')
        if args == 'broadcasthistory':
            fleetSvc.broadcastHistory = []
        elif args == 'voicehistory':
            fleetSvc.voiceHistory = []
        elif args == 'loothistory':
            fleetSvc.lootHistory = []
        elif args == 'memberhistory':
            fleetSvc.memberHistory = []
        elif args == 'all':
            fleetSvc.broadcastHistory = []
            fleetSvc.voiceHistory = []
            fleetSvc.lootHistory = []
            fleetSvc.memberHistory = []
        self.LoadHistory(self.combo, '', args)

    def Load(self, args):
        if not self.sr.Get('inited', 0):
            self.PostStartup()
            setattr(self.sr, 'inited', 1)
        self.LoadHistory(self.combo, '', self.combo.selectedValue)

    def LoadHistory(self, combo, label, value, *args):
        scrolllist = []
        headers = []
        hint = ''
        sp = self.scrollHistory.GetScrollProportion()
        self.scrollHistory.multiSelect = 1
        self.scrollHistory.OnChar = self.OnScrollHistoryChar
        if value == 'broadcasthistory':
            scrolllist, hint = self.LoadBroadcastHistory()
            self.scrollHistory.multiSelect = 0
            self.scrollHistory.OnChar = self.OnScrollBroadcastChar
        elif value == 'voicehistory':
            scrolllist, hint = self.LoadVoiceHistory()
        elif value == 'loothistory':
            scrolllist, hint = self.LoadLootHistory()
        elif value == 'memberhistory':
            scrolllist, hint = self.LoadMemberHistory()
        else:
            scrolllist, hint = self.LoadAllHistory()
        settings.user.ui.Set('fleetHistoryFilter', value)
        self.scrollHistory.Load(contentList=scrolllist, scrollTo=sp, headers=[], noContentHint=hint)

    def LoadAllHistory(self):
        allHistory = []
        broadcastHistory, hint = self.LoadBroadcastHistory()
        memberHistory, hint = self.LoadMemberHistory()
        voiceHistory, hint = self.LoadVoiceHistory()
        lootHistory, hint = self.LoadLootHistory()
        allHistory.extend(broadcastHistory)
        allHistory.extend(memberHistory)
        allHistory.extend(voiceHistory)
        allHistory.extend(lootHistory)
        allHistory.sort(key=lambda x: x.time, reverse=True)
        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (allHistory, hint)

    def LoadBroadcastHistory(self):
        scrolllist = []
        broadcastHistory = sm.GetService('fleet').GetBroadcastHistory()
        for kv in broadcastHistory:
            data = self.GetBroadcastListEntry(kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            data.OnClick = self.OnBroadcastClick
            scrolllist.append(listentry.Get('Generic', data=data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def OnBroadcastClick(self, entry):
        data = entry.sr.node.data
        itemID = data.itemID
        if data.itemID == session.shipid or session.shipid is None or data.itemID is None or util.IsUniverseCelestial(data.itemID):
            return
        sm.GetService('menu').TacticalItemClicked(itemID)

    def LoadVoiceHistory(self):
        scrolllist = []
        voiceHistory = sm.GetService('fleet').GetVoiceHistory()
        for data in voiceHistory:
            data2 = self.GetVoiceListEntry(data)
            data2.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), data.time)
            data2.time = data.time
            scrolllist.append(listentry.Get('Generic', data=data2))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def LoadLootHistory(self):
        scrolllist = []
        lootHistory = sm.GetService('fleet').GetLootHistory()
        for kv in lootHistory:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventLoot', time=kv.time, charID=kv.charID, item=kv.typeID, itemQuantity=kv.quantity)
            data = util.KeyVal(charID=kv.charID, label=label, GetMenu=self.GetLootMenu, data=kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            scrolllist.append(listentry.Get('Generic', data=data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def LoadMemberHistory(self):
        scrolllist = []
        memberHistory = sm.GetService('fleet').GetMemberHistory()
        for kv in memberHistory:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/Event', time=kv.time, eventLabel=kv.event)
            data = util.KeyVal(charID=kv.charID, label=label, GetMenu=self.GetMemberMenu, data=kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            scrolllist.append(listentry.Get('Generic', data=data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def OpenSettings(self):
        form.BroadcastSettings.Open()

    def OnClear(self, *args):
        selectedValue = self.combo.selectedValue
        self.ClearHistory(selectedValue)

    def OnScrollHistoryChar(self, *args):
        uicls.ScrollCore.OnChar(self, *args)

    def OnScrollBroadcastChar(self, *args):
        return False

    def GetBroadcastListEntry(self, data):
        label = localization.GetByLabel('UI/Fleet/FleetBroadcast/Event', time=data.time, eventLabel=data.broadcastLabel)
        data2 = util.KeyVal(charID=data.charID, label=label, GetMenu=self.GetBroadcastMenu, data=data)
        return data2

    def GetVoiceListEntry(self, data):
        eventText = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventSpeaking', charID=data.charID, channelName=data.channelName)
        label = localization.GetByLabel('UI/Fleet/FleetBroadcast/Event', time=data.time, eventLabel=eventText)
        data2 = util.KeyVal(channel=data.channelID, charID=data.charID, label=label, GetMenu=fleetbr.GetVoiceMenu)
        return data2

    def OnSpeakingEvent_Local(self, data):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('voicehistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetLootEvent_Local(self):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('loothistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetJoin_Local(self, rec):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetLeave_Local(self, rec):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetMemberChanged_Local(self, *args):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def GetBroadcastMenu(self, entry):
        m = []
        data = entry.sr.node.data
        func = getattr(fleetbr, 'GetMenu_%s' % data.name, None)
        if func:
            m = func(data.charID, data.solarSystemID, data.itemID)
            m += [None]
        m += fleetbr.GetMenu_Member(data.charID)
        m += [None]
        m += fleetbr.GetMenu_Ignore(data.name)
        return m

    def GetLootMenu(self, entry):
        m = []
        data = entry.sr.node.data
        m += sm.GetService('menu').GetMenuFormItemIDTypeID(None, data.typeID, ignoreMarketDetails=0)
        m += [None]
        m += fleetbr.GetMenu_Member(data.charID)
        return m

    def GetMemberMenu(self, entry):
        m = []
        data = entry.sr.node.data
        m += fleetbr.GetMenu_Member(data.charID)
        return m

    def OnFleetBroadcast_Local(self, broadcast):
        self.RefreshBroadcastHistory()

    def OnFleetBroadcastFilterChange(self):
        self.RefreshBroadcastHistory()

    def RefreshBroadcastHistory(self):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('broadcasthistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)


class BroadcastEntryMixin():

    def PostStartup(self):
        self.sr.iconRoleContainer = uicls.Container(name='iconRoleContainer', parent=self, align=uiconst.TORIGHT, width=16, height=16, state=uiconst.UI_DISABLED, left=const.defaultPadding)
        self.sr.labelclipper = uicls.Container(name='labelclipper', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, clipChildren=True)
        uiutil.Transplant(self.sr.label, self.sr.labelclipper)
        self.sr.label.maxLines = 1
        self.sr.label.state = uiconst.UI_DISABLED
        self.sr.label.width = self.absoluteRight - self.absoluteLeft
        icon = uicls.Sprite(align=uiconst.RELATIVE, left=4, top=2, width=16, height=16)
        icon.state = uiconst.UI_DISABLED
        self.children.append(icon)
        self.sr.icon = icon
        self.sr.label.left += icon.left + icon.width
        self.sr.iconRole = icon = uicls.Sprite(name='iconRole', align=uiconst.RELATIVE, top=2, left=0, width=16, height=16)
        icon.state = uiconst.UI_DISABLED
        self.sr.iconRoleContainer.children.append(icon)

    def Load_(self, node):
        self.sr.node = node
        self.sr.label.text = node.label
        icon = node.Get('icon', None)
        if icon is None:
            self.sr.icon.state = uiconst.UI_HIDDEN
        else:
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.icon.LoadIcon(icon)
        self.sr.icon.color.a = 0.0
        iconRole = node.Get('iconRole', None)
        if iconRole is None:
            self.sr.iconRole.parent.state = uiconst.UI_HIDDEN
        else:
            self.sr.iconRole.parent.state = uiconst.UI_DISABLED
            self.sr.iconRole.LoadIcon(iconRole)
        uthread.worker('BroadcastEntryMixin::Flash', self.Flash)
        self.height = self.sr.label.height = self.sr.icon.height + 4

    def GetHeight(self, *args):
        node, width = args
        node.height = max(16, uix.GetTextHeight(node.label)) + 4
        return node.height

    def DisplayActive(self, isActive):
        self.sr.label.text = self.sr.node.rawText

    def Flash(self):
        period = 0.7
        cycles = 3
        duration = period * int(cycles)
        node = self.sr.node
        coeff = math.pi / period
        while True:
            if node != util.GetAttrs(self, 'sr', 'node'):
                return
            time = (blue.os.GetWallclockTime() - node.Get('timeReceived', 0)) / 10000000.0
            if time >= duration:
                self.sr.icon.color.a = 1.0
                return
            self.sr.icon.color.a = 1.0 - math.sin(coeff * (time % period))
            blue.pyos.synchro.SleepWallclock(10)

    Flash = uiutil.ParanoidDecoMethod(Flash, ('sr', 'node'))


def CopyFunctions(class_, locals):
    for name, fn in class_.__dict__.iteritems():
        if type(fn) is type(CopyFunctions):
            if name in locals:
                raise RuntimeError, 'What are you trying to do here?'
            locals[name] = fn


class BroadcastSettings(uicls.Window):
    __guid__ = 'form.BroadcastSettings'
    default_windowID = 'broadcastsettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.SetCaption(localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastSettings'))
        self.SetMinSize([300, 200])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.main.left = self.sr.main.width = self.sr.main.top = self.sr.main.height = const.defaultPadding
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastSettingsHelp'), parent=self.sr.main, align=uiconst.TOTOP, left=20, state=uiconst.UI_NORMAL)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=6)
        self.sr.scrollBroadcasts = uicls.Scroll(name='scrollBroadcasts', parent=self.sr.main)
        self.sr.scrollBroadcasts.multiSelect = 0
        self.LoadFilters()

    def LoadFilters(self):
        scrolllist = []
        history = sm.GetService('fleet').broadcastHistory
        for name, labelName in fleetbr.broadcastNames.iteritems():
            data = util.KeyVal()
            if name == 'Event':
                rngName = ''
            else:
                rng = fleetbr.GetBroadcastWhere(name)
                rngName = fleetbr.GetBroadcastWhereName(rng)
            n = len([ b for b in history if b.name == name or name == 'Event' and b.name not in fleetbr.types.keys() ])
            data.label = localization.GetByLabel(labelName) + '<t>' + rngName + '<t>%d' % n
            data.props = None
            data.checked = bool(settings.user.ui.Get('listenBroadcast_%s' % name, True))
            data.cfgname = name
            data.retval = None
            data.hint = None
            data.OnChange = self.Filter_OnCheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        self.sr.scrollBroadcasts.sr.id = 'scrollBroadcasts'
        self.sr.scrollBroadcasts.Load(headers=[localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastType'), localization.GetByLabel('UI/Fleet/FleetBroadcast/RecipientRange'), localization.GetByLabel('UI/Fleet/FleetBroadcast/NumBroadcasts')], contentList=scrolllist)

    def Filter_OnCheckBoxChange(self, cb):
        sm.GetService('fleet').SetListenBroadcast(cb.data['key'], cb.checked)