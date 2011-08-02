import uix
import uiutil
import xtriui
import uthread
import blue
import os
import util
import trinity
import uicls
import uiconst
DRAWLVLREG = 1
DRAWLVLCON = 2
DRAWLVLSOL = 3
DRAWLVLSYS = 4

class MapBrowser(uicls.Container):
    __guid__ = 'xtriui.MapBrowser'
    __nonpersistvars__ = []
    __notifyevents__ = ['ProcessSessionChange', 'DoBallsAdded']

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.ids = [[],
         [],
         [],
         []]
        self.loadingMap = 0



    def ProcessSessionChange(self, isRemote, session, change):
        if 'regionid' in change and change['regionid'][0] == self.ids[1][0]:
            self.LoadIDs([(const.locationUniverse,
              0,
              DRAWLVLREG,
              eve.session.regionid),
             (eve.session.regionid,
              1,
              DRAWLVLCON,
              eve.session.constellationid),
             (eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2),
             (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])
        elif 'constellationid' in change and change['constellationid'][0] == self.ids[2][0]:
            self.LoadIDs([(eve.session.regionid,
              1,
              DRAWLVLCON,
              eve.session.constellationid), (eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2), (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])
        elif 'solarsystemid' in change and change['solarsystemid'][0] == self.ids[3][0]:
            self.LoadIDs([(eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2), (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])



    def Startup(self):
        pass



    def LoadCurrent(self):
        self.LoadIDs([(const.locationUniverse,
          0,
          DRAWLVLREG,
          eve.session.regionid),
         (eve.session.regionid,
          1,
          DRAWLVLCON,
          eve.session.constellationid),
         (eve.session.constellationid,
          2,
          DRAWLVLSOL,
          eve.session.solarsystemid2),
         (eve.session.solarsystemid2,
          3,
          DRAWLVLSYS,
          None)])



    def LoadIDs(self, ids):
        for (id, idlevel, drawlevel, selected,) in ids:
            if self.destroyed:
                return 
            if self.ids[idlevel] == [id]:
                if selected and len(self.children) > idlevel:
                    self.children[idlevel].SetSelected([selected])
                continue
            self.GetMap([id], idlevel, drawlevel, selected)




    def Prepare():
        pass



    def GetMap(self, ids, idlevel, drawlevel, selected = None):
        if getattr(self, 'loadingMap', 0):
            return 
        self.loadingMap = 1
        uiutil.FlushList(self.children[idlevel:])
        self.ids[idlevel] = ids
        cfg.evelocations.Prime(ids)
        (l, t, absWidth, absHeight,) = self.GetAbsolute()
        pilmap = xtriui.Map2D(name='map', align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=absWidth)
        pilmap.OnSelectItem = self.OnMapSelection
        pilmap.GetParentMenu = self.GetMenu
        pilmapList = []
        if drawlevel == DRAWLVLSYS:
            basesize = self.absoluteRight - self.absoluteLeft
            pilmap.width = pilmap.height = basesize
            pilmap.left = pilmap.top = (pilmap.width - basesize) / 2
            pilmap.align = uiconst.RELATIVE
            pilmap.dragAllowed = 1
            mapparent = uicls.Container(name='mapparent', align=uiconst.TOTOP, lockAspect=1, parent=self, clipChildren=1, height=absWidth)
            uicls.Line(parent=mapparent, align=uiconst.TOBOTTOM, color=(0.0, 0.0, 0.0, 0.5))
            uicls.Line(parent=mapparent, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.5))
            pilmapList = mapparent.children
            drawsize = max(uiutil.GetBuffersize(basesize), 512)
            self.SetLoadExternalPointer(mapparent, self.ids[idlevel][0])
            addstuff = mapparent
        else:
            uicls.Line(parent=pilmap.overlays, align=uiconst.TOBOTTOM, color=(0.0, 0.0, 0.0, 0.5))
            uicls.Line(parent=pilmap.overlays, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.5))
            pilmapList = self.children
            drawsize = 256
            self.SetLoadExternalPointer(pilmap, self.ids[idlevel][0])
            addstuff = pilmap.overlays
        pilmap.Draw(ids, idlevel, drawlevel, drawsize)
        pilmapList.append(pilmap)
        listicon = xtriui.ListSurroundingsBtn(parent=addstuff, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(0, 0, 16, 16), idx=0, showIcon=True)
        locConsts = {0: {const.typeUniverse: ''},
         1: {const.typeRegion: mls.UI_GENERIC_REGION},
         2: {const.typeConstellation: mls.UI_GENERIC_CONSTELLATION},
         3: {const.typeSolarSystem: mls.UI_GENERIC_SOLARSYSTEM}}
        locStr = ''
        for id in ids:
            locStr += '%s ' % {False: cfg.evelocations.Get(id).name,
             True: mls.UNIVERSE}[(id == const.typeUniverse)]

        levelName = locConsts.get(idlevel, '').values()[0]
        levelID = locConsts.get(idlevel, '').keys()[0]
        locStr += '%s ' % levelName
        listbtn = uicls.Label(text=['', {False: cfg.evelocations.Get(ids[0]).name,
          True: mls.UNIVERSE}[(ids[0] == const.typeUniverse)]][(len(ids) == 1)] + ' ' + levelName + ['s', ''][(len(ids) == 1)], parent=addstuff, left=listicon.left + listicon.width + 4, top=5, color=(1.0, 1.0, 1.0, 0.75), idx=0, state=uiconst.UI_NORMAL)
        listbtn.expandOnLeft = True
        listbtn.GetMenu = listicon.GetMenu
        for id in ids:
            if id != const.typeUniverse:
                listicon.sr.typeID = listbtn.sr.typeID = levelID
                listicon.sr.itemID = listbtn.sr.itemID = id

        listbtn.sr.hint = mls.UI_SHARED_LISTITEMSINSYSTEM % {'typeName': [mls.UI_GENERIC_REGIONS,
                      mls.UI_GENERIC_CONSTELLATIONS,
                      mls.UI_GENERIC_SOLARSYSTEMS,
                      mls.UI_GENERIC_CELESTIALS][(drawlevel - 1)],
         'where': locStr}
        if self.destroyed:
            return 
        if drawlevel == DRAWLVLSYS:
            listbtn.sr.groupByType = listicon.sr.groupByType = 1
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems
        elif drawlevel in (DRAWLVLCON, DRAWLVLSOL):
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems[1:]
        else:
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems
        listbtn.solarsystemid = listicon.solarsystemid = ids[0]
        if selected:
            pilmap.SetSelected([selected])
        self.Refresh()
        self.loadingMap = 0



    def GetMenu(self):
        return []



    def ShowOnMap(self, itemID, *args):
        if itemID >= const.mapWormholeRegionMin and itemID <= const.mapWormholeRegionMax or itemID >= const.mapWormholeConstellationMin and itemID <= const.mapWormholeConstellationMax or itemID >= const.mapWormholeSystemMin and itemID <= const.mapWormholeSystemMax:
            raise UserError('MapShowWormholeSpaceInfo', {'name': (OWNERID, eve.session.charid)})
        initing = 0
        if eve.session.stationid:
            sm.GetService('station').CleanUp()
        sm.GetService('map').OpenStarMap()
        sm.GetService('starmap').SetInterest(itemID, 1)



    def SetLoadExternalPointer(self, where, id, func = None, args = None, hint = mls.UI_SHARED_MAPSHOWINWORLDMAP):
        pointer = uicls.Sprite(parent=where, name='pointer', align=uiconst.BOTTOMLEFT, pos=(2, 2, 16, 16), texturePath='res:/UI/Texture/Shared/arrowLeft.png', color=(1.0, 1.0, 1.0, 0.5))
        pointer.hint = hint
        pointer.OnClick = (self.ShowOnMap, id)



    def OnMapSelection(self, themap, itemID):
        if themap.drawlevel == DRAWLVLSYS:
            return 
        sm.GetService('loading').Cycle('Loading map')
        mapidx = self.children.index(themap)
        ids = [itemID]
        idlevel = mapidx + 1
        drawlevel = mapidx + 2
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if drawlevel > DRAWLVLSYS:
            sm.GetService('loading').StopCycle()
            return 
        if drawlevel == DRAWLVLSYS:
            if shift:
                uthread.new(eve.Message, 'CustomInfo', {'info': mls.UI_SHARED_MAPCANNOTSHIFTSELECT})
        elif shift and len(self.children) > idlevel:
            currentids = self.children[idlevel].ids
            ids += currentids
            if itemID in currentids:
                while itemID in ids:
                    ids.remove(itemID)

        if not len(ids):
            return 
        themap.SetSelected(ids)
        if mapidx < 3:
            uthread.new(self.GetMap, ids, idlevel, drawlevel)
        sm.GetService('loading').StopCycle()



    def Refresh(self, update = 0):
        if update:
            uiutil.Update(self, 'Browser::Refresh')
        for each in self.children:
            if hasattr(each, 'RefreshSize'):
                each.RefreshSize()
            if hasattr(each, 'RefreshOverlays'):
                each.RefreshOverlays()




    def SetTempAngle(self, angle):
        if len(self.children) == 4 and len(self.children[-1].children):
            if hasattr(self.children[-1].children[-1], 'SetTempAngle'):
                self.children[-1].children[-1].SetTempAngle(angle)



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::mapBrowser')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, lst):

        def PassEventToChild(childItem):
            if hasattr(childItem, 'CheckMyLocation'):
                childItem.CheckMyLocation()
            if hasattr(childItem, 'CheckDestination'):
                childItem.CheckDestination()


        for (ball, slimItem,) in lst:
            if slimItem.itemID == eve.session.shipid:
                for childMap in self.children:
                    PassEventToChild(childMap)
                    if hasattr(childMap, 'children'):
                        for grandchildItem in childMap.children:
                            PassEventToChild(grandchildItem)


                break





