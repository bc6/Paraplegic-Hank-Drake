#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/surveyscan.py
import xtriui
import uix
import uiutil
import uiconst
import listentry
import util
import sys
import state
import uicls
import localization
import localizationUtil

class SurveyScanView(uicls.Window):
    __guid__ = 'form.SurveyScanView'
    default_windowID = 'SurveyScanView'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'inflight'
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Inflight/Scanner/SurveyScanResults'))
        self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Inventory/Clear'), okFunc=self.ClearAll)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'surveyscan_scroll'

    def _OnClose(self, *args):
        sm.GetService('surveyScan').Clear()

    def ClearAll(self, *args):
        sm.GetService('surveyScan').Clear()

    def Clear(self):
        self.sr.scroll.Load(contentList=[])

    def SetEntries(self, entries):
        scrolllist = []
        asteroidTypes = {}
        headers = [localization.GetByLabel('UI/Common/Ore'), localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Distance')]
        for ballID, (typeID, qty) in entries.iteritems():
            if not asteroidTypes.has_key(typeID):
                asteroidTypes[typeID] = [(ballID, qty)]
            else:
                asteroidTypes[typeID].append((ballID, qty))

        scrolllist = []
        for asteroidType in asteroidTypes:
            label = cfg.invtypes.Get(asteroidType).name
            data = {'GetSubContent': self.GetTypeSubContent,
             'label': label,
             'id': ('TypeSel', asteroidType),
             'groupItems': asteroidTypes[asteroidType],
             'typeID': asteroidType,
             'showlen': 1,
             'sublevel': 0,
             'state': 'locked'}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist = localizationUtil.Sort(scrolllist, key=lambda x: x.label)
        self.sr.scroll.Load(contentList=scrolllist, headers=headers)

    def GetTypeSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        bp = sm.GetService('michelle').GetBallpark()
        for ballID, qty in nodedata.groupItems:
            try:
                dist = bp.DistanceBetween(eve.session.shipid, ballID)
            except:
                dist = 0
                import traceback
                traceback.print_exc()
                sys.exc_clear()

            data = util.KeyVal()
            data.label = cfg.invtypes.Get(nodedata.typeID).name + '<t>' + util.FmtAmt(qty) + '<t>' + util.FmtDist(dist)
            data.itemID = ballID
            data.typeID = nodedata.typeID
            data.GetMenu = self.OnGetEntryMenu
            data.OnClick = self.OnEntryClick
            data.showinfo = 1
            data.Set('sort_' + localization.GetByLabel('UI/Common/Distance'), dist)
            data.Set('sort_' + localization.GetByLabel('UI/Common/Quantity'), qty)
            scrolllist.append(listentry.Get('Generic', data=data))

        return scrolllist

    def OnEntryClick(self, entry, *args):
        sm.GetService('state').SetState(entry.sr.node.itemID, state.selected, 1)
        if sm.GetService('target').IsTarget(entry.sr.node.itemID):
            sm.GetService('state').SetState(entry.sr.node.itemID, state.activeTarget, 1)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.GetService('target').TryLockTarget(entry.sr.node.itemID)
        elif uicore.uilib.Key(uiconst.VK_MENU):
            sm.GetService('menu').TryLookAt(entry.sr.node.itemID)

    def OnGetEntryMenu(self, entry, *args):
        return sm.GetService('menu').CelestialMenu(entry.sr.node.itemID)