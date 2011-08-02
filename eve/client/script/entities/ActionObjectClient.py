import svc
import uthread
import util
import random
import uiconst

class EveActionObjectClientSvc(svc.actionObjectClientSvc):
    __guid__ = 'svc.eveActionObjectClientSvc'
    __replaceservice__ = 'actionObjectClientSvc'
    __startupdependencies__ = ['cmd']

    def SetupComponent(self, entity, component):
        infoComponent = entity.GetComponent('info')
        if infoComponent and not infoComponent.name and component in self.preservedStates:
            typeData = cfg.invtypes.Get(self.preservedStates[component]['_typeID'])
            infoComponent.name = typeData.name
        svc.actionObjectClientSvc.SetupComponent(self, entity, component)



    def Run(self, *args):
        svc.actionObjectClientSvc.Run(self, *args)
        self.UICallbackDict = {None: self._NoneKeyIsInvalid_Callback,
         'OpenCharacterCustomization': self._EveActionObjectClientSvc__OpenCharacterCustomization_Callback,
         'CorpRecruitment': self._CorpRecruitment_Callback,
         'OpenCorporationPanel_Planets': self._OpenCorporationPanel_Planets_Callback,
         'OpenAuraInteraction': self.cmd.OpenAuraInteraction,
         'ExitStation': self.cmd.CmdExitStation,
         'OpenFitting': self.cmd.OpenFitting,
         'OpenShipHangar': self.cmd.OpenShipHangar,
         'OpenCargoBay': self.cmd.OpenCargoHoldOfActiveShip,
         'OpenDroneBay': self.cmd.OpenDroneBayOfActiveShip,
         'OpenMarket': self.cmd.OpenMarket,
         'OpenAgentFinder': self.cmd.OpenAgentFinder,
         'OpenStationDoor': self._EveActionObjectClientSvc__OpenStationDoor_Callback}



    def _PerformUICallback(self, callbackKey):
        callback = self.UICallbackDict.get(callbackKey, None)
        if callback is not None:
            uthread.worker('_PerformUICallback_%s' % callbackKey, self._PerformUICallbackTasklet, callbackKey, callback)
            return True
        self.LogError('ActionObject.PerformUICallback: Unknown callbackKey', callbackKey)
        return False



    def _PerformUICallbackTasklet(self, callbackKey, callback):
        try:
            callback()
        except TypeError as e:
            self.LogError('ActionObject.PerformUICallback: callbackKey "%s" is associated with a non-callable object: %s' % (callbackKey, callback), e)



    def _NoneKeyIsInvalid_Callback(self):
        self.LogError('PerformUICallback called from ActionObject without the callbackKey property (it was None)!')



    def _CorpRecruitment_Callback(self):
        if util.IsNPC(session.corpid):
            self.cmd.OpenCorporationPanel_RecruitmentPane()
        else:
            self.cmd.OpenCorporationPanel()



    def _OpenCorporationPanel_Planets_Callback(self):
        if sm.GetService('planetSvc').GetMyPlanets():
            self.cmd.OpenCorporationPanel_Planets()
        else:
            systemData = sm.RemoteSvc('config').GetMapObjects(session.solarsystemid2, 0, 0, 0, 1, 0)
            systemPlanets = []
            for orbitalBody in systemData:
                if orbitalBody.groupID == const.groupPlanet:
                    systemPlanets.append(orbitalBody)

            planetID = systemPlanets[random.randrange(0, len(systemPlanets))].itemID
            sm.GetService('planetUI').Open(planetID)
            if not settings.user.suppress.Get('suppress.PI_Info', None):
                (ret, supp,) = sm.GetService('gameui').MessageBox(mls.UI_PI_INTRO_TEXT, title=mls.UI_GENERIC_INFORMATION, buttons=uiconst.OK, modal=False, icon=uiconst.INFO, suppText=mls.UI_SHARED_SUPPRESS1)
                if supp:
                    settings.user.suppress.Set('suppress.PI_Info', supp)



    def __OpenStationDoor_Callback(self):
        uicore.Message('CaptainsQuartersStationDoorClosed')



    def __OpenCharacterCustomization_Callback(self):
        if getattr(sm.GetService('map'), 'busy', False):
            return 
        if uicore.Message('EnterCharacterCustomizationCQ', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            self.cmd.OpenCharacterCustomization()



    def GetActionNodeTranslatedText(self, actionID, fallbackText):
        dataID = cfg.treeNodes.Get(actionID).dataID
        return Tr(fallbackText, 'ztree.nodes.treeNodeName', dataID)




