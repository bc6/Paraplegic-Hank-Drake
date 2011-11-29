import uicls
import uiutil
import uiconst
import uthread

class GridCore(uicls.Container):
    __guid__ = 'uicls.GridCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        (xSlots, ySlots,) = attributes.get('gridSize', (1, 1))



    def _OnResize(self, *args):
        uicls.Container._OnResize(self, *args)



    def UpdateSlots(self):
        pass




class FlipMenuCore(uicls.Container):
    __guid__ = 'uicls.FlipMenuCore'
    default_state = uiconst.UI_NORMAL
    MAXPAGES = 6
    DOTPARENTSIZE = 10

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.toolSlots = {}
        self.showLabel = attributes.get('showLabel', False)
        self._lastBrowseDiff = None
        self._pageStops = []
        self._direction = attributes.get('direction', uiconst.HORIZONTAL)
        (self._xSlots, self._ySlots, self._slotSize, self._slotMarginX, self._slotMarginY, self._pageMargin,) = attributes.get('gridSize', (4, 5, 48, 2, 6, 4))
        self.dragScrollAreaSize = attributes.get('dragScrollAreaSize', 16)
        self.dragScrollStepSize = attributes.get('dragScrollStepSize', 6)
        (pageWidth, pageHeight,) = self.GetPageSize()
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        if isHorizontal:
            self.SetSize(pageWidth, pageHeight + self.DOTPARENTSIZE)
            self.sr.pagesParent = uicls.Container(parent=self, align=uiconst.TOBOTTOM, pos=(0,
             0,
             0,
             self.DOTPARENTSIZE), state=uiconst.UI_PICKCHILDREN)
        else:
            self.SetSize(pageWidth + self.DOTPARENTSIZE, pageHeight)
            self.sr.pagesParent = uicls.Container(parent=self, align=uiconst.TOLEFT, pos=(0,
             0,
             self.DOTPARENTSIZE,
             0), state=uiconst.UI_NORMAL)
        self.sr.slotClipper = uicls.Container(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=True)
        self.sr.slotParent = uicls.Container(parent=self.sr.slotClipper, align=uiconst.RELATIVE, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        underlay = uicls.Frame(name='underlay', frameConst=uiconst.FRAME_FILLED_CORNER6, parent=self.sr.slotClipper, color=(0.0,
         0.0,
         0.0,
         attributes.get('bgAlpha', 0.3)))
        defaultSlots = attributes.get('defaultSlots', {})
        self.defaultSlots = defaultSlots
        menuID = attributes.get('menuID', None)
        self.menuID = menuID
        if menuID is not None:
            registeredSlots = settings.user.ui.Get('%sSlots_%s' % (menuID, VERSION), defaultSlots)
            delData = []
            for (slotIdx, slotData,) in registeredSlots.iteritems():
                if slotData not in defaultSlots.values():
                    delData.append(slotIdx)

            for each in delData:
                del registeredSlots[each]

            for (slotIdx, each,) in defaultSlots.iteritems():
                if each not in registeredSlots.values():
                    while slotIdx in registeredSlots.keys():
                        slotIdx += 1

                    registeredSlots[slotIdx] = each

            uthread.new(self.LoadSlots, registeredSlots)



    def GetMenu(self):
        return [('Reset To Default', self.Reset)]



    def Reset(self):
        uthread.new(self.LoadSlots, self.defaultSlots)



    def UpdatePages(self, maxPages = None, dragging = False):
        if dragging:
            pass
        maxPages = maxPages or 1
        slotsInPage = self._xSlots * self._ySlots
        (pageWidth, pageHeight,) = self.GetPageSize()
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        for (slotIdx, slotData,) in self.slots.iteritems():
            pageIdx = slotIdx / slotsInPage + 1
            maxPages = max(pageIdx, maxPages)

        maxPages = max(1, min(self.MAXPAGES, maxPages))
        if len(self._pageStops) == maxPages:
            return 
        for slot in self.sr.slotParent.children[:]:
            if isinstance(slot, uicls.Line):
                slot.Close()

        self._pageStops = []
        for i in xrange(maxPages):
            if isHorizontal:
                self._pageStops.append(i * pageWidth)
            else:
                self._pageStops.append(i * pageHeight)
            if i:
                if isHorizontal:
                    uicls.Line(parent=self.sr.slotParent, align=uiconst.RELATIVE, pos=(i * pageWidth,
                     6,
                     1,
                     pageHeight - 12), color=(1.0, 1.0, 1.0, 0.065))
                else:
                    uicls.Line(parent=self.sr.slotParent, align=uiconst.RELATIVE, pos=(6,
                     i * pageHeight,
                     pageWidth - 12,
                     1), color=(1.0, 1.0, 1.0, 0.065))

        if isHorizontal:
            self.sr.slotParent.width = max(self._pageStops) + pageWidth
            self.sr.slotParent.height = pageHeight
        else:
            self.sr.slotParent.width = pageWidth
            self.sr.slotParent.height = max(self._pageStops) + pageHeight
        self.UpdatePageInfo()



    def UpdatePageInfo(self):
        needDots = len(self._pageStops)
        if needDots > 1:
            portionStep = 1.0 / (needDots - 1)
        else:
            portionStep = 0.0
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        step = 7
        centerOffset = step * (needDots - 1) / 2
        if needDots != len(self.sr.pagesParent.children):
            uiutil.Flush(self.sr.pagesParent)
            portion = 0.0
            offset = 0
            for each in self._pageStops:
                dot = uicls.Icon(parent=self.sr.pagesParent, icon='ui_3_8_1', align=uiconst.CENTER)
                dot.OnClick = (self.ClickPageDot, dot)
                dot.portion = portion
                dot.pageStop = each
                portion += portionStep
                if isHorizontal:
                    dot.left = offset - centerOffset
                else:
                    dot.top = offset - centerOffset
                offset += 7

        self.UpdatePageStatus()



    def ClickPageDot(self, dot, *args):
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        if isHorizontal:
            uthread.new(uicore.effect.MorphUIMassSpringDamper, self.sr.slotParent, 'left', -dot.pageStop, float=False, frequency=15.0, dampRatio=0.5, callback=self.UpdatePageStatus)
        else:
            uthread.new(uicore.effect.MorphUIMassSpringDamper, self.sr.slotParent, 'top', -dot.pageStop, float=False, frequency=15.0, dampRatio=0.5, callback=self.UpdatePageStatus)



    def UpdatePageStatus(self, *args):
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        portion = 0.0
        if isHorizontal:
            scrollRange = self.sr.slotParent.width - self.width
            if scrollRange and self.sr.slotParent.left:
                portion = -self.sr.slotParent.left / float(scrollRange)
        else:
            scrollRange = self.sr.slotParent.height - self.height
            if scrollRange and self.sr.slotParent.top:
                portion = -self.sr.slotParent.top / float(scrollRange)
        for dot in self.sr.pagesParent.children:
            dot.SetAlpha(min(1.0, max(0.25, 1.0 - abs(dot.portion - portion) * 2.5)))




    def GetPageSize(self):
        pageWidth = self._xSlots * (self._slotSize + self._slotMarginX * 2) + self._pageMargin * 2
        pageHeight = self._ySlots * (self._slotSize + self._slotMarginY * 2) + self._pageMargin * 2
        return (pageWidth, pageHeight)



    def CheckDragScroll(self, slotID = None, *args):
        x = uicore.uilib.x
        y = uicore.uilib.y
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        (l, t, w, h,) = self.GetAbsolute()
        halfSlot = self._slotSize / 2
        scrollAreaSize = self.dragScrollAreaSize
        browse = 0
        if isHorizontal and t - scrollAreaSize < y < t + h + scrollAreaSize:
            if l - scrollAreaSize < x <= l:
                browse = -1
            elif l + w < x <= l + w + scrollAreaSize:
                browse = 1
        elif not isHorizontal and l - scrollAreaSize < x < l + w + scrollAreaSize:
            if t - scrollAreaSize < y <= t:
                browse = -1
            elif t + h < y <= t + h + scrollAreaSize:
                browse = 1
        if browse:
            self.Browse(browse * self.dragScrollStepSize, dragging=True)
        elif l < x < l + w and t < y < t + h:
            if slotID is not None:
                self.CheckSlotLocation(slotID)



    def CheckSlotLocation(self, slotID, moveSlotsInstantly = False):
        x = uicore.uilib.x
        y = uicore.uilib.y
        (l, t, w, h,) = self.sr.slotParent.GetAbsolute()
        lastCheckPos = getattr(self, '_lastArrangementPos', (-1, -1))
        (lx, ly,) = lastCheckPos
        if lx == x and ly == y and x >= l:
            slotIdx = self.GetSlotUnderCursor()
            oldSlotIndex = None
            for (k, v,) in self.slots.iteritems():
                if v[0] == slotID:
                    oldSlotIndex = k
                    break

            if oldSlotIndex is not None:
                data = self.slots[oldSlotIndex]
                del self.slots[oldSlotIndex]
                self.CompactArrangement()
                if slotIdx in self.slots:
                    newSlots = {}
                    for (k, v,) in self.slots.iteritems():
                        if k >= slotIdx:
                            newSlots[k + 1] = v
                        else:
                            newSlots[k] = v

                    self.slots = newSlots
                self.slots[slotIdx] = data
                self.CompactArrangement()
                newActualSlotIndex = None
                for (k, v,) in self.slots.iteritems():
                    if v[0] == slotID:
                        newActualSlotIndex = k
                        break

                if newActualSlotIndex != oldSlotIndex:
                    self.RearrangeSlots(moveSlotsInstantly)
        self._lastArrangementPos = (x, y)



    def GetSlotUnderCursor(self):
        x = uicore.uilib.x
        y = uicore.uilib.y
        (l, t, w, h,) = self.sr.slotParent.GetAbsolute()
        (pageWidth, pageHeight,) = self.GetPageSize()
        slotsInPage = self._xSlots * self._ySlots
        xStep = pageWidth / float(self._xSlots)
        yStep = pageHeight / float(self._ySlots)
        xIdx = int((x - l) / xStep)
        yIdx = int((y - t) / yStep)
        slotIdx = xIdx / self._xSlots * slotsInPage + yIdx * self._xSlots
        if xIdx >= self._xSlots:
            slotIdx += xIdx % self._xSlots
        else:
            slotIdx += xIdx
        slotIdx = max(0, min(self.MAXPAGES * slotsInPage - 1, slotIdx))
        return slotIdx



    def OnDropData(self, draggedObj, dropData):
        if type(dropData) != types.DictionaryType:
            return 
        shortCutSlotData = dropData.get('shortCutSlotData', None)
        if shortCutSlotData is None:
            return 
        sourceMenuID = dropData.get('menuID', None)
        if sourceMenuID is None:
            return 
        dropSlotIndex = self.GetSlotUnderCursor()
        if sourceMenuID != self.menuID:
            self.AddNewSlot(shortCutSlotData[1:], dropSlotIndex)



    def AddNewSlot(self, slotData, slotIdx, refresh = True):
        (name, cmdstring, iconNo,) = slotData
        slotID = uthread.uniqueId()
        if not uicore.cmd.HasCommand(cmdstring):
            print 'Command not available',
            print cmdstring
        slotDataWithID = (slotID,
         name,
         cmdstring,
         iconNo)
        if name in self.toolSlots:
            return 
        if slotIdx in self.slots:
            newSlots = {}
            for (k, v,) in self.slots.iteritems():
                if k >= slotIdx:
                    newSlots[k + 1] = v
                else:
                    newSlots[k] = v

            self.slots = newSlots
        self.slots[slotIdx] = slotDataWithID
        self.toolSlots[name] = uicls.ToolSlot(parent=self.sr.slotParent, pos=(self._slotMarginX + self._pageMargin,
         self._slotMarginY + self._pageMargin,
         self._slotSize,
         self._slotSize), name='slot_%s' % name, slotData=slotDataWithID, slotIdx=slotIdx, slotID=slotID, showLabel=self.showLabel)
        if refresh:
            self.RearrangeSlots()



    def GetToolSlots(self):
        return self.toolSlots



    def CompactArrangement(self):
        slotIdxs = self.slots.keys()
        slotIdxs.sort()
        slotsInPage = self._xSlots * self._ySlots
        newSetup = {}
        registerSetup = {}
        pageIdx = 0
        newIdx = 0
        for slotIdx in slotIdxs:
            thisPageIdx = slotIdx / slotsInPage
            if pageIdx != thisPageIdx:
                pageIdx = thisPageIdx
                newIdx = 0
            data = self.slots[slotIdx]
            (slotID, name, cmdstring, iconNo,) = data
            newSetup[newIdx + pageIdx * slotsInPage] = data
            registerSetup[newIdx + pageIdx * slotsInPage] = (name, cmdstring, iconNo)
            newIdx += 1

        self.slots = newSetup
        settings.user.ui.Set('%sSlots_%s' % (self.menuID, VERSION), registerSetup)



    def RearrangeSlots(self, moveSlotsInstantly = True):
        if getattr(self, '_rearranging', False):
            self._pendingRearrangement = True
            return 
        self._rearranging = True
        self.CompactArrangement()
        slotsByID = {}
        for slot in self.sr.slotParent.children[:]:
            if hasattr(slot, 'slotID'):
                slotsByID[slot.slotID] = slot

        slotsInPage = self._xSlots * self._ySlots
        (pageWidth, pageHeight,) = self.GetPageSize()
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        for (slotIdx, slotData,) in self.slots.iteritems():
            (slotID, name, cmdstring, iconNo,) = slotData
            slot = slotsByID.get(slotID, None)
            if slot is None:
                print 'Slot not found',
                print name
                continue
            pageIdx = slotIdx / slotsInPage
            localSlotIdx = slotIdx - pageIdx * slotsInPage
            if isHorizontal:
                newLeft = self._slotMarginX + pageIdx * pageWidth + localSlotIdx % self._xSlots * (self._slotSize + self._slotMarginX * 2) + self._pageMargin
                newTop = self._slotMarginY + localSlotIdx / self._xSlots * (self._slotSize + self._slotMarginY * 2) + self._pageMargin
            else:
                newLeft = self._slotMarginX + localSlotIdx % self._xSlots * (self._slotSize + self._slotMarginX * 2) + self._pageMargin
                newTop = self._slotMarginY + pageIdx * pageHeight + localSlotIdx / self._xSlots * (self._slotSize + self._slotMarginY * 2) + self._pageMargin
            slot.slotIdx = slotIdx
            if slot.left != newLeft or slot.top != newTop:
                if moveSlotsInstantly:
                    slot.left = newLeft
                    slot.top = newTop
                else:
                    uthread.new(uicore.effect.CombineEffects, slot, left=newLeft, top=newTop, time=250.0)

        self.UpdatePages()
        self._rearranging = False
        if getattr(self, '_pendingRearrangement', False):
            self._pendingRearrangement = False
            self.RearrangeSlots(moveSlotsInstantly)



    def LoadSlots(self, slots):
        self.slots = {}
        self.toolSlots = {}
        self.sr.slotParent.Flush()
        for (slotIdx, slotData,) in slots.iteritems():
            self.AddNewSlot(slotData, slotIdx, refresh=False)

        self.RearrangeSlots()
        sm.ScatterEvent('OnFlipMenuLoadSlotsThreadFinished', self)



    def OnMouseWheel(self, *args):
        uthread.new(self.Throw, max(-5, min(5, int(uicore.uilib.dz * 0.05)))).context = 'FlipMenu::Throw'



    def OnMouseDown(self, *args):
        self.StartDragScroll()



    def StartDragScroll(self):
        self._lastBrowseDiff = None
        self._initMouseDown = (uicore.uilib.x, uicore.uilib.y)
        self.sr.scrollTimer = base.AutoTimer(10, self.UpdateScroll)



    def StopDragScroll(self):
        self.sr.scrollTimer = None
        self._initMouseDown = None
        if self._lastBrowseDiff:
            uthread.new(self.Throw, self._lastBrowseDiff)
        else:
            uthread.new(self.FixPosition)



    def OnMouseUp(self, *args):
        self.StopDragScroll()



    def UpdateScroll(self, *args):
        mx = uicore.uilib.x
        my = uicore.uilib.y
        (ix, iy,) = self._initMouseDown
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        if isHorizontal:
            diff = mx - ix
        else:
            diff = my - iy
        if diff:
            if abs(diff) > self._slotSize:
                if diff > 0:
                    self._initMouseDown = (ix + self._slotSize, iy + self._slotSize)
                else:
                    self._initMouseDown = (ix - self._slotSize, iy - self._slotSize)
            else:
                self._initMouseDown = (mx, my)
            self._lastBrowseDiff = diff
            self.Browse(-int(diff))
        else:
            self._lastBrowseDiff = None



    def Browse(self, direction, dragging = False):
        self._breakSlotParentMovement = True
        if direction < 0:
            direction = max(direction, -self._slotSize)
        else:
            direction = min(direction, self._slotSize)
        (pageWidth, pageHeight,) = self.GetPageSize()
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        if dragging:
            if isHorizontal:
                self.sr.slotParent.left = self.sr.slotParent.left - direction
                if self.sr.slotParent.left < 0:
                    maxPages = abs(self.sr.slotParent.left / pageWidth) + 1
                    if len(self._pageStops) != maxPages:
                        self.UpdatePages(maxPages)
            else:
                self.sr.slotParent.top = self.sr.slotParent.top - direction
                if self.sr.slotParent.top < 0:
                    maxPages = abs(self.sr.slotParent.top / pageHeight) + 1
                    if len(self._pageStops) != maxPages:
                        self.UpdatePages(maxPages)
        elif isHorizontal:
            self.sr.slotParent.left = min(pageWidth, max(-self.sr.slotParent.width, self.sr.slotParent.left - direction))
        else:
            self.sr.slotParent.top = min(pageHeight, max(-self.sr.slotParent.height, self.sr.slotParent.top - direction))
        self._breakSlotParentMovement = False
        self.UpdatePageStatus()



    def Throw(self, distance):
        steps = 20
        maxExp = math.exp(steps / 10.0)
        self._initMouseDown = None
        tot = 0
        for i in xrange(1, steps + 1):
            iExp = math.exp(i / 10.0)
            self.Browse(-(distance - int(distance * (iExp / maxExp))))
            tot += abs(-(distance - int(distance * (iExp / maxExp))))
            blue.pyos.synchro.SleepWallclock(10)
            if self.destroyed:
                return 
            if self._initMouseDown:
                break

        self.FixPosition()



    def FixPosition(self):
        self.UpdatePages()
        if not self._pageStops:
            return 
        self._pendingPositionFix = True
        isHorizontal = bool(self._direction == uiconst.HORIZONTAL)
        gotoPageStop = 0
        lastDiff = 100000
        for pageStop in self._pageStops:
            if isHorizontal:
                thisDiff = abs(pageStop + self.sr.slotParent.left)
            else:
                thisDiff = abs(pageStop + self.sr.slotParent.top)
            if thisDiff < lastDiff:
                lastDiff = thisDiff
                gotoPageStop = pageStop

        self._fixingPosition = True
        if isHorizontal:
            if -gotoPageStop != self.sr.slotParent.left:
                self._pendingPositionFix = False
                uthread.new(uicore.effect.CombineEffects, self.sr.slotParent, left=-gotoPageStop, time=250.0, callback=self.UpdatePageStatus, abortFunction=self.CheckScrollMovement)
        elif -gotoPageStop != self.sr.slotParent.top:
            self._pendingPositionFix = False
            uthread.new(uicore.effect.CombineEffects, self.sr.slotParent, top=-gotoPageStop, time=250.0, callback=self.UpdatePageStatus, abortFunction=self.CheckScrollMovement)



    def CheckScrollMovement(self, *args):
        return getattr(self, '_breakSlotParentMovement', False) or getattr(self, '_pendingPositionFix', False) or getattr(self, '_initMouseDown', None)




