import blue
import string
import math
import sys
import re
import const
from util import DECIMAL, FmtAmt
import log
PROBE_STATE_TEXT_MAP = {const.probeStateInactive: 'UI_GENERIC_INACTIVE',
 const.probeStateIdle: 'UI_SHARED_PROBE_STATE_IDLE',
 const.probeStateMoving: 'UI_SHARED_PROBE_STATE_MOVING',
 const.probeStateWarping: 'UI_SHARED_PROBE_STATE_WARPING',
 const.probeStateScanning: 'UI_SHARED_PROBE_STATE_SCANNING',
 const.probeStateReturning: 'UI_SHARED_PROBE_STATE_RETURNING'}
PROBE_STATE_COLOR_MAP = {const.probeStateInactive: '<color=gray>%s</color>',
 const.probeStateIdle: '<color=0xFF22FF22>%s</color>',
 const.probeStateMoving: '<color=yellow>%s</color>',
 const.probeStateWarping: '<color=yellow>%s</color>',
 const.probeStateScanning: '<color=0xFF66BBFF>%s</color>',
 const.probeStateReturning: '<color=yellow>%s</color>'}

def FmtISK(isk, showFractionsAlways = 1):
    return FmtCurrency(isk, showFractionsAlways, const.creditsISK)



def FmtAUR(aur, showFractionsAlways = 0):
    return FmtCurrency(aur, showFractionsAlways, const.creditsAURUM)



def FmtCurrency(amount, showFractionsAlways = 1, currency = None):
    if currency == const.creditsAURUM:
        currencyString = ' %s' % mls.UI_GENERIC_AUR
    elif currency == const.creditsISK:
        currencyString = ' %s' % mls.UI_GENERIC_ISK
    else:
        currencyString = ''
    minus = ['-', ''][(amount >= 0)]
    fractions = 0.0
    try:
        fractions = abs(math.fmod(amount, 1.0))
        if amount is None:
            amount = 0
        amount = long(amount)
    except:
        log.LogTraceback()
        raise RuntimeError(mls.UI_SHARED_FORMAT_VALUEMUSTBE)
    ret = ''
    digit = ''
    amt = str(abs(amount))
    for i in xrange(len(amt) % 3, len(amt) + 3, 3):
        if i < 3:
            ret += amt[:i]
        else:
            ret += digit + amt[(i - 3):i]
        if i != 0:
            digit = [',', '.'][(DECIMAL == ',')]

    if fractions != 0.0 and currency != const.creditsAURUM or showFractionsAlways:
        if round(fractions * 100) / 100 == 1:
            return FmtAmt(float('%s%s' % (minus, ret.replace(digit, ''))) + 1, showFraction=showFractionsAlways * 2) + currencyString
        rest = str(100 * round(fractions, 2))[:2]
        if rest[1] == '.':
            rest = '0' + rest[0]
        ret = '%s%s%s' % (ret, DECIMAL, rest)
    return minus + ret + currencyString



def FmtRef(entryTypeID, o1, o2, arg1, pretty = 1, amount = 0.0, constants = None):
    constants = constants or const
    if entryTypeID == constants.refBackwardCompatible:
        if pretty:
            return ''
        else:
            return mls.UI_SHARED_FORMAT_BACKWARDCOMPATIBILITY % {'type': entryTypeID,
             'o1': o1,
             'o2': o2,
             'arg': arg1}
    if entryTypeID == constants.refUndefined:
        if pretty:
            return ''
        else:
            return mls.UI_SHARED_FORMAT_UNDEFINEDREFTYPE % {'type': entryTypeID,
             'o1': o1,
             'o2': o2,
             'arg': arg1}
    elif entryTypeID == constants.refPlayerTrading:
        return mls.UI_SHARED_FORMAT_DIRECTTRADEBETWEEN % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refMarketTransaction:
        return mls.UI_SHARED_FORMAT_MARKETBOUGHTSTUFF % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refMarketFinePaid:
        return mls.UI_SHARED_FORMAT_MARKETPAIDFINE
    if entryTypeID == constants.refGMCashTransfer:
        return mls.UI_SHARED_FORMAT_GMISSUEDTRANSACTION % {'arg': arg1,
         'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refATMWithdraw:
        return mls.UI_SHARED_FORMAT_ATMCASHWITHDRAWALBY % {'name': GetName(o1),
         'location': cfg.evelocations.Get(arg1).name}
    if entryTypeID == constants.refATMDeposit:
        return mls.UI_SHARED_FORMAT_ATMCASHDEPOSITBY % {'name': GetName(o1),
         'location': cfg.evelocations.Get(arg1).name}
    if entryTypeID == constants.refMissionReward:
        return mls.UI_SHARED_FORMAT_MISSIOINREWARD
    if entryTypeID == constants.refCloneActivation:
        return mls.UI_SHARED_FORMAT_CLONEACTIVATION
    if entryTypeID == constants.refCloneTransfer:
        return mls.UI_SHARED_FORMAT_CLONETRANSFERTO % {'location': GetLocation(arg1)}
    if entryTypeID == constants.refInheritance:
        return mls.UI_SHARED_FORMAT_INHERITANCEFROM % {'name': GetName(o1)}
    if entryTypeID == constants.refPlayerDonation:
        return mls.UI_SHARED_FORMAT_DEPOSITEDCASHINTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refCorporationPayment:
        if arg1 != -1:
            return mls.UI_SHARED_FORMAT_TRANSFERREDCASHFROMTO % {'arg': GetName(arg1),
             'name1': GetName(o1),
             'name2': GetName(o2)}
        return mls.UI_SHARED_FORMAT_CASHTRANSFERREDFROMTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refDockingFee:
        return mls.UI_SHARED_FORMAT_DOCKINGFEEBETWEEN % {'amount1': GetName(o1),
         'amount2': GetName(o2)}
    if entryTypeID == constants.refOfficeRentalFee:
        return mls.UI_SHARED_FORMAT_OFFICERENTALFEEBETWEEN % {'amount1': GetName(o1),
         'amount2': GetName(o2)}
    if entryTypeID == constants.refFactorySlotRentalFee:
        return mls.UI_SHARED_FORMAT_FACTORYSLOTRENTALFEE % {'amount1': GetName(o1),
         'amount2': GetName(o2)}
    if entryTypeID == constants.refAgentMiscellaneous:
        return mls.UI_SHARED_FORMAT_CASHTRANSFERFROMAGENTTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentMissionReward:
        return mls.UI_SHARED_FORMAT_MISSIONREWARDFROMAGENTTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentMissionTimeBonusReward:
        return mls.UI_SHARED_FORMAT_MISSIONREWARDBONUSFROMTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentMissionCollateralPaid:
        return mls.UI_SHARED_FORMAT_MISSIONCOLLATERALPAIDBY % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentMissionCollateralRefunded:
        return mls.UI_SHARED_FORMAT_MISSIONCOLLATERALREFUNDEDBY % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentDonation:
        return mls.UI_SHARED_FORMAT_DONATIONFROMTO % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refAgentSecurityServices:
        return mls.UI_SHARED_FORMAT_CONCORDRELATIONSBYAGENT % {'name1': GetName(o2),
         'name2': GetName(o1)}
    if entryTypeID == constants.refAgentLocationServices:
        return mls.UI_SHARED_FORMAT_PAIDAGENTTOLOCATE
    if entryTypeID == constants.refCSPA:
        if arg1:
            return mls.UI_SHARED_FORMAT_CSPASERVICECHARGE_PAIDBY % {'name1': GetName(o1),
             'name2': GetName(arg1)}
        else:
            return mls.UI_SHARED_FORMAT_CSPASERVICECHARGE_PAIDBYWITHVARIOUSPARTIES % {'name': GetName(o1)}
    elif entryTypeID == constants.refCSPAOfflineRefund:
        if arg1:
            return mls.UI_SHARED_FORMAT_CSPASERVICECHARGE_FORFAILEDCOM % {'name1': GetName(o2),
             'name2': GetName(arg1)}
        else:
            return mls.UI_SHARED_FORMAT_CSPASERVICECHARGE_FORFAILEDCOMWITHVARIOUSPARTIES % {'name1': GetName(o2)}
    elif entryTypeID == constants.refBountySurcharge:
        return mls.UI_SHARED_FORMAT_MARKETSURCHARGE
    if entryTypeID == constants.refRepairBill:
        return mls.UI_SHARED_FORMAT_REPAIRBILLBETWEEN % {'name1': GetName(o1),
         'name2': GetName(o2)}
    if entryTypeID == constants.refBounty:
        return mls.UI_SHARED_FORMAT_GAVECASHTOBOUNTYPOOL % {'name1': GetName(o1),
         'name2': GetName(arg1)}
    if entryTypeID == constants.refBountyPrize:
        return mls.UI_SHARED_FORMAT_GOTBOUNTYPRIZEFORKILLING % {'name1': GetName(o2),
         'name2': GetName(arg1)}
    if entryTypeID == constants.refBountyPrizes:
        return mls.UI_SHARED_FORMAT_GOTBOUNTYPRIZES % {'name1': GetName(o2),
         'location': GetLocation(arg1) or cfg.evelocations.Get(arg1).name}
    if entryTypeID == constants.refInsurance:
        if arg1 > 0:
            return mls.UI_SHARED_FORMAT_INSURANCEPAIDBYCOVERINGLOSS % {'name1': GetName(o1),
             'name2': GetName(o2),
             'itemname': GetName(-arg1)}
        else:
            if arg1 and arg1 < 0:
                return mls.UI_SHARED_FORMAT_INSURANCEPAIDBYFORSHIP % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'location': GetLocation(-arg1),
                 'refID': -arg1}
            return mls.UI_SHARED_FORMAT_INSURANCEPAIDBYTO % {'name1': GetName(o1),
             'name2': GetName(o2)}
    elif entryTypeID == constants.refMissionExpiration:
        return mls.UI_SHARED_FORMAT_MISSIONROLLBACKDUETO
    if entryTypeID == constants.refMissionCompletion:
        return mls.UI_SHARED_FORMAT_MISSIONCOMPLETION
    if entryTypeID == constants.refShares:
        return mls.UI_SHARED_FORMAT_COMPANYSHARESTRANSACTION
    if entryTypeID == constants.refCourierMissionEscrow:
        return mls.UI_SHARED_FORMAT_COURIERMISSIONESCROW
    if entryTypeID == constants.refMissionCost:
        return mls.UI_SHARED_FORMAT_MISSIONCOST
    if entryTypeID == const.refCorporationTaxNpcBounties:
        return mls.UI_SHARED_FORMAT_CORPORATIONTAX_NPCBOUNTY
    if entryTypeID == const.refCorporationTaxAgentRewards:
        return mls.UI_SHARED_FORMAT_CORPORATIONTAX_AGENTREWARD
    if entryTypeID == const.refCorporationTaxAgentBonusRewards:
        return mls.UI_SHARED_FORMAT_CORPORATIONTAX_AGENTBONUSREWARD
    if entryTypeID == const.refCorporationTaxRewards:
        return mls.UI_SHARED_FORMAT_CORPORATIONTAX_REWARD % {'name': GetName(o1)}
    if entryTypeID == constants.refCorporationAccountWithdrawal:
        return mls.UI_SHARED_FORMAT_TRANSFEREDCASHFROM % {'name1': GetName(arg1),
         'name2': GetName(o1),
         'name3': GetName(o2)}
    if entryTypeID == constants.refCorporationDividendPayment:
        if o2 == constants.ownerBank:
            return mls.UI_SHARED_FORMAT_PAYINGDIVIDENDS % {'name': GetName(o1)}
        else:
            return mls.UI_SHARED_FORMAT_RECEIVINGDIVIDENDPAYMENTFROM % {'name1': GetName(o2),
             'name2': GetName(arg1)}
    else:
        if entryTypeID == constants.refCorporationRegistrationFee:
            return mls.UI_SHARED_FORMAT_PAIDCORPREGISTRATIONFEE % {'name': GetName(o1)}
        else:
            if entryTypeID == constants.refCorporationLogoChangeCost:
                return mls.UI_SHARED_FORMAT_PAIDFORLOGOCHANGE % {'name1': GetName(o1),
                 'name2': GetName(arg1)}
            if entryTypeID == constants.refCorporationAdvertisementFee:
                return mls.UI_SHARED_FORMAT_PAIDCORPADVERTISEMENTFEE % {'name': GetName(o1)}
            if entryTypeID == constants.refReleaseOfImpoundedProperty:
                return mls.UI_SHARED_FORMAT_PAIDFOR_RELEASEOFIMPOUNDED % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'location': GetLocation(arg1)}
            if entryTypeID == constants.refBrokerfee:
                owner = cfg.eveowners.GetIfExists(o1)
                if owner is not None:
                    return mls.UI_SHARED_FORMAT_MARKETORDERCOMMISSIONAUTHORIZEDBY % {'name': owner.ownerName}
                return mls.UI_SHARED_FORMAT_MARKETORDERCOMMISSION
            if entryTypeID == constants.refMarketEscrow:
                if arg1 == -1:
                    owner = cfg.eveowners.GetIfExists(o1)
                else:
                    owner = cfg.eveowners.GetIfExists(o2)
                if owner is not None:
                    if amount < 0.0:
                        return mls.UI_SHARED_FORMAT_MARKETESCROWAUTHORIZEDBY % {'name': owner.ownerName}
                return [mls.UI_SHARED_FORMAT_MARKETESCROWRELEASE, mls.UI_SHARED_FORMAT_MARKETESCROW][(amount < 0.0)]
            if entryTypeID == constants.refWarFee:
                return mls.UI_SHARED_FORMAT_FEEFORWARAGAINST % {'name': GetName(arg1)}
            if entryTypeID == constants.refAllianceRegistrationFee:
                return mls.UI_SHARED_FORMAT_ALLIANCEREGISTRATIONFEE
            if entryTypeID == constants.refAllianceMaintainanceFee:
                return mls.UI_SHARED_FORMAT_FEEFORTHEMAINTAINANCE % {'name': GetName(arg1)}
            if entryTypeID == constants.refSovereignityRegistrarFee:
                return mls.UI_SHARED_FORMAT_SOVEREIGNITYREGISTRARFEE % {'systemname': GetLocation(arg1)}
            if entryTypeID == constants.refSovereignityUpkeepAdjustment:
                return mls.UI_SHARED_FORMAT_SOVEREIGNITYUPKEEPADJUSTMENT % {'systemname': GetLocation(arg1)}
            if entryTypeID == constants.refAccelerationGateFee:
                return mls.UI_SHARED_FORMAT_FEEFORUSINGACCELERATIONGATE % {'name': GetName(o2),
                 'location': GetLocation(arg1)}
            if entryTypeID == constants.refTransactionTax:
                return mls.UI_SHARED_FORMAT_SALESTAXPAID
            if entryTypeID == constants.refContrabandFine:
                return mls.UI_SHARED_FORMAT_FINEFORCONSTRABANDSMUGGLING
            if entryTypeID == constants.refManufacturing:
                return mls.UI_SHARED_FORMAT_MANUFACTURINGJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refResearchingTechnology:
                return mls.UI_SHARED_FORMAT_TECHNOLOGICALRESEARCHJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refResearchingTimeProductivity:
                return mls.UI_SHARED_FORMAT_TIMEPRODUCTIVITY_RESEARCHJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refResearchingMaterialProductivity:
                return mls.UI_SHARED_FORMAT_MATERIALPRODUCTIVITYRESEARCHJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refCopying:
                return mls.UI_SHARED_FORMAT_BLUEPRINTCOPYINGJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refDuplicating:
                return mls.UI_SHARED_FORMAT_ITEMDUPLICATIONJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refReverseEngineering:
                return mls.UI_SHARED_FORMAT_REVERSEENGINEERINGJOBFEE % {'name1': GetName(o1),
                 'name2': GetName(o2),
                 'arg': arg1}
            if entryTypeID == constants.refContractAuctionBid:
                return mls.UI_SHARED_FORMAT_CONTRACTAUCTIONBID
            if entryTypeID == constants.refContractAuctionBidRefund:
                return mls.UI_SHARED_FORMAT_CONTRACTAUCTIONBIDREFUND
            if entryTypeID == constants.refContractCollateral:
                return mls.UI_SHARED_FORMAT_CONTRACTCOLLATERAL
            if entryTypeID == constants.refContractRewardRefund:
                return mls.UI_SHARED_FORMAT_CONTRACTREWARDREFUND
            if entryTypeID == constants.refContractAuctionSold:
                return mls.UI_SHARED_FORMAT_CONTRACTAUCTIONSOLD
            if entryTypeID == constants.refContractReward:
                return mls.UI_SHARED_FORMAT_CONTRACTREWARD
            if entryTypeID == constants.refContractCollateralRefund:
                return mls.UI_SHARED_FORMAT_CONTRACTCOLLATERALREFUND
            if entryTypeID == constants.refContractCollateralPayout:
                return mls.UI_SHARED_FORMAT_CONTRACTCOLLATERALPAYOUT
            if entryTypeID == constants.refContractPrice:
                return mls.UI_SHARED_FORMAT_CONTRACTPRICE
            if entryTypeID == constants.refContractBrokersFee:
                return mls.UI_SHARED_FORMAT_CONTRACTBROKERSFEE
            if entryTypeID == constants.refContractSalesTax:
                return mls.UI_SHARED_FORMAT_CONTRACTSALESTAX
            if entryTypeID == constants.refContractDeposit:
                return mls.UI_SHARED_FORMAT_CONTRACTDEPOSIT
            if entryTypeID == constants.refContractDepositSalesTax:
                return mls.UI_SHARED_FORMAT_CONTRACTDEPOSITSALESTAX
            if entryTypeID == constants.refContractRewardAdded:
                return mls.UI_SHARED_FORMAT_CONTRACTREWARDADDED
            if entryTypeID == constants.refContractReversal:
                return mls.UI_SHARED_FORMAT_CONTRACTREVERSAL % {'arg': arg1,
                 'name1': GetName(o1),
                 'name2': GetName(o2)}
            if entryTypeID == constants.refContractAuctionBidCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTAUCTIONBIDCORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractCollateralCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTCOLLATERALCORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractPriceCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTPRICECORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractBrokersFeeCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTBROKERSFEECORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractDepositCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTDEPOSITCORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractDepositRefund:
                return mls.UI_SHARED_FORMAT_CONTRACTDEPOSITREFUND
            if entryTypeID == constants.refContractCollateralCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTCOLLATERALCORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refContractRewardAddedCorp:
                return mls.UI_SHARED_FORMAT_CONTRACTREWARDADDEDCORP % {'name': GetName(o1),
                 'arg': arg1}
            if entryTypeID == constants.refJumpCloneInstallationFee:
                return mls.UI_SHARED_FORMAT_JUMPCLONEINSTALLATIONFEE
            if entryTypeID == constants.refPaymentToLPStore:
                return mls.UI_SHARED_FORMAT_LPSTORE_PAYMENT
            if entryTypeID == constants.refSecureEVETimeCodeExchange:
                return mls.UI_SHARED_FORMAT_ETCEXCHANGEBETWEEN % {'arg': arg1,
                 'name1': GetName(o1),
                 'name2': GetName(o2)}
            if entryTypeID == constants.refMedalCreation:
                return mls.UI_SHARED_FORMAT_MEDALCREATIONFEE % {'amount1': GetName(o1),
                 'amount2': GetName(o2)}
            if entryTypeID == constants.refMedalIssuing:
                return mls.UI_SHARED_FORMAT_MEDALISSUINGFEE % {'amount1': GetName(o1),
                 'amount2': GetName(o2)}
            if entryTypeID == constants.refAttributeRespecification:
                return mls.UI_SHARED_FORMAT_ATTRIBUTERESPEC
            if entryTypeID == constants.refPlanetaryImportTax:
                return mls.UI_SHARED_FORMAT_PLANETARYIMPORTTAX % {'name': GetName(o1),
                 'planet': cfg.evelocations.Get(arg1).name if arg1 is not None else mls.UI_GENERIC_UNKNOWN}
            if entryTypeID == constants.refPlanetaryExportTax:
                return mls.UI_SHARED_FORMAT_PLANETARYEXPORTTAX % {'name': GetName(o1),
                 'planet': cfg.evelocations.Get(arg1).name if arg1 is not None else mls.UI_GENERIC_UNKNOWN}
            if entryTypeID == constants.refPlanetaryConstruction:
                return mls.UI_SHARED_FORMAT_PLANETARYCONSTRUCTION % {'name': GetName(o1),
                 'planet': cfg.evelocations.Get(arg1).name if arg1 is not None else mls.UI_GENERIC_UNKNOWN}
            if entryTypeID == constants.refRewardManager:
                return mls.UI_REWARD_JOURNAL_DESCRIPTION % {'name1': GetName(o1),
                 'name2': GetName(o2)}
            if entryTypeID == constants.refMinigameBetting:
                return mls.UI_SHARED_FORMAT_BETTINGCASHTRANSFERFROMTO % {'name1': GetName(o1),
                 'name2': GetName(o2)}
            if entryTypeID == constants.refStorePurchase:
                return mls.UI_SHARED_FORMAT_PURCHASEFROMSTORE
            if entryTypeID == constants.refPlexConversion:
                return mls.UI_SHARED_FORMAT_PLEXCONVERSION
            if pretty:
                return '-'
            return mls.UI_SHARED_FORMAT_UNKNOWNREFERENCE % {'ID': entryTypeID,
             'o1': o1,
             'o2': o2,
             'arg': arg1}



def FmtStandingTransaction(transaction):
    import uix
    subject = mls.UI_SHARED_FORMAT_STANDINGCHANGE
    body = ''
    try:
        if transaction.eventTypeID == const.eventStandingDecay:
            subject = mls.UI_SHARED_FORMAT_STANDINGDECAY
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG1
        elif transaction.eventTypeID == const.eventStandingDerivedModificationPositive:
            cfg.eveowners.Prime([transaction.fromID])
            subject = mls.UI_SHARED_FORMAT_DERIVEDMODIFICATION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG2 % {'name1': cfg.eveowners.Get(transaction.fromID).name,
             'name2': cfg.eveowners.Get(transaction.fromID).name,
             'name3': cfg.eveowners.Get(transaction.fromID).name}
        elif transaction.eventTypeID == const.eventStandingDerivedModificationNegative:
            cfg.eveowners.Prime([transaction.fromID])
            subject = mls.UI_SHARED_FORMAT_DERIVEDMODIFICATION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG3 % {'name1': cfg.eveowners.Get(transaction.fromID).name,
             'name2': cfg.eveowners.Get(transaction.fromID).name,
             'name3': cfg.eveowners.Get(transaction.fromID).name}
        elif transaction.eventTypeID == const.eventStandingCombatAggression:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = mls.UI_SHARED_FORMAT_COMBATAGGRESSION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG4 % {'ownerName': cfg.eveowners.Get(transaction.int_1).name,
             'typeName': cfg.invtypes.Get(transaction.int_3).name,
             'locationName': cfg.evelocations.Get(transaction.int_2).name}
        elif transaction.eventTypeID == const.eventStandingCombatAssistance:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = mls.UI_SHARED_FORMAT_COMBATASSISTANCE
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG5 % {'ownerName': cfg.eveowners.Get(transaction.int_1).name,
             'typeName': cfg.invtypes.Get(transaction.int_3).name,
             'locationName': cfg.evelocations.Get(transaction.int_2).name}
        elif transaction.eventTypeID == const.eventStandingCombatShipKill:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = mls.UI_SHARED_FORMAT_COMBATSHIPKILL
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG6 % {'owerName': cfg.eveowners.Get(transaction.int_1).name,
             'typeName': cfg.invtypes.Get(transaction.int_3).name,
             'locationName': cfg.evelocations.Get(transaction.int_2).name}
        elif transaction.eventTypeID == const.eventStandingPropertyDamage:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = mls.UI_SHARED_FORMAT_PROPERTYDAMAGE
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG6 % {'owerName': cfg.eveowners.Get(transaction.int_1).name,
             'typeName': cfg.invtypes.Get(transaction.int_3).name,
             'locationName': cfg.evelocations.Get(transaction.int_2).name}
        elif transaction.eventTypeID == const.eventStandingCombatPodKill:
            subject = mls.UI_SHARED_FORMAT_COMBATPODKILL
            if transaction.int_1:
                n1 = cfg.eveowners.Get(transaction.int_1).name
            else:
                n1 = '???'
            if transaction.int_2:
                n2 = cfg.evelocations.Get(transaction.int_2).name
            else:
                n2 = '???'
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG7 % {'ownerName': n1,
             'locationName': n2}
        elif transaction.eventTypeID == const.eventStandingSlashSet:
            subject = 'GM Intervention'
            if transaction.int_1:
                n = cfg.eveowners.Get(transaction.int_1).name
            else:
                n = '???'
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG8 % {'ownerName': n,
             'message': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingStandingreset:
            subject = mls.UI_SHARED_FORMAT_GMINTERVENTION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG9
        elif transaction.eventTypeID == const.eventStandingPlayerSetStanding:
            subject = mls.UI_SHARED_FORMAT_PLAYERSET
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG10 % {'message': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingPlayerCorpSetStanding:
            subject = mls.UI_SHARED_FORMAT_CORPSET
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG11 % {'ownerName': cfg.eveowners.Get(transaction.int_1).name,
             'msg': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingAgentMissionCompleted:
            subject = mls.UI_SHARED_FORMAT_MISSIONCOMPLETED % {'message': transaction.msg}
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG12 % {'msg': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingAgentMissionDeclined:
            subject = mls.UI_SHARED_FORMAT_MISSIONDECLINED % {'message': transaction.msg}
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG13 % {'msg': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingAgentMissionFailed:
            subject = mls.UI_SHARED_FORMAT_MISSIONFAILURE % {'message': transaction.msg}
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG14 % {'message': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingAgentMissionOfferExpired:
            subject = mls.UI_SHARED_FORMAT_MISSIONOFFEREXPIRED % {'message': transaction.msg}
            if transaction.msg:
                body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG15
            else:
                body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG16 % {'message': transaction.msg}
        elif transaction.eventTypeID == const.eventStandingAgentMissionBonus:
            import binascii
            import cPickle
            stuff = cPickle.loads(binascii.a2b_hex(transaction.msg))
            if transaction.modification >= 0.0:
                subject = mls.UI_SHARED_FORMAT_MISSIONBONUS % {'arg': stuff.get('header', '???')}
                body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG17 % {'arg': stuff.get('body', '???')}
            else:
                subject = mls.UI_SHARED_FORMAT_MISSIONPENALTY % {'arg': stuff.get('header', '???')}
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG18 % {'arg': stuff.get('body', '???')}
        elif transaction.eventTypeID == const.eventStandingPirateKillSecurityStatus:
            subject = mls.UI_SHARED_FORMAT_LAWENFORCEMENT
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG19 % {'ownerName': cfg.eveowners.Get(transaction.int_1).name}
        elif transaction.eventTypeID == const.eventStandingPromotionStandingIncrease:
            rankNumber = transaction.int_1
            corpID = transaction.int_2
            faction = sm.StartService('faction').GetFaction(corpID)
            subject = mls.UI_FACWAR_RANKPROMOTION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG21 % {'rankName': uix.GetRankLabel(faction, rankNumber)[0],
             'corpName': cfg.eveowners.Get(corpID).name}
        elif transaction.eventTypeID == const.eventStandingCombatShipKill_OwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = mls.UI_SHARED_FORMAT_COMBATSHIPKILL
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG27 % {'factionName': cfg.eveowners.Get(factionID).name,
             'typeName': cfg.invtypes.Get(typeID).name,
             'locationName': cfg.evelocations.Get(locationID).name}
        elif transaction.eventTypeID == const.eventStandingCombatPodKill_OwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            subject = mls.UI_SHARED_FORMAT_COMBATPODKILL
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG22 % {'factionName': cfg.eveowners.Get(factionID).name,
             'locationName': cfg.evelocations.Get(locationID).name}
        elif transaction.eventTypeID == const.eventStandingCombatAggression_OwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = mls.UI_SHARED_FORMAT_COMBATAGGRESSION
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG26 % {'factionName': cfg.eveowners.Get(factionID).name,
             'typeName': cfg.invtypes.Get(typeID).name,
             'locationName': cfg.evelocations.Get(locationID).name}
        elif transaction.eventTypeID == const.eventStandingCombatAssistance_OwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = mls.UI_SHARED_FORMAT_COMBATASSISTANCE
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG23 % {'factionName': cfg.eveowners.Get(factionID).name,
             'typeName': cfg.invtypes.Get(typeID).name,
             'locationName': cfg.evelocations.Get(locationID).name}
        elif transaction.eventTypeID == const.eventStandingPropertyDamage_OwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = mls.UI_SHARED_FORMAT_PROPERTYDAMAGE
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG27 % {'factionName': cfg.eveowners.Get(factionID).name,
             'typeName': cfg.invtypes.Get(typeID).name,
             'locationName': cfg.evelocations.Get(locationID).name}
        elif transaction.eventTypeID == const.eventStandingTacticalSiteDefended:
            factionID = transaction.int_1
            enemyFactionID = transaction.int_2
            subject = mls.UI_SHARED_FORMAT_SITEDEFENDED
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG24 % {'factionName': cfg.eveowners.Get(factionID).name,
             'enemyFactionName': cfg.eveowners.Get(enemyFactionID).name}
        elif transaction.eventTypeID == const.eventStandingTacticalSiteConquered:
            factionID = transaction.int_1
            enemyFactionID = transaction.int_2
            subject = mls.UI_SHARED_FORMAT_SITECONQUERED
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG25 % {'factionName': cfg.eveowners.Get(factionID).name,
             'enemyFactionName': cfg.eveowners.Get(enemyFactionID).name}
        elif transaction.eventTypeID == const.eventStandingRecommendationLetterUsed:
            subject = mls.UI_SHARED_FORMAT_RECOMMENDATIONLETTERUSED
            body = mls.UI_SHARED_FORMAT_RECOMMENDATIONLETTERUSED_BODY
        elif transaction.eventTypeID == const.eventStandingTutorialAgentInitial:
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG28
        elif transaction.eventTypeID == const.eventStandingContrabandTrafficking:
            factionID = transaction.int_1
            locationID = transaction.int_2
            if factionID:
                factionName = cfg.eveowners.Get(factionID).name
            else:
                factionName = mls.UI_GENERIC_SOMEONE
            if locationID:
                locationName = cfg.evelocations.Get(locationID).name
            else:
                locationName = mls.UI_GENERIC_SOMEWHERE
            subject = mls.SHARED_HDCONTRABAND
            body = mls.UI_SHARED_FORMAT_FMTSTANDINGTRANSACTION_MSG29 % {'factionName': factionName,
             'systemName': locationName}
    except:
        log.LogException()
        sys.exc_clear()
    return (subject, body)



def FmtSystemSecStatus(raw, getColor = 0):
    sec = round(raw, 1)
    if sec == -0.0:
        sec = 0.0
    if getColor == 0:
        return sec
    else:
        if sec <= 0.0:
            colorIndex = 0
        else:
            colorIndex = int(sec * 10)
        return (sec, sm.GetService('map').GetSecColorList()[colorIndex])



def GetStandingEventTypes():
    return [(mls.UI_SHARED_FORMAT_AGENTBUYOFF, const.eventStandingAgentBuyOff),
     (mls.UI_SHARED_FORMAT_AGENTDONATION, const.eventStandingAgentDonation),
     (mls.UI_SHARED_FORMAT_AGENTMISSIONBONUS, const.eventStandingAgentMissionBonus),
     (mls.UI_SHARED_FORMAT_AGENTMISSIONCOMPLETED, const.eventStandingAgentMissionCompleted),
     (mls.UI_SHARED_FORMAT_AGENTMISSIONDECLINED, const.eventStandingAgentMissionDeclined),
     (mls.UI_SHARED_FORMAT_AGENTMISSIONFAILED, const.eventStandingAgentMissionFailed),
     (mls.UI_SHARED_FORMAT_AGENTMISSIONOFFEREXPIRED, const.eventStandingAgentMissionOfferExpired),
     (mls.UI_SHARED_FORMAT_COMBATAGGRESSION, const.eventStandingCombatAggression),
     (mls.UI_SHARED_FORMAT_COMBATOTHER, const.eventStandingCombatOther),
     (mls.UI_SHARED_FORMAT_COMBATPODKILL, const.eventStandingCombatPodKill),
     (mls.UI_SHARED_FORMAT_COMBATSHIPKILL, const.eventStandingCombatShipKill),
     (mls.UI_SHARED_FORMAT_DECAY, const.eventStandingDecay),
     (mls.UI_SHARED_FORMAT_DERIVEDMODIFICATIONNEG, const.eventStandingDerivedModificationNegative),
     (mls.UI_SHARED_FORMAT_DERIVEDMODIFICATIONPOS, const.eventStandingDerivedModificationPositive),
     (mls.UI_SHARED_FORMAT_INITIALCORPAGENT, const.eventStandingInitialCorpAgent),
     (mls.UI_SHARED_FORMAT_INITIALFACTIONALLY, const.eventStandingInitialFactionAlly),
     (mls.UI_SHARED_FORMAT_INITIALFACTIONCORP, const.eventStandingInitialFactionCorp),
     (mls.UI_SHARED_FORMAT_INITIALFACTIONENEMY, const.eventStandingInitialFactionEnemy),
     (mls.UI_SHARED_FORMAT_LAW_ENFORCEMENT, const.eventStandingPirateKillSecurityStatus),
     (mls.UI_SHARED_FORMAT_PLAYERCORPSETSTANDING, const.eventStandingPlayerCorpSetStanding),
     (mls.UI_SHARED_FORMAT_PLAYERSETSTANDING, const.eventStandingPlayerSetStanding),
     (mls.UI_SHARED_FORMAT_RECALCENTITYKILLS, const.eventStandingReCalcEntityKills),
     (mls.UI_SHARED_FORMAT_RECALCMISSIONFAILURE, const.eventStandingReCalcMissionFailure),
     (mls.UI_SHARED_FORMAT_RECALCMISSIONSUCESS, const.eventStandingReCalcMissionSuccess),
     (mls.UI_SHARED_FORMAT_RECALCPIRATEKILLS, const.eventStandingReCalcPirateKills),
     (mls.UI_SHARED_FORMAT_RECALCPLAYERSETSTANDING, const.eventStandingReCalcPlayerSetStanding),
     (mls.UI_SHARED_FORMAT_SLASHSET, const.eventStandingSlashSet),
     (mls.UI_SHARED_FORMAT_STANDINGRESET, const.eventStandingStandingreset),
     (mls.UI_SHARED_FORMAT_TUTORIALAGENTINITIAL, const.eventStandingTutorialAgentInitial),
     (mls.UI_SHARED_FORMAT_UPDATESTANDING, const.eventStandingUpdatestanding)]



def GetName(ownerID):
    try:
        if ownerID == -1:
            return '(none)'
        else:
            if ownerID < 0:
                return cfg.invtypes.Get(-ownerID).name
            return cfg.eveowners.Get(ownerID).name
    except:
        sys.exc_clear()
        return 'id:%s (no name)' % ownerID



def GetLocation(locationID):
    try:
        if boot.role == 'server' or eve.session.regionid < const.mapWormholeRegionMin:
            return cfg.evelocations.Get(locationID).name
        if locationID >= const.mapWormholeRegionMin and locationID <= const.mapWormholeRegionMax:
            return '%s %s' % (mls.UI_GENERIC_UNCHARTED, mls.UI_GENERIC_REGION)
        if locationID >= const.mapWormholeConstellationMin and locationID <= const.mapWormholeConstellationMax:
            return '%s %s' % (mls.UI_GENERIC_UNCHARTED, mls.UI_GENERIC_CONSTELLATION)
        if locationID >= const.mapWormholeSystemMin and locationID <= const.mapWormholeSystemMax:
            return '%s %s' % (mls.UI_GENERIC_UNCHARTED, mls.SYSTEM)
    except:
        sys.exc_clear()
        return 'id:%s (unknown location)' % locationID



def FmtProbeState(state, colorize = False):
    stateText = getattr(mls, PROBE_STATE_TEXT_MAP[state])
    if colorize:
        return PROBE_STATE_COLOR_MAP[state] % stateText
    else:
        return stateText



def FmtPlanetAttributeKeyVal(key, val):
    text = val
    if key == 'temperature':
        text = str(int(val)) + ' K'
    elif key == 'orbitRadius':
        numAU = val / const.AU
        if numAU > 0.1:
            text = '%.3f AU' % numAU
        else:
            text = '%s km' % FmtAmt(int(val))
    elif key == 'eccentricity':
        text = '%.3f' % val
    elif key in ('massDust', 'massGas'):
        text = '%.1e kg' % val
    elif key == 'density':
        text = '%.1f g/cm^3' % val
    elif key == 'orbitPeriod':
        numDays = val / 864000
        if numDays > 1.0:
            text = '%d %s' % (int(numDays), mls.UI_GENERIC_DAYSLOWER)
        else:
            text = '%.3f %s' % (numDays, mls.UI_GENERIC_DAYSLOWER)
    elif key in ('age',):
        text = '%s %s' % (FmtAmt(int(val / 31536000 / 1000000) * 1000000), mls.UI_GENERIC_YEARS)
    elif key == 'radius':
        text = '%s km' % FmtAmt(int(val / 1000))
    elif key == 'surfaceGravity':
        text = '%.1f m/s^2' % val
    elif key == 'escapeVelocity':
        text = '%.1f km/s' % (val / 1000)
    elif key == 'pressure':
        if val < 1000:
            text = mls.UI_GENERIC_VERYLOW
        else:
            text = '%.2f kPa' % (val / 100000)
    return (getattr(mls, 'UI_CELINFO_' + key.upper(), key), text)


exports = {'util.FmtISK': FmtISK,
 'util.FmtAUR': FmtAUR,
 'util.FmtCurrency': FmtCurrency,
 'util.FmtRef': FmtRef,
 'util.FmtStandingTransaction': FmtStandingTransaction,
 'util.GetStandingEventTypes': GetStandingEventTypes,
 'util.FmtSystemSecStatus': FmtSystemSecStatus,
 'util.FmtProbeState': FmtProbeState,
 'util.GetLocation': GetLocation,
 'util.FmtPlanetAttributeKeyVal': FmtPlanetAttributeKeyVal}

