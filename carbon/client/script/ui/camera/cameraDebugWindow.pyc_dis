#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/cameraDebugWindow.py
import uiconst
import uicls
import cameras
DEFAULT_Y_OFFSET = 1.55

class CameraDebugWindow(uicls.Window):
    __guid__ = 'uicls.CameraDebugWindow'
    default_windowID = 'CameraDebugWindow'
    default_width = 500
    default_height = 200

    def ApplyAttributes(self, attributes):
        super(uicls.CameraDebugWindow, self).ApplyAttributes(attributes)
        self.SetMinSize([self.default_width, self.default_height])
        self.SetCaption('Camera Debug Window')
        self.sr.content.padding = (5, 16, 5, 5)
        self.debugSelectionClient = sm.GetService('debugSelectionClient')
        self.cameraDebugClient = sm.GetService('cameraDebugClient')
        self.cameraClient = sm.GetService('cameraClient')
        self.cameraStack = uicls.Label(parent=self.sr.content, align=uiconst.TOPLEFT, text=self.PrintCameraStack())
        buttonContainer = uicls.Container(parent=self.sr.content, align=uiconst.TOBOTTOM, height=70, padding=(150, 0, 150, 0))
        self.toggleCamera = uicls.Button(parent=buttonContainer, align=uiconst.TOBOTTOM, label='Activate Normal Camera', func=self.OnToggleDebugCamera)
        self.toggleCamUpdate = uicls.Button(parent=buttonContainer, align=uiconst.TOBOTTOM, label='Toggle Camera Update', func=self.OnToggleDebugCameraUpdate, hint='Toggle between updating the debug, and normal camera.')
        self.showCamCheckBox = uicls.Checkbox(parent=buttonContainer, aligh=uiconst.TOBOTTOM, text='Show Normal Camera', checked=False, callback=self.OnSnowNormalCameraCheckbox)
        self.cameraClient.AddSharedCamera('Debug Camera', cameras.DebugCamera())
        if type(self.cameraClient.GetActiveCamera()) is cameras.DebugCamera:
            self.DisableDebugCamera()
        self.EnableDebugCamera()
        sm.GetService('navigation').hasControl = False

    def OnSnowNormalCameraCheckbox(self, checkBox):
        debugCam = self.cameraClient.GetSharedCamera('Debug Camera')
        debugCam.SetShowNormalCamera(checkBox.GetValue())

    def OnToggleDebugCamera(self, *args):
        activeCam = self.cameraClient.GetActiveCamera()
        debugCam = self.cameraClient.GetSharedCamera('Debug Camera')
        if activeCam is debugCam:
            self.DisableDebugCamera()
        else:
            self.EnableDebugCamera()

    def EnableDebugCamera(self):
        debugCamera = self.cameraClient.GetSharedCamera('Debug Camera')
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            self.debugSelectionClient.SelectPlayer()
            entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is not None:
            entPos = entity.position.position
            position = (entPos[0], entPos[1] + DEFAULT_Y_OFFSET, entPos[2])
            debugCamera.SetPointOfInterest(position)
            debugCamera.distance = 0.0
            if debugCamera not in self.cameraClient.GetCameraStack():
                self.cameraClient.PushActiveCamera(debugCamera)
        self.cameraStack.SetText(self.PrintCameraStack())
        self.toggleCamera.SetLabel('Activate Normal Camera')
        self.toggleCamUpdate.Enable()
        self.showCamCheckBox.Show()
        sm.GetService('navigation').hasControl = debugCamera.IsControlEnabled()
        debugCamera.SetShowNormalCamera(self.showCamCheckBox.GetValue())

    def DisableDebugCamera(self):
        self.cameraClient.PopActiveCamera()
        self.cameraStack.SetText(self.PrintCameraStack())
        self.toggleCamera.SetLabel('Activate Debug Camera')
        self.toggleCamUpdate.Disable()
        self.showCamCheckBox.Hide()
        sm.GetService('navigation').hasControl = True
        debugCam = self.cameraClient.GetSharedCamera('Debug Camera')
        debugCam.SetShowNormalCamera(False)

    def OnToggleDebugCameraUpdate(self, *args):
        self.cameraDebugClient.ToggleDebugCameraUpdate()

    def PrintCameraStack(self):
        stack = self.cameraClient.GetCameraStack()
        stackStr = ''
        for i, cam in enumerate(stack):
            stackStr += str(i) + ': ' + str(cam) + '\n'
            for behavior in cam.cameraBehaviors:
                stackStr += '\t' + str(behavior) + '\n'

        stackStr = stackStr.replace('<', '').replace('>', '')
        return stackStr

    def Close(self, *args, **kwds):
        if type(self.cameraClient.GetActiveCamera()) is cameras.DebugCamera:
            self.DisableDebugCamera()
        uicls.Window.Close(self, *args, **kwds)