#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/addressBookEntries.py
import uicls
import uiconst
import uix
import uiutil
import uthread
import localization
import blue
import service

class PlaceEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.PlaceEntry'
    __nonpersistvars__ = []
    isDragObject = True

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, maxLines=1)
        self.sr.icon = uicls.Icon(icon='ui_9_64_1', parent=self, pos=(4, 1, 16, 16), align=uiconst.RELATIVE, ignoreSize=True)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125))

    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.left = 24 + data.Get('sublevel', 0) * 16
        self.sr.icon.left = 4 + data.Get('sublevel', 0) * 16
        self.sr.bm = data.bm
        self.sr.label.text = data.label
        self.id = self.sr.bm.bookmarkID
        self.groupID = self.sr.node.listGroupID
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]
        if self.sr.bm.itemID and self.sr.bm.itemID == sm.GetService('starmap').GetDestination():
            self.sr.label.color.SetRGB(1.0, 1.0, 0.0, 1.0)
        elif self.sr.bm.locationID == session.solarsystemid2:
            self.sr.label.color.SetRGB(0.5, 1.0, 0.5, 1.0)
        else:
            self.sr.label.color.SetRGB(1.0, 1.0, 1.0, 1.0)
        self.EnableDrag()
        dropDataFunc = getattr(node, 'DropData')
        if dropDataFunc is not None:
            self.OnDropData = dropDataFunc

    def GetHeight(_self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def OnMouseHover(self, *args):
        uthread.new(self.SetHint)

    def SetHint(self, *args):
        if not (self.sr and self.sr.node):
            return
        bookmark = self.sr.node.bm
        hint = self.sr.node.hint
        destination = sm.GetService('starmap').GetDestination()
        if destination is not None and destination == bookmark.itemID:
            hint = localization.GetByLabel('UI/PeopleAndPlaces/BookmarkHintCurrent', hintText=hint)
        else:
            hint = localization.GetByLabel('UI/PeopleAndPlaces/BookmarkHint', hintText=hint)
        self.sr.hint = hint

    def OnDblClick(self, *args):
        sm.GetService('addressbook').EditBookmark(self.sr.bm)

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        eve.Message('ListEntryClick')
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def OnMouseExit(self, *args):
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(const.typeBookmark, self.sr.bm.bookmarkID)

    def GetDragData(self, *args):
        ret = []
        for each in self.sr.node.scroll.GetSelectedNodes(self.sr.node):
            if not hasattr(each, 'itemID'):
                continue
            if isinstance(each.itemID, tuple):
                self.DisableDrag()
                eve.Message('CantTradeMissionBookmarks')
                return []
            ret.append(each)

        return ret

    def GetMenu(self):
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        m = []
        bmIDs = [ entry.bm.bookmarkID for entry in selected if entry.bm ]
        if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            bmids = []
            if len(bmIDs) > 10:
                text = uiutil.MenuLabel('UI/PeopleAndPlaces/BookmarkIDTooMany')
            else:
                idString = bmIDs
                text = uiutil.MenuLabel('UI/PeopleAndPlaces/BookmarkIDs', {'bookmarkIDs': idString})
            m += [(text, self.CopyItemIDToClipboard, (bmIDs,)), None]
            m.append(None)
        eve.Message('ListEntryClick')
        readonly = 0
        for bmID in bmIDs:
            if isinstance(bmID, tuple):
                readonly = 1

        if not multi:
            m += sm.GetService('menu').CelestialMenu(selected[0].bm.itemID, bookmark=selected[0].bm)
            if not readonly:
                m.append((uiutil.MenuLabel('UI/PeopleAndPlaces/EditViewLocation'), sm.GetService('addressbook').EditBookmark, (selected[0].bm,)))
        elif not readonly:
            m.append((uiutil.MenuLabel('UI/Inflight/RemoveBookmark'), self.Delete, (bmIDs,)))
        if self.sr.node.Get('GetMenu', None) is not None:
            m += self.sr.node.GetMenu(self.sr.node)
        return m

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def Approach(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp:
            bp.CmdGotoBookmark(self.sr.bm.bookmarkID)

    def WarpTo(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp:
            bp.CmdWarpToStuff('bookmark', self.sr.bm.bookmarkID)

    def Delete(self, bmIDs = None):
        ids = bmIDs or [ entry.bm.bookmarkID for entry in self.sr.node.scroll.GetSelected() ]
        if ids:
            sm.GetService('addressbook').DeleteBookmarks(ids)

    @classmethod
    def GetCopyData(cls, node):
        return node.label