#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/view/characterCustomizationView.py
from viewstate import View
import uicls
from sceneManager import SCENE_TYPE_CHARACTER_CREATION
import localization

class CharacterCustomizationView(View):
    __guid__ = 'viewstate.CharacterCustomizationView'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = uicls.CharacterCreationLayer
    __suppressedOverlays__ = {'sidePanels'}
    __dependencies__ = View.__dependencies__[:]
    __dependencies__.extend(['entityClient', 'cameraClient', 'gameui'])

    def __init__(self):
        View.__init__(self)

    def LoadView(self, charID = None, gender = None, dollState = None, bloodlineID = None, **kwargs):
        View.LoadView(self)
        self.LogInfo('Opening character creator with arguments', kwargs)
        if charID is not None:
            if session.worldspaceid == session.stationid2:
                player = self.entityClient.GetPlayerEntity()
                if player is not None:
                    pos = player.GetComponent('position')
                    if pos is not None:
                        self.cachedPlayerPos = pos.position
                        self.cachedPlayerRot = pos.rotation
                camera = self.cameraClient.GetActiveCamera()
                if camera is not None:
                    self.cachedCameraYaw = camera.yaw
                    self.cachedCameraPitch = camera.pitch
                    self.cachedCameraZoom = camera.zoom
            change = {'worldspaceid': [session.worldspaceid, None]}
            self.entityClient.ProcessSessionChange(False, session, change)
            self.gameui.OnSessionChanged(False, session, change)
        factory = sm.GetService('character').factory
        factory.compressTextures = False
        factory.allowTextureCache = False
        clothSimulation = sm.GetService('device').GetAppFeatureState('CharacterCreation.clothSimulation', True)
        factory.clothSimulationActive = clothSimulation
        sm.GetService('sceneManager').SetSceneType(SCENE_TYPE_CHARACTER_CREATION)
        self.layer.SetCharDetails(charID, gender, bloodlineID, dollState=dollState)
        uicore.layer.main.display = False

    def UnloadView(self):
        View.UnloadView(self)
        uicore.layer.main.display = True

    def GetProgressText(self, **kwargs):
        if kwargs.get('charID', None) is not None:
            text = localization.GetByLabel('UI/CharacterCustomization/EnteringCharacterCustomization')
        else:
            text = localization.GetByLabel('UI/CharacterCreation/EnteringCharacterCreation')
        return text