import uiconst
import uicls
import uiutil
import trinity
import blue
import cameras
import weakref
import bluepy
import geo2

class UIRoot(uicls.Container):
    __guid__ = 'uicls.UIRoot'
    __renderObject__ = trinity.Tr2Sprite2dScene
    default_name = 'root'
    default_clearBackground = False
    default_backgroundColor = (0, 0, 0, 1)
    default_isFullscreen = True
    default_align = uiconst.ABSOLUTE
    default_dpiScaling = 1.0

    def PrepareProperties(self):
        self._rotationX = 0.0
        self._rotationY = 0.0
        self._rotationZ = 0.0



    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        myScene = self.GetRenderObject()
        if attributes.depthMax or attributes.depthMin:
            self.depthMin = attributes.depthMin
            self.depthMax = attributes.depthMax
            myScene.is2dRender = False
            myScene.is2dPick = False
            self.InitCamera()
        else:
            self.depthMin = 0
            self.depthMax = 0
            self.camera = None
        self.isFullscreen = attributes.isFullscreen or self.default_isFullscreen
        self.clearBackground = attributes.clearBackground or self.default_clearBackground
        self.backgroundColor = attributes.backgroundColor or self.default_backgroundColor
        self._dpiScaling = attributes.dpiScaling or self.default_dpiScaling
        renderJob = attributes.renderJob or uicore.uilib.GetRenderJob()
        renderJob.SetViewport().name = 'Set fullscreen viewport'
        updateStep = renderJob.Update(myScene)
        updateStep.name = attributes.name + ' Update'
        self.sceneObject = None
        renderSteps = [updateStep]
        if attributes.depthMax:
            pythonCallback = renderJob.PythonCB(self.camera)
            pythonCallback.name = attributes.name + ' Camera Update'
            self.viewStep = renderJob.SetView(self.camera.viewMatrix)
            self.projStep = renderJob.SetProjection(self.camera.projectionMatrix)
            renderSteps.append(pythonCallback)
            renderSteps.append(self.viewStep)
            renderSteps.append(self.projStep)
        self.renderTargetStep = None
        if attributes.renderTarget:
            self.renderTargetStep = renderJob.PushRenderTarget(attributes.renderTarget)
            renderSteps.append(self.renderTargetStep)
            myScene.clearBackground = True
            myScene.backgroundColor = (0, 0, 0, 1)
        renderStep = renderJob.RenderScene(myScene)
        renderStep.name = attributes.name + ' Render'
        renderSteps.append(renderStep)
        if attributes.renderTarget:
            renderSteps.append(renderJob.PopRenderTarget(attributes.renderTarget))
        self.renderSteps = renderSteps
        self.__dict__['rootIsReady'] = True



    def InitCamera(self):
        self.camera = cameras.UICamera()
        self.camera.desktop = self
        self.camera.AdjustForDesktop()
        self.camera.Update()



    def GetCamera(self):
        return self.camera



    def UpdateCamera(self):
        print 'Updating camera'



    def Create3DRenderTarget(self, destscene):
        sprite = blue.os.LoadObject('res:/uicore/uiInSpace.red')
        area = sprite.mesh.opaqueAreas[0]
        texture = area.effect.resources[0]
        destscene.objects.append(sprite)
        rj = trinity.CreateRenderJob()
        rj.Update(destscene)
        myScene = self.GetRenderObject()
        renderTarget = trinity.device.CreateTexture(self.width, self.height, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_DEFAULT)
        rj.PushRenderTarget(renderTarget.GetSurfaceLevel(0))
        rj.RenderScene(myScene).name = 'Render 2D scene'
        rj.PopRenderTarget()
        rj.ScheduleRecurring(insertFront=True)
        texture.SetResource(renderTarget)
        myScene.is2dRender = True
        self.sceneObject = blue.BluePythonWeakRef(sprite)
        self.renderSteps[-1].enabled = False



    def GetInSceneObject(self):
        if self.sceneObject:
            return self.sceneObject.object



    def CheckMouseMove(self, *args):
        if uicore.uilib.leftbtn and uicore.uilib.Key(uiconst.VK_MENU):
            if uicore.uilib.rightbtn:
                self.camera.distance -= uicore.uilib.dy
            else:
                self.camera.AdjustYaw(-uicore.uilib.dx * 0.1)
                self.camera.AdjustPitch(-uicore.uilib.dy * 0.1)
        return 1



    def _OnClose(self, *args, **kwds):
        if self.renderSteps:
            renderJob = uicore.uilib.GetRenderJob()
            if renderJob:
                for each in self.renderSteps:
                    if each in renderJob.steps:
                        renderJob.steps.remove(each)

        uicore.uilib.RemoveRootObject(self)
        uicls.Container._OnClose(self, *args, **kwds)



    def AddLayer(self, name, decoClass = None, subLayers = None, idx = -1, loadLayerClass = False):
        useClass = decoClass or uicls.LayerCore
        layer = useClass(parent=self, name=name, idx=idx, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        layer.decoClass = decoClass
        uicore.layerData[name] = (useClass, subLayers)
        if name.startswith('l_'):
            setattr(uicore.layer, name[2:].lower(), layer)
        else:
            setattr(uicore.layer, name.lower(), layer)
        if subLayers is not None:
            for (_layerName, _decoClass, _subLayers,) in subLayers:
                layer.AddLayer(_layerName, _decoClass, _subLayers)

        return layer



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAlignment(self):
        self._alignmentDirty = False
        self.displayWidth = self.ScaleDpi(self.width)
        self.displayHeight = self.ScaleDpi(self.height)
        self.FlagAlignmentDirty()
        for each in self.children:
            if each.display:
                each.FlagAlignmentDirty()

        budget = (0,
         0,
         self.displayWidth,
         self.displayHeight)
        orgBudget = (0,
         0,
         self.displayWidth,
         self.displayHeight)
        for each in self.children:
            if each.display:
                each.Traverse(budget, orgBudget, 1)




    def UpdateSize(self):
        if self.isFullscreen and not self.renderTargetStep:
            self.width = int(float(trinity.device.width) / self.dpiScaling)
            self.height = int(float(trinity.device.height) / self.dpiScaling)
            self.renderObject.isFullscreen = True
        if self.camera:
            self.camera.AdjustForDesktop()
        self.FlagAlignmentDirty()
        self._displayDirty = True
        for each in self.children:
            if each.display:
                each._displayDirty = True
                each.FlagAlignmentDirty()




    def GetAbsoluteSize(self):
        return (self.width, self.height)



    def GetAbsolutePosition(self):
        return (0, 0)



    @apply
    def dpiScaling():
        doc = 'DPI scaling - scale the UI independent of resolution'

        def fget(self):
            return self._dpiScaling



        def fset(self, value):
            self._dpiScaling = value
            ro = self.renderObject
            if ro:
                ro.dpiScaling = value
            self.UpdateSize()
            for each in uicore.textObjects:
                each.OnCreate(trinity.device)



        return property(**locals())



    @apply
    def rotationY():
        doc = 'Rotation around the y-axis'

        def fget(self):
            return self._rotationY



        def fset(self, value):
            self._rotationY = value
            ro = self.renderObject
            if ro:
                ro.rotation = geo2.QuaternionRotationSetYawPitchRoll(self._rotationY, self._rotationX, self._rotationZ)


        return property(**locals())



    @apply
    def clearBackground():
        doc = '\n        If set, background is cleared to backgroundColor before the desktop is rendered\n        '

        def fget(self):
            return self.renderObject.clearBackground



        def fset(self, value):
            self.renderObject.clearBackground = value


        return property(**locals())



    @apply
    def backgroundColor():
        doc = '\n        If clearBackground is set, the background is cleared to this color before the\n        desktop is rendered\n        '

        def fget(self):
            return self.renderObject.backgroundColor



        def fset(self, value):
            self.renderObject.backgroundColor = value


        return property(**locals())




