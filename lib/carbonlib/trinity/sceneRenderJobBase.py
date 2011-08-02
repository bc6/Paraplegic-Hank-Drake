import trinity
import blue
import bluepy
import geo2

class SceneRenderJobBase(object):
    __cid__ = 'trinity.TriRenderJob'
    __metaclass__ = bluepy.BlueWrappedMetaclass
    renderStepOrder = []
    multiViewStages = None
    visualizations = []
    stereoEnabled = False

    def Start(self):
        if not self.scheduled:
            trinity.device.scheduledRecurring.insert(0, self)
            self.scheduled = True



    def Pause(self):
        if self.scheduled:
            self.UnscheduleRecurring()
            self.scheduled = False



    def UnscheduleRecurring(self, scheduledRecurring = None):
        if scheduledRecurring is None:
            scheduledRecurring = trinity.device.scheduledRecurring
        if self in scheduledRecurring:
            scheduledRecurring.remove(self)



    def ScheduleOnce(self):
        if not self.enabled:
            self.enabled = True
            try:
                self.DoPrepareResources()
            except trinity.D3DError:
                pass
        trinity.device.scheduledOnce.append(self)



    def WaitForFinish(self):
        while not (self.status == trinity.RJ_DONE or self.status == trinity.RJ_FAILED):
            blue.synchro.Yield()




    def Disable(self):
        self.enabled = False
        self.DoReleaseResources(1)
        if self.scheduled:
            trinity.device.scheduledRecurring.remove(self)
            self.scheduled = False



    def Enable(self):
        self.enabled = True
        try:
            self.DoPrepareResources()
        except trinity.D3DError:
            pass
        self.Start()



    def GetRenderStepOrderList(self):
        if self.multiViewStages is not None and self.currentMultiViewStageKey is not None:
            for (stageName, sharedSetupStep, stepList,) in self.multiViewStages:
                if stageName == self.currentMultiViewStageKey:
                    return stepList

            return 
        return self.renderStepOrder



    def _AddStereoStep(self, step):
        if not self.stereoEnabled:
            return 
        index = self.steps.index(step)
        startLeft = -1
        startRight = -1
        for (i, step,) in enumerate(self.steps):
            if step.name == 'UPDATE_STEREO':
                startLeft = i
            elif step.name == 'UPDATE_STEREO_RIGHT':
                startRight = i

        if startLeft < 0 or startRight < 0:
            return 
        if index > startLeft and index < startRight:
            self.steps.insert(startRight + index - startLeft, step)
        elif index > startRight:
            self.steps.insert(startLeft + index - startRight, step)



    def AddStep(self, stepKey, step):
        renderStepOrder = self.GetRenderStepOrderList()
        if renderStepOrder is None:
            return 
        else:
            if stepKey not in renderStepOrder:
                return 
            if stepKey in self.stepsLookup:
                s = self.stepsLookup[stepKey]
                if s.object is None:
                    del self.stepsLookup[stepKey]
                else:
                    replaceIdx = self.steps.index(s.object)
                    if replaceIdx >= 0:
                        while True:
                            try:
                                self.steps.remove(s.object)
                            except:
                                break

                        self.steps.insert(replaceIdx, step)
                        step.name = stepKey
                        self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
                        self._AddStereoStep(step)
                        return step
            stepIdx = renderStepOrder.index(stepKey)
            nextExistingStepIdx = None
            nextExistingStep = None
            for (i, oStep,) in enumerate(renderStepOrder[(stepIdx + 1):]):
                if oStep in self.stepsLookup and self.stepsLookup[oStep].object is not None:
                    nextExistingStepIdx = i + stepIdx
                    nextExistingStep = self.stepsLookup[oStep].object
                    break

            if nextExistingStepIdx is not None:
                insertPosition = self.steps.index(nextExistingStep)
                self.steps.insert(insertPosition, step)
                step.name = stepKey
                self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
                self._AddStereoStep(step)
                return step
            step.name = stepKey
            self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
            self.steps.append(step)
            self._AddStereoStep(step)
            return step



    def HasStep(self, stepKey):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                return True
        return False



    def RemoveStep(self, stepKey):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                while True:
                    try:
                        self.steps.remove(s)
                    except:
                        break

            del self.stepsLookup[stepKey]



    def EnableStep(self, stepKey):
        self.SetStepAttr(stepKey, 'enabled', True)



    def DisableStep(self, stepKey):
        self.SetStepAttr(stepKey, 'enabled', False)



    def GetStep(self, stepKey):
        if stepKey in self.stepsLookup:
            return self.stepsLookup[stepKey].object



    def SetStepAttr(self, stepKey, attr, val):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                setattr(s, attr, val)



    def GetScene(self):
        if self.scene is None:
            return 
        else:
            return self.scene.object



    def GetVisualizationsForRenderjob(self):
        return self.visualizations



    def AppendRenderStepToRenderStepOrder(self, renderStep):
        if renderStep not in self.renderStepOrder:
            self.renderStepOrder.append(renderStep)



    def ApplyVisualization(self, vis):
        if self.appliedVisualization is not None:
            self.appliedVisualization.RemoveVisualization(self)
            self.appliedVisualization = None
        if vis is not None:
            visInstance = vis()
            visInstance.ApplyVisualization(self)
            self.appliedVisualization = visInstance



    def ManualInit(self, name = 'BaseSceneRenderJob'):
        self.name = name
        self.scene = None
        self.stepsLookup = {}
        self.enabled = False
        self.scheduled = False
        self.canCreateRenderTargets = True
        self.appliedVisualization = None
        self.currentMultiViewStageKey = None
        self.view = None
        self.projection = None
        self._ManualInit(name)



    def DoPrepareResources(self):
        raise NotImplementedError('You must provide an implementation of DoPrepareResources(self)')



    def DoReleaseResources(self, level):
        raise NotImplementedError('You must provide an implementation of DoReleaseResources(self, level)')



    def SetScene(self, scene):
        if scene is None:
            self.scene = None
        else:
            self.scene = blue.BluePythonWeakRef(scene)
        self._SetScene(scene)



    def CreateBasicRenderSteps(self):
        self.steps.removeAt(-1)
        self.stepsLookup = {}
        self._CreateBasicRenderSteps()



    def SetRenderTargetCreationEnabled(self, enabled):
        self.canCreateRenderTargets = enabled
        if enabled:
            try:
                self.DoPrepareResources()
            except trinity.D3DError:
                pass



    def SetMultiViewStage(self, stageKey):
        self.currentMultiViewStageKey = stageKey
        validStepList = self.GetRenderStepOrderList()
        if validStepList:
            for stepID in self.stepsLookup.keys():
                if stepID not in validStepList:
                    self.RemoveStep(stepID)




    def GetRenderTargets(self):
        raise NotImplementedError('You must provide an implementation of GetRenderTargets(self)')



    def SetRenderTargets(self):
        raise NotImplementedError('You must provide an implementation of SetRenderTargets(self, ...)')



    def SetCameraView(self, view):
        if view is None:
            self.RemoveStep('SET_VIEW')
            self.view = None
        else:
            self.AddStep('SET_VIEW', trinity.TriStepSetView(view))
            self.view = blue.BluePythonWeakRef(view)



    def SetCameraProjection(self, proj):
        if proj is None:
            self.RemoveStep('SET_PROJECTION')
            self.projection = None
        else:
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(proj))
            if self.stereoEnabled:
                self.originalProjection = blue.BluePythonWeakRef(proj)
            else:
                self.projection = blue.BluePythonWeakRef(proj)



    def SetActiveCamera(self, camera):
        self.SetCameraView(camera.viewMatrix)
        self.SetCameraProjection(camera.projectionMatrix)



    def SetClearColor(self, color):
        step = self.GetStep('CLEAR')
        if step is not None:
            step.color = color



    def _StereoUpdateViewProjection(self, eye):
        if self.originalProjection.object.transform[2][3] != 0:
            offset = trinity.stereoSupport.GetEyeSeparation() * trinity.stereoSupport.GetSeparation()
            if eye == trinity.STEREO_EYE_LEFT:
                offset = -offset
            projection = (self.originalProjection.object.transform[0],
             self.originalProjection.object.transform[1],
             geo2.Vec4Add(self.originalProjection.object.transform[2], (-offset,
              0,
              0,
              0)),
             geo2.Vec4Add(self.originalProjection.object.transform[3], (-offset * trinity.stereoSupport.GetConvergence(),
              0,
              0,
              0)))
            self.projection.object.CustomProjection(projection)
            trinity.stereoSupport.SetActiveEye(eye)



    def EnableStereo(self, enable):
        if enable == self.stereoEnabled:
            return True
        if enable:

            def leftCallback():
                return self._StereoUpdateViewProjection(trinity.STEREO_EYE_LEFT)



            def rightCallback():
                return self._StereoUpdateViewProjection(trinity.STEREO_EYE_RIGHT)


            leftUpdate = self.AddStep('UPDATE_STEREO', trinity.TriStepPythonCB())
            if leftUpdate is None:
                return False
            leftUpdate.SetCallback(leftCallback)
            self.originalProjection = self.projection
            self.stereoProjection = trinity.TriProjection()
            self.SetCameraProjection(self.stereoProjection)
            rightUpdate = trinity.TriStepPythonCB()
            rightUpdate.name = 'UPDATE_STEREO_RIGHT'
            rightUpdate.SetCallback(rightCallback)
            self.steps.append(rightUpdate)
            index = -1
            try:
                index = self.steps.index(self.GetStep('UPDATE_STEREO'))
            except:
                pass
            if index >= 0:
                count = len(self.steps)
                for i in range(index + 1, count - 1):
                    step = self.steps[i]
                    self.steps.append(step)

            self.stereoEnabled = True
        else:
            index = -1
            for (i, step,) in enumerate(self.steps):
                if step.name == 'UPDATE_STEREO_RIGHT':
                    index = i
                    break

            if index >= 0:
                while len(self.steps) > index:
                    self.steps.removeAt(index)

            self.stereoEnabled = False
            self.RemoveStep('UPDATE_STEREO')
            self.SetCameraProjection(self.originalProjection.object)
        return True




