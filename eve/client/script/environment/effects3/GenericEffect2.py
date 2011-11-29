import blue
import trinity
import audio2
FX_SCALE_EFFECT_NONE = 0
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_BOUNDING = 2
FX_USEBALLTRANSLATION = 1
FX_USEBALLROTATION = 2

class GenericEffect:
    __guid__ = 'effects.GenericEffect'
    __scaleTime__ = 1
    __blockingIO__ = False

    def _Key(trigger):
        return (trigger.shipID,
         trigger.moduleID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def _GetDuration():
        return 10000


    _GetDuration = staticmethod(_GetDuration)

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]
        self.gfx = None
        self.gfxModel = None



    def Prepare(self):
        pass



    def Start(self, duration):
        pass



    def Stop(self):
        pass



    def Repeat(self, duration):
        pass



    def GetBalls(self):
        return self.ballIDs



    def GetEffectShipID(self):
        return self.ballIDs[0]



    def GetEffectShipBall(self):
        michelle = sm.StartService('michelle')
        return michelle.GetBall(self.GetEffectShipID())



    def GetEffectTargetID(self):
        return self.ballIDs[1]



    def GetEffectTargetBall(self):
        michelle = sm.StartService('michelle')
        return michelle.GetBall(self.GetEffectTargetID())



    def PlayOldAnimations(self, tf):
        curveTypes = ['trinity.TriScalarCurve',
         'trinity.TriVectorCurve',
         'trinity.TriRotationCurve',
         'trinity.TriColorCurve']
        curves = tf.Find(curveTypes)
        now = blue.os.GetSimTime()
        for curve in curves:
            curve.start = now




    def PlayNamedAnimations(self, model, animName):
        if not model:
            return 
        for each in model.curveSets:
            if each.name == animName:
                each.Play()




    def FindCurveSet(self, name):
        if not model:
            return None
        for each in model.curveSets:
            if each.name == name:
                return each





class ShipEffect(GenericEffect):
    __guid__ = 'effects.ShipEffect'
    __scaling__ = FX_SCALE_EFFECT_BOUNDING
    __positioning__ = FX_USEBALLTRANSLATION | FX_USEBALLROTATION

    def Stop(self):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.fremove(self.gfxModel)
        self.gfx = None
        if self.gfxModel:
            self.gfxModel.translationCurve = None
            self.gfxModel.rotationCurve = None
        self.gfxModel = None



    def Prepare(self):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        if shipBall is None:
            raise RuntimeError('ShipEffect: no ball found')
        self.gfx = trinity.Load(self.__gfx__)
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect found')
        entity = audio2.AudEmitter('effect_' + str(shipID))
        obs = trinity.TriObserverLocal()
        obs.observer = entity
        if self.gfx.__bluetype__ in ('trinity.EveTransform',):
            self.gfx.observers.append(obs)
        for curve in self.gfx.Find('trinity.TriEventCurve'):
            if curve.name == 'audioEvents':
                curve.eventListener = entity

        self.gfxModel = trinity.EveRootTransform()
        if shipBall.model.__bluetype__ == 'trinity.EveShip2':
            self.gfxModel.modelRotationCurve = shipBall.model.modelRotationCurve
            self.gfxModel.modelTranslationCurve = shipBall.model.modelTranslationCurve
        self.gfxModel.children.append(self.gfx)
        if self.__scaling__ == FX_SCALE_EFFECT_BOUNDING:
            (shipBBoxMin, shipBBoxMax,) = shipBall.model.GetLocalBoundingBox()
            bBox = (max(-shipBBoxMin.x, shipBBoxMax.x) * 1.2, max(-shipBBoxMin.y, shipBBoxMax.y) * 1.2, max(-shipBBoxMin.z, shipBBoxMax.z) * 1.2)
            self.gfxModel.scaling = bBox
        elif self.__scaling__ == FX_SCALE_EFFECT_SYMMETRICAL:
            radius = shipBall.model.GetBoundingSphereRadius()
            originalScaling = self.gfx.scaling
            self.gfx.scaling = (radius * originalScaling[0], radius * originalScaling[1], radius * originalScaling[2])
            self.gfx.translation = shipBall.model.GetBoundingSphereCenter()
        self.gfxModel.name = self.__guid__
        if FX_USEBALLTRANSLATION & self.__positioning__:
            self.gfxModel.translationCurve = shipBall
        if FX_USEBALLROTATION & self.__positioning__:
            self.gfxModel.rotationCurve = shipBall
        if hasattr(shipBall, 'model') and hasattr(shipBall.model, 'renderLast'):
            self.gfxModel.renderLast = shipBall.model.renderLast
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(self.gfxModel)



    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        curveSets = self.gfx.curveSets
        if len(curveSets) > 0:
            if self.__scaleTime__:
                length = self.gfx.curveSets[0].GetMaxCurveDuration()
                if length > 0.0:
                    scaleValue = length / (duration / 1000.0)
                    self.gfx.curveSets[0].scale = scaleValue
            curveSets[0].Play()



    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        gfxModelChildren = self.gfxModel.children
        if len(gfxModelChildren):
            curveSets = gfxModelChildren[0].curveSets
            if len(curveSets):
                curveSets[0].Play()




class ShipRenderEffect(ShipEffect):
    __guid__ = 'effects.ShipRenderEffect'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def Prepare(self):
        ShipEffect.Prepare(self)
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        resPath = None
        if shipBall.model.mesh is None:
            if shipBall.model.highDetailMesh is not None:
                if hasattr(shipBall.model.highDetailMesh.object, 'geometryResPath'):
                    resPath = shipBall.model.highDetailMesh.object.geometryResPath
        else:
            resPath = shipBall.model.mesh.geometryResPath
        numAreas = -1
        if resPath is None:
            sm.StartService('FxSequencer').LogError("This effect could not determine the respath to use as it's model: ", self.__guid__, shipID)
            return 
        for mesh in self.gfxModel.Find('trinity.Tr2Mesh'):
            mesh.geometryResPath = resPath
            for area in mesh.Find('trinity.Tr2MeshArea'):
                area.count = numAreas


        normalScalingSize = shipBall.model.GetBoundingSphereRadius() * 0.01
        for parameter in self.gfxModel.Find('trinity.TriVector4Parameter'):
            if parameter.name == 'ScaleAlongNormal':
                originalValue = parameter.value
                parameter.value = (normalScalingSize * originalValue[0],
                 normalScalingSize * originalValue[1],
                 normalScalingSize * originalValue[2],
                 normalScalingSize * originalValue[3])

        slimItem = sm.StartService('michelle').GetItem(shipID)
        if hasattr(slimItem, 'dunRotation') and hasattr(shipBall.model, 'rotationCurve'):
            self.gfxModel.rotationCurve = shipBall.model.rotationCurve




class StretchEffect(GenericEffect):
    __guid__ = 'effects.StretchEffect'

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None



    def Stop(self):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.fremove(self.gfxModel)
        self.gfx.source.parentPositionCurve = None
        self.gfx.source.parentRotationCurve = None
        self.gfx.source.alignPositionCurve = None
        self.gfx.dest.parentPositionCurve = None
        self.gfx.dest.parentRotationCurve = None
        self.gfx.dest.alignPositionCurve = None
        self.gfx = None
        self.gfxModel = None



    def Prepare(self):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        targetID = self.GetEffectTargetID()
        targetBall = self.GetEffectTargetBall()
        if shipBall is None:
            raise RuntimeError('StretchEffect: no ball found')
        if not hasattr(shipBall, 'model') or shipBall.model is None:
            raise RuntimeError('StretchEffect: no model found')
        if targetBall is None:
            raise RuntimeError('StretchEffect: no target ball found')
        if not hasattr(targetBall, 'model') or targetBall.model is None:
            raise RuntimeError('StretchEffect: no target model found')
        self.gfx = blue.os.LoadObject(self.__gfx__)
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect found')
        srcAudio = audio2.AudEmitter('effect_source_' + str(shipID))
        destAudio = audio2.AudEmitter('effect_dest_' + str(targetID))
        if self.gfx.sourceObject:
            obs = trinity.TriObserverLocal()
            obs.front = (0.0, -1.0, 0.0)
            obs.observer = srcAudio
            self.gfx.sourceObject.observers.append(obs)
        if self.gfx.destObject:
            obs = trinity.TriObserverLocal()
            obs.front = (0.0, -1.0, 0.0)
            obs.observer = destAudio
            self.gfx.destObject.observers.append(obs)
        for eachSet in self.gfx.curveSets:
            for eachCurve in eachSet.curves:
                if eachCurve.__typename__ == 'TriEventCurve':
                    if eachCurve.name == 'audioEventsSource':
                        eachCurve.eventListener = srcAudio
                    elif eachCurve.name == 'audioEventsDest':
                        eachCurve.eventListener = destAudio


        self.gfxModel = self.gfx
        self.gfx.source = trinity.TriNearestBoundingPoint()
        self.gfx.dest = trinity.TriNearestBoundingPoint()
        self.gfx.source.parentPositionCurve = shipBall
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = targetBall
        self.gfx.dest.parentPositionCurve = targetBall
        self.gfx.dest.parentRotationCurve = targetBall
        self.gfx.dest.alignPositionCurve = shipBall
        if shipBall.__guid__ != 'spaceObject.Ship' and shipBall.__guid__ != 'spaceObject.EntityShip':
            self.gfx.source.boundingSize = trinity.TriVector(shipBall.radius, shipBall.radius, shipBall.radius)
        elif hasattr(shipBall.model, 'GetLocalBoundingBox'):
            (shipBBoxMin, shipBBoxMax,) = shipBall.model.GetLocalBoundingBox()
            if shipBBoxMin is None or shipBBoxMax is None:
                radius = shipBall.model.boundingSphereRadius
                center = shipBall.model.boundingSphereCenter
                minX = center[0] - radius
                minY = center[1] - radius
                minZ = center[2] - radius
                maxX = center[0] + radius
                maxY = center[1] + radius
                maxZ = center[2] + radius
                self.gfx.source.boundingSize.SetXYZ(1.2 * max(-minX, maxX), 1.2 * max(-minY, maxY), 1.2 * max(-minZ, maxZ))
            else:
                self.gfx.source.boundingSize.SetXYZ(1.2 * max(-shipBBoxMin.x, shipBBoxMax.x), 1.2 * max(-shipBBoxMin.y, shipBBoxMax.y), 1.2 * max(-shipBBoxMin.z, shipBBoxMax.z))
        else:
            raise RuntimeError('StretchEffect: needs GetLocalBoundingBox')
        if targetBall.__guid__ != 'spaceObject.Ship' and targetBall.__guid__ != 'spaceObject.EntityShip':
            self.gfx.dest.boundingSize = trinity.TriVector(targetBall.radius, targetBall.radius, targetBall.radius)
        elif hasattr(targetBall.model, 'GetLocalBoundingBox'):
            (shipBBoxMin, shipBBoxMax,) = targetBall.model.GetLocalBoundingBox()
            if shipBBoxMin is None or shipBBoxMax is None:
                radius = targetBall.model.boundingSphereRadius
                center = targetBall.model.boundingSphereCenter
                minX = center[0] - radius
                minY = center[1] - radius
                minZ = center[2] - radius
                maxX = center[0] + radius
                maxY = center[1] + radius
                maxZ = center[2] + radius
                self.gfx.dest.boundingSize.SetXYZ(1.2 * max(-minX, maxX), 1.2 * max(-minY, maxY), 1.2 * max(-minZ, maxZ))
            else:
                self.gfx.dest.boundingSize.SetXYZ(1.2 * max(-shipBBoxMin.x, shipBBoxMax.x), 1.2 * max(-shipBBoxMin.y, shipBBoxMax.y), 1.2 * max(-shipBBoxMin.z, shipBBoxMax.z))
        else:
            raise RuntimeError('StretchEffect: needs GetLocalBoundingBox')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(self.gfxModel)



    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect defined')
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            if self.__scaleTime__:
                length = self.gfx.curveSets[0].GetMaxCurveDuration()
                if length > 0.0:
                    scaleValue = length / (duration / 1000.0)
                    self.gfx.curveSets[0].scale = scaleValue
            self.gfx.curveSets[0].Play()



    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect defined')
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            self.gfx.curveSets[0].Play()




