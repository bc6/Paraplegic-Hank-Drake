import util

def GetCharacterName(o = None):
    if o is not None:
        return cfg.eveowners.Get(o.charID).name
    else:
        if eve.session.charid:
            return cfg.eveowners.Get(eve.session.charid).name
        return 'no name'


exports = util.AutoExports('dbg', locals())

