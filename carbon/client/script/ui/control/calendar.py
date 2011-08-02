import blue
import uthread
import uiutil
import util
import uiconst
import uicls
import calendar
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
const.defaultPadding = 4
NUM_DAYROWS = 6

class Calendar(uicls.Container):
    __guid__ = 'form.Calendar'
    __notifyevents__ = ['OnReloadCalendar', 'OnReloadEvents', 'OnCalendarFilterChange']
    default_width = 256
    default_height = 256

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        sm.GetService('calendar').GetEventResponses()
        self.monthInView = None
        self.allDayBoxes = []
        self.allDayBoxesByRows = {}
        self.allHeaderBoxes = []
        self.allDayRows = {}
        self.dayBoxesByDates = {}
        self.headerHeight = 24
        self.dayPadding = 1
        self.isTabStop = 1
        self.selectedDay = None
        self.disbleForward = False
        self.disbleBack = False
        self.Setup()
        self.InsertData()



    def Setup(self):
        sm.RegisterNotify(self)
        now = blue.os.GetTime()
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(now)
        self.today = (year, month, day)
        self.calendar = calendar.Calendar()
        self.sr.monthTextCont = uicls.Container(name='monthTextCont', parent=self, align=uiconst.TOTOP, pos=(0, 10, 0, 30))
        self.sr.gridCont = uicls.Container(name='gridCont', parent=self, align=uiconst.TOALL, pos=(0,
         0,
         0,
         const.defaultPadding))
        uicls.Frame(parent=self.sr.gridCont, name='gridContFrame', state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25), pos=(-const.defaultPadding,
         0,
         -const.defaultPadding,
         -const.defaultPadding))
        self.InsertBrowseControls()
        boxWidth = boxHeight = 30
        self.allHeaderBoxes = []
        self.allDayBoxes = []
        self.allDayBoxesByRows = {}
        row = uicls.Container(name='row', parent=self.sr.gridCont, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.headerHeight))
        for j in xrange(0, const.calendarNumDaysInWeek):
            box = uicls.CalendarHeader(name='box', parent=row, align=uiconst.TOLEFT, pos=(0,
             0,
             boxWidth,
             0), padding=(self.dayPadding,
             self.dayPadding,
             self.dayPadding,
             self.dayPadding))
            self.allHeaderBoxes.append(box)
            setattr(self.sr, '%s_%s' % (0, j), box)

        row = None
        for i in xrange(1, NUM_DAYROWS + 1):
            row = uicls.Container(name='row', parent=self.sr.gridCont, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             boxHeight))
            self.allDayRows[i] = row
            daysInRow = []
            box = None
            for j in xrange(0, const.calendarNumDaysInWeek):
                configname = '%s_%s' % (i, j)
                box = self.GetDay(row, boxWidth, configname)
                self.allDayBoxes.append(box)
                daysInRow.append(box)
                setattr(self.sr, configname, box)

            if box is not None:
                box.SetAlign(uiconst.TOALL)
                box.width = 0
            self.allDayBoxesByRows[i] = daysInRow

        if row is not None:
            row.SetAlign(uiconst.TOALL)
            row.height = 0
        (boxWidth, boxHeight,) = self.SetSizes()



    def GetDay(self, parent, width, configname):
        box = uicls.CalendarDay(name='box', parent=parent, align=uiconst.TOLEFT, pos=(0,
         0,
         width,
         0), padding=(self.dayPadding,
         self.dayPadding,
         self.dayPadding,
         self.dayPadding), configname=configname)
        box.DoClickDay = self.DoClickDay
        box.DoDblClickDay = self.DoDblClickDay
        return box



    def _OnResize(self, *args):
        uicls.Container._OnResize(self, *args)
        if not self.destroyed and self.sr.gridCont:
            self.SetSizes()



    def SetSizes(self):
        (l, t, w, h,) = self.sr.gridCont.GetAbsolute()
        newBoxWidth = w / const.calendarNumDaysInWeek
        newBoxHeight = (h - self.headerHeight) / NUM_DAYROWS
        newBoxWidth -= 2 * self.dayPadding
        newBoxHeight -= 2 * self.dayPadding
        for box in self.allHeaderBoxes:
            box.width = newBoxWidth

        row = None
        for row in self.allDayRows.values():
            row.height = newBoxHeight

        if row is not None:
            row.height = 0
        counter = 0
        for box in self.allDayBoxes:
            counter += 1
            if counter >= const.calendarNumDaysInWeek:
                counter = 0
            else:
                box.width = newBoxWidth
            box.CheckEventsClipped()

        return (newBoxWidth, newBoxHeight)



    def InsertBrowseControls(self, *args):
        self.sr.backBtn = uicls.Container(name='backBtn', parent=self.sr.monthTextCont, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16))
        icon = uicls.Icon(parent=self.sr.backBtn, icon='ui_1_16_13', pos=(0, 0, 0, 0), hint=mls.UI_GENERIC_PREVIOUS)
        icon.OnClick = (self.ChangeMonth, -1)
        self.sr.fwdBtn = uicls.Container(name='fwdBtn', parent=self.sr.monthTextCont, align=uiconst.TOPRIGHT, pos=(0, 0, 16, 16))
        icon = uicls.Icon(parent=self.sr.fwdBtn, icon='ui_1_16_14', pos=(0, 0, 0, 0), hint=mls.UI_CMD_NEXT)
        icon.OnClick = (self.ChangeMonth, 1)



    def ChangeBrowseDisplay(self, btn, disable = 0):
        if disable:
            btn.opacity = 0.3
            btn.state = uiconst.UI_DISABLED
        else:
            btn.opacity = 1.0
            btn.state = uiconst.UI_NORMAL



    def ResetBrowse(self, *args):
        self.disbleBack = False
        self.disbleForward = False
        self.ChangeBrowseDisplay(self.sr.backBtn, disable=self.disbleBack)
        self.ChangeBrowseDisplay(self.sr.fwdBtn, disable=self.disbleForward)



    def InsertData(self, *args):
        self.SetCurrentRLMonth()
        self.SetHeader()



    def SetCurrentRLMonth(self, selectToday = True, *args):
        now = blue.os.GetTime()
        (year, month, wd, monthday, hour, min, sec, ms,) = util.GetTimeParts(now)
        self.yearMonthInView = (year, month)
        self.SetMonth(year, month)
        if selectToday:
            self.CrawlForAndSetMonthday(monthday)



    def OnReloadCalendar(self, *args):
        (year, month,) = self.yearMonthInView
        self.SetMonth(year, month)



    def OnReloadEvents(self, *args):
        self.LoadEvents()



    def AddMonthText(self, text = '', *args):
        if self.sr.get('monthText', None) is None:
            self.sr.monthText = uicls.Label(parent=self.sr.monthTextCont, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=1, idx=0)
        return self.sr.monthText



    def SetMonthText(self, year, month, *args):
        self.AddMonthText()
        text = sm.GetService('calendar').GetMonthText(year, month)
        self.sr.monthText.text = text



    def SetHeader(self, *args):
        j = 0
        i = 0
        for j in xrange(0, const.calendarNumDaysInWeek):
            dayName = self.GetDayNameText(j)
            day = self.sr.get('%s_%s' % (i, j), None)
            if day:
                day.SetDayName(dayName)
            j += 1




    def GetDayNameText(self, dayNumber):
        dayName = getattr(mls, 'UI_CAL_DAY%s' % dayNumber, '')
        return dayName



    def SetMonth(self, year, month, updateInView = 0, *args):
        if updateInView:
            self.yearMonthInView = (year, month)
        tags = sm.GetService('calendar').GetActiveTags()
        i = 1
        j = 0
        self.dayBoxesByDates = {}
        self.lastNextMonthDay = 0
        daysInMonth = self.calendar.monthdayscalendar(year, month)
        firstRow = daysInMonth[0]
        numEmptyDaysBefore = firstRow.count(0)
        emptyDaysBefore = []
        if emptyDaysBefore > 0:
            (newYear, newMonth,) = sm.GetService('calendar').GetBrowsedMonth(-1, year, month)
            monthRange = calendar.monthrange(newYear, newMonth)
            emptyDaysBefore = [ d for d in xrange(monthRange[1], monthRange[1] - numEmptyDaysBefore, -1) ]
        for (weekNumber, week,) in enumerate(daysInMonth):
            for monthday in week:
                notInMonth = 0
                if monthday == 0:
                    if weekNumber == 0:
                        monthday = emptyDaysBefore.pop(-1)
                        notInMonth = -1
                    else:
                        self.lastNextMonthDay += 1
                        monthday = self.lastNextMonthDay
                        notInMonth = 1
                self.ChangeDayBox(i, j, year, month, monthday, notInMonth)
                j += 1

            j = 0
            i += 1

        for i in xrange(i, NUM_DAYROWS + 1):
            for j in xrange(0, const.calendarNumDaysInWeek):
                self.lastNextMonthDay += 1
                monthday = self.lastNextMonthDay
                self.ChangeDayBox(i, j, year, month, monthday, notInMonth=1)


        self.SetMonthText(year, month)
        self.LoadEvents()



    def ChangeDayBox(self, i, j, year, month, monthday = 0, notInMonth = 0):
        day = self.sr.get('%s_%s' % (i, j), None)
        if day:
            today = False
            if notInMonth == 0:
                self.dayBoxesByDates[monthday] = day
                if self.today == (year, month, monthday):
                    today = True
            day.SetDay(year, month, monthday=monthday, notInMonth=notInMonth, today=today)



    def ChangeMonth(self, direction = 1, selectDay = 1, *args):
        (year, month,) = self.yearMonthInView
        if direction == -1 and self.disbleBack or direction == 1 and self.disbleForward:
            return False
        (year, month,) = sm.GetService('calendar').GetBrowsedMonth(direction, year, month)
        self.yearMonthInView = (year, month)
        self.SetMonth(year, month)
        now = blue.os.GetTime()
        (rlYear, rlMonth, wd, day, hour, min, sec, ms,) = util.GetTimeParts(now)
        nowNumMonths = rlYear * 12 + rlMonth
        thenNumMonths = year * 12 + month
        difference = thenNumMonths - nowNumMonths
        self.disbleForward = 0
        self.disbleBack = 0
        if direction == 1 and difference >= const.calendarViewRangeInMonths:
            fwdDisable = 1
            self.disbleForward = 1
        elif direction == -1 and -difference >= const.calendarViewRangeInMonths:
            backDisable = 1
            self.disbleBack = 1
        self.ChangeBrowseDisplay(self.sr.backBtn, disable=self.disbleBack)
        self.ChangeBrowseDisplay(self.sr.fwdBtn, disable=self.disbleForward)
        self.selectedDay = self.CrawlForValidDay(self.selectedDay, direction, 'day')
        if selectDay:
            self.SelectDay()
        return True



    def LoadEvents(self, *args):
        pass



    def LoadEventsToADay(self, date, eventsThisDay):
        dayBox = self.dayBoxesByDates.get(date, None)
        if dayBox is None:
            return 
        dayBox.LoadEvents(eventsThisDay)



    def OnCalendarFilterChange(self, *args):
        self.OnReloadCalendar()



    def OnKeyDown(self, vkey, flag, *args):
        if vkey == uiconst.VK_RIGHT:
            self.SelectNextDay(1)
        elif vkey == uiconst.VK_LEFT:
            self.SelectNextDay(-1)
        elif vkey == uiconst.VK_UP:
            self.SelectNextDay(-1, weekOrDay='week')
        elif vkey == uiconst.VK_DOWN:
            self.SelectNextDay(1, weekOrDay='week')
        elif vkey == uiconst.VK_RETURN:
            self.OpenDay()



    def OnSetFocus(self, *args):
        self.SelectDay()



    def SelectDay(self, *args):
        if self.selectedDay is None:
            self.selectedDay = self.sr.get('1_0', None)
        if self.selectedDay:
            for dayBox in self.allDayBoxes:
                if dayBox != self.selectedDay:
                    dayBox.SetSelectedFrameState(on=0)

            self.selectedDay.SetSelectedFrameState(on=1)



    def DoClickDay(self, day, *args):
        uthread.new(self.DoClickDay_thread, day)



    def DoClickDay_thread(self, day):
        if day.disabled:
            return 
        self.selectedDay = day
        self.SelectDay()



    def DoDblClickDay(self, day, *args):
        if uiutil.GetAttrs(day, 'disabled'):
            monthday = day.monthday
            self.ChangeMonth(day.disabled, selectDay=0)
            self.CrawlForAndSetMonthday(monthday)
        else:
            day.OpenSingleDayWnd()



    def SelectNextDay(self, direction = 1, weekOrDay = 'day', *args):
        currentlySelected = self.selectedDay
        usePreviousMonth = False
        useNextMonth = False
        if currentlySelected is None:
            newSelected = self.sr.get('1_0', None)
        else:
            newSelected = self.FindAnotherDay(currentlySelected, direction, weekOrDay)
        if newSelected:
            if newSelected.disabled:
                wasChanged = self.ChangeMonth(direction, selectDay=0)
                if wasChanged == False:
                    return 
                validDay = self.CrawlForValidDay(newSelected, direction, weekOrDay)
                newSelected = validDay
            self.selectedDay = newSelected
        self.SelectDay()



    def CrawlForValidDay(self, newSelected, direction, weekOrDay, *args):
        configname = newSelected.configname
        (row, col,) = configname.split('_')
        if direction == -1:
            row = NUM_DAYROWS
        elif direction == 1:
            row = 1
        configname = '%s_%s' % (row, col)
        newSelected = self.sr.get(configname, None)
        while newSelected.disabled:
            newSelected = self.FindAnotherDay(newSelected, direction, weekOrDay)

        return newSelected



    def CrawlForMonthday(self, monthday, *args):
        for day in self.allDayBoxes:
            if day.monthday == monthday and not day.disabled:
                return day




    def CrawlForAndSetMonthday(self, monthday, *args):
        day = self.CrawlForMonthday(monthday)
        if day:
            self.selectedDay = day
            self.SelectDay()



    def OpenDay(self, *args):
        if self.selectedDay is not None:
            self.selectedDay.OnDblClickDay()



    def FindAnotherDay(self, selectedDay, direction, weekOrDay = 'day'):
        newSelected = selectedDay
        index = self.allDayBoxes.index(selectedDay)
        if weekOrDay == 'day':
            if direction == -1:
                if index == 0:
                    newSelected = self.allDayBoxes[-1]
                else:
                    newSelected = self.allDayBoxes[(index - 1)]
            elif direction == 1:
                if len(self.allDayBoxes) > index + 1:
                    newSelected = self.allDayBoxes[(index + 1)]
                else:
                    newSelected = self.allDayBoxes[0]
        elif weekOrDay == 'week':
            configname = selectedDay.configname
            (row, col,) = configname.split('_')
            row = int(row)
            col = int(col)
            if direction == -1:
                previousRow = row - 1
                newRow = self.allDayBoxesByRows.get(previousRow, None)
                if newRow is None:
                    newRow = self.allDayBoxesByRows.get(len(self.allDayBoxesByRows), None)
                    if newRow is None:
                        newRow = self.allDayBoxesByRows.get(1)
                newSelected = newRow[col]
            elif direction == 1:
                nextRow = row + 1
                newRow = self.allDayBoxesByRows.get(nextRow, None)
                if newRow is None:
                    newRow = self.allDayBoxesByRows.get(1)
                newSelected = newRow[col]
        return newSelected




class CalendarHeaderCore(uicls.Container):
    __guid__ = 'uicls.CalendarHeaderCore'
    default_width = 256
    default_height = 256
    default_name = 'CalendarHeader'
    default_charID = None

    def _Initialize(self, *args, **kw):
        uicls.Container._Initialize(self, *args, **kw)



    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.Prepare_()



    def Prepare_(self, *args):
        self.sr.dayNameCont = uicls.Container(name='dayNameCont', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.AddDayNameText()



    def AddDayNameText(self, text = '', *args):
        if self.sr.get('dayNameText', None) is None:
            self.sr.dayNameText = uicls.Label(text=text, parent=self.sr.dayNameCont, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=1, idx=0)
        return self.sr.dayNameText



    def SetDayName(self, text = None, *args):
        self.AddDayNameText()
        if text is not None:
            self.sr.dayNameText.text = text




class CalendarEventEntryCore(uicls.Container):
    __guid__ = 'uicls.CalendarEventEntryCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.eventInfo = getattr(attributes, 'eventInfo', None)
        self.response = getattr(attributes, 'response', None)
        if self.eventInfo is not None:
            tagIcon = attributes.get('tagIcon', None)
            myResponse = attributes.get('response', None)
            time = self.eventInfo.eventTimeStamp
            title = self.eventInfo.eventTitle
            timeAndTitle = '%s %s' % (time, title)
            if settings.user.ui.Get('calendar_showTimestamp', 1):
                text = timeAndTitle
            else:
                text = title
            if getattr(self.eventInfo, 'importance', None) > 0:
                text = '<color=red>!</color> %s' % text
            hint = sm.GetService('calendar').GetEventHint(self.eventInfo, myResponse)
            responseIconPath = attributes.get('responseIconPath', None)
        else:
            text = ''
            tagIcon = None
            responseIconPath = None
        onDblClick = getattr(attributes, 'onDblClick', None)
        if onDblClick is not None:
            self.OnDblClick = onDblClick
        self.Prepare_(text, tagIcon, responseIconPath, hint)



    def Prepare_(self, text = '', tagIcon = None, responseIconPath = None, hint = '', *args):
        self.clipChildren = 1
        self.AddLabel(text)
        self.height = 14
        self.AddIconCont(responsePath=responseIconPath, tagIcon=tagIcon)
        self.AddFill()
        self.hint = hint



    def AddLabel(self, text, *args):
        self.sr.label = uicls.Label(text=text, parent=self, left=12, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=1, idx=0)



    def AddFill(self, *args):
        self.sr.fill = uicls.Frame(parent=self, name='fill', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, color=(1.0, 1.0, 1.0, 0.05))
        self.sr.hilite = uicls.Frame(parent=self, name='hilite', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, pos=(1, 1, 0, 0), color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_HIDDEN)



    def OnMouseEnter(self, *args):
        if uiutil.GetAttrs(self, 'sr', 'hilite'):
            self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if uiutil.GetAttrs(self, 'sr', 'hilite'):
            self.sr.hilite.state = uiconst.UI_HIDDEN



    def AddIconCont(self, responsePath = None, tagIcon = None, *args):
        self.sr.tagCont = uicls.Container(name='statusCont', parent=self, align=uiconst.TOPRIGHT, pos=(0, 2, 14, 14), state=uiconst.UI_DISABLED, idx=0)
        self.sr.tagCont.autoPos = uiconst.AUTOPOSYCENTER
        self.sr.responseCont = uicls.Container(name='responseCont', parent=self, align=uiconst.TOPLEFT, pos=(1, 0, 10, 14), state=uiconst.UI_DISABLED)
        if tagIcon is not None:
            self.SetTag(tagIcon)
        self.SetStatus(self.sr.responseCont, responsePath)



    def SetStatus(self, cont, iconPath = None):
        uiutil.Flush(cont)
        if iconPath:
            icon = uicls.Icon(icon=iconPath, parent=cont, align=uiconst.CENTER, pos=(0, 0, 16, 16))



    def SetTag(self, tagIcon):
        uiutil.Flush(self.sr.tagCont)
        self.sr.tagCont.children.append(tagIcon)




class CalendarDayCore(uicls.Container):
    __guid__ = 'uicls.CalendarDayCore'
    default_width = 256
    default_height = 256
    default_name = 'CalendarDay'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.year = None
        self.month = None
        self.monthday = 0
        self.events = {}
        self.eventHeight = 14
        self.disabled = 0
        self.configname = attributes.get('configname', None)
        self.Prepare_()



    def Prepare_(self, *args):
        self.sr.day = uicls.Container(name='dayNumberCont', parent=self, align=uiconst.TOALL, pos=(1, 1, 1, 1))
        self.sr.dayNumberCont = uicls.Container(name='dayNumberCont', parent=self.sr.day, align=uiconst.TOTOP, pos=(0, 0, 0, 12), state=uiconst.UI_NORMAL)
        self.sr.moreCont = uicls.Container(name='moreCont', parent=self.sr.day, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), state=uiconst.UI_HIDDEN, padding=(0, 0, 0, 0))
        self.AddMoreContFill()
        self.AddFill()
        self.AddFrame()
        self.sr.emptyDay = uicls.Container(name='emptyDay', parent=self.sr.day, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.emptyDay.state = uiconst.UI_NORMAL
        self.sr.dayNumberCont.OnDblClick = self.OnDblClickDay
        self.sr.dayNumberCont.OnMouseDown = self.OnMouseClickDay
        self.sr.dayNumberCont.GetMenu = self.GetMenu
        self.sr.emptyDay.OnDblClick = self.OnDblClickDay
        self.sr.emptyDay.OnMouseDown = self.OnMouseClickDay
        self.sr.emptyDay.GetMenu = self.GetMenu
        uiutil.SetOrder(self.sr.fill, -1)
        uiutil.SetOrder(self.sr.todayFill, -1)



    def AddMoreContFill(self, *args):
        (maincolor, backgroundcolor, component, componentsub,) = self.GetWindowColors()
        uicls.Frame(parent=self.sr.moreCont, name='moreContFill', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, color=(1.0, 1.0, 1.0, 0.5))



    def GetWindowColors(self, *args):
        return ((0.5, 0.5, 0.5, 0.5),
         (0.5, 0.5, 0.5, 0.5),
         (0.5, 0.5, 0.5, 0.5),
         (0.5, 0.5, 0.5, 0.5))



    def AddFill(self, *args):
        self.sr.fill = uicls.Frame(parent=self, name='fill', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, color=(0.5, 0.5, 0.5, 0.5), padding=(1, 1, 1, 1))



    def AddFrame(self, *args):
        self.sr.frame = uicls.Frame(parent=self, name='frame', frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(0.5, 0.5, 0.5, 0.0))
        self.sr.todayFill = uicls.Frame(parent=self, name='todayFill', frameConst=uiconst.FRAME_FILLED_CORNER0, padding=(1, 1, 1, 1), color=(0.5, 0.5, 0.5, 0.75))
        self.sr.selectedFrame = uicls.Frame(parent=self, name='frame', frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(0.5, 0.5, 0.5, 0.5), padding=(1, 1, 1, 1), state=uiconst.UI_HIDDEN)



    def AddDayNumber(self, text = '', *args):
        if self.sr.get('dayNumberText', None) is None:
            self.sr.dayNumberText = uicls.Label(parent=self.sr.dayNumberCont, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT, bold=1, uppercase=1, idx=0, fontsize=10)
        return self.sr.dayNumberText



    def SetDayNumber(self, text = None, *args):
        self.AddDayNumber()
        if text is not None:
            self.sr.dayNumberText.text = text



    def SetDayInfo(self, year, month, monthday = 0, *args):
        self.year = year
        self.month = month
        self.monthday = monthday



    def SetDay(self, year, month, monthday = 0, notInMonth = 0, today = False):
        self.SetDayNumber(text=monthday)
        self.ChangeDayVisibility(disabled=notInMonth)
        self.ClearDay()
        self.SetDayInfo(year, month, monthday=monthday)
        self.SetTodayMarker(today=today)



    def ChangeDayVisibility(self, disabled = 1, *args):
        self.disabled = disabled
        self.SetFillState(visible=not disabled)
        self.SetFrameState(visible=disabled)
        self.SetDayVisibility(visible=not disabled)



    def SetFrameState(self, visible = 1):
        self.sr.frame.SetAlpha([0.0, 0.4][bool(visible)])



    def SetFillState(self, visible = 1):
        self.sr.fill.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][bool(visible)]



    def SetDayVisibility(self, visible = 1):
        self.sr.day.opacity = [0.4, 1.0][bool(visible)]



    def SetTodayMarker(self, today = False, *args):
        self.sr.todayFill.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][(today == True)]



    def GetMenu(self, *args):
        return self.GetMenuFunction(*args)



    def GetMenuFunction(self, *args):
        m = []
        if self.disabled:
            return m
        if not sm.GetService('calendar').IsInPast(self.year, self.month, self.monthday, allowToday=1):
            m += [(mls.UI_CAL_CREATEEVENT, self.OpenNewEventWnd)]
        if not self.disabled:
            m += [(mls.UI_CAL_VIEWDAY, self.OpenSingleDayWnd)]
        return m



    def SetSelectedFrameState(self, on = 0):
        self.sr.selectedFrame.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][on]



    def OnMouseClickDay(self, *args):
        self.DoClickDay(self)



    def DoClickDay(self, object):
        self.SetSelectedFrameState(on=1)



    def OnDblClickDay(self, *args):
        self.DoDblClickDay(self)



    def DoDblClickDay(self, day, *args):
        self.OpenSingleDayWnd()



    def OpenNewEventWnd(self, *args):
        sm.GetService('calendar').OpenNewEventWnd(self.year, self.month, self.monthday)



    def OpenSingleDayWnd(self, *args):
        sm.GetService('calendar').OpenSingleDayWnd('day', self.year, self.month, self.monthday, self.events)



    def ClearDay(self, *args):
        self.events = {}
        self.CheckEventsClipped()
        self.sr.emptyDay.Flush()



    def LoadEvents(self, eventsThisDay, *args):
        self.sr.emptyDay.Flush()
        self.events = {}
        toSort = [ ((eventKV.eventTimeStamp, eventKV.eventTitle), eventKV) for eventKV in eventsThisDay.values() ]
        eventsKVs = uiutil.SortListOfTuples(toSort)
        for eventInfo in eventsKVs:
            onDblClick = (self.OpenEvent, eventInfo)
            (iconPath, response,) = sm.GetService('calendar').GetMyResponseIconFromID(eventInfo.eventID, long=1)
            if response == const.eventResponseDeleted or response == const.eventResponseDeclined and not settings.user.ui.Get('calendar_showDeclined', 1):
                continue
            tagIcon = self.GetTagIcon(eventInfo.flag)
            entry = uicls.CalendarEventEntry(name='calendarEventEntry', parent=self.sr.emptyDay, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             self.eventHeight), padding=(1, 1, 1, 0), state=uiconst.UI_NORMAL, eventInfo=eventInfo, onDblClick=onDblClick, responseIconPath=iconPath, tagIcon=tagIcon, response=response)
            entry.MenuFunction = self.GetEventMenu
            self.events[eventInfo.eventID] = eventInfo

        self.CheckEventsClipped()



    def GetTagIcon(self, tag):
        tagIcon = sm.GetService('calendar').LoadTagIcon(tag)
        return tagIcon



    def GetEventMenu(self, entry, *args):
        eventInfo = entry.eventInfo
        m = sm.GetService('calendar').GetEventMenu(eventInfo, entry.response, getJumpOption=False)
        return m



    def OpenEvent(self, eventInfo, *args):
        sm.GetService('calendar').OpenEventWnd(eventInfo)



    def CheckEventsClipped(self, *args):
        numEvents = len(self.events)
        if numEvents < 1:
            self.sr.moreCont.state = uiconst.UI_HIDDEN
            return 
        totalEntryHeight = numEvents * (self.eventHeight + 1)
        (l, t, w, h,) = self.sr.emptyDay.GetAbsolute()
        moreHeight = 0
        if self.sr.moreCont.state != uiconst.UI_HIDDEN:
            moreHeight = self.sr.moreCont.height
        if totalEntryHeight > h + moreHeight:
            self.sr.moreCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.moreCont.state = uiconst.UI_HIDDEN




class EventListCore(uicls.Container):
    __guid__ = 'uicls.EventListCore'
    __notifyevents__ = ['OnReloadToDo', 'OnCalendarFilterChange']

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.maxEntries = 25
        self.events = {}
        self.listentryClass = attributes.get('listentryClass')
        self.getEventsFunc = attributes.get('getEventsFunc', sm.GetService('calendar').GetMyNextEvents)
        self.getEventsArgs = attributes.get('getEventsArgs', ())
        self.header = attributes.get('header', '')
        self.Setup()



    def Setup(self):
        sm.RegisterNotify(self)
        self.sr.moreCont = uicls.Container(name='moreCont', parent=self, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), state=uiconst.UI_NORMAL, padding=(0, 0, 0, 0))
        self.AddMoreContFill()
        self.SetupScroll()
        self.LoadNextEvents()



    def LoadNextEvents(self, *args):
        nextEvents = self.GetEvents()
        scrolllist = []
        self.events = {}
        for (eventID, eventKV,) in nextEvents.iteritems():
            eventEntryTuple = self.GetEventEntryTuple(eventKV)
            if eventEntryTuple is None:
                continue
            self.events[eventID] = eventKV
            scrolllist.append(eventEntryTuple)

        scrolllist = uiutil.SortListOfTuples(scrolllist, reverse=self.GetSortOrder())
        self.LoadScroll(scrolllist)
        self.OnResize()



    def SetupScroll(self, *args):
        pass



    def GetEvents(self, *args):
        return apply(self.getEventsFunc, self.getEventsArgs)



    def GetEventEntryTuple(self, eventKV, *args):
        entry = self.GetEventEntry(eventKV)
        if entry is None:
            return 
        return (eventKV.eventDateTime, entry)



    def GetSortOrder(self, *args):
        return 0



    def GetEventEntry(self, *args):
        return None



    def LoadScroll(self, scrolllist, *args):
        pass



    def AddMoreContFill(self, *args):
        pass



    def OnResize(self, *args):
        uthread.new(self.UpdateMoreIndicators)



    def UpdateMoreIndicators(self, *args):
        if self.sr.eventScroll.scrollingRange >= self.sr.moreCont.height:
            self.sr.moreCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.moreCont.state = uiconst.UI_HIDDEN



    def OnReloadToDo(self, *args):
        self.LoadNextEvents()



    def OnCalendarFilterChange(self, *args):
        self.OnReloadToDo()



    def OnMoreClick(self, *args):
        pass




