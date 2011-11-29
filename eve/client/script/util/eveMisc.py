import blue
import sys
import util
import uthread
import log
import uix
import uiconst

def LaunchFromShip(items, whoseBehalfID = None, ignoreWarning = False):
    oldItems = []
    for item in items:
        if getattr(item, 'quantity', 0) < 0:
            oldItems.append((item.itemID, 1))

    for item in items:
        if item.itemID not in items:
            if getattr(item, 'quantity', 0) > 0:
                oldItems.append((item.itemID, getattr(item, 'quantity', 1)))

    try:
        ret = sm.StartService('gameui').GetShipAccess().Drop(oldItems, whoseBehalfID, ignoreWarning)
    except UserError as e:
        if e.msg in ('LaunchCPWarning', 'LaunchUpgradePlatformWarning'):
            reply = eve.Message(e.msg, e.dict, uiconst.YESNO)
            if reply == uiconst.ID_YES:
                LaunchFromShip(items, whoseBehalfID, ignoreWarning=True)
            sys.exc_clear()
            return 
        raise e

    def PackError(err):
        errID = err[0]
        if len(err) == 1:
            errDetails = {}
        elif len(err) == 2:
            errDetails = each[1]
        else:
            errDetails = {}
            log.LogTraceback('Bad error length: %r' % err)
        errDetailsType = type(errDetails)
        if errDetailsType is dict:
            errDetails = tuple(errDetails.iteritems())
        return (errID, errDetailsType, errDetails)



    def UnpackError(err):
        (errID, errDetailsType, errDetails,) = err
        return (errID, errDetailsType(errDetails))


    newIDs = {}
    errors = set()
    for (itemID, seq,) in ret.iteritems():
        newIDs[itemID] = []
        for each in seq:
            if type(each) is tuple:
                errors.add(PackError(each))
            else:
                newIDs[itemID].append(each)


    sm.ScatterEvent('OnItemLaunch', newIDs)

    def raise_(e):
        raise e


    for error in errors:
        uthread.new(raise_, UserError(*UnpackError(error)))




def IsItemOfRepairableType(item):
    return item.singleton and (item.categoryID in (const.categoryDeployable,
     const.categoryShip,
     const.categoryDrone,
     const.categoryStructure,
     const.categoryModule) or item.groupID in (const.groupCargoContainer,
     const.groupSecureCargoContainer,
     const.groupAuditLogSecureContainer,
     const.groupFreightContainer,
     const.groupTool))



def CSPAChargedAction(message, obj, function, *args):
    try:
        return apply(getattr(obj, function), args)
    except UserError as e:
        if e.msg == 'ContactCostNotApproved':
            info = e.args[1]
            if eve.Message(message, {'amount': info['totalCost'],
             'amountISK': info['totalCostISK']}, uiconst.YESNO) != uiconst.ID_YES:
                return None
            kwArgs = {'approvedCost': info['totalCost']}
            return apply(getattr(obj, function), args, kwArgs)
        raise 


exports = util.AutoExports('util', globals())

