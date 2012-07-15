#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/entities/commandPin.py
import planet
import planetCommon

class CommandPin(planet.SpaceportPin):
    __guid__ = 'planet.CommandPin'
    __slots__ = []

    def OnStartup(self, id, ownerID, latitude, longitude):
        planet.SpaceportPin.OnStartup(self, id, ownerID, latitude, longitude)

    def IsCommandCenter(self):
        return True

    def CanImportCommodities(self, commodities):
        return False

    def GetPowerOutput(self):
        level = self.eventHandler.level
        return planetCommon.GetPowerOutput(level)

    def GetCpuOutput(self):
        level = self.eventHandler.level
        return planetCommon.GetCPUOutput(level)


exports = {'planet.CommandPin': CommandPin}