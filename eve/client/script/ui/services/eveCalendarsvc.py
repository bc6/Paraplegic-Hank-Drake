import uiconst
import service
import svc
import blue
import sys
import log
import os
import const
import moniker
import uiconst
import util
import zlib
import form
import xtriui
import uiutil
import uthread
import uix
import uicls
import state
RESPONSETYPES = {const.eventResponseAccepted: mls.UI_CAL_ACCEPTED,
 const.eventResponseDeclined: mls.UI_CAL_DECLINED,
 const.eventResponseDeleted: mls.UI_CAL_EVENTCANCELED,
 const.eventResponseUninvited: mls.UI_CAL_UNINVITED,
 const.eventResponseUndecided: mls.UI_CAL_NOTRESPONDED,
 const.eventResponseMaybe: mls.UI_CAL_MAYBEREPLY}
EVENTTYPES = {const.calendarTagPersonal: mls.UI_CAL_GROUPPERSONCAL,
 const.calendarTagCorp: mls.UI_CAL_GROUPCORP,
 const.calendarTagAlliance: mls.UI_CAL_GROUPALLIANCE,
 const.calendarTagCCP: mls.UI_CAL_GROUPCCP}

class EveCalendarSvc(svc.calendar):
    __guid__ = 'svc.eveCalendar'
    __displayname__ = 'Calendar service'
    __replaceservice__ = 'calendar'
    __exportedcalls__ = {'ShowCharacterInfo': [service.ROLE_IGB]}
    __notifyevents__ = ['OnNewCalendarEvent',
     'OnEditCalendarEvent',
     'OnRemoveCalendarEvent',
     'OnSessionChanged']
    __startupdependencies__ = ['settings']

    def Run(self, *etc):
        svc.calendar.Run(self, *etc)
        self._calendarProxy = None



    def GetCalendarProxy(self):
        if self._calendarProxy is None:
            self._calendarProxy = sm.ProxySvc('calendarProxy')
        return self._calendarProxy



    def OpenNewEventWnd(self, year, month, monthday, *args):
        configname = 'calendarNewEventWnd_%s_%s_%s' % (year, month, monthday)
        wnd = sm.GetService('window').GetWindow(configname, create=1, decoClass=form.CalendarNewEventWnd, maximize=1, year=year, month=month, monthday=monthday)



    def CreateNewEvent(self, dateTime, duration, title, description, eventTag, important = 0, invitees = []):
        if not title.strip():
            raise UserError('CalendarEventMustSpecifyTitle')
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(dateTime)
        if self.IsTooFarInFuture(year, month):
            raise UserError('CalendarTooFarIntoFuture', {'numMonths': const.calendarViewRangeInMonths})
        if len(title) > const.calendarMaxTitleSize:
            raise UserError('CalendarTitleTooLong')
        newEventID = None
        if eventTag == const.calendarTagPersonal:
            if invitees:
                newEventID = util.CSPAChargedAction('CSPACalendarCheck', self.calendarMgr, 'CreatePersonalEvent', dateTime, duration, title, description, important, invitees)
            else:
                newEventID = self.calendarMgr.CreatePersonalEvent(dateTime, duration, title, description, important, invitees)
            if newEventID is not None:
                self.OnNewCalendarEvent(eventID=newEventID, ownerID=session.charid, eventDateTime=dateTime, eventDuration=duration, eventTitle=title, importance=important)
                if self.eventResponses is not None:
                    self.eventResponses[newEventID] = const.eventResponseAccepted
        elif eventTag == const.calendarTagCorp:
            newEventID = self.calendarMgr.CreateCorporationEvent(dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagAlliance:
            newEventID = self.calendarMgr.CreateAllianceEvent(dateTime, duration, title, description, important)



    def UpdateEventParticipants(self, eventID, charsToAdd, charsToRemove):
        if eventID is not None:
            if len(charsToAdd) > 0:
                util.CSPAChargedAction('CSPACalendarCheck', self.calendarMgr, 'UpdateEventParticipants', eventID, charsToAdd, charsToRemove)
            elif len(charsToRemove) > 0:
                self.calendarMgr.UpdateEventParticipants(eventID, charsToAdd, charsToRemove)
            self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, session.charid)



    def EditEvent(self, eventID, oldDateTime, dateTime, duration, title, description, eventTag, important = 0):
        if oldDateTime != dateTime:
            if eve.Message('CalendarEventEditDate', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        if eventTag == const.calendarTagPersonal:
            self.calendarMgr.EditPersonalEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagCorp:
            self.calendarMgr.EditCorporationEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagAlliance:
            self.calendarMgr.EditAllianceEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        return True



    def GetEventFlag(self, ownerID):
        if ownerID == session.corpid:
            return const.calendarTagCorp
        else:
            if ownerID == session.allianceid:
                return const.calendarTagAlliance
            if ownerID == const.ownerSystem:
                return const.calendarTagCCP
            return const.calendarTagPersonal



    def GetEventsByMonthYear(self, month, year):
        eventList = self.events.get((month, year))
        if eventList is None:
            eventList = []
            dbRowList = self.GetCalendarProxy().GetEventList(month, year)
            for dbRows in dbRowList:
                if dbRows is not None:
                    eventList.extend([ util.KeyVal(x) for x in dbRows.Unpack() ])

            for x in eventList:
                x.flag = self.GetEventFlag(x.ownerID)

            self.events[(month, year)] = eventList
        return eventList



    def GetEventResponses(self):
        if self.eventResponses is None:
            dbRows = self.calendarMgr.GetResponsesForCharacter()
            self.eventResponses = {}
            for dbRow in dbRows:
                self.eventResponses[dbRow.eventID] = dbRow.status

        return self.eventResponses



    def GetEventDetails(self, eventID, ownerID):
        if eventID not in self.eventDetails:
            self.eventDetails[eventID] = self.GetCalendarProxy().GetEventDetails(eventID, ownerID)
        return self.eventDetails[eventID]



    def OpenSingleDayWnd(self, config, year, month, monthday, events, isADay = 1, *args):
        wnd = sm.GetService('window').GetWindow('singleDayWnd', create=0, decoClass=form.CalendarSingleDayWnd)
        configname = '%s_%s_%s_%s' % (config,
         year,
         month,
         monthday)
        if wnd:
            if wnd.configname == configname:
                wnd.Maximize()
                return 
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if shift:
                wnd = sm.GetService('window').GetWindow('singleDayWnd', create=1, decoClass=form.CalendarSingleDayWnd, maximize=1, ignoreCurrent=1, config=config, year=year, month=month, monthday=monthday, events=events, configname=configname, isADay=isADay)
                return 
            while wnd:
                wnd.CloseX()
                wnd = sm.GetService('window').GetWindow('singleDayWnd', create=0, decoClass=form.CalendarSingleDayWnd)

        wnd = sm.GetService('window').GetWindow('singleDayWnd', create=1, decoClass=form.CalendarSingleDayWnd, maximize=1, config=config, year=year, month=month, monthday=monthday, events=events, configname=configname, isADay=isADay)



    def OpenEventWnd(self, eventInfo, edit = 0, *args):
        (year, month, wd, monthday, hour, min, sec, ms,) = util.GetTimeParts(eventInfo.eventDateTime)
        name = 'calendarEventWnd_%s' % eventInfo.eventID
        if edit:
            wnd = sm.GetService('window').GetWindow(name, create=0, decoClass=form.CalendarNewEventWnd)
            if wnd and not wnd.inEditMode:
                wnd.CloseX()
        wnd = sm.GetService('window').GetWindow(name, create=1, decoClass=form.CalendarNewEventWnd, maximize=1, year=year, month=month, monthday=monthday, eventInfo=eventInfo, edit=edit)



    def RespondToEvent(self, eventID, eventKV, response):
        self.calendarMgr.SendEventResponse(eventID, eventKV.ownerID, response)
        if self.eventResponses is not None:
            self.eventResponses[eventID] = response
        if response != const.eventResponseDeclined:
            self.nextEvents[eventID] = eventKV
        elif eventID in self.nextEvents:
            self.nextEvents.pop(eventID, None)
        self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, eventKV.ownerID)
        sm.ScatterEvent('OnReloadToDo')
        sm.ScatterEvent('OnRespondToEvent')
        sm.ScatterEvent('OnReloadCalendar')



    def DeleteEvent(self, eventID, ownerID):
        if eve.Message('CalendarDeleteEvent', {}, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.calendarMgr.DeleteEvent(eventID, ownerID)
        name = 'calendarEventWnd_%s' % eventID
        wnd = sm.GetService('window').GetWindow(name, create=0, decoClass=form.CalendarNewEventWnd)
        if wnd:
            wnd.CloseX()
        return True



    def IsInNextEventsWindow(self, eventYear, eventMonth):
        (nowYear, nowMonth,) = util.GetYearMonthFromTime(blue.os.GetTime())
        if eventYear == nowYear:
            return eventMonth in (nowMonth, nowMonth + 1)
        if eventYear == nowYear + 1:
            return nowMonth == const.calendarDecember and eventMonth == const.calendarJanuary
        return False



    def OnNewCalendarEvent(self, eventID, ownerID, eventDateTime, eventDuration, eventTitle, importance, doBlink = True):
        (year, month,) = util.GetYearMonthFromTime(eventDateTime)
        now = blue.os.GetTime()
        eventList = self.events.get((month, year))
        if eventList is not None:
            if eventID not in [ x.eventID for x in eventList ]:
                eventKV = util.KeyVal(eventID=eventID, ownerID=ownerID, eventDateTime=eventDateTime, eventDuration=eventDuration, eventTitle=eventTitle, importance=importance, flag=self.GetEventFlag(ownerID))
                eventKV.isDeleted = False
                eventKV.dateModified = blue.os.GetTime()
                eventList.append(eventKV)
                self.events[(month, year)] = eventList
                if eventDateTime > now and self.IsInNextEventsWindow(year, month):
                    self.nextEvents[eventID] = eventKV
        if doBlink and ownerID != session.charid and eventDateTime > now and self.IsInNextEventsWindow(year, month):
            sm.GetService('neocom').Blink('clock')
        sm.ScatterEvent('OnReloadCalendar')
        sm.ScatterEvent('OnReloadToDo')



    def OnEditCalendarEvent(self, eventID, ownerID, oldEventDateTime, eventDateTime, eventDuration, eventTitle, importance):
        (oldYear, oldMonth,) = util.GetYearMonthFromTime(oldEventDateTime)
        if eventID in self.nextEvents:
            self.nextEvents.pop(eventID)
        if eventID in self.eventDetails:
            self.eventDetails.pop(eventID)
        if oldEventDateTime != eventDateTime:
            if self.eventResponses is None:
                self.GetEventResponses()
            if ownerID != session.charid:
                oldReply = self.eventResponses.get(eventID, const.eventResponseUndecided)
                if oldReply in (const.eventResponseUndecided, const.eventResponseAccepted, const.eventResponseMaybe):
                    self.eventResponses[eventID] = const.eventResponseUndecided
                    (year, month,) = util.GetYearMonthFromTime(eventDateTime)
                    if eventDateTime > blue.os.GetTime() and self.IsInNextEventsWindow(year, month):
                        sm.GetService('neocom').Blink('clock')
            self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, ownerID)
        eventList = self.events.get((oldMonth, oldYear))
        if eventList is not None:
            for evt in eventList:
                if eventID == evt.eventID:
                    eventList.remove(evt)

            self.events[(oldMonth, oldYear)] = eventList
        self.OnNewCalendarEvent(eventID, ownerID, eventDateTime, eventDuration, eventTitle, importance, False)



    def OnRemoveCalendarEvent(self, eventID, eventDateTime, isDeleted):
        (year, month, wd, monthday, hour, min, sec, ms,) = util.GetTimeParts(eventDateTime)
        eventList = self.events.get((month, year))
        if eventList is not None:
            for x in eventList:
                if x.eventID == eventID:
                    if isDeleted:
                        x.isDeleted = True
                        x.dateModified = blue.os.GetTime()
                    else:
                        eventList.remove(x)
                    break

            self.events[(month, year)] = eventList
            if eventID in self.eventResponses and self.eventResponses.get(eventID, None) != const.eventResponseDeclined:
                self.eventResponses.pop(eventID)
        self.nextEventsFetched = False
        sm.ScatterEvent('OnReloadToDo')
        sm.ScatterEvent('OnReloadCalendar')



    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.events = {}
            self.nextEvents = {}
            self.nextEventsFetched = False
            sm.ScatterEvent('OnReloadToDo')
            sm.ScatterEvent('OnReloadCalendar')



    def GetResponsesToEvent(self, eventID, ownerID):
        dbRows = self.calendarMgr.GetResponsesToEvent(eventID, ownerID)
        responseDict = {}
        for row in dbRows:
            if row.status != const.eventResponseUninvited:
                responseDict[row.characterID] = row.status

        return responseDict



    def GetResponsesToEventInStatusDict(self, eventID, responseDict):
        statusDict = {}
        accepted = []
        rejected = []
        noreply = []
        maybe = []
        for (charID, response,) in responseDict.iteritems():
            if response == const.eventResponseUndecided:
                noreply.append(charID)
            elif response == const.eventResponseDeclined:
                rejected.append(charID)
            elif response == const.eventResponseAccepted:
                accepted.append(charID)
            elif response == const.eventResponseMaybe:
                maybe.append(charID)

        statusDict[const.eventResponseUndecided] = noreply
        statusDict[const.eventResponseDeclined] = rejected
        statusDict[const.eventResponseAccepted] = accepted
        statusDict[const.eventResponseMaybe] = maybe
        return statusDict



    def GetResponseIconNum(self, response):
        if response == const.eventResponseAccepted:
            return 'ui_38_16_193'
        if response in [const.eventResponseDeclined, const.eventResponseDeleted]:
            return 'ui_38_16_194'
        if response == const.eventResponseUndecided:
            return 'ui_38_16_177'
        if response == const.eventResponseMaybe:
            return 'ui_38_16_195'
        return 'ui_38_16_192'



    def GetLongResponseIconPath(self, response):
        return self.GetResponseIconNum(response)



    def GetMyResponseIconFromID(self, eventID, long = 0, getDeleted = 0):
        if getDeleted:
            myResponse = const.eventResponseDeleted
        else:
            myResponse = self.GetMyResponse(eventID)
        if long:
            icon = self.GetLongResponseIconPath(myResponse)
        else:
            icon = self.GetResponseIconNum(myResponse)
        return (icon, myResponse)



    def GetActiveTags(self, *args):
        showTags = 0
        tagList = [const.calendarTagPersonal,
         const.calendarTagCorp,
         const.calendarTagAlliance,
         const.calendarTagCCP]
        for tag in tagList:
            checked = settings.user.ui.Get('calendarTagCheked_%s' % tag, 1)
            if checked:
                showTags += tag

        return showTags



    def LoadTagIcon(self, tag):
        if tag not in [const.calendarTagCorp, const.calendarTagAlliance, const.calendarTagCCP]:
            return 
        else:
            tagIconCont = uicls.Container(name='tagIconCont', parent=None, align=uiconst.TOPLEFT, pos=(0, 0, 14, 14))
            self.LoadTagIconInContainer(tag, tagIconCont, left=0, top=0)
            return tagIconCont



    def LoadTagIconInContainer(self, tag, cont, left = 2, top = 4, *args):
        uiutil.Flush(cont)
        if tag == const.calendarTagCorp:
            uix.SetStateFlagForFlag(cont, state.flagSameCorp, top=top, left=left, showHint=True)
        elif tag == const.calendarTagAlliance:
            uix.SetStateFlagForFlag(cont, state.flagSameAlliance, top=top, left=left, showHint=True)
        elif tag == const.calendarTagCCP:
            self.LoadCCPIcon(cont, top, left)



    def LoadCCPIcon(self, container, top, left, *args):
        if getattr(container.sr, 'flag', None) is None:
            container.sr.flag = uicls.Container(parent=container, pos=(0, 0, 10, 10), name='flag', state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
            uicls.Sprite(parent=container.sr.flag, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE)
            uicls.Fill(parent=container.sr.flag)
        col = (0.7, 0.7, 0.7, 0.75)
        container.sr.flag.children[1].color.SetRGB(*col)
        container.sr.flag.width = container.sr.flag.height = 9
        container.sr.flag.left = left
        container.sr.flag.top = top
        container.sr.flag.children[0].rectLeft = 20



    def GetMyChangedEvents(self, monthsAhead = 1):
        events = self.GetEventsNextXMonths(monthsAhead)
        showTag = self.GetActiveTags()
        changedEvents = {}
        now = blue.os.GetTime()
        for (eventID, eventKV,) in events.iteritems():
            if self.IsInUpdateEventsList(now, eventKV) and (showTag is None or showTag & eventKV.flag != 0):
                changedEvents[eventID] = eventKV

        return changedEvents



    def GetMyNextEvents(self, monthsAhead = 1):
        events = self.GetEventsNextXMonths(monthsAhead)
        showTag = self.GetActiveTags()
        myNextEvents = {}
        now = blue.os.GetTime()
        for (eventID, eventKV,) in events.iteritems():
            if self.IsOnToDoList(now, eventKV) and (showTag is None or showTag & eventKV.flag != 0):
                myNextEvents[eventID] = eventKV

        return myNextEvents



    def GetEventsNextXMonths(self, monthsAhead = 1, force = 0):
        if getattr(self, 'nextEventsFetched', False) and not force:
            return self.nextEvents
        self.nextEvents = self.FetchNextEvents(monthsAhead=monthsAhead)
        self.nextEventsFetched = True
        return self.nextEvents



    def FetchNextEvents(self, monthsAhead = 1):
        now = blue.os.GetTime()
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(now)
        nextEvents = self.FetchNextEventsDict(month, year, now)
        for i in xrange(monthsAhead):
            monthsFromNow = i + 1
            (y, m,) = self.GetBrowsedMonth(monthsFromNow, year, month)
            nextMonthEvents = self.FetchNextEventsDict(m, y, now)
            nextEvents.update(nextMonthEvents)

        return nextEvents



    def FetchNextEventsDict(self, month, year, now):
        dict = {}
        events = self.GetEventsByMonthYear(month, year)
        for eventKV in events:
            dict[eventKV.eventID] = eventKV

        return dict



    def IsOnToDoList(self, now, eventKV):
        if eventKV.eventDateTime < now:
            return False
        if eventKV.isDeleted:
            return False
        if self.GetMyResponse(eventKV.eventID) in [const.eventResponseDeclined]:
            return False
        return True



    def IsInUpdateEventsList(self, now, eventKV):
        if now > eventKV.eventDateTime:
            return False
        myResponse = self.GetMyResponse(eventKV.eventID)
        if eventKV.isDeleted and myResponse != const.eventResponseDeclined:
            return True
        if myResponse == const.eventResponseUndecided:
            return True
        return False



    def GetMyResponse(self, eventID):
        if self.eventResponses is None:
            self.GetEventResponses()
        myResponse = self.eventResponses.get(eventID, const.eventResponseUndecided)
        return myResponse



    def GetEventHint(self, eventInfo, myResponse):
        if eventInfo is None:
            return ''
        if eventInfo.eventDuration is None:
            durationLabel = mls.UI_SHARED_NOTSPECIFIED
        else:
            hours = eventInfo.eventDuration / 60
            if hours > 1:
                durationLabel = mls.UI_CAL_NUMHOURS % {'num': hours}
            else:
                durationLabel = mls.UI_CAL_ONEHOUR
        responseLabel = self.GetResponseType().get(myResponse, mls.UI_GENERIC_UNKNOWN)
        if getattr(eventInfo, 'eventTimeStamp', None) is None:
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(eventInfo.eventDateTime)
            eventInfo.eventTimeStamp = '%02d:%02d' % (hour, min)
        hint = '%(time)s %(title)s<br>%(eventType)s<br>%(response)s<br>%(durationText)s: %(duration)s<br>%(ownerText)s: %(owner)s' % {'time': eventInfo.eventTimeStamp,
         'title': eventInfo.eventTitle,
         'response': responseLabel,
         'eventType': self.GetEventTypes().get(eventInfo.flag, '-'),
         'durationText': mls.UI_GENERIC_DURATION,
         'duration': durationLabel,
         'ownerText': mls.UI_GENERIC_OWNER,
         'owner': cfg.eveowners.Get(eventInfo.ownerID).name}
        if eventInfo.importance > 0:
            hint += '<br>%s ' % mls.UI_GENERIC_IMPORTANT
        return hint



    def GetResponseType(self, *args):
        return RESPONSETYPES



    def GetEventTypes(self, *args):
        return EVENTTYPES



    def ShowCharacterInfo(self, itemID):
        return sm.GetService('info').ShowInfo(const.typeCharacterGallente, itemID)



    def FindCalendar(self, *args):
        calendar = None
        wnd = sm.GetService('window').GetWindow('calendar', create=0, decoClass=form.eveCalendarWnd)
        if wnd:
            calendar = wnd.sr.calendarForm
        return calendar




