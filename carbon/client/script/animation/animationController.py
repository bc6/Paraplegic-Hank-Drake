import log
INVALID_TRACK_ID = -1

class AnimationController(object):
    __guid__ = 'animation.AnimationController'

    def __init__(self, animationNetwork):
        self.animationNetwork = animationNetwork
        self.entityRef = None
        self.controlParameterIDs = self.animationNetwork.GetAllControlParameters()
        self.controlParameterValues = {}
        self.requestIDs = self.animationNetwork.GetAllRequestIDs()
        self.eventTrackIDs = self.animationNetwork.GetAllEventTrackIDs()
        self.eventTrackNames = {}
        self.targetController = None
        self.behaviors = []
        self._MapEventTrackNames()
        self._MapControlParameterValues()
        self.Run()



    def Run(self):
        pass



    def Reset(self):
        pass



    def Stop(self, stream):
        pass



    def _MapEventTrackNames(self):
        for (name, id,) in self.eventTrackIDs.iteritems():
            self.eventTrackNames[id] = name




    def _MapControlParameterValues(self):
        for (name, id,) in self.controlParameterIDs.iteritems():
            self.controlParameterValues[id] = self.animationNetwork.GetControlParameterValueByID(id)




    def GetEventTrackID(self, trackName):
        return self.eventTrackIDs.get(trackName)



    def GetEventTrackName(self, trackID):
        trackName = self.eventTrackNames.get(trackID, 'Unknown')
        return trackName



    def GetEventTrackIDs(self):
        return self.eventTrackIDs



    def SetControlParameter(self, name, args):
        cpID = None
        name = 'ControlParameters|' + name
        if name not in self.controlParameterIDs:
            log.LogError('Attempting to set a value to an invalid control parameter %s!' % name)
            return 
        cpID = self.controlParameterIDs[name]
        if self.controlParameterValues[cpID] != args and self.animationNetwork is not None:
            self.controlParameterValues[cpID] = args
            self.animationNetwork.SetControlParameterByID(cpID, args)



    def GetControlParameter(self, name, forceLookup = False):
        name = 'ControlParameters|' + name
        cpID = self.controlParameterIDs.get(name)
        value = self.controlParameterValues.get(cpID)
        if value is not None:
            return value
        self.controlParameterValues[id] = self.animationNetwork.GetControlParameterValueByID(cpID)
        log.LogError('Attempted to get a control parameter value %s, but it does not exist!' % name)



    def GetAllControlParameterValues(self, force = False):
        if force is True:
            self._MapControlParameterValues()
        return self.controlParameterValues



    def GetAllControlParameterValuesByName(self, force = False):
        if force is True:
            self._MapControlParameterValues()
        nameDict = {}
        for (name, id,) in self.controlParameterIDs.iteritems():
            nameDict[name.split('|')[1]] = self.controlParameterValues[id]

        return nameDict



    def BroadcastRequest(self, name):
        if self.animationNetwork is not None:
            bcID = self.requestIDs.get(name, None)
            if bcID:
                self.animationNetwork.BroadcastRequestByID(bcID)
            else:
                log.LogError('Attempted to broadcast the %s request, but it does not exist!' % name)



    def SetTargetController(self, animationController):
        self.targetController = animationController



    def GetTargetController(self):
        return self.targetController



    def _UpdateHook(self):
        pass



    def _UpdateTargetHook(self):
        pass



    def _UpdateNoTargetHook(self):
        pass



    def Update(self):
        if self.animationNetwork is not None:
            self._UpdateHook()
            if self.targetController is not None:
                self._UpdateTargetHook()
            else:
                self._UpdateNoTargetHook()
            for (priority, behavior,) in self.behaviors:
                behavior.Update(self)




    def AddBehavior(self, behavior, priority = 100):
        self.behaviors.append((priority, behavior))
        self.behaviors.sort()
        behavior.OnAdd(self)



    def RemoveBehavior(self, behavior):
        toRemove = None
        for (priority, myBehavior,) in self.behaviors:
            if myBehavior == behavior:
                toRemove = (priority, myBehavior)
                break

        if toRemove is not None:
            self.behaviors.remove(toRemove)



    def ResetBehaviors(self):
        for (priority, behavior,) in self.behaviors:
            behavior.Reset()




    def SetEntityRef(self, ent):
        self.entityRef = ent
        self._UpdateEntityInfo()



    def _UpdateEntityInfo(self):
        pass




