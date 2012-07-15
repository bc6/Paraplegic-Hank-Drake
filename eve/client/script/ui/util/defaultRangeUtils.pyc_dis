#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/util/defaultRangeUtils.py
import util
_RANGE_BY_TYPE_SETTING_FORMAT = 'defaultType%sDist'
_WARPTO_SETTING = 'WarpTo'
_GENERIC_TYPE_ID = 0
DEFAULT_RANGES = {_WARPTO_SETTING: const.minWarpEndDistance,
 'Orbit': 1000,
 'KeepAtRange': 1000}

def _GetCurrentShipTypeID():
    if session.shipid and session.solarsystemid:
        shipItem = sm.GetService('godma').GetItem(session.shipid)
        if shipItem:
            return shipItem.typeID


def UpdateRangeSetting(key, newRange):
    typeRangeSettings = settings.char.ui.Get(_RANGE_BY_TYPE_SETTING_FORMAT % key, {})
    if key != _WARPTO_SETTING:
        typeID = _GetCurrentShipTypeID()
        if typeID is not None:
            typeRangeSettings[typeID] = newRange
    typeRangeSettings[_GENERIC_TYPE_ID] = newRange
    settings.char.ui.Set(_RANGE_BY_TYPE_SETTING_FORMAT % key, typeRangeSettings)
    sm.ScatterEvent('OnDistSettingsChange')


def FetchRangeSetting(key):
    if key not in util.DEFAULT_RANGES:
        return
    typeRangeSettings = settings.char.ui.Get(_RANGE_BY_TYPE_SETTING_FORMAT % key, {})
    if key != _WARPTO_SETTING:
        typeID = _GetCurrentShipTypeID()
        if typeID is not None and typeID in typeRangeSettings:
            return typeRangeSettings[typeID]
    if _GENERIC_TYPE_ID in typeRangeSettings:
        return typeRangeSettings[_GENERIC_TYPE_ID]
    return DEFAULT_RANGES[key]


exports = util.AutoExports('util', globals())