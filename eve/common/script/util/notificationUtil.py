import sys
import log
import const
import util
import blue
import entities
import types
import yaml
notificationTypes = {'notificationTypeOldLscMessages': 1,
 'notificationTypeCharTerminationMsg': 2,
 'notificationTypeCharMedalMsg': 3,
 'notificationTypeAllMaintenanceBillMsg': 4,
 'notificationTypeAllWarDeclaredMsg': 5,
 'notificationTypeAllWarSurrenderMsg': 6,
 'notificationTypeAllWarRetractedMsg': 7,
 'notificationTypeAllWarInvalidatedMsg': 8,
 'notificationTypeCharBillMsg': 9,
 'notificationTypeCorpAllBillMsg': 10,
 'notificationTypeBillOutOfMoneyMsg': 11,
 'notificationTypeBillPaidCharMsg': 12,
 'notificationTypeBillPaidCorpAllMsg': 13,
 'notificationTypeBountyClaimMsg': 14,
 'notificationTypeCloneActivationMsg': 15,
 'notificationTypeCorpAppNewMsg': 16,
 'notificationTypeCorpAppRejectMsg': 17,
 'notificationTypeCorpAppAcceptMsg': 18,
 'notificationTypeCorpTaxChangeMsg': 19,
 'notificationTypeCorpNewsMsg': 20,
 'notificationTypeCharLeftCorpMsg': 21,
 'notificationTypeCorpNewCEOMsg': 22,
 'notificationTypeCorpDividendMsg': 23,
 'notificationTypeCorpVoteMsg': 25,
 'notificationTypeCorpVoteCEORevokedMsg': 26,
 'notificationTypeCorpWarDeclaredMsg': 27,
 'notificationTypeCorpWarFightingLegalMsg': 28,
 'notificationTypeCorpWarSurrenderMsg': 29,
 'notificationTypeCorpWarRetractedMsg': 30,
 'notificationTypeCorpWarInvalidatedMsg': 31,
 'notificationTypeContainerPasswordMsg': 32,
 'notificationTypeCustomsMsg': 33,
 'notificationTypeInsuranceFirstShipMsg': 34,
 'notificationTypeInsurancePayoutMsg': 35,
 'notificationTypeInsuranceInvalidatedMsg': 36,
 'notificationTypeSovAllClaimFailMsg': 37,
 'notificationTypeSovCorpClaimFailMsg': 38,
 'notificationTypeSovAllBillLateMsg': 39,
 'notificationTypeSovCorpBillLateMsg': 40,
 'notificationTypeSovAllClaimLostMsg': 41,
 'notificationTypeSovCorpClaimLostMsg': 42,
 'notificationTypeSovAllClaimAquiredMsg': 43,
 'notificationTypeSovCorpClaimAquiredMsg': 44,
 'notificationTypeAllAnchoringMsg': 45,
 'notificationTypeAllStructVulnerableMsg': 46,
 'notificationTypeAllStrucInvulnerableMsg': 47,
 'notificationTypeSovDisruptorMsg': 48,
 'notificationTypeCorpStructLostMsg': 49,
 'notificationTypeCorpOfficeExpirationMsg': 50,
 'notificationTypeCloneRevokedMsg1': 51,
 'notificationTypeCloneMovedMsg': 52,
 'notificationTypeCloneRevokedMsg2': 53,
 'notificationTypeInsuranceExpirationMsg': 54,
 'notificationTypeInsuranceIssuedMsg': 55,
 'notificationTypeJumpCloneDeletedMsg1': 56,
 'notificationTypeJumpCloneDeletedMsg2': 57,
 'notificationTypeFWCorpJoinMsg': 58,
 'notificationTypeFWCorpLeaveMsg': 59,
 'notificationTypeFWCorpKickMsg': 60,
 'notificationTypeFWCharKickMsg': 61,
 'notificationTypeFWCorpWarningMsg': 62,
 'notificationTypeFWCharWarningMsg': 63,
 'notificationTypeFWCharRankLossMsg': 64,
 'notificationTypeFWCharRankGainMsg': 65,
 'notificationTypeAgentMoveMsg': 66,
 'notificationTypeTransactionReversalMsg': 67,
 'notificationTypeReimbursementMsg': 68,
 'notificationTypeLocateCharMsg': 69,
 'notificationTypeResearchMissionAvailableMsg': 70,
 'notificationTypeMissionOfferExpirationMsg': 71,
 'notificationTypeMissionTimeoutMsg': 72,
 'notificationTypeStoryLineMissionAvailableMsg': 73,
 'notificationTypeTutorialMsg': 74,
 'notificationTypeTowerAlertMsg': 75,
 'notificationTypeTowerResourceAlertMsg': 76,
 'notificationTypeStationAggressionMsg1': 77,
 'notificationTypeStationStateChangeMsg': 78,
 'notificationTypeStationConquerMsg': 79,
 'notificationTypeStationAggressionMsg2': 80,
 'notificationTypeFacWarCorpJoinRequestMsg': 81,
 'notificationTypeFacWarCorpLeaveRequestMsg': 82,
 'notificationTypeFacWarCorpJoinWithdrawMsg': 83,
 'notificationTypeFacWarCorpLeaveWithdrawMsg': 84,
 'notificationTypeCorpLiquidationMsg': 85,
 'notificationTypeSovereigntyTCUDamageMsg': 86,
 'notificationTypeSovereigntySBUDamageMsg': 87,
 'notificationTypeSovereigntyIHDamageMsg': 88,
 'notificationTypeContactAdd': 89,
 'notificationTypeContactEdit': 90,
 'notificationTypeIncursionCompletedMsg': 91}
groupUnread = 0
groupAgents = 1
groupBills = 2
groupCorp = 3
groupMisc = 4
groupOld = 5
groupSov = 6
groupStructures = 7
groupWar = 8
groupContacts = 9
groupTypes = {groupAgents: [notificationTypes['notificationTypeAgentMoveMsg'],
               notificationTypes['notificationTypeLocateCharMsg'],
               notificationTypes['notificationTypeResearchMissionAvailableMsg'],
               notificationTypes['notificationTypeMissionOfferExpirationMsg'],
               notificationTypes['notificationTypeMissionTimeoutMsg'],
               notificationTypes['notificationTypeStoryLineMissionAvailableMsg'],
               notificationTypes['notificationTypeTutorialMsg']],
 groupBills: [notificationTypes['notificationTypeAllMaintenanceBillMsg'],
              notificationTypes['notificationTypeCharBillMsg'],
              notificationTypes['notificationTypeCorpAllBillMsg'],
              notificationTypes['notificationTypeBillOutOfMoneyMsg'],
              notificationTypes['notificationTypeBillPaidCharMsg'],
              notificationTypes['notificationTypeBillPaidCorpAllMsg'],
              notificationTypes['notificationTypeCorpOfficeExpirationMsg']],
 groupContacts: [notificationTypes['notificationTypeContactAdd'], notificationTypes['notificationTypeContactEdit']],
 groupCorp: [notificationTypes['notificationTypeCharTerminationMsg'],
             notificationTypes['notificationTypeCharMedalMsg'],
             notificationTypes['notificationTypeCorpAppNewMsg'],
             notificationTypes['notificationTypeCorpAppRejectMsg'],
             notificationTypes['notificationTypeCorpAppAcceptMsg'],
             notificationTypes['notificationTypeCorpTaxChangeMsg'],
             notificationTypes['notificationTypeCorpNewsMsg'],
             notificationTypes['notificationTypeCharLeftCorpMsg'],
             notificationTypes['notificationTypeCorpNewCEOMsg'],
             notificationTypes['notificationTypeCorpDividendMsg'],
             notificationTypes['notificationTypeCorpVoteMsg'],
             notificationTypes['notificationTypeCorpVoteCEORevokedMsg'],
             notificationTypes['notificationTypeCorpLiquidationMsg']],
 groupMisc: [notificationTypes['notificationTypeBountyClaimMsg'],
             notificationTypes['notificationTypeCloneActivationMsg'],
             notificationTypes['notificationTypeContainerPasswordMsg'],
             notificationTypes['notificationTypeCustomsMsg'],
             notificationTypes['notificationTypeInsuranceFirstShipMsg'],
             notificationTypes['notificationTypeInsurancePayoutMsg'],
             notificationTypes['notificationTypeInsuranceInvalidatedMsg'],
             notificationTypes['notificationTypeCloneRevokedMsg1'],
             notificationTypes['notificationTypeCloneMovedMsg'],
             notificationTypes['notificationTypeCloneRevokedMsg2'],
             notificationTypes['notificationTypeInsuranceExpirationMsg'],
             notificationTypes['notificationTypeInsuranceIssuedMsg'],
             notificationTypes['notificationTypeJumpCloneDeletedMsg1'],
             notificationTypes['notificationTypeJumpCloneDeletedMsg2'],
             notificationTypes['notificationTypeTransactionReversalMsg'],
             notificationTypes['notificationTypeReimbursementMsg'],
             notificationTypes['notificationTypeIncursionCompletedMsg']],
 groupOld: [notificationTypes['notificationTypeOldLscMessages']],
 groupSov: [notificationTypes['notificationTypeSovAllClaimFailMsg'],
            notificationTypes['notificationTypeSovCorpClaimFailMsg'],
            notificationTypes['notificationTypeSovAllBillLateMsg'],
            notificationTypes['notificationTypeSovCorpBillLateMsg'],
            notificationTypes['notificationTypeSovAllClaimLostMsg'],
            notificationTypes['notificationTypeSovCorpClaimLostMsg'],
            notificationTypes['notificationTypeSovAllClaimAquiredMsg'],
            notificationTypes['notificationTypeSovCorpClaimAquiredMsg'],
            notificationTypes['notificationTypeSovDisruptorMsg'],
            notificationTypes['notificationTypeAllStructVulnerableMsg'],
            notificationTypes['notificationTypeAllStrucInvulnerableMsg'],
            notificationTypes['notificationTypeSovereigntyTCUDamageMsg'],
            notificationTypes['notificationTypeSovereigntySBUDamageMsg'],
            notificationTypes['notificationTypeSovereigntyIHDamageMsg']],
 groupStructures: [notificationTypes['notificationTypeAllAnchoringMsg'],
                   notificationTypes['notificationTypeCorpStructLostMsg'],
                   notificationTypes['notificationTypeTowerAlertMsg'],
                   notificationTypes['notificationTypeTowerResourceAlertMsg'],
                   notificationTypes['notificationTypeStationAggressionMsg1'],
                   notificationTypes['notificationTypeStationStateChangeMsg'],
                   notificationTypes['notificationTypeStationConquerMsg'],
                   notificationTypes['notificationTypeStationAggressionMsg2']],
 groupWar: [notificationTypes['notificationTypeAllWarDeclaredMsg'],
            notificationTypes['notificationTypeAllWarSurrenderMsg'],
            notificationTypes['notificationTypeAllWarRetractedMsg'],
            notificationTypes['notificationTypeAllWarInvalidatedMsg'],
            notificationTypes['notificationTypeCorpWarDeclaredMsg'],
            notificationTypes['notificationTypeCorpWarFightingLegalMsg'],
            notificationTypes['notificationTypeCorpWarSurrenderMsg'],
            notificationTypes['notificationTypeCorpWarRetractedMsg'],
            notificationTypes['notificationTypeCorpWarInvalidatedMsg'],
            notificationTypes['notificationTypeFWCorpJoinMsg'],
            notificationTypes['notificationTypeFWCorpLeaveMsg'],
            notificationTypes['notificationTypeFWCorpKickMsg'],
            notificationTypes['notificationTypeFWCharKickMsg'],
            notificationTypes['notificationTypeFWCorpWarningMsg'],
            notificationTypes['notificationTypeFWCharWarningMsg'],
            notificationTypes['notificationTypeFWCharRankLossMsg'],
            notificationTypes['notificationTypeFWCharRankGainMsg'],
            notificationTypes['notificationTypeFacWarCorpJoinRequestMsg'],
            notificationTypes['notificationTypeFacWarCorpLeaveRequestMsg'],
            notificationTypes['notificationTypeFacWarCorpJoinWithdrawMsg'],
            notificationTypes['notificationTypeFacWarCorpLeaveWithdrawMsg']]}
groupNames = {groupAgents: mls.UI_EVEMAIL_NOTIFICATIONS_AGENTS,
 groupBills: mls.UI_EVEMAIL_NOTIFICATIONS_BILLS,
 groupContacts: mls.UI_CONTACTS_CONTACTS,
 groupCorp: mls.UI_EVEMAIL_NOTIFICATIONS_CORPORATE,
 groupMisc: mls.UI_EVEMAIL_NOTIFICATIONS_MISC,
 groupOld: mls.UI_EVEMAIL_NOTIFICATIONS_OLD,
 groupSov: mls.UI_EVEMAIL_NOTIFICATIONS_SOV,
 groupStructures: mls.UI_EVEMAIL_NOTIFICATIONS_STRUCTURES,
 groupWar: mls.UI_EVEMAIL_NOTIFICATIONS_WAR}
events = {notificationTypes['notificationTypeOldLscMessages']: 'OnNotificationTypeOldMLSMessages',
 notificationTypes['notificationTypeCharTerminationMsg']: 'OnNotificationTypeCharTerminationMsg',
 notificationTypes['notificationTypeCharMedalMsg']: 'OnNotificationTypeCharMedal',
 notificationTypes['notificationTypeAllMaintenanceBillMsg']: 'OnNotificationTypeAllMaintenanceBillMsg',
 notificationTypes['notificationTypeAllWarDeclaredMsg']: 'OnNotificationTypeAllWarDeclaredMsg',
 notificationTypes['notificationTypeAllWarSurrenderMsg']: 'OnNotificationTypeAllWarSurrenderMsg',
 notificationTypes['notificationTypeAllWarRetractedMsg']: 'OnNotificationTypeAllWarRetractedMsg',
 notificationTypes['notificationTypeAllWarInvalidatedMsg']: 'OnNotificationTypeAllWarInvalidatedMsg',
 notificationTypes['notificationTypeCharBillMsg']: 'OnNotificationTypeCharBillMsg',
 notificationTypes['notificationTypeCorpAllBillMsg']: 'OnNotificationTypeCorpAllBillMsg',
 notificationTypes['notificationTypeBillOutOfMoneyMsg']: 'OnNotificationTypeBillOutOfMoneyMsg',
 notificationTypes['notificationTypeBillPaidCharMsg']: 'OnNotificationTypeBillPaidCharMsg',
 notificationTypes['notificationTypeBillPaidCorpAllMsg']: 'OnNotificationTypeBillPaidCorpAllMsg',
 notificationTypes['notificationTypeBountyClaimMsg']: 'OnNotificationTypeBountyClaimMsg',
 notificationTypes['notificationTypeCloneActivationMsg']: 'OnNotificationTypeCloneActivationMsg',
 notificationTypes['notificationTypeCorpAppNewMsg']: 'OnNotificationTypeCorpAppNewMsg',
 notificationTypes['notificationTypeCorpAppRejectMsg']: 'OnNotificationTypeCorpAppRejectMsg',
 notificationTypes['notificationTypeCorpAppAcceptMsg']: 'OnNotificationTypeCorpAppAcceptMsg',
 notificationTypes['notificationTypeCorpTaxChangeMsg']: 'OnNotificationTypeCorpTaxChangeMsg',
 notificationTypes['notificationTypeCorpNewsMsg']: 'OnNotificationTypeCorpNewsMsg',
 notificationTypes['notificationTypeCharLeftCorpMsg']: 'OnNotificationTypeCharLeftCorpMsg',
 notificationTypes['notificationTypeCorpNewCEOMsg']: 'OnNotificationTypeCorpNewCEOMsg',
 notificationTypes['notificationTypeCorpLiquidationMsg']: 'OnNotificationTypeCorpDividendMsg',
 notificationTypes['notificationTypeCorpDividendMsg']: 'OnNotificationTypeCorpDividendMsg',
 notificationTypes['notificationTypeCorpVoteMsg']: 'OnNotificationTypeCorpVoteMsg',
 notificationTypes['notificationTypeCorpVoteCEORevokedMsg']: 'OnNotificationTypeCorpVoteCEORevokedMsg',
 notificationTypes['notificationTypeCorpWarDeclaredMsg']: 'OnNotificationTypeCorpWarDeclaredMsg',
 notificationTypes['notificationTypeCorpWarFightingLegalMsg']: 'OnNotificationTypeCorpWarFightingLegalMsg',
 notificationTypes['notificationTypeCorpWarSurrenderMsg']: 'OnNotificationTypeCorpWarSurrenderMsg',
 notificationTypes['notificationTypeCorpWarRetractedMsg']: 'OnNotificationTypeCorpWarRetractedMsg',
 notificationTypes['notificationTypeCorpWarInvalidatedMsg']: 'OnNotificationTypeCorpWarInvalidatedMsg',
 notificationTypes['notificationTypeContainerPasswordMsg']: 'OnNotificationTypeContainerPasswordMsg',
 notificationTypes['notificationTypeCustomsMsg']: 'OnNotificationTypeCustomsMsg',
 notificationTypes['notificationTypeInsuranceFirstShipMsg']: 'OnNotificationTypeInsuranceFirstShipMsg',
 notificationTypes['notificationTypeInsurancePayoutMsg']: 'OnNotificationTypeInsurancePayoutMsg',
 notificationTypes['notificationTypeInsuranceInvalidatedMsg']: 'OnNotificationTypeInsuranceInvalidatedMsg',
 notificationTypes['notificationTypeSovAllClaimFailMsg']: 'OnNotificationTypeSovAllClaimFailMsg',
 notificationTypes['notificationTypeSovCorpClaimFailMsg']: 'OnNotificationTypeSovCorpClaimFailMsg',
 notificationTypes['notificationTypeSovAllBillLateMsg']: 'OnNotificationTypeSovAllBillLateMsg',
 notificationTypes['notificationTypeSovCorpBillLateMsg']: 'OnNotificationTypeSovCorpBillLateMsg',
 notificationTypes['notificationTypeSovAllClaimLostMsg']: 'OnNotificationTypeSovAllClaimLostMsg',
 notificationTypes['notificationTypeSovCorpClaimLostMsg']: 'OnNotificationTypeSovCorpClaimLostMsg',
 notificationTypes['notificationTypeSovAllClaimAquiredMsg']: 'OnNotificationTypeSovAllClaimAquiredMsg',
 notificationTypes['notificationTypeSovCorpClaimAquiredMsg']: 'OnNotificationTypeSovCorpClaimAquiredMsg',
 notificationTypes['notificationTypeAllAnchoringMsg']: 'OnNotificationTypeAllAnchoringMsg',
 notificationTypes['notificationTypeAllStructVulnerableMsg']: 'OnNotificationTypeAllStructVulnerableMsg',
 notificationTypes['notificationTypeAllStrucInvulnerableMsg']: 'OnNotificationTypeAllStrucInvulnerableMsg',
 notificationTypes['notificationTypeSovDisruptorMsg']: 'OnNotificationTypeSovDisruptorMsg',
 notificationTypes['notificationTypeCorpStructLostMsg']: 'OnNotificationTypeCorpStructLostMsg',
 notificationTypes['notificationTypeCorpOfficeExpirationMsg']: 'OnNotificationTypeCorpOfficeExpirationMsg',
 notificationTypes['notificationTypeCloneRevokedMsg1']: 'OnNotificationTypeCloneRevokedMsg1',
 notificationTypes['notificationTypeCloneMovedMsg']: 'OnNotificationTypeCloneMovedMsg',
 notificationTypes['notificationTypeCloneRevokedMsg2']: 'OnNotificationTypeCloneRevokedMsg2',
 notificationTypes['notificationTypeInsuranceExpirationMsg']: 'OnNotificationTypeInsuranceExpirationMsg',
 notificationTypes['notificationTypeInsuranceIssuedMsg']: 'OnNotificationTypeInsuranceIssuedMsg',
 notificationTypes['notificationTypeJumpCloneDeletedMsg1']: 'OnNotificationTypeJumpCloneDeletedMsg1',
 notificationTypes['notificationTypeJumpCloneDeletedMsg2']: 'OnNotificationTypeJumpCloneDeletedMsg2',
 notificationTypes['notificationTypeFWCorpJoinMsg']: 'OnNotificationTypeFWCorpJoinMsg',
 notificationTypes['notificationTypeFWCorpLeaveMsg']: 'OnNotificationTypeFWCorpLeaveMsg',
 notificationTypes['notificationTypeFWCorpKickMsg']: 'OnNotificationTypeFWCorpKickMsg',
 notificationTypes['notificationTypeFWCharKickMsg']: 'OnNotificationTypeFWCharKickMsg',
 notificationTypes['notificationTypeFWCorpWarningMsg']: 'OnNotificationTypeFWCorpWarningMsg',
 notificationTypes['notificationTypeFWCharWarningMsg']: 'OnNotificationTypeFWCharWarningMsg',
 notificationTypes['notificationTypeFWCharRankLossMsg']: 'OnNotificationTypeFWCharRankLossMsg',
 notificationTypes['notificationTypeFWCharRankGainMsg']: 'OnNotificationTypeFWCharRankGainMsg',
 notificationTypes['notificationTypeAgentMoveMsg']: 'OnNotificationTypeAgentMoveMsg',
 notificationTypes['notificationTypeTransactionReversalMsg']: 'OnNotificationTypeTransactionReversalMsg',
 notificationTypes['notificationTypeReimbursementMsg']: 'OnNotificationTypeReimbursementMsg',
 notificationTypes['notificationTypeLocateCharMsg']: 'OnNotificationTypeLocateCharMsg',
 notificationTypes['notificationTypeResearchMissionAvailableMsg']: 'OnNotificationTypeResearchMissionAvailableMsg',
 notificationTypes['notificationTypeMissionOfferExpirationMsg']: 'OnNotificationTypeMissionOfferExpirationMsg',
 notificationTypes['notificationTypeMissionTimeoutMsg']: 'OnNotificationTypeMissionTimeoutMsg',
 notificationTypes['notificationTypeStoryLineMissionAvailableMsg']: 'OnNotificationTypeStoryLineMissionAvailableMsg',
 notificationTypes['notificationTypeTowerAlertMsg']: 'OnNotificationTypeTowerAlertMsg',
 notificationTypes['notificationTypeTowerResourceAlertMsg']: 'OnNotificationTypeTowerResourceAlertMsg',
 notificationTypes['notificationTypeStationAggressionMsg1']: 'OnNotificationTypeStationAggressionMsg1',
 notificationTypes['notificationTypeStationStateChangeMsg']: 'OnNotificationTypeStationStateChangeMsg',
 notificationTypes['notificationTypeStationConquerMsg']: 'OnNotificationTypeStationConquerMsg',
 notificationTypes['notificationTypeStationAggressionMsg2']: 'OnNotificationTypeStationAggressionMsg2',
 notificationTypes['notificationTypeFacWarCorpJoinRequestMsg']: 'OnNotificationTypeFacWarCorpJoinRequestMsg',
 notificationTypes['notificationTypeFacWarCorpLeaveRequestMsg']: 'OnNotificationTypeFacWarCorpLeaveRequestMsg',
 notificationTypes['notificationTypeFacWarCorpJoinWithdrawMsg']: 'OnNotificationTypeFacWarCorpJoinWithdrawMsg',
 notificationTypes['notificationTypeFacWarCorpLeaveWithdrawMsg']: 'OnNotificationTypeFacWarCorpLeaveWithdrawMsg',
 notificationTypes['notificationTypeSovereigntyTCUDamageMsg']: 'OnNotificationTypeSovTCUDamagedMsg',
 notificationTypes['notificationTypeSovereigntySBUDamageMsg']: 'OnNotificationTypeSovSBUDamagedMsg',
 notificationTypes['notificationTypeSovereigntyIHDamageMsg']: 'OnNotificationTypeSovIHDamagedMsg',
 notificationTypes['notificationTypeIncursionCompletedMsg']: 'OnNotificationTypeIncursionCompletedMsg',
 notificationTypes['notificationTypeTutorialMsg']: 'OnNotificationTypeTutorialMsg'}

def GetTypeGroup(typeID):
    for (groupID, typeIDs,) in groupTypes.iteritems():
        if typeID in typeIDs:
            return groupID




def CreateItemInfoLink(itemID):
    item = cfg.eveowners.Get(itemID)
    return '<a href="showinfo:%(typeID)s//%(itemID)s">%(itemName)s</a>' % {'typeID': item.typeID,
     'itemID': itemID,
     'itemName': item.name}



def CreateLocationInfoLink(locationID, locationTypeID = None):
    locationName = cfg.evelocations.Get(locationID).name
    if locationTypeID is None:
        if util.IsRegion(locationID):
            locationTypeID = const.typeRegion
        elif util.IsConstellation(locationID):
            locationTypeID = const.typeConstellation
        elif util.IsSolarSystem(locationID):
            locationTypeID = const.typeSolarSystem
        elif util.IsStation(locationID):
            if boot.role == 'client':
                stationinfo = sm.RemoteSvc('stationSvc').GetStation(locationID)
            else:
                stationinfo = sm.GetService('stationSvc').GetStation(locationID)
            locationTypeID = stationinfo.stationTypeID
    if locationTypeID is None:
        return locationName
    else:
        return '<a href="showinfo:%(typeID)s//%(locationID)s">%(locationName)s</a>' % {'typeID': locationTypeID,
         'locationID': locationID,
         'locationName': locationName}



def CreateTypeInfoLink(typeID):
    return '<a href="showinfo:%(typeID)s">%(typeName)s</a>' % {'typeID': typeID,
     'typeName': cfg.invtypes.Get(typeID).name}



def GetAgent(agentID):
    if boot.role == 'client':
        return sm.GetService('agents').GetAgentByID(agentID)
    else:
        agent = util.KeyVal(sm.GetService('agentMgr').GetAgentStaticInfo(agentID))
        station = sm.GetService('stationSvc').GetStation(agent.stationID)
        if agent.corporationID is None:
            agent.corporationID = station.ownerID
        agent.solarsystemID = station.solarSystemID
        return agent



def FormatOldLscNotification(notification):
    return (notification.data['subject'], notification.data['body'])



def FormatCharacterTerminationNotification(notification):
    dict = {}
    dict['charName'] = CreateItemInfoLink(notification.data['charID'])
    dict['date'] = util.FmtDate(notification.created, 'ln')
    dict['corpName'] = CreateItemInfoLink(notification.data['corpID'])
    dict['roleName'] = notification.data['roleName']
    security = int(round(notification.data['security']))
    if security >= 0:
        mlsID = 'MAIL_TEMPLATE_CHAR_TERMINATION_SEC_P%02d' % security
    else:
        mlsID = 'MAIL_TEMPLATE_CHAR_TERMINATION_SEC_M%02d' % -security
    secDesc = mls.GetLabelIfExists(mlsID) or ''
    if len(secDesc):
        secDesc = secDesc % dict
    dict['securityDescription'] = secDesc
    subject = mls.MAIL_TEMPLATE_CHAR_TERMINATION_SUBJECT % dict
    body = mls.MAIL_TEMPLATE_CHAR_TERMINATION_BODY % dict
    body2 = mls.MAIL_TEMPLATE_CHAR_TERMINATION_BODY_P10 % dict
    tailpiece = mls.MAIL_TEMPLATE_CHAR_TERMINATION_TAIL % dict
    message = '%s\n\n%s\n\n%s' % (body, body2, tailpiece)
    return (subject, message)



def FormatCharacterMedalNotification(notification):
    medalID = notification.data['medalID']
    if boot.role == 'client':
        medalDetails = sm.GetService('medals').GetMedalDetails(medalID)
    else:
        medalDetails = sm.GetService('corporationSvc').GetMedalDetails(medalID)
    medal = medalDetails.info[0]
    reason = notification.data['reason']
    corpName = CreateItemInfoLink(notification.data['corpID'])
    subject = mls.UI_GENERIC_MEDAL_MESSAGE_TITLE % {'medalName': medal['title']}
    message = mls.UI_GENERIC_MEDAL_MESSAGE_BODY % {'medalName': medal['title'],
     'issuerCorp': corpName,
     'reason': reason,
     'medalDescription': medal['description']}
    return (subject, message)



def FormatAllMaintenanceBillNotification(notification):
    allianceID = notification.data['allianceID']
    dueDate = notification.data['dueDate']
    allianceName = CreateItemInfoLink(allianceID)
    message = mls.MAIL_TEMPLATE_ALLIANCE_MAINTENANCE_DUE_BODY % {'allianceName': allianceName,
     'dueDate': util.FmtDate(dueDate, 'ln')}
    return (mls.MAIL_TEMPLATE_ALLIANCE_MAINTENANCE_DUE_HEADER, message)



def FormatAllWarNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    delayHours = notification.data['delayHours']
    hostileState = notification.data['hostileState']
    cost = notification.data['cost']
    againstName = CreateItemInfoLink(againstID)
    declaredByName = CreateItemInfoLink(declaredByID)
    if notification.typeID == const.notificationTypeAllWarDeclaredMsg:
        heading = mls.MAIL_TEMPLATE_DECLARES_WAR_AGAINST_SUBJECT % {'declaredByName': declaredByName,
         'againstName': againstName}
        if hostileState:
            message = mls.MAIL_TEMPLATE_WAR_MAIL_FIGHTING_IS_LEGAL % {'declaredByName': declaredByName,
             'againstName': againstName}
        else:
            message = mls.MAIL_TEMPLATE_DECLARES_WAR_AGAINST_BODY2 % {'declaredByName': declaredByName,
             'againstName': againstName,
             'hours': delayHours}
        if cost:
            message += mls.MAIL_TEMPLATE_WAR_STANDARD_BODY % {'cost': util.FmtISK(cost)}
    elif notification.typeID == const.notificationTypeAllWarSurrenderMsg:
        heading = mls.MAIL_TEMPLATE_SURRENDERS_SUBJECT % {'againstName': againstName,
         'declaredByName': declaredByName}
        message = mls.MAIL_TEMPLATE_SURRENDERS_BODY % {'againstName': againstName,
         'declaredByName': declaredByName}
    elif notification.typeID == const.notificationTypeAllWarRetractedMsg:
        heading = mls.MAIL_TEMPLATE_RETRACTS_WAR_SUBJECT % {'declaredByName': declaredByName,
         'againstName': againstName}
        message = mls.MAIL_TEMPLATE_RETRACTS_WAR_BODY % {'declaredByName': declaredByName,
         'againstName': againstName}
    elif notification.typeID == const.notificationTypeAllWarInvalidatedMsg:
        heading = mls.MAIL_TEMPLATE_CONCORD_INVALIDATES_WAR_SUBJECT % {'declaredByName': declaredByName,
         'againstName': againstName}
        message = mls.MAIL_TEMPLATE_CONCORD_INVALIDATES_WAR_BODY
    return (heading, message)



def FormatBillNotification(notification):
    creditorID = notification.data['creditorID']
    debtorID = notification.data['debtorID']
    externalID = notification.data['externalID']
    externalID2 = notification.data['externalID2']
    billTypeID = notification.data['billTypeID']
    amount = util.FmtAmt(notification.data['amount'])
    dueDate = notification.data['dueDate']
    try:
        currentDate = notification.data['currentDate']
    except KeyError:
        currentDate = notification.created
    mlsParams = {}
    mlsParams['amount'] = amount
    mlsParams['dueDate'] = util.FmtDate(dueDate, 'ln')
    mlsParams['creditorsName'] = CreateItemInfoLink(creditorID)
    mlsParams['debtorsName'] = CreateItemInfoLink(debtorID)
    mlsParams['currentDate'] = util.FmtDate(currentDate, 'ln')
    message = ''
    if billTypeID == const.billTypeMarketFine:
        if externalID != -1 and externalID2 != -1:
            mlsParams['locationName'] = CreateLocationInfoLink(externalID2)
            mlsParams['itemType'] = CreateTypeInfoLink(externalID)
        else:
            mlsParams['locationName'] = mls.UI_GENERIC_SOMEMARKET.lower()
            mlsParams['itemType'] = mls.UI_GENERIC_SOMETHING.lower()
        message = mls.MAIL_TEMPLATE_BILL_MARKET_FINE % mlsParams
    elif billTypeID == const.billTypeRentalBill:
        if externalID != -1 and externalID2 != -1:
            typeID = externalID
            locationID = externalID2
            mlsParams['locationName'] = CreateLocationInfoLink(locationID)
            if typeID == const.typeOffice:
                mlsParams['itemType'] = mls.UI_GENERIC_OFFICE.lower()
            else:
                mlsParams['itemType'] = CreateTypeInfoLink(typeID)
        else:
            mlsParams['locationName'] = mls.UI_GENERIC_SOMESTATION.lower()
            mlsParams['itemType'] = mls.UI_GENERIC_UNKNOWN.lower()
        message = mls.MAIL_TEMPLATE_BILL_RENTAL % mlsParams
    elif billTypeID == const.billTypeBrokerBill:
        if externalID != -1 and externalID2 != -1:
            mlsParams['locationName'] = CreateLocationInfoLink(externalID2)
            mlsParams['orderID'] = externalID
        else:
            mlsParams['locationName'] = mls.UI_GENERIC_SOMEWHERE.lower()
            mlsParams['orderID'] = mls.UI_GENERIC_UNKNOWN
        message = mls.MAIL_TEMPLATE_BILL_BROKER % mlsParams
    elif billTypeID == const.billTypeWarBill:
        if externalID != -1:
            mlsParams['against'] = CreateItemInfoLink(externalID)
        else:
            mlsParams['against'] = mls.UI_GENERIC_SOMEONE.lower()
        message = mls.MAIL_TEMPLATE_BILL_WAR % mlsParams
    elif billTypeID == const.billTypeAllianceMaintainanceBill:
        if externalID != -1:
            mlsParams['allianceName'] = CreateItemInfoLink(externalID)
        else:
            mlsParams['allianceName'] = mls.UI_GENERIC_SOMEALLIANCE.lower()
        message = mls.MAIL_TEMPLATE_BILL_ALLIANCE_MTS % mlsParams
    elif billTypeID == const.billTypeSovereignityMarker:
        if externalID2 != -1:
            mlsParams['solarSystemName'] = CreateLocationInfoLink(externalID2)
        else:
            mlsParams['solarSystemName'] = mls.UI_GENERIC_SOMEWHERE
        message = mls.MAIL_TEMPLATE_BILL_SOVEREIGNTY % mlsParams
    return (mls.UI_GENERIC_BILLISSUED, message)



def FormatBillOutOfMoneyNotification(notification):
    dueTime = util.FmtDate(notification.data['dueDate'], 'ss')
    billTypeID = notification.data['billTypeID']
    billTypeName = cfg.billtypes.Get(billTypeID).billTypeName
    message = mls.MAIL_TEMPLATE_BILL_OUT_OF_MONEY_BODY % {'billType': billTypeName,
     'dueDate': dueTime}
    return (mls.MAIL_TEMPLATE_BILL_OUT_OF_MONEY_SUBJECT, message)



def FormatBillPaidNotification(notification):
    amount = notification.data['amount']
    dueDate = notification.data['dueDate']
    message = mls.MAIL_TEMPLATE_BILL_PAID_BODY % {'amount': util.FmtISK(amount),
     'dueDate': util.FmtDate(dueDate, 'ln'),
     'currentDate': util.FmtDate(notification.created, 'ln')}
    return (mls.MAIL_TEMPLATE_BILL_PAID_SUBJECT, message)



def FormatBountyClaimNotification(notification):
    characterID = notification.data['charID']
    amount = notification.data['amount']
    message = mls.MAIL_TEMPLATE_CLAIM_BOUNTY_BODY % {'playerName': CreateItemInfoLink(characterID),
     'paymentAmount': util.FmtISK(amount)}
    return (mls.MAIL_TEMPLATE_CLAIM_BOUNTY_SUBJECT, message)



def FormatCloneActivationNotification(notification):
    cloneStationID = notification.data['cloneStationID']
    corpStationID = notification.data['corpStationID']
    cloneTypeID = notification.data['cloneTypeID']
    podKillerID = notification.data['podKillerID']
    skillPointsLost = notification.data['skillPointsLost']
    skillID = notification.data['skillID']
    lastCloned = notification.data['lastCloned']
    cloneBought = notification.data['cloneBought']
    cloningServiceMessage = ''
    if cloneStationID != corpStationID:
        cloningServiceMessage = mls.MGT_CHAR_CLONE_SERVICE_DISABLED % {'newStationName': CreateLocationInfoLink(corpStationID),
         'oldStationName': CreateLocationInfoLink(cloneStationID)}
    if podKillerID:
        warning = mls.MGT_CHAR_CLONEMGR_ACTIVATEDCLONE_WARNING2 % {'name': CreateItemInfoLink(podKillerID)}
    else:
        warning = mls.MGT_CHAR_CLONEMGR_ACTIVATEDCLONE_WARNING1
    cloneTypeName = CreateTypeInfoLink(cloneTypeID)
    if skillPointsLost is None:
        dict = {'stationname': CreateLocationInfoLink(corpStationID),
         'cloneTypeName': cloneTypeName,
         'warning': warning,
         'cloningServiceMessage': cloningServiceMessage}
        text = mls.MAIL_TEMPLATE_CLONE_ACTIVATED % dict
    else:
        dict = {'stationname': CreateLocationInfoLink(corpStationID),
         'spLost': skillPointsLost,
         'skillDecreased': CreateTypeInfoLink(skillID),
         'cloneTypeName': cloneTypeName,
         'warning': warning,
         'cloningServiceMessage': cloningServiceMessage}
        text = mls.MAIL_TEMPLATE_CLONE_ACTIVATED_SP_LOST % dict
        if lastCloned is not None:
            text = text + '<br><br>' + mls.MAIL_TEMPLATE_CLONE_LAST % {'date': util.FmtDate(lastCloned, 'ls')}
        if cloneBought is not None:
            text = text + '<br>' + mls.MAIL_TEMPLATE_CLONE_LAST_PURCHASE % {'cloneName': cloneTypeName,
             'date': util.FmtDate(cloneBought, 'ls')}
    return (mls.MGT_CHAR_CLONEMGR_CLONEACTIVATED, text)



def FormatCorpAppNewNotification(notification):
    characterID = notification.data['charID']
    applicationText = notification.data['applicationText']
    title = mls.MAIL_TEMPLATE_NEW_APPLICATION_SUBJECT % {'playerName': CreateItemInfoLink(characterID)}
    return (title, applicationText)



def FormatCorpAppRejectNotification(notification):
    characterID = notification.data['charID']
    corporationID = notification.data['corpID']
    applicationText = notification.data['applicationText']
    corporationName = CreateItemInfoLink(corporationID)
    title = mls.MAIL_TEMPLATE_APP_REJECTED_BY_CORP_SUBJECT % {'corporationName': corporationName}
    message = mls.MAIL_TEMPLATE_APP_REJECTED_BY_CORP_BODY2 % {'applicantName': CreateItemInfoLink(characterID),
     'corporationName': corporationName,
     'message': applicationText}
    return (title, message)



def FormatCorpAppAcceptNotification(notification):
    characterID = notification.data['charID']
    corporationID = notification.data['corpID']
    applicationText = notification.data['applicationText']
    corporationName = CreateItemInfoLink(corporationID)
    title = mls.MAIL_TEMPLATE_APP_ACCEPTED_BY_CORP_SUBJECT % {'corporationName': corporationName}
    message = mls.MAIL_TEMPLATE_APP_ACCEPTED_BY_CORP_BODY2 % {'applicantName': CreateItemInfoLink(characterID),
     'corporationName': corporationName,
     'message': applicationText}
    return (title, message)



def FormatCorpTaxChangeNotification(notification):
    corporationID = notification.data['corpID']
    oldTaxRate = notification.data['oldTaxRate']
    newTaxRate = notification.data['newTaxRate']
    title = mls.MAIL_TEMPLATE_TAX_RATE_CHANGED_SUBJECT % {'newTaxRate': newTaxRate}
    message = mls.MAIL_TEMPLATE_TAX_RATE_CHANGED_BODY % {'corporationName': CreateItemInfoLink(corporationID),
     'oldTaxRate': oldTaxRate,
     'newTaxRate': newTaxRate}
    return (title, message)



def FormatCorpNewsNotification(notification):
    corporationID = notification.data['corpID']
    parameter = notification.data['parameter']
    voteType = notification.data['voteType']
    inEffect = notification.data['inEffect']
    message = notification.data['body']
    heading = CreateItemInfoLink(corporationID)
    if voteType == const.voteWar:
        if inEffect:
            title = mls.MAIL_TEMPLATE_X_DECLARES_WAR_ON_Y % {'corporationX': heading,
             'corporationY': CreateItemInfoLink(parameter)}
        else:
            title = mls.MAIL_TEMPLATE_X_NO_LONGER_AT_WAR_WITH_Y % {'corporationX': heading,
             'corporationY': CreateItemInfoLink(parameter)}
    elif voteType == const.voteShares:
        title = mls.MAIL_TEMPLATE_X_CREATES_Y_SHARES % {'corporationName': heading,
         'amount': parameter}
    elif voteType == const.voteKickMember:
        title = mls.MAIL_TEMPLATE_X_EXPELLS_Y % {'corporationName': heading,
         'playerName': CreateItemInfoLink(parameter)}
    if message == '':
        message = title
    return (title, message)



def FormatCharLeftCorpNotification(notification):
    characterID = notification.data['charID']
    oldCorporationID = notification.data['corpID']
    mlsParams = {'corporationName': CreateItemInfoLink(oldCorporationID),
     'playerName': CreateItemInfoLink(characterID)}
    title = mls.MAIL_TEMPLATE_X_HAS_LEFT_Y_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_X_HAS_LEFT_Y_BODY % mlsParams
    return (title, message)



def FormatCorpNewCEONotification(notification):
    corporationID = notification.data['corpID']
    oldCeoID = notification.data['oldCeoID']
    newCeoID = notification.data['newCeoID']
    mlsParams = {'OldCEOsName': CreateItemInfoLink(oldCeoID),
     'NewCEOsName': CreateItemInfoLink(newCeoID),
     'CorporationName': CreateItemInfoLink(corporationID)}
    title = mls.MAIL_TEMPLATE_CEO_QUIT_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_CEO_QUIT_BODY % mlsParams
    return (title, message)



def FormatCorpLiquidationNotification(notification):
    corporationID = notification.data['corpID']
    payoutAmount = notification.data['payout']
    corpName = CreateItemInfoLink(corporationID)
    title = mls.MAIL_TEMPLATE_LIQUIDATION_SUBJECT % {'corporationName': corpName}
    message = mls.MAIL_TEMPLATE_LIQUIDATION_BODY % {'corporationName': corpName,
     'amount': payoutAmount}
    message = message + ' ' + mls.MAIL_TEMPLATE_PAYOUT_BODY_TAIL
    return (title, message)



def FormatCorpDividendNotification(notification):
    corporationID = notification.data['corpID']
    payoutAmount = notification.data['payout']
    corpName = CreateItemInfoLink(corporationID)
    title = mls.MAIL_TEMPLATE_DIVIDEND_SUBJECT % {'corporationName': corpName}
    if 'isMembers' in notification.data and notification.data['isMembers']:
        message = mls.MAIL_TEMPLATE_DIVIDEND_MEMBERS_BODY % {'corporationName': corpName,
         'amount': payoutAmount}
        message = message + ' ' + mls.MAIL_TEMPLATE_PAYOUT_MEMBERS_BODY_TAIL
    else:
        message = mls.MAIL_TEMPLATE_DIVIDEND_BODY % {'corporationName': corpName,
         'amount': payoutAmount}
        message = message + ' ' + mls.MAIL_TEMPLATE_PAYOUT_BODY_TAIL
    return (title, message)



def FormatCorpVoteNotification(notification):
    voteCaseText = notification.data['subject']
    description = notification.data['body']
    title = mls.MAIL_TEMPLATE_CORPORATE_VOTE_SUBJECT % {'voteCaseText': voteCaseText}
    return (title, description)



def FormatCorpVoteCEORevokedNotification(notification):
    corporationID = notification.data['corpID']
    characterID = notification.data['charID']
    message = mls.MAIL_TEMPLATE_CEO_ROLES_REVOKED_BODY % {'candidateName': CreateItemInfoLink(characterID),
     'corporationName': CreateItemInfoLink(corporationID)}
    return (mls.MAIL_TEMPLATE_CEO_ROLES_REVOKED_SUBJECT, message)



def FormatCorpWarDeclaredNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    cost = notification.data['cost']
    mlsParams = {'declaredByName': CreateItemInfoLink(declaredByID),
     'againstName': CreateItemInfoLink(againstID)}
    title = mls.MAIL_TEMPLATE_DECLARES_WAR_AGAINST_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_DECLARES_WAR_AGAINST_BODY % mlsParams
    if cost:
        message += mls.MAIL_TEMPLATE_WAR_STANDARD_BODY % {'cost': util.FmtISK(cost)}
    return (title, message)



def FormatCorpWarFightingLegalNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    cost = notification.data['cost']
    mlsParams = {'declaredByName': CreateItemInfoLink(declaredByID),
     'againstName': CreateItemInfoLink(againstID)}
    title = mls.MAIL_TEMPLATE_DECLARES_WAR_AGAINST_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_WAR_MAIL_FIGHTING_IS_LEGAL % mlsParams
    if cost:
        message += mls.MAIL_TEMPLATE_WAR_STANDARD_BODY % {'cost': util.FmtISK(cost)}
    return (title, message)



def FormatCorpWarSurrenderNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    mlsParams = {'declaredByName': CreateItemInfoLink(declaredByID),
     'againstName': CreateItemInfoLink(againstID)}
    title = mls.MAIL_TEMPLATE_SURRENDERS_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_SURRENDERS_BODY % mlsParams
    return (title, message)



def FormatCorpWarRetractedNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    mlsParams = {'declaredByName': CreateItemInfoLink(declaredByID),
     'againstName': CreateItemInfoLink(againstID)}
    title = mls.MAIL_TEMPLATE_RETRACTS_WAR_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_RETRACTS_WAR_BODY % mlsParams
    return (title, message)



def FormatCorpWarInvalidatedNotification(notification):
    declaredByID = notification.data['declaredByID']
    againstID = notification.data['againstID']
    mlsParams = {'declaredByName': CreateItemInfoLink(declaredByID),
     'againstName': CreateItemInfoLink(againstID)}
    title = mls.MAIL_TEMPLATE_CONCORD_INVALIDATES_WAR_SUBJECT % mlsParams
    message = mls.MAIL_TEMPLATE_CONCORD_INVALIDATES_WAR_BODY
    return (title, message)



def FormatContainerPasswordNotification(notification):
    characterID = notification.data['charID']
    solarsystemID = notification.data['solarSystemID']
    stationID = notification.data['stationID']
    typeID = notification.data['typeID']
    passwordType = notification.data['passwordType']
    password = notification.data['password']
    locationName = ''
    if stationID is not None:
        locationName = mls.UI_GENERIC_STATIONINSYSTEM % {'stationName': CreateLocationInfoLink(stationID),
         'solarSystem': CreateLocationInfoLink(solarsystemID)}
    else:
        locationName = CreateLocationInfoLink(solarsystemID)
    if passwordType == 'general':
        passwordType = mls.UI_GENERIC_GENERAL
    else:
        passwordType = mls.UI_GENERIC_CONFIGURATION
    title = mls.INV_CONTAINER_PASSWORD_MAIL_TITLE % CreateItemInfoLink(characterID)
    message = mls.INV_CONTAINER_PASSWORD_MAIL_BODY % (passwordType.lower(),
     CreateTypeInfoLink(typeID),
     locationName,
     password)
    return (title, message)



def FormatCustomsNotification(notification):
    factionID = notification.data['factionID']
    solarsystemID = notification.data['solarSystemID']
    shouldAttack = notification.data['shouldAttack']
    shouldConfiscate = notification.data['shouldConfiscate']
    securityLevel = notification.data['securityLevel']
    standingDivision = notification.data['standingDivision']
    lostList = notification.data['lostList']
    standingPenaltySum = 0
    fineSum = 0
    message = mls.DJINN_INFESTGROUP_CONTRABANDCONFISCATIONBODY % {'empire': CreateItemInfoLink(factionID),
     'solarsystem': CreateLocationInfoLink(solarsystemID),
     'security': securityLevel}
    for lost in lostList:
        typeID = lost['typeID']
        quantity = lost['quantity']
        penalty = lost['penalty']
        fine = lost['fine']
        message += mls.AGGRESSION_KILLMAIL_LOST_STACK_ENTRY % {'type': CreateTypeInfoLink(typeID),
         'qty': quantity,
         'loc': ''}
        standingPenaltySum += penalty
        fineSum += fine
        message += mls.DJINN_INFESTGROUP_STANDINGPENALTY % {'penalty': penalty,
         'fine': util.FmtAmt(fine)}
        if shouldAttack:
            message += mls.DJINN_INFESTGROUP_STANDINGRESPONSEREASON1
        elif shouldConfiscate:
            message += mls.DJINN_INFESTGROUP_STANDINGRESPONSEREASON2
        message += '<br>'

    message += mls.DJINN_INFESTGROUP_STANDINGSPENALTIES % {'ideal': standingPenaltySum,
     'actual': standingPenaltySum / standingDivision,
     'total': util.FmtAmt(fineSum)}
    if shouldAttack:
        message += mls.DJINN_INFESTGROUP_STANDINGSUMMARYRESPONSEREASON1
    elif shouldConfiscate:
        message += mls.DJINN_INFESTGROUP_STANDINGSUMMARYRESPONSEREASON2
    return (mls.DJINN_INFESTGROUP_CONTRABANDCONFISCATION, message)



def FormatInsuranceFirstShipNotification(notification):
    shipTypeID = notification.data['shipTypeID']
    if 'isHouseWarmingGift' not in notification.data:
        isHouseWarmingGift = 0
    else:
        isHouseWarmingGift = notification.data['isHouseWarmingGift']
    if isHouseWarmingGift:
        giftName = CreateTypeInfoLink(const.deftypeHouseWarmingGift)
    else:
        giftName = mls.INSURANCE_MAIL_NOOBSHIP_GIFTOFKINDTHOUGHTS
    message = mls.INSURANCE_MAIL_NOOBSHIP_BODY % {'ship': CreateTypeInfoLink(shipTypeID),
     'gift': giftName}
    return (mls.INSURANCE_MAIL_NOOBSHIP_TITLE, message)



def FormatInsurancePayoutNotification(notification):
    itemID = notification.data['itemID']
    defaultPayout = notification.data['payout']
    amount = notification.data['amount']
    message = mls.MAIL_TEMPLATE_LIEN_PAGE_BODY % {'amount': util.FmtCurrency(amount, showFractionsAlways=1, currency=None)}
    message = 'RefID:%s ' % itemID + message
    if defaultPayout:
        message = message + mls.MGT_SOL_LIENMGR_PAYOUT_MSG
    return (mls.MAIL_TEMPLATE_LIEN_PAGE_SUBJECT, message)



def FormatInsuranceInvalidatedNotification(notification):
    shipID = notification.data['shipID']
    typeID = notification.data['typeID']
    ownerID = notification.data['ownerID']
    reason = notification.data['reason']
    startDate = notification.data['startDate']
    endDate = notification.data['endDate']
    mlsParams = {'shipID': shipID,
     'type': CreateTypeInfoLink(typeID),
     'startDate': util.FmtDate(startDate, 'ls'),
     'endDate': util.FmtDate(endDate, 'ls'),
     'reason': ''}
    if reason == 1:
        mlsParams['reason'] = mls.MGT_SOL_LIENMGR_HANDLESHIPDESTRUCTION_INVALIDCONTRACT % {'name': CreateItemInfoLink(ownerID)}
    elif reason == 2:
        mlsParams['reason'] = mls.MGT_SOL_LIENMGR_HANDLESHIPDESTRUCTION_INVALIDCONTRACT2
    elif reason == 3:
        mlsParams['reason'] = mls.MGT_SOL_LIENMGR_HANDLESHIPDESTRUCTION_INVALIDCONTRACT3
    return (mls.MGT_SOL_LIENMGR_SENDMAILFORINVALIDCONTRACT_TITLE, mls.MGT_SOL_LIENMGR_SENDMAILFORINVALIDCONTRACT_MSG % mlsParams)



def FormatSovAllClaimFailNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    reason = notification.data['reason']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    title = mls.SOVEREIGNTY_CLAIM_FAILED_HEADER % mlsParams
    message = ''
    if reason == 1:
        message = mls.SOVEREIGNTY_CLAIMED_BY_OTHER_BODY % mlsParams
    elif reason == 2:
        message = mls.SOVEREIGNTY_NO_ALLIANCE_BODY % mlsParams
    elif reason == 3:
        message = mls.SOVEREIGNTY_BILL_NOT_PAID_BODY % mlsParams
    return (title, message)



def FormatSovCorpClaimFailNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    reason = notification.data['reason']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    title = mls.SOVEREIGNTY_CLAIM_FAILED_HEADER % mlsParams
    message = ''
    if reason == 1:
        message = mls.SOVEREIGNTY_CLAIMED_BY_OTHER_BODY % mlsParams
    elif reason == 2:
        message = mls.SOVEREIGNTY_NO_ALLIANCE_BODY % mlsParams
    elif reason == 3:
        message = mls.SOVEREIGNTY_BILL_NOT_PAID_BODY % mlsParams
    return (title, message)



def FormatSovAllBillLateNotification(notification):
    corporationID = notification.data['corpID']
    solarSystemID = notification.data['solarSystemID']
    dueInDays = notification.data['dueInDays']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'dueInDays': dueInDays}
    return (mls.SOVEREIGNTY_BILL_LATE_HEADER % mlsParams, mls.SOVEREIGNTY_BILL_LATE_BODY % mlsParams)



def FormatSovCorpBillLateNotification(notification):
    corporationID = notification.data['corpID']
    solarSystemID = notification.data['solarSystemID']
    dueInDays = notification.data['dueInDays']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'dueInDays': dueInDays}
    return (mls.SOVEREIGNTY_BILL_LATE_HEADER % mlsParams, mls.SOVEREIGNTY_BILL_LATE_BODY % mlsParams)



def FormatSovAllClaimLostNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    return (mls.SOVEREIGNTY_UNCLAIM_MAIL_ALLIANCE_HEADER % mlsParams, mls.SOVEREIGNTY_UNCLAIM_MAIL_ALLIANCE_BODY % mlsParams)



def FormatSovCorpClaimLostNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    return (mls.SOVEREIGNTY_UNCLAIM_MAIL_CORPORATION_HEADER % mlsParams, mls.SOVEREIGNTY_UNCLAIM_MAIL_CORPORATION_BODY % mlsParams)



def FormatSovAllClaimAquiredNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    return (mls.SOVEREIGNTY_CLAIM_MAIL_ALLIANCE_HEADER % mlsParams, mls.SOVEREIGNTY_CLAIM_MAIL_ALLIANCE_BODY % mlsParams)



def FormatSovCorpClaimAquiredNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarSystemID = notification.data['solarSystemID']
    mlsParams = {'system': CreateLocationInfoLink(solarSystemID),
     'corporation': CreateItemInfoLink(corporationID),
     'alliance': CreateItemInfoLink(allianceID)}
    return (mls.SOVEREIGNTY_CLAIM_MAIL_CORPORATION_HEADER % mlsParams, mls.SOVEREIGNTY_CLAIM_MAIL_CORPORATION_BODY % mlsParams)



def FormatAllAnchoringNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    moonID = notification.data['moonID']
    typeID = notification.data['typeID']
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    corpsPresent = notification.data['corpsPresent']
    title = mls.STARBASE_MAIL_ANCHORING_TITLE % CreateLocationInfoLink(solarsystemID)
    message = mls.STARBASE_MAIL_ANCHORING_SYSTEM % CreateLocationInfoLink(solarsystemID)
    message += mls.STARBASE_TEMPLATE_MOON_BIT % {'moon': CreateLocationInfoLink(moonID)}
    message += mls.STARBASE_TEMPLATE_TOWER_BIT % {'tower': CreateTypeInfoLink(typeID)}
    message += mls.STARBASE_TEMPLATE_CORP_BIT % {'corp': CreateItemInfoLink(corporationID)}
    if allianceID is not None:
        message += mls.STARBASE_TEMPLATE_ALLIANCE_BIT % {'alliance': CreateItemInfoLink(allianceID)}
    message += '<br>'
    if corpsPresent is not None and len(corpsPresent):
        message += mls.STARBASE_MAIL_ANCHORING_TOWERS
        for corp in corpsPresent:
            if len(corp['towers']) > 0:
                subCorporationID = corp['corpID']
                subAllianceID = corp['allianceID']
                message += mls.STARBASE_MAIL_ANCHORING_CORP_BIT % CreateItemInfoLink(subCorporationID)
                if subAllianceID is not None:
                    message += mls.STARBASE_MAIL_ANCHORING_ALLIANCE_BIT % CreateItemInfoLink(subAllianceID)
                for tower in corp['towers']:
                    subTypeID = tower['typeID']
                    subMoonID = tower['moonID']
                    moonName = CreateLocationInfoLink(subMoonID)
                    message += mls.STARBASE_MAIL_ANCHORING_TOWER_BIT % {'moonName': moonName,
                     'towerType': CreateTypeInfoLink(subTypeID)}

                message += '<br>'

    else:
        message += mls.STARBASE_MAIL_ANCHORING_TOWERS_NONE
    return (title, message)



def FormatAllStructVulnerableNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarsystemID = notification.data['solarSystemID']
    systemName = CreateLocationInfoLink(solarsystemID)
    mlsParams = {'corporation': corporationID,
     'alliance': allianceID,
     'system': systemName}
    return (mls.SOVEREIGNTY_VULNERABLE_ALLIANCE_HEADER % mlsParams, mls.SOVEREIGNTY_VULNERABLE_ALLIANCE_BODY % mlsParams)



def FormatAllStrucInvulnerableNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarsystemID = notification.data['solarSystemID']
    systemName = CreateLocationInfoLink(solarsystemID)
    mlsParams = {'corporation': corporationID,
     'alliance': allianceID,
     'system': systemName}
    return (mls.SOVEREIGNTY_NOTVULNERABLE_ALLIANCE_HEADER % mlsParams, mls.SOVEREIGNTY_NOTVULNERABLE_ALLIANCE_BODY % mlsParams)



def FormatSovDisruptorNotification(notification):
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    solarsystemID = notification.data['solarSystemID']
    systemName = CreateLocationInfoLink(solarsystemID)
    mlsParams = {'corporation': corporationID,
     'alliance': allianceID,
     'system': systemName}
    return (mls.SOVEREIGNTY_DISRUPTOR_DETECTED_HEADER % mlsParams, mls.SOVEREIGNTY_DISRUPTOR_DETECTED_BODY % mlsParams)



def FormatCorpStructLostNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    oldOwnerID = notification.data['oldOwnerID']
    newOwnerID = notification.data['newOwnerID']
    ownerID = notification.data['ownerID']
    structName = notification.data['name']
    title = mls.INFRASTRUCTURE_MAIL_CONQUER_TITLE % {'struct': structName}
    message = mls.INFRASTRUCTURE_MAIL_CONQUER_LOCATION % {'system': CreateLocationInfoLink(solarsystemID)}
    message += mls.INFRASTRUCTURE_MAIL_CONQUER_LOSER % {'corp': CreateItemInfoLink(oldOwnerID)}
    message += mls.INFRASTRUCTURE_MAIL_CONQUER_WINNER % {'corp': CreateItemInfoLink(newOwnerID)}
    if ownerID is not None:
        message += mls.INFRASTRUCTURE_MAIL_CONQUER_PILOT % {'char': CreateItemInfoLink(ownerID)}
    return (title, message)



def FormatCorpOfficeExpirationNotification(notification):
    typeID = notification.data['typeID']
    stationID = notification.data['stationID']
    rentPeriod = notification.data['rentPeriod']
    errorRecordText = notification.data['errorText']
    dueDate = notification.data['dueDate']
    message = ''
    strDueDate = util.FmtDate(dueDate, 'ls')
    locationName = CreateLocationInfoLink(stationID)
    if typeID == const.typeOfficeFolder:
        message = mls.MAIL_TEMPLATE_LEASE_BODY_1 % {'station': locationName,
         'when': strDueDate}
    else:
        message = mls.MAIL_TEMPLATE_LEASE_BODY_2 % {'item': CreateTypeInfoLink(typeID),
         'station': locationName,
         'when': strDueDate}
    message = mls.MAIL_TEMPLATE_LEASE_BODY_3 % {'prefix': message,
     'days': rentPeriod}
    if errorRecordText:
        message = mls.MAIL_TEMPLATE_LEASE_BODY_4 % {'prefix': message,
         'postfix': errorRecordText}
    return (mls.MAIL_TEMPLATE_LEASE_SUBJECT, message)



def FormatCloneRevoked1Notification(notification):
    stationID = notification.data['stationID']
    corporationID = notification.data['corpID']
    newStationID = notification.data['newStationID']
    title = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_SUBJECT % {'station': CreateLocationInfoLink(stationID)}
    message = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_BODY_1 % {'managerStation': CreateItemInfoLink(corporationID),
     'toStation': CreateLocationInfoLink(newStationID)}
    return (title, message)



def FormatCloneMovedNotification(notification):
    stationID = notification.data['stationID']
    corporationID = notification.data['corpID']
    newStationID = notification.data['newStationID']
    charsInCorpID = notification.data['charsInCorpID']
    title = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_SUBJECT % {'station': CreateLocationInfoLink(stationID)}
    message = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_BODY_2 % {'corporation': CreateItemInfoLink(charsInCorpID),
     'managerStation': CreateItemInfoLink(corporationID),
     'toStation': CreateLocationInfoLink(newStationID)}
    return (title, message)



def FormatCloneRevoked2Notification(notification):
    stationID = notification.data['stationID']
    corporationID = notification.data['corpID']
    newStationID = notification.data['newStationID']
    title = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_SUBJECT % {'station': CreateLocationInfoLink(stationID)}
    message = mls.MAIL_TEMPLATE_CLONE_CONTRACT_REVOKED_BODY_3 % {'managerStation': CreateItemInfoLink(corporationID),
     'toStation': CreateLocationInfoLink(newStationID)}
    return (title, message)



def FormatInsuranceExpirationNotification(notification):
    shipID = notification.data['shipID']
    shipName = notification.data['shipName']
    startDate = notification.data['startDate']
    endDate = notification.data['endDate']
    message = mls.INSURANCE_MAIL_EXPIRE_BODY % {'shipName': shipName,
     'startDate': util.FmtDate(startDate, 'ls'),
     'endDate': util.FmtDate(endDate, 'ls'),
     'refID': shipID}
    return (mls.INSURANCE_MAIL_EXPIRE_TITLE, message)



def FormatInsuranceIssuedNotification(notification):
    typeID = notification.data['typeID']
    itemID = notification.data['itemID']
    numWeeks = notification.data['numWeeks']
    level = notification.data['level']
    shipName = notification.data['shipName']
    startDate = notification.data['startDate']
    endDate = notification.data['endDate']
    d = {'typeID': typeID,
     'itemID': itemID,
     'shipName': shipName,
     'typeName': CreateTypeInfoLink(typeID),
     'level': level,
     'startDate': startDate,
     'endDate': util.FmtDate(endDate, 'ls'),
     'numWeeks': numWeeks,
     'refID': itemID}
    message = mls.INSURANCE_MAIL_ISSUE_BODY % d
    return (mls.INSURANCE_MAIL_ISSUE_TITLE, message)



def FormatJumpCloneDeleted1Notification(notification):
    jumpCloneOwnerID = notification.data['ownerID']
    jumpCloneLocationID = notification.data['locationID']
    jumpCloneLocationOwnerID = notification.data['locationOwnerID']
    implantTypeIDs = notification.data['typeIDs']
    locationOwnerName = CreateItemInfoLink(jumpCloneLocationOwnerID)
    mlsParams = {'cloneOwner': CreateItemInfoLink(jumpCloneOwnerID),
     'cloneLoc': CreateLocationInfoLink(jumpCloneLocationID),
     'cloneLocOwner': locationOwnerName,
     'cloneDestroyer': locationOwnerName}
    message = mls.CLONE_MAIL_JUMP_DESTRUCTION_BODY % mlsParams
    if len(implantTypeIDs):
        message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANTS_HEADER
        for implantTypeID in implantTypeIDs:
            message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANT_TYPE % CreateTypeInfoLink(int(implantTypeID))

    else:
        message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANTS_NONE
    return (mls.CLONE_MAIL_JUMP_DESTRUCTION_TITLE, message)



def FormatJumpCloneDeleted2Notification(notification):
    jumpCloneOwnerID = notification.data['ownerID']
    jumpCloneLocationID = notification.data['locationID']
    jumpCloneLocationOwnerID = notification.data['locationOwnerID']
    jumpCloneDestroyerID = notification.data['destroyerID']
    implantTypeIDs = notification.data['typeIDs']
    mlsParams = {'cloneOwner': CreateItemInfoLink(jumpCloneOwnerID),
     'cloneLoc': CreateLocationInfoLink(jumpCloneLocationID),
     'cloneLocOwner': CreateItemInfoLink(jumpCloneLocationOwnerID),
     'cloneDestroyer': CreateItemInfoLink(jumpCloneDestroyerID)}
    message = mls.CLONE_MAIL_JUMP_DESTRUCTION_BODY % mlsParams
    if len(implantTypeIDs):
        message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANTS_HEADER
        for implantTypeID in implantTypeIDs:
            message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANT_TYPE % CreateTypeInfoLink(int(implantTypeID))

    else:
        message += mls.CLONE_MAIL_JUMP_DESTRUCTION_IMPLANTS_NONE
    return (mls.CLONE_MAIL_JUMP_DESTRUCTION_TITLE, message)



def FormatFWCorpJoinNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_ACTIVE_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_ACTIVE_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFWCorpLeaveNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_GONE_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_GONE_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFWCharKickNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_MEMBER_KICKED_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_MEMBER_KICKED_BODY
    return FormatFacWarMemberStandingNotification(mlsTitle, mlsMessage, notification)



def FormatFWCorpKickNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_KICKED_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_KICKED_BODY
    return FormatFacWarMemberStandingNotification(mlsTitle, mlsMessage, notification)



def FormatFWCharWarningNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_MEMBER_WARNING_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_MEMBER_WARNING_BODY
    return FormatFacWarMemberStandingNotification(mlsTitle, mlsMessage, notification)



def FormatFWCorpWarningNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_WARNING_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_WARNING_BODY
    return FormatFacWarMemberStandingNotification(mlsTitle, mlsMessage, notification)



def FormatFacWarMemberStandingNotification(mlsTitle, mlsMessage, notification):
    corporationID = notification.data['corpID']
    factionID = notification.data['factionID']
    currentStanding = notification.data['currentStanding']
    requiredStanding = notification.data['requiredStanding']
    mlsParams = {'corporationName': CreateItemInfoLink(corporationID),
     'factionName': CreateItemInfoLink(factionID),
     'currentStanding': currentStanding,
     'requiredStanding': requiredStanding}
    return (mlsTitle % mlsParams, mlsMessage % mlsParams)



def FormatFWCharRankLossNotification(notification):
    factionID = notification.data['factionID']
    newRank = notification.data['newRank']
    rankName = getattr(mls, 'UI_FACWAR_FACTION_%s_RANK_%s' % (factionID, newRank), mls.UI_GENERIC_UNKNOWN)
    message = getattr(mls, 'UI_FACWAR_RANKLOST_%s' % factionID, mls.UI_GENERIC_UNKNOWN) % {'rank': rankName}
    return (mls.UI_FACWAR_RANKDEMOTION, message)



def FormatFWCharRankGainNotification(notification):
    factionID = notification.data['factionID']
    newRank = notification.data['newRank']
    rankName = getattr(mls, 'UI_FACWAR_FACTION_%s_RANK_%s' % (factionID, newRank), mls.UI_GENERIC_UNKNOWN)
    message = getattr(mls, 'UI_FACWAR_RANKGAINED_%s' % factionID, mls.UI_GENERIC_UNKNOWN) % {'rank': rankName}
    return (mls.UI_FACWAR_RANKPROMOTION, message)



def FormatAgentMoveNotification(notification):
    title = notification.data['subject']
    message = notification.data['body']
    return (title, message)



def FormatTransactionReversalNotification(notification):
    message = notification.data['body']
    return (mls.ACC_MASSREVERSAL_MAIL_TITLE, message)



def FormatReimbursementNotification(notification):
    title = notification.data['subject']
    message = notification.data['body']
    return (title, message)



def FormatLocateCharNotification(notification):
    characterID = notification.data['characterID']
    messageIndex = notification.data['messageIndex']
    agentLocation = notification.data['agentLocation']
    agentRegion = agentLocation.get(const.groupRegion, None)
    agentConstellation = agentLocation.get(const.groupConstellation, None)
    agentSystem = agentLocation.get(const.groupSolarSystem, None)
    agentStation = agentLocation.get(const.groupStation, None)
    targetLocation = notification.data['targetLocation']
    targetRegion = targetLocation.get(const.groupRegion, None)
    targetConstellation = targetLocation.get(const.groupConstellation, None)
    targetSystem = targetLocation.get(const.groupSolarSystem, None)
    targetStation = targetLocation.get(const.groupStation, None)
    locationText = ''
    if agentStation == targetStation:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_HERE1
    elif targetStation != None and agentSystem == targetSystem and agentStation != targetStation:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_STATION1 % {'external.station': targetStation}
    elif agentSystem == targetSystem:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_HERE2
    elif targetStation == None:
        if targetRegion != None:
            locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_SYSTEM3 % {'external.system': targetSystem,
             'external.constellation': targetConstellation,
             'external.region': targetRegion}
        elif targetConstellation != None:
            locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_SYSTEM2 % {'external.system': targetSystem,
             'external.constellation': targetConstellation}
        elif targetSystem != None:
            locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_SYSTEM1 % {'external.system': targetSystem}
    elif targetRegion != None:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_STATION4 % {'external.station': targetStation,
         'external.system': targetSystem,
         'external.constellation': targetConstellation,
         'external.region': targetRegion}
    elif targetConstellation != None:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_STATION3 % {'external.station': targetStation,
         'external.system': targetSystem,
         'external.constellation': targetConstellation}
    elif targetSystem != None:
        locationText = mls.AGT_LOCATECHARACTER_LOCATIONSTRING_STATION2 % {'external.station': targetStation,
         'external.system': targetSystem}
    title = mls.AGT_MESSAGES_LOCATECHARACTER_LOCATED_EMAIL_HEADER % {'char.locatecharacter.who.name': CreateItemInfoLink(characterID)}
    message = mls.AGT_MESSAGES_LOCATECHARACTER_LOCATED_EMAIL_BODY.split('||')[messageIndex] % {'char.locatecharacter.who.location': locationText,
     'agent.name': CreateItemInfoLink(notification.senderID)}
    return (title, message)



def FormatResearchMissionAvailableNotification(notification):
    return (mls.AGT_MESSAGES_RESEARCH_MISSIONAVAILABLE_EMAIL_HEADER, mls.AGT_MESSAGES_RESEARCH_MISSIONAVAILABLE_EMAIL_BODY)



def FormatMissionOfferExpirationNotification(notification):
    title = notification.data['header']
    message = notification.data['body']
    return (title, message)



def FormatMissionTimeoutNotification(notification):
    title = mls.AGT_MESSAGES_MISSION_TIMEOUT_EMAILHEADER % {'char.name': CreateItemInfoLink(notification.receiverID)}
    return (title, mls.AGT_MESSAGES_MISSION_TIMEOUT_EMAILBODY)



def FormatStoryLineMissionAvailableNotification(notification):
    agent = GetAgent(notification.senderID)
    mlsParams = {'char.name': CreateItemInfoLink(notification.receiverID),
     'agent.name': CreateItemInfoLink(agent.agentID),
     'the agent.faction.name': CreateItemInfoLink(agent.corporationID)}
    title = mls.AGT_MESSAGES_MISSION_STORYLINE_INVITED_EMAIL_HEADER % mlsParams
    if agent.stationID:
        mlsParams['agent.station.name'] = CreateLocationInfoLink(agent.stationID)
        message = mls.AGT_MESSAGES_MISSION_STORYLINE_INVITEDTOSTATION_EMAIL_BODY % mlsParams
    else:
        mlsParams['agent.solarsystem.name'] = CreateLocationInfoLink(agent.solarsystemID)
        message = mls.AGT_MESSAGES_MISSION_STORYLINE_INVITEDTOSPACE_EMAIL_BODY % mlsParams
    return (title, message)



def FormatTutorialNotification(notification):
    agent = GetAgent(notification.senderID)
    mlsParams = {'char.name': CreateItemInfoLink(notification.receiverID),
     'agent.name': CreateItemInfoLink(agent.agentID),
     'agent.corp.name': CreateItemInfoLink(agent.corporationID),
     "the agent.corp.name's": CreateItemInfoLink(agent.corporationID),
     'agent.station.name': CreateLocationInfoLink(agent.stationID)}
    title = mls.AGT_MESSAGES_TUTORIAL_ONCHARCREATED_EMAIL_HEADER
    message = mls.AGT_MESSAGES_TUTORIAL_ONCHARCREATED_EMAIL_BODY % mlsParams
    return (title, message)



def FormatTowerAlertNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    towerTypeID = notification.data['typeID']
    aggressorID = notification.data['aggressorID']
    aggressorCorpID = notification.data['aggressorCorpID']
    aggressorAllID = notification.data['aggressorAllianceID']
    shieldValue = notification.data['shieldValue']
    armorValue = notification.data['armorValue']
    hullValue = notification.data['hullValue']
    if 'moonID' in notification.data:
        moonID = notification.data['moonID']
    else:
        moonID = None
    systemName = CreateLocationInfoLink(solarsystemID)
    message = mls.STARBASE_MAIL_DAMAGE_LOCATION % {'system': systemName}
    if moonID is not None:
        moonName = CreateLocationInfoLink(moonID)
    else:
        moonName = mls.UI_GENERIC_UNKNOWN.lower()
    message += mls.STARBASE_MAIL_DAMAGE_MOON % {'moon': moonName}
    message += mls.STARBASE_MAIL_DAMAGE_TARGET % {'object': CreateTypeInfoLink(towerTypeID)}
    if shieldValue is not None and armorValue is not None and hullValue is not None:
        message += mls.STARBASE_MAIL_DAMAGE_SHIELD % {'damage': int(shieldValue * 100)}
        message += mls.STARBASE_MAIL_DAMAGE_ARMOR % {'damage': int(armorValue * 100)}
        message += mls.STARBASE_MAIL_DAMAGE_HULL % {'damage': int(hullValue * 100)}
    else:
        message = mls.STARBASE_MAIL_DAMAGE_MISSING
    if aggressorID is not None:
        ownerOb = cfg.eveowners.Get(aggressorID)
        aggressorName = CreateItemInfoLink(aggressorID)
        if ownerOb.IsCharacter():
            message += mls.STARBASE_MAIL_DAMAGE_ATTACKER % {'attacker': aggressorName}
            message += mls.STARBASE_MAIL_DAMAGE_ATTACKER_CORP % {'corp': CreateItemInfoLink(aggressorCorpID)}
            allianceName = '-'
            if aggressorAllID is not None:
                allianceName = CreateItemInfoLink(aggressorAllID)
            message += mls.STARBASE_MAIL_DAMAGE_ATTACKER_ALLIANCE % {'alliance': allianceName}
        else:
            message += mls.STARBASE_MAIL_DAMAGE_ATTACKING_OWNER % {'owner': aggressorName}
    return (mls.STARBASE_MAIL_DAMAGE_TITLE % systemName, message)



def FormatTowerResourceAlertNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    moonID = notification.data['moonID']
    towerTypeID = notification.data['typeID']
    corporationID = notification.data['corpID']
    allianceID = notification.data['allianceID']
    wants = notification.data['wants']
    systemName = CreateLocationInfoLink(solarsystemID)
    message = mls.STARBASE_MAIL_RESOURCE_PREFACE
    message += mls.STARBASE_MAIL_RESOURCE_LOCATION % {'system': systemName}
    message = mls.STARBASE_TEMPLATE_MOON_BIT % {'moon': CreateLocationInfoLink(moonID)}
    message += mls.STARBASE_TEMPLATE_TOWER_BIT % {'tower': CreateTypeInfoLink(towerTypeID)}
    if corporationID:
        message += mls.STARBASE_TEMPLATE_CORP_BIT % {'corp': CreateItemInfoLink(corporationID)}
        if allianceID is not None:
            message += mls.STARBASE_TEMPLATE_ALLIANCE_BIT % {'alliance': CreateItemInfoLink(allianceID)}
        message += '<br>'
    message += mls.STARBASE_MAIL_RESOURCE_NEEDS
    for want in wants:
        message += mls.STARBASE_MAIL_RESOURCE_TYPE % {'type': CreateTypeInfoLink(want['typeID'])}
        message += mls.STARBASE_MAIL_RESOURCE_QTY % {'qty': want['quantity']}

    return (mls.STARBASE_MAIL_RESOURCE_TITLE % {'system': systemName}, message)



def FormatStationAggression1Notification(notification):
    solarsystemID = notification.data['solarSystemID']
    typeID = notification.data['typeID']
    stationID = notification.data['stationID']
    aggressorID = notification.data['aggressorID']
    aggressorCorpID = notification.data['aggressorCorpID']
    shieldValue = notification.data['shieldValue']
    message = mls.OUTPOST_MAIL_AGGRESSION_LOCATION % {'system': CreateLocationInfoLink(solarsystemID)}
    message += mls.OUTPOST_MAIL_AGGRESSION_SHIELD % {'damage': int(shieldValue * 100)}
    if aggressorID is not None:
        ownerOb = cfg.eveowners.Get(aggressorID)
        if ownerOb.IsCharacter():
            message += mls.OUTPOST_MAIL_AGGRESSION_HOSTILE_PILOT % {'char': CreateItemInfoLink(aggressorID)}
            message += mls.OUTPOST_MAIL_AGGRESSION_HOSTILE_PILOT_CORP % {'corp': CreateItemInfoLink(aggressorCorpID)}
        else:
            message += mls.OUTPOST_MAIL_AGGRESSION_HOSTILE_OWNER % {'owner': ownerOb.name}
    title = mls.OUTPOST_MAIL_SERVICE_AGGRESSION_TITLE % {'station': CreateLocationInfoLink(stationID),
     'service': CreateTypeInfoLink(typeID)}
    return (title, message)



def FormatStationStateChangeNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    typeID = notification.data['typeID']
    stationID = notification.data['stationID']
    state = notification.data['state']
    message = mls.OUTPOST_MAIL_STATE_CHANGE_LOCATION % {'system': CreateLocationInfoLink(solarsystemID)}
    title = ''
    mlsParams = {'station': CreateLocationInfoLink(stationID),
     'service': CreateTypeInfoLink(typeID)}
    if state == entities.STATE_IDLE:
        title = mls.OUTPOST_MAIL_STATE_REENABLED_TITLE % mlsParams
    elif state == entities.STATE_INCAPACITATED:
        title = mls.OUTPOST_MAIL_STATE_DISABLED_TITLE % mlsParams
    return (title, message)



def FormatStationConquerNotification(notification):
    solarsystemID = notification.data['solarSystemID']
    stationID = notification.data['stationID']
    oldOwnerID = notification.data['oldOwnerID']
    newOwnerID = notification.data['newOwnerID']
    characterID = notification.data['charID']
    title = mls.OUTPOST_MAIL_CONQUER_TITLE % {'station': CreateLocationInfoLink(stationID)}
    message = mls.OUTPOST_MAIL_CONQUER_LOCATION % {'system': CreateLocationInfoLink(solarsystemID)}
    message += mls.OUTPOST_MAIL_CONQUER_LOSER % {'corp': CreateItemInfoLink(oldOwnerID)}
    message += mls.OUTPOST_MAIL_CONQUER_WINNER % {'corp': CreateItemInfoLink(newOwnerID)}
    if characterID is not None:
        message += mls.OUTPOST_MAIL_CONQUER_PILOT % {'char': CreateItemInfoLink(characterID)}
    return (title, message)



def FormatStationAggression2Notification(notification):
    stationID = notification.data['stationID']
    aggressorID = notification.data['aggressorID']
    aggressorCorpID = notification.data['aggressorCorpID']
    aggressorAllianceID = notification.data.get('aggressorAllianceID', 0)
    shieldValue = notification.data.get('shieldValue', 0.0)
    armorValue = notification.data.get('armorValue', 0.0)
    hullValue = notification.data.get('hullValue', 0.0)
    params = {'system': CreateLocationInfoLink(notification.data['solarSystemID']),
     'station': CreateLocationInfoLink(stationID),
     'shieldValue': '%4.1f' % (shieldValue * 100.0),
     'armorValue': '%4.1f' % (armorValue * 100.0),
     'hullValue': '%4.1f' % (hullValue * 100.0)}
    if aggressorID is not None:
        params['aggressor'] = CreateItemInfoLink(aggressorID)
    else:
        params['aggressor'] = mls.UI_GENERIC_UNKNOWN
    if aggressorCorpID is not None:
        params['aggressorCorp'] = CreateItemInfoLink(aggressorCorpID)
    else:
        params['aggressorCorp'] = mls.UI_GENERIC_UNKNOWN
    if aggressorAllianceID == 0:
        params['aggressorAlliance'] = mls.UI_GENERIC_UNKNOWN
    elif aggressorAllianceID is None:
        params['aggressorAlliance'] = mls.UI_CORP_ISINALLIANCENOT
    else:
        params['aggressorAlliance'] = CreateItemInfoLink(aggressorAllianceID)
    message = mls.OUTPOST_MAIL_AGGRESSION_BODY % params
    title = mls.OUTPOST_MAIL_AGGRESSION_TITLE % {'station': CreateLocationInfoLink(stationID)}
    return (title, message)



def FormatFacWarCorpJoinRequestNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_JOINING_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_JOINING_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFacWarCorpLeaveRequestNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_LEAVING_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_LEAVING_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFacWarCorpJoinWithdrawNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_WITHDRAWN_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_WITHDRAWN_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFacWarCorpLeaveWithdrawNotification(notification):
    mlsTitle = mls.MAIL_TEMPLATE_FACTION_CORP_STAYING_SUBJECT
    mlsMessage = mls.MAIL_TEMPLATE_FACTION_CORP_STAYING_BODY
    return FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification)



def FormatFacWarCorpNotification(mlsTitle, mlsMessage, notification):
    corpID = notification.data['corpID']
    factionID = notification.data['factionID']
    mlsParams = {'corporationName': CreateItemInfoLink(corpID),
     'factionName': CreateItemInfoLink(factionID)}
    return (mlsTitle % mlsParams, mlsMessage % mlsParams)



def FormatSovDamagedNotification(header, body, notification):
    solarsystemID = notification.data['solarSystemID']
    aggressorID = notification.data.get('aggressorID', None)
    aggressorCorpID = notification.data.get('aggressorCorpID', None)
    aggressorAllID = notification.data.get('aggressorAllianceID', None)
    mlsParams = {'system': CreateLocationInfoLink(solarsystemID),
     'shieldValue': '%4.1f' % (notification.data['shieldValue'] * 100.0),
     'armorValue': '%4.1f' % (notification.data['armorValue'] * 100.0),
     'hullValue': '%4.1f' % (notification.data['hullValue'] * 100.0)}
    if aggressorID is not None:
        mlsParams['aggressor'] = CreateItemInfoLink(aggressorID)
    else:
        mlsParams['aggressor'] = mls.UI_GENERIC_UNKNOWN
    if aggressorCorpID is not None:
        mlsParams['aggressorCorp'] = CreateItemInfoLink(aggressorCorpID)
    else:
        mlsParams['aggressorCorp'] = mls.UI_GENERIC_UNKNOWN
    if aggressorAllID is not None:
        mlsParams['aggressorAlliance'] = CreateItemInfoLink(aggressorAllID)
    else:
        mlsParams['aggressorAlliance'] = mls.SOVEREIGNTY_NO_ALLIANCE
    return (header % mlsParams, body % mlsParams)



def FormatSovTCUDamagedNotification(notification):
    return FormatSovDamagedNotification(mls.SOVEREIGNTY_TCU_DAMAGE_HEADER, mls.SOVEREIGNTY_TCU_DAMAGE_BODY, notification)



def FormatSovSBUDamagedNotification(notification):
    return FormatSovDamagedNotification(mls.SOVEREIGNTY_SBU_DAMAGE_HEADER, mls.SOVEREIGNTY_SBU_DAMAGE_BODY, notification)



def FormatSovIHDamagedNotification(notification):
    return FormatSovDamagedNotification(mls.SOVEREIGNTY_IH_DAMAGE_HEADER, mls.SOVEREIGNTY_IH_DAMAGE_BODY, notification)



def FormatContactAddNotification(notification):
    level = notification.data['level']
    message = ''
    if notification.data.has_key('message'):
        message = notification.data['message']
    mlsParams = {'characterName': CreateItemInfoLink(notification.senderID),
     'level': GetRelationshipName(level)}
    return (mls.MAIL_TEMPLATE_CONTACT_ADD_HEADER, '%s<br><br>%s' % (mls.MAIL_TEMPLATE_CONTACT_ADD_BODY % mlsParams, message))



def FormatContactEditNotification(notification):
    level = notification.data['level']
    message = ''
    if notification.data.has_key('message'):
        message = notification.data['message']
    mlsParams = {'characterName': CreateItemInfoLink(notification.senderID),
     'level': GetRelationshipName(level)}
    return (mls.MAIL_TEMPLATE_CONTACT_EDIT_HEADER, '%s<br><br>%s' % (mls.MAIL_TEMPLATE_CONTACT_EDIT_BODY % mlsParams, message))



def FormatIncursionCompletedNotification(notification):
    topTen = notification.data['topTen']
    solarSystemID = notification.data['solarSystemID']
    taleID = notification.data['taleID']
    if boot.role == 'client':
        constellationID = sm.GetService('map').GetParent(solarSystemID)
    else:
        solarSystemCache = sm.GetService('cache').Index(const.cacheMapSolarSystems)
        constellationID = solarSystemCache[solarSystemID].constellationID
    (charIDs, discarded,) = zip(*topTen)
    cfg.eveowners.Prime(charIDs)
    topTenString = ''
    for (index, (topTenCharacterID, topTenRewardAmount,),) in enumerate(topTen):
        topTenArgs = {'number': index + 1,
         'character': CreateItemInfoLink(topTenCharacterID),
         'LPAmount': topTenRewardAmount}
        topTenString += mls.MAIL_TEMPLATE_INCURSION_COMPLETE_TOP_TEN_ENTRY % topTenArgs

    journalLink = '<b>' + mls.UI_GENERIC_JOURNAL + '</b>'
    messageArgs = {'character': CreateItemInfoLink(notification.receiverID),
     'constellation': CreateLocationInfoLink(constellationID),
     'topTenString': topTenString,
     'journalLink': journalLink}
    subjectArgs = {'constellation': CreateLocationInfoLink(constellationID)}
    return (mls.MAIL_TEMPLATE_INCURSION_COMPLETE_SUBJECT % subjectArgs, mls.MAIL_TEMPLATE_INCURSION_COMPLETE_MESSAGE % messageArgs)



def GetRelationshipName(level):
    if level == const.contactHighStanding:
        return mls.UI_CONTACTS_HIGHSTANDING
    if level == const.contactGoodStanding:
        return mls.UI_CONTACTS_GOODSTANDING
    if level == const.contactNeutralStanding:
        return mls.UI_CONTACTS_NEUTRALSTANDING
    if level == const.contactBadStanding:
        return mls.UI_CONTACTS_BADSTANDING
    if level == const.contactHorribleStanding:
        return mls.UI_CONTACTS_HORRIBLESTANDING


formatters = {notificationTypes['notificationTypeOldLscMessages']: FormatOldLscNotification,
 notificationTypes['notificationTypeCharTerminationMsg']: FormatCharacterTerminationNotification,
 notificationTypes['notificationTypeCharMedalMsg']: FormatCharacterMedalNotification,
 notificationTypes['notificationTypeAllMaintenanceBillMsg']: FormatAllMaintenanceBillNotification,
 notificationTypes['notificationTypeAllWarDeclaredMsg']: FormatAllWarNotification,
 notificationTypes['notificationTypeAllWarSurrenderMsg']: FormatAllWarNotification,
 notificationTypes['notificationTypeAllWarRetractedMsg']: FormatAllWarNotification,
 notificationTypes['notificationTypeAllWarInvalidatedMsg']: FormatAllWarNotification,
 notificationTypes['notificationTypeCharBillMsg']: FormatBillNotification,
 notificationTypes['notificationTypeCorpAllBillMsg']: FormatBillNotification,
 notificationTypes['notificationTypeBillOutOfMoneyMsg']: FormatBillOutOfMoneyNotification,
 notificationTypes['notificationTypeBillPaidCharMsg']: FormatBillPaidNotification,
 notificationTypes['notificationTypeBillPaidCorpAllMsg']: FormatBillPaidNotification,
 notificationTypes['notificationTypeBountyClaimMsg']: FormatBountyClaimNotification,
 notificationTypes['notificationTypeCloneActivationMsg']: FormatCloneActivationNotification,
 notificationTypes['notificationTypeCorpAppNewMsg']: FormatCorpAppNewNotification,
 notificationTypes['notificationTypeCorpAppRejectMsg']: FormatCorpAppRejectNotification,
 notificationTypes['notificationTypeCorpAppAcceptMsg']: FormatCorpAppAcceptNotification,
 notificationTypes['notificationTypeCorpTaxChangeMsg']: FormatCorpTaxChangeNotification,
 notificationTypes['notificationTypeCorpNewsMsg']: FormatCorpNewsNotification,
 notificationTypes['notificationTypeCharLeftCorpMsg']: FormatCharLeftCorpNotification,
 notificationTypes['notificationTypeCorpNewCEOMsg']: FormatCorpNewCEONotification,
 notificationTypes['notificationTypeCorpLiquidationMsg']: FormatCorpLiquidationNotification,
 notificationTypes['notificationTypeCorpDividendMsg']: FormatCorpDividendNotification,
 notificationTypes['notificationTypeCorpVoteMsg']: FormatCorpVoteNotification,
 notificationTypes['notificationTypeCorpVoteCEORevokedMsg']: FormatCorpVoteCEORevokedNotification,
 notificationTypes['notificationTypeCorpWarDeclaredMsg']: FormatCorpWarDeclaredNotification,
 notificationTypes['notificationTypeCorpWarFightingLegalMsg']: FormatCorpWarFightingLegalNotification,
 notificationTypes['notificationTypeCorpWarSurrenderMsg']: FormatCorpWarSurrenderNotification,
 notificationTypes['notificationTypeCorpWarRetractedMsg']: FormatCorpWarRetractedNotification,
 notificationTypes['notificationTypeCorpWarInvalidatedMsg']: FormatCorpWarInvalidatedNotification,
 notificationTypes['notificationTypeContainerPasswordMsg']: FormatContainerPasswordNotification,
 notificationTypes['notificationTypeCustomsMsg']: FormatCustomsNotification,
 notificationTypes['notificationTypeInsuranceFirstShipMsg']: FormatInsuranceFirstShipNotification,
 notificationTypes['notificationTypeInsurancePayoutMsg']: FormatInsurancePayoutNotification,
 notificationTypes['notificationTypeInsuranceInvalidatedMsg']: FormatInsuranceInvalidatedNotification,
 notificationTypes['notificationTypeSovAllClaimFailMsg']: FormatSovAllClaimFailNotification,
 notificationTypes['notificationTypeSovCorpClaimFailMsg']: FormatSovCorpClaimFailNotification,
 notificationTypes['notificationTypeSovAllBillLateMsg']: FormatSovAllBillLateNotification,
 notificationTypes['notificationTypeSovCorpBillLateMsg']: FormatSovCorpBillLateNotification,
 notificationTypes['notificationTypeSovAllClaimLostMsg']: FormatSovAllClaimLostNotification,
 notificationTypes['notificationTypeSovCorpClaimLostMsg']: FormatSovCorpClaimLostNotification,
 notificationTypes['notificationTypeSovAllClaimAquiredMsg']: FormatSovAllClaimAquiredNotification,
 notificationTypes['notificationTypeSovCorpClaimAquiredMsg']: FormatSovCorpClaimAquiredNotification,
 notificationTypes['notificationTypeAllAnchoringMsg']: FormatAllAnchoringNotification,
 notificationTypes['notificationTypeAllStructVulnerableMsg']: FormatAllStructVulnerableNotification,
 notificationTypes['notificationTypeAllStrucInvulnerableMsg']: FormatAllStrucInvulnerableNotification,
 notificationTypes['notificationTypeSovDisruptorMsg']: FormatSovDisruptorNotification,
 notificationTypes['notificationTypeCorpStructLostMsg']: FormatCorpStructLostNotification,
 notificationTypes['notificationTypeCorpOfficeExpirationMsg']: FormatCorpOfficeExpirationNotification,
 notificationTypes['notificationTypeCloneRevokedMsg1']: FormatCloneRevoked1Notification,
 notificationTypes['notificationTypeCloneMovedMsg']: FormatCloneMovedNotification,
 notificationTypes['notificationTypeCloneRevokedMsg2']: FormatCloneRevoked2Notification,
 notificationTypes['notificationTypeInsuranceExpirationMsg']: FormatInsuranceExpirationNotification,
 notificationTypes['notificationTypeInsuranceIssuedMsg']: FormatInsuranceIssuedNotification,
 notificationTypes['notificationTypeJumpCloneDeletedMsg1']: FormatJumpCloneDeleted1Notification,
 notificationTypes['notificationTypeJumpCloneDeletedMsg2']: FormatJumpCloneDeleted2Notification,
 notificationTypes['notificationTypeFWCorpJoinMsg']: FormatFWCorpJoinNotification,
 notificationTypes['notificationTypeFWCorpLeaveMsg']: FormatFWCorpLeaveNotification,
 notificationTypes['notificationTypeFWCorpKickMsg']: FormatFWCorpKickNotification,
 notificationTypes['notificationTypeFWCharKickMsg']: FormatFWCharKickNotification,
 notificationTypes['notificationTypeFWCorpWarningMsg']: FormatFWCorpWarningNotification,
 notificationTypes['notificationTypeFWCharWarningMsg']: FormatFWCharWarningNotification,
 notificationTypes['notificationTypeFWCharRankLossMsg']: FormatFWCharRankLossNotification,
 notificationTypes['notificationTypeFWCharRankGainMsg']: FormatFWCharRankGainNotification,
 notificationTypes['notificationTypeAgentMoveMsg']: FormatAgentMoveNotification,
 notificationTypes['notificationTypeTransactionReversalMsg']: FormatTransactionReversalNotification,
 notificationTypes['notificationTypeReimbursementMsg']: FormatReimbursementNotification,
 notificationTypes['notificationTypeLocateCharMsg']: FormatLocateCharNotification,
 notificationTypes['notificationTypeResearchMissionAvailableMsg']: FormatResearchMissionAvailableNotification,
 notificationTypes['notificationTypeMissionOfferExpirationMsg']: FormatMissionOfferExpirationNotification,
 notificationTypes['notificationTypeMissionTimeoutMsg']: FormatMissionTimeoutNotification,
 notificationTypes['notificationTypeStoryLineMissionAvailableMsg']: FormatStoryLineMissionAvailableNotification,
 notificationTypes['notificationTypeTowerAlertMsg']: FormatTowerAlertNotification,
 notificationTypes['notificationTypeTowerResourceAlertMsg']: FormatTowerResourceAlertNotification,
 notificationTypes['notificationTypeStationAggressionMsg1']: FormatStationAggression1Notification,
 notificationTypes['notificationTypeStationStateChangeMsg']: FormatStationStateChangeNotification,
 notificationTypes['notificationTypeStationConquerMsg']: FormatStationConquerNotification,
 notificationTypes['notificationTypeStationAggressionMsg2']: FormatStationAggression2Notification,
 notificationTypes['notificationTypeFacWarCorpJoinRequestMsg']: FormatFacWarCorpJoinRequestNotification,
 notificationTypes['notificationTypeFacWarCorpLeaveRequestMsg']: FormatFacWarCorpLeaveRequestNotification,
 notificationTypes['notificationTypeFacWarCorpJoinWithdrawMsg']: FormatFacWarCorpJoinWithdrawNotification,
 notificationTypes['notificationTypeFacWarCorpLeaveWithdrawMsg']: FormatFacWarCorpLeaveWithdrawNotification,
 notificationTypes['notificationTypeSovereigntyTCUDamageMsg']: FormatSovTCUDamagedNotification,
 notificationTypes['notificationTypeSovereigntySBUDamageMsg']: FormatSovSBUDamagedNotification,
 notificationTypes['notificationTypeSovereigntyIHDamageMsg']: FormatSovIHDamagedNotification,
 notificationTypes['notificationTypeContactAdd']: FormatContactAddNotification,
 notificationTypes['notificationTypeContactEdit']: FormatContactEditNotification,
 notificationTypes['notificationTypeIncursionCompletedMsg']: FormatIncursionCompletedNotification,
 notificationTypes['notificationTypeTutorialMsg']: FormatTutorialNotification}

def Format(notification):
    if notification.typeID in formatters:
        try:
            if type(notification.data) in types.StringTypes:
                notification.data = yaml.load(notification.data, Loader=yaml.CSafeLoader)
            (subject, body,) = formatters[notification.typeID](notification)
        except Exception as e:
            log.LogException('Error processing notification=%s, error=%s' % (str(notification), e))
            sys.exc_clear()
            subject = mls.NOTIFICATION_BAD_FORMAT_SUBJECT
            body = mls.NOTIFICATION_BAD_FORMAT_BODY % {'id': notification.notificationID}
        return (subject, body)
    else:
        log.LogException('No formatter found for typeID=%s' % notification.typeID)
        subject = mls.NOTIFICATION_BAD_FORMAT_SUBJECT
        body = mls.NOTIFICATION_BAD_FORMAT_BODY % {'id': notification.notificationID}
        return (subject, body)


exports = util.AutoExports('const', notificationTypes)
exports['notificationUtil.GetTypeGroup'] = GetTypeGroup
exports['notificationUtil.Format'] = Format
exports['notificationUtil.groupTypes'] = groupTypes
exports['notificationUtil.groupNames'] = groupNames
exports['notificationUtil.events'] = events
exports['const.notificationGroupUnread'] = groupUnread
exports['const.groupContacts'] = groupContacts

