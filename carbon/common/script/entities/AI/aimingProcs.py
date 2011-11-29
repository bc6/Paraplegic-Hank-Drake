import zaction
import perception
import batma

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
                                  zaction.ProcPropertyTypeDef('Tags', 'S', userDataType=None, isPrivate=True, displayName='Tags')], description='Select a target if possible.'),
 'actionProcTypes.TargetSelectable': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='Set Target'),
                                      zaction.ProcPropertyTypeDef('Candidate', 'I', userDataType='AICandidate', isPrivate=True, displayName='From Candidate List'),
                                      zaction.ProcPropertyTypeDef('Subject', 'I', userDataType='AISubject', isPrivate=True, displayName='Where Subject is'),
                                      zaction.ProcPropertyTypeDef('Confidence', 'I', userDataType='AIConfidence', isPrivate=True, displayName='If Confidence >='),
                                      zaction.ProcPropertyTypeDef('ConfidenceWeight', 'B', userDataType=None, isPrivate=True, displayName='Confidence weighting'),
                                      zaction.ProcPropertyTypeDef('DistanceNearest', 'B', userDataType=None, isPrivate=True, displayName='Pick Nearest'),
                                      zaction.ProcPropertyTypeDef('DistanceMin', 'F', userDataType=None, isPrivate=True, displayName='Minimum distance'),
                                      zaction.ProcPropertyTypeDef('DistanceOptimal', 'F', userDataType=None, isPrivate=True, displayName='Optimal distance'),
                                      zaction.ProcPropertyTypeDef('Tags', 'S', userDataType=None, isPrivate=True, displayName='Tags')], description='Test if a target would be selected. No target is selected'),
 'actionProcTypes.TargetClear': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)], description='Clears the target'),
 'actionProcTypes.TargetPreventSelect': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True), zaction.ProcPropertyTypeDef('Time', 'F', userDataType=None, isPrivate=True, displayName='Time in secs')], description='Prevents re-selection of the current target for a period of time'),
 'actionProcTypes.TargetIsSelected': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)], description='Do we have a target'),
 'actionProcTypes.TargetPreventListClearAll': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)], description='Clear the prevent selection list'),
 'actionProcTypes.TargetSelectedEntity': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True)], description="Target the player's selected entity. Used by head tracking"),
 'actionProcTypes.TargetSelectFromHate': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='Set Target')], description='Select a target from the hate list.')}

