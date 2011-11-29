import util
import trinity
import blue
import nodemanager
import __builtin__
import random
import base
turretpath = 'res:/Model/Turret/'
ammodir = 'res:/Model/Turret/Ammo/'
turretlight = 'res:/Model/Turret/turret_light.blue'
defaultAmmoColor = {'p': 'res:/Model/Turret/Ammo/p1.blue',
 'e': 'res:/Model/Turret/Ammo/ye1.blue',
 'h': 'res:/Model/Turret/Ammo/h1.blue'}
ONESECONDL = 10000000L

class TurretPair():
    __persistvars__ = ['owner',
     'turrets',
     'timecurves',
     'target',
     'lastFiredID',
     'shooting',
     'weaponType']

    def Initialize(self, graphicID):
        self.shooting = 0
        turrStart = blue.os.GetWallclockTimeNow()
        if type(graphicID) == type(''):
            gfxString = graphicID
        else:
            gfxString = util.GraphicFile(graphicID)
        if util.IsFullLogging():
            sm.GetService('FxSequencer').LogInfo('turret gfxString = ', gfxString, ' graphicID = ', graphicID)
        if gfxString == '':
            sm.GetService('FxSequencer').LogError('ERROR! There is no graphicFile entry for graphicID ' + str(graphicID))
        if gfxString[0:3] == 'res':
            sm.GetService('FxSequencer').LogError('ERROR! The entry  for turret ' + str(graphicID) + ' is a res path. We want something more l33t than that! Alert torfi')
            self.turrets = []
            return 
        race = gfxString[0:1]
        weaponSize = gfxString[1:2]
        weaponType = gfxString[2:3]
        weaponId = gfxString[3:4]
        techlevel = gfxString[4:5]
        ammo = gfxString[5:6]
        self.lastFiredID = 0
        self.turrets = []
        self.weaponType = weaponType
        audio = 1
        turret1 = Turret()
        tempTriTurret = turret1.Initialize(race, weaponSize, weaponType, weaponId, techlevel, ammo, audio)
        turret2 = Turret()
        turret2.InitWithTriTurret(tempTriTurret)
        self.turrets.append(turret1)
        self.turrets.append(turret2)
        turrEnd = blue.os.GetWallclockTimeNow()
        self.target = None



    def Release(self):
        for turret in self.turrets:
            turret.Release()

        self.turrets = []



    def SetTarget(self, shipID, targetID):
        targetTf = sm.GetService('damage').GetTargetLocators(shipID, targetID)
        for turret in self.turrets:
            success = turret.SetTarget(shipID, targetID, targetTf)
            if success is None:
                self.target = None
                return 

        self.targetID = targetID
        self.shipID = shipID



    def SetAmmoColor(self, ammoTypeID):
        if ammoTypeID is None:
            if self.weaponType in defaultAmmoColor:
                gfxString = defaultAmmoColor[self.weaponType]
            else:
                return 
        else:
            gfxString = cfg.invtypes.Get(ammoTypeID).GraphicFile()
        if len(gfxString):
            col = eve.rot.GetInstance(gfxString)
            for turret in self.turrets:
                turret.SetAmmoColor(col, gfxString)




    def StartShooting(self, ammoGFXid = None):
        blue.pyos.synchro.SleepSim(1)
        blue.pyos.synchro.SleepSim(random.randint(0, 100))
        self.shooting = 1
        fireNow = self.lastFiredID
        if len(self.turrets) > fireNow:
            turret = self.turrets[fireNow]
        else:
            return 
        if not turret.triTurret.canShoot:
            fireNow = not fireNow
            turret = self.turrets[fireNow]
        if turret.triTurret.canShoot:
            self.lastFiredID = fireNow
            turret.Shoot()
            if self.turrets[(not fireNow)].source_sound:
                self.turrets[(not fireNow)].source_sound.Stop()
            self.shooting = 0
            return 
        elapsedTime = 0.0
        aimTime = self.turrets[0].triTurret.aimTime
        startTime = blue.os.GetSimTime()
        while elapsedTime < aimTime + 0.1:
            elapsedTime = float(blue.os.GetSimTime() - startTime) / 10000000.0
            for turret in self.turrets:
                if turret.triTurret.canShoot:
                    turret.Shoot()
                    for otherTurret in self.turrets:
                        if otherTurret != turret:
                            if otherTurret.source_sound:
                                otherTurret.source_sound.Stop()

                    self.shooting = 0
                    return 

            blue.pyos.synchro.SleepSim(20)

        sm.GetService('FxSequencer').LogInfo('No turret in scope. No turret made hit')



    def Rest(self):
        for turret in self.turrets:
            turret.Rest()

        self.target = None



    def ActivateFluff(self, fluffname, active):
        for turret in self.turrets:
            turret.ActivateFluff(fluffname, active)




    def StopShooting(self):
        pass




class MiningTurretPair(TurretPair):
    __persistvars__ = ['shootTimer', 'shootDelay']

    def Initialize(self, graphicID, shootDelay):
        self.shootDelay = shootDelay
        self.now = blue.os.GetSimTime()
        self.shootTimer = None
        self.weaponType = None
        TurretPair.Initialize(self, graphicID)



    def Release(self):
        self.StopShooting()
        TurretPair.Release(self)



    def StartShooting(self, ammoGFXid = None):
        if self.shootDelay:
            if self.shootTimer:
                self.shootTimer = None
            else:
                self.Shoot()
            offset = self.shootDelay / 5 * 4 + random.randint(0, self.shootDelay / 5)
            self.shootTimer = base.AutoTimer(offset, self.Shoot)



    def StopShooting(self):
        self.shootTimer = None



    def Rest(self):
        self.StopShooting()
        for turret in self.turrets:
            turret.Rest()

        self.target = None



    def Shoot(self):
        targetBall = sm.GetService('michelle').GetBall(self.targetID)
        shipBall = sm.GetService('michelle').GetBall(self.shipID)
        if targetBall is None:
            sm.GetService('FxSequencer').LogWarn('Target Ball not found, stopped mining animation.', self.targetID)
            return 
        if getattr(targetBall, 'model', None) is None:
            sm.GetService('FxSequencer').LogWarn('Target Ball had no model stopped mining animation.', self.targetID)
            return 
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if targetBall.model not in scene.models or targetBall.model.display == 0:
            sm.GetService('FxSequencer').LogError('Target model was not in scene, or was not displayed.', self.targetID)
            return 
        if shipBall.model not in scene.models or shipBall.model.display == 0:
            sm.GetService('FxSequencer').LogError('Ship was not in scene or was not displayed', self.shipID)
            return 
        self.ShootAnimation()



    def ShootAnimation(self):
        self.shooting = 1
        fireNow = 1 - self.lastFiredID
        turret = self.turrets[fireNow]
        if not turret.triTurret.canShoot:
            fireNow = not fireNow
            turret = self.turrets[fireNow]
        blue.pyos.synchro.SleepSim(random.randint(0, 100))
        if not turret.triTurret:
            return 
        if turret.triTurret.canShoot:
            self.lastFiredID = fireNow
            turret.Shoot()
            if self.turrets[(not fireNow)].source_sound:
                self.turrets[(not fireNow)].source_sound.Stop()
            self.shooting = 0
            return 
        elapsedTime = 0.0
        aimTime = self.turrets[0].triTurret.aimTime
        startTime = blue.os.GetSimTime()
        while elapsedTime < aimTime + 0.1:
            elapsedTime = float(blue.os.GetSimTime() - startTime) / 10000000.0
            for turret in self.turrets:
                if turret.triTurret.canShoot:
                    turret.Shoot()
                    for otherTurret in self.turrets:
                        if otherTurret != turret:
                            if otherTurret.source_sound:
                                otherTurret.source_sound.Stop()

                    self.shooting = 0
                    return 

            blue.pyos.synchro.SleepSim(20)

        sm.GetService('FxSequencer').LogInfo('No turret in scope. No turret made hit')




class EntityTurrets(TurretPair):

    def Initialize(self, graphicID, amount = 2):
        if type(graphicID) == type(''):
            gfxString = graphicID
        else:
            gfxString = util.GraphicFile(graphicID)
        if util.IsFullLogging():
            sm.GetService('FxSequencer').LogInfo('turret gfxString = ', gfxString, ' graphicID = ', graphicID)
        if not gfxString:
            sm.GetService('FxSequencer').LogError('ERROR! There is no graphicFile entry for graphicID ' + str(graphicID))
        if gfxString[0:3] == 'res':
            sm.GetService('FxSequencer').LogError('ERROR! The entry  for turret ' + str(graphicID) + ' is a res path. We want something more l33t than that! Alert torfi')
            self.turrets = []
            return 
        race = gfxString[0]
        weaponSize = gfxString[1]
        weaponType = gfxString[2]
        weaponId = gfxString[3]
        techlevel = gfxString[4]
        ammo = gfxString[5]
        audio = 1
        self.shooting = 0
        self.weaponType = weaponType
        self.lastFiredID = 0
        self.target = None
        self.turrets = [ Turret() for each in range(amount) ]
        tempTriTurret = self.turrets[0].Initialize(race, weaponSize, weaponType, weaponId, techlevel, ammo, audio)
        for each in self.turrets[1:amount]:
            each.InitWithTriTurret(tempTriTurret)




    def StartShooting(self, ammoGFXid = None):
        blue.pyos.synchro.SleepSim(random.randint(0, 500))
        self.shooting = 1
        turretLen = len(self.turrets)
        if not turretLen:
            sm.GetService('FxSequencer').LogError('Entity unable to fire as it has no turrets fitted')
            return 
        offset = self.lastFiredID + random.randrange(1, turretLen)
        for turretID in range(turretLen):
            offset = (offset + turretID) % turretLen
            turret = self.turrets[offset]
            if turret.triTurret.canShoot:
                blue.pyos.synchro.SleepSim(random.randint(0, 100))
                turret.Shoot()
                for otherTurret in self.turrets:
                    if otherTurret != turret:
                        if otherTurret.source_sound:
                            otherTurret.source_sound.Stop()

                self.shooting = 0
                self.lastFiredID = offset
                return 

        for turret in self.turrets:
            if turret.targetOwner is None:
                return 

        elapsedTime = 0.0
        aimTime = self.turrets[0].triTurret.aimTime
        startTime = blue.os.GetSimTime()
        while elapsedTime < aimTime + 0.1:
            elapsedTime = float(blue.os.GetSimTime() - startTime) / 10000000.0
            for turret in self.turrets:
                if turret.triTurret.canShoot:
                    turret.Shoot()
                    sm.GetService('FxSequencer').LogInfo('Turret shot needed to wait ', elapsedTime, ' sec for target')
                    for otherTurret in self.turrets:
                        if otherTurret != turret:
                            if otherTurret.source_sound:
                                otherTurret.source_sound.Stop()

                    self.shooting = 0
                    return 

            blue.pyos.synchro.SleepSim(20)

        sm.GetService('FxSequencer').LogInfo('No turret in scope. No turret made hit')



    def SetAmmoColor(self, ammoTypeID):
        pass




class Turret():
    __persistvars__ = ['triTurret',
     'targetOwner',
     'owner',
     'timecurves',
     'soundcurves',
     'source_sound',
     'dest_sound',
     'vxOwners',
     'lightbulb',
     'guntype',
     'lightbulbInScene',
     'ammoColorName']
    __guid__ = 'turret.Turret'

    def __init__(self):
        self.triTurret = None
        self.targetOwner = None
        self.owner = None
        self.source_sound = None
        self.dest_sound = None
        self.lightbulb = None
        self.guntype = 'e'
        self.vxOwners = []
        self.timecurves = []
        self.soundcurves = []
        self.lightbulbInScene = 0



    def Initialize(self, race, weaponSize, weaponType, weaponId, techlevel, ammo, audio = 0):
        self.Assemble(race, weaponSize, weaponType, weaponId, techlevel, ammo)
        for fluffname in ['accX',
         'DamX',
         'RofX',
         'capX']:
            self.ActivateFluff(fluffname, 0)

        return self.triTurret



    def InitWithTriTurret(self, triTurret):
        self.triTurret = triTurret.CopyTo()
        self.timecurves = self.triTurret.FindCurves()
        if self.triTurret.outburstSounds and len(self.triTurret.outburstSounds):
            self.source_sound = self.triTurret.outburstSounds[0]
            self.soundcurves.append(self.source_sound)
        if self.triTurret.impactSounds and len(self.triTurret.impactSounds):
            self.dest_sound = self.triTurret.impactSounds[0]
            self.soundcurves.append(self.dest_sound)



    def Assemble(self, race, weaponSize, weaponType, weaponId, techlevel, ammo):
        import blue
        if 'space' in sm.services and util.IsFullLogging():
            sm.GetService('space').LogInfo('turrets: race = -', race, '- weaponsize = -', weaponSize, '- techlevel = -', techlevel, '- ')
        base_filename = 'base_' + race + weaponSize + str(techlevel) + '_l33t.blue'
        self.triTurret = blue.os.LoadObject(turretpath + 'Base/' + base_filename)
        self.triTurret.constraint = -0.15
        self.triTurret.aimTime = 0.5
        if weaponSize == 'l':
            self.triTurret.treshold3 = 8000000.0
        elif weaponSize == 'h':
            self.triTurret.treshold0 = 6400000.0
            self.triTurret.treshold1 = 25000000.0
            self.triTurret.treshold2 = 25000000.0
            self.triTurret.treshold3 = 80000000.0
        idtext = '0' + str(weaponId)
        barrel_filename = 'barrel_' + weaponSize + weaponType + idtext + '_l33t.blue'
        barrel = blue.os.LoadObject(turretpath + 'Barrel/' + barrel_filename)
        self.triTurret.SetBarrel(barrel)
        self.triTurret.shootingCurve.ScaleTime(4.0)
        curves = self.triTurret.FindCurves()
        for curve in curves:
            self.timecurves.append(curve)
            curve.extrapolation = trinity.TRIEXT_CONSTANT

        if not hasattr(__builtin__, 'settings') or settings.public.audio.Get('audioEnabled', 1):
            size_and_type = weaponSize + weaponType + str(weaponId)
            f = blue.ResFile()
            outburst = 'res:/Sound/Turret/' + size_and_type + '.blue'
            if f.Open(outburst):
                node = blue.os.LoadObject(outburst)
                node.renderonce = 1
                self.source_sound = node
                self.soundcurves.append(node)
                self.triTurret.outburstSounds.append(self.source_sound)
            impact = 'res:/Sound/Turret/Impact/' + size_and_type + '.blue'
            if f.Open(impact):
                kode = blue.os.LoadObject(impact)
                kode.renderonce = 1
                self.dest_sound = kode
                self.triTurret.impactSounds.append(self.dest_sound)
                self.soundcurves.append(kode)
            del f



    def Shoot(self):
        if self.targetOwner is None:
            return 
        now = blue.os.GetSimTime()
        for curve in self.timecurves:
            curve.start = now

        for curve in self.soundcurves:
            curve.Play(0, 1)

        if self.lightbulb and not self.lightbulbInScene:
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            self.lightbulbInScene = 1
            scene.lights.append(self.lightbulb)



    def Release(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if self.lightbulbInScene and self.lightbulb in scene.lights:
            self.lightbulbInScene = 0
            scene.lights.remove(self.lightbulb)
        self.owner = None
        self.triTurret.target = None
        self.timecurves = []
        self.soundcurves = []
        self.source_sound = None
        self.dest_sound = None
        self.targetOwner = None
        self.RemoveVertexTarget()
        self.triTurret = None



    def Rest(self):
        self.triTurret.target = None
        self.targetOwner = None
        self.RemoveVertexTarget()



    def SetSubTarget(self, shipID, targetID, targetTf):
        if self.targetOwner is None:
            return 0
        if getattr(self.targetOwner, 'model', None) is None:
            return 0
        if len(targetTf) == 0:
            return 0
        self.triTurret.target = targetTf[0]
        return 1



    def SetTarget(self, shipID, targetID, targetTf):
        self.targetOwner = sm.GetService('michelle').GetBall(targetID)
        return self.SetSubTarget(shipID, targetID, targetTf)



    def RemoveVertexTarget(self):
        if self.vxOwners:
            sm.GetService('FxSequencer').LogInfo('Turret::RemoveVertexTarget')
            nodemanager.RemoveVertexTarget(self.vxOwners)
            self.vxOwners = []



    def TargetFX(self):
        blue.pyos.synchro.SleepSim(100)
        if self.triTurret.target:
            if not self.targetOwner:
                return 
            if self.targetOwner.id == session.shipid:
                self.targetOwner.FlashScreen(0.25, 0.1)
                v = trinity.TriVector(0.0, 0.0, -10.0)
                self.targetOwner.ShakeCamera(25, v)



    def ActivateFluff(self, fluffname, active):
        fluffname = fluffname.lower()
        for component in filter(lambda item: item.name.lower() == fluffname, self.triTurret.components):
            component.display = active




    def SetAmmoColor(self, color, colorName):
        if hasattr(self, 'ammoColorName'):
            if self.ammoColorName == colorName:
                return 
        for m in self.triTurret.Find('trinity.TriMaterial'):
            if m.name == 'ammo':
                m.emissive = color.emissive

        for stage in self.triTurret.Find('trinity.TriTextureStage'):
            if stage.name == 'ammo':
                stage.customColor = color.emissive

        if self.lightbulb is not None:
            self.SetLightBulbColor(color)
        self.ammoColorName = colorName



    def SetLightBulbColor(self, color):
        for key in self.lightbulb.diffuseCurve.keys:
            brightness = key.value.a
            key.value = color.emissive.CopyTo()
            key.value.Scale(brightness)
            key.value.a = brightness




    def AddLight(self):
        lightbulb = blue.os.LoadObject(turretlight)
        self.lightbulb = lightbulb
        lightbulb.attenuation1 = 0.0001
        lightbulb.priority = 10
        if self.guntype == 'p':
            mats = nodemanager.FindNodes(self.triTurret.outbursts, 'ammo', 'trinity.TriMaterial')
        else:
            mats = nodemanager.FindNodes(self.triTurret.beams, 'ammo', 'trinity.TriMaterial')
        if len(mats) == 0:
            sm.GetService('FxSequencer').LogInfo('Error: there is not ammo material on the turret ' + self.triTurret.name + ' using default color')
            ammoMat = trinity.TriMaterial()
            ammoMat.emissive.SetRGB(0.5, 0.4, 0.29)
            mats = [ammoMat]
        mat = mats[0]
        if self.guntype == 'p':
            tfs = []
            for each in self.triTurret.outbursts:
                tfs_temp = each.Find('trinity.TriTurretSprite')
                tfs = tfs + tfs_temp

        else:
            tfs = []
            for each in self.triTurret.beams:
                tfs_temp = each.Find('trinity.TriTurretSprite')
                tfs = tfs + tfs_temp

        scCurves = []
        for tf in tfs:
            if tf.scalingCurve is not None:
                scCurves.append(tf.scalingCurve)

        if len(scCurves) == 0:
            return 
        keyframes = []
        for curve in scCurves:
            for key in curve.keys:
                if key.time not in keyframes:
                    keyframes.append(key.time)


        keyframes.sort()
        newDisplayCurve = blue.os.CreateInstance('trinity.TriScalarCurve')
        newDisplayCurve.extrapolation = 1
        newDiffuseCurve = blue.os.CreateInstance('trinity.TriColorCurve')
        newDiffuseCurve.extrapolation = 1
        black = blue.os.CreateInstance('trinity.TriColor')
        peakvalue = 0.0
        for key in keyframes:
            totalvalue = 0.0
            for curve in scCurves:
                totalvalue = totalvalue + curve.GetVectorAt(key).Length()

            newDisplayCurve.AddKey(key, totalvalue, 0.0, 0.0, 2)
            if totalvalue > peakvalue:
                peakvalue = totalvalue

        newDisplayCurve.AddKey(key + 0.1, 0.0, 0.0, 0.0, 2)
        if peakvalue > 0.0:
            newDisplayCurve.ScaleValue(1 / peakvalue)
        else:
            print 'peakvalue is 0. something is wrong'
            return 
        for key in newDisplayCurve.keys:
            key.value = key.value * 1.1 - 0.1

        for key in newDisplayCurve.keys:
            scaledCol = mat.emissive.CopyTo()
            scaledCol.Scale(key.value)
            scaledCol.a = key.value
            newDiffuseCurve.AddKey(key.time, scaledCol, black, black, 2)

        if len(newDiffuseCurve.keys) > 0:
            newDiffuseCurve.Sort()
        else:
            print 'no keys found on newDiffuseCurve '
            return 
        if len(newDisplayCurve.keys) > 0:
            newDisplayCurve.Sort()
        else:
            print 'no keys found on newDisplayCurve '
            return 
        lightbulb.diffuseCurve = newDiffuseCurve
        lightbulb.displayCurve = newDisplayCurve
        self.timecurves.append(lightbulb.displayCurve)
        self.timecurves.append(lightbulb.diffuseCurve)
        lightbulb.trackTransform = self.owner



strLoc = ['locator_turret', 'locator_booster']

def HackLocators(lodgroup):
    locators = [ item for item in lodgroup.Find('trinity.TriSplTransform', -1, False, 3) if item[0].name.startswith('locator_') ]
    hackedLocators = {}
    for locator in locators:
        oldLocator = locator[0]
        parentList = locator[1]
        if not (oldLocator.name.startswith(strLoc[0]) or oldLocator.name.startswith(strLoc[1])):
            continue
        if oldLocator not in parentList:
            continue
        parentList.remove(oldLocator)
        newLocator = None
        if oldLocator.name in hackedLocators:
            for x in hackedLocators[oldLocator.name]:
                if x[0] is oldLocator:
                    newLocator = x[1]
                    break

        if not newLocator:
            newLocator = trinity.TriTransform()
            newLocator.translation = oldLocator.translation.CopyTo()
            newLocator.scaling = oldLocator.scaling.CopyTo()
            newLocator.rotation = oldLocator.rotation.CopyTo()
            newLocator.name = oldLocator.name
            newLocator.display = oldLocator.display
            newLocator.update = oldLocator.update
            newLocator.transformBaseFlags = oldLocator.transformBaseFlags
            if oldLocator.name in hackedLocators:
                hackedLocators[oldLocator.name].append((oldLocator, newLocator))
            else:
                hackedLocators[oldLocator.name] = [(oldLocator, newLocator)]
        parentList.append(newLocator)



exports = {'turret.HackLocators': HackLocators,
 'turret.Turret': Turret,
 'turret.TurretPair': TurretPair,
 'turret.MiningTurretPair': MiningTurretPair,
 'turret.EntityTurrets': EntityTurrets}

