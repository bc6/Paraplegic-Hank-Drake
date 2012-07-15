#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/sidePanelsLayer.py
import uicls
import uiconst

class SidePanels(uicls.LayerCore):
    __guid__ = 'uicls.SidePanelsLayer'

    def ApplyAttributes(self, attributes):
        uicls.LayerCore.ApplyAttributes(self, attributes)
        self.inactivePanels = ['sidePanel']
        self.leftPush = 0
        self.rightPush = 0

    def OnOpenView(self):
        sm.GetService('neocom').CreateNeocom()

    def Traverse(self, *args, **kw):
        needsUpdate = False
        for c in self.children:
            if c._alignmentDirty:
                needsUpdate = True
                break

        ret = uicls.LayerCore.Traverse(self, *args, **kw)
        if needsUpdate:
            self.UpdateWindowPositions()
        return ret

    def UpdateWindowPositions(self):
        dockedLeft = []
        dockedLeftGap = []
        dockedRight = []
        dockedRightGap = []
        for wnd in uicore.registry.GetValidWindows():
            if getattr(wnd, 'isImplanted', False):
                continue
            if wnd.name == 'mapbrowser':
                continue
            if wnd.left == self.leftPush:
                dockedLeft.append(wnd)
            elif wnd.left == self.leftPush + uicls.Window.SNAP_DISTANCE:
                dockedLeftGap.append(wnd)
            elif wnd.left + wnd.width == uicore.desktop.width - self.rightPush:
                dockedRight.append(wnd)
            elif wnd.left + wnd.width == uicore.desktop.width - self.rightPush - uicls.Window.SNAP_DISTANCE:
                dockedRightGap.append(wnd)

        self.leftPush, self.rightPush = self.GetSideOffset()
        for wnd in dockedLeft:
            wnd.left = self.leftPush

        for wnd in dockedLeftGap:
            wnd.left = self.leftPush + uicls.Window.SNAP_DISTANCE

        for wnd in dockedRight:
            wnd.left = uicore.desktop.width - self.rightPush - wnd.width

        for wnd in dockedRightGap:
            wnd.left = uicore.desktop.width - self.rightPush - wnd.width - uicls.Window.SNAP_DISTANCE

        layers = (uicore.layer.inflight, uicore.layer.station, uicore.layer.target)
        for layer in layers:
            layer.padLeft = self.leftPush
            layer.padRight = self.rightPush

    def GetSideOffset(self):
        leftPush = 0
        rightPush = 0
        for c in self.children:
            if not c.display or c.name in self.inactivePanels:
                continue
            if c.align == uiconst.TOLEFT:
                leftPush += c.width + c.left
            elif c.align == uiconst.TORIGHT:
                rightPush += c.width + c.left

        leftPush = int(round(leftPush))
        rightPush = int(round(rightPush))
        return (leftPush, rightPush)