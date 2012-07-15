#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/shouldSpawn.py
import cef

def ShouldSpawnOn(componentIDList, spawnLoc):
    shouldSpawn = False
    for componentID in componentIDList:
        componentView = cef.BaseComponentView.GetComponentViewByID(componentID)
        spawnHere = componentView.__SHOULD_SPAWN__.get(spawnLoc, None)
        if spawnHere is False:
            return False
        if spawnHere:
            shouldSpawn = True

    return shouldSpawn


exports = {'cef.ShouldSpawnOn': ShouldSpawnOn}