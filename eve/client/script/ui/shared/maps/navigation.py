import blue
import uthread
import xtriui
import uix
import uiutil
import service
import form
import types
import base
import uicls
import uiconst
from mapcommon import STARMODE_SECURITY
import util
MOUSE_HOVER_REFRESH_TIME = 100

class MapNav(uicls.Container):
    __guid__ = 'form.MapNav'
    __nonpersistvars__ = ['wnd']
    __update_on_reload__ = 0

    def init(self):
        self.align = uiconst.TOALL
        self.lastTimeLeftMouseWasPressed = blue.os.GetTime()
        self.cursor = uiconst.UICURSOR_SELECTDOWN
        self._isPicked = False
        self.lastPickTime = blue.os.GetTime()
        self.drag = False



    def Startup(self):
        self.bubbleHint = None



    def MoveTF(self, tf, dx, dy):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        X = float(dx) / float(trinity.device.width)
        Y = -float(dy) / float(trinity.device.height)
        viewVec = camera.viewVec
        upVec = camera.upVec
        upVec.Scale(Y)
        rightVec = camera.rightVec
        rightVec.Scale(X)
        pos = rightVec + upVec
        pos.Scale(pow(tf.cameraDistSq, 0.5))
        pos.Scale(1.5)
        q = camera.rotationAroundParent
        pos.TransformQuaternion(q)
        tf.translation = tf.translation + pos



    def ScaleTF(self, tf, dy):
        tf.scaling.Scale(1.0 + 0.025 * float(dy))
        if tf.scaling.x < 80.0:
            tf.scaling.SetXYZ(80.0, 80.0, 80.0)



    def OnMouseEnter(self, *args):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN



    def OnMouseMove(self, *args):
        currentTime = blue.os.GetTime()
        self.hoverTimer = base.AutoTimer(MOUSE_HOVER_REFRESH_TIME, self.MouseHover)
        if currentTime - self.lastPickTime > MOUSE_HOVER_REFRESH_TIME * const.MSEC:
            self.lastPickTime = currentTime
            self.MouseHover()
        if not self._isPicked:
            return 
        starmap = sm.GetService('starmap')
        lib = uicore.uilib
        dx = lib.dx
        dy = lib.dy
        scene = sm.GetService('sceneManager').GetRegisteredScene('starmap')
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        fov = camera.fieldOfView
        ctrl = lib.Key(uiconst.VK_CONTROL)
        shift = lib.Key(uiconst.VK_SHIFT)
        cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
        self.mouseDownRegionID = None
        if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            if ctrl and shift and lib.leftbtn and not lib.rightbtn:
                if self.pickedTF is not None:
                    self.MoveTF(self.pickedTF, dx, dy)
                    return 
            if ctrl and shift and not lib.leftbtn and lib.rightbtn:
                if self.pickedTF is not None:
                    self.ScaleTF(self.pickedTF, dy)
                    return 
        drag = False
        if not lib.leftbtn and lib.rightbtn:
            drag = True
        elif lib.leftbtn and not lib.rightbtn:
            if sm.GetService('map').ViewingStarMap() and starmap.IsFlat():
                drag = True
        if drag:
            starmap.TranslateCamera(lib.x, lib.y, dx, dy)
        elif lib.leftbtn and lib.rightbtn:
            camera.Dolly(-(dy * 0.01) * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z, source='starmap')
            uthread.new(starmap.CheckLabelDist)
        elif lib.leftbtn and not lib.rightbtn:
            camera.OrbitParent(-dx * fov * 0.2, dy * fov * 0.2)
        else:
            regionID = self.PickRegionID()
            if regionID is not None:
                label = starmap.GetRegionLabel(regionID)
                starmap.UpdateLines(regionID)
        self.drag = drag



    def MouseHover(self, *args):
        self.hoverTimer = None
        uthread.new(self.CheckPick)



    def CheckPick(self):
        if self.destroyed or getattr(self, 'checkingPick', 0):
            return 
        self.checkingPick = 1
        try:
            starmap = sm.GetService('starmap')
            particleID = starmap.PickParticle()
            if particleID != None:
                solarsystemID = starmap.GetItemIDFromParticleID(particleID)
                if solarsystemID:
                    mapColor = settings.user.ui.Get('starscolorby', STARMODE_SECURITY)
                    if getattr(self, 'bubbleHint', None) != (particleID,
                     solarsystemID,
                     mapColor,
                     0):
                        self.state = uiconst.UI_DISABLED
                        uthread.new(self.ShowBubbleHint, particleID, solarsystemID, mapColor)
                    else:
                        starmap.ShowCursorInterest(solarsystemID)
                    uthread.new(starmap.UpdateLines, solarsystemID)
                    self.hoveringParticleID = particleID
            elif self.destroyed:
                return 
            self.hoveringParticleID = None
            blue.pyos.synchro.Sleep(100)
            if self.destroyed:
                return 
            if uicore.uilib.mouseOver == self:
                _particleID = starmap.PickParticle()
                if _particleID is None:
                    self.hoveringParticleID = None
                    bubble = self.GetBubble()
                    bubble.state = uiconst.UI_HIDDEN
                    self.bubbleHint = None

        finally:
            if not self.destroyed:
                self.checkingPick = 0




    def PickRegionID(self):
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
        if scene2 is None:
            return 
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
        pick = scene2.PickObject(x, y, projection, view, viewport)
        if pick is not None:
            if hasattr(pick, 'regionID'):
                return pick.regionID
            if pick.name[:11] == '__regionDot':
                return int(pick.name[11:])



    def ShowBubbleHint(self, particleID, solarsystemID, mapColor = None, extended = 0):
        starmap = sm.GetService('starmap')
        if not extended:
            blue.pyos.synchro.Sleep(25)
            if self.destroyed:
                return 
            _particleID = starmap.PickParticle()
            if _particleID is None or _particleID != particleID:
                self.state = uiconst.UI_NORMAL
                return 
        self.bubbleHint = (particleID,
         solarsystemID,
         mapColor,
         extended)
        eve.Message('click')
        mapData = sm.GetService('map').GetItem(solarsystemID)
        bubblehint = sm.GetService('systemmap').GetBubbleHint(solarsystemID, mapData=mapData, extended=extended)
        if self.destroyed:
            return 
        hint = bubblehint or [mapData.itemName]
        data = starmap.GetStarData()
        if particleID in data:
            hint.append('<line>')
            hint.append('<b>' + mls.UI_GENERIC_STATISTICS)
            if type(data[particleID]) == types.TupleType:
                for each in data[particleID]:
                    hint += each

            else:
                hint.append(data[particleID])
        if hint:
            bubble = self.GetBubble()
            if extended:
                bubble.state = uiconst.UI_DISABLED
            else:
                bubble.state = uiconst.UI_HIDDEN
            bubble.ShowHint(hint, 0)
            uiutil.SetOrder(bubble.parent, 0)
            blue.pyos.synchro.Yield()
            if bubble.destroyed or self.destroyed:
                return 
            bubble.state = uiconst.UI_NORMAL
            self.hoveringParticleID = particleID
        starmap.ShowCursorInterest(solarsystemID)
        self.state = uiconst.UI_NORMAL



    def ExpandBubbleHint(self, bubble, expand = 1):
        if not self.destroyed and self.bubbleHint:
            (tple, regionID, mapColor, exp,) = self.bubbleHint
            if not exp:
                self.state = uiconst.UI_DISABLED
                uthread.new(self.ShowBubbleHint, tple, regionID, mapColor, 1)



    def GetBubble(self):
        mapUICursor = sm.GetService('starmap').GetUICursor()
        if mapUICursor:
            for each in mapUICursor.children[:]:
                if each.name == 'bubblehint':
                    each.Close()

        bubble = xtriui.BubbleHint(parent=mapUICursor, name='bubblehint', align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_PICKCHILDREN)
        bubble.sr.ExpandHint = self.ExpandBubbleHint
        return bubble



    def ResetHightlight(self):
        blue.pyos.synchro.Sleep(400)
        if self.destroyed:
            return 
        regionID = self.PickRegionID()
        sm.GetService('starmap').UpdateLines(regionID)



    def OnClick(self, *args):
        if self.destroyed:
            return 
        starmap = sm.GetService('starmap')
        particleID = starmap.PickParticle()
        if particleID:
            if particleID == getattr(self, 'hoveringParticleID', None):
                solarSystemID = starmap.GetItemIDFromParticleID(particleID)
                starmap.SetInterest(solarSystemID)
                return 
        regionID = self.PickRegionID()
        if regionID is not None and getattr(self, 'mouseDownRegionID', None) == regionID:
            starmap.SetInterest(regionID)



    def OnMouseDown(self, button):
        self._isPicked = True
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
        self.pickedTF = None
        if scene2 is not None:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            self.pickedTF = scene2.PickObject(uicore.uilib.x, uicore.uilib.y, projection, view, viewport)
        self.mouseDownRegionID = self.PickRegionID()



    def OnMouseUp(self, button):
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self._isPicked = False
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        self.lastTimeLeftMouseWasPressed = blue.os.GetTime()
        self.pickedTF = None



    def OnMouseWheel(self, *args):
        if self.destroyed:
            return 
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        if camera.__typename__ == 'EveCamera':
            camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z, source='starmap')
        uthread.new(sm.GetService('starmap').CheckLabelDist)
        return 1



    def OnDblClick(self, *args):
        if self.destroyed:
            return 
        starmap = sm.GetService('starmap')
        solarSystemID = starmap.PickSolarSystemID()
        if solarSystemID is not None:
            starmap.SetInterest(solarSystemID)



    def GetMenu(self):
        if self.drag:
            self.drag = False
            return 
        mapSvc = sm.GetService('map')
        starmapSvc = sm.GetService('starmap')
        solarsystemID = starmapSvc.PickSolarSystemID()
        if solarsystemID is not None:
            return starmapSvc.GetItemMenu(solarsystemID)
        regionID = self.PickRegionID()
        if regionID:
            return starmapSvc.GetItemMenu(regionID)
        if blue.os.GetTime(1) - self.lastTimeLeftMouseWasPressed < 30000L:
            return 
        loctations = [(mls.UI_GENERIC_SOLARSYSTEM, starmapSvc.SetInterest, (eve.session.solarsystemid2, 1)), (mls.UI_GENERIC_CONSTELLATION, starmapSvc.SetInterest, (eve.session.constellationid, 1)), (mls.UI_GENERIC_REGION, starmapSvc.SetInterest, (eve.session.regionid, 1))]
        panel = [(mls.UI_SHARED_MAPSEARCH, self.ShowPanel, (mls.UI_SHARED_MAPSEARCH,)),
         (mls.UI_SHARED_MAPDISPLAYSETTINGS, self.ShowPanel, (mls.UI_GENERIC_STARMAP,)),
         (mls.UI_GENERIC_AUTOPILOT, self.ShowPanel, (mls.UI_GENERIC_AUTOPILOT,)),
         (mls.UI_SHARED_MAPWAYPOINTS, self.ShowPanel, (mls.UI_SHARED_MAPWAYPOINTS,))]
        m = [(mls.UI_SHARED_MAPSELECTCURRENT, loctations)]
        waypoints = starmapSvc.GetWaypoints()
        if len(waypoints):
            waypointList = []
            wpCount = 1
            for waypointID in waypoints:
                waypointItem = mapSvc.GetItem(waypointID)
                caption = str(wpCount) + ' - ' + waypointItem.itemName
                waypointList += [(caption, starmapSvc.SetInterest, (waypointID, 1))]
                wpCount += 1

            m.append((mls.UI_SHARED_MAPSELECTWAYPOINT, waypointList))
        m += [None, (mls.UI_SHARED_MAPWORLDCTRLPANEL, panel)]
        if len(starmapSvc.GetWaypoints()) > 0:
            m.append(None)
            m.append((mls.UI_SHARED_MAPCLEARALLWAYPOINTS, starmapSvc.ClearWaypoints, (None,)))
            if starmapSvc.genericRoute:
                m.append((mls.UI_SHARED_CLEAR_ROUTE, starmapSvc.RemoveGenericPath))
        if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            landmarkScales = [(mls.UI_SHARED_MAPALLIMPORTANCE, starmapSvc.LM_DownloadLandmarks, ()),
             ('%s 0' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (0,)),
             ('%s 1' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (1,)),
             ('%s 2' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (2,)),
             ('%s 3' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (3,)),
             ('%s 4' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (4,)),
             ('%s 5' % mls.UI_SHARED_MAPIMPORTANCE, starmapSvc.LM_DownloadLandmarks, (5,))]
            m.append(None)
            m.append((mls.UI_SHARED_MAPGETLANDMARKSFROM, landmarkScales))
            if eve.session.role & service.ROLE_WORLDMOD:
                m.append((mls.UI_SHARED_MAPUPDATESERVERLANDMARKS, starmapSvc.LM_UploadLandmarks, ()))
            m.append((mls.UI_SHARED_MAPHIDELANDMARKS, starmapSvc.LM_ClearLandmarks, ()))
        return m



    def ShowPanel(self, panelName):
        wnd = sm.GetService('window').GetWindow('mapspalette', create=1, decoClass=form.MapsPalette, maximize=1)
        if wnd:
            uthread.pool('MapNav::ShowPanel', wnd.ShowPanel, panelName)




