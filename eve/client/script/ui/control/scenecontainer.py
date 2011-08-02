import sys
import blue
import uthread
import uiutil
import xtriui
import form
import trinity
import util
import base
import math
import log
import triui
import lg
import destiny
import dbg
import bluepy
import uicls
import uiconst
import bitmapjob

class SceneContainer(uicls.Base):
    __guid__ = 'form.SceneContainer'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def ApplyAttributes(self, attributes):
        self.viewport = trinity.TriViewport()
        self.viewport.x = 0
        self.viewport.y = 0
        self.viewport.width = 1
        self.viewport.height = 1
        self.viewport.minZ = 0.0
        self.viewport.maxZ = 1.0
        self.projection = trinity.TriProjection()
        self.renderJob = None
        self.frontClip = 1.0
        self.backClip = 350000.0
        self.fieldOfView = 1.0
        self.minPitch = -1.4
        self.maxPitch = 1.4
        uicls.Base.ApplyAttributes(self, attributes)



    def Startup(self, *args):
        self.PrepareCamera()
        self.scene = None
        self.DisplayScene()



    def PrepareSpaceScene(self, maxPitch = 1.4, scenePath = None):
        if scenePath is None:
            scenePath = 'res:/dx9/scene/fitting/fitting.red'
        self.scene = trinity.Load(scenePath)
        self.frontClip = 1.0
        self.backClip = 350000.0
        self.fieldOfView = 1.0
        self.minPitch = -1.4
        self.maxPitch = maxPitch
        self.SetupCamera()
        self.DisplayScene()



    def PrepareInteriorScene(self):
        self.scene = trinity.Load('res:/Graphics/Interior/characterCreation/Preview.red')
        self.frontClip = 0.01
        self.backClip = 100.0
        self.fieldOfView = 0.3
        self.minPitch = -0.6
        self.maxPitch = 0.6
        self.SetupCamera()
        blue.resMan.Wait()
        self.DisplayScene(addClearStep=True, addBitmapStep=True)



    def SetupCamera(self):
        self.camera.frontClip = self.frontClip
        self.camera.backClip = self.backClip
        self.camera.fieldOfView = self.fieldOfView
        self.camera.minPitch = self.minPitch
        self.camera.maxPitch = self.maxPitch



    def PrepareCamera(self):
        self.cameraParent = trinity.TriTransform()
        self.cameraParent.useCurves = 1
        self.cameraParent.translationCurve = trinity.EveSO2ModelCenterPos()
        self.camera = trinity.EveCamera()
        self.camera.parent = self.cameraParent



    def DisplayScene(self, addClearStep = False, addBitmapStep = False):
        self.renderJob = trinity.CreateRenderJob('SceneInScene')
        self.renderJob.SetViewport(self.viewport)
        self.projection.PerspectiveFov(self.fieldOfView, self.viewport.GetAspectRatio(), self.frontClip, self.backClip)
        self.renderJob.SetProjection(self.projection)
        self.renderJob.SetView(None, self.camera, self.cameraParent)
        self.renderJob.Update(self.scene)
        if addClearStep:
            self.renderJob.Clear((0.2, 0.2, 0.2, 1.0), 1.0)
        if addBitmapStep:
            backgroundImage = 'res:/UI/Texture/preview/asset_preview_background.png'
            step = bitmapjob.makeBitmapStep(backgroundImage, scaleToFit=False, color=(1.0, 1.0, 1.0, 1.0))
            self.renderJob.steps.append(step)
        self.renderJob.RenderScene(self.scene)
        self.renderObject.renderJob = self.renderJob



    def SetStencilMap(self, path = 'res:/UI/Texture/circleStencil.dds'):
        stencilMap = trinity.TriTexture2DParameter()
        stencilMap.name = 'StencilMap'
        stencilMap.resourcePath = path
        self.scene.backgroundEffect.resources.append(stencilMap)
        self.scene.backgroundEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/NebulaWithStencil.fx'



    def AddToScene(self, model, clear = 1):
        if model == None:
            return 
        if clear:
            del self.scene.objects[:]
            self.scene.objects.append(model)
        self.scene.UpdateScene(blue.os.GetTime(1))
        self.cameraParent.translationCurve.parent = model
        self.camera.rotationOfInterest.SetIdentity()



    def ClearScene(self):
        self.scene.UpdateScene(blue.os.GetTime(1))
        del self.scene.objects[:]



    def _OnResize(self):
        self.UpdateViewPort()



    def UpdateViewPort(self, *args):
        (l, t, w, h,) = self.GetAbsolute()
        if not w and not h:
            return 
        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = w
        self.viewport.height = h
        self.projection.PerspectiveFov(self.fieldOfView, self.viewport.GetAspectRatio(), self.frontClip, self.backClip)



    def OnResize_(self, k, v):
        self.UpdateViewPort()



    def _OnClose(self, *args):
        self.clearStep = None
        self.scene = None




class SceneWindowTest(uicls.Window):
    __guid__ = 'form.SceneWindowTest'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        sc = form.SceneContainer(uicls.Frame(parent=self.sr.main, padding=(6, 6, 6, 6)))
        sc.Startup()
        nav = SceneContainerBaseNavigation(uicls.Container(parent=self.sr.main, left=6, top=6, width=6, height=6, idx=0, state=uiconst.UI_NORMAL))
        nav.Startup(sc)
        self.sr.navigation = nav
        self.sr.sceneContainer = sc



    def OnResizeUpdate(self, *args):
        self.sr.sceneContainer.UpdateViewPort()




class SceneContainerBaseNavigation(uicls.Container):
    __guid__ = 'form.SceneContainerBaseNavigation'

    def init(self):
        self.sr.cookie = None
        self.isTabStop = 1



    def Startup(self, sceneContainer):
        self.sr.sceneContainer = sceneContainer
        self.minZoom = 10.0
        self.maxZoom = 3000.0
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self._OnGlobalMouseUp)



    def _OnClose(self, *args):
        if self.sr.cookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie)
            self.sr.cookie = None



    def SetMinMaxZoom(self, minZoom, maxZoom):
        self.minZoom = minZoom
        self.maxZoom = maxZoom
        self.CheckCameraTranslation()



    def CheckCameraTranslation(self):
        self.sr.sceneContainer.camera.translationFromParent.z = min(self.maxZoom, max(self.minZoom, self.sr.sceneContainer.camera.translationFromParent.z))



    def OnMouseWheel(self, *args):
        self.sr.sceneContainer.camera.Dolly(uicore.uilib.dz * 0.001 * abs(self.sr.sceneContainer.camera.translationFromParent.z))
        self.CheckCameraTranslation()



    def OnMouseMove(self, *args):
        lib = uicore.uilib
        dx = lib.dx
        dy = lib.dy
        fov = self.sr.sceneContainer.camera.fieldOfView
        cameraSpeed = 3.0
        ctrl = lib.Key(uiconst.VK_CONTROL)
        if lib.leftbtn and not lib.rightbtn:
            self.sr.sceneContainer.camera.OrbitParent(-dx * fov * 0.2 * cameraSpeed, dy * fov * 0.2 * cameraSpeed)
        if lib.leftbtn and lib.rightbtn:
            self.sr.sceneContainer.camera.Dolly(-(dy * 0.01) * abs(self.sr.sceneContainer.camera.translationFromParent.z))
            self.CheckCameraTranslation()
            if ctrl:
                self.sr.sceneContainer.camera.fieldOfView = -dx * 0.01 + fov
                if self.sr.sceneContainer.camera.fieldOfView > 1.0:
                    self.sr.sceneContainer.camera.fieldOfView = 1.0
                if self.sr.sceneContainer.camera.fieldOfView < 0.1:
                    self.sr.sceneContainer.camera.fieldOfView = 0.1
            else:
                self.sr.sceneContainer.camera.OrbitParent(dx * fov * 0.2, 0.0)



    def _OnGlobalMouseUp(self, wnd, msgID, btn, *args):
        if btn and btn[0] == 1:
            self.sr.sceneContainer.camera.rotationOfInterest.SetIdentity()
        return 1




