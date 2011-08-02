from contractscommon import *
import util
import blue
import uix
COL_PAY = '0xffcc2222'
COL_GET = '0xff00bb00'

def FmtISKWithDescription(isk, justDesc = False):
    iskFmt = util.FmtISK(isk, showFractionsAlways=0)
    isk = float(isk)
    if abs(isk) >= 1000000000:
        isk = long(isk / 10000000L)
        if justDesc:
            iskFmt = '%.2f %s %s' % (isk / 100.0, mls.UI_GENERIC_BILLION, mls.UI_GENERIC_ISK)
        else:
            iskFmt += ' (%.2f %s)' % (isk / 100.0, mls.UI_GENERIC_BILLION)
    elif abs(isk) >= 1000000:
        isk = long(isk / 10000L)
        if justDesc:
            iskFmt = '%.2f %s %s' % (isk / 100.0, mls.UI_GENERIC_MILLION, mls.UI_GENERIC_ISK)
        else:
            iskFmt += ' (%.2f %s)' % (isk / 100.0, mls.UI_GENERIC_MILLION)
    elif abs(isk) >= 10000:
        isk = long(isk / 10L)
        if justDesc:
            iskFmt = '%.2f %s %s' % (isk / 100.0, mls.THOUSAND, mls.UI_GENERIC_ISK)
        else:
            iskFmt += ' (%.2f %s)' % (isk / 100.0, mls.THOUSAND)
    return iskFmt



def GetMarketTypes():
    data = []
    for t in cfg.invtypes:
        if t.published:
            g = cfg.invgroups.Get(t.groupID)
            if g.published:
                c = cfg.invcategories.Get(g.categoryID)
                if c.published:
                    data.append(t.line)

    ret = util.Rowset(cfg.invtypes.header, data)
    return ret



def GetContractIcon(type):
    icons = {const.conTypeNothing: '64_10',
     const.conTypeItemExchange: '64_9',
     const.conTypeAuction: '64_16',
     const.conTypeCourier: '64_13',
     const.conTypeLoan: '64_15'}
    return icons.get(type, '64_10')



def GetColoredContractStatusText(status):
    cols = {0: 'ffffff',
     1: 'ffffff',
     2: 'ffffff',
     3: 'ffffff',
     4: 'ffffff',
     5: 'ffffff',
     6: 'ffffff',
     7: 'aa0000',
     8: 'ffffff'}
    col = cols[status]
    st = GetContractStatusText(status)
    return '<color=0xff%s>%s</color>' % (col, st)



def ConFmtDate(time, isText = False):
    if time < 0:
        return '<color=red>%s</color>' % mls.UI_CONTRACTS_EXPIRED
    res = ''
    d = time / DAY
    h = (time - d * DAY) / HOUR
    if isText:
        if d >= 1:
            res = '%s %s' % (d, [mls.UI_GENERIC_DAYLOWER, mls.UI_GENERIC_DAYSLOWER][(d > 1)])
        elif d < 0:
            res = mls.UI_CONTRACTS_EXPIRED
        elif h >= 1:
            res = mls.UI_CONTRACTS_LESSTHANADAY
        else:
            res = mls.UI_CONTRACTS_LESSTHANANHOUR
    elif d == 1:
        res += '%s %s ' % (d, mls.UI_GENERIC_DAYLOWER)
    elif d > 1:
        res += '%s %s ' % (d, mls.UI_GENERIC_DAYSLOWER)
    if h == 1 and d >= 0:
        res += '%s %s' % (h, mls.UI_GENERIC_HOURLOWER)
    elif h > 1 and d >= 0:
        res += '%s %s' % (h, mls.UI_GENERIC_HOURSLOWER)
    if time / HOUR == 0:
        res = mls.UI_CONTRACTS_LESSTHANANHOUR
    return res



def GetContractTimeLeftText(c):
    if c.status == const.conStatusOutstanding:
        if c.dateExpired < blue.os.GetTime():
            return mls.UI_CONTRACTS_EXPIRED
        else:
            return ConFmtDate(c.dateExpired - blue.os.GetTime(), c.type == const.conTypeAuction)
    elif c.status == const.conStatusInProgress:
        de = c.dateAccepted + c.numDays * DAY
        diff = de - blue.os.GetTime()
        if diff > 0:
            timeleft = '%s' % ConFmtDate(diff, False)
        else:
            timeleft = '<color:0xffff0000><b>%s</b> (%s)</color>' % (mls.UI_CONTRACTS_OVERDUE, ConFmtDate(-diff, False), mls.UI_GENERIC_AGO)
    else:
        return ''



def CutAt(txt, l):
    if len(txt) > l:
        return txt[:(l - 3)] + '...'
    else:
        return txt



def SelectItemTypeDlg(itemTypes):
    tmplst = []
    for typeID in itemTypes:
        t = cfg.invtypes.Get(typeID)
        c = cfg.invcategories.Get(t.categoryID)
        tmplst.append(('%s (%s)' % (TypeName(typeID), c.categoryName), typeID))

    if not tmplst:
        eve.Message('ConNoItemsFound')
        return 
    else:
        if len(tmplst) == 1:
            return tmplst[0][1]
        ret = uix.ListWnd(tmplst, 'generic', mls.UI_CONTRACTS_SELECTITEMTYPE, None, 1, windowName='contractSelectItemTypeDlg')
        return ret and ret[1]



def MatchInvTypeName(s, invType):
    cfgType = cfg.invtypes.Get(invType.typeID)
    localized = cfgType.typeName
    english = cfgType._typeName
    return CaseInsensitiveSubMatch(s, localized) or CaseInsensitiveSubMatch(s, english)



def CaseInsensitiveSubMatch(matchStr, inStr):
    return matchStr.lower() in inStr.lower()



def TypeName(typeID):
    return cfg.invtypes.Get(typeID).typeName



def GroupName(groupID):
    return cfg.invgroups.Get(groupID).groupName



def CategoryName(categoryID):
    return cfg.invcategories.Get(categoryID).categoryName



def IsSearchStringLongEnough(txt):
    error = None
    if IsIdeographic(eve.session.languageID) and not txt:
        error = 'ConNeedAtLeastOneLetter'
    if not IsIdeographic(eve.session.languageID) and (not txt or len(txt) < 3):
        error = 'ConNeedAtLeastThreeLetters'
    if error:
        eve.Message(error)
    return not error



def IsIdeographic(languageID):
    return languageID == 'ZH'



def DoParseItemType(wnd, prevVal = None, marketOnly = False):
    itemTypes = []
    txt = wnd.GetValue()
    if len(txt) == 0 or not IsSearchStringLongEnough(txt):
        return 
    if txt == prevVal:
        return 
    for t in GetMarketTypes():
        if t.marketGroupID is None and marketOnly:
            continue
        if MatchInvTypeName(txt, t):
            itemTypes.append(t.typeID)

    typeID = SelectItemTypeDlg(itemTypes)
    if typeID:
        wnd.SetValue(TypeName(typeID))
    return typeID


exports = util.AutoExports('contractutils', locals())

