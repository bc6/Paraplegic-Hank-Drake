import trinity
import blue
import log
import turret
import audio2
import util
TURRETSET_SHADERTYPE_INVALID = 0
TURRETSET_SHADERTYPE_OVERRIDE = 1
TURRETSET_SHADERTYPE_HALFOVERRIDE = 2
TURRETSET_SHADERTYPE_NOTOVERRIDE = 3
SIEGE_TURRETS = [20450,
 3561,
 20444,
 20448,
 3550,
 20450,
 3546,
 3573,
 20452,
 3571,
 20454]

class TurretSet():
    __guid__ = 'turretSet.TurretSet'
    turretsEnabled = [False]

    def Initialize(self, graphics, locator, overrideBeamGraphicID = None, count = 1):
        self.inWarp = False
        self.isShooting = False
        self.targetsAvailable = False
        self.shaderType = TURRETSET_SHADERTYPE_INVALID
        self.online = True
        if not hasattr(graphics, 'graphicFile'):
            log.LogError('New turret system got wrong initialization data, will use fallback: ' + str(graphics))
            turretPath = 'res:/dx9/model/turret/Special/FallbackTurret.red'
        else:
            turretPath = graphics.graphicFile
            if not turretPath.endswith('.red'):
                log.LogError('BSD data is pointing to an old turret, will use fallback: ' + str(graphics))
                turretPath = 'res:/dx9/model/turret/Special/FallbackTurret.red'
        self.turretSets = []
        for i in range(count):
            self.turretSets.append(trinity.Load(turretPath))
            self.turretSets[i].locatorName = 'locator_turret_' + str(i + locator)

        blue.resMan.Wait()
        for turretSet in self.turretSets:
            for j in range(turretSet.muzzleCount):
                effect = trinity.Load(turretSet.firingEffectResPath)
                if effect is not None:
                    effect.source = None
                    effect.dest = None
                    if j == 0:
                        self.AddSoundToEffect(effect, turretSet.soundSourceName, turretSet.soundDestName)
                    turretSet.firingEffects.append(effect)
                else:
                    log.LogError('Could not find primary firingeffect ' + turretSet.firingEffectResPath + ' for turret: ' + turretPath)

            for j in range(turretSet.secMuzzleCount):
                effect = trinity.Load(turretSet.firingEffectSecResPath)
                if effect is not None:
                    effect.source = None
                    effect.dest = None
                    turretSet.firingEffects.append(effect)
                else:
                    log.LogError('Could not find secondary firingeffect ' + turretSet.firingEffectSecResPath + ' for turret: ' + turretPath)


        if len(self.turretSets) > 0:
            if self.turretSets[0].turretEffect is not None:
                if self.turretSets[0].turretEffect.name == 'overridable':
                    self.shaderType = TURRETSET_SHADERTYPE_OVERRIDE
                elif self.turretSets[0].turretEffect.name == 'half_overridable':
                    self.shaderType = TURRETSET_SHADERTYPE_HALFOVERRIDE
                elif self.turretSets[0].turretEffect.name == 'not_overridable':
                    self.shaderType = TURRETSET_SHADERTYPE_NOTOVERRIDE
        return self.turretSets



    def AddSoundToEffect(self, fe, srcName, destName):
        srcAudio = audio2.AudEmitter(srcName)
        destAudio = audio2.AudEmitter(destName)
        if fe.sourceObject:
            obs = trinity.TriObserverLocal()
            obs.front = (0.0, -1.0, 0.0)
            obs.observer = srcAudio
            del fe.sourceObject.observers[:]
            fe.sourceObject.observers.append(obs)
        if fe.destObject:
            obs = trinity.TriObserverLocal()
            obs.front = (0.0, -1.0, 0.0)
            obs.observer = destAudio
            del fe.destObject.observers[:]
            fe.destObject.observers.append(obs)
        for eachSet in fe.curveSets:
            for eachCurve in eachSet.curves:
                if eachCurve.__typename__ == 'TriEventCurve':
                    if eachCurve.name == 'audioEventsSource':
                        eachCurve.eventListener = srcAudio
                    elif eachCurve.name == 'audioEventsDest':
                        eachCurve.eventListener = destAudio





    def GetTurretSet(self, index = 0):
        return self.turretSets[index]



    def GetTurretSets(self):
        return self.turretSets



    def Release(self):
        pass



    def SetTargetsAvailable(self, available):
        if self.targetsAvailable and not available:
            self.Rest()
        self.targetsAvailable = available



    def SetTarget(self, shipID, targetID):
        self.targetID = targetID
        targetBall = sm.GetService('michelle').GetBall(targetID)
        if targetBall is not None:
            for turretSet in self.turretSets:
                turretSet.targetObject = targetBall.model




    def SetAmmoColorByTypeID(self, ammoTypeID):
        gfxString = cfg.invtypes.Get(ammoTypeID).GraphicFile().lower()
        gfxString = gfxString.replace('res:/model', 'res:/dx9/model').replace('.blue', '.red')
        color = trinity.Load(gfxString)
        blue.resMan.Wait()
        if color is None:
            log.LogError('turretSet::SetAmmoColor - unable to load color for ammoTypeID %d' % ammoTypeID)
            return 
        self.SetAmmoColor(color)



    def SetAmmoColor(self, color):
        if color is None:
            return 
        for turretSet in self.turretSets:
            for firingEffect in turretSet.firingEffects:
                for curve in firingEffect.Find('trinity.TriColorCurve'):
                    if curve.name == 'Ammo':
                        curve.value = color






    def IsShooting(self):
        return self.isShooting



    def StartShooting(self, ammoGFXid = None):
        if self.inWarp:
            return 
        for turretSet in self.turretSets:
            turretSet.EnterStateFiring()

        self.isShooting = True



    def StopShooting(self):
        for turretSet in self.turretSets:
            if self.inWarp:
                turretSet.EnterStateDeactive()
            elif self.targetsAvailable:
                turretSet.EnterStateTargeting()
            else:
                turretSet.EnterStateIdle()

        self.isShooting = False



    def Rest(self):
        if self.inWarp or not self.online:
            return 
        for turretSet in self.turretSets:
            turretSet.EnterStateIdle()




    def Offline(self):
        if self.online == False:
            return 
        self.online = False
        for turretSet in self.turretSets:
            turretSet.EnterStateDeactive()




    def Online(self):
        if self.online == True:
            return 
        self.online = True
        for turretSet in self.turretSets:
            turretSet.EnterStateIdle()




    def EnterWarp(self):
        self.inWarp = True
        for turretSet in self.turretSets:
            turretSet.EnterStateDeactive()




    def ExitWarp(self):
        self.inWarp = False
        if self.online:
            for turretSet in self.turretSets:
                turretSet.EnterStateIdle()




    def TakeAim(self, targetID):
        if self.targetID != targetID:
            log.LogWarn('target ids mismatch!')
            return 
        if not self.online:
            return 
        for turretSet in self.turretSets:
            turretSet.EnterStateTargeting()




    def SetShaderParameter(self, materialFilename, blocked):
        overrideEffect = trinity.Load(materialFilename)
        if overrideEffect is not None:
            for turretSet in self.turretSets:
                for param in turretSet.turretEffect.parameters:
                    if param.name not in blocked:
                        for overrideParam in overrideEffect.parameters:
                            if param.name == overrideParam.name:
                                overrideParam.CopyTo(param)






    def ApplyTurretPresets(self, parentTypeID, turretTypeID):
        godma = sm.GetService('godma')
        turretColorSchemeID = None
        if turretTypeID is not None:
            turretColorSchemeID = godma.GetTypeAttribute(turretTypeID, const.attributeTypeColorScheme)
        parentColorSchemeID = None
        if parentTypeID is not None:
            parentColorSchemeID = godma.GetTypeAttribute(parentTypeID, const.attributeTypeColorScheme)
        blockedParameters = {}
        colorSchemeID = None
        if self.shaderType == TURRETSET_SHADERTYPE_OVERRIDE:
            colorSchemeID = parentColorSchemeID
        elif self.shaderType == TURRETSET_SHADERTYPE_HALFOVERRIDE:
            colorSchemeID = parentColorSchemeID
            blockedParameters = {'GlowColor'}
        elif self.shaderType == TURRETSET_SHADERTYPE_NOTOVERRIDE:
            colorSchemeID = turretColorSchemeID
        if colorSchemeID is not None:
            colorSchemeGraphics = cfg.graphics.Get(colorSchemeID)
            if colorSchemeGraphics is not None:
                self.SetShaderParameter(colorSchemeGraphics.graphicFile, blockedParameters)



    @staticmethod
    def AddTurretToModel(model, turretGraphicsID, locatorID, count = 1):
        if model.__bluetype__ != 'trinity.EveShip2':
            log.LogError('Wrong object is trying to get turret attached due to wrong authored content! model:' + model.name + ' bluetype:' + model.__bluetype__)
            return 
        graphics = cfg.graphics.Get(turretGraphicsID)
        newTurretSet = TurretSet()
        eveTurretSets = newTurretSet.Initialize(graphics, locatorID, None, count=count)
        for tSet in eveTurretSets:
            model.turretSets.append(tSet)

        model.RebuildTurretPositions()
        return newTurretSet



    @staticmethod
    def FitTurret(model, parentTypeID, turretTypeID, locatorID, count = 1, online = True, checkSettings = True):
        to = cfg.invtypes.GetIfExists(turretTypeID)
        if to is None:
            return 
        if checkSettings and not settings.user.ui.Get('turretsEnabled', 1):
            return 
        groupID = to.groupID
        newTurretSet = None
        if model is None:
            log.LogError('FitTurret() called with NoneType, so there is no model to fit the turret to!')
            return 
        if groupID not in const.turretModuleGroups:
            return 
        if to.graphicID is not None:
            newTurretSet = turret.TurretSet.AddTurretToModel(model, to.graphicID, locatorID, count=count)
            if newTurretSet is None:
                return 
            newTurretSet.ApplyTurretPresets(parentTypeID, turretTypeID)
            if not online:
                newTurretSet.Offline()
        return newTurretSet



    @staticmethod
    def FitTurrets(shipID, model, checkSettings = True):
        if checkSettings and not settings.user.ui.Get('turretsEnabled', 1):
            return {}
        turretsFitted = {}
        modules = []
        groupID = None
        if shipID == util.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            dogmaLocation.LoadItem(shipID)
            ship = dogmaLocation.GetDogmaItem(shipID)
            modules = []
            for module in ship.GetFittedItems().itervalues():
                if module.groupID in const.turretModuleGroups:
                    modules.append([module.itemID,
                     module.typeID,
                     module.flagID - const.flagHiSlot0 + 1,
                     module.IsOnline()])

            shipTypeID = ship.typeID
            groupID = ship.groupID
        else:
            slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            moduleItems = slimItem.modules
            modules = [ [module[0],
             module[1],
             None,
             True] for module in moduleItems ]
            shipTypeID = slimItem.typeID
            groupID = slimItem.groupID
        if groupID == const.groupDreadnought:
            siegeTurrets = []
            for module in modules:
                if module[1] in SIEGE_TURRETS:
                    siegeTurrets.append(module)

            for (i, each,) in enumerate(siegeTurrets):
                each[2] = i + 1

            counter = len(siegeTurrets) + 1
            for each in modules:
                if each not in siegeTurrets:
                    each[2] = counter
                    counter += 1

        oldTurrets = model.turretSets[:]
        locatorCounter = 1
        for (moduleID, typeID, slot, isOnline,) in modules:
            slot = slot or locatorCounter
            ts = turret.TurretSet.FitTurret(model, shipTypeID, typeID, slot, checkSettings=checkSettings, online=isOnline)
            if ts is not None:
                turretsFitted[moduleID] = ts
                locatorCounter += 1

        for each in oldTurrets:
            if each in model.turretSets:
                model.turretSets.remove(each)

        return turretsFitted



exports = {'turret.TurretSet': TurretSet}

