#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/dust/dustEventManager.py
STATE_NORMAL = 0
STATE_PLACE_PIN = 1

class DustEventManager:
    __guid__ = 'planet.ui.DustEventManager'
    __notifyevents__ = []

    def __init__(self):
        self.state = STATE_NORMAL

    def Close(self):
        pass

    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.dustPinManager = self.planetUISvc.myPinManager

    def OnPlanetViewClosed(self):
        pass

    def PlacePinOnNextClick(self):
        self.state = STATE_PLACE_PIN

    def SetNormalState(self):
        self.state = STATE_NORMAL

    def OnPlanetPinClicked(self, pinID):
        if uicore.uilib.rightbtn:
            return
        self.dustPinManager.PinSelected(pinID)

    def OnPlanetPinDblClicked(self, pinID):
        pass

    def OnDepletionPinClicked(self, index):
        pass

    def OnPlanetPinMouseEnter(self, pinID):
        pass

    def OnPlanetPinMouseExit(self, pinID):
        if not self:
            return

    def OnPlanetNavClicked(self, surfacePoint, wasDragged):
        if wasDragged:
            return
        if surfacePoint is None:
            self.dustPinManager.CancelPinPlacement()
            return
        if self.state is STATE_PLACE_PIN:
            self.dustPinManager.PlacePin(surfacePoint)
        else:
            self.dustPinManager.PinUnselected()

    def OnPlanetNavMouseUp(self):
        pass

    def OnPlanetNavRightClicked(self):
        return False

    def OnPlanetSurfaceDblClicked(self, surfacePoint):
        pass

    def OnPlanetSurfaceMouseMoved(self, surfacePoint):
        if self.state is STATE_PLACE_PIN:
            self.dustPinManager.MoveIndicatorPin(surfacePoint)

    def OnPlanetNavFocusLost(self):
        pass