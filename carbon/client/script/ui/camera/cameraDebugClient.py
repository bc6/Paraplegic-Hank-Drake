import service
import uiconst
import uicls
import cameras
DEFAULT_Y_OFFSET = 1.55

class CameraDebugWindow(uicls.WindowCore):
    __guid__ = 'uicls.CameraDebugWindow'
    default_windowID = 'CameraDebugWindow'
    ENTRY_FONTSIZE = 11
    HEADER_FONTSIZE = 12
    ENTRY_FONT = 'res:/UI/Fonts/arial.ttf'
    HEADER_FONT = 'res:/UI/Fonts/arialbd.ttf'
    ENTRY_LETTERSPACE = 1

    def ApplyAttributes(self, attributes):
        super(uicls.CameraDebugWindow, self).ApplyAttributes(attributes)
        self.SetMinSize([500, 200])
        self.SetSize(500, 200)
        self.SetCaption('Camera Debug Window')
        self.sr.content.SetPadding(5, 5, 5, 5)
        self.debugSelectionClient = sm.GetService('debugSelectionClient')
        self.cameraDebugClient = sm.GetService('cameraDebugClient')
        self.cameraClient = sm.GetService('cameraClient')
        self.cameraStack = uicls.LabelCore(parent=self.sr.content, align=uiconst.TOPLEFT, text=self.PrintCameraStack(), padding=(0, 0, 0, 0))
        uicls.ButtonCore(parent=self.sr.content, align=uiconst.BOTTOMLEFT, label='Enable Debug Camera', padding=(0, 0, 0, 0), func=self.OnDebugCameraButton)
        uicls.ButtonCore(parent=self.sr.content, align=uiconst.BOTTOMRIGHT, label='Disable Debug Camera', padding=(0, 0, 0, 0), func=self.OnRemoveDebugCameraButton)
        debugCamera = cameras.DebugCamera()
        debugCamera.AddBehavior(cameras.FlyCameraBehavior())
        self.cameraClient.AddSharedCamera('Debug Camera', debugCamera)



    def OnDebugCameraButton(self, button):
        debugCamera = self.cameraClient.GetSharedCamera('Debug Camera')
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is not None:
            entPos = entity.position.position
            position = (entPos[0], entPos[1] + DEFAULT_Y_OFFSET, entPos[2])
            debugCamera.SetPointOfInterest(position)
            debugCamera.distance = 0.0
            if debugCamera not in self.cameraClient.GetCameraStack():
                self.cameraClient.PushActiveCamera(debugCamera)
        self.cameraStack.SetText(self.PrintCameraStack())



    def OnRemoveDebugCameraButton(self, button):
        self.cameraClient.PopActiveCamera()
        self.cameraStack.SetText(self.PrintCameraStack())



    def PrintCameraStack(self):
        stack = self.cameraClient.GetCameraStack()
        stackStr = ''
        for (i, cam,) in enumerate(stack):
            stackStr += str(i) + ': ' + str(cam) + '\n'
            for behavior in cam.cameraBehaviors:
                stackStr += '\t' + str(behavior) + '\n'


        stackStr = stackStr.replace('<', '').replace('>', '')
        return stackStr




class CameraDebugClient(service.Service):
    __guid__ = 'svc.cameraDebugClient'
    __dependencies__ = ['debugSelectionClient', 'debugRenderClient', 'cameraClient']

    def __init__(self, *args):
        service.Service.__init__(self, *args)



    def Run(self, *args):
        service.Service.Run(self, *args)
        self.RegisterKeyEvents()



    def RegisterKeyEvents(self):
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyDownCallback)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)



    def UnRegisterKeyEvents(self):
        if self.keyDownCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
            self.keyDownCookie = None
        if self.keyUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
            self.keyUpCookie = None



    def OnGlobalKeyDownCallback(self, wnd, eventID, (vkey, flag,)):
        activeCamera = self.cameraClient.GetActiveCamera()
        flyCam = activeCamera.GetBehavior(cameras.FlyCameraBehavior)
        if flyCam is not None:
            vec = flyCam.GetTranslationVector()
            if vkey == uiconst.VK_UP:
                vec[2] = -1.0
            if vkey == uiconst.VK_RIGHT:
                vec[0] = 1.0
            if vkey == uiconst.VK_DOWN:
                vec[2] = 1.0
            if vkey == uiconst.VK_LEFT:
                vec[0] = -1.0
            flyCam.SetTranslationVector(vec)
        return True



    def OnGlobalKeyUpCallback(self, wnd, eventID, (vkey, flag,)):
        activeCamera = self.cameraClient.GetActiveCamera()
        flyCam = activeCamera.GetBehavior(cameras.FlyCameraBehavior)
        if flyCam is not None:
            vec = flyCam.GetTranslationVector()
            if vkey in (uiconst.VK_UP, uiconst.VK_DOWN):
                vec[2] = 0.0
            if vkey in (uiconst.VK_LEFT, uiconst.VK_RIGHT):
                vec[0] = 0.0
            flyCam.SetTranslationVector(vec)
        return True




