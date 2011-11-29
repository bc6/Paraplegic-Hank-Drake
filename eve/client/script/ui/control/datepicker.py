import blue
import uicls
import uiconst
import calendar
import time
import localization
import localizationUtil

class DatePicker(uicls.Container):
    __guid__ = 'xtriui.DatePicker'
    __nonpersistvars__ = []

    def init(self):
        self.months = [localization.GetByLabel('UI/Common/Months/January'),
         localization.GetByLabel('UI/Common/Months/February'),
         localization.GetByLabel('UI/Common/Months/March'),
         localization.GetByLabel('UI/Common/Months/April'),
         localization.GetByLabel('UI/Common/Months/May'),
         localization.GetByLabel('UI/Common/Months/June'),
         localization.GetByLabel('UI/Common/Months/July'),
         localization.GetByLabel('UI/Common/Months/August'),
         localization.GetByLabel('UI/Common/Months/September'),
         localization.GetByLabel('UI/Common/Months/October'),
         localization.GetByLabel('UI/Common/Months/November'),
         localization.GetByLabel('UI/Common/Months/December')]



    def Startup(self, now, withTime = False, timeparts = 4, startYear = None, yearRange = None):
        self.timeparts = timeparts
        if now is None:
            now = time.gmtime()
        if startYear is None:
            startYear = const.calendarStartYear
        year = max(startYear, now[0])
        month = now[1]
        day = now[2]
        left = 0
        if yearRange is None:
            yRange = year - startYear + 1
        else:
            yRange = yearRange
        yearops = [ (localizationUtil.FormatNumeric(startYear + i, decimalPlaces=0), startYear + i) for i in xrange(yRange) ]
        self.ycombo = uicls.Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Year'), options=yearops, name='year', select=year, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), width=48, align=uiconst.TOPLEFT)
        left += self.ycombo.width + 4
        monthops = [ (self.months[i], i + 1) for i in xrange(12) ]
        self.mcombo = uicls.Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Month'), options=monthops, name='month', select=month, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), width=64, align=uiconst.TOPLEFT)
        left += self.mcombo.width + 4
        (firstday, numdays,) = calendar.monthrange(year, month)
        dayops = [ (localizationUtil.FormatNumeric(i + 1, decimalPlaces=0), i + 1) for i in xrange(numdays) ]
        self.dcombo = uicls.Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Day'), options=dayops, name='day', select=day, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), width=48, align=uiconst.TOPLEFT)
        self.width = self.dcombo.left + self.dcombo.width
        self.height = self.ycombo.height
        if withTime:
            index = self.GetTimeIndex(now)
            hourops = self.GetTimeOptions()
            left += self.dcombo.width + 4
            self.hcombo = uicls.Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Time'), options=hourops, name='time', select=index, callback=self.OnComboChange, pos=(left,
             0,
             0,
             0), width=48, align=uiconst.TOPLEFT)
            self.width = self.hcombo.left + self.hcombo.width
            self.height = self.hcombo.height



    def OnComboChange(self, combo, header, value, *args):
        self.CheckDays()
        if hasattr(self, 'OnDateChange'):
            self.OnDateChange()



    def CheckDays(self):
        sely = self.ycombo.GetValue()
        selm = self.mcombo.GetValue()
        seld = self.dcombo.GetValue()
        (firstday, numdays,) = calendar.monthrange(sely, selm)
        dayops = [ (str(i + 1), i + 1) for i in xrange(numdays) ]
        self.dcombo.LoadOptions(dayops, min(seld, numdays))



    def GetValue(self):
        y = self.ycombo.GetValue()
        m = self.mcombo.GetValue()
        d = self.dcombo.GetValue()
        h = 0
        min = 0
        if getattr(self, 'hcombo', None) is not None:
            time = self.hcombo.GetValue()
            h = time / self.timeparts
            interval = 60 / self.timeparts
            min = time % self.timeparts * interval
        return blue.os.GetTimeFromParts(y, m, d, h, min, 0, 0)



    def GetFancyValue(self):
        y = self.ycombo.GetValue()
        m = self.mcombo.GetValue()
        d = self.dcombo.GetValue()
        tme = (y,
         m,
         d,
         0,
         0,
         0,
         0,
         0,
         0)
        return strftime('%d %B %Y', tme)



    def GetTimeOptions(self, *args):
        hours = []
        counter = 0
        for h in xrange(0, 24):
            interval = 60 / self.timeparts
            for m in xrange(0, self.timeparts):
                min = m * interval
                ts = time.struct_time((0,
                 1,
                 1,
                 h,
                 min,
                 0,
                 0,
                 1,
                 0))
                timeStr = localizationUtil.FormatDateTime(value=ts, dateFormat='none', timeFormat='short')
                hours.append((timeStr, counter))
                counter += 1


        return hours



    def GetTimeIndex(self, now, *args):
        if len(now) > 3:
            hour = now[3]
        else:
            hour = 12
        if len(now) > 4:
            min = now[4]
        else:
            min = 0
        interval = 60 / self.timeparts
        index = hour * self.timeparts + min / interval
        return index




