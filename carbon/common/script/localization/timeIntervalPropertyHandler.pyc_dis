#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/localization/timeIntervalPropertyHandler.py
import eveLocalization
import localization
import localizationUtil

class TimeIntervalPropertyHandler(localization.BasePropertyHandler):
    __guid__ = 'localization.TimeIntervalPropertyHandler'
    PROPERTIES = {localization.CODE_UNIVERSAL: ('shortForm', 'shortWrittenForm', 'writtenForm')}

    def _GetShortForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        try:
            timeIntervalString = localizationUtil.FormatTimeIntervalShort(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            localization.LogError(e)

    def _GetShortWrittenForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        try:
            timeIntervalString = localizationUtil.FormatTimeIntervalShortWritten(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            localization.LogError(e)

    def _GetWrittenForm(self, value, languageID, *args, **kwargs):
        kwargs = self._GetToFromArgs(kwargs)
        kwargs['languageID'] = languageID
        try:
            timeIntervalString = localizationUtil.FormatTimeIntervalWritten(value, **kwargs)
            return timeIntervalString
        except ValueError as e:
            localization.LogError(e)

    def _GetDefault(self, value, languageID, *args, **kwargs):
        return self._GetShortForm(value, languageID, *args, **kwargs)

    def _GetToFromArgs(self, kwargs):
        fromMark = kwargs.get('from', None)
        toMark = kwargs.get('to', None)
        kwargs = {}
        if fromMark:
            kwargs['showFrom'] = fromMark
        if toMark:
            kwargs['showTo'] = toMark
        return kwargs


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.TIMEINTERVAL, TimeIntervalPropertyHandler())