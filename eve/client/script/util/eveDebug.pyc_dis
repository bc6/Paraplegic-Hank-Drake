#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/util/eveDebug.py
import util

def GetCharacterName(o = None):
    if o is not None:
        return cfg.eveowners.Get(o.charID).name
    elif eve.session.charid:
        return cfg.eveowners.Get(eve.session.charid).name
    else:
        return 'no name'


exports = util.AutoExports('dbg', locals())