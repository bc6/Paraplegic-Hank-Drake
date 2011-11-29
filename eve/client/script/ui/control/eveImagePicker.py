import uicls
import uiconst
import math
import uthread
import blue
import base
import service
import ccConst
import log
import localization
HILITE = ('ui_105_32_27', 15, -3)

class ImagePicker(uicls.Container):
    __guid__ = 'uicls.ImagePicker'
    default_align = uiconst.CENTER
    default_left = 0
    default_top = 0
    default_width = 768
    default_height = 128
    default_name = 'ImagePicker'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.onPreSetValueCallback = None
        self.onSetValueCallback = None
        self.onChangeFocusCallback = None
        self._activeData = None
        self._lastBrowseDiff = False
        self._lastSpringValue = None
        self._initMouseDownX = None
        self._doBlock = False
        self._availableTypeIDs = set()
        if session.role & service.ROLE_CONTENT:
            invCache = sm.GetService('invCache')
            if session.stationid:
                try:
                    inv = invCache.GetInventory(const.containerHangar)
                    self._availableTypeIDs.update({i.typeID for i in inv.List() if i.categoryID == const.categoryApparel})
                except Exception as e:
                    log.LogWarn()
            if session.charid:
                try:
                    inv = invCache.GetInventoryFromId(session.charid)
                    self._availableTypeIDs.update({i.typeID for i in inv.List() if i.flagID == const.flagWardrobe})
                except Exception as e:
                    log.LogWarn()
        self.zoomFactor = attributes.get('zoomFactor', 6.0)
        self.imageWidth = attributes.get('imageWidth', 128)
        self.imageHeight = attributes.get('imageHeight', 128)
        self.browserWidth = attributes.get('browserWidth', 400)
        self.numSpecialItems = attributes.get('numSpecialItems', 0)
        (l, t, w, h,) = self.parent.GetAbsolute()
        self.sr.counterParent = uicls.Container(parent=self.parent, align=uiconst.TOPLEFT, name='counterParent', state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/CharacterCustomization/ShowActive'), pos=(7, 6, 13, 9), opacity=0.5, idx=0)
        self.sr.counterParent.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.counterParent)
        self.sr.counterParent.OnMouseExit = (self.OnGenericMouseExit, self.sr.counterParent)
        self.sr.counterParent.OnClick = self.ShowActiveSlot
        self.sr.counterParent.sr.icon = uicls.Frame(frameConst=(ccConst.ICON_FOCUSFRAME, 15, -11), parent=self.sr.counterParent, color=ccConst.COLOR50)
        self.sr.counterParent.sr.label = uicls.CCLabel(text='', parent=self.sr.counterParent, color=ccConst.COLOR50, align=uiconst.CENTER, left=1)
        if self.DebugRoleCheck():
            self.sr.debugLabel = uicls.CCLabel(text='', parent=self, align=uiconst.CENTER, top=self.imageHeight / 2 + 8, letterspace=0, fontsize=9, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_NORMAL, idx=0)
            self.sr.debugLabel.GetMenu = self.GetDebugMenu
        self.BuildStrip(attributes.images)
        self.UpdateCounter()
        self.onSetValueCallback = attributes.get('OnSetValue', None)
        self.onChangeFocusCallback = attributes.get('OnChangeFocus', None)
        self.onPreSetValueCallback = attributes.get('OnPreSetValue', None)



    def ShowActiveSlot(self, *args):
        active = self.GetActiveData()
        if active:
            self.SetActiveData(active)



    def GetDebugMenu(self):
        if self.DebugRoleCheck():
            return [('Copy Focus Data', self.CopyFocusData)]



    def CopyFocusData(self):
        fd = self.GetFocusData()
        if fd:
            blue.pyos.SetClipboardData(repr(fd[1]))



    def BuildStrip(self, images, *args):
        if self.sr.slots:
            self.sr.slots.Close()
        self.sr.slots = uicls.Container(parent=self, align=uiconst.CENTERLEFT)
        self.images = images
        self.slots = []
        self.height = self.imageHeight + 64
        self.width = self.browserWidth
        self.focusSlot = None
        if len(images) > 0:
            for (idx, imageData,) in enumerate(images):
                slot = self.AddSlot(idx, imageData)

        else:
            slot = self.AddSlot(0, (None, [None, None], None))
            log.LogTraceback('ImagePicker - Building strip without images')
        self.sr.slots.width = self.sr.slots.children[-1].left + self.sr.slots.children[-1].width
        self.maxSlotLeft = int(self.width / 2.0 - self.imageWidth / 4.0)
        self.minSlotLeft = -int(self.sr.slots.width - self.width / 2.0)
        self.sr.slots.height = self.imageHeight
        self.FixPosition(instant=True)
        self.UpdateSlotZoom()



    def AddSlot(self, idx, imageData):
        step = int(self.imageWidth * 0.75)
        self._slotGap = step
        specialItemPadding = 0
        if self.numSpecialItems and idx >= self.numSpecialItems:
            specialItemPadding = int(step * 0.5)
        slotpar = uicls.Container(name='slotPar_%s' % idx, parent=self.sr.slots, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(-self.imageWidth / 2 + (idx + 1) * step + specialItemPadding,
         0,
         self.imageWidth,
         self.imageHeight))
        slotpar.idx = idx
        slotpar.imageData = imageData
        slot = uicls.Container(parent=slotpar, align=uiconst.CENTER, state=uiconst.UI_NORMAL, pos=(0,
         0,
         self.imageWidth / 2,
         self.imageHeight / 2))
        slot.OnMouseDown = (self.OnSlotMouseDown, slot)
        slot.OnMouseUp = (self.OnSlotMouseUp, slot)
        slot.imageData = imageData
        slot.sr.hilite = uicls.Frame(parent=slot, align=uiconst.TOALL, frameConst=HILITE, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 1.0))
        slot.sr.hilite.SetPadding(-6, -6, -6, -6)
        slot.sr.thumbnail = uicls.Sprite(parent=slot, texturePath=None, align=uiconst.TOALL, padding=(2, 2, 2, 2), state=uiconst.UI_DISABLED)
        uicls.Fill(parent=slot, padding=(2, 2, 2, 2), color=(0.0, 0.0, 0.0, 0.75))
        return slot



    def GetActiveData(self):
        return self._activeData



    def GetOptions(self):
        return self.images



    def GetFocusData(self):
        if self.focusSlot:
            return self.focusSlot.imageData



    def SetActiveDataFromValue(self, toValue, doCallbacks = True, focusOnSlot = True, doYield = True):
        toValueSet = set([toValue])
        if isinstance(toValue, tuple):
            if toValue[1] == '':
                v0TypeData = (toValue[0], 'v0', toValue[2])
                toValueSet.add(v0TypeData)
            elif toValue[1] == 'v0':
                emptyStringTypeData = (toValue[0], '', toValue[2])
                toValueSet.add(emptyStringTypeData)
        for (i, imageData,) in enumerate(self.images):
            (resPath, data, hiliteResPath,) = imageData
            if data[1] in toValueSet:
                self.SetActiveData(imageData, focusOnSlot=focusOnSlot, doCallbacks=doCallbacks, doYield=doYield)
                break




    def SetActiveData(self, data, focusOnSlot = True, doCallbacks = True, doYield = True):
        newData = self._activeData != data
        if doCallbacks and self.onPreSetValueCallback and newData:
            self.onPreSetValueCallback(data)
        self._activeData = data
        self.UpdateCounter()
        if focusOnSlot:
            uthread.new(self.SetFocusData, data, doYield)
        if doCallbacks and self.onSetValueCallback and newData:
            self.onSetValueCallback(data)



    def SetFocusData(self, data, doYield = True):
        if self.destroyed:
            return 
        slotParent = self.GetSlotParentByData(data)
        if slotParent:
            (l, t, w, h,) = self.GetAbsolute()
            newleft = w / 2 - (slotParent.left + slotParent.width / 2)
            if newleft == self.sr.slots.left:
                return 
            uicore.effect.MorphUIMassSpringDamper(self.sr.slots, 'left', newleft, newthread=not doYield, initVal=self.sr.slots.left, float=False, frequency=15.0, dampRatio=0.75, callback=self.UpdateSlotZoom)
            self.state = uiconst.UI_NORMAL



    def UpdateCounter(self):
        if self.sr.counterParent:
            if self._activeData is not None:
                slotParent = self.GetSlotParentByData(self._activeData)
                self.sr.counterParent.sr.label.text = '%s/%s' % (slotParent.idx + 1, len(self.images))
            else:
                self.sr.counterParent.sr.label.text = '-/%s' % len(self.images)
            self.sr.counterParent.width = self.sr.counterParent.sr.label.textwidth + 8



    def GetSlotParentByData(self, data):
        for slot in self.sr.slots.children:
            if getattr(slot, 'imageData', None) == data:
                return slot




    def GetValue(self, *args):
        if self.focusSlot:
            return self.focusSlot.imageData



    def SpringFeed(self, item, value):
        if self.destroyed:
            return 
        lastSpringValue = self._lastSpringValue or 0
        self.RotateImages(lastSpringValue - value, clampValue=False)
        self._lastSpringValue = value



    def CheckMouseOver(self, slot):
        if slot.destroyed:
            slot.sr.mouseOverTimer = None
            return 
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return 
        if self._activeData == slot.imageData:
            slot.sr.hilite.state = uiconst.UI_DISABLED
            slot.sr.hilite.SetAlpha(1.0)
        elif uicore.uilib.mouseOver is slot:
            slot.sr.hilite.state = uiconst.UI_DISABLED
            slot.sr.hilite.SetAlpha(0.25)
        else:
            slot.sr.hilite.state = uiconst.UI_HIDDEN



    def OnSlotMouseDown(self, slot, mouseBtn, *args):
        self.OnMouseDown(mouseBtn)



    def OnSlotMouseUp(self, slot, mouseBtn, *args):
        self.OnMouseUpAlt(slot, mouseBtn)



    def CheckIfSlotLoaded(self, slotParent):
        if getattr(slotParent, '_loaded', False):
            return 
        slotParent._loaded = True
        slot = slotParent.children[0]
        (resPath, data, hiliteResPath,) = slot.imageData
        resFile = blue.ResFile()
        if not resPath or not resFile.FileExists(resPath):
            resPath = 'res:/UI/Asset/missingThumbnail.dds'
        slot.sr.thumbnail.LoadTexture(resPath)
        if len(data) > 2 and data[2] is not None and session.role & service.ROLE_CONTENT:
            inLimitedRecustomization = getattr(uicore.layer.charactercreation, 'mode', -1) == ccConst.MODE_LIMITED_RECUSTOMIZATION
            flag = uicls.Container(parent=slot, align=uiconst.TOPLEFT, padding=(2, 2, 2, 2), pos=(0, 0, 20, 20), state=uiconst.UI_DISABLED, idx=0)
            fill = uicls.Fill(parent=flag, color=(0, 1.0, 0, 0.5))
            if data[2] not in self._availableTypeIDs:
                fill.SetRGB(1.0, 0, 0)
                slot.GetMenu = (self.GetRightClickMenu, data[2])
            if not inLimitedRecustomization:
                uicls.Fill(parent=flag, color=(0, 0.0, 0, 1.0), padding=5, idx=0)
        if self._activeData == slot.imageData:
            slot.sr.hilite.state = uiconst.UI_DISABLED
            slot.sr.hilite.SetAlpha(1.0)
        elif slot.sr.hilite:
            slot.sr.hilite.state = uiconst.UI_HIDDEN
        slot.sr.mouseOverTimer = base.AutoTimer(33, self.CheckMouseOver, slot)



    def OnMouseDown(self, mouseBtn = 0, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return 
        self._lastBrowseDiff = None
        self._lastMouseX = uicore.uilib.x
        self._initMouseDownX = uicore.uilib.x
        self._initPosX = self.sr.slots.left
        self.sr.scrollTimer = base.AutoTimer(10, self.UpdateScroll)
        uthread.new(self.OnScrollStart)



    def OnMouseUp(self, mouseBtn, *args):
        self.OnMouseUpAlt(mouseBtn=mouseBtn)



    def OnMouseUpAlt(self, slot = None, mouseBtn = 0):
        if mouseBtn != uiconst.MOUSELEFT:
            return 
        self.sr.scrollTimer = None
        if self._lastBrowseDiff:
            uthread.new(self.Throw, self._lastBrowseDiff)
        elif self.sr.slots.left != getattr(self, '_initPosX', 0):
            self._initMouseDownX = None
            uthread.new(self.FixPosition)
        elif slot:
            self.SetActiveData(slot.imageData)



    def OnMouseWheel(self, *args):
        uthread.new(self.MouseWheel_thread).context = 'ImagePicker::Throw'
        return 1



    def MouseWheel_thread(self, *args):
        self.Browse(uicore.uilib.dz / 3)
        if self.sr.settleWheelThread:
            self.sr.settleWheelThread.kill()
            self.sr.settleWheelThread = None
        self.sr.settleWheelThread = uthread.new(self.SettleAfterWheel_thread)



    def SettleAfterWheel_thread(self, *args):
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed:
            return 
        self.sr.wheelSettleTimer = None
        self.FixPosition()



    def FixPosition(self, instant = False):
        (l, t, w, h,) = self.GetAbsolute()
        newleft = self.sr.slots.left
        rounding = (newleft - w / 2) % self._slotGap
        if rounding > self._slotGap / 2:
            newleft += self._slotGap - rounding
        elif rounding < self._slotGap / 2:
            newleft -= rounding
        else:
            return 
        newleft = max(-self.sr.slots.width + (w + self.imageWidth) / 2, min(newleft, w / 2 - self._slotGap))
        if instant:
            self.sr.slots.left = newleft
        else:
            uicore.effect.MorphUIMassSpringDamper(self.sr.slots, 'left', newleft, newthread=0, initVal=self.sr.slots.left, float=False, frequency=15.0, dampRatio=0.75, callback=self.UpdateSlotZoom)
        self.state = uiconst.UI_NORMAL



    def UpdateScroll(self, *args):
        newLeft = self._initPosX + (uicore.uilib.x - self._initMouseDownX)
        if self.maxSlotLeft > newLeft and newLeft > self.minSlotLeft:
            self.sr.slots.left = newLeft
        self._lastBrowseDiff = uicore.uilib.x - self._lastMouseX
        self._lastMouseX = uicore.uilib.x
        self.UpdateSlotZoom()



    def UpdateSlotZoom(self, *args):
        if not hasattr(self, 'sr'):
            return 
        (l, t, w, h,) = self.GetAbsolute()
        centerX = l + w / 2
        slotsInside = []
        centerSlot = None
        minDistFromCenter = 1000
        for slot in self.sr.slots.children:
            if not hasattr(slot, 'children'):
                continue
            (sl, st, sw, sh,) = slot.GetAbsolute()
            slotCenter = sl + sw / 2
            if slotCenter >= l and slotCenter <= l + w:
                slotsInside.append((abs(centerX - slotCenter), slotCenter, slot))
            else:
                slot.children[0].width = self.imageWidth / 2
                slot.children[0].height = self.imageHeight / 2
            distFromCenter = abs(centerX - slotCenter)
            if distFromCenter < minDistFromCenter:
                minDistFromCenter = distFromCenter
                centerSlot = slot

        slotsInside.sort()
        slotsInside.reverse()
        maxDist = w / 2
        for (diff, slotCenter, slot,) in slotsInside:
            if diff:
                sizeFactor = 1.0 - abs(diff) / float(maxDist)
            else:
                sizeFactor = 1.0
            slot.children[0].width = self.imageWidth / 2 + int(self.imageWidth / 2 * sizeFactor)
            slot.children[0].height = self.imageHeight / 2 + int(self.imageHeight / 2 * sizeFactor)
            slot.SetOrder(0)
            uthread.new(self.CheckIfSlotLoaded, slot)

        if slotsInside:
            self.focusSlot = slotsInside[-1][-1]
            if self.onChangeFocusCallback:
                self.onChangeFocusCallback(self.focusSlot.imageData)
            if self.DebugRoleCheck():
                (resPath, data, hiliteResPath,) = self.focusSlot.imageData
                self.sr.debugLabel.text = repr(data[1])



    def DebugRoleCheck(self):
        mask = service.ROLE_CONTENT | service.ROLE_QA | service.ROLE_PROGRAMMER | service.ROLE_GMH
        if eve.session.role & mask and not prefs.GetValue('CCHideAssetDebugText', False):
            return True
        else:
            return False



    def Browse(self, direction):
        if not len(self.sr.slots.children):
            return 
        self.sr.slots.left = self.sr.slots.left - direction
        self.UpdateSlotZoom()



    def Throw(self, distance):
        steps = 20
        maxExp = math.exp(steps / 10.0)
        (l, t, w, h,) = self.GetAbsolute()
        self._initMouseDownX = None
        for i in xrange(1, steps + 1):
            if self.sr.slots.left > self.maxSlotLeft:
                break
            if self.sr.slots.left < self.minSlotLeft:
                break
            iExp = math.exp(i / 10.0)
            self.Browse(-(distance - int(distance * (iExp / maxExp))))
            blue.pyos.synchro.SleepWallclock(10)
            if self.destroyed:
                return 
            if self._initMouseDownX:
                break

        self.FixPosition()



    def OnScrollStart(self, *args):
        pass



    def OnGenericMouseEnter(self, btn, *args):
        btn.SetOpacity(1.0)



    def OnGenericMouseExit(self, btn, *args):
        btn.SetOpacity(0.5)



    def OnGenericMouseDown(self, btn, *args):
        btn.sr.icon.top += 1



    def GetRightClickMenu(self, typeID, *args):
        if not session.role & service.ROLE_WORLDMOD:
            return []
        return [('WM: /create this type', self.GMCreateItem, (typeID,))]



    def GMCreateItem(self, typeID, *args):
        try:
            sm.RemoteSvc('slash').SlashCmd('/create %s %s %s' % (typeID, 1, session.stationid2))
            uicore.layer.charactercreation.sr.step.GoToAssetMode(animate=0, forcedMode=1)
            sm.GetService('cc').ClearMyAvailabelTypeIDs()
        except Exception as e:
            log.LogWarn()




