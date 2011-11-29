import math
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import log
import trinity
import timecurves
import base
import random
import triui
import uicls
import uiconst
import localization
VIEWWIDTH = 48
MAXMAPSIZE = 8000
MINMAPSIZE = 256
IDLVLUNI = 0
IDLVLREG = 1
IDLVLCON = 2
IDLVLSOL = 3
IDLVLSYS = 4
DRAWLVLREG = 1
DRAWLVLCON = 2
DRAWLVLSOL = 3
DRAWLVLSYS = 4

class MapBrowserWnd(uicls.Window):
    __guid__ = 'form.MapBrowserWnd'
    __notifyevents__ = ['OnSetDevice', 'OnUIScalingChange']
    default_windowID = 'mapbrowser'

    def ApplyAttributes(self, attributes):
        attributes.parent = uicore.layer.neocom
        uicls.Window.ApplyAttributes(self, attributes)
        locationID = attributes.locationID
        self.Reset_()
        self.scope = 'station_inflight'
        self.SetCaption(localization.GetByLabel('UI/Map/MapBrowser/MapBrowser'))
        self.MakeUnMinimizable()
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.HideHeader()
        self.MakeUnResizeable()
        closeX = uicls.Icon(parent=self.sr.main, icon='ui_38_16_220', align=uiconst.TOPRIGHT, top=-1, idx=0)
        closeX.OnClick = self.CloseByUser
        closeX.hint = localization.GetByLabel('UI/Map/MapBrowser/CloseMapBrowser')
        self.isDockWnd = 0
        self.sr.browser = xtriui.MapBrowser(name='browserX', parent=self.sr.main, pos=(3, 0, 3, 0))
        self.sr.browser.GetMenu = self.GetMenu
        self.initLocationID = locationID



    def Hide(self, *args, **kwargs):
        data = sm.GetService('neocom').PrepareForWindowPush(canWait=True)
        self.state = uiconst.UI_HIDDEN
        if data:
            sm.GetService('neocom').UpdateWindowPush(data, **kwargs)



    def Show(self, *args, **kwargs):
        data = sm.GetService('neocom').PrepareForWindowPush(canWait=True)
        self.state = uiconst.UI_NORMAL
        if data:
            sm.GetService('neocom').UpdateWindowPush(data, **kwargs)



    def OnUIScalingChange(self, change, *args):
        self.OnSetDevice()



    def OnSetDevice(self):
        data = sm.GetService('neocom').PrepareForWindowPush()
        self.Close()
        form.MapBrowserWnd.Open()
        if data:
            sm.GetService('neocom').UpdateWindowPush(data)



    def Reset_(self):
        self.id = None
        self.ids = None
        self.inited = 0
        self.loading = 0
        self.history = []
        self.sr.mainmap = None
        self.mapscale = settings.user.ui.Get('mapscale', 1.0) or 1.0



    def InitializeStatesAndPosition(self, *args, **kw):
        windowData = sm.GetService('neocom').PrepareForWindowPush(canWait=True)
        uicls.Window.InitializeStatesAndPosition(self, *args, **kw)
        self.SetAlign([uiconst.TOLEFT, uiconst.TORIGHT][(settings.user.ui.Get('mapbrowseralign', 'right') == 'right')])
        self.height = uicore.desktop.height
        self.width = self.height / 4 + 5
        self.left = 0
        self.top = 0
        self.state = uiconst.UI_PICKCHILDREN
        if windowData:
            sm.GetService('neocom').UpdateWindowPush(windowData)
        neocomWindow = sm.GetService('neocom').GetWnd()
        if neocomWindow:
            neocomWindow.SetOrder(0)
        self.DoLoad(self.initLocationID)



    def DoLoad(self, locationID = None):
        if locationID:
            self.ShowLocation(locationID)
        else:
            uthread.new(self.LoadCurrentDelayed)



    def LoadCurrentDelayed(self):
        blue.pyos.synchro.SleepWallclock(200)
        if not self.destroyed:
            self.LoadCurrent()



    def LoadCurrent(self):
        self.sr.browser.LoadCurrent()



    def Maximize(self, *args):
        pass



    def GetMenu(self):
        m = []
        if self.GetAlign() == uiconst.TOLEFT:
            m.append((localization.GetByLabel('UI/Map/MapBrowser/AlignRight'), self.ChangeAlign, ('right',)))
        else:
            m.append((localization.GetByLabel('UI/Map/MapBrowser/AlignLeft'), self.ChangeAlign, ('left',)))
        return m



    def ChangeAlign(self, align):
        data = sm.GetService('neocom').PrepareForWindowPush(canWait=True)
        settings.user.ui.Set('mapbrowseralign', align)
        self.SetAlign([uiconst.TOLEFT, uiconst.TORIGHT][(align == 'right')])
        if data:
            sm.GetService('neocom').UpdateWindowPush(data)



    def SetTempAngle(self, angle):
        if self is None or self.destroyed:
            return 
        if self.sr.browser and not self.sr.browser.destroyed:
            self.sr.browser.SetTempAngle(angle)



    def ShowLocation(self, locationID):
        (universeID, regionID, constellationID, solarsystemID, _itemID,) = sm.GetService('map').GetParentLocationID(locationID, 1)
        ids = [(universeID,
          IDLVLUNI,
          DRAWLVLREG,
          regionID)]
        if regionID is not None:
            ids.append((regionID,
             IDLVLREG,
             DRAWLVLCON,
             constellationID))
        if constellationID is not None:
            ids.append((constellationID,
             IDLVLCON,
             DRAWLVLSOL,
             solarsystemID))
        if solarsystemID is not None:
            ids.append((solarsystemID,
             IDLVLSOL,
             DRAWLVLSYS,
             None))
        self.sr.browser.LoadIDs(ids)



    def MapScaler(self, where):
        parent = uicls.Container(parent=where, align=uiconst.TOBOTTOM, height=14)
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Map/MapBrowser/ZoomLevel'), parent=parent, left=0, top=-12, width=100, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_NORMAL)
        for level in (1, 2, 4):
            sub = uicls.Container(parent=parent, align=uiconst.TOLEFT, width=24, state=uiconst.UI_NORMAL)
            sub.OnClick = (self.ChangeZoomLevel, sub, level)
            parent.width += sub.width
            uicls.Frame(parent=sub)
            txt = uicls.EveLabelSmall(text='%sx' % level, parent=sub, align=uiconst.TOALL, left=6, top=2, state=uiconst.UI_DISABLED)
            if settings.user.ui.Get('mapbrowserzoomlevel', 1) == level:
                uicls.Fill(parent=sub, padding=(1, 1, 1, 1))




    def ChangeZoomLevel(self, btn, level, *args):
        for each in btn.parent.children:
            uiutil.FlushList(each.children[5:])

        uicls.Fill(parent=btn, padding=(1, 1, 1, 1))
        settings.user.ui.Set('mapbrowserzoomlevel', level)
        self.ResetMapContainerSize()
        if self.sr.mainmap:
            self.sr.mainmap.RefreshOverlays(1)



    def _OnClose(self, *args):
        data = sm.GetService('neocom').PrepareForWindowPush(canWait=True)
        settings.user.ui.Set('mapscale', self.mapscale)
        if self.sr.mainmap:
            self.sr.mainmap.Close()
            self.sr.mainmap = None
        self.Reset_()
        if data:
            uthread.new(sm.GetService('neocom').UpdateWindowPush, data)



    def SetViewport(self, update = 0):
        uiutil.Update(self, 'MapBrowser::SetViewport')
        viewwidth = self.sr.mainmapparent.absoluteRight - self.sr.mainmapparent.absoluteLeft
        viewheight = self.sr.mainmapparent.absoluteBottom - self.sr.mainmapparent.absoluteTop
        self.sr.viewport.width = int(viewwidth * (float(VIEWWIDTH) / self.sr.mapcontainer.width))
        self.sr.viewport.height = int(self.sr.viewport.width * (float(viewheight) / viewwidth))
        self.sr.viewport.left = -int(self.sr.mapcontainer.left * (float(VIEWWIDTH) / self.sr.mapcontainer.width))
        self.sr.viewport.top = -int(self.sr.mapcontainer.top * (float(VIEWWIDTH) / self.sr.mapcontainer.width))



    def ResetMapContainerSize(self, keeplocation = 0):
        mainwidth = self.sr.mainmapparent.absoluteRight - self.sr.mainmapparent.absoluteLeft
        mainheight = self.sr.mainmapparent.absoluteBottom - self.sr.mainmapparent.absoluteTop
        size = max(mainwidth, mainheight)
        scale = settings.user.ui.Get('mapbrowserzoomlevel', 1)
        self.sr.mapcontainer.width = size * scale
        self.sr.mapcontainer.height = size * scale
        if not keeplocation:
            self.sr.mapcontainer.left = (mainwidth - self.sr.mapcontainer.width) / 2
            self.sr.mapcontainer.top = (mainheight - self.sr.mapcontainer.height) / 2
        self.SetViewport()



    def SetMyViewportLocation(self, maxdist):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        myball = bp.GetBall(eve.session.shipid)
        pos = trinity.TriVector(myball.x, myball.y, myball.z)
        sizefactor = VIEWWIDTH / (maxdist * 2.0) * 0.75
        pos.Scale(sizefactor)
        me = self.sr.viewport.sr.me
        me.left = VIEWWIDTH / 2 + int(pos.x) - me.width / 2
        me.top = VIEWWIDTH / 2 + int(pos.z) - me.height / 2



    def MoveMapWithViewport(self):
        self.sr.mapcontainer.left = -int(self.sr.viewport.left / (float(VIEWWIDTH) / self.sr.mapcontainer.width))
        self.sr.mapcontainer.top = -int(self.sr.viewport.top / (float(VIEWWIDTH) / self.sr.mapcontainer.width))



    def OnFrameMouseDown(self, par, frame, *args):
        self.dragframe = 1
        uicore.uilib.ClipCursor(par.absoluteLeft, par.absoluteTop, par.absoluteRight, par.absoluteBottom)
        frame.sr.grableft = uicore.uilib.x - frame.absoluteLeft
        frame.sr.grabtop = uicore.uilib.y - frame.absoluteTop



    def OnFrameMouseUp(self, par, frame, *args):
        self.dragframe = 0
        uicore.uilib.UnclipCursor()



    def OnFrameMouseMove(self, par, frame, *args):
        if getattr(self, 'dragframe', 0) == 1:
            self.MoveMapWithViewport()




