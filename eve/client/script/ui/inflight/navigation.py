import uthread
import trinity
import xtriui
import uix
import uiutil
import mathUtil
import blue
import form
import util
import base
import service
import state
import uicls
import uiconst

class InflightNav(uicls.Container):
    __guid__ = 'form.InflightNav'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.looking = 1
        self.locked = 0
        self.zoomlooking = 0
        self.fovready = 0
        self.resetfov = 0
        self.prefov = None
        self.scope = 'inflight'
        self.align = uiconst.TOALL
        self.notdbl = 0
        self.sr.tcursor = None
        self.sr.clicktime = None
        self.zoomcursor = None
        self.hoverbracket = None
        self.blockDisable = 0
        self.movingCursor = None
        self.sr.spacemenu = None
        self.downpos = None
        self.locks = {}
        self._isPicked = False
        self.dungeonEditorSelectionEnabled = False
        sceneManager = sm.GetService('sceneManager')
        self.maxFov = sceneManager.maxFov
        self.minFov = sceneManager.minFov



    def Startup(self):
        self.sr.tcursor = uicls.Container(name='targetingcursor', parent=self, align=uiconst.ABSOLUTE, width=1, height=1, state=uiconst.UI_HIDDEN)
        uicls.Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, left=10, width=3000, height=1)
        uicls.Line(parent=self.sr.tcursor, align=uiconst.TOPRIGHT, left=10, width=3000, height=1)
        uicls.Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, top=10, width=1, height=3000)
        uicls.Line(parent=self.sr.tcursor, align=uiconst.BOTTOMLEFT, top=10, width=1, height=3000)
        sm.StartService('posAnchor')
        sm.StartService('systemmap')



    def GetSpaceMenu(self):
        if self.sr.spacemenu:
            if self.sr.spacemenu.solarsystemid == eve.session.solarsystemid2:
                return self.sr.spacemenu
            m = self.sr.spacemenu
            self.sr.spacemenu = None
            m.Close()
        solarsystemitems = sm.RemoteSvc('config').GetMapObjects(eve.session.solarsystemid2, 0, 0, 0, 1, 0)
        listbtn = xtriui.ListSurroundingsBtn(name='gimp', parent=self, state=uiconst.UI_HIDDEN, pos=(0, 0, 0, 0))
        listbtn.sr.mapitems = solarsystemitems
        listbtn.sr.groupByType = 1
        listbtn.filterCurrent = 1
        listbtn.solarsystemid = eve.session.solarsystemid2
        self.sr.spacemenu = listbtn
        return self.sr.spacemenu



    def GetSelfMenu(self):
        cam = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if eve.session.shipid and cam.parent and getattr(cam.parent, 'translationCurve', None) is not None and cam.parent.translationCurve.id == eve.session.shipid:
            return sm.GetService('menu').CelestialMenu(eve.session.shipid)
        return self.GetMenu()



    def SelfMouseDown(self, *args):
        (picktype, pickobject,) = self.GetPick()
        if not (pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id')):
            if sm.GetService('menu').TryExpandActionMenu(eve.session.shipid, uicore.uilib.x, uicore.uilib.y, self):
                return 
        self.OnMouseDown()



    def _OnClose(self):
        uicls.Container._OnClose(self)
        self.CloseZoomCursor()
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN



    def OnMouseDown(self, *args):
        self._isPicked = True
        self.downpos = (uicore.uilib.x, uicore.uilib.y)
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_DISABLED
        sm.GetService('systemmap').CollapseBubbles()
        sm.GetService('systemmap').SortBubbles()
        sm.GetService('bracket').ResetOverlaps()
        self.notdbl = 0
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if uicore.uilib.rightbtn:
            sm.GetService('target').CancelTargetOrder()
            if getattr(self, 'prefov', None) is None:
                self.prefov = camera.fieldOfView
            self.notdbl = 1
        (picktype, pickobject,) = self.GetPick()
        if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            uthread.pool('navigation::OnMouseDown', sm.GetService('menu').TryExpandActionMenu, pickobject.translationCurve.id, uicore.uilib.x, uicore.uilib.y, self)
        if uicore.uilib.leftbtn:
            if sm.IsServiceRunning('scenario') and sm.StartService('scenario').IsActive():
                self.movingCursor = sm.StartService('scenario').GetPickAxis()
            if pickobject:
                if sm.GetService('posAnchor').IsActive():
                    if pickobject.name[:6] == 'cursor':
                        self.movingCursor = pickobject
                        sm.GetService('posAnchor').StartMovingCursor()
                        return 
                if eve.session.role & service.ROLE_CONTENT and self.dungeonEditorSelectionEnabled and not self.movingCursor:
                    scenario = sm.GetService('scenario')
                    michelle = sm.GetService('michelle')
                    item = michelle.GetItem(pickobject.translationCurve.id)
                    if getattr(item, 'dunObjectID', None) != None and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
                        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
                        if not shift:
                            slimItem = michelle.GetItem(item.itemID)
                            scenario.SetSelectionByID([slimItem.dunObjectID])
                        elif not scenario.IsSelected(item.itemID):
                            scenario.AddSelected(item.itemID)
                        else:
                            scenario.RemoveSelected(item.itemID)
        self.looking = 1
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)



    def OnDblClick(self, *args):
        if eve.rookieState and eve.rookieState < 22:
            return 
        self.sr.clicktime = None
        solarsystemID = eve.session.solarsystemid
        uthread.Lock(self)
        try:
            if solarsystemID != eve.session.solarsystemid:
                return 
            if self.notdbl:
                return 
            if uicore.uilib.Key(uiconst.VK_SHIFT) and eve.session.role & service.ROLE_CONTENT:
                return 
            (x, y,) = (uicore.uilib.x, uicore.uilib.y)
            if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
                return 
            cameraSvc = sm.StartService('camera')
            if cameraSvc.IsFreeLook():
                (picktype, pickobject,) = self.GetPick()
                if pickobject:
                    cameraSvc.LookAt(pickobject.translationCurve.id)
                return 
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            proj = camera.projection
            view = camera.view
            pickDir = scene.PickInfinity(x, y, proj, view)
            if pickDir:
                bp = sm.GetService('michelle').GetRemotePark()
                if bp is not None:
                    if solarsystemID != eve.session.solarsystemid:
                        return 
                    try:
                        bp.GotoDirection(pickDir.x, pickDir.y, pickDir.z)
                    except RuntimeError as what:
                        if what.args[0] != 'MonikerSessionCheckFailure':
                            raise what
            shipui = uicore.layer.shipui
            if shipui.isopen:
                shipui.UpdateSpeed()

        finally:
            uthread.UnLock(self)




    def OnMouseUp(self, button, *args):
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self._isPicked = False
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        sm.GetService('systemmap').SortBubbles()
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if not uicore.uilib.rightbtn:
            if self.zoomlooking and self.resetfov and camera.fieldOfView != self.prefov:
                uthread.new(self.ResetFov)
            if camera.__typename__ == 'EveCamera':
                camera.rotationOfInterest.SetIdentity()
            self.zoomlooking = 0
        if not uicore.uilib.leftbtn:
            self.looking = 0
            self.fovready = 0
        if button == 0 and not uicore.uilib.rightbtn:
            mt = self.GetMouseTravel()
            cameraSvc = sm.StartService('camera')
            freeLookMove = cameraSvc.IsFreeLook() and uicore.uilib.Key(uiconst.VK_MENU)
            if not (mt and mt > 5 or freeLookMove):
                (picktype, pickobject,) = self.GetPick()
                if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
                    slimItem = uix.GetBallparkRecord(pickobject.translationCurve.id)
                    if slimItem and slimItem.groupID not in (const.groupPlanet, const.groupMoon, const.groupAsteroidBelt):
                        itemID = pickobject.translationCurve.id
                        sm.GetService('state').SetState(itemID, state.selected, 1)
                        sm.GetService('menu').TacticalItemClicked(itemID)
                elif uicore.uilib.Key(uiconst.VK_MENU):
                    sm.GetService('menu').TryLookAt(eve.session.shipid)
        if not uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
        elif uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            uthread.new(uicore.uilib.SetCapture, self)
        if self.movingCursor:
            if sm.GetService('posAnchor').IsActive():
                sm.GetService('posAnchor').StopMovingCursor()
                self.movingCursor = None
                return 
        if eve.session.role & service.ROLE_CONTENT:
            if self.movingCursor:
                self.movingCursor = None
        self.downpos = None



    def GetMouseTravel(self):
        if self.downpos:
            (x, y,) = (uicore.uilib.x, uicore.uilib.y)
            v = trinity.TriVector(float(x - self.downpos[0]), float(y - self.downpos[1]), 0.0)
            return int(v.Length())
        else:
            return None



    def OnMouseWheel(self, *args):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera.__typename__ == 'EveCamera':
            camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z)
        return 1



    def OnMouseEnter(self, *args):
        if self is None or self.destroyed or self.parent is None or self.parent.destroyed:
            return 
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if sm.IsServiceRunning('tactical'):
            uthread.pool('InflightNav::MouseEnter --> ResetTargetingRanges', sm.GetService('tactical').ResetTargetingRanges)
        uiutil.SetOrder(self, -1)



    def OnMouseMove(self, *args):
        self.sr.hint = ''
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        if not self._isPicked:
            return 
        lib = uicore.uilib
        ctrl = lib.Key(uiconst.VK_CONTROL)
        alt = lib.Key(uiconst.VK_MENU)
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return 
        if lib.leftbtn and self.movingCursor:
            if sm.GetService('posAnchor').IsActive():
                sm.GetService('posAnchor').MoveCursor(self.movingCursor, lib.dx, lib.dy, camera)
                return 
            if eve.session.role & service.ROLE_CONTENT:
                sm.GetService('scenario').MoveCursor(self.movingCursor, lib.dx, lib.dy, camera)
                return 
        if not alt or not ctrl:
            self.CloseZoomCursor()
        if (self.looking or self.zoomlooking) and camera.__typename__ == 'EveCamera':
            dx = lib.dx
            dy = lib.dy
            fov = camera.fieldOfView
            cameraSvc = sm.StartService('camera')
            if alt and cameraSvc.IsFreeLook():
                leftBtn = lib.leftbtn and not lib.rightbtn and not lib.midbtn
                rightBtn = lib.rightbtn and not lib.leftbtn and not lib.midbtn
                midBtn = lib.rightbtn and lib.leftbtn or lib.midbtn
                if leftBtn:
                    camera.OrbitParent(-dx * fov * 0.2, -dy * fov * 0.2)
                    sm.GetService('systemmap').SortBubbles()
                if rightBtn:
                    cameraSvc = sm.StartService('camera')
                    camera.Dolly(-0.01 * dy * abs(camera.translationFromParent.z))
                    camera.translationFromParent.z = cameraSvc.CheckTranslationFromParent(camera.translationFromParent.z)
                if midBtn:
                    vertMovement = camera.upVec * dy * camera.translationFromParent.z / uicore.uilib.desktop.height
                    horizMovement = -camera.rightVec * dx * camera.translationFromParent.z / uicore.uilib.desktop.height
                    cameraSvc._ChangeCamPos(vertMovement + horizMovement)
                return 
            if lib.rightbtn and not lib.leftbtn:
                camera.RotateOnOrbit(-dx * fov * 0.2, dy * fov * 0.2)
                self.fovready = self.zoomlooking = 1
            if lib.leftbtn and not lib.rightbtn:
                camera.OrbitParent(-dx * fov * 0.2, dy * fov * 0.2)
                sm.GetService('systemmap').SortBubbles()
            if lib.leftbtn and lib.rightbtn:
                if self.fovready and self.zoomlooking:
                    camera.fieldOfView = dy * 0.01 + fov
                    if camera.fieldOfView > self.maxFov:
                        camera.fieldOfView = self.maxFov
                    if camera.fieldOfView < self.minFov:
                        camera.fieldOfView = self.minFov
                    self.resetfov = 1
                else:
                    camera.Dolly(-0.01 * dy * abs(camera.translationFromParent.z))
                    camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z)
                    if ctrl:
                        camera.fieldOfView = -dx * 0.01 + fov
                        if camera.fieldOfView > self.maxFov:
                            camera.fieldOfView = self.maxFov
                        if camera.fieldOfView < self.minFov:
                            camera.fieldOfView = self.minFov
                    else:
                        camera.OrbitParent(-dx * fov * 0.2, 0.0)
                        if uicore.uilib.leftbtn:
                            sm.GetService('systemmap').SortBubbles()



    def ResetFov(self):
        if self.prefov is not None:
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            to = self.prefov
            fr = camera.fieldOfView
            (start, ndt,) = (blue.os.GetTime(), 0.0)
            while ndt != 1.0:
                ndt = min(blue.os.TimeDiffInMs(start) / 1000.0, 1.0)
                camera.fieldOfView = mathUtil.Lerp(fr, to, ndt)
                blue.pyos.synchro.Yield()

            self.prefov = None
        self.resetfov = 0



    def ShowTargetingCursor(self):
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        self.sr.tcursor.state = uiconst.UI_DISABLED



    def HideTargetingCursor(self):
        self.sr.tcursor.state = uiconst.UI_HIDDEN



    def ShowZoomCursor(self):
        if uicore.registry.GetFocus() == self:
            uthread.new(self._ShowZoomCursor)



    def _ShowZoomCursor(self):
        blue.pyos.synchro.Sleep(750)
        if not uicore.uilib.Key(uiconst.VK_CONTROL):
            return 
        if self.zoomcursor is None or self.zoomcursor.destroyed:
            self.zoomcursor = xtriui.CursorZoom(state=uiconst.UI_NORMAL)
            self.zoomcursor.Startup()



    def CloseZoomCursor(self):
        if self.zoomcursor is not None and not self.zoomcursor.destroyed:
            self.zoomcursor.Close()
            self.zoomcursor = None



    def GetPick(self):
        if not trinity.app.IsActive():
            return (None, None)
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        if scene2:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            pick = scene2.PickObject(x, y, projection, view, viewport)
            if pick:
                return ('scene', pick)
        return (None, None)



    def OnMouseHover(self, *args):
        (picktype, pickobject,) = self.GetPick()
        if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            itemID = pickobject.translationCurve.id
            slimItem = uix.GetBallparkRecord(itemID)
            if slimItem:
                slimItemName = uix.GetSlimItemName(slimItem)
                if slimItemName:
                    self.sr.hint = slimItemName
                    uicore.UpdateHint(self)



    def GetMenu(self, itemID = None):
        if self.locked:
            return []
        m = []
        cam = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if not itemID:
            (picktype, pickobject,) = self.GetPick()
            if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
                itemID = pickobject.translationCurve.id
            if pickobject:
                if sm.GetService('posAnchor').IsActive():
                    if pickobject.name[:6].lower() == 'cursor':
                        m.append((mls.UI_CMD_ANCHORHERE, sm.GetService('posAnchor').SubmitAnchorPosSelect, ()))
                        m.append(None)
                        m.append((mls.UI_CMD_CANCELANCHORING, sm.GetService('posAnchor').CancelAchorPosSelect, ()))
                        return m
        if not itemID:
            mm = []
            if not (eve.rookieState and eve.rookieState < 32):
                mm = self.GetSpaceMenu().GetMenu()
            m += [(mls.UI_CMD_RESETCAMERA, sm.GetService('camera').ResetCamera, ())]
            m += [None, [mls.UI_CMD_SHOWSSINMAPBR, sm.GetService('menu').ShowInMapBrowser, (eve.session.solarsystemid2,)], None]
            return m + mm
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return m
        slimItem = bp.GetInvItem(itemID)
        if slimItem is None:
            return m
        pickid = slimItem.itemID
        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        if eve.session.shipid is None:
            return m
        m += sm.GetService('menu').CelestialMenu(slimItem.itemID, slimItem=slimItem)
        return m




