#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/view/planetView.py
from viewstate import View
import uicls
import uiconst
import moniker
import uthread

class PlanetView(View):
    __guid__ = 'viewstate.PlanetView'
    __notifyevents__ = ['OnUIRefresh']
    __dependencies__ = []
    __layerClass__ = uicls.PlanetLayer
    __suppressedOverlays__ = {'shipui', 'target'}

    def CanEnter(self, planetID = None, **kwargs):
        canEnter = True
        if planetID is None:
            self.LogInfo('Must have a valid planetID to open planet view')
            canEnter = False
        elif self.IsActive() and planetID == sm.GetService('planerUI').planetID:
            self.LogInfo('Planet', planetID, 'is already open and loaded')
            canEnter = False
        if canEnter:
            try:
                remoteHandler = moniker.GetPlanet(planetID)
                remoteHandler.GetPlanetInfo()
            except UserError as e:
                eve.Message(*e.args)
                canEnter = False

        return canEnter

    def CanExit(self):
        currentPlanet = sm.GetService('planetUI').GetCurrentPlanet()
        if currentPlanet and currentPlanet.IsInEditMode():
            if eve.Message('ExitPlanetModeWhileInEditMode', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
            currentPlanet.RevertChanges()
        return True

    def LoadView(self, planetID = None, **kwargs):
        planetUI = sm.GetService('planetUI')
        if self.IsActive():
            planetUI.Close(clearAll=False)
        planetUI._Open(planetID)
        if session.stationid2 is not None:
            player = sm.GetService('entityClient').GetPlayerEntity()
            if player is not None:
                pos = player.GetComponent('position')
                if pos is not None:
                    self.cachedPlayerPos = pos.position
                    self.cachedPlayerRot = pos.rotation
            camera = sm.GetService('cameraClient').GetActiveCamera()
            if camera is not None:
                self.cachedCameraYaw = camera.yaw
                self.cachedCameraPitch = camera.pitch
                self.cachedCameraZoom = camera.zoom
        self.lastPlanetID = planetID

    def UnloadView(self):
        planetUI = sm.GetService('planetUI')
        planetUI.Close()

    def OnUIRefresh(self):
        uthread.new(self._ReOpen)

    def _ReOpen(self):
        viewState = sm.GetService('viewState')
        viewState.CloseSecondaryView('planet')
        planetID = getattr(self, 'lastPlanetID', None)
        viewState.ActivateView('planet', planetID=planetID)