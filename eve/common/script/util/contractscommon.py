import util
import blue
CONTYPE_AUCTIONANDITEMECHANGE = 10
CREATECONTRACT_CONFIRM_CHARGESTOHANGAR = 1
const_conSalesTax = 0.01
const_conSalesTaxMinimum = 10000
const_conSalesTaxMaximum = 100000000
const_conBrokersFee = 0.004
const_conBrokersFeeMinimum = 10000
const_conBrokersFeeMaximum = 10000000
const_conDeposit = 0.01
const_conDepositMinimum = 100000
const_conDepositMaximum = 10000000
const_conBidMinimum = 1000000
MAX_AMOUNT = 1000000000000L
SECOND = 10000000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
NUM_CONTRACTS_BY_SKILL = [1,
 5,
 9,
 13,
 17,
 21]
NUM_CONTRACTS_BY_SKILL_CORP = [10,
 20,
 30,
 40,
 50,
 60]
MAX_NUM_ITEMS = 200
MAX_NUM_ITEMS_TOTAL = 2000
MAX_NUM_CONTRACTS = 500
const_conCourierMaxVolume = 981250
const_conCourierWarningVolume = 20000
MAX_DESC_LENGTH = 4000
MAX_TITLE_LENGTH = 50
MAX_NOTES_LENGTH = 1000
EXPIRE_TIMES = [1440,
 4320,
 10080,
 20160]
MAX_NUM_CONTRACTS = 500
SORT_ID = 0
SORT_PRICE = 1
SORT_EXPIRED = 2
SORT_STATION_ID = 3
SORT_SOLARSYSTEM_ID = 4
SORT_REGION_ID = 5
SORT_CONSTELLATION_ID = 6
SORT_CONTRACT_TYPE = 7
SORT_REWARD = 8
SORT_COLLATERAL = 9
SORT_VOLUME = 10
SORT_ASSIGNEEID = 11
CONTRACTS_PER_PAGE = 100
MAX_CONTRACTS_PER_SEARCH = 1000
NUMJUMPS_UNREACHABLE = 100
SEARCHHINT_BPO = 1
SEARCHHINT_BPC = 2

def CalcContractFees(price, reward, type, time, skillLevels):
    BASE_COST_MULTIPLIERS = {const.conTypeAuction: 1.0,
     const.conTypeItemExchange: 1.0,
     const.conTypeCourier: 0.1,
     const.conTypeLoan: 1.0}
    base = max(price, reward)
    numAdditionalDays = int(float(time) / 1440.0) - 1
    costMult = BASE_COST_MULTIPLIERS[type]
    ret = util.KeyVal()
    tax = const_conSalesTax - float(skillLevels.accounting) * 0.001
    taxMinimum = const_conSalesTaxMinimum
    tax *= costMult
    ret.salesTax = tax
    maxSalesTax = const_conSalesTaxMaximum * (1.0 - float(skillLevels.accounting) * 0.1)
    ret.salesTaxAmt = int(min(max(base * tax, taxMinimum), maxSalesTax))
    brokersFee = const_conBrokersFee - float(skillLevels.brokerRelations) * 0.0002
    brokersFeeMininum = const_conBrokersFeeMinimum
    brokersFee *= costMult
    ret.brokersFee = brokersFee
    ret.brokersFee += numAdditionalDays * 0.0005
    maxBrokersFee = const_conBrokersFeeMaximum * (1.0 - float(skillLevels.brokerRelations) * 0.05)
    ret.brokersFeeAmt = int(min(max(base * brokersFee, brokersFeeMininum), maxBrokersFee))
    ret.brokersFeeAmt *= 1.0 + numAdditionalDays * 0.05
    deposit = const_conDeposit
    depositMininum = const_conDepositMinimum
    if type == const.conTypeCourier:
        depositMininum /= 10
    deposit *= costMult
    ret.deposit = deposit
    maxDeposit = const_conDepositMaximum
    ret.depositAmt = int(min(max(base * deposit, depositMininum), maxDeposit))
    return ret



def GetContractTypeText(id):
    typesTxt = {const.conTypeItemExchange: mls.UI_CONTRACTS_ITEMEXCHANGE,
     const.conTypeAuction: mls.UI_CONTRACTS_AUCTION,
     const.conTypeCourier: mls.UI_CONTRACTS_COURIER,
     const.conTypeLoan: mls.UI_CONTRACTS_LOAN}
    return typesTxt.get(id, mls.UI_GENERIC_UNKNOWN)



def GetContractStatusText(id, typ = None):
    statusTxt = {const.conStatusOutstanding: mls.UI_CONTRACTS_OUTSTANDING,
     const.conStatusInProgress: mls.UI_CONTRACTS_INPROGRESS,
     const.conStatusFinishedIssuer: mls.UI_CONTRACTS_FINISHEDISSUER,
     const.conStatusFinishedContractor: mls.UI_CONTRACTS_FINISHEDCONTRACTOR,
     const.conStatusFinished: mls.UI_CONTRACTS_FINISHED,
     const.conStatusRejected: mls.UI_CONTRACTS_REJECTED,
     const.conStatusFailed: mls.UI_CONTRACTS_FAILED,
     const.conStatusDeleted: mls.UI_CONTRACTS_DELETED,
     const.conStatusReversed: mls.UI_CONTRACTS_REVERSED}
    return statusTxt.get(id, '?')



def GetContractTitle(r, items):
    MAX_COL_LENGTH = 60
    MAX_TITLE_LEN = 100
    txt = ''
    title = ''
    if (r.type == const.conTypeItemExchange or r.type == const.conTypeAuction) and len(items) > 0:
        l = len([ e for e in items if e.inCrate ])
        lgive = len(items) - l
        if r.type == const.conTypeItemExchange and lgive > 0 and l > 0:
            txt = mls.UI_CONTRACTS_WANTTOTRADE
        elif l > 1:
            txt = mls.UI_CONTRACTS_MULTIPLEITEMS
        elif l == 1:
            txt = '%s' % cfg.invtypes.Get(items[0].itemTypeID).typeName
            if items[0].quantity > 1:
                txt += ' x %s' % items[0].quantity
        elif r.type == const.conTypeItemExchange:
            if r.reward == 0:
                txt = mls.UI_CONTRACTS_WANTAGIFT
            else:
                txt = mls.UI_CONTRACTS_WANTTOBUY
    elif r.type == const.conTypeCourier:
        title = '%s &gt;&gt; %s (%s m\xb3)' % (cfg.evelocations.Get(r.startSolarSystemID).name, cfg.evelocations.Get(r.endSolarSystemID).name, util.FmtAmt(r.volume, showFraction=0))
        txt = title
    else:
        txt = r.title
    if len(txt) > MAX_COL_LENGTH:
        txt = txt[:MAX_COL_LENGTH] + '...'
    if txt == '':
        txt = mls.UI_GENERIC_UNKNOWN
    return txt



def GetCurrentBid(contract, bids):
    currentBid = contract.price
    if len(bids) > 0:
        currentBid = bids[0].amount
    return currentBid



def GetCorpRoleAtLocation(session, locationID):
    hqID = session.hqID
    baseID = session.baseID
    rolesAtAll = session.rolesAtAll
    rolesAtHQ = session.rolesAtHQ
    rolesAtBase = session.rolesAtBase
    rolesAtOther = session.rolesAtOther
    corprole = 0L
    if locationID == hqID:
        corprole = rolesAtAll | rolesAtHQ
    elif locationID == baseID:
        corprole = rolesAtAll | rolesAtBase
    else:
        corprole = rolesAtAll | rolesAtOther
    return corprole


exports = util.AutoExports('contractscommon', locals())

