import os
import extraCatmaConfig
from dataLog import DataLog, DATALOG_SCHEMA_NAME
from dustEnums import PopulateEnums
EDITORFLAG_CHARACTER_ID = 1
EDITORFLAG_TEAM_ID = 2
EDITORFLAG_CATMA_ID = 3
EDITORFLAG_MASK = EDITORFLAG_CHARACTER_ID | EDITORFLAG_TEAM_ID | EDITORFLAG_CATMA_ID

def PopulateGeneric(ax2):
    typeDef = ax2.CreateType('Vector', forUE3=False)
    typeDef.AddMember('Float x')
    typeDef.AddMember('Float y')
    typeDef.AddMember('Float z')



def PopulateKillEvent(ax2):
    typeDef = ax2.CreateType('Kill')
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('EKillType killType', caption='The type of kill')
    typeDef.AddMember('Int killerID', caption='The character who did the killing', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int killerPawnTypeID', caption='The pawn type of the killer')
    typeDef.AddMember('Int victimID', caption='The character who was killed', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int victimPawnTypeID', caption='The pawn type of the killed')
    typeDef.AddMember('Int killerTeamID', caption='The team of the killer, 0 = attacker, 1 = defender, 255 = observer', editorFlag=EDITORFLAG_TEAM_ID)
    typeDef.AddMember('Int victimTeamID', caption='The team of the victim, 0 = attacker, 1 = defender, 255 = observer', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateWarPointEvent(ax2):
    typeDef = ax2.CreateType('WarPoint')
    typeDef.AddMember('Int actorID', caption='The character who received the war points', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int delta', caption='The amount of war points received')
    typeDef.AddMember('Int balance', caption='The new amount of war points the character now has')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateHackEvent(ax2):
    typeDef = ax2.CreateType('Hack')
    typeDef.AddMember('Int actorID', caption='The character who did the actual capturing', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int objectTypeID', caption='The catma type ID of the hacked object')
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateObjectDestructionEvent(ax2):
    typeDef = ax2.CreateType('ObjectDestruction')
    typeDef.AddMember('Int actorID', caption='The character who directly caused the destruction', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int objectTypeID', caption='The catma type ID of the destroyed object', editorFlag=EDITORFLAG_CATMA_ID)
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateObjectSpawnEvent(ax2):
    typeDef = ax2.CreateType('ObjectSpawn')
    typeDef.AddMember('Int actorID', caption='The character who spawned the object', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int objectTypeID', caption='The catma type ID of the spawned object', editorFlag=EDITORFLAG_CATMA_ID)
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateMCCSurgeEvent(ax2):
    typeDef = ax2.CreateType('MCCSurge')
    typeDef.AddMember('Int actorID', caption='The character who directly caused the surge', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateMatchWinEvent(ax2):
    typeDef = ax2.CreateType('MatchWin')
    typeDef.AddMember('Int teamID', caption='The team the character is currently working for', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateTeamSelectEvent(ax2):
    typeDef = ax2.CreateType('TeamSelect')
    typeDef.AddMember('Int actorID', caption='The character who joined a team', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int teamID', caption='The team joined, 0 = attacker, 1 = defender, 255 = observer', editorFlag=EDITORFLAG_TEAM_ID)



def PopulateTeamQuitEvent(ax2):
    typeDef = ax2.CreateType('TeamQuit')
    typeDef.AddMember('Int actorID', caption='The character who joined a team', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int reason', caption='The quit reason , 0 = quit normal, 1 = quit abnormal')



def PopulateCharacterPositionEvent(ax2):
    typeDef = ax2.CreateType('CharacterPosition')
    typeDef.AddMember('Int actorID', caption='The character', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Vector position', caption='Location')
    typeDef.AddMember('Int vehicleTypeID', caption='The catma type ID of the vehicle object, 0 = no vehicle', editorFlag=EDITORFLAG_CATMA_ID)



def PopulateWeaponUseEvent(ax2):
    typeDef = ax2.CreateType('WeaponUse')
    typeDef.AddMember('Int actorID', caption='The character', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int typeID', caption='The catma id of the weapon which equipped, 0 means the character is putting down the weapon', editorFlag=EDITORFLAG_CATMA_ID)



def PopulateVehicleUseEvent(ax2):
    typeDef = ax2.CreateType('VehicleUse')
    typeDef.AddMember('Int actorID', caption='The character', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int typeID', caption='The catma id of the vehicle that the character got on, 0 means the character is getting off the vehicle', editorFlag=EDITORFLAG_CATMA_ID)



def PopulateAssistKillEvent(ax2):
    typeDef = ax2.CreateType('AssistKill')
    typeDef.AddMember('Int instigatorID', caption='The character id of instigator', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int victimID', caption='The character id of victim', editorFlag=EDITORFLAG_CHARACTER_ID)
    typeDef.AddMember('Int damageType', caption='The damage type, 0 = person damage, 1 = vehicle damage')



def PopulateAll(ax2):
    PopulateGeneric(ax2)
    PopulateEnums(ax2)
    PopulateKillEvent(ax2)
    PopulateWarPointEvent(ax2)
    PopulateHackEvent(ax2)
    PopulateObjectDestructionEvent(ax2)
    PopulateObjectSpawnEvent(ax2)
    PopulateMCCSurgeEvent(ax2)
    PopulateMatchWinEvent(ax2)
    PopulateTeamSelectEvent(ax2)
    PopulateTeamQuitEvent(ax2)
    PopulateCharacterPositionEvent(ax2)
    PopulateWeaponUseEvent(ax2)
    PopulateVehicleUseEvent(ax2)
    PopulateAssistKillEvent(ax2)


if __name__ == '__main__':
    scriptPath = os.path.realpath(os.path.dirname(__file__))
    pyfolder = os.path.normpath(os.path.join(scriptPath, '..'))
    ue3folder = os.path.join(scriptPath, '../../dust/ue3/Development/Src/DustGame/Classes')
    ue3folder = os.path.normpath(ue3folder)
    if not os.path.exists(ue3folder):
        raise RuntimeError('UE3 script folder path not found', ue3folder)
    cppfolder = os.path.join(scriptPath, '../../dust/ue3/Development/Src/DustGame/Inc')
    cppfolder = os.path.normpath(cppfolder)
    sqlFolder = os.path.abspath('../../../../db/db-eve/schemas/' + DATALOG_SCHEMA_NAME)
    if not os.path.exists(cppfolder):
        raise RuntimeError('CPP include folder path not found', ue3folder)
    ax2 = DataLog(extraCatmaConfig)
    PopulateAll(ax2)
    print '********* Generating .CPP to %s *********' % ue3folder
    fileNames = ax2.GenerateCppCode(cppfolder)
    for fileName in fileNames:
        print 'touched %s' % fileName

    print '\n********* Generating .UCI to %s *********' % ue3folder
    fileNames = ax2.GenerateUE3Code(ue3folder)
    for fileName in fileNames:
        print 'touched %s' % fileName

    print '\n********* Generating .PY  to %s *********' % pyfolder
    fileNames = ax2.GeneratePythonCode(pyfolder)
    for fileName in fileNames:
        print 'touched %s' % fileName

    print '\n********* Generating .SQL to %s *********' % sqlFolder
    fileNames = ax2.GenerateSQLTableDefinitions(sqlFolder)
    for fileName in fileNames:
        print 'touched %s' % fileName

    print '********* Done *********'

