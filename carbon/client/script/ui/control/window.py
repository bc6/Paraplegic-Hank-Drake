import blue
import bluepy
import uthread
import types
import log
import sys
import base
import uicls
import uiutil
import uiconst
import trinity
POSOVERLAPSHIFT = 11

class WindowCore(uicls.Area):
    __guid__ = 'uicls.WindowCore'
    default_width = 256
    default_height = 128
    default_minSize = (default_width, default_height)
    default_maxSize = (None, None)
    default_fixedHeight = None
    default_fixedWidth = None
    default_left = '__center__'
    default_top = '__center__'
    default_name = 'window'
    default_idx = 0
    default_windowID = None
    default_stackID = None
    default_args = ()
    default_caption = None
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        self.startingup = True
        self.ResetAttributes()
        self._CheckCallableDefaults()
        self.windowID = attributes.get('windowID', self.default_windowID)
        self.windowPrefsID = attributes.get('windowPrefsID') or self.windowID
        uicore.registry.RegisterWindow(self)
        (left, top, width, height,) = self.GetDefaultSizeAndPosition()
        attributes['left'] = left
        attributes['top'] = top
        if self.windowID:
            try:
                self.name = str(self.windowID)
            except Exception as e:
                self.name = repr(self.windowID)
        self.stackID = attributes.get('stackID', self.default_stackID)
        self.minsize = attributes.get('minSize', self.minsize)
        self.maxsize = attributes.get('maxSize', self.maxsize)
        uicls.Area.ApplyAttributes(self, attributes)
        self.InitializeSize()
        self.Prepare_()



    def PostApplyAttributes(self, attributes):
        self.RegisterPositionAndSize('width')
        self.RegisterPositionAndSize('height')
        self.InitializeStacking(attributes.get('showIfInStack', True))
        self.InitializeStatesAndPosition()
        self.startingup = False
        caption = attributes.get('caption', self.default_caption)
        if caption is not None:
            self.SetCaption(caption)



    def GetAbsolutePosition(self):
        return (self.left, self.top)



    def _CheckCallableDefaults(self):
        if callable(self.default_left):
            self.default_left = self.default_left()
        if callable(self.default_top):
            self.default_top = self.default_top()
        if callable(self.default_width):
            self.default_width = self.default_width()
        if callable(self.default_height):
            self.default_height = self.default_height()



    def Prepare_(self):
        self.Prepare_Header_()
        self.Prepare_LoadingIndicator_()
        self.Prepare_Background_()
        self.Prepare_ScaleAreas_()



    def Prepare_HeaderButtons_(self):
        if self.sr.headerButtons:
            self.sr.headerButtons.Close()
        self.sr.headerButtons = uicls.Container(name='headerButtons', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPRIGHT, parent=self, pos=(5, 0, 0, 16), idx=0)
        if self.sr.stack:
            closehint = mls.UI_GENERIC_CLOSEWINDOWSTACK
            minimizehint = mls.UI_CMD_MINIMIZEWINDOWSTACK
        else:
            closehint = mls.UI_GENERIC_CLOSE
            minimizehint = mls.UI_CMD_MINIMIZE
        w = 0
        for (icon, name, hint, showflag, clickfunc, menufunc,) in [(102,
          'close',
          closehint,
          self._killable,
          self._CloseClick,
          False), (103,
          'minimize',
          minimizehint,
          self._minimizable,
          self.Minimize,
          False)]:
            if not showflag:
                continue
            btn = uicls.ImageButton(name=name, parent=self.sr.headerButtons, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, pos=(w,
             0,
             16,
             16), idleIcon='ui_1_16_%s' % icon, mouseoverIcon='ui_1_16_%s' % (icon + 16), mousedownIcon='ui_1_16_%s' % (icon + 32), onclick=clickfunc, getmenu=menufunc, expandonleft=True, hint=hint)
            w += 15

        self.sr.headerButtons.width = w
        if self.sr.captionParent:
            self.sr.captionParent.padRight = w + 6



    def Prepare_Header_(self):
        if self.sr.headerParent:
            self.sr.headerParent.Close()
        self.sr.headerParent = uicls.Container(parent=self.sr.maincontainer, name='__headerParent', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP, pos=(0, 0, 0, 18), idx=0)
        self.sr.captionParent = uicls.Container(parent=self.sr.headerParent, name='__captionParent', state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self.sr.caption = uicls.Label(parent=self.sr.captionParent, name='__caption', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, idx=0, pos=(8, 0, 0, 0), uppercase=uiconst.WINHEADERUPPERCASE, fontsize=uiconst.WINHEADERFONTSIZE, letterspace=uiconst.WINHEADERLETTERSPACE)



    def Update_Header_(self):
        self.SetCaption(self._caption or 'Window')



    def Prepare_Background_(self):
        self.LoadUnderlay(color=(0.5, 0.5, 0.5, 1.0), offset=-8, iconPath='ui_2_32_8', cornerSize=14)



    def Prepare_ScaleAreas_(self):
        if self.sr.resizers:
            self.sr.resizers.Close()
        self.sr.resizers = uicls.Container(name='resizers', parent=self, state=uiconst.UI_PICKCHILDREN, idx=0)
        if not self._resizeable:
            return 
        for (name, align, w, h, cursor,) in [('sLeftTop',
          uiconst.TOPLEFT,
          8,
          8,
          15),
         ('sRightTop',
          uiconst.TOPRIGHT,
          6,
          6,
          13),
         ('sRightBottom',
          uiconst.BOTTOMRIGHT,
          8,
          8,
          15),
         ('sLeftBottom',
          uiconst.BOTTOMLEFT,
          8,
          8,
          13),
         ('sLeft',
          uiconst.TOLEFT,
          4,
          0,
          16),
         ('sRight',
          uiconst.TORIGHT,
          4,
          0,
          16),
         ('sTop',
          uiconst.TOTOP,
          0,
          4,
          17),
         ('sBottom',
          uiconst.TOBOTTOM,
          0,
          4,
          17)]:
            r = uicls.Fill(name=name, parent=self.sr.resizers, state=uiconst.UI_NORMAL, align=align, pos=(0,
             0,
             w,
             h), color=(0.0, 0.0, 0.0, 0.0))
            r.OnMouseDown = (self.StartScale, r)
            r.OnMouseUp = (self.EndScale, r)
            r.cursor = cursor




    def Prepare_LoadingIndicator_(self):
        if self.sr.loadingParent:
            self.sr.loadingParent.Close()
        self.sr.loadingParent = uicls.Container(name='__loadingParent', parent=self.sr.maincontainer, state=uiconst.UI_HIDDEN, idx=0)
        self.sr.loadingIndicator = uicls.AnimSprite(parent=self.sr.loadingParent, state=uiconst.UI_HIDDEN, align=uiconst.TOPRIGHT, left=5)



    def ResetAttributes(self):
        self._grab = [0, 0]
        self._dragging = False
        self._draginited = False
        self._scaling = False
        self._ret = None
        self._changing = False
        self._requesthideload = False
        self._caption = ''
        self._fixedWidth = self.default_fixedWidth
        self._fixedHeight = self.default_fixedHeight
        self._prelockdata = None
        self._splitList = []
        self._collapsed = False
        self._locked = False
        self._minimized = 0
        self._open = False
        self.isModal = False
        self.isDialog = False
        self.snapGrid = None
        self._killable = True
        self._minimizable = True
        self._stackable = True
        self._resizeable = True
        self._collapseable = 1
        self._anchorable = 1
        self.headerIconNo = None
        self.headerIconHint = None
        self.sr.minimizedBtn = None
        self.sr.tab = None
        self.sr.caption = None
        self.sr.modalParent = None
        self.sr.buttonParent = None
        self.sr.loadingParent = None
        self.sr.headerIcon = None
        self.sr.snapIndicator = None
        self.sr.headerLine = None
        self.sr.headerButtonsTimer = None
        self.sr.resizers = None
        self.sr.stack = None
        self.sr.headerParent = None
        self.sr.headerButtons = None
        self.sr.captionParent = None
        self.sr.loadingIndicator = None
        width = self.default_width
        height = self.default_height
        self.minsize = self.default_minSize
        self.maxsize = self.default_maxSize



    def GetMainArea(self):
        return self.sr.maincontainer



    def InStack(self):
        return bool(self.sr.stack)



    def GetStack(self):
        return self.sr.stack



    def GetStackID(self):
        if self.windowPrefsID:
            all = settings.user.windows.Get('stacksWindows', {})
            if self.windowPrefsID in all:
                return all[self.windowPrefsID]
            return all.get(self.windowPrefsID, self.stackID)



    def RegisterStackID(self, stack = None):
        if self.windowPrefsID:
            all = settings.user.windows.Get('stacksWindows', {})
            if stack:
                all[self.windowPrefsID] = stack.windowID
            else:
                all[self.windowPrefsID] = None
            settings.user.windows.Set('stacksWindows', all)



    def InitializeSize(self):
        d = uicore.desktop
        (left, top, width, height, dw, dh,) = self.GetRegisteredPositionAndSize()
        (maxWidth, maxHeight,) = (self.GetMaxWidth(), self.GetMaxHeight())
        (minWidth, minHeight,) = (self.GetMinWidth(), self.GetMinHeight())
        if self._fixedWidth:
            self.width = self._fixedWidth
        else:
            self.width = min(maxWidth, max(minWidth, min(d.width, width)))
        if self._fixedHeight:
            self.height = self._fixedHeight
        else:
            self.height = min(maxHeight, max(minHeight, min(d.height, height)))



    def InitializeStacking(self, setFocus = True):
        if getattr(self, 'isModal', 0):
            return 
        (left, top, width, height, dw, dh,) = self.GetRegisteredPositionAndSize()
        if self._stackable:
            stackID = self.GetStackID()
            stackIsOpen = bool(uicore.registry.GetWindow(stackID))
            if stackID is not None and not isinstance(self, self.GetStackClass()):
                stack = uicore.registry.GetStack(stackID, self.GetStackClass())
                if stack is not None:
                    self.left = max(0, min(uicore.desktop.width - self.width, left))
                    self.top = max(0, min(uicore.desktop.height - self.height, top))
                    stack.InsertWnd(self, not stackIsOpen, setFocus, 1)



    def GetStackClass(self):
        return uicls.WindowStackCore



    def InitializeStatesAndPosition(self, expandIfCollapsed = False, skipCornerAligmentCheck = False):
        if not self.sr.stack:
            collapsed = self.GetRegisteredState('collapsed')
            if not expandIfCollapsed and collapsed:
                self.Collapse(True)
            else:
                self.Expand(True)
                focus = uicore.registry.GetFocus()
                if not (focus and (isinstance(focus, uicls.EditCore) or isinstance(focus, uicls.SinglelineEditCore))):
                    uthread.new(uicore.registry.SetFocus, self)
            if skipCornerAligmentCheck or not self.TryAlignToCornerGroup():
                d = uicore.desktop
                (left, top, width, height, dw, dh,) = self.GetRegisteredPositionAndSize()
                self.left = max(0, min(d.width - self.width, left))
                self.top = max(0, min(d.height - self.height, top))
                self.CheckWndPos()
            self.state = uiconst.UI_NORMAL
        locked = self.GetRegisteredState('locked')
        if locked:
            self.Lock()
        else:
            self.Unlock()
        self._SetOpen(True)



    def TryAlignToCornerGroup(self):
        cornerAlignment = self.GetCornerAlignment()
        if cornerAlignment:
            windowGroups = self.GetWindowGroups(checking=1, cornerCheck=1)
            (corner, wndChainImIn,) = cornerAlignment
            wndChainImIn = list(wndChainImIn)
            if corner in windowGroups:
                if self.windowID in wndChainImIn:
                    myIdxInChain = wndChainImIn.index(self.windowID)
                else:
                    myIdxInChain = max(0, len(wndChainImIn) - 1)
                wndsInCorner = list(windowGroups[corner])
                if corner in ('topright', 'topleft'):
                    side = 'bottom'
                    cside = 'top'
                else:
                    side = 'top'
                    cside = 'bottom'
                    wndsInCorner.reverse()
                prevWndName = wndsInCorner[max(0, min(len(wndsInCorner) - 1, myIdxInChain - 1))]
                prevWnd = uicore.registry.GetWindow(prevWndName)
                if prevWnd and prevWnd != self and prevWnd.windowID in wndChainImIn:
                    prevWndIdxInChain = wndChainImIn.index(prevWnd.windowID)
                    if prevWndIdxInChain >= myIdxInChain:
                        side = cside
                    prevWnd.AttachWindow(self, side, 0)
                    return True
                maxRange = len(wndChainImIn)
                rnge = [ i for i in xrange(myIdxInChain, maxRange) ]
                if myIdxInChain > 0:
                    rnge += [ abs(i - myIdxInChain) - 1 for i in xrange(0, myIdxInChain) ]
                for idx in rnge:
                    checkWnd = uicore.registry.GetWindow(wndChainImIn[idx])
                    if checkWnd and checkWnd != self:
                        checkWnd.AttachWindow(self, side, 0)
                        return True

            elif 'top' in corner:
                self.top = 16
            elif 'bottom' in corner:
                self.top = uicore.desktop.height - self.height - 16
            if 'left' in corner:
                self.left = 16
            elif 'right' in corner:
                self.left = uicore.desktop.width - self.width - 16
        return False



    def CheckCorners(self):
        windowGroups = self.GetWindowGroups(checking=1, cornerCheck=1)
        current = self.GetCurrentCornerAlignment_()
        for cornerKey in windowGroups:
            wndNames = list(windowGroups[cornerKey])
            if 'bottom' in cornerKey:
                wndNames.reverse()
            i = 0
            for wndName in wndNames:
                for currentCornerKey in current:
                    if cornerKey == currentCornerKey:
                        continue
                    inCurrentCorner = current[currentCornerKey]
                    if wndName in inCurrentCorner:
                        inCurrentCorner.remove(wndName)

                if cornerKey not in ('topright', 'topleft', 'bottomright', 'bottomleft'):
                    continue
                if cornerKey not in current:
                    current[cornerKey] = []
                if wndName not in current[cornerKey]:
                    current[cornerKey].insert(i, wndName)
                i += 1


        settings.user.windows.Set('windowCornerGroups_1', current)



    def GetCornerAlignment(self):
        if self.windowPrefsID:
            current = self.GetCurrentCornerAlignment_()
            for cornerKey in current:
                if cornerKey and self.windowPrefsID in current[cornerKey]:
                    return (cornerKey, current[cornerKey])




    def GetCurrentCornerAlignment_(self):
        return settings.user.windows.Get('windowCornerGroups_1', {})



    def GetWindowGroups(self, refresh = 0, checking = 0, cornerCheck = 0):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(1, floatingOnly=True)
        knownGroups = {}
        for wnd in all:
            if wnd.sr.stack is not None:
                continue
            if cornerCheck:
                wndGroup = wnd.FindConnectingWindows(wnd, 'top', fullSideOnly=True)[1:] + wnd.FindConnectingWindows(wnd, 'bottom', fullSideOnly=True)
            else:
                wndGroup = wnd.FindConnectingWindows(wnd)
            (l, t, r, b,) = self.GetBoundries(wndGroup)
            sorted = uiutil.SortListOfTuples([ ((_wnd.top, _wnd.left), _wnd) for _wnd in wndGroup ])
            groupNames = tuple([ _wnd.windowID or _wnd.name for _wnd in sorted if getattr(_wnd, 'registerCornerAlignment', 1) ])
            if t in (0, 16):
                side = 'top'
            elif b in (0, 16):
                side = 'bottom'
            else:
                side = ''
            if l in (0, 16):
                side += 'left'
            elif r in (0, 16):
                side += 'right'
            if checking:
                if side in knownGroups:
                    if groupNames != knownGroups[side]:
                        knownGroups[side] += groupNames
                else:
                    knownGroups[side] = groupNames
            elif side:
                knownGroups[(groupNames, side)] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)
            else:
                knownGroups[(groupNames, 'left')] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)
                knownGroups[(groupNames, 'top')] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)

        return knownGroups



    def RegisterState(self, statename):
        if self.windowPrefsID is None:
            return 
        val = getattr(self, statename, 'notset')
        if val == 'notset':
            return 
        all = settings.user.windows.Get('%sWindows' % statename[1:], {})
        all[self.windowPrefsID] = val
        settings.user.windows.Set('%sWindows' % statename[1:], all)



    def GetRegisteredState(self, statename):
        if self.windowPrefsID is None:
            return 0
        all = settings.user.windows.Get('%sWindows' % statename, {})
        if self.windowPrefsID in all:
            return all[self.windowPrefsID]
        if hasattr(self, 'default_%s' % statename):
            return getattr(self, 'default_%s' % statename)



    def RegisterPositionAndSize(self, key = None):
        if self.windowPrefsID is None:
            return 
        if self._changing or self.IsMinimized():
            return 
        stackID = self.GetStackID()
        if self.sr.stack:
            (l, t,) = (self.sr.stack.left, self.sr.stack.top)
            (w, h,) = (self.sr.stack.width, self.sr.stack.height)
            (cl, ct, cw, ch, cdw, cdh,) = self.sr.stack.GetRegisteredPositionAndSize()
        elif stackID:
            return 
        if self.GetAlign() != uiconst.RELATIVE:
            return 
        (l, t,) = (self.left, self.top)
        (w, h,) = (self.width, self.height)
        (cl, ct, cw, ch, cdw, cdh,) = self.GetRegisteredPositionAndSize()
        if key is not None:
            if key == 'left':
                (t, w, h,) = (ct, cw, ch)
            elif key == 'top':
                (l, w, h,) = (cl, cw, ch)
            elif key == 'width':
                (l, t, h,) = (cl, ct, ch)
            elif key == 'height':
                (l, t, w,) = (cl, ct, cw)
        if self.IsCollapsed():
            h = ch
        (dw, dh,) = (uicore.desktop.width, uicore.desktop.height)
        all = settings.user.windows.Get('windowSizesAndPositions_1', {})
        all[self.windowPrefsID] = (l,
         t,
         w,
         h,
         dw,
         dh)
        settings.user.windows.Set('windowSizesAndPositions_1', all)
        if isinstance(self, self.GetStackClass()):
            for each in self.sr.content.children:
                each.RegisterPositionAndSize()




    def GetRegisteredPositionAndSize(self):
        (left, top, width, height,) = self.GetDefaultSizeAndPosition()
        (cdw, cdh,) = (uicore.desktop.width, uicore.desktop.height)
        usingDefault = 1
        if self.windowPrefsID:
            all = settings.user.windows.Get('windowSizesAndPositions_1', {})
            if self.windowPrefsID in all:
                (left, top, width, height, cdw, cdh,) = all[self.windowPrefsID]
                usingDefault = 0
        if usingDefault:
            pushleft = self.GetDefaultLeftOffset(width=width, align=uiconst.CENTER, left=left)
            if pushleft < 0:
                left = max(0, left + pushleft)
            elif pushleft > 0:
                left = min(left + pushleft, uicore.desktop.width - width)
        (dw, dh,) = (uicore.desktop.width, uicore.desktop.height)
        if cdw != dw:
            wDiff = dw - cdw
            if left + width in (cdw, cdw - 16):
                left += wDiff
            elif left not in (0, 16):
                oldCenterX = (cdw - width) / 2
                xPortion = oldCenterX / float(cdw)
                newCenterX = int(xPortion * dw)
                cxDiff = newCenterX - oldCenterX
                left += cxDiff
        if cdh != dh:
            hDiff = dh - cdh
            if top in (0, 16):
                pass
            elif top + height in (cdh, cdh - 16):
                top += hDiff
            oldCenterY = (cdh - height) / 2
            yPortion = oldCenterY / float(cdh)
            newCenterY = int(yPortion * dh)
            cyDiff = newCenterY - oldCenterY
            top += cyDiff
        return (left,
         top,
         width,
         height,
         dw,
         dh)



    def GetDefaultSizeAndPosition(self):
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        width = self.default_width
        height = self.default_height
        if self.default_left == '__center__':
            l = (dw - width) / 2
        elif self.default_left == '__right__':
            l = dw - width
        else:
            l = self.default_left
        if self.default_top == '__center__':
            t = (dh - height) / 2
        elif self.default_top == '__bottom__':
            t = dh - height
        else:
            t = self.default_top
        return (l,
         t,
         width,
         height)



    def SetFixedHeight(self, height = None):
        self._fixedHeight = height



    def SetFixedWidth(self, width = None):
        self._fixedWidth = width



    def GetMinSize(self, *args, **kw):
        (w, h,) = uicls.Area.GetMinSize(self, *args, **kw)
        if self.sr.buttonParent:
            (bw, bh,) = self._GetMinSize(self.sr.buttonParent)
            w = max(w, bw)
            h = max(h, bh)
        if self.sr.headerParent and self.sr.headerParent.state != uiconst.UI_HIDDEN:
            h += self.sr.headerParent.height
        return (w, h)



    def IsCurrentDialog(self):
        ret = getattr(self, 'isDialog', False) and (not getattr(self, 'isModal', False) or uicore.registry.GetModalWindow() == self)
        return ret



    def _CloseClick(self, *args):
        self._SetOpen(False)
        self.SelfDestruct(checkOthers=1)



    def SelfDestruct(self, checkStack = 1, checkOthers = 0, checkOutmost = 1, *args):
        sm.ScatterEvent('OnWindowClosed', self.windowID, self.GetCaption(), self.__guid__)
        if self._ret:
            self.SetModalResult(uiconst.ID_CLOSE, 'SelfDestruct')
            return 
        alignedWindows = []
        if checkOthers:
            if checkOutmost:
                self.CheckIfOutmost()
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            if shift or ctrl:
                if shift:
                    alignedWindows = self.FindConnectingWindows(self)
                else:
                    alignedWindows = self.FindConnectingWindows(self, 'bottom')
        stack = self.sr.stack
        if getattr(self, 'OnClose_', None):
            self.OnClose_(self)
            if self.destroyed:
                return 
            self.OnClose_ = None
        self.state = uiconst.UI_HIDDEN
        if self is not None and not self.destroyed:
            uicore.registry.CheckMoveActiveState(self)
            self.Close()
        if checkStack and stack is not None and not stack.destroyed:
            stack.Check(checknone=1)
        for each in alignedWindows:
            if each == self:
                continue
            if not each.destroyed and each._killable:
                each.SelfDestruct(checkOthers=1)




    def _OnClose(self, *args):
        uicls.Area._OnClose(self)
        if not hasattr(self, 'sr'):
            return 
        if self._ret:
            self.SetModalResult(uiconst.ID_CLOSE, '_OnClose')
            return 
        if self.sr.minimizedBtn:
            self.sr.minimizedBtn.Close()
            self.sr.minimizedBtn = None
            self.ArrangeMinimizedButtons()
        if self.sr.modalParent is not None and not self.sr.modalParent.destroyed:
            self.sr.modalParent.Close()
        uicore.registry.UnregisterWindow(self)
        self.OnScale_ = None
        self.OnStartScale_ = None
        self.OnEndScale_ = None
        self.OnMouseDown_ = None
        self.OnStartMinimize_ = None
        self.OnEndMinimize_ = None
        self.OnStartMaximize_ = None
        self.OnEndMaximize_ = None
        self.OnDropData = None
        self.Confirm = None
        self.OnClose_ = None
        self.OnResize_ = None
        self.OnCollapsed = None
        self.OnExpanded = None



    def CheckIfOutmost(self):
        if not self or self.destroyed:
            return 
        if self.GetAlign() == uiconst.RELATIVE:
            dh = self.parent.height
            wnds = self.FindConnectingWindows(self, 'top') + self.FindConnectingWindows(self, 'bottom')
            if not wnds:
                return 
            (gl, gt, gw, gh,) = self.GetGroupAbsolute(wnds)
            ok = []
            for each in wnds:
                if each not in ok and each != self:
                    ok.append((each.top, each))

            wnds = uiutil.SortListOfTuples(ok)
            if gt in (0, 16):
                top = gt
                for wnd in wnds:
                    wnd.top = top
                    top += wnd.height

            elif gt + gh in (dh, dh - 16):
                bottom = gt + gh
                wnds.reverse()
                for wnd in wnds:
                    bottom -= wnd.height
                    wnd.top = bottom




    def ShowHeaderButtons(self, refresh = False, *args):
        if refresh:
            if self.sr.headerButtons:
                self.sr.headerButtons.Close()
                self.sr.headerButtons = None
            else:
                return 
        if self.sr.stack or self.GetAlign() != uiconst.RELATIVE or uicore.uilib.leftbtn:
            return 
        if self.sr.headerParent and self.sr.headerParent.state == uiconst.UI_HIDDEN:
            return 
        if not self.sr.headerButtons:
            self.Prepare_HeaderButtons_()
        if self.sr.headerButtons:
            w = self.sr.headerButtons.width
            if self.sr.captionParent:
                self.sr.captionParent.padRight = w + 6
            if self.sr.loadingIndicator:
                self.sr.loadingIndicator.left = w
        self.sr.headerButtonsTimer = base.AutoTimer(1000, self.CloseHeaderButtons)



    def CloseHeaderButtons(self, *args):
        if not uicore.uilib.leftbtn and (uicore.uilib.mouseOver is self or uiutil.IsUnder(uicore.uilib.mouseOver, self)):
            return 
        if self.sr.headerButtons:
            self.sr.headerButtons.Close()
            self.sr.headerButtons = None
        self.sr.headerButtonsTimer = None
        if self.sr.captionParent:
            self.sr.captionParent.padRight = 6
        if self.sr.loadingIndicator:
            self.sr.loadingIndicator.left = 5



    def _OnResize(self, *args, **kw):
        uicls.Area._OnResize(self, *args, **kw)
        if not getattr(self, 'startingup', True):
            self.RegisterPositionAndSize()
        if self.OnResize_:
            self.OnResize_(self)



    def HideHeader(self):
        self._collapseable = 0
        if self.sr.headerParent:
            self.sr.headerParent.state = uiconst.UI_HIDDEN



    def ShowHeader(self):
        self._collapseable = 1
        if self.sr.headerParent:
            self.sr.headerParent.state = uiconst.UI_PICKCHILDREN



    def ShowBackground(self):
        self.Prepare_Background_()



    def HideBackground(self):
        self.LoadUnderlay(color=(0.5, 0.5, 0.5, 0.0))



    def Blink(self):
        if self.state == uiconst.UI_HIDDEN and self.sr.tab and hasattr(self.sr.tab, 'Blink'):
            self.sr.tab.Blink(1)
        if self.state == uiconst.UI_HIDDEN and self.sr.minimizedBtn and hasattr(self.sr.minimizedBtn, 'SetBlink'):
            self.sr.minimizedBtn.SetBlink(1)
        elif self.sr.stack is not None and (self.sr.stack.state != uiconst.UI_NORMAL or self.state != uiconst.UI_NORMAL):
            if self.sr.stack.sr.minimizedBtn and hasattr(self.sr.stack.sr.minimizedBtn, 'SetBlink'):
                self.sr.stack.sr.minimizedBtn.SetBlink(1)



    def GetMenu(self, *args):
        menu = []
        if self._killable:
            menu.append((mls.UI_CMD_CLOSE, self._CloseClick))
        if not self.sr.stack and self._minimizable:
            if not getattr(self, 'isModal', 0):
                if self.state == uiconst.UI_NORMAL:
                    menu.append((mls.UI_CMD_MINIMIZE, self.ToggleVis))
                else:
                    menu.append((mls.UI_CMD_MAXIMIZE, self.ToggleVis))
        return menu



    def ShowLoad(self, doBlock = True):
        self._requesthideload = False
        if self.sr.loadingParent:
            if doBlock:
                self.sr.loadingParent.state = uiconst.UI_NORMAL
            else:
                self.sr.loadingParent.state = uiconst.UI_DISABLED
            if self.sr.loadingIndicator and hasattr(self.sr.loadingIndicator, 'Play'):
                if not (self.sr.stack or self.GetAlign() != uiconst.RELATIVE):
                    self.sr.loadingIndicator.sr.hint = mls.UI_GENERIC_LOADING
                    self.sr.loadingIndicator.Play()
        if not self.destroyed and self._requesthideload:
            self.HideLoad()



    def HideLoad(self):
        if self.sr.loadingIndicator and hasattr(self.sr.loadingIndicator, 'Stop'):
            self.sr.loadingIndicator.Stop()
        if self.sr.loadingParent:
            self.sr.loadingParent.state = uiconst.UI_HIDDEN
        self._requesthideload = True



    def ShowModal(self):
        return self.ShowDialog(modal=True)



    def ShowDialog(self, modal = False, state = uiconst.UI_NORMAL):
        self.isDialog = True
        self.isModal = modal
        self.state = uiconst.UI_HIDDEN
        self.MakeUnMinimizable()
        if modal:
            if self.parent and not self.parent.destroyed and self.parent.name[:8] == 'l_modal_':
                self.parent.SetOrder(0)
            else:
                myLayer = uicls.Container(name='l_modal_%s' % self.name, state=uiconst.UI_NORMAL, parent=uicore.layer.modal, idx=0)
                uiutil.Transplant(self, myLayer)
                self.sr.modalParent = myLayer
                self.ModalPosition()
            uicore.registry.AddModalWindow(self)
        self._ret = uthread.Channel()
        self.state = state
        if modal:
            uicore.registry.SetFocus(self)
        self.HideLoad()
        ret = self._ret.receive()
        return ret



    def ModalPosition(self):
        otherModal = uicore.registry.GetModalWindow()
        if otherModal and otherModal.state == uiconst.UI_NORMAL and otherModal.parent.state == uiconst.UI_NORMAL:
            self.left = otherModal.left + 16
            self.top = otherModal.top + 16
            if self.left + self.width > uicore.desktop.width:
                self.left = 0
            if self.top + self.height > uicore.desktop.height:
                self.top = 0
        else:
            cameraOffset = self.GetDefaultLeftOffset(self.width, align=uiconst.CENTER, left=0)
            self.left = (uicore.desktop.width - self.width) / 2 + cameraOffset
            self.top = (uicore.desktop.height - self.height) / 2



    def ButtonResult(self, button, *args):
        if self.IsCurrentDialog():
            self.SetModalResult(button.btn_modalresult, 'ButtonResult')



    def __ConfirmFunction(self, button, *args):
        uicore.registry.Confirm(button)



    def SetButtons(self, buttons, okLabel = None, okFunc = None, cancelLabel = None, cancelFunc = None, defaultBtn = None):
        if self.sr.buttonParent is None:
            self.sr.buttonParent = self.Split(uiconst.SPLITBOTTOM, 24, line=0)
        self.sr.buttonParent.Flush()
        if buttons is None:
            self.sr.buttonParent.state = uiconst.UI_HIDDEN
            return 
        okFunc = okFunc or self._WindowCore__ConfirmFunction
        cancelFunc = cancelFunc or self.ButtonResult
        btns = []
        if buttons in (uiconst.YESNO, uiconst.YESNOCANCEL):
            btns.append(self.GetButtonData('YES', defaultBtn))
            btns.append(self.GetButtonData('NO', defaultBtn))
        if buttons in (uiconst.OKCANCEL, uiconst.YESNOCANCEL):
            btns.append(self.GetButtonData('CANCEL', defaultBtn, cancelLabel, cancelFunc))
        if buttons in (uiconst.OKCLOSE, uiconst.CLOSE):
            btns.append(self.GetButtonData('CLOSE', defaultBtn, None, self._CloseClick))
        if buttons in (uiconst.OK, uiconst.OKCANCEL, uiconst.OKCLOSE) or not btns:
            btns.insert(0, self.GetButtonData('OK', defaultBtn, okLabel, okFunc))
        bg = uicls.ButtonGroup(parent=self.sr.buttonParent.sr.content, buttons=btns, buttonClass=getattr(self, '_buttonClass', uicls.WindowButton))
        self.sr.buttonParent.height = bg.height + 8
        self.sr.buttonParent.state = uiconst.UI_PICKCHILDREN



    def SetButtonClass(self, buttonClass):
        self._buttonClass = buttonClass



    def GetButtonData(self, btnStringID, defaultBtnID, label = None, func = None):
        btnID = getattr(uiconst, 'ID_%s' % btnStringID, -1)
        bd = uiutil.Bunch()
        bd.label = label or btnStringID
        bd.func = func or self.ButtonResult
        bd.args = None
        bd.btn_modalresult = btnID
        bd.btn_default = bool(btnID == defaultBtnID)
        bd.btn_cancel = bool(btnStringID in ('CANCEL', 'CLOSE'))
        return bd



    def SetModalResult(self, result, caller = None, close = True):
        if self._ret:
            uicore.registry.RemoveModalWindow(self)
            self._ret.send(result)
            self._ret = None
        if close:
            self.SelfDestruct()



    def MakeUnResizeable(self):
        self._resizeable = False
        self.Prepare_ScaleAreas_()
        self.MakeUnstackable()
        self.ShowHeaderButtons(1)



    def IsMinimizable(self):
        return self._minimizable



    def MakeUnMinimizable(self):
        self._minimizable = False
        self.ShowHeaderButtons(1)



    def MakeUnKillable(self):
        self._killable = False
        self.ShowHeaderButtons(1)



    def MakeKillable(self):
        self._killable = True
        self.ShowHeaderButtons(1)



    def IsKillable(self):
        return self._killable



    def MakeUnstackable(self):
        self._stackable = False
        self.ShowHeaderButtons(1)



    def MakeStackable(self):
        self._stackable = True
        self.ShowHeaderButtons(1)



    def MakeCollapseable(self):
        self._collapseable = True
        self.ShowHeaderButtons(1)



    def MakeUncollapseable(self):
        self._collapseable = False
        self.ShowHeaderButtons(1)



    def MakeAnchorable(self):
        self._anchorable = True



    def MakeUnanchorable(self):
        self._anchorable = False



    def IsResizeable(self):
        return self._resizeable



    def Lock(self):
        if self.IsLocked():
            return 
        self._prelockdata = (self._stackable, self._resizeable)
        self.MakeUnstackable()
        self.MakeUnResizeable()
        self._SetLocked(True)
        self.ShowHeaderButtons(1)



    def Unlock(self):
        if self._prelockdata:
            (self._stackable, self._resizeable,) = self._prelockdata
            self._prelockdata = None
        self.Prepare_ScaleAreas_()
        self._SetLocked(False)
        self.ShowHeaderButtons(1)



    def IsLocked(self):
        return self._locked



    def _SetLocked(self, isLocked):
        self._locked = isLocked
        self.RegisterState('_locked')



    def SetMinSize(self, size, refresh = 0):
        self.minsize = size
        if self.GetAlign() == uiconst.RELATIVE and not self.sr.stack:
            if not self.IsCollapsed():
                if self.height < self.minsize[1]:
                    self.height = self.minsize[1]
                if self.width < self.minsize[0]:
                    self.width = self.minsize[0]
                if refresh:
                    (self.width, self.height,) = self.minsize
        if self.sr.stack:
            self.sr.stack.Check()



    def SetMaxSize(self, size, refresh = 0):
        self.maxsize = size
        (maxWidth, maxHeight,) = size
        if self.GetAlign() == uiconst.RELATIVE:
            if not self.IsCollapsed():
                if maxWidth is not None and self.width > maxWidth:
                    self.width = maxWidth
                if maxHeight is not None and self.height > maxHeight:
                    self.height = maxHeight
                if refresh:
                    if maxWidth is not None:
                        self.width = maxWidth
                    if maxHeight is not None:
                        self.height = maxHeight
        if self.sr.stack:
            self.sr.stack.Check()



    def SetCaption(self, caption, delete = 1):
        self._caption = (self._caption, '')[delete] + caption
        if self.sr.caption is None:
            return 
        self.sr.caption.text = self._caption
        if self.sr.headerParent:
            self.sr.headerParent.height = max(16, self.sr.caption.textheight + 4)
        if delete:
            if self.sr.minimizedBtn and hasattr(self.sr.minimizedBtn, 'SetLabel'):
                self.sr.minimizedBtn.SetLabel(self._caption)
            if self.sr.tab and hasattr(self.sr.tab, 'SetLabel'):
                self.sr.tab.SetLabel(self._caption)



    def GetCaption(self, update = 1):
        self.UpdateCaption_(self)
        return self._caption



    def _LockHeight(self, height):
        self._fixedHeight = height
        if self.sr.stack is None:
            self.height = height
        if self.sr.resizers:
            for each in self.sr.resizers.children:
                if each.name in ('sTop', 'sBottom', 'sRightTop', 'sLeftTop', 'sRightBottom', 'sLeftBottom'):
                    each.state = uiconst.UI_HIDDEN




    def UnlockHeight(self):
        self._fixedHeight = None



    def ToggleVis(self, *args):
        if self.state != uiconst.UI_HIDDEN:
            uicore.registry.CheckMoveActiveState(self)
            self.Minimize()
        else:
            self.Maximize()



    def Maximize(self, silent = 0, expandIfCollapsed = True):
        if self is None or self.destroyed:
            return 
        if self.sr.stack:
            return self.sr.stack.Maximize(silent, expandIfCollapsed)
        self._changing = True
        if self.sr.minimizedBtn:
            self.sr.minimizedBtn.Close()
            self.sr.minimizedBtn = None
            self.ArrangeMinimizedButtons()
        if self.sr.stack:
            self._SetMinimized(False)
            self.sr.stack.ShowWnd(self)
            self.sr.stack.Maximize()
            self._changing = False
            return 
        self.OnStartMaximize_(self)
        if expandIfCollapsed and self.IsCollapsed():
            self.Expand(0)
        self.SetOrder(0)
        self._SetMinimized(False)
        self.state = uiconst.UI_NORMAL
        self.OnEndMaximize_(self)
        self._changing = False


    Show = Maximize

    def Hide(self, *args, **kw):
        uicls.Area.Hide(self, *args, **kw)
        uicore.registry.CheckMoveActiveState(self)



    def Minimize(self, *args):
        if self.sr.stack:
            return self.sr.stack.Minimize()
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if shift or ctrl:
            if shift:
                alignedWindows = self.FindConnectingWindows(self)
            else:
                alignedWindows = self.FindConnectingWindows(self, 'bottom')
            for each in alignedWindows:
                if each == self:
                    continue
                self._Minimize(each)

        self._Minimize(self)



    def IsMinimized(self):
        if self.sr.stack:
            return bool(self.sr.stack.IsMinimized())
        return bool(self._minimized)



    def _SetMinimized(self, isMinimized):
        self._minimized = isMinimized
        self.RegisterState('_minimized')



    def IsCollapsed(self):
        if self.sr.stack:
            return bool(self.sr.stack.IsCollapsed())
        return bool(self._collapsed)



    def _SetCollapsed(self, isCollapsed):
        self._collapsed = isCollapsed
        self.RegisterState('_collapsed')



    def _SetOpen(self, isOpen):
        self._open = isOpen
        self.RegisterState('_open')



    def _Minimize(self, wnd):
        if not wnd or wnd.destroyed or wnd.IsMinimized() or wnd.sr.minimizedBtn:
            return 
        wnd.OnStartMinimize_(wnd)
        wnd._changing = True
        uicore.registry.CheckMoveActiveState(wnd)
        btn = uicls.WindowMinimizeButton(parent=uicore.layer.main, name='windowBtn', align=uiconst.BOTTOMLEFT, state=uiconst.UI_NORMAL, pos=(0, 0, 100, 18), idx=0)
        btn.Startup(wnd)
        wnd.sr.minimizedBtn = btn
        self.ArrangeMinimizedButtons()
        if wnd.destroyed:
            return 
        wnd._SetMinimized(True)
        wnd.state = uiconst.UI_HIDDEN
        wnd.OnEndMinimize_(wnd)
        wnd._changing = False



    def ArrangeMinimizedButtons(self):
        if not self.parent:
            return 
        l = 0
        for each in self.parent.children:
            if isinstance(each, uicls.WindowMinimizeButton):
                each.left = l
                l += each.width




    def CheckShiftUpwards(self, heightDiff = None):
        if self.GetAlign() == uiconst.RELATIVE:
            (pl, pt, pw, ph,) = self.parent.GetAbsolute()
            bottomwnds = self.FindConnectingWindows(self, 'bottom')
            topwnds = self.FindConnectingWindows(self, 'top')
            (bl, bt, bw, bh,) = self.GetGroupAbsolute(bottomwnds + topwnds)
            if bt in (0, 16):
                wnds = bottomwnds
                direction = 1
            elif bt + bh in (ph, ph - 16):
                wnds = topwnds
                direction = -1
            else:
                return 
            h = heightDiff or self.height
            if len(wnds) > 1:
                for wnd in wnds[1:]:
                    if wnd == self:
                        continue
                    wnd.top += h * direction




    def OnMouseEnter(self, *args):
        self.ShowHeaderButtons()



    def OnMouseExit(self, *args):
        self.CloseHeaderButtons()



    def OnMouseDown(self, *args):
        self.OnMouseDown_(self)
        if not self.IsLocked():
            self._dragging = True
            ctrlDragWindows = self.FindConnectingWindows(self, 'bottom')
            shiftDragWindows = self.FindConnectingWindows(self)
            self.PrepareWindowsForMove(shiftDragWindows)
            uthread.new(self.BeginDrag, ctrlDragWindows, shiftDragWindows)
        self.SetOrder(0)



    def GetDragClipRects(self, shiftGroup, ctrlGroup):
        (ml, mt, mw, mh,) = self.GetAbsolute()
        (sl, st, sw, sh,) = self.GetGroupAbsolute(shiftGroup)
        (cl, ct, cw, ch,) = self.GetGroupAbsolute(ctrlGroup)
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        return ((0,
          y - mt,
          pw,
          ph - (mt + self.GetCollapsedHeight() - y) + 1), (x - sl,
          y - st,
          pw - (sl + sw - x) + 1,
          ph - (st + sh - y) + 1), (x - cl,
          y - ct,
          pw - (cl + cw - x) + 1,
          ph - (ct + ch - y) + 1))



    def BeginDrag(self, ctrlDragWindows = None, shiftDragWindows = None):
        while not self.destroyed and self._dragging:
            if uicore.uilib.mouseTravel > 1:
                break
            blue.pyos.synchro.Yield()

        if self.destroyed or not self._dragging or self._draginited:
            return 
        if ctrlDragWindows is None:
            ctrlDragWindows = self.FindConnectingWindows(self, 'bottom')
        if shiftDragWindows is None:
            shiftDragWindows = self.FindConnectingWindows(self)
            self.PrepareWindowsForMove(shiftDragWindows)
        snapGrid = None
        snapGroup = None
        snapIndicator = self.GetSnapIndicator()
        (allGrid, myGrid, shiftGrid, ctrlGrid,) = self.CreateSnapGrid(shiftDragWindows, ctrlDragWindows)
        (myRect, shiftRect, ctrlRect,) = self.GetDragClipRects(shiftDragWindows, ctrlDragWindows)
        self._draginited = 1
        while self and not self.destroyed and self._dragging and uicore.uilib.leftbtn and self.GetAlign() == uiconst.RELATIVE:
            self.state = uiconst.UI_DISABLED
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            self.left = uicore.uilib.x - self._grab[0]
            self.top = uicore.uilib.y - self._grab[1]
            for each in shiftDragWindows:
                if each == self:
                    continue
                if shift or ctrl and each in ctrlDragWindows:
                    each.left = uicore.uilib.x - each._grab[0]
                    each.top = uicore.uilib.y - each._grab[1]
                else:
                    each.left = each.preDragAbs[0]
                    each.top = each.preDragAbs[1]

            self.SetOrder(0)
            self.FindWindowToStackTo()
            if shift:
                snapGrid = shiftGrid
                snapGroup = shiftDragWindows
                cursorRect = shiftRect
            elif ctrl:
                cursorRect = ctrlRect
                snapGrid = ctrlGrid
                snapGroup = ctrlDragWindows
            else:
                snapGrid = myGrid
                snapGroup = [self]
                cursorRect = myRect
            uicore.uilib.ClipCursor(*cursorRect)
            self.ShowSnapEdges_Moving(snapGroup, snapGrid, snapIndicator=snapIndicator)
            self.OnDragTick()
            blue.pyos.synchro.Yield()

        if self.sr.stack is None and self.StackingActive():
            trystackto = self.FindWindowToStackTo()
            self.ClearStackIndication()
            if trystackto:
                if trystackto.sr.stack:
                    trystackto.sr.stack.CheckStack(self)
                else:
                    trystackto.CheckStack(self)
        uicore.uilib.UnclipCursor()
        if self.destroyed:
            return 
        if self.sr.stack is None and snapGrid and snapGroup:
            self.ShowSnapEdges_Moving(snapGroup, snapGrid, doSnap=True)
        self.CleanupParent('snapIndicator')
        self.ClearStackIndication()
        if self.sr.stack is not None:
            self.state = uiconst.UI_PICKCHILDREN
        else:
            self.state = uiconst.UI_NORMAL
        if not self.destroyed:
            self._draginited = 0



    def GetOtherWindows(self, useMe = False, checkAlign = False):
        validWnds = []
        if self.parent:
            for wnd in self.parent.children:
                if checkAlign and wnd.GetAlign() != uiconst.RELATIVE:
                    continue
                if wnd == self and useMe:
                    validWnds.append(wnd)
                    continue
                if not isinstance(wnd, uicls.WindowCore) or wnd == self or wnd.state == uiconst.UI_HIDDEN:
                    continue
                validWnds.append(wnd)

        return validWnds



    def Debug_ShowSnapGrid(self, grid):
        self.CleanupParent('axeindicator')
        if grid and self.parent:
            (hAxes, vAxes,) = grid
            (pl, pt, pw, ph,) = self.parent.GetAbsolute()
            for y in hAxes:
                uicls.Fill(parent=self.parent, name='axeindicator', pos=(0,
                 y,
                 pw,
                 1), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=(0.0, 1.0, 0.0, 1.0))

            for x in vAxes:
                uicls.Fill(parent=self.parent, name='axeindicator', pos=(x,
                 0,
                 1,
                 ph), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=(0.0, 1.0, 0.0, 1.0))




    def Debug_UpdateMinMaxScalingRect(self, minMax):
        scalingRect = uiutil.FindChild(self.parent, 'scalingRect')
        if scalingRect is None:
            scalingRect = uicls.Frame(parent=self.parent, color=(0.0, 0.0, 1.0, 1.0), align=uiconst.TOPLEFT, name='scalingRect')
        if minMax is None:
            scalingRect.state = uiconst.UI_HIDDEN
            return 
        (l, t, r, b,) = minMax
        scalingRect.left = l
        scalingRect.top = t
        scalingRect.width = r - l
        scalingRect.height = b - t
        scalingRect.state = uiconst.UI_DISABLED
        scalingRect.SetOrder(0)



    def CreateSnapGrid(self, shiftGroup = None, ctrlGroup = None):
        allWnds = self.GetOtherWindows()
        desk = uicore.desktop
        hAxes = [0,
         desk.height,
         16,
         desk.height - 16]
        vAxes = [0, desk.width, desk.width - 16]
        hAxesWithOutMe = hAxes[:]
        vAxesWithOutMe = vAxes[:]
        hAxesWithOutShiftGroup = hAxes[:]
        vAxesWithOutShiftGroup = vAxes[:]
        hAxesWithOutCtrlGroup = hAxes[:]
        vAxesWithOutCtrlGroup = vAxes[:]
        hLists = [hAxes,
         hAxesWithOutMe,
         hAxesWithOutShiftGroup,
         hAxesWithOutCtrlGroup]
        vLists = [vAxes,
         vAxesWithOutMe,
         vAxesWithOutShiftGroup,
         vAxesWithOutCtrlGroup]
        for wnd in allWnds:
            (l, t, w, h,) = wnd.GetAbsolute()
            self.AddtoAxeList(wnd, vLists, l, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, vLists, l + w, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t + h, shiftGroup, ctrlGroup)

        self.snapGrid = [(hAxes, vAxes),
         (hAxesWithOutMe, vAxesWithOutMe),
         (hAxesWithOutShiftGroup, vAxesWithOutShiftGroup),
         (hAxesWithOutCtrlGroup, vAxesWithOutCtrlGroup)]
        return self.snapGrid



    def AddtoAxeList(self, wnd, lists, val, shiftgroup, ctrlgroup):
        (all, minusMe, minusShiftGroup, minusCtrlGroup,) = lists
        if val not in all:
            all.append(val)
        if wnd != self and val not in minusMe:
            minusMe.append(val)
        if shiftgroup and wnd not in shiftgroup and val not in minusShiftGroup:
            minusShiftGroup.append(val)
        if ctrlgroup and wnd not in ctrlgroup and val not in minusCtrlGroup:
            minusCtrlGroup.append(val)



    def AttachWindow(self, wnd, side, chain = 1, chainOrder = None):
        alignedWindows = self.FindConnectingWindows(self, side)
        removeFrom = None
        if wnd in alignedWindows:
            removeFrom = alignedWindows
        elif side in ('top', 'bottom'):
            removeFrom = self.FindConnectingWindows(self, 'top') + self.FindConnectingWindows(self, 'bottom')
        elif side in ('left', 'right'):
            removeFrom = self.FindConnectingWindows(self, 'left') + self.FindConnectingWindows(self, 'right')

        def FilterWnds(wnds, side):
            valid = []
            done = []
            for w in wnds:
                if w not in done:
                    if side in ('top', 'bottom'):
                        valid.append((w.top, w))
                    else:
                        valid.append((w.left, w))
                    done.append(w)

            return uiutil.SortListOfTuples(valid)


        removeFrom = FilterWnds(removeFrom, side)
        (pgl, pgt, pgw, pgh,) = self.GetGroupAbsolute(removeFrom)
        if removeFrom and wnd in removeFrom:
            idx = removeFrom.index(wnd)
            for awnd in removeFrom[(idx + 1):]:
                if side in ('bottom', 'top'):
                    awnd.top -= wnd.height
                if side in ('left', 'right'):
                    awnd.left -= wnd.width

            wnd.state = uiconst.UI_HIDDEN
            alignedWindows = self.FindConnectingWindows(self, side)
        wnd.state = uiconst.UI_NORMAL
        if chain:
            attachTo = alignedWindows[-1]
        else:
            attachTo = alignedWindows[0]
            if attachTo != self:
                return 
        if side == 'bottom':
            wnd.left = attachTo.left
            wnd.top = attachTo.top + attachTo.height
        elif side == 'left':
            wnd.left = attachTo.left - attachTo.width
            wnd.top = attachTo.top
        elif side == 'right':
            wnd.left = attachTo.left + attachTo.width
            wnd.top = attachTo.top
        elif side == 'top':
            wnd.left = attachTo.left
            wnd.top = attachTo.top - wnd.height
        if not chain:
            for awnd in alignedWindows[1:]:
                if awnd == wnd:
                    continue
                if side == 'bottom':
                    awnd.top += wnd.height
                elif side == 'left':
                    awnd.left -= wnd.width
                elif side == 'right':
                    awnd.left += wnd.width
                elif side == 'top':
                    awnd.top -= wnd.height

        if side in ('top', 'bottom'):
            alignedWindows = self.FindConnectingWindows(self, 'top') + self.FindConnectingWindows(self, 'bottom')
        elif side in ('left', 'right'):
            alignedWindows = self.FindConnectingWindows(self, 'left') + self.FindConnectingWindows(self, 'right')
        (gl, gt, gw, gh,) = self.GetGroupAbsolute(alignedWindows)
        diffY = 0
        diffX = 0
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        if gt < 0:
            diffY = abs(gt)
        elif gt + gh > ph:
            diffY = ph - (gt + gh)
        if gl < 0:
            diffX = abs(gl)
        elif gl + gw > pw:
            diffX = pw - (gl + gw)
        done = []
        for wnd in alignedWindows:
            if wnd in done:
                continue
            wnd.top += diffY
            wnd.left += diffX
            done.append(wnd)




    def ShowSnapEdges_Scaling(self, snapGrid, showSnap = True, doSnap = False):
        (horizontal, vertical,) = snapGrid
        snapdist = settings.user.windows.Get('snapdistance', 12)
        if not snapdist:
            self.HideSnapIndicator()
            return 
        match = {}
        for side in self.scaleSides:
            wnd = self
            minLDist = 1000
            minRDist = 1000
            minTDist = 1000
            minBDist = 1000
            (wl, wt, ww, wh,) = wnd.GetAbsolute()
            if showSnap:
                snapIndicator = wnd.GetSnapIndicator()
                snapIndicator.left = wl
                snapIndicator.top = wt
                snapIndicator.width = ww
                snapIndicator.height = wh
                for each in snapIndicator.children:
                    each.state = uiconst.UI_HIDDEN

            else:
                wnd.HideSnapIndicator()
            if side in ('top', 'bottom'):
                for hAxe in horizontal:
                    tDist = abs(hAxe - wt)
                    bDist = abs(hAxe - (wt + wh))
                    if side == 'top' and tDist <= snapdist and tDist < minTDist:
                        minTDist = tDist
                        match[(side, wnd)] = hAxe
                    elif side == 'bottom' and bDist <= snapdist and bDist < minBDist:
                        minBDist = bDist
                        match[(side, wnd)] = hAxe

            elif side in ('left', 'right'):
                for vAxe in vertical:
                    lDist = abs(vAxe - wl)
                    rDist = abs(vAxe - (wl + ww))
                    if side == 'left' and lDist <= snapdist and lDist < minLDist:
                        minLDist = lDist
                        match[(side, wnd)] = vAxe
                    elif side == 'right' and rDist <= snapdist and rDist < minRDist:
                        minRDist = rDist
                        match[(side, wnd)] = vAxe


        if showSnap or doSnap:
            checkMultipleSideSnap = {}
            for (side, wnd,) in match.iterkeys():
                if wnd not in checkMultipleSideSnap:
                    checkMultipleSideSnap[wnd] = []
                snapValue = match[(side, wnd)]
                (wl, wt, ww, wh,) = wnd.GetAbsolute()
                minH = wnd.GetMinHeight()
                snapIndicator = wnd.GetSnapIndicator()
                snapIndicator.state = uiconst.UI_DISABLED
                snapIndicator.SetOrder(1)
                if side == 'left':
                    if doSnap:
                        wnd.left = snapValue
                        if wnd.IsResizeable():
                            wnd.width = wl - snapValue + ww
                    if showSnap:
                        snapIndicator.left = snapValue - 2
                        snapIndicator.width = wl - snapValue + ww + 4
                        uiutil.GetChild(snapIndicator, 'sLeft').state = uiconst.UI_DISABLED
                if side == 'right':
                    if doSnap:
                        if wnd.IsResizeable():
                            wnd.width = snapValue - wl
                    if showSnap:
                        snapIndicator.width = snapValue - wl + 4
                        uiutil.GetChild(snapIndicator, 'sRight').state = uiconst.UI_DISABLED
                if side == 'top':
                    if doSnap:
                        wnd.top = snapValue
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or max(minH, wt - snapValue + wh)
                    if showSnap:
                        snapIndicator.top = snapValue - 2
                        snapIndicator.height = wt - snapValue + wh + 4
                        uiutil.GetChild(snapIndicator, 'sTop').state = uiconst.UI_DISABLED
                if side == 'bottom':
                    if doSnap:
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or max(minH, snapValue - wt)
                    if showSnap:
                        snapIndicator.height = snapValue - wt + 4
                        uiutil.GetChild(snapIndicator, 'sBottom').state = uiconst.UI_DISABLED
                checkMultipleSideSnap[wnd].append(side)




    def SetActive(self, *args):
        self.OnSetActive_(self)



    def HideSnapIndicator(self):
        snapIndicator = uiutil.FindChild(self.parent, 'snapIndicator')
        if snapIndicator is not None:
            snapIndicator.Close()



    def GetSnapIndicator(self):
        snapIndicator = uiutil.FindChild(self.parent, 'snapIndicator')
        if snapIndicator is None:
            snapIndicator = uicls.Container(parent=self.parent, color=(0.0, 1.0, 0.0, 1.0), align=uiconst.TOPLEFT, name='snapIndicator')
            for (label, align, icon,) in [('sLeftTop', uiconst.TOPLEFT, 'ui_1_16_1'),
             ('sRightTop', uiconst.TOPRIGHT, 'ui_1_16_3'),
             ('sRightBottom', uiconst.BOTTOMRIGHT, 'ui_1_16_35'),
             ('sLeftBottom', uiconst.BOTTOMLEFT, 'ui_1_16_33'),
             ('sLeft', uiconst.CENTERLEFT, 'ui_1_16_17'),
             ('sTop', uiconst.CENTERTOP, 'ui_1_16_2'),
             ('sRight', uiconst.CENTERRIGHT, 'ui_1_16_19'),
             ('sBottom', uiconst.CENTERBOTTOM, 'ui_1_16_34')]:
                indicator = uicls.Icon(parent=snapIndicator, name=label, align=align, state=uiconst.UI_HIDDEN, icon=icon)

        return snapIndicator



    def IndicateScaleSnap(self, wnd, side, offsetX = 0, offsetY = 0):
        indicator = uiutil.FindChild(wnd, side)
        if indicator:
            indicator.children[0].state = uiconst.UI_DISABLED
            indicator.children[0].left = offsetX
            indicator.children[0].top = offsetY



    def IndicateStackable(self, over):
        if not over or not self.IsStackable():
            if self.sr.stackIndicator:
                (s1, s2,) = self.sr.stackIndicator
                s1.Close()
                s2.Close()
                self.sr.stackIndicator = None
            return 
        if not self.sr.stackIndicator:
            s1 = uicls.Fill(parent=self, color=(0.0, 0.0, 0.0, 1.0), height=6, width=0, align=uiconst.TOPLEFT, idx=0)
            s2 = uicls.Fill(parent=self.parent, color=(0.0, 0.0, 0.0, 1.0), height=6, width=0, align=uiconst.ABSOLUTE, idx=1)
            self.sr.stackIndicator = (s1, s2)
        (s1, s2,) = self.sr.stackIndicator
        (l, t, w, h,) = self.GetAbsolute()
        s1.width = w
        if isinstance(self, self.GetStackClass()):
            s1.top = 18
        else:
            s1.top = 0
        (ol, ot, ow, oh,) = over.GetAbsolute()
        s2.left = ol
        s2.width = ow
        if isinstance(over, self.GetStackClass()):
            s2.top = ot + 18
        else:
            s2.top = ot



    def ClearStackIndication(self):
        self.IndicateStackable(None)



    def ShowSnapEdges_Moving(self, snapGroup, snapGrid, snapIndicator = None, doSnap = False):
        if snapGrid is None:
            return 
        (l, t, w, h,) = (gl, gt, gw, gh,) = self.GetGroupAbsolute(snapGroup)
        snapdist = settings.user.windows.Get('snapdistance', 12)
        if not snapdist:
            self.HideSnapIndicator()
            return 
        lSnap = None
        rSnap = None
        tSnap = None
        bSnap = None
        minLDist = 1000
        minRDist = 1000
        minTDist = 1000
        minBDist = 1000
        (horizontal, vertical,) = snapGrid
        for hAxe in horizontal:
            tDist = abs(hAxe - t)
            bDist = abs(hAxe - (t + h))
            if tDist <= snapdist and tDist < minTDist:
                tSnap = hAxe
                minTDist = tDist
            elif bDist <= snapdist and bDist < minBDist:
                bSnap = hAxe
                minBDist = bDist

        for vAxe in vertical:
            lDist = abs(vAxe - l)
            rDist = abs(vAxe - (l + w))
            if lDist <= snapdist and lDist < minLDist:
                lSnap = vAxe
                minLDist = lDist
            elif rDist <= snapdist and rDist < minRDist:
                rSnap = vAxe
                minRDist = rDist

        if tSnap is not None:
            t = tSnap
            if bSnap is not None:
                h = bSnap - tSnap
        elif bSnap is not None:
            t = bSnap - h
        if lSnap is not None:
            l = lSnap
            if rSnap is not None:
                w = rSnap - lSnap
        elif rSnap is not None:
            l = rSnap - w
        if snapIndicator and not snapIndicator.destroyed:
            snapIndicator.width = w + 6
            snapIndicator.height = h + 6
            snapIndicator.left = l - 2
            snapIndicator.top = t - 2
            for each in snapIndicator.children:
                each.state = uiconst.UI_HIDDEN

            snapIndicator.SetOrder(1)
            if lSnap is not None:
                uiutil.GetChild(snapIndicator, 'sLeft').state = uiconst.UI_DISABLED
            if rSnap is not None:
                uiutil.GetChild(snapIndicator, 'sRight').state = uiconst.UI_DISABLED
            if tSnap is not None:
                uiutil.GetChild(snapIndicator, 'sTop').state = uiconst.UI_DISABLED
            if bSnap is not None:
                uiutil.GetChild(snapIndicator, 'sBottom').state = uiconst.UI_DISABLED
            snapIndicator.state = uiconst.UI_DISABLED
        if doSnap:
            scaleX = float(w) / gw
            scaleY = float(h) / gh
            diffX = l - gl
            diffY = t - gt
            for wnd in snapGroup:
                wnd.left += diffX
                wnd.top += diffY
                if wnd.IsResizeable():
                    wnd.width = int(wnd.width * scaleX)
                    wnd.height = int(wnd.height * scaleY)

            for wnd in snapGroup:
                if wnd._fixedHeight and wnd.height != wnd._fixedHeight:
                    diff = wnd.height - wnd._fixedHeight
                    bottomAlignedWindows = self.FindConnectingWindows(wnd, 'bottom')
                    wnd.height -= diff
                    for each in bottomAlignedWindows[1:]:
                        each.top -= diff

                if wnd._fixedWidth and wnd.width != wnd._fixedWidth:
                    diff = wnd.width - wnd._fixedWidth
                    rightAlignedWindows = self.FindConnectingWindows(wnd, 'right')
                    wnd.width -= diff
                    for each in rightAlignedWindows[1:]:
                        each.left -= diff





    def FindWindowsImAlignedTo(self, side = None):
        validWnds = self.GetOtherWindows()
        (l, t, w, h,) = self.GetAbsolute()
        if side:
            wnds = []
            for wnd in validWnds:
                (wl, wt, ww, wh,) = wnd.GetAbsolute()
                if side == 'left':
                    if wl == l:
                        wnds.append((wnd, 'left'))
                    elif wl + ww == l:
                        wnds.append((wnd, 'right'))
                elif side == 'right':
                    if wl + ww == l + w:
                        wnds.append((wnd, 'right'))
                    elif wl == l + w:
                        wnds.append((wnd, 'left'))

            return wnds
        wnds = []
        myCorners = [(l, t),
         (l + w, t),
         (l, t + h),
         (l + w, t + h)]
        for wnd in validWnds:
            (wl, wt, ww, wh,) = wnd.GetAbsolute()
            wndCorners = ((wl, wt),
             (wl + ww, wt),
             (wl, wt + wh),
             (wl + ww, wt + wh))
            for c in wndCorners:
                if c in myCorners:
                    if wnd not in wnds:
                        wnds.append(wnd)
                    for c2 in wndCorners:
                        if c2 not in myCorners:
                            myCorners.append(c2)

                    break


        return wnds



    def FindWindowToStackTo(self):
        over = uicore.uilib.mouseOver
        if over is self:
            return None
        over = uiutil.GetWindowAbove(over)
        if not isinstance(over, uicls.WindowCore) or not over.StackingActive():
            self.ClearStackIndication()
            return None
        if over.sr.stack:
            over = over.sr.stack
        (l, t, w, h,) = over.GetAbsolute()
        (sl, st, sw, sh,) = self.GetAbsolute()
        isStack = isinstance(over, self.GetStackClass())
        pickSize = 32
        if isStack:
            pickSize += 18
        if (l < sl < l + w or l < sl + sw < l + w) and t <= st <= t + pickSize:
            self.IndicateStackable(over)
            return over
        self.ClearStackIndication()



    def StackingActive(self):
        if getattr(self, '_stackable', 1) and not self.IsLocked():
            shiftonly = settings.user.ui.Get('stackwndsonshift', 0)
            if shiftonly:
                return uicore.uilib.Key(uiconst.VK_SHIFT)
            return 1
        return 0


    IsStackable = StackingActive

    def OnMouseUp(self, *args):
        self.ClearStackIndication()
        self.CleanupParent('snapIndicator')
        uicore.uilib.UnclipCursor()
        self._dragging = 0
        self._draginited = 0
        self.RegisterPositionAndSize()
        self.CheckCorners()



    def OnDblClick(self, *args):
        if getattr(self, 'isDialog', False):
            return 
        self.ToggleCollapse()



    def ToggleCollapse(self):
        if not self._collapseable:
            return 
        self.ResetToggleState()
        if self.IsCollapsed():
            self.Expand()
        else:
            self.Collapse()



    def ResetToggleState(self):
        uicore.toggleState = None



    def GetCollapsedHeight(self):
        if self.sr.headerParent:
            return self.sr.headerParent.height
        return 18



    def GetHeaderHeight(self):
        if self.sr.headerParent:
            return self.sr.headerParent.height
        return 0



    def Collapse(self, forceCollapse = False, checkchain = 1, *args):
        if not self.parent or not self._collapseable or not forceCollapse and self.IsCollapsed():
            return 
        if self.sr.stack:
            return self.sr.stack.Collapse(forceCollapse, checkchain, *args)
        bottomAlignedWindows = self.FindConnectingWindows(self, 'bottom')
        allAlignedWindows = self.FindConnectingWindows(self)
        (gl, gt, gw, gh,) = self.GetGroupAbsolute(allAlignedWindows)
        ch = self.GetCollapsedHeight()
        heightDiff = self.height - ch
        self._SetCollapsed(True)
        self._LockHeight(ch)
        alignedToBottom = False
        alignedToTop = False
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        if gt in (0, 16):
            alignedToTop = True
        elif gt + gh in (ph, ph - 16):
            alignedToBottom = True
        if alignedToBottom:
            topAlignedWindows = self.FindConnectingWindows(self, 'top')
            for wnd in topAlignedWindows:
                wnd.top += heightDiff

        else:
            for wnd in bottomAlignedWindows:
                if wnd == self:
                    continue
                wnd.top -= heightDiff

        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if checkchain and (shift or ctrl):
            if shift:
                affected = self.FindConnectingWindows(self)
            elif ctrl:
                affected = bottomAlignedWindows
            for each in affected:
                if each != self:
                    each.Collapse(checkchain=0)

        if self.sr.headerLine:
            self.sr.headerLine.state = uiconst.UI_HIDDEN
        if self.sr.buttonParent:
            self.sr.buttonParent.state = uiconst.UI_HIDDEN
        self.sr.content.state = uiconst.UI_HIDDEN
        self.ShowHeaderButtons(1)
        self.OnCollapsed(self)



    def HideButtons(self):
        if self.sr.buttonParent:
            self.sr.buttonParent.Hide()



    def ShowButtons(self):
        if self.sr.buttonParent:
            self.sr.buttonParent.Show()



    def Expand(self, checkchain = 1, *args):
        if not self.parent:
            return 
        if self.sr.stack:
            return self.sr.stack.Expand(checkchain, *args)
        self.UnlockHeight()
        bottomAlignedWindows = self.FindConnectingWindows(self, 'bottom')
        (gl, gt, gw, gh,) = self.GetGroupAbsolute(bottomAlignedWindows)
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        alignedToBottom = False
        if gt + gh in (ph, ph - 16):
            alignedToBottom = True
        (left, top, width, height, dw, dh,) = self.GetRegisteredPositionAndSize()
        _h = height
        height = max(height, self.GetMinHeight())
        heightDiff = height - self.height
        self._SetCollapsed(False)
        self.height = height
        if alignedToBottom:
            topAlignedWindows = self.FindConnectingWindows(self, 'top')
            for wnd in topAlignedWindows:
                wnd.top -= heightDiff

        else:
            overshot = 0
            for wnd in bottomAlignedWindows:
                if wnd == self:
                    continue
                wnd.top += heightDiff
                if wnd.top + wnd.height > uicore.desktop.height:
                    overshot = wnd.top + wnd.height - uicore.desktop.height

            if overshot:
                myMinH = self.GetMinHeight()
                shrinkTo = max(myMinH, self.height - overshot)
                diff = self.height - shrinkTo
                self.height = shrinkTo
                for wnd in bottomAlignedWindows:
                    if wnd == self:
                        continue
                    wnd.top -= diff

        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if checkchain and (shift or ctrl):
            if shift:
                affected = self.FindConnectingWindows(self)
            elif ctrl:
                affected = bottomAlignedWindows
            for each in affected:
                if each != self:
                    each.Expand(0)

        if self.sr.headerLine:
            self.sr.headerLine.state = uiconst.UI_DISABLED
        if self.sr.buttonParent:
            self.sr.buttonParent.state = uiconst.UI_PICKCHILDREN
        self.sr.content.state = uiconst.UI_PICKCHILDREN
        self.ShowHeaderButtons(1)
        self.OnExpanded(self)
        self.ValidateWindows()



    def ValidateWindows(self):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(getModals=1, floatingOnly=True)
        for wnd in all:
            if wnd.GetAlign() != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))




    def CheckStack(self, drop):
        if not self.StackingActive():
            return 
        if self.sr.modalParent is not None or drop.sr.modalParent is not None or drop == self:
            return 
        if isinstance(self, uicls.WindowStack):
            if not isinstance(drop, uicls.WindowStack):
                self.InsertWnd(drop, 0, 1)
            else:
                for wnd in drop.sr.content.children[:]:
                    self.InsertWnd(wnd, 0, 1)

                drop.SelfDestruct()
            return 
        if self.state != uiconst.UI_HIDDEN:
            wnds = [(self, 0)]
            location = None
            kill = []
            if isinstance(drop, uicls.WindowStack):
                for wnd in drop.sr.content.children:
                    wnds.append((wnd, wnd.state == uiconst.UI_NORMAL))

                kill.append(drop)
            else:
                wnds.append((drop, 1))
            self.Stack(wnds, kill)



    def CheckWndPos(self, i = 0):
        if self.parent is None or self.parent.destroyed or i == 10:
            return 
        for each in self.parent.children:
            if each != self and each.state == uiconst.UI_NORMAL:
                if each.left == self.left and each.top == self.top:
                    self.left = self.left + POSOVERLAPSHIFT
                    self.top = self.top + POSOVERLAPSHIFT
                    if self.left + self.width > uicore.desktop.width:
                        self.left = uicore.desktop.width - self.width
                    if self.top + self.height > uicore.desktop.height:
                        self.top = uicore.desktop.height - self.height
                    self.CheckWndPos(i + 1)
                    break




    def Stack(self, wnds, kill, group = None, groupidx = None):
        stack = uicore.registry.GetStack(str(uthread.uniqueId()), self.GetStackClass())
        for _wnd in wnds:
            (wnd, show,) = _wnd
            stack.InsertWnd(wnd, 1, show)
            stack.stack_starting = 0

        for each in kill:
            if each is not None and not each.destroyed:
                each.Close()




    def SetHeight(self, height):
        if self.GetAlign() == uiconst.RELATIVE and height != self.height:
            (pl, pt, pw, ph,) = self.parent.GetAbsolute()
            height = max(self.GetMinHeight(), height)
            diff = self.height - height
            if self.top + self.height in (ph, ph - 16):
                wnds = self.FindConnectingWindows(self, 'top')
                if len(wnds) > 1:
                    for wnd in wnds[1:]:
                        wnd.top += diff

                self.top += diff
            else:
                wnds = self.FindConnectingWindows(self, 'bottom')
                (bl, bt, br, bb,) = self.GetGroupRect(wnds)
                if bb < ph:
                    maxDiff = min(ph - bb, diff)
                    if len(wnds) > 1:
                        for wnd in wnds[1:]:
                            wnd.top -= maxDiff

            self.height = height



    def GetMinWidth(self):
        if self._fixedWidth:
            return min(self._fixedWidth, self.minsize[0])
        (w, h,) = self.GetMinSize()
        return max(w, self.minsize[0])



    def GetMinHeight(self):
        if self._fixedHeight:
            return min(self._fixedHeight, self.minsize[1])
        (w, h,) = self.GetMinSize()
        return max(h, self.minsize[1])



    def GetMaxWidth(self):
        if self._fixedWidth:
            return self._fixedWidth
        return self.maxsize[0] or sys.maxint



    def GetMaxHeight(self):
        if self._fixedHeight:
            return self._fixedHeight
        return self.maxsize[1] or sys.maxint



    def SortScaleWindows(self, sides):
        wnds = []
        for side in sides:
            wnds += self.FindConnectingWindows(self, side, getParallelSides=1)

        self.PrepareWindowsForMove(wnds)
        (ml, mt, mw, mh,) = self.GetAbsolute()
        scaleWidthMeH = []
        scaleWidthMeV = []
        onLeft = []
        onRight = []
        onBottom = []
        onTop = []
        all = [self]
        scaleAbove = []
        for wnd in wnds:
            if wnd == self or wnd in all:
                continue
            (l, t, w, h,) = wnd.GetAbsolute()
            if l == ml and w == mw:
                scaleWidthMeH.append(wnd)
            elif l >= ml + mw:
                onRight.append(wnd)
            elif l + w <= ml:
                onLeft.append(wnd)
            elif 'right' in sides:
                onRight.append(wnd)
            elif 'left' in sides:
                onLeft.append(wnd)
            if t == mt and h == mh:
                scaleWidthMeV.append(wnd)
            elif t >= mt + mh:
                onBottom.append(wnd)
            elif t + h == mt and 'top' in sides:
                scaleAbove.append(wnd)
            elif t == mt and 'top' in sides:
                onTop.append(wnd)
            all.append(wnd)

        return (scaleWidthMeH,
         scaleWidthMeV,
         scaleAbove,
         onLeft,
         onRight,
         onTop,
         onBottom,
         all)



    def GetClipRectModify(self, sides):
        (l, t, w, h,) = self.GetAbsolute()
        mx = uicore.uilib.x
        my = uicore.uilib.y
        (rl, rt, rr, rb,) = (0, 0, 0, 0)
        if 'right' in sides:
            rl = l + w - mx
        if 'left' in sides:
            rr = l - mx
        if 'bottom' in sides:
            rt = t + h - my
        if 'top' in sides:
            rb = t - my
        return (rl,
         rt,
         rr,
         rb)



    def CornersToSide(self, cs):
        sNames = ['left',
         'right',
         'top',
         'bottom']
        cMap = [(3, 2),
         (0, 1),
         (1, 0),
         (2, 3),
         (0, 3),
         (1, 2),
         (2, 1),
         (3, 0)]
        if cs in cMap:
            return sNames[(cMap.index(cs) // 2)]



    def FindConnectingWindows(self, fromWnd, fromSide = None, wnds = None, validWnds = None, getParallelSides = 0, fullSideOnly = 0):
        if validWnds is None:
            validWnds = self.GetOtherWindows(useMe=True, checkAlign=True)
        (l, t, w, h,) = fromWnd.GetAbsolute()
        fromWndCorners = [(l, t),
         (l + w, t),
         (l + w, t + h),
         (l, t + h)]
        if fromSide == 'left':
            validCornerPairs = [(3, 2), (0, 1)]
            if getParallelSides:
                validCornerPairs += [(3, 0), (0, 3)]
        elif fromSide == 'right':
            validCornerPairs = [(1, 0), (2, 3)]
            if getParallelSides:
                validCornerPairs += [(1, 2), (2, 1)]
        elif fromSide == 'top':
            validCornerPairs = [(0, 3), (1, 2)]
            if getParallelSides:
                validCornerPairs += [(0, 1), (1, 0)]
        elif fromSide == 'bottom':
            validCornerPairs = [(2, 1), (3, 0)]
            if getParallelSides:
                validCornerPairs += [(3, 2), (2, 3)]
        else:
            validCornerPairs = [(3, 2),
             (0, 1),
             (1, 0),
             (2, 3),
             (0, 3),
             (1, 2),
             (2, 1),
             (3, 0)]
        wnds = wnds or []
        if fromWnd not in wnds:
            wnds.append(fromWnd)
        for wnd in validWnds:
            if wnd in wnds:
                continue
            (wl, wt, ww, wh,) = wnd.GetAbsolute()
            wndCorners = ((wl, wt),
             (wl + ww, wt),
             (wl + ww, wt + wh),
             (wl, wt + wh))
            m = 0
            for (c1, c2,) in validCornerPairs:
                c1Pos = fromWndCorners[c1]
                c2Pos = wndCorners[c2]
                if c1Pos == c2Pos:
                    if not fullSideOnly or m == 1:
                        if getParallelSides:
                            self.FindConnectingWindows(wnd, None, wnds, validWnds, getParallelSides, fullSideOnly)
                        else:
                            self.FindConnectingWindows(wnd, fromSide, wnds, validWnds, getParallelSides, fullSideOnly)
                        break
                    m += 1


        return wnds



    def PrepareWindowsForMove(self, wnds):
        for each in wnds:
            (l, t, w, h,) = each.GetAbsolute()
            each._grab = [uicore.uilib.x - l, uicore.uilib.y - t]
            each.preDragAbs = each.GetAbsolute()
            each.preDragCursorPos = (uicore.uilib.x, uicore.uilib.y)
            each.SetOrder(0)




    def CleanupParent(self, what):
        for each in self.parent.children[:]:
            if each.name == what:
                each.Close()




    def FindMinMaxScaling(self, sides):
        (scaleH, scaleV, scaleAbove, followL, followR, followT, followB, all,) = self.sortedScaleWindows
        (pl, pt, pw, ph,) = self.parent.GetAbsolute()
        myMinX = minX = 0
        myMaxX = maxX = pw
        myMinY = minY = 0
        myMaxY = maxY = ph
        for wnd in scaleH + [self]:
            (spdl, spdt, spdw, spdh,) = wnd.preDragAbs
            wndMinWidth = wnd.GetMinWidth()
            wndMaxWidth = wnd.GetMaxWidth()
            if 'left' in sides:
                minX = max(minX, spdl + spdw - wndMaxWidth)
                maxX = min(maxX, spdl + spdw - wndMinWidth)
            elif 'right' in sides:
                minX = max(minX, spdl + wndMinWidth)
                maxX = min(maxX, spdl + wndMaxWidth)

        for wnd in scaleV + [self]:
            (spdl, spdt, spdw, spdh,) = wnd.preDragAbs
            wndMinHeight = wnd.GetMinHeight()
            wndMaxHeight = wnd.GetMaxHeight()
            if 'top' in sides:
                minY = max(minY, spdt + spdh - wndMaxHeight)
                maxY = min(maxY, spdt + spdh - wndMinHeight)
            elif 'bottom' in sides:
                minY = max(minY, spdt + wndMinHeight)
                maxY = min(maxY, spdt + wndMaxHeight)

        for wnd in scaleAbove:
            (spdl, spdt, spdw, spdh,) = wnd.preDragAbs
            wndMinHeight = wnd.GetMinHeight()
            wndMaxHeight = wnd.GetMaxHeight()
            minY = max(minY, spdt + wndMinHeight)
            maxY = min(maxY, spdt + wndMaxHeight)

        (spdl, spdt, spdw, spdh,) = self.preDragAbs
        myMinWidth = self.GetMinWidth()
        myMinHeight = self.GetMinHeight()
        myMaxWidth = self.GetMaxWidth()
        myMaxHeight = self.GetMaxHeight()
        (mx, my,) = self.preDragCursorPos
        if 'top' in sides:
            myMaxY = min(myMaxY, spdt + spdh - myMinHeight)
            myMinY = max(myMinY, spdt + spdh - myMaxHeight)
            for wnd in followT:
                (pdl, pdt, pdw, pdh,) = wnd.preDragAbs
                minY = max(minY, spdt - pdt)

        elif 'bottom' in sides:
            myMinY = max(myMinY, spdt + myMinHeight)
            myMaxY = min(myMaxY, spdt + myMaxHeight)
            for wnd in followB:
                (pdl, pdt, pdw, pdh,) = wnd.preDragAbs
                maxY = min(maxY, spdt + spdh + (ph - (pdt + pdh)))

        if 'left' in sides:
            myMaxX = min(myMaxX, spdl + spdw - myMinWidth)
            myMinX = max(myMinX, spdl + spdw - myMaxWidth)
            for wnd in followL:
                (pdl, pdt, pdw, pdh,) = wnd.preDragAbs
                minX = max(minX, spdl - pdl)

        elif 'right' in sides:
            myMinX = max(myMinX, spdl + myMinWidth)
            myMaxX = min(myMaxX, spdl + myMaxWidth)
            for wnd in followR:
                (pdl, pdt, pdw, pdh,) = wnd.preDragAbs
                maxX = min(maxX, spdl + spdw + (pw - (pdl + pdw)))

        return ((minX,
          minY,
          maxX,
          maxY), (myMinX,
          myMinY,
          myMaxX,
          myMaxY))



    def ModifyRect(self, sides):
        (l, t, w, h,) = self.GetAbsolute()
        mx = uicore.uilib.x
        my = uicore.uilib.y
        (rl, rt, rr, rb,) = (0, 0, 0, 0)
        rh = rv = 0
        if 'right' in sides:
            rh = l + w - mx
        elif 'left' in sides:
            rh = l - mx
        if 'bottom' in sides:
            rv = t + h - my
        elif 'top' in sides:
            rv = t - my
        return (int(rh),
         int(rv),
         int(rh),
         int(rv))



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateClipCursor(self, rect, mrect):
        (ml, mt, mr, mb,) = mrect
        (rl, rt, rr, rb,) = rect
        uicore.uilib.ClipCursor(rl - ml, rt - mt, rr - mr, rb - mb)



    def GetSidesFromScalerName(self, sName):
        ret = []
        for s in ['Left',
         'Top',
         'Right',
         'Bottom']:
            if s in sName:
                ret.append(s.lower())

        return ret



    def StartScale(self, sender, btn, *args):
        if btn == uiconst.MOUSELEFT:
            self.scaleSides = self.GetSidesFromScalerName(sender.name)
            self.sortedScaleWindows = self.SortScaleWindows(self.scaleSides)
            self.minmaxScale = self.FindMinMaxScaling(self.scaleSides)
            self.CreateSnapGrid(self.sortedScaleWindows[-1])
            self.OnStartScale_(self)
            self._scaling = True
            uthread.new(self.OnScale, sender)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnScale(self, sender, *args):
        mRect = self.ModifyRect(self.scaleSides)
        while self._scaling and uicore.uilib.leftbtn and self and not self.destroyed:
            diffx = uicore.uilib.x - self.preDragCursorPos[0]
            diffy = uicore.uilib.y - self.preDragCursorPos[1]
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            (allMinMaxRect, myMinMaxRect,) = self.minmaxScale
            if shift:
                snapGrid = self.snapGrid[2]
                rect = allMinMaxRect
            else:
                snapGrid = self.snapGrid[1]
                rect = myMinMaxRect
            self.UpdateClipCursor(rect, mRect)
            if not shift:
                for wnd in self.sortedScaleWindows[-1]:
                    (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                    wnd.left = wpdl
                    wnd.top = wpdt
                    wnd.width = wpdw
                    wnd.height = wpdh

                (scaleH, scaleV, scaleAbove, followL, followR, followT, followB,) = ([],
                 [],
                 [],
                 [],
                 [],
                 [],
                 [])
            else:
                (scaleH, scaleV, scaleAbove, followL, followR, followT, followB, all,) = self.sortedScaleWindows
            for side in self.scaleSides:
                if side in ('left', 'right') and self.GetMinWidth() != self.GetMaxWidth():
                    for wnd in scaleH + [self]:
                        (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                        if side == 'left':
                            wnd.left = wpdl + diffx
                            if wnd.IsResizeable():
                                wnd.width = wnd._fixedWidth or wpdw - diffx
                        elif side == 'right':
                            if wnd.IsResizeable():
                                wnd.width = wnd._fixedWidth or wpdw + diffx

                    for wnd in [followR, followL][(side == 'left')]:
                        (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                        wnd.left = wpdl + diffx

                if side in ('top', 'bottom') and self.GetMinHeight() != self.GetMaxHeight():
                    for wnd in scaleV + [self]:
                        (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                        if side == 'top':
                            if wnd.IsResizeable():
                                wnd.height = wnd._fixedHeight or wpdh - diffy
                            wnd.top = wpdt + diffy
                        elif side == 'bottom':
                            if wnd.IsResizeable():
                                wnd.height = wnd._fixedHeight or wpdh + diffy

                    for wnd in [followB, followT][(side == 'top')]:
                        (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                        wnd.top = wpdt + diffy

                    for wnd in scaleAbove:
                        (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or wpdh + diffy


            self.ShowSnapEdges_Scaling(snapGrid)
            self.OnScale_(self)
            uicls.Area._OnResize(self)
            blue.pyos.synchro.Sleep(1)




    def AdjustScaleWindowsAfterSnapping(self):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not shift:
            return 
        (scaleH, scaleV, scaleAbove, followL, followR, followT, followB, all,) = self.sortedScaleWindows
        (spdl, spdt, spdw, spdh,) = self.preDragAbs
        (l, t, w, h,) = self.GetAbsolute()
        dl = l - spdl
        dt = t - spdt
        dw = w - spdw
        dh = h - spdh
        for wnd in scaleH:
            (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
            wnd.left = wpdl + dl
            if wnd.IsResizeable():
                wnd.width = wnd._fixedWidth or wpdw + dw

        if 'right' in self.scaleSides:
            for wnd in followR:
                (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                wnd.left = wpdl + dw

        elif 'left' in self.scaleSides:
            for wnd in followL:
                (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                wnd.left = wpdl + dl

        for wnd in scaleV:
            (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
            if wnd.IsResizeable():
                wnd.height = wnd._fixedHeight or wpdh + dh
            wnd.top = wpdt + dt

        if 'bottom' in self.scaleSides:
            for wnd in followB:
                (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                wnd.top = wpdt + dh

        elif 'top' in self.scaleSides:
            for wnd in followT:
                (wpdl, wpdt, wpdw, wpdh,) = wnd.preDragAbs
                wnd.top = wpdt + dt




    def EndScale(self, sender, *args):
        self.CleanupParent('snapIndicator')
        self._scaling = False
        uicore.uilib.UnclipCursor()
        if self.destroyed:
            return 
        if self.snapGrid:
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                snapGrid = self.snapGrid[2]
            else:
                snapGrid = self.snapGrid[1]
            self.ShowSnapEdges_Scaling(snapGrid, showSnap=False, doSnap=True)
            self.AdjustScaleWindowsAfterSnapping()
        self.RegisterPositionAndSize()
        self.CheckCorners()
        self.OnEndScale_(self)



    def GetBoundries(self, wnds):
        d = uicore.desktop
        (dw, dh,) = (d.width, d.height)
        (l, t, r, b,) = self.GetGroupRect(wnds)
        return (l,
         t,
         dw - r,
         dh - b)



    def GetGroupRect(self, group, getAbsolute = 0):
        if not len(group):
            return (0, 0, 0, 0)
        (l, t, w, h,) = group[0].GetAbsolute()
        r = l + w
        b = t + h
        for wnd in group[1:]:
            (wl, wt, ww, wh,) = wnd.GetAbsolute()
            l = min(l, wl)
            t = min(t, wt)
            r = max(r, wl + ww)
            b = max(b, wt + wh)

        if getAbsolute:
            return (l,
             t,
             r - l,
             b - t)
        return (l,
         t,
         r,
         b)



    def GetGroupAbsolute(self, group):
        return self.GetGroupRect(group, 1)



    def GetDefaultLeftOffset(self, *args, **kw):
        return 0



    def OnResize_(self, *args):
        pass



    def OnScale_(self, wnd, *args):
        pass



    def OnStartScale_(self, wnd, *args):
        pass



    def OnEndScale_(self, wnd, *args):
        pass



    def OnMouseDown_(self, what):
        pass



    def OnStartMinimize_(self, *args):
        pass



    def OnEndMinimize_(self, *args):
        pass



    def OnStartMaximize_(self, *args):
        pass



    def OnEndMaximize_(self, *args):
        pass



    def OnSetActive_(self, *args):
        pass



    def OnClose_(self, *args):
        pass



    def UpdateCaption_(self, *args):
        pass



    def OnDropData(self, *args, **kwds):
        pass



    def OnCollapsed(self, wnd, *args):
        pass



    def OnExpanded(self, wnd, *args):
        pass



    def OnDragTick(self, *args):
        pass


    l = locals()
    all = l.keys()
    all.sort()
    o = 'Overwriteables:\n'
    for each in all:
        if each.endswith('_') and not each.endswith('__'):
            o += each + '\n'

    __doc__ = o

exports = {'uicls.WindowCoreReady': True}

