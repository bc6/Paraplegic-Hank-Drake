import planet
import uthread

class OtherPinManager:
    __guid__ = 'planet.ui.OtherPinManager'
    __notifyevents__ = []

    def __init__(self):
        sm.RegisterNotify(self)
        self.currentOtherExpandedCommandPin = None
        self.otherPlayerPinsByPinID = {}
        self.otherPlayerVisiblePins = []
        self.otherPlayerExtractors = []



    def Close(self):
        sm.UnregisterNotify(self)
        self.currentOtherExpandedCommandPin = None
        self.otherPlayerPinsByPinID = None
        self.otherPlayerVisiblePins = None
        self.otherPlayerExtractors = None



    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        uthread.new(self.RenderCommandCentersOfOtherCharacters)



    def OnPlanetViewClosed(self):
        self.ShowOrHideOtherCharactersPins(show=False)



    def RenderCommandCentersOfOtherCharacters(self):
        if not settings.user.ui.Get('planetShowOtherCharactersPins', True):
            return 
        commandCenters = self.GetCommandCentersOfOtherCharacters()
        for (charid, cc,) in commandCenters.iteritems():
            if charid == session.charid:
                continue
            sp = planet.SurfacePoint(theta=cc.longitude, phi=cc.latitude)
            pin = planet.ui.OtherPlayersPin(sp, cc.pinID, cc.typeID, cc.ownerID, self.planetUISvc.pinOthersTransform)
            self.otherPlayerPinsByPinID[cc.pinID] = pin

        self.planetUISvc.curveLineDrawer.SubmitLineset('otherLinks')



    def ShowOrHideOtherCharactersPins(self, show):
        if show:
            showOtherPins = settings.user.ui.Set('planetShowOtherCharactersPins', True)
            self.RenderCommandCentersOfOtherCharacters()
        else:
            showOtherPins = settings.user.ui.Set('planetShowOtherCharactersPins', False)
            self.HideOtherCharactersNetwork()
            for pin in self.otherPlayerPinsByPinID.values():
                pin.Remove()
                self.otherPlayerPinsByPinID = {}




    def RenderOtherCharactersNetwork(self, charid):
        linkColor = (0.0, 1.0, 1.0, 1.0)
        linkBgColor = (0.0, 0.0, 0.0, 0.3)
        (pins, links,) = self.GetOtherCharactersNetwork(charid)
        self.HideOtherCharactersNetwork()
        for pinData in pins:
            groupID = cfg.invtypes.Get(pinData.typeID).groupID
            if groupID == const.groupCommandPins:
                self.currentOtherExpandedCommandPin = self.otherPlayerPinsByPinID[pinData.pinID]
                self.currentOtherExpandedCommandPin.RenderAsActive()
                continue
            sp = planet.SurfacePoint(theta=pinData.longitude, phi=pinData.latitude)
            pin = planet.ui.OtherPlayersPin(sp, pinData.pinID, pinData.typeID, pinData.ownerID, self.planetUISvc.pinOthersTransform, isActive=True)
            self.otherPlayerVisiblePins.append(pin)
            self.otherPlayerPinsByPinID[pinData.pinID] = pin

        for link in links:
            sp1 = self.otherPlayerPinsByPinID[link[0]].surfacePoint
            sp2 = self.otherPlayerPinsByPinID[link[1]].surfacePoint
            length = sp1.GetDistanceToOther(sp2)
            texWidth = 600.0 * length
            lineID = self.planetUISvc.curveLineDrawer.DrawArc('otherLinks', sp1, sp2, 5.0, linkBgColor, linkBgColor)
            numSegments = max(1, int(length * 25.0))
            self.planetUISvc.curveLineDrawer.SetLineSetNumSegments('otherLinks', lineID, numSegments)
            self.planetUISvc.curveLineDrawer.ChangeLineAnimation('otherLinks', lineID, linkColor, 0.0, texWidth)

        self.planetUISvc.curveLineDrawer.SubmitLineset('otherLinks')



    def HideOtherCharactersNetwork(self):
        for pin in self.otherPlayerVisiblePins:
            pin.Remove()

        self.otherPlayerVisiblePins = []
        self.planetUISvc.curveLineDrawer.ClearLines('otherLinks')
        if self.currentOtherExpandedCommandPin:
            self.currentOtherExpandedCommandPin.RenderAsDefault()
            self.currentOtherExpandedCommandPin = None



    def RenderOtherPlayersExtractors(self, resourceTypeID):
        self.HideOtherPlayersExtractors()
        extractorData = self.GetExtractorsOfOtherCharacters(resourceTypeID)
        if not extractorData:
            return 
        for pinData in extractorData:
            sp = planet.SurfacePoint(theta=pinData.longitude, phi=pinData.latitude)
            pin = planet.ui.OtherPlayersPin(sp, pinData.pinID, pinData.typeID, pinData.ownerID, self.planetUISvc.pinOthersTransform, isActive=True)
            self.otherPlayerExtractors.append(pin)
            self.otherPlayerPinsByPinID[pinData.pinID] = pin




    def HideOtherPlayersExtractors(self):
        for pin in self.otherPlayerExtractors:
            pin.Remove()

        self.otherPlayerExtractors = []



    def GetCommandCentersOfOtherCharacters(self):
        if not self.planetUISvc.planet:
            return 
        return sm.GetService('planetSvc').GetPlanetCommandPins(self.planetUISvc.planet.planetID)



    def GetExtractorsOfOtherCharacters(self, resourceTypeID):
        if self.planetUISvc.planet is None:
            return 
        extractors = sm.GetService('planetSvc').GetExtractorsForPlanet(self.planetUISvc.planet.planetID)
        ret = []
        for extractor in extractors:
            extractedType = sm.GetService('godma').GetTypeAttribute(extractor.typeID, const.attributeHarvesterType)
            if extractedType != resourceTypeID:
                continue
            if extractor.ownerID == session.charid:
                continue
            ret.append(extractor)

        return ret



    def GetOtherCharactersNetwork(self, charid):
        if self.planetUISvc.planet is None:
            return 
        return sm.GetService('planetSvc').GetColonyForCharacter(self.planetUISvc.planet.planetID, charid)



    def GetPinMenuOther(self, pinID):
        pin = self.otherPlayerPinsByPinID.get(pinID)
        if pin:
            return pin.GetMenu()




