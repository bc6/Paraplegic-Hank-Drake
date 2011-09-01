import uix
import blue
import uthread
import util
import uicls
import uiconst

class StationNav(uicls.Container):
    __guid__ = 'form.StationNav'

    def __init__(self, *args, **kwds):
        uicls.Container.__init__(self, *args, **kwds)
        self.looking = 0
        self.blockDisable = 0



    def Startup(self):
        pass



    def GetMenu(self):
        scene2 = sm.GetService('sceneManager').GetActiveScene2()
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        if scene2:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            pick = scene2.PickObject(x, y, projection, view, viewport)
            if pick and pick.name == str(eve.session.shipid):
                return self.GetShipMenu()



    def OnMouseEnter(self, *args):
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN



    def OnDropData(self, dragObj, nodes):
        sm.GetService('loading').StopCycle()
        if len(nodes) == 1:
            node = nodes[0]
            if getattr(node, '__guid__', None) not in ('xtriui.InvItem', 'listentry.InvItem'):
                return 
            if eve.session.shipid == node.item.itemID:
                eve.Message('CantMoveActiveShip', {})
                return 
            if node.item.categoryID == const.categoryShip and node.item.singleton:
                if not node.item.ownerID == eve.session.charid:
                    eve.Message('CantDoThatWithSomeoneElsesStuff')
                    return 
                sm.GetService('station').TryActivateShip(node.item)
        selsvc = sm.GetService('station').GetSvc()
        if selsvc is not None:
            if util.LocalSvcHasAttr(selsvc, 'OnStuffDropOnMainArea'):
                uthread.new(selsvc.OnStuffDropOnMainArea, nodes)



    def GetShipMenu(self):
        if eve.session.shipid:
            hangarInv = eve.GetInventory(const.containerHangar)
            hangarItems = hangarInv.List()
            for each in hangarItems:
                if each.itemID == eve.session.shipid:
                    return sm.GetService('menu').InvItemMenu(each)

        return []



    def OnDblClick(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()



    def OnMouseDown(self, *args):
        if settings.user.ui.Get('loadstationenv', 1):
            self.looking = 1
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_DISABLED
        self.cursor = uiconst.UICURSOR_DRAGGABLE
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)



    def OnMouseUp(self, button, *args):
        if not self.blockDisable and not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if settings.user.ui.Get('loadstationenv', 1):
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            if camera is None:
                return 
            camera.interest = None
            camera.friction = 7.0
            if not uicore.uilib.rightbtn:
                camera.rotationOfInterest.SetIdentity()
            if not uicore.uilib.leftbtn:
                self.looking = 0
        self.cursor = None
        uicore.uilib.UnclipCursor()
        if uicore.uilib.GetCapture() == self:
            uicore.uilib.ReleaseCapture()



    def OnMouseWheel(self, *args):
        if settings.user.ui.Get('loadstationenv', 1):
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            if camera is None:
                return 
            if camera.__typename__ == 'EveCamera':
                camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent.z))
                camera.translationFromParent.z = sm.GetService('station').CheckCameraTranslation(camera.translationFromParent.z)



    def OnMouseMove(self, *args):
        if self.looking and settings.user.ui.Get('loadstationenv', 1):
            lib = uicore.uilib
            dx = lib.dx
            dy = lib.dy
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            if camera is None:
                return 
            fov = camera.fieldOfView
            ctrl = lib.Key(uiconst.VK_CONTROL)
            if lib.rightbtn and not lib.leftbtn:
                camera.RotateOnOrbit(-dx * fov * 0.2, dy * fov * 0.2)
            if lib.leftbtn and not lib.rightbtn:
                camera.OrbitParent(-dx * fov * 0.2, dy * fov * 0.2)
            if lib.leftbtn and lib.rightbtn:
                station = sm.GetService('station')
                camera.Dolly(-0.01 * dy * abs(camera.translationFromParent.z))
                camera.translationFromParent.z = station.CheckCameraTranslation(camera.translationFromParent.z)
                if ctrl:
                    camera.fieldOfView = -dx * 0.01 + fov
                    if camera.fieldOfView > 1.0:
                        camera.fieldOfView = 1.0
                    if camera.fieldOfView < 0.1:
                        camera.fieldOfView = 0.1
                else:
                    camera.OrbitParent(-dx * fov * 0.2, 0.0)
        else:
            self.cursor = None




