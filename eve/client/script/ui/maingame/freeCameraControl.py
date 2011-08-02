import uicls
import uiconst
import cameras
import uthread
import blue

class FreeCameraControl(uicls.LayerCore):
    __guid__ = 'uicls.FreeCameraControl'

    def ApplyAttributes(self, *args, **kw):
        uicls.LayerCore.ApplyAttributes(self, *args, **kw)
        self.cameraClient = sm.GetService('cameraClient')
        self.gameui = sm.GetService('gameui')
        self.storedMousePos = None



    def GetMenu(self):
        if not eve.session.stationid:
            return []
        menu = []
        if eve.session.shipid:
            hangarInv = eve.GetInventory(const.containerHangar)
            hangarItems = hangarInv.List()
            for each in hangarItems:
                if each.itemID == eve.session.shipid:
                    menu = sm.GetService('menu').InvItemMenu(each)

        if menu:
            menu.append(None)
        menu.append(('Corporation', uicore.cmd.OpenCorporationPanel, ()))
        menu.append(('Science & Industry', uicore.cmd.OpenFactories, ()))
        menu.append(('Character Customization (In Development)', uicore.cmd.OpenCharacterCustomization, ()))

        def TalkToAura():
            agentService = sm.GetService('agents')
            auraID = agentService.GetAuraAgentID()
            agentService.InteractWith(auraID)


        menu.append(('Talk to Aura', TalkToAura, ()))
        return menu



    def Startup(self):
        sceneManager = sm.GetService('sceneManager')
        camera = sceneManager.GetRegisteredCamera('freeCamera')
        if camera is None:
            camera = cameras.FreeCamera()
            sceneManager.RegisterCamera('freeCamera', camera)
        self.cameraClient.PushActiveCamera(camera)
        self.keydownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.KeyDown)
        self.keyupCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.KeyUp)
        self.pressedKeys = set([])
        self.updateKeysTasklet = uthread.new(self.UpdateKeyInput)
        self.updateKeysTasklet.context = 'FreeCameraControl::OnOpenView'



    def _OnClose(self, *args, **kw):
        self.cameraClient.PopActiveCamera()
        self.updateKeysTasklet.kill()
        uicore.event.UnregisterForTriuiEvents(self.keydownCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyupCookie)
        uicls.LayerCore._OnClose(self, *args, **kw)



    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.cursor = uiconst.UICURSOR_NONE
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
            uicore.uilib.SetCapture(self)
            self.storedMousePos = (uicore.uilib.x, uicore.uilib.y)
            uicore.uilib.centerMouse = True
        return True



    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.capture == self:
                uicore.uilib.ReleaseCapture()
            uicore.uilib.centerMouse = False
            self.storedMousePos = None
            self.cursor = uiconst.UICURSOR_DEFAULT
        return True



    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            lib = uicore.uilib
            dx = lib.dx
            dy = lib.dy
            mouseLookSpeed = 0.005
            camera = sm.GetService('sceneManager').GetRegisteredCamera('freeCamera')
            camera.RotateCamera(-dx * mouseLookSpeed, -dy * mouseLookSpeed, 0)
        return True



    def KeyDown(self, wnd, eventID, (vkey, flag,)):
        if hasattr(uicore.registry.GetFocus(), 'OnChar'):
            self.pressedKeys.clear()
            return True
        if vkey == 87:
            self.pressedKeys.add('W')
        if vkey == 65:
            self.pressedKeys.add('A')
        if vkey == 83:
            self.pressedKeys.add('S')
        if vkey == 68:
            self.pressedKeys.add('D')
        if vkey == 82:
            self.pressedKeys.add('R')
        if vkey == 70:
            self.pressedKeys.add('F')
        return True



    def KeyUp(self, wnd, eventID, (vkey, flag,)):
        if hasattr(uicore.registry.GetFocus(), 'OnChar'):
            self.pressedKeys.clear()
            return True
        if vkey == 87:
            self.pressedKeys.discard('W')
        if vkey == 65:
            self.pressedKeys.discard('A')
        if vkey == 83:
            self.pressedKeys.discard('S')
        if vkey == 68:
            self.pressedKeys.discard('D')
        if vkey == 82:
            self.pressedKeys.discard('R')
        if vkey == 70:
            self.pressedKeys.discard('F')
        return True



    def UpdateKeyInput(self):
        cameraMoveRate = 0.1
        sceneManager = sm.GetService('sceneManager')
        while True:
            if self.dead:
                return 
            dx = dy = dz = 0
            if 'W' in self.pressedKeys:
                dz += -cameraMoveRate
            if 'A' in self.pressedKeys:
                dx += -cameraMoveRate
            if 'S' in self.pressedKeys:
                dz += cameraMoveRate
            if 'D' in self.pressedKeys:
                dx += cameraMoveRate
            if 'R' in self.pressedKeys:
                dy += cameraMoveRate
            if 'F' in self.pressedKeys:
                dy -= cameraMoveRate
            if dx or dy or dz:
                camera = sceneManager.GetRegisteredCamera('freeCamera')
                camera.MoveCamera(dx, dy, dz)
            blue.synchro.Yield()





