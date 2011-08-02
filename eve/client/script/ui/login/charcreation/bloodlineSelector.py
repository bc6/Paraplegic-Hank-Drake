import GameWorld
import paperDoll as PD
import log
import trinity
import random
import blue
import sys
import uthread
import geo2
import paperDoll
RACE_PATHS_MAPPING = {1: [[['res:/Graphics/Character/Unique/CharacterSelect/AchuraFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/AchuraMaleClothing'], 11, 3], [['res:/Graphics/Character/Unique/CharacterSelect/CivireFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/CivireMaleClothing'], 2, 4], [['res:/Graphics/Character/Unique/CharacterSelect/DeteisFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/DeteisMaleClothing'], 1, 5]],
 2: [[['res:/Graphics/Character/Unique/CharacterSelect/BrutorFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/BrutorMaleClothing'], 4, 9], [['res:/Graphics/Character/Unique/CharacterSelect/SebiestorFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/SebiestorMaleClothing'], 3, 10], [['res:/Graphics/Character/Unique/CharacterSelect/VherokiorFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/VherokiorMaleClothing'], 14, 11]],
 4: [[['res:/Graphics/Character/Unique/CharacterSelect/AmarrFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/AmarrMaleClothing'], 5, 0], [['res:/Graphics/Character/Unique/CharacterSelect/KhanidFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/KhanidMaleClothing'], 13, 1], [['res:/Graphics/Character/Unique/CharacterSelect/NikunniFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/NikunniMaleClothing'], 6, 2]],
 8: [[['res:/Graphics/Character/Unique/CharacterSelect/GallenteFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/GallenteMaleClothing'], 7, 6], [['res:/Graphics/Character/Unique/CharacterSelect/IntakiFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/IntakiMaleClothing'], 8, 7], [['res:/Graphics/Character/Unique/CharacterSelect/JinmeiFemaleClothing', 'res:/Graphics/Character/Unique/CharacterSelect/JinMeiMaleClothing'], 12, 8]]}
MORPHEME_NETWORK = 'res:/Animation/MorphemeIncarna/Export/CharCreation_runtimeBinary/CharacterCreation.mor'
LIGHT_CURVE = 'res:/Graphics/Placeable/CharCreation/LightCurve.red'
LIGHT_RIGS = {1: 'res:/Graphics/Character/Global/PaperdollSettings/LightSettings/BloodlineCaldari.red',
 2: 'res:/Graphics/Character/Global/PaperdollSettings/LightSettings/BloodlineMinmatar.red',
 4: 'res:/Graphics/Character/Global/PaperdollSettings/LightSettings/BloodlineAmarr.red',
 8: 'res:/Graphics/Character/Global/PaperdollSettings/LightSettings/BloodlineGAllente.red'}

class BloodlineSelector(object):
    __guid__ = 'ccUtil.BloodlineSelector'

    def __init__(self, scene):
        self.race = None
        self.lineUp = []
        self.scene = scene
        self.currentSelection = None



    def LoadRace(self, raceID, callBack = None):
        if self.race == raceID:
            return 
        if self.race is not None:
            self.TearDown()
        self.currentSelection = None
        self.SetLightScene(LIGHT_RIGS[raceID], self.scene)
        factory = sm.GetService('character').factory
        if raceID in RACE_PATHS_MAPPING:
            self.race = raceID
            for bloodline in RACE_PATHS_MAPPING[raceID]:
                female = PD.PaperDollCharacter.ImportCharacter(factory, self.scene, bloodline[0][0])
                male = PD.PaperDollCharacter.ImportCharacter(factory, self.scene, bloodline[0][1])
                self.lineUp.append(self.Platform((female, male), bloodline[1], bloodline[2]))

        else:
            log.LogError('raceID ' + raceID + ' not valid')
            return 
        for platform in self.lineUp:
            for (i, each,) in enumerate(platform.pair):
                animation = GameWorld.GWAnimation(MORPHEME_NETWORK)
                if animation.network is not None:
                    animation.network.SetAnimationSetIndex(i)
                    animation.network.SetControlParameter('ControlParameters|NetworkMode', 0)
                    animation.network.SetControlParameter('ControlParameters|BloodlinePoseNumber', platform.poseID)
                    each.avatar.animationUpdater = animation

            platform.Deactivate()

        self.PositionLineUp()
        for each in self.lineUp:
            if each.position[0] < -0.5:
                for light in self.scene.lights:
                    if light.name == 'FrontMain1':
                        each.lightCurve.bindings[0].destinationObject = light
                        self.scene.curveSets.append(each.lightCurve)

            elif each.position[0] > 0.5:
                for light in self.scene.lights:
                    if light.name == 'FrontMain3':
                        each.lightCurve.bindings[0].destinationObject = light
                        self.scene.curveSets.append(each.lightCurve)

            else:
                for light in self.scene.lights:
                    if light.name == 'FrontMain2':
                        each.lightCurve.bindings[0].destinationObject = light
                        self.scene.curveSets.append(each.lightCurve)


        if callBack is not None:
            blue.resMan.Wait()
            callBack()



    def SetLightScene(self, lightPath, scene = None):
        scene = scene or self.scene
        lightScene = trinity.Load(lightPath)
        if scene:
            lightList = []
            for l in scene.lights:
                lightList.append(l)

            for l in lightList:
                scene.RemoveLightSource(l)

            for l in lightScene.lights:
                scene.AddLightSource(l)

            if paperDoll.SkinSpotLightShadows.instance is not None:
                paperDoll.SkinSpotLightShadows.instance.RefreshLights()



    def PositionLineUp(self):
        if len(self.lineUp) != 3:
            return 
        POSITIONS = [(-1.4, 0.0, 0.0), (0.0, 0.0, 0.0), (1.4, 0.0, 0.0)]
        for i in range(3):
            size = 2 - i
            toPop = random.randint(0, size)
            position = POSITIONS.pop(toPop)
            self.lineUp[i].Translate(position)




    def GetGenderOrder(self, bloodlineID):
        for platform in self.lineUp:
            if platform.bloodlineID == bloodlineID:
                female = platform.pair[0].avatar
                male = platform.pair[1].avatar
                femaleIndex = female.GetBoneIndex('Head')
                if female.skinningMatrixCount > femaleIndex:
                    femalePosition = female.GetBonePosition(femaleIndex)
                else:
                    femalePosition = None
                maleIndex = male.GetBoneIndex('Head')
                if male.skinningMatrixCount > maleIndex:
                    malePosition = male.GetBonePosition(maleIndex)
                else:
                    malePosition = None
                if femalePosition is not None and malePosition is not None:
                    return int(femalePosition < malePosition)
            log.LogWarn('Bloodline', bloodlineID, 'not in character lineup')

        return 0



    def GetBloodlineAndGender(self, pickedObject):
        for platform in self.lineUp:
            for (i, each,) in enumerate(platform.pair):
                if each.avatar == pickedObject:
                    if self.currentSelection != platform:
                        self.currentSelection = platform
                        return (platform.bloodlineID, None)
                    return (platform.bloodlineID, i)


        return (None, None)



    def SelectBloodline(self, bloodlineID):
        for platform in self.lineUp:
            if platform.bloodlineID == bloodlineID:
                platform.Activate()
            elif platform.active == True:
                platform.Deactivate()




    def TearDown(self):
        self.race = None
        self.lineUp = []



    def GetProjectedPosition(self, bloodlineID, genderID, camera):
        if camera is None:
            return 
        avatar = None
        camera.Update()
        for platform in self.lineUp:
            if platform.bloodlineID == bloodlineID:
                if genderID is None:
                    position = geo2.Add(platform.position, (0.0, 2.0, 0.0))
                    return camera.ProjectPoint(position)
                for (i, each,) in enumerate(platform.pair):
                    if i == genderID:
                        avatar = each.avatar


        if avatar == None:
            log.LogError('Could not get the projected head position for character with bloodlineID %s and genderID %s', (bloodlineID, genderID))
            return (0, 0)
        index = avatar.GetBoneIndex('Head')
        position = avatar.GetBonePosition(index)
        return camera.ProjectPoint(position)



    class Platform(object):

        def __init__(self, pair, bloodlineID, poseID):
            self.pair = pair
            self.bloodlineID = bloodlineID
            self.poseID = poseID
            self.genderIcons = []
            self.position = (0.0, 0.0, 0.0)
            self.active = False
            self.lightCurve = trinity.Load(LIGHT_CURVE)



        def Translate(self, pos):
            self.position = pos
            for each in self.pair:
                each.avatar.translation = pos
                if pos[0] < -0.5:
                    each.avatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.2, 0.0, 0.0)
                elif pos[0] > 0.5:
                    each.avatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(-0.2, 0.0, 0.0)




        def Activate(self):
            self.active = True
            for each in self.pair:
                each.avatar.animationUpdater.network.SetControlParameter('ControlParameters|Selected', 1.0)

            self.lightCurve.scale = 1.0
            self.lightCurve.Play()



        def Deactivate(self):
            self.active = False
            for each in self.pair:
                each.avatar.animationUpdater.network.SetControlParameter('ControlParameters|Selected', 0.0)

            self.lightCurve.scale = -1.0
            self.lightCurve.PlayFrom(0.5)





