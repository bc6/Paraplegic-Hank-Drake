#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/localization/numericPropertyHandler.py
import eveLocalization
import localization
import util

class NumericPropertyHandler(localization.BasePropertyHandler):
    __guid__ = 'localization.NumericPropertyHandler'
    PROPERTIES = {localization.CODE_UNIVERSAL: ['quantity',
                                   'isk',
                                   'aur',
                                   'distance']}

    def _GetQuantity(self, value, languageID, *args, **kwargs):
        return value

    def _GetIsk(self, value, languageID, *args, **kwargs):
        return util.FmtISK(value)

    def _GetAur(self, value, languageID, *args, **kwargs):
        return util.FmtAUR(value)

    def _GetDistance(self, value, languageID, *args, **kwargs):
        return util.FmtDist(value, maxdemicals=kwargs.get('decimalPlaces', 3))


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.NUMERIC, NumericPropertyHandler())