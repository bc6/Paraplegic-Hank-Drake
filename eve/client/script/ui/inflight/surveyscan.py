import xtriui
import uix
import uiutil
import uiconst
import listentry
import util
import sys
import state
import uicls

class SurveyScanView(uicls.Window):
    __guid__ = 'form.SurveyScanView'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'inflight'
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_INFLIGHT_SURVEYSCANRESULTS)
        self.DefineButtons(uiconst.OK, okLabel=mls.UI_GENERIC_CLEAR, okFunc=self.ClearAll)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'surveyscan_scroll'



    def OnClose_(self, *args):
        sm.GetService('surveyScan').Clear()



    def ClearAll(self, *args):
        sm.GetService('surveyScan').Clear()



    def Clear(self):
        self.sr.scroll.Load(contentList=[])



    def SetEntries(self, entries):
        scrolllist = []
        asteroidTypes = {}
        headers = [mls.UI_GENERIC_ORE, mls.UI_GENERIC_QUANTITY, mls.UI_GENERIC_DISTANCE]
        for (ballID, (typeID, qty,),) in entries.iteritems():
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
            scrolllist.append((label, listentry.Get('Group', data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.sr.scroll.Load(contentList=scrolllist, headers=headers)



    def GetTypeSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        bp = sm.GetService('michelle').GetBallpark()
        for (ballID, qty,) in nodedata.groupItems:
            try:
                dist = bp.DistanceBetween(eve.session.shipid, ballID)
            except:
                dist = 0
                import traceback
                traceback.print_exc()
                sys.exc_clear()
            data = util.KeyVal()
            data.label = '%s<t>%s<t>%s' % (cfg.invtypes.Get(nodedata.typeID).name, util.FmtAmt(qty), util.FmtDist(dist))
            data.itemID = ballID
            data.typeID = nodedata.typeID
            data.GetMenu = self.OnGetEntryMenu
            data.OnMouseHover = self.OnEntryHover
            data.OnMouseExit = self.OnEntryExit
            data.OnClick = self.OnEntryClick
            data.showinfo = 1
            data.Set('sort_' + mls.UI_GENERIC_DISTANCE, dist)
            scrolllist.append(listentry.Get('Generic', data=data))

        return scrolllist



    def OnEntryHover(self, entry, *etc):
        try:
            sm.GetService('target').SetAsInterest(entry.sr.node.itemID)
        except:
            import traceback
            traceback.print_exc()
            sys.exc_clear()



    def OnEntryClick(self, entry, *args):
        sm.GetService('state').SetState(entry.sr.node.itemID, state.selected, 1)
        if sm.GetService('target').IsTarget(entry.sr.node.itemID):
            sm.GetService('state').SetState(entry.sr.node.itemID, state.activeTarget, 1)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.GetService('target').TryLockTarget(entry.sr.node.itemID)
        elif uicore.uilib.Key(uiconst.VK_MENU):
            sm.GetService('menu').TryLookAt(entry.sr.node.itemID)



    def OnEntryExit(self, entry, *etc):
        sm.GetService('target').SetAsInterest(None)



    def OnGetEntryMenu(self, entry, *args):
        return sm.GetService('menu').CelestialMenu(entry.sr.node.itemID)




