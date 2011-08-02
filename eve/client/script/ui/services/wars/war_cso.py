from service import Service, SERVICE_START_PENDING, SERVICE_RUNNING
import blue
import uthread
import moniker
import warObject
import log
import sys

def ReturnNone():
    return None



class Wars(Service):
    __exportedcalls__ = {'GetWars': [],
     'GetRelationship': [],
     'AreInAnyHostileWarStates': [],
     'GetCostOfWarAgainst': []}
    __guid__ = 'svc.war'
    __notifyevents__ = ['DoSessionChanging', 'OnWarChanged']
    __servicename__ = 'war'
    __displayname__ = 'War Client Service'
    __dependencies__ = []
    __functionalobjects__ = ['wars']

    def __init__(self):
        Service.__init__(self)



    def GetDependencies(self):
        return self.__dependencies__



    def GetObjectNames(self):
        return self.__functionalobjects__



    def Run(self, memStream = None):
        self.LogInfo('Starting War')
        self.state = SERVICE_START_PENDING
        self._Wars__warMoniker = None
        self._Wars__warMonikerOwnerID = None
        items = warObject.__dict__.items()
        for objectName in self.__functionalobjects__:
            if objectName == 'base':
                continue
            object = None
            classType = 'warObject.%s' % objectName
            for i in range(0, len(warObject.__dict__)):
                self.LogInfo('Processing', items[i])
                if len(items[i][0]) > 1:
                    if items[i][0][:2] == '__':
                        continue
                if items[i][1].__guid__ == classType:
                    object = CreateInstance(classType, (self,))
                    break

            if object is None:
                raise RuntimeError('FunctionalObject not found %s' % classType)
            setattr(self, objectName, object)

        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            object.DoObjectWeakRefConnections()

        self.state = SERVICE_RUNNING
        uthread.new(self.CheckForStartOrEndOfWar)



    def Stop(self, memStream = None):
        self._Wars__warMoniker = None
        self._Wars__warMonikerOwnerID = None



    def DoSessionChanging(self, isRemote, session, change):
        try:
            if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
                sm.StopService(self.__guid__[4:])
        except:
            log.LogException()
            sys.exc_clear()



    def RefreshMoniker(self):
        if self._Wars__warMoniker is not None:
            self._Wars__warMoniker.UnBind()



    def GetMoniker(self):
        if self._Wars__warMoniker is None:
            self._Wars__warMoniker = moniker.GetWar()
            self._Wars__warMonikerOwnerID = eve.session.allianceid or eve.session.corpid
        if self._Wars__warMonikerOwnerID != (eve.session.allianceid or eve.session.corpid):
            if self._Wars__warMoniker is not None:
                self._Wars__warMoniker.Unbind()
            self._Wars__warMoniker = moniker.GetWar()
            self._Wars__warMonikerOwnerID = eve.session.allianceid or eve.session.corpid
        return self._Wars__warMoniker



    def OnWarChanged(self, warID, declaredByID, againstID, change):
        try:
            self.LogInfo('OnWarChanged warID:', warID, 'declaredByID:', declaredByID, 'againstID:', againstID, 'change:', change)
            self.wars.OnWarChanged(warID, declaredByID, againstID, change)
        except:
            log.LogException()
            sys.exc_clear()



    def GetWars(self, ownerID, forceRefresh = 0):
        return self.wars.GetWars(ownerID, forceRefresh)



    def GetRelationship(self, ownerIDaskingAbout):
        return self.wars.GetRelationship(ownerIDaskingAbout)



    def AreInAnyHostileWarStates(self, ownerID):
        return self.wars.AreInAnyHostileWarStates(ownerID)



    def GetCostOfWarAgainst(self, ownerID):
        return self.wars.GetCostOfWarAgainst(ownerID)



    def CheckForStartOrEndOfWar(self):
        while self.state == SERVICE_RUNNING:
            if not session.charid:
                blue.pyos.synchro.Sleep(10000)
                continue
            try:
                self.wars.CheckForStartOrEndOfWar()
            except Exception:
                log.LogException()
                sys.exc_clear()
            blue.pyos.synchro.Sleep(10000)





