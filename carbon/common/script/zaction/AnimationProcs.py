import actionProperties
import batma
import blue
import yaml
import zaction
animInfoDict = None

def GetAnimInfo():
    global animInfoDict
    if animInfoDict is None:
        dataFile = blue.ResFile()
        dataFile.Open('res:/Animation/animInfo.yaml')
        animInfoDict = yaml.load(dataFile)
        dataFile.close()
    return animInfoDict



def GetAnimPropertyByName(animName, propertyName):
    animInfo = GetAnimInfo()
    anim = animInfo.get(animName, None)
    if anim is not None:
        return anim.get(propertyName, None)



def _AnimationProcNameHelper(name, procRow):
    propDict = actionProperties.GetPropertyValueDict(procRow)
    animName = propDict.get('AnimName', 'None')
    duration = GetAnimPropertyByName(animName, 'duration')
    if duration is None:
        duration = 0.0
    displayName = 'PerformAnim ' + animName + ' for ' + str(duration) + ' sec'
    return displayName



def AnimationProcNameHelper(name):
    return lambda procRow: _AnimationProcNameHelper(name, procRow)



def GetControlParameters(propRow):
    validList = ['HeadLookWeight',
     'HeadBlendSpeed',
     'Aim_X',
     'Aim_Y',
     'AllowFidgets']
    retList = []
    for param in validList:
        retList.append((param, param, ''))

    retList.sort()
    return retList


exports = {'actionProperties.ControlParameters': ('listMethod', GetControlParameters),
 'actionProcTypes.OrAllCondition': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Condition', displayName=' Or All', properties=[zaction.ProcPropertyTypeDef('NegateAll', 'B', isPrivate=True, default=False)], description="Conditional procs can be used to modify the result of a conditional step or prereq container. Only a single Conditional proc will be respected, so don't use more than one. \n\nOr All: For all procs in this ProcContainer, evaluate to True if any of them returns True.\nThe Negate All option will cause this to evaluate True if any of them returns False."),
 'actionProcTypes.AndAllCondition': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Condition', displayName=' And All', properties=[zaction.ProcPropertyTypeDef('NegateAll', 'B', isPrivate=True, default=False)], description="Conditional procs can be used to modify the result of a conditional step or prereq container. Only a single Conditional proc will be respected, so don't use more than one. \n\nAnd All: For all procs in this ProcContainer, evaluate to True if all of them return True. This is the default behavior for ProcContainers so... you may not even need this unless you use...\nThe Negate All option will cause this to evaluate True if all of them return False."),
 'actionProcTypes.NotCondition': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Condition', displayName=' Not', properties=[], description="Conditional procs can be used to modify the result of a conditional step or prereq container. Only a single Conditional proc will be respected, so don't use more than one. \n\nNot: For all procs in this ProcContainer, evaluate to True if all of them return False. "),
 'actionProcTypes.XorCondition': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Condition', displayName=' Xor', properties=[zaction.ProcPropertyTypeDef('NegateAll', 'B', isPrivate=True, default=False)], description="Conditional procs can be used to modify the result of a conditional step or prereq container. Only a single Conditional proc will be respected, so don't use more than one. \n\nXor: For all procs in this ProcContainer, evaluate to True if exactly one of them is True.\nThe Negate All option will cause this to evaluate True if not exactly one is True."),
 'actionProcTypes.ComplexCondition': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Condition', displayName=' Complex Condition %(ConditionEvalString)s', properties=[zaction.ProcPropertyTypeDef('ConditionEvalString', 'S', isPrivate=True)], description="Conditional procs can be used to modify the result of a conditional step or prereq container. Only a single Conditional proc will be respected, so don't use more than one. \n\nComplex: The ConditionEvalString is a reverse polish notation string with ,&|! as delimiters. Specific procs are referenced by their proc IDs.\n\nFor example, if you want the condition to evaluate true if Proc 4 and Proc 11 are True or Proc 8  is False, then you would use the EvalString:\n4,11&8!|\n\nYes, we realize this is fugly, but until enough people are even using it that it matters, it's not really in the schedule to make the user interface for this especially usable."),
 'actionProcTypes.ChangeAction': zaction.ProcTypeDef(isMaster=True, procCategory='Action', displayName=zaction.ProcNameHelper('ChangeAction to %(NewAction)s'), properties=[zaction.ProcPropertyTypeDef('NewAction', 'I', userDataType='ActionChildrenAndSiblingsList', isPrivate=True)], description='Attempt to transition from the current action on this tree instance to another action in thesame tree. This requires valid availability on the action tree.\n\nThis will not allow you to begin actions on other trees. IE, buffs cannot start decision actions'),
 'actionProcTypes.ExitAction': zaction.ProcTypeDef(isMaster=True, procCategory='Action', properties=[], description='Clear the current actions step stack causing this action to finish upon completion of the step.'),
 'actionProcTypes.LogMessage': zaction.ProcTypeDef(isMaster=True, procCategory='General', properties=[zaction.ProcPropertyTypeDef('LogCategory', 'I', userDataType='LogCategory', isPrivate=True), zaction.ProcPropertyTypeDef('LogMessage', 'S', isPrivate=True)], description='Output a message to the log server.'),
 'actionProcTypes.WaitForTime': zaction.ProcTypeDef(isMaster=True, procCategory='General', properties=[zaction.ProcPropertyTypeDef('Duration', 'F', isPrivate=True)], description='Hold the current step open for a fixed amount of time.'),
 'actionProcTypes.CooldownForTime': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='General', properties=[zaction.ProcPropertyTypeDef('Duration', 'F', isPrivate=True)]),
 'actionProcTypes.CreateProperty': zaction.ProcTypeDef(isMaster=False, isConditional=False, procCategory='General', properties=[zaction.ProcPropertyTypeDef('CreateName', 'S', isPrivate=True), zaction.ProcPropertyTypeDef('CreateType', 'S', userDataType='PropertyType', isPrivate=True), zaction.ProcPropertyTypeDef('CreateValue', 'S', isPrivate=True)], description='Create a public property in the Action PropertyList.'),
 'actionProcTypes.WaitForever': zaction.ProcTypeDef(isMaster=True, procCategory='General', description='Hold the current step open forever. Note that this should only ever be used within a try block.'),
 'actionProcTypes.LogPropertyList': zaction.ProcTypeDef(isMaster=True, procCategory='General', description='Output the entire contents of the current actions property list to the log server. Spammy.'),
 'actionProcTypes.HasTargetList': zaction.ProcTypeDef(isMaster=True, procCategory='Target', isConditional=True, description='Returns True if the target list contains at least a single target.'),
 'actionProcTypes.StartTargetAction': zaction.ProcTypeDef(isMaster=True, procCategory='Action', properties=[zaction.ProcPropertyTypeDef('TargetAction', 'I', userDataType='ActionList', isPrivate=False)], description='Starts an action in the action tree on the first entity in the target list.\n\nUseful for syncing actions.'),
 'actionProcTypes.HasLockedTarget': zaction.ProcTypeDef(isMaster=True, procCategory='Target', isConditional=True, description='Returns true if a synced action has set a locked target.\n\nUseful for syncing actions.'),
 'actionProcTypes.UseLockedTarget': zaction.ProcTypeDef(isMaster=True, procCategory='Target', description='Takes the current locked target it and places it in the TargetList property\n\nUseful for syncing actions.'),
 'actionProcTypes.CanTargetStartAction': zaction.ProcTypeDef(isMaster=True, procCategory='Action', isConditional=True, properties=[zaction.ProcPropertyTypeDef('TargetAction', 'I', userDataType='ActionList', isPrivate=False)], description='Returns true if the target entity can validly request the specified action.\n\nUseful for syncing actions.'),
 'actionProcTypes.CanLockedTargetStartAction': zaction.ProcTypeDef(isMaster=True, procCategory='Action', isConditional=True, properties=[zaction.ProcPropertyTypeDef('TargetAction', 'I', userDataType='ActionList', isPrivate=False)], description='Returns true if the locked target can validly request the specified action.\n\nUseful for syncing actions.'),
 'actionProcTypes.PerformAnim': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', displayName=AnimationProcNameHelper('%(AnimName)s'), properties=[zaction.ProcPropertyTypeDef('AnimName', 'S', userDataType='AnimationListDialogWrapper', isPrivate=True)], description='Will attempt to perform the specified animation request as defined in the animInfo.yaml'),
 'actionProcTypes.SetPose': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', displayName='SetPose %(AnimName)s', properties=[zaction.ProcPropertyTypeDef('AnimName', 'S', userDataType=None, isPrivate=True)]),
 'actionProcTypes.PerformSyncAnim': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', displayName='PerformSyncAnim %(AnimName)s', properties=[zaction.ProcPropertyTypeDef('AnimName', 'S', userDataType=None, isPrivate=True)]),
 'actionProcTypes.FaceTarget': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', description="Causes the current entity to turn and face it's target."),
 'actionProcTypes.IsFacingTarget': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', isConditional=True, properties=[zaction.ProcPropertyTypeDef('TargetFacingAngle', 'F', isPrivate=True)], description="Returns true if the current entity is facing it's target."),
 'actionProcTypes.SetSyncAnimEntry': zaction.ProcTypeDef(isMaster=False, procCategory='Animation', displayName='SetSyncAnimEntry %(AnimName)s', properties=[zaction.ProcPropertyTypeDef('AnimName', 'S', userDataType=None, isPrivate=True)]),
 'actionProcTypes.GetEntryFromAttacker': zaction.ProcTypeDef(isMaster=False, procCategory='Animation'),
 'actionProcTypes.IsEntityInRange': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='Animation', properties=[zaction.ProcPropertyTypeDef('Range', 'F', userDataType=None, isPrivate=True)], description='Returns true if the target entity is within the specified range.'),
 'actionProcTypes.SlaveMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', properties=[zaction.ProcPropertyTypeDef('BoneName', 'S', userDataType=None, isPrivate=True)]),
 'actionProcTypes.AlignToMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation'),
 'actionProcTypes.PathToMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', properties=[zaction.ProcPropertyTypeDef('PathDistance', 'F', userDataType=None, isPrivate=True)], description='Paths the requesting entity to within the specified distance of the ALIGN_POS.'),
 'actionProcTypes.WanderMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation', properties=[]),
 'actionProcTypes.RestoreMoveMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation'),
 'actionProcTypes.RestoreTargetMoveMode': zaction.ProcTypeDef(isMaster=True, procCategory='Animation'),
 'actionProcTypes.SetControlParameter': zaction.ProcTypeDef(isMaster=False, procCategory='Animation', properties=[zaction.ProcPropertyTypeDef('Parameter', 'S', userDataType='ControlParameters', isPrivate=True), zaction.ProcPropertyTypeDef('Value', 'F', userDataType=None, isPrivate=True)])}

