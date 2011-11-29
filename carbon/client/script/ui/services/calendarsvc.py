import service
import blue
import const
import util
import localization
const.calendarMonday = 0
const.calendarTuesday = 1
const.calendarWednesday = 2
const.calendarThursday = 3
const.calendarFriday = 4
const.calendarSaturday = 5
const.calendarSunday = 6
const.calendarJanuary = 1
const.calendarFebruary = 2
const.calendarMarch = 3
const.calendarApril = 4
const.calendarMay = 5
const.calendarJune = 6
const.calendarJuly = 7
const.calendarAugust = 8
const.calendarSeptember = 9
const.calendarOctober = 10
const.calendarNovember = 11
const.calendarDecember = 12
const.calendarNumDaysInWeek = 7
const.calendarTagPersonal = 1
const.calendarTagCorp = 2
const.calendarTagAlliance = 4
const.calendarTagCCP = 8
const.calendarViewRangeInMonths = 12
const.eventResponseUninvited = 0
const.eventResponseDeleted = 1
const.eventResponseDeclined = 2
const.eventResponseUndecided = 3
const.eventResponseAccepted = 4
const.eventResponseMaybe = 5
MONTHANDYEAR_NAME_TEXT = ['/Carbon/UI/Common/MonthsWithYear/January',
 '/Carbon/UI/Common/MonthsWithYear/February',
 '/Carbon/UI/Common/MonthsWithYear/March',
 '/Carbon/UI/Common/MonthsWithYear/April',
 '/Carbon/UI/Common/MonthsWithYear/May',
 '/Carbon/UI/Common/MonthsWithYear/June',
 '/Carbon/UI/Common/MonthsWithYear/July',
 '/Carbon/UI/Common/MonthsWithYear/August',
 '/Carbon/UI/Common/MonthsWithYear/September',
 '/Carbon/UI/Common/MonthsWithYear/October',
 '/Carbon/UI/Common/MonthsWithYear/November',
 '/Carbon/UI/Common/MonthsWithYear/December']

class CalendarSvc(service.Service):
    __guid__ = 'svc.calendar'
    __servicename__ = 'calendar service'
    __displayname__ = 'Calendar Service'
    __notifyevents__ = []
    __dependencies__ = ['objectCaching']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, ms = None):
        self.state = service.SERVICE_START_PENDING
        self.events = {}
        self.eventDetails = {}
        self.nextEvents = {}
        self.eventResponses = None
        self.calendarMgr = sm.RemoteSvc('calendarMgr')
        self.state = service.SERVICE_RUNNING



    def OpenNewEventWnd(self, year, month, monthday, *args):
        pass



    def OpenExistingEventWnd(self, *args):
        pass



    def CreateNewEvent(self, dateTime, duration, title, description, eventTag, important = 0, invitees = []):
        pass



    def IsInPast(self, year, month, monthday, hour = 0, min = 0, allowToday = 0, *args):
        now = blue.os.GetWallclockTime()
        if allowToday:
            (cyear, cmonth, cwd, cday, chour, cmin, csec, cms,) = util.GetTimeParts(now)
            now = blue.os.GetTimeFromParts(cyear, cmonth, cday, 0, 0, 0, 0)
        thisDay = blue.os.GetTimeFromParts(year, month, monthday, hour, min, 0, 0)
        return self.IsInPastFromBlueTime(thisDay, now)



    def IsInPastFromBlueTime(self, then, now = None, *args):
        if now is None:
            now = blue.os.GetWallclockTime()
        inPast = now > then
        return inPast



    def IsTooFarInFuture(self, year, month):
        now = blue.os.GetWallclockTime()
        (rlYear, rlMonth, wd, day, hour, min, sec, ms,) = util.GetTimeParts(now)
        nowNumMonths = rlYear * 12 + rlMonth
        thenNumMonths = year * 12 + month
        difference = thenNumMonths - nowNumMonths
        if difference > const.calendarViewRangeInMonths:
            return True
        return False



    def GetEventsByMonthYear(self, month, year):
        return []



    def FlushCache(self):
        self.events = {}
        self.nextEvents = {}



    def OpenSingleDayWnd(self, config, year, month, monthday, *args):
        pass



    def GetMonthText(self, year, month, *args):
        return localization.GetByLabel(MONTHANDYEAR_NAME_TEXT[(month - 1)], year=year)



    def OpenEventWnd(self, eventInfo, edit = 0, *args):
        pass



    def OpenEditEventWnd(self, eventInfo, *args):
        self.OpenEventWnd(eventInfo, edit=1)



    def EditEvent(self, *args):
        pass



    def RespondToEvent(self, eventID, eventKV, response):
        pass



    def DeleteEvent(self, eventID, ownerID):
        pass



    def GetActiveTags(self, *args):
        pass



    def GetMyNextEvents(self, monthsAhead = 1):
        return {}



    def GetMyChangedEvents(self, monthsAhead = 1):
        return {}



    def LoadTagIcon(self, tag):
        return None



    def LoadTagIconInContainer(self, tag, cont, left = 2, top = 4, *args):
        pass



    def GetBrowsedMonth(self, direction, year, month):
        if direction == 1:
            if month == const.calendarDecember:
                year += 1
                month = const.calendarJanuary
            else:
                month += 1
        elif direction == -1:
            if month == const.calendarJanuary:
                year -= 1
                month = const.calendarDecember
            else:
                month -= 1
        return (year, month)



    def GetEventResponses(self, *args):
        return None



    def GetEventMenu(self, eventInfo, myResponse = None, getJumpOption = True, *args):
        m = []
        m.append((localization.GetByLabel('/Carbon/UI/Calendar/ViewEvent'), self.OpenEventWnd, (eventInfo,)))
        if getattr(eventInfo, 'isDeleted', None):
            return m
        canDelete = 0
        if not self.IsInPastFromBlueTime(then=eventInfo.eventDateTime):
            if eventInfo.ownerID != session.charid:
                if eventInfo.flag in [const.calendarTagCorp, const.calendarTagAlliance]:
                    if eventInfo.ownerID in [session.corpid, session.allianceid] and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
                        canDelete = 1
                        m.append((localization.GetByLabel('/Carbon/UI/Calendar/EditEvent'), self.OpenEditEventWnd, (eventInfo,)))
                if myResponse is None:
                    (iconPath, myResponse,) = self.GetMyResponseIconFromID(eventInfo.eventID)
                m.append(None)
                if eventInfo.flag is not const.calendarTagCCP:
                    if myResponse != const.eventResponseAccepted:
                        m.append((localization.GetByLabel('/Carbon/UI/Calendar/Accept'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseAccepted)))
                    if myResponse != const.eventResponseMaybe:
                        m.append((localization.GetByLabel('/Carbon/UI/Calendar/MaybeReply'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseMaybe)))
                    if myResponse != const.eventResponseDeclined:
                        m.append((localization.GetByLabel('/Carbon/UI/Calendar/Decline'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseDeclined)))
            elif eventInfo.flag == const.calendarTagPersonal:
                canDelete = 1
                m.append((localization.GetByLabel('/Carbon/UI/Calendar/EditEvent'), self.OpenEditEventWnd, (eventInfo,)))
        if getJumpOption:
            m.append(None)
            m.append((localization.GetByLabel('/Carbon/UI/Calendar/GotoDay'), self.JumpToDay, (eventInfo,)))
        if canDelete:
            m.append(None)
            m.append((localization.GetByLabel('/Carbon/UI/Calendar/DeleteEvent'), self.DeleteEvent, (eventInfo.eventID, eventInfo.ownerID)))
        return m



    def GetEventHint(self, eventInfo, myResponse):
        time = eventInfo.eventTimeStamp
        title = eventInfo.eventTitle
        timeAndTitle = '%s %s' % (time, title)
        return timeAndTitle



    def GetMyResponseIconFromID(self, eventID, long = 0, getDeleted = 0):
        return ('', 0)



    def FetchNextEvents(self, monthsAhead = 1):
        pass



    def JumpToDay(self, eventInfo):
        calendar = self.FindCalendar()
        if calendar:
            (year, month, wd, monthday, hour, min, sec, ms,) = util.GetTimeParts(eventInfo.eventDateTime)
            calendar.SetMonth(year, month, updateInView=1)
            blue.synchro.Yield()
            if calendar and not calendar.destroyed:
                calendar.CrawlForAndSetMonthday(monthday)



    def FindCalendar(self, *args):
        return None




