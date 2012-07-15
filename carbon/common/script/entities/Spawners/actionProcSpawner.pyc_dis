#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/entities/Spawners/actionProcSpawner.py
import GameWorld
import cef

class ActionProcSpawner(cef.RuntimeSpawner):
    __guid__ = 'cef.ActionProcSpawner'

    def __init__(self, entitySceneID, dynamicSpawnID, recipeTypeID, posProp, rotProp):
        position = GameWorld.GetPropertyForCurrentPythonProc(posProp)
        rotation = GameWorld.GetPropertyForCurrentPythonProc(rotProp)
        cef.RuntimeSpawner.__init__(self, entitySceneID, dynamicSpawnID, recipeTypeID, position, rotation)