import zaction
import perception

def GetAITargetList(propRow):
    retList = []
    for target in const.aiming.AIMING_VALID_TARGETS.values():
        name = target[const.aiming.AIMING_VALID_TARGETS_FIELD_NAME]
        clientServerFlag = target[const.aiming.AIMING_VALID_TARGETS_FIELD_CLIENTSERVER_FLAG]
        if clientServerFlag != const.aiming.AIMING_CLIENTSERVER_FLAG_BOTH:
            name = name + const.aiming.AIMING_CLIENTSERVER_FLAGS[clientServerFlag]
        retList.append((name, target[const.aiming.AIMING_VALID_TARGETS_FIELD_ID], ''))

    return retList


exports = {'actionProperties.AITarget': ('listMethod', GetAITargetList),
 'actionProcTypes.TargetSelect': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='Set Target'),
                                  zaction.ProcPropertyTypeDef('Candidate', 'I', userDataType='AICandidate', isPrivate=True, displayName='From Candidate List'),
                                  zaction.ProcPropertyTypeDef('Subject', 'I', userDataType='AISubject', isPrivate=True, displayName='Where Subject is'),
                                  zaction.ProcPropertyTypeDef('Confidence', 'I', userDataType='AIConfidence', isPrivate=True, displayName='If Confidence >='),
                                  zaction.ProcPropertyTypeDef('ConfidenceWeight', 'B', userDataType=None, isPrivate=True, displayName='Confidence weighting'),
                                  zaction.ProcPropertyTypeDef('DistanceNearest', 'B', userDataType=None, isPrivate=True, displayName='Pick Nearest'),
                                  zaction.ProcPropertyTypeDef('DistanceMin', 'F', userDataType=None, isPrivate=True, displayName='Minimum distance'),
                                  zaction.ProcPropertyTypeDef('DistanceOptimal', 'F', userDataType=None, isPrivate=True, displayName='Optimal distance'),
                                  zaction.ProcPropertyTypeDef('DistanceMax', 'F', userDataType=None, isPrivate=True, displayName='Maximum distance')]),
 'actionProcTypes.TargetSelectable': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='Set Target'),
                                      zaction.ProcPropertyTypeDef('Candidate', 'I', userDataType='AICandidate', isPrivate=True, displayName='From Candidate List'),
                                      zaction.ProcPropertyTypeDef('Subject', 'I', userDataType='AISubject', isPrivate=True, displayName='Where Subject is'),
                                      zaction.ProcPropertyTypeDef('Confidence', 'I', userDataType='AIConfidence', isPrivate=True, displayName='If Confidence >='),
                                      zaction.ProcPropertyTypeDef('ConfidenceWeight', 'B', userDataType=None, isPrivate=True, displayName='Confidence weighting'),
                                      zaction.ProcPropertyTypeDef('DistanceNearest', 'B', userDataType=None, isPrivate=True, displayName='Pick Nearest'),
                                      zaction.ProcPropertyTypeDef('DistanceMin', 'F', userDataType=None, isPrivate=True, displayName='Minimum distance'),
                                      zaction.ProcPropertyTypeDef('DistanceOptimal', 'F', userDataType=None, isPrivate=True, displayName='Optimal distance'),
                                      zaction.ProcPropertyTypeDef('DistanceMax', 'F', userDataType=None, isPrivate=True, displayName='Maximum distance')]),
 'actionProcTypes.TargetClear': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)]),
 'actionProcTypes.TargetPreventSelect': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True), zaction.ProcPropertyTypeDef('Time', 'F', userDataType=None, isPrivate=True, displayName='Time in secs')]),
 'actionProcTypes.TargetIsSelected': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)]),
 'actionProcTypes.TargetPreventListClearAll': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)]),
 'actionProcTypes.TargetSelectedEntity': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)])}

