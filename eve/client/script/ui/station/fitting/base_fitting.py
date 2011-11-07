import sys
import uix
import uiutil
import mathUtil
import xtriui
import uthread
import blue
import util
import lg
import log
import form
import listentry
import base
import math
import trinity
import uiconst
import uicls
import turret
CONSTMAXSHIELDFRI = 350
CONSTMAXSHIELDCRU = 1500
CONSTMAXSHIELDBAT = 5000
CONSTMAXARMORFRI = 350
CONSTMAXARMORCRU = 1500
CONSTMAXARMORBAT = 5000
CONSTMAXSTRUCTUREFRI = 350
CONSTMAXSTRUCTURECRU = 1500
CONSTMAXSTRUCTUREBAT = 5000
PASSIVESHIELDRECHARGE = 0
SHIELDBOOSTRATEACTIVE = 1
ARMORREPAIRRATEACTIVE = 2
HULLREPAIRRATEACTIVE = 3
FONTCOLOR_HILITE = '<color=0xffffff00>'
FONTCOLOR_DEFAULT = '<color=0xc0ffffff>'
CALIBRATION_GAUGE_ZERO = 223.0
CALIBRATION_GAUGE_RANGE = 30.0
CALIBRATION_GAUGE_COLOR = (0.29296875,
 0.328125,
 0.33984375,
 1)
CPU_GAUGE_ZERO = 45.0
CPU_GAUGE_RANGE = -45.0
CPU_GAUGE_COLOR = (0.203125,
 0.3828125,
 0.37890625,
 1)
POWERGRID_GAUGE_ZERO = 45.0
POWERGRID_GAUGE_RANGE = 45.0
POWERGRID_GAUGE_COLOR = (0.40625,
 0.078125,
 0.03125,
 1)
GAUGE_THICKNESS = 11

class SaveFittingSettings(uicls.Window):
    __guid__ = 'form.SaveFittingSettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(mls.UI_GENERIC_FITTING)
        self.SetWndIcon('ui_17_128_4')
        self.SetTopparentHeight(0)
        self.SetMinSize([256, 160])
        self.MakeUnMinimizable()
        self.sr.main.padTop = const.defaultPadding
        self.sr.main.padBottom = const.defaultPadding
        fittings = sm.GetService('fittingSvc').GetFittings(eve.session.charid)
        options = []
        for (fittingID, data,) in fittings.iteritems():
            options.append((data.name.lower(), (data.name, fittingID)))

        options = uiutil.SortListOfTuples(options)
        options.insert(0, (mls.UI_GENERIC_NEW_SETTING, -1))
        self.sr.savedFittingsCombo = c = uicls.Combo(label=None, parent=self.sr.main, options=options, name='savedFittingsCombo', select=None, callback=self.ComboSavedFittingChange, align=uiconst.TOTOP)
        self.sr.savedFittingsCombo.padTop = 4
        self.sr.savedFittingsCombo.padRight = 6
        self.sr.savedFittingsCombo.padLeft = 100
        uicls.Label(text=mls.UI_CMD_SAVEAS, left=-90, top=2, parent=self.sr.savedFittingsCombo, fontsize=12, state=uiconst.UI_NORMAL)
        self.sr.nameInput = uicls.SinglelineEdit(name='nameInput', parent=self.sr.main, maxLength=32, align=uiconst.TOTOP)
        self.sr.nameInput.padTop = 4
        self.sr.nameInput.padRight = 6
        self.sr.nameInput.padLeft = 100
        uicls.Label(text=mls.UI_GENERIC_NAME, left=-90, top=2, parent=self.sr.nameInput, fontsize=12, state=uiconst.UI_NORMAL)
        self.sr.descriptionEdit = uicls.EditPlainText(setvalue='', parent=self.sr.main, align=uiconst.TOALL)
        self.sr.descriptionEdit.padTop = 4
        self.sr.descriptionEdit.padBottom = 4
        self.sr.descriptionEdit.padRight = 5
        self.sr.descriptionEdit.padLeft = 99
        uicls.Label(text=mls.UI_GENERIC_DESCRIPTION, left=-90, top=2, parent=self.sr.descriptionEdit, fontsize=12, state=uiconst.UI_NORMAL)
        self.DefineButtons(uiconst.OKCANCEL)



    def ComboSavedFittingChange(self, combo, label, id, *args):
        if id != -1:
            fitting = sm.GetService('fittingSvc').GetFitting(eve.session.charid, id)
            self.sr.nameInput.SetValue(fitting.name)
            self.sr.descriptionEdit.SetValue(fitting.description)
        else:
            self.sr.nameInput.SetValue('')
            self.sr.descriptionEdit.SetValue('')



    def Confirm(self, sender = None, *args):
        name = self.sr.nameInput.GetValue()
        if not name:
            eve.Message('MissingRequiredField', {'fieldname': mls.UI_GENERIC_NAME})
            return 
        description = self.sr.descriptionEdit.GetValue()
        fittingID = self.sr.savedFittingsCombo.GetValue()
        if fittingID == -1:
            fittingID = None
        sm.GetService('fittingSvc').PersistFitting(eve.session.charid, name, description, fittingID)
        self.SetModalResult(uiconst.ID_OK)




class LoadFittingSettings(uicls.Window):
    __guid__ = 'form.LoadFittingSettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(mls.UI_GENERIC_FITTING)
        self.SetWndIcon('ui_17_128_4')
        self.SetTopparentHeight(0)
        self.SetMinSize([256, 160])
        self.MakeUnMinimizable()
        self.sr.main.padTop = const.defaultPadding
        self.sr.main.padBottom = const.defaultPadding
        fittings = sm.GetService('fittingSvc').GetFittings(eve.session.charid)
        options = []
        for (fittingID, data,) in fittings.iteritems():
            options.append((data.name.lower(), (data.name, fittingID)))

        options = uiutil.SortListOfTuples(options)
        options.insert(0, (mls.UI_CMD_PICK_SETTING, -1))
        self.sr.savedFittingsCombo = c = uicls.Combo(label=None, parent=self.sr.main, options=options, name='savedFittingsCombo', select=None, callback=self.ComboSavedFittingChange, align=uiconst.TOTOP)
        self.sr.savedFittingsCombo.padTop = 4
        self.sr.savedFittingsCombo.padRight = 6
        self.sr.savedFittingsCombo.padLeft = 100
        uicls.Label(text=mls.UI_GENERIC_SETTINGS, left=-90, top=2, parent=self.sr.savedFittingsCombo, fontsize=12, state=uiconst.UI_NORMAL)
        self.sr.descriptionText = uicls.Label(text='', parent=self.sr.main, fontsize=12, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.sr.descriptionText.padTop = 4
        self.sr.descriptionText.padBottom = 4
        self.sr.descriptionText.padRight = 5
        self.sr.descriptionText.padLeft = 99
        self.DefineButtons(uiconst.OKCANCEL)



    def ComboSavedFittingChange(self, combo, label, id, *args):
        if id != -1:
            fitting = sm.GetService('fittingSvc').GetFitting(eve.session.charid, id)
            self.sr.descriptionText.text = fitting.description
        else:
            self.sr.descriptionText.text = ''



    def Confirm(self, sender = None, *args):
        fittingID = self.sr.savedFittingsCombo.GetValue()
        if fittingID == -1:
            eve.Message('MissingRequiredField', {'fieldname': 'Settings'})
            return 
        uthread.new(sm.GetService('fittingSvc').LoadFitting, eve.session.charid, fittingID)
        self.SetModalResult(uiconst.ID_OK)




class FittingWindow(uicls.Window):
    __guid__ = 'form.FittingWindow'
    __notifyevents__ = ['OnSetDevice']
    default_width = 920
    default_height = 560

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(mls.UI_GENERIC_FITTING)
        self.SetWndIcon('ui_17_128_4', hidden=True)
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.shipID = attributes.shipID
        self.ConstructLayout()



    def ConstructLayout(self):
        uix.Flush(self.sr.main)
        if eve.session.stationid:
            self.scope = 'station'
        else:
            self.scope = 'inflight'
        self.sr.fitting = form.Fitting(top=-8, parent=self.sr.main, shipID=self.shipID)
        self.sr.fitting.sr.wnd = self
        self.sr.fitting.Startup()
        self.clipChildren = 0
        self.sr.main.clipChildren = 0
        self.sr.maincontainer.clipChildren = 0



    def OnResize_(self, *args):
        self.OnResizeUpdate()



    def OnSetDevice(self):
        if self.shipID:
            uthread.new(self.ConstructLayout)



    def InitializeStatesAndPosition(self, *args, **kw):
        current = sm.GetService('window').GetWndPositionAndSize('fitting')
        default = sm.GetService('window').GetDefaults('fitting')
        (fixedWidth, fixedHeight,) = (self._fixedWidth, self._fixedHeight)
        uicls.Window.InitializeStatesAndPosition(self, *args, **kw)
        if fixedWidth is not None:
            self.width = fixedWidth
            self._fixedWidth = fixedWidth
        if fixedHeight is not None:
            self.height = fixedHeight
            self._fixedHeight = fixedHeight
        if list(default)[:4] == list(current)[:4]:
            settings.user.ui.Set('defaultFittingPosition', 1)
            dw = uicore.desktop.width
            dh = uicore.desktop.height
            self.left = (dw - self.width) / 2
            self.top = (dh - self.height) / 2
        self.sr.headerLine.state = uiconst.UI_HIDDEN
        self.MakeUnpinable()
        self.Unlock()
        uthread.new(uicore.registry.SetFocus, self)
        self._collapseable = 0



    def OnClose_(self, *args):
        settings.user.ui.Set('defaultFittingPosition', 0)



    def MouseDown(self, *args):
        uthread.new(uicore.registry.SetFocus, self)
        uiutil.SetOrder(self, 0)



    def HiliteFitting(self, item):
        uthread.new(self.sr.fitting.HiliteSlots, item)



    def OnResizeUpdate(self, *args):
        if util.GetAttrs(self, 'sr', 'fitting', 'sr', 'sceneContainer'):
            self.sr.fitting.sr.sceneContainer.UpdateViewPort()



    def OnMouseMove(self, *args):
        self.DisplayGaugeTooltips()



    def DisplayGaugeTooltips(self):
        if not self.sr.fitting:
            return 
        (l, t, w, h,) = self.sr.fitting.GetAbsolute()
        cX = w / 2 + l
        cY = h / 2 + t
        x = uicore.uilib.x - cX
        y = uicore.uilib.y - cY
        length2 = pow(x, 2) + pow(y, 2)
        if length2 < pow(w / 2 - 20, 2):
            if y != 0:
                rad = math.atan(float(x) / float(y))
                degrees = 180 * rad / math.pi
            else:
                degrees = 90
            if x > 0:
                status = self.sr.fitting.GetStatusCpuPowerCalibr()
                if degrees > 0 and degrees < 45:
                    self.hint = '%s - %s %%' % (mls.UI_GENERIC_POWERGRID, status[1])
                elif degrees > 45 and degrees < 90:
                    self.hint = '%s - %s %%' % (mls.UI_GENERIC_CPU, status[0])
                self.hint = ''
            elif degrees > 47 and degrees < 77:
                status = self.sr.fitting.GetStatusCpuPowerCalibr()
                self.hint = '%s - %s %%' % (mls.UI_GENERIC_CALIBRATION, status[2])
            self.hint = ''
        else:
            self.hint = ''




class FittingInventory(uicls.Scroll):
    __guid__ = 'xtriui.FittingInventory'
    __notifyevents__ = ['OnItemChange']

    def SetData(self, initialLoad = True):
        uix.Flush(self.sr.activeframe)
        forceLoad = bool(initialLoad or getattr(self, '_pendingInventroyLoad', False))
        if forceLoad:
            self.LoadInventory(forceLoad)
        sm.RegisterNotify(self)



    def _OnClose(self):
        uicls.Scroll._OnClose(self)
        sm.UnregisterNotify(self)
        self.FilterFunction = None



    def OnItemChange(self, item, change):
        if item.locationID == eve.session.shipid or util.IsStation(item.locationID) or const.ixLocationID in change and util.IsStation(change[const.ixLocationID]):
            self.LoadInventory()



    def LoadInventory(self, force = False):
        if not force and (getattr(self, '_loadingInventory', False) or not uiutil.IsVisible(self)):
            self._pendingInventroyLoad = True
            return 
        self._loadingInventory = True
        self.sr.loadInvTimer = base.AutoTimer(50, self._LoadInventory)



    def _LoadInventory(self):
        self._loadingInventory = True
        self.sr.loadInvTimer = None
        (assets, sortby,) = self.GetAssets(self)
        self.Load(contentList=assets, sortby=sortby, scrollTo=self.GetScrollProportion())
        expandableMenu = self.parent.parent
        if expandableMenu._expanded:
            while expandableMenu._changing:
                blue.pyos.synchro.Sleep(10)

            expandableMenu.Expand(time=-1)
        self._loadingInventory = False
        if getattr(self, '_pendingInventroyLoad', False):
            self._pendingInventroyLoad = False
            self.LoadInventory()



    def GetTotalHeight(self):
        return self.GetContentHeight()



    def OnDropData(self, dragObj, nodes):
        itemlist = [ item for item in nodes if getattr(item, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem') if not (self.flag == const.flagDroneBay and item.rec.categoryID != const.categoryDrone) ]
        if len(itemlist) == 0:
            return 
        fromLocation = itemlist[0].item.locationID
        if self.flag == const.flagHangar:
            toContainer = const.containerHangar
        elif self.flag in (const.flagCargo, const.flagDroneBay):
            toContainer = eve.session.shipid
        else:
            return 
        if len(itemlist) == 1:
            qty = getattr(itemlist[0].rec, 'quantity', 1)
            if uicore.uilib.Key(uiconst.VK_SHIFT) and qty > 1:
                ret = uix.QtyPopup(qty, 1, 1, None)
                if ret is None:
                    return 
                qty = ret['qty']
            stateMgr = sm.StartService('godma').GetStateManager()
            item = itemlist[0].item
            if item.categoryID == const.categoryCharge:
                return self.dogmaLocation.UnloadChargeToContainer(item.locationID, item.itemID, (toContainer,), self.flag)
            if item.categoryID == const.categoryModule:
                return self.dogmaLocation.UnloadModuleToContainer(item.locationID, item.itemID, (toContainer,), self.flag)
            if toContainer == eve.session.shipid:
                return eve.GetInventoryFromId(eve.session.shipid).Add(itemlist[0].itemID, fromLocation, qty=qty, flag=self.flag)
            return eve.GetInventory(toContainer).Add(itemlist[0].itemID, fromLocation, qty=qty)
        if toContainer == eve.session.shipid:
            return eve.GetInventoryFromId(toContainer).MultiAdd([ item.itemID for item in itemlist ], fromLocation, flag=self.flag)
        return eve.GetInventory(toContainer).MultiAdd([ item.itemID for item in itemlist ], fromLocation, flag=self.flag)




class Fitting(uicls.FittingLayout):
    __notifyevents__ = ['ProcessActiveShipChanged',
     'OnAttributes',
     'OnDogmaItemChange',
     'OnDogmaAttributeChanged',
     'OnDropDataOnItemNameChange',
     'OnStartSlotLinkingMode',
     'OnResetSlotLinkingMode',
     'OnAttributes',
     'OnAttribute']
    __guid__ = 'form.Fitting'

    def init(self):
        self._nohilitegroups = {const.groupRemoteSensorBooster: [const.attributeCpu, const.attributePower],
         const.groupRemoteSensorDamper: [const.attributeCpu, const.attributePower]}
        self.sr.colorPickerCookie = None
        self.Reset()



    def ApplyAttributes(self, attributes):
        uicls.FittingLayout.ApplyAttributes(self, attributes)
        shipID = attributes.shipID
        if shipID is None:
            self.shipID = session.shipid
        else:
            self.shipID = shipID
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.updateStatsThread = None
        self.updateStatsArgs = (None, None)



    def GetShipAttribute(self, attributeID):
        if session.shipid == self.shipID:
            ship = sm.GetService('godma').GetItem(self.shipID)
            attributeName = self.dogmaLocation.dogmaStaticMgr.attributes[attributeID].attributeName
            return getattr(ship, attributeName)
        else:
            return self.dogmaLocation.GetAttributeValue(self.shipID, attributeID)



    def GetSensorStrengthAttribute(self):
        if session.shipid == self.shipID:
            return sm.GetService('godma').GetStateManager().GetSensorStrengthAttribute(self.shipID)
        else:
            return self.dogmaLocation.GetSensorStrengthAttribute(self.shipID)



    def Reset(self):
        self.slots = {}
        self.isDelayedAnim = False
        self.menuSlots = {}
        self.statusCpuPowerCalibr = [None, None, None]
        self.initialized = False



    def _OnClose(self):
        uicls.Container._OnClose(self)
        if self.sr.colorPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.colorPickerCookie)
            self.sr.colorPickerCookie = None



    def OnDogmaItemChange(self, item, change):
        if self is None or self.destroyed or not hasattr(self, 'sr') or not self.initialized:
            return 
        if const.ixStackSize not in change and const.ixFlag not in change and const.ixLocationID not in change:
            return 
        oldLocationID = change.get(const.ixLocationID, None)
        if self.shipID not in (oldLocationID, item.locationID):
            return 
        self.LoadCapacitorStats()
        if item.groupID in const.turretModuleGroups:
            self.UpdateHardpoints()
        self.ReloadFitting(self.shipID)



    def Startup(self):
        sm.RegisterNotify(self)
        self.state = uiconst.UI_PICKCHILDREN
        self.sr.slotParent = uicls.Container(parent=self, name='slotParent', idx=0, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uthread.new(self.Anim)



    def Anim(self):
        try:
            self._Anim()
        except:
            if self.destroyed:
                log.LogException(severity=log.LGWARN, toMsgWindow=0, toConsole=0)
                sys.exc_clear()
            else:
                raise 



    def _Anim(self):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        self.sr.baseColor.SetRGB(*color)
        newslotParent = self.sr.slotParent
        uix.Flush(newslotParent)
        dw = uicore.desktop.width
        minWidth = 1400
        scaleFactor = min(1.0, max(0.75, dw / float(minWidth)))
        totalSidePanelsWidth = min(1200, max(960, dw - 120))
        self.sr.wnd.height = int(max(490, 560 * scaleFactor))
        self._scaleFactor = scaleFactor
        self._fullWidth = totalSidePanelsWidth
        self._baseShapeSize = int(640 * scaleFactor)
        self._fullPanelWidth = (totalSidePanelsWidth - self._baseShapeSize) / 2
        self._centerOnlyWidth = totalSidePanelsWidth - self._fullPanelWidth * 2
        self._leftPanelWidth = 0
        self._rightPanelWidth = 0
        self.width = self._baseShapeSize
        self.height = self._baseShapeSize
        cX = cY = self._baseShapeSize / 2
        width = self._centerOnlyWidth
        settings.user.ui.Set('fittingPanelLeft', 0)
        if settings.user.ui.Get('fittingPanelRight', 1):
            width += self._fullPanelWidth
            self._rightPanelWidth = self._fullPanelWidth
            iconNo = 'ui_73_16_195'
        else:
            iconNo = 'ui_73_16_196'
        icon = uicls.Icon(icon=iconNo, parent=newslotParent, align=uiconst.CENTER, pos=(int(304 * scaleFactor),
         0,
         0,
         0))
        icon.OnClick = self.ToggleRight
        self.sr.toggleRightBtn = icon
        self.sr.wnd.width = width
        self.UpdateCenterShapePosition()
        sceneContainerParent = uicls.Container(parent=self, align=uiconst.CENTER, width=int(550 * scaleFactor), height=int(550 * scaleFactor))
        sc = form.SceneContainer(align=uiconst.TOALL)
        sc.pickState = uiconst.TR2_SPS_OFF
        sc.SetAlign(uiconst.TOALL)
        sceneContainerParent.children.append(sc)
        sc.PrepareCamera()
        sc.PrepareSpaceScene()
        sc.SetStencilMap()
        self.sr.sceneContainer = sc
        nav = form.SceneContainerBaseNavigation(parent=sceneContainerParent, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL, pickRadius=-1)
        nav.Startup(sc)
        nav.OnDropData = self.OnDropData
        nav.GetMenu = self.GetShipMenu
        self.sr.sceneNavigation = nav
        rightside = uicls.Container(name='rightside', parent=self.sr.wnd.sr.main, align=uiconst.TORIGHT, width=self._fullPanelWidth - 16, idx=0)
        rightside.padRight = 10
        rightside.padTop = 0
        rightside.padBottom = 10
        if not settings.user.ui.Get('fittingPanelRight', 1):
            rightside.opacity = 0.0
            rightside.state = uiconst.UI_DISABLED
        self.sr.rightPanel = rightside
        gapsize = 1.0
        numgaps = 4
        numslots = 32
        step = 360.0 / (numslots + numgaps * gapsize)
        rad = int(239 * scaleFactor)
        angle = 360.0 - 3.5 * step
        key = uix.FitKeys()
        i = 0
        for gidx in [0, 1, 2]:
            for sidx in xrange(8):
                if not self or self.destroyed:
                    return 
                flag = getattr(const, 'flag%sSlot%s' % (key[gidx], sidx))
                cos = math.cos((angle - 90.0) * math.pi / 180.0)
                sin = math.sin((angle - 90.0) * math.pi / 180.0)
                width = int(44 * scaleFactor)
                height = int(54 * scaleFactor)
                left = int(rad * cos) + cX - width / 2
                top = int(rad * sin) + cY - height / 2
                nSlot = xtriui.FittingSlot(name='slot_%s_%s' % (gidx, sidx), parent=newslotParent, pos=(left,
                 top,
                 width,
                 height), rotation=-mathUtil.DegToRad(angle))
                nSlot.scaleFactor = scaleFactor
                nSlot.radCosSin = (rad,
                 cos,
                 sin,
                 cX,
                 cY)
                angle += step
                if i + 1 in (8, 16):
                    angle += step * gapsize
                powerType = [const.effectHiPower, const.effectMedPower, const.effectLoPower][gidx]
                nSlot.gidx = gidx
                nSlot.Startup(flag, powerType, self.dogmaLocation, scaleFactor)
                self.slots[flag] = nSlot
                eve.Message('fittingSlot%s' % key[gidx])
                blue.pyos.synchro.Sleep(5)
                i += 1


        gapsize = 0.333
        numgaps = 2
        numslots = 8
        step = 90.0 / (numslots + numgaps * gapsize)
        angle += step * (gapsize * 2.0)
        for i in xrange(5):
            if not self or self.destroyed:
                return 
            i = 4 - i
            subsystemFlag = getattr(const, 'flagSubSystemSlot%s' % i, None)
            if not subsystemFlag:
                continue
            cos = math.cos((angle - 90.0) * math.pi / 180.0)
            sin = math.sin((angle - 90.0) * math.pi / 180.0)
            width = int(44 * scaleFactor)
            height = int(54 * scaleFactor)
            left = int(rad * cos) + cX - width / 2
            top = int(rad * sin) + cY - height / 2
            nSlot = xtriui.FittingSlot(name='subsystemSlot_%s' % i, parent=newslotParent, pos=(left,
             top,
             width,
             height), rotation=-mathUtil.DegToRad(angle))
            nSlot.scaleFactor = scaleFactor
            nSlot.radCosSin = (rad,
             cos,
             sin,
             cX,
             cY)
            nSlot.gidx = 3
            nSlot.Startup(subsystemFlag, const.effectSubSystem, self.dogmaLocation, scaleFactor)
            angle += step
            self.slots[subsystemFlag] = nSlot
            blue.pyos.synchro.Sleep(5)

        angle += step * gapsize
        for i in xrange(3):
            rigFlag = getattr(const, 'flagRigSlot%s' % i, None)
            if not rigFlag:
                continue
            cos = math.cos((angle - 90.0) * math.pi / 180.0)
            sin = math.sin((angle - 90.0) * math.pi / 180.0)
            width = int(44 * scaleFactor)
            height = int(54 * scaleFactor)
            left = int(rad * cos) + cX - width / 2
            top = int(rad * sin) + cY - height / 2
            nSlot = xtriui.FittingSlot(name='slot_%s_%s' % (gidx, sidx), parent=newslotParent, pos=(left,
             top,
             width,
             height), rotation=-mathUtil.DegToRad(angle))
            nSlot.scaleFactor = scaleFactor
            nSlot.radCosSin = (rad,
             cos,
             sin,
             cX,
             cY)
            nSlot.gidx = 4
            nSlot.Startup(rigFlag, const.effectRigSlot, self.dogmaLocation, scaleFactor)
            angle += step
            self.slots[rigFlag] = nSlot
            blue.pyos.synchro.Sleep(5)

        blue.pyos.synchro.Yield()
        self.sr.cpu_power_statustext = uicls.Label(text='', parent=newslotParent, name='cpu_power_statustext', left=8, top=0, width=200, autowidth=False, idx=0, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        self.sr.cpu_power_statustext.top = (self.height - self.sr.wnd.height) / 2 + 10
        self.sr.calibrationstatustext = uicls.Label(text='', parent=newslotParent, name='calibrationstatustext', left=8, top=int(100 * scaleFactor), idx=0, state=uiconst.UI_DISABLED)
        self.sr.calibrationstatustext.top = (self.height - self.sr.wnd.height) / 2 + 50
        self.sr.shipnamecont = uicls.Container(name='shipname', parent=rightside, align=uiconst.TOTOP, height=42, width=271)
        self.sr.shipnamecont.padBottom = 6
        self.sr.shipnametext = uicls.Label(text='', parent=self.sr.shipnamecont, letterspace=1, fontsize=12, width=200, state=uiconst.UI_DISABLED, uppercase=True)
        self.sr.dragIcon = xtriui.FittingDraggableText(name='theicon', idx=0, align=uiconst.TOPLEFT, parent=self.sr.shipnamecont, width=100, height=20)
        self.sr.dragIcon.state = uiconst.UI_NORMAL
        shipTypeID = self.GetShipDogmaItem().typeID
        self.sr.infolink = uicls.InfoIcon(typeID=shipTypeID, itemID=self.shipID, size=16, left=0, top=0, parent=self.sr.shipnamecont, idx=0)
        self.sr.fittingSvcCont = uicls.Container(name='fittingSvcCont', parent=self.sr.shipnamecont, align=uiconst.BOTTOMLEFT, height=22, width=200)
        loadFittingBtn = uicls.Button(parent=self.sr.fittingSvcCont, label=mls.UI_FITTING_BROWSE, func=self.LoadFittingSetup, pos=(-2, 6, 0, 0), alwaysLite=True)
        loadFittingBtn.hint = mls.UI_GENERIC_FITTING_BROWSETOOLTIP
        saveFittingBtn = uicls.Button(parent=self.sr.fittingSvcCont, label=mls.UI_CMD_SAVE, func=self.SaveFittingSetup, pos=(loadFittingBtn.left + loadFittingBtn.width,
         loadFittingBtn.top,
         0,
         0), alwaysLite=True)
        saveFittingBtn.hint = mls.UI_GENERIC_FITTING_SAVETOOLTIP
        self.sr.stripBtn = uicls.Button(parent=self.sr.fittingSvcCont, label=mls.UI_FITTING_STRIP, func=self.StripFitting, pos=(saveFittingBtn.left + saveFittingBtn.width,
         loadFittingBtn.top,
         0,
         0), alwaysLite=True)
        self.sr.stripBtn.hint = mls.UI_GENERIC_FITTING_STRIPTOOLTIP
        self.sr.fittingSvcCont.width = self.sr.stripBtn.left + self.sr.stripBtn.width
        self.sr.capacitorStatsParent = uicls.Container(name='capacitorStatsParent', parent=None, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        self.sr.capacitorHeaderStatsParent = uicls.Container(name='capacitorHeaderStatsParent', parent=None, align=uiconst.TOPRIGHT, state=uiconst.UI_PICKCHILDREN, width=200, height=20)
        label = uicls.Label(text='', parent=self.sr.capacitorHeaderStatsParent, left=8, idx=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT)
        self.sr.capacitorHeaderStatsParent.sr.statusText = label
        self.sr.defenceStatsParent = uicls.Container(name='defenceStatsParent', parent=None, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        self.sr.defenceHeaderStatsParent = uicls.Container(name='defenceHeaderStatsParent', parent=None, align=uiconst.CENTERRIGHT, state=uiconst.UI_PICKCHILDREN, width=200, height=20)
        label = uicls.Label(text='', parent=self.sr.defenceHeaderStatsParent, left=8, idx=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT)
        self.sr.defenceHeaderStatsParent.sr.statusText = label
        self.sr.targetingStatsParent = uicls.Container(name='targetingStatsParent', parent=None, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        self.sr.targetingStatsParent.sumContent = True
        self.sr.targetingHeaderStatsParent = uicls.Container(name='targetingHeaderStatsParent', parent=None, align=uiconst.CENTERRIGHT, state=uiconst.UI_PICKCHILDREN, width=200, height=20)
        label = uicls.Label(text='', parent=self.sr.targetingHeaderStatsParent, left=8, aidx=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT)
        self.sr.targetingHeaderStatsParent.sr.statusText = label
        self.sr.navigationStatsParent = uicls.Container(name='navigationStatsParent', parent=None, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        self.sr.navigationStatsParent.sumContent = True
        em = xtriui.ExpandableMenuContainer(parent=rightside, pos=(0, 0, 0, 0))
        em.multipleExpanded = True
        em.Load([(mls.UI_GENERIC_CAPACITOR,
          self.sr.capacitorStatsParent,
          self.LoadCapacitorStats,
          None,
          76,
          self.sr.capacitorHeaderStatsParent),
         (mls.UI_GENERIC_DEFENCE,
          self.sr.defenceStatsParent,
          self.LoadDefenceStats,
          None,
          183,
          self.sr.defenceHeaderStatsParent),
         (mls.UI_GENERIC_TARGETING,
          self.sr.targetingStatsParent,
          self.LoadTargetingStats,
          None,
          None),
         (mls.UI_GENERIC_NAVIGATION,
          self.sr.navigationStatsParent,
          self.LoadNavigationStats,
          None,
          None)], 'fittingRightside')
        angle = 306.0
        rad = int(310 * scaleFactor)
        attribute = cfg.dgmattribs.Get(const.attributeTurretSlotsLeft)
        cos = math.cos((180.0 - angle) * math.pi / 180.0)
        sin = math.sin((180.0 - angle) * math.pi / 180.0)
        left = int(rad * cos) + cX - 16
        top = int(rad * sin) + cY - 16
        icon = uicls.Icon(name='turretSlotsLeft', icon='ui_26_64_1', parent=newslotParent, state=uiconst.UI_NORMAL, hint=attribute.displayName, pos=(left,
         top,
         32,
         32), ignoreSize=True)
        attribute = cfg.dgmattribs.Get(const.attributeLauncherSlotsLeft)
        cos = math.cos(angle * math.pi / 180.0)
        sin = math.sin(angle * math.pi / 180.0)
        left = int(rad * cos) + cX - 16
        top = int(rad * sin) + cY - 16
        icon = uicls.Icon(name='missileLauncherSlotsLeft', icon='ui_81_64_16', parent=newslotParent, state=uiconst.UI_NORMAL, hint=attribute.displayName, pos=(left,
         top,
         32,
         32), ignoreSize=True)
        step = 2.5
        rad = int(280 * scaleFactor)
        angle = 310.0 - step * 7.5
        self.sr.turretSlots = []
        self.sr.launcherSlots = []
        for i in xrange(8):
            cos = math.cos(angle * math.pi / 180.0)
            sin = math.sin(angle * math.pi / 180.0)
            iconPar = uicls.Transform(parent=newslotParent, pos=(rad * cos + cX - 8,
             rad * sin + cY - 8,
             16,
             16))
            iconPar.SetRotation(-mathUtil.DegToRad(angle + 90.0))
            icon = uicls.Icon(icon='ui_73_16_193', parent=iconPar)
            cos = math.cos((180.0 - angle) * math.pi / 180.0)
            sin = math.sin((180.0 - angle) * math.pi / 180.0)
            iconPar2 = uicls.Transform(parent=newslotParent, pos=(rad * cos + cX - 8,
             rad * sin + cY - 8,
             16,
             16))
            iconPar2.SetRotation(mathUtil.DegToRad(angle + 90.0))
            icon2 = uicls.Icon(icon='ui_73_16_193', parent=iconPar2)
            self.sr.launcherSlots.append(icon)
            self.sr.turretSlots.append(icon2)
            angle += step

        self.sr.turretSlots.reverse()
        self.sr.launcherSlots.reverse()
        cargoDroneCont = uicls.Container(name='rightside', parent=newslotParent, align=uiconst.BOTTOMLEFT, width=110, height=64, left=const.defaultPadding)
        cargoDroneCont.top = (self.height - self.sr.wnd.height) / 2 + 6
        self.sr.cargoSlot = xtriui.CargoCargoSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, idx=-1)
        self.sr.cargoSlot.Startup(mls.UI_GENERIC_CARGOHOLD, 'ui_3_64_13', const.flagCargo, self.dogmaLocation)
        self.sr.cargoSlot.OnClick = self.OpenCargoHoldOfActiveShip
        self.sr.cargoSlot.state = uiconst.UI_NORMAL
        self.sr.droneSlot = xtriui.CargoDroneSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=-1)
        self.sr.droneSlot.Startup(mls.UI_GENERIC_DRONEBAY, 'ui_11_64_16', const.flagDroneBay, self.dogmaLocation)
        self.sr.droneSlot.OnClick = self.OpenDroneBayOfActiveShip
        self.sr.droneSlot.state = uiconst.UI_NORMAL
        self.initialized = True
        uthread.new(self.ReloadFitting, eve.session.shipid)
        uthread.new(self.ReloadShipModel)



    def GetShipMenu(self, *args):
        if self.shipID is None:
            return []
        if session.stationid:
            hangarInv = eve.GetInventory(const.containerHangar)
            hangarItems = hangarInv.List()
            for each in hangarItems:
                if each.itemID == self.shipID:
                    return sm.GetService('menu').InvItemMenu(each)

        elif session.solarsystemid:
            return sm.GetService('menu').CelestialMenu(session.shipid)



    def SaveFittingSetup(self, *args):
        fittingSvc = sm.StartService('fittingSvc')
        fitting = util.KeyVal()
        (fitting.shipTypeID, fitting.fitData,) = fittingSvc.GetFittingDictForActiveShip()
        fitting.fittingID = None
        fitting.description = ''
        fitting.name = cfg.evelocations.Get(util.GetActiveShip()).locationName
        fitting.ownerID = 0
        wnd = sm.StartService('window').GetWindow('viewFitting' + fitting.name, create=1, decoClass=form.ViewFitting, fitting=fitting, truncated=None)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def LoadFittingSetup(self, *args):
        if sm.GetService('fittingSvc').HasLegacyClientFittings():
            wnd = sm.StartService('window').GetWindow('ImportLegacyFittingsWindow', create=1)
        else:
            wnd = sm.StartService('window').GetWindow('FittingMgmt', create=1, decoClass=form.FittingMgmt)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def LoadNavigationStats(self, initialLoad = False):
        np = self.sr.navigationStatsParent
        uix.Flush(np)
        self.sr.navigationStatsParent.state = uiconst.UI_PICKCHILDREN
        lineColor = (1.0, 1.0, 1.0, 0.125)
        toShow = [(const.attributeMaxVelocity, const.attributeMass, const.attributeAgility), (const.attributeBaseWarpSpeed,)]
        (l, t, w, h,) = np.GetAbsolute()
        step = w / 3
        if step < 90:
            iconSize = 24
        else:
            iconSize = 32
        i = 0
        for attrGroup in toShow:
            row = uicls.Container(name='topRow', parent=np, align=uiconst.TOTOP, height=iconSize)
            if i:
                uicls.Line(parent=row, align=uiconst.TOTOP, color=lineColor)
            left = 0
            for each in attrGroup:
                attribute = cfg.dgmattribs.Get(each)
                if left:
                    uicls.Line(parent=row, align=uiconst.RELATIVE, color=lineColor, left=left, height=iconSize - 1, width=1, top=1)
                icon = uicls.Icon(graphicID=attribute.iconID, parent=row, pos=(left,
                 0,
                 iconSize,
                 iconSize), hint=attribute.displayName, name=attribute.displayName, ignoreSize=True)
                label = uicls.Label(text='', parent=row, left=icon.left + icon.width, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
                label.hint = attribute.displayName
                left += step
                self.sr.Set(('StatsLabel', attribute.attributeID), label)
                self.sr.Set(('StatsIcon', attribute.attributeID), icon)

            i += 1
            row.sr.backgroundFrame = uicls.BumpedUnderlay(parent=row, padding=(-1, -1, -1, -1))

        if not initialLoad:
            self.UpdateStats()



    def LoadTargetingStats(self, initialLoad = False):
        tp = self.sr.targetingStatsParent
        uix.Flush(tp)
        self.sr.targetingStatsParent.state = uiconst.UI_PICKCHILDREN
        lineColor = (1.0, 1.0, 1.0, 0.125)
        (sensorStrengthAttributeID, val,) = self.GetSensorStrengthAttribute()
        toShow = [('sensorStrength', const.attributeScanResolution, const.attributeMaxTargetRange), (const.attributeSignatureRadius, const.attributeMaxLockedTargets)]
        (l, t, w, h,) = tp.GetAbsolute()
        step = w / 3
        if step < 90:
            iconSize = 24
        else:
            iconSize = 32
        i = 0
        for attrGroup in toShow:
            row = uicls.Container(name='topRow', parent=tp, align=uiconst.TOTOP, height=iconSize)
            if i:
                uicls.Line(parent=row, align=uiconst.TOTOP, color=lineColor)
            left = 0
            for attributeID in attrGroup:
                if attributeID == 'sensorStrength':
                    each = sensorStrengthAttributeID
                else:
                    each = attributeID
                attribute = cfg.dgmattribs.Get(each)
                if left:
                    uicls.Line(parent=row, align=uiconst.RELATIVE, color=lineColor, left=left, height=iconSize - 1, width=1, top=1)
                icon = uicls.Icon(graphicID=attribute.iconID, parent=row, pos=(left,
                 0,
                 iconSize,
                 iconSize), hint=attribute.displayName, name=attribute.displayName, ignoreSize=True)
                label = uicls.Label(text='', parent=row, left=icon.left + icon.width, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
                label.hint = attribute.displayName
                left += step
                tp.sr.Set(('StatsLabel', attributeID), label)
                tp.sr.Set(('StatsIcon', attributeID), icon)

            i += 1
            row.sr.backgroundFrame = uicls.BumpedUnderlay(parent=row, padding=(-1, -1, -1, -1))

        if not initialLoad:
            self.UpdateStats()



    def LoadDefenceStats(self, initialLoad = False):
        col1Width = 90
        lineColor = (1.0, 1.0, 1.0, 0.125)
        barColors = [(0.1, 0.37, 0.55, 1.0),
         (0.55, 0.1, 0.1, 1.0),
         (0.45, 0.45, 0.45, 1.0),
         (0.55, 0.37, 0.1, 1.0)]
        resAttrs = (cfg.dgmattribs.Get(const.attributeEmDamageResonance),
         cfg.dgmattribs.Get(const.attributeThermalDamageResonance),
         cfg.dgmattribs.Get(const.attributeKineticDamageResonance),
         cfg.dgmattribs.Get(const.attributeExplosiveDamageResonance))
        dsp = self.sr.defenceStatsParent
        uix.Flush(dsp)
        dsp.state = uiconst.UI_PICKCHILDREN
        tRow = uicls.Container(name='topRow', parent=dsp, align=uiconst.TOTOP, height=32)
        uicls.Line(parent=tRow, align=uiconst.RELATIVE, color=lineColor, left=col1Width, height=31, width=1, top=1)
        tRow.sr.backgroundFrame = uicls.BumpedUnderlay(parent=tRow, padding=(-1, -1, -1, -1))
        self.sr.bestRepairPickerPanel = None
        bestPar = uicls.Container(name='bestPar', parent=tRow, align=uiconst.TOPLEFT, height=32, width=col1Width, state=uiconst.UI_NORMAL, idx=0)
        bestPar.OnClick = self.ExpandBestRepair
        expandIcon = uicls.Icon(name='expandIcon', icon='ui_38_16_229', parent=bestPar, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        numPar = uicls.Container(name='numPar', parent=bestPar, width=11, height=11, top=17, left=4, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        numLabel = uicls.Label(text='', parent=numPar, atop=-1, state=uiconst.UI_DISABLED, align=uiconst.CENTER, shadow=None)
        uicls.Fill(parent=numPar, color=barColors[1])
        dsp.sr.Set('activeBestRepairNumLabel', numLabel)
        icon = uicls.Icon(parent=bestPar, state=uiconst.UI_DISABLED, width=32, height=32)
        statusLabel = uicls.Label(text='', parent=bestPar, left=icon.left + icon.width, linespace=10, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        dsp.sr.Set('activeBestRepairLabel', statusLabel)
        dsp.sr.Set('activeBestRepairParent', bestPar)
        dsp.sr.Set('activeBestRepairIcon', icon)
        (l, t, w, h,) = dsp.GetAbsolute()
        step = (w - col1Width) / 4
        left = col1Width
        for attribute in resAttrs:
            icon = uicls.Icon(graphicID=attribute.iconID, parent=tRow, pos=(left + (step - 32) / 2 + 4,
             0,
             0,
             0), idx=0, hint=attribute.displayName)
            left += step

        for (label, what, iconNo, labelhint, iconhint,) in ((mls.UI_GENERIC_SHIELD,
          'shield',
          'ui_1_64_13',
          mls.UI_FITTING_SHIELDHP_CHARGERATE,
          ''),
         (mls.UI_GENERIC_ARMOR,
          'armor',
          'ui_1_64_9',
          '',
          ''),
         (mls.UI_GENERIC_STRUCTURE,
          'structure',
          'ui_2_64_12',
          '',
          ''),
         (mls.UI_GENERIC_EFFECTIVE_HP,
          'effectiveHp',
          'ui_26_64_2',
          mls.UI_FITTING_EFFECTIVE_HP,
          mls.UI_FITTING_EFFECTIVE_HP)):
            row = uicls.Container(name='row_%s' % what, parent=dsp, align=uiconst.TOTOP, height=32)
            uicls.Line(parent=row, align=uiconst.TOTOP, color=lineColor)
            mainIcon = uicls.Icon(icon=iconNo, parent=row, pos=(0, 0, 32, 32), ignoreSize=True)
            mainIcon.hint = [label, iconhint][(len(iconhint) > 0)]
            statusLabel = uicls.Label(text='', parent=row, left=mainIcon.left + mainIcon.width, linespace=10, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
            statusLabel.hint = [label, labelhint][(len(labelhint) > 0)]
            dsp.sr.Set('%sStatusText' % what, statusLabel)
            if what != 'effectiveHp':
                uicls.Line(parent=row, align=uiconst.RELATIVE, color=lineColor, left=col1Width, height=31, width=1, top=1)
                left = col1Width
                for (i, attribute,) in enumerate(resAttrs):
                    gaugePar = uicls.Container(parent=row, align=uiconst.CENTERLEFT, width=step - 6, height=12, left=left + 3)
                    gaugePar.hint = attribute.displayName
                    gaugePar.state = uiconst.UI_NORMAL
                    gauge = uicls.Fill(parent=gaugePar, align=uiconst.TOLEFT, width=36, color=barColors[i])
                    fillColor = (barColors[i][0],
                     barColors[i][1],
                     barColors[i][2],
                     0.2)
                    uicls.Fill(parent=gaugePar, color=fillColor)
                    dsp.sr.Set(('%sGauge' % what, attribute.attributeID), gauge)
                    statusLabel = uicls.Label(text='0%', parent=gaugePar, left=6, fontsize=10, state=uiconst.UI_DISABLED, idx=0, align=uiconst.CENTERLEFT)
                    dsp.sr.Set(('%sGaugeLabel' % what, attribute.attributeID), statusLabel)
                    gaugePar.height = max(12, statusLabel.textheight + 2)
                    left += step

            row.sr.backgroundFrame = uicls.BumpedUnderlay(parent=row, padding=(-1, -1, -1, -1))

        if not initialLoad:
            self.UpdateStats()



    def LoadCapacitorStats(self, initialLoad = False):
        uix.Flush(self.sr.capacitorStatsParent)
        lineColor = (1.0, 1.0, 1.0, 0.125)
        left = 0
        self.sr.capacitorStatsParent.sr.powerCore = uicls.Container(parent=self.sr.capacitorStatsParent, name='powercore', pos=(4, 6, 45, 45), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        csp = self.sr.capacitorStatsParent
        label = uicls.Label(text='', parent=csp, idx=0, state=uiconst.UI_NORMAL, top=-16, left=56, align=uiconst.CENTERLEFT)
        label.hint = mls.UI_FITTING_CAPACITOR_CHARGERATE
        self.sr.capacitorStatsParent.sr.statusText = label
        label = uicls.Label(text='', parent=csp, idx=0, state=uiconst.UI_NORMAL, top=0, left=56, align=uiconst.CENTERLEFT)
        label.hint = mls.UI_FITTING_EXCESSCAPACITORRECHARGERATE
        self.sr.capacitorStatsParent.sr.delta = label
        label = uicls.Label(text='', parent=csp, idx=0, state=uiconst.UI_NORMAL, top=16, left=56, align=uiconst.CENTERLEFT)
        self.sr.capacitorStatsParent.sr.sustainable = label
        self.sr.capacitorStatsParent.sr.backgroundFrame = uicls.BumpedUnderlay(parent=self.sr.capacitorStatsParent, padding=(-1, 2, -1, -1))
        self.UpdateCapacitor(reload=1)
        if not initialLoad:
            self.UpdateStats()



    def GetModules(self, parentContainer):
        hangarInv = eve.GetInventory(const.containerHangar)
        items = hangarInv.List()

        def Filter(item):
            if item.categoryID not in (const.categoryModule, const.categorySubSystem):
                return True
            return not sm.StartService('godma').CheckSkillRequirementsForType(item.typeID)


        assets = []
        for each in items:
            if Filter(each):
                continue
            assets.append(listentry.Get('InvFittingItem', data=uix.GetItemData(each, 'details', container=parentContainer)))

        if not len(assets):
            assets.append(listentry.Get('Generic', {'label': mls.UI_GENERIC_NOTHINGTOFIT,
             'hint': '',
             'OnDropData': parentContainer.OnDropData,
             'hideLines': 1}))
        return (assets, 'label')



    def GetCharges(self, parentContainer):
        hangarInv = eve.GetInventory(const.containerHangar)
        items = hangarInv.List()

        def Filter(item):
            if item.categoryID != const.categoryCharge:
                return True
            return False


        assets = []
        for each in items:
            if Filter(each):
                continue
            assets.append(listentry.Get('InvFittingItem', data=uix.GetItemData(each, 'details', container=parentContainer)))

        if not len(assets):
            assets.append(listentry.Get('Generic', {'label': mls.UI_GENERIC_NOCHARGESTOFIT,
             'hint': '',
             'OnDropData': parentContainer.OnDropData,
             'hideLines': 1}))
        return (assets, 'label')



    def GetDrones(self, parentContainer):
        shipInv = self.GetShipInventory()
        drones = shipInv.ListDroneBay()

        def Filter(item):
            if item.categoryID != const.categoryDrone:
                return True
            return False


        assets = []
        for each in drones:
            if Filter(each):
                continue
            data = uix.GetItemData(each, 'details', container=parentContainer)
            data.showFitIcon = False
            assets.append(listentry.Get('InvFittingItem', data=data))

        if not len(assets):
            assets.append(listentry.Get('Generic', {'label': mls.UI_GENERIC_NODRONESINSHIP,
             'OnDropData': parentContainer.OnDropData,
             'hideLines': 1}))
        return (assets, 'label')



    def GetCargo(self, parentContainer):
        shipInv = self.GetShipInventory()
        drones = shipInv.ListCargo()
        assets = []
        for each in drones:
            data = uix.GetItemData(each, 'details', container=parentContainer)
            assets.append(listentry.Get('InvFittingItem', data=data))

        if not len(assets):
            assets.append(listentry.Get('Generic', {'label': mls.UI_GENERIC_NOTHINGINCARGOHOLD,
             'OnDropData': parentContainer.OnDropData,
             'hideLines': 1}))
        return (assets, 'label')



    def GetShipInventory(self):
        return sm.GetService('invCache').GetInventoryFromId(self.shipID, locationID=session.stationid2)



    def UpdateStats(self, typeID = None, item = None):
        if typeID:
            typeOb = cfg.invtypes.Get(typeID)
            if not cfg.IsFittableCategory(typeOb.categoryID):
                return 
        self.updateStatsArgs = (typeID, item)
        if self.updateStatsThread is not None:
            return 
        self.updateStatsThread = uthread.pool('Fitting::UpdateStats', self._UpdateStats)



    def _UpdateStats(self):
        try:
            blue.pyos.synchro.Sleep(100)

        finally:
            self.updateStatsThread = None

        (typeID, item,) = self.updateStatsArgs
        if self is None or self.destroyed or not hasattr(self, 'sr') or not self.initialized:
            return 
        if session.stationid2:
            if util.GetAttrs(self, 'sr', 'stripBtn'):
                self.sr.stripBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.stripBtn.state = uiconst.UI_HIDDEN
        xtraArmor = 0.0
        multiplyArmor = 1.0
        multiplyPower = 1.0
        xtraPower = 0.0
        xtraPowerload = 0.0
        multiplyCpu = 1.0
        xtraCpuLoad = 0.0
        xtraCpu = 0.0
        multiplyRecharge = 1.0
        xtraCapacitor = 0.0
        multiplyCapacitor = 1.0
        multiplyShieldRecharge = 1.0
        multiplyShieldCapacity = 1.0
        xtraShield = 0.0
        hpDrawback = 1.0
        multiplyStructure = 1.0
        xtraStructure = 0.0
        multiplyCargoCapacity = 1.0
        multiplySpeed = 1.0
        xtraSpeed = 0.0
        multiplyMaxTargetRange = 1.0
        multiplyCalibration = 1.0
        xtraCalibrationLoad = 0.0
        xtraCalibrationOutput = 0.0
        xtraCargoSpace = 1.0
        xtraDroneSpace = 1.0
        multiplyResonance = {}
        multiplyResistance = {}
        sensorStrengthAttrs = [const.attributeScanRadarStrength,
         const.attributeScanMagnetometricStrength,
         const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrength]
        sensorStrengthPercent = {}
        sensorStrengthPercentAttrs = [const.attributeScanRadarStrengthBonus,
         const.attributeScanMagnetometricStrengthBonus,
         const.attributeScanGravimetricStrengthBonus,
         const.attributeScanLadarStrengthBonus]
        sensorStrengthBonus = {}
        sensorStrengthBonusAttrs = [const.attributeScanRadarStrengthPercent,
         const.attributeScanMagnetometricStrengthPercent,
         const.attributeScanGravimetricStrengthPercent,
         const.attributeScanLadarStrengthPercent]
        ship = self.GetShipDogmaItem()
        modulesByGroupInShip = {}
        for module in ship.GetFittedItems().itervalues():
            if module.groupID not in modulesByGroupInShip:
                modulesByGroupInShip[module.groupID] = []
            modulesByGroupInShip[module.groupID].append(module)

        typeAttributesByID = {}
        if typeID:
            for attribute in cfg.dgmtypeattribs.get(typeID, []):
                typeAttributesByID[attribute.attributeID] = attribute.value

            dgmAttr = sm.GetService('godma').GetType(typeID)
            asm = self.ArmorOrShieldMultiplier(typeID)
            asp = self.ArmorShieldStructureMultiplierPostPercent(typeID)
            mtr = self.MaxTargetRangeBonusMultiplier(typeID)
            doHilite = dgmAttr.groupID not in self._nohilitegroups
            allowedAttr = dgmAttr.displayAttributes
            for attribute in allowedAttr:
                if not doHilite and attribute.attributeID not in self._nohilitegroups[dgmAttr.groupID]:
                    continue
                if attribute.attributeID in sensorStrengthBonusAttrs:
                    sensorStrengthBonus[attribute.attributeID] = attribute
                elif attribute.attributeID in sensorStrengthPercentAttrs:
                    sensorStrengthPercent[attribute.attributeID] = attribute
                elif attribute.attributeID == const.attributeCapacityBonus:
                    xtraShield += attribute.value
                elif attribute.attributeID == const.attributeArmorHPBonusAdd:
                    xtraArmor += attribute.value
                elif attribute.attributeID == const.attributeStructureBonus:
                    xtraStructure += attribute.value
                elif attribute.attributeID == const.attributeCapacitorBonus:
                    xtraCapacitor += attribute.value
                elif attribute.attributeID == const.attributeCapacitorCapacityMultiplier:
                    multiplyCapacitor *= attribute.value
                elif attribute.attributeID == const.attributeCapacitorCapacityBonus:
                    multiplyCapacitor = 1 + attribute.value / 100
                elif attribute.attributeID == const.attributeCpuMultiplier:
                    multiplyCpu = attribute.value
                elif attribute.attributeID == const.attributeCpuOutput:
                    xtraCpu += attribute.value
                elif attribute.attributeID == const.attributePowerOutputMultiplier:
                    multiplyPower = attribute.value
                elif attribute.attributeID == const.attributePowerEngineeringOutputBonus:
                    multiplyPower = 1 + attribute.value / 100
                elif attribute.attributeID == const.attributeArmorHpBonus:
                    multiplyArmor += attribute.value / 100
                elif attribute.attributeID == const.attributeArmorHPMultiplier:
                    multiplyArmor = attribute.value
                elif attribute.attributeID == const.attributePowerIncrease:
                    xtraPower = attribute.value
                elif attribute.attributeID == const.attributePowerOutput:
                    xtraPower = attribute.value
                elif attribute.attributeID in (const.attributeCpuLoad, const.attributeCpu):
                    xtraCpuLoad += attribute.value
                elif attribute.attributeID in (const.attributePowerLoad, const.attributePower):
                    xtraPowerload += attribute.value
                elif attribute.attributeID == const.attributeUpgradeCost:
                    xtraCalibrationLoad = attribute.value
                elif attribute.attributeID == const.attributeCargoCapacityMultiplier:
                    xtraCargoSpace = attribute.value
                elif attribute.attributeID == const.attributeDroneCapacity:
                    xtraDroneSpace = attribute.value
                elif attribute.attributeID == const.attributeMaxVelocityBonus:
                    multiplySpeed = attribute.value
                elif asm is not None and attribute.attributeID == const.attributeEmDamageResonanceMultiplier:
                    multiplyResonance['%s_EmDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == const.attributeExplosiveDamageResonanceMultiplier:
                    multiplyResonance['%s_ExplosiveDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == const.attributeKineticDamageResonanceMultiplier:
                    multiplyResonance['%s_KineticDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == const.attributeThermalDamageResonanceMultiplier:
                    multiplyResonance['%s_ThermalDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asp and attribute.attributeID in (const.attributeEmDamageResistanceBonus,
                 const.attributeExplosiveDamageResistanceBonus,
                 const.attributeKineticDamageResistanceBonus,
                 const.attributeThermalDamageResistanceBonus):
                    groupName = {const.attributeEmDamageResistanceBonus: 'EmDamageResistance',
                     const.attributeExplosiveDamageResistanceBonus: 'ExplosiveDamageResistance',
                     const.attributeKineticDamageResistanceBonus: 'KineticDamageResistance',
                     const.attributeThermalDamageResistanceBonus: 'ThermalDamageResistance'}.get(attribute.attributeID, '')
                    if 'armor' in asp:
                        multiplyResistance['a_%s' % groupName] = attribute.value
                    if 'shield' in asp:
                        multiplyResistance['s_%s' % groupName] = attribute.value
                    if 'structure' in asp:
                        multiplyResistance['h_%s' % groupName] = attribute.value
                elif attribute.attributeID == const.attributeCapacitorRechargeRateMultiplier:
                    multiplyRecharge = multiplyRecharge * attribute.value
                elif attribute.attributeID == const.attributeCapRechargeBonus:
                    multiplyRecharge = 1 + attribute.value / 100
                elif attribute.attributeID == const.attributeShieldRechargeRateMultiplier:
                    multiplyShieldRecharge = attribute.value
                elif attribute.attributeID == const.attributeShieldCapacityMultiplier:
                    multiplyShieldCapacity *= attribute.value
                elif attribute.attributeID == const.attributeStructureHPMultiplier:
                    multiplyStructure = attribute.value
                elif attribute.attributeID == const.attributeCargoCapacityMultiplier:
                    multiplyCargoCapacity = attribute.value
                elif attribute.attributeID == const.attributeMaxTargetRangeMultiplier:
                    multiplyMaxTargetRange = attribute.value
                elif mtr is not None and attribute.attributeID == const.attributeMaxTargetRangeBonus:
                    multiplyMaxTargetRange = abs(1.0 + attribute.value / 100.0)

        resAttrs = [const.attributeEmDamageResonance,
         const.attributeExplosiveDamageResonance,
         const.attributeKineticDamageResonance,
         const.attributeThermalDamageResonance]
        effectiveHp = 0.0
        effectiveHpColor = FONTCOLOR_DEFAULT
        dsp = util.GetAttrs(self, 'sr', 'defenceStatsParent')
        if not dsp or dsp.destroyed:
            return 
        resMap = {'structure': 'h',
         'armor': 'a',
         'shield': 's'}
        for (what, suffix, attrname, idx, alt, altm,) in (('structure',
          mls.UI_GENERIC_FITTING_HP,
          'hp',
          0,
          xtraStructure,
          multiplyStructure), ('armor',
          mls.UI_GENERIC_FITTING_HP,
          'armorHP',
          0,
          xtraArmor,
          multiplyArmor), ('shield',
          mls.UI_GENERIC_FITTING_HP,
          'shieldCapacity',
          1,
          xtraShield,
          multiplyShieldCapacity)):
            attrID = self.dogmaLocation.dogmaStaticMgr.attributesByName[attrname].attributeID
            status = self.GetShipAttribute(attrID)
            if not status:
                continue
            label = dsp.sr.Get('%sStatusText' % what, None)
            if label:
                if what in ('armor', 'structure') and altm > 1.0:
                    status = status * altm
                    label.text = '%s%i %s' % (self.GetMultiplyColor(altm / 100), status, suffix)
                else:
                    status = (alt + status) * altm
                    label.text = '%s%i %s' % (self.GetColor(alt, altm), status, suffix)
                if what == 'shield':
                    label.text += '<br>%s%i %s' % (self.GetMultiplyColor(multiplyShieldRecharge), self.GetShipAttribute(const.attributeShieldRechargeRate) * multiplyShieldRecharge * 0.001, mls.UI_GENERIC_SECONDVERYSHORT.lower())
            minResistance = 0.0
            for (i, res,) in enumerate(['EmDamageResonance',
             'ExplosiveDamageResonance',
             'KineticDamageResonance',
             'ThermalDamageResonance']):
                shipmod = '%s_%s' % (resMap[what], res)
                modmod = '%s_%s' % (resMap[what], res.replace('Resonance', 'Resistance'))
                multiplierShip = multiplyResonance.get(shipmod, 0.0)
                multiplierMod = multiplyResistance.get(modmod, 0.0)
                attribute = '%s%s' % ([what, ''][(what == 'structure')], res)
                attribute = attribute[0].lower() + attribute[1:]
                attributeID = self.dogmaLocation.dogmaStaticMgr.attributesByName[attribute].attributeID
                value = self.GetShipAttribute(attributeID)
                if multiplierMod != 0.0:
                    effectiveHpColor = FONTCOLOR_HILITE
                if value is not None:
                    value = value + value * multiplierMod / 100
                    if dsp.state != uiconst.UI_HIDDEN:
                        gauge = dsp.sr.Get(('%sGauge' % what, resAttrs[i]), None)
                        gaugeLabel = dsp.sr.Get(('%sGaugeLabel' % what, resAttrs[i]), None)
                        if gauge:
                            self.UpdateGauge(gauge, 1.0 - value)
                        if gaugeLabel:
                            gaugeLabel.text = '%s<b>%s%%</b>' % (self.GetColor(multiplierMod), util.FmtAmt(100 - int(value * 100)))
                    minResistance = max(minResistance, value)

            if minResistance:
                effectiveHp += status / minResistance
            if multiplyStructure != 1.0:
                effectiveHpColor = FONTCOLOR_HILITE

        self.sr.defenceHeaderStatsParent.sr.statusText.text = '%s%d %s' % (effectiveHpColor, effectiveHp, mls.UI_GENERIC_FITTING_HPEFFECTIVE)
        effectiveHpLabel = dsp.sr.Get('effectiveHpStatusText', None)
        if label:
            effectiveHpLabel.text = self.sr.defenceHeaderStatsParent.sr.statusText.text
        activeRepairLabel = dsp.sr.Get('activeBestRepairLabel', None)
        activeBestRepairParent = dsp.sr.Get('activeBestRepairParent', None)
        activeBestRepairNumLabel = dsp.sr.Get('activeBestRepairNumLabel', None)
        activeBestRepairIcon = dsp.sr.Get('activeBestRepairIcon', None)
        if activeRepairLabel:
            activeBestRepair = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
            if activeBestRepair == PASSIVESHIELDRECHARGE:
                shieldCapacity = self.GetShipAttribute(const.attributeShieldCapacity)
                shieldRR = self.GetShipAttribute(const.attributeShieldRechargeRate)
                activeRepairLabel.text = '%s%s %s' % (self.GetMultiplyColor(multiplyShieldRecharge), util.FmtAmt(shieldCapacity * multiplyShieldCapacity / (shieldRR * multiplyShieldRecharge / 1000.0) * 2.5), mls.UI_GENERIC_FITTING_HPPERSEC)
                activeBestRepairParent.hint = mls.UI_FITTING_PASSIVE_SHIELD_RECHARGE
                activeBestRepairNumLabel.parent.state = uiconst.UI_HIDDEN
                activeBestRepairIcon.LoadIcon(cfg.dgmattribs.Get(const.attributeShieldCapacity).iconID, ignoreSize=True)
            else:
                dataSet = {ARMORREPAIRRATEACTIVE: (mls.UI_FITTING_ARMOR_REPAIR_RATE_ACTIVE,
                                         const.groupArmorRepairUnit,
                                         const.attributeArmorDamageAmount,
                                         'ui_1_64_11'),
                 HULLREPAIRRATEACTIVE: (mls.UI_FITTING_HULL_REPAIR_RATE_ACTIVE,
                                        const.groupHullRepairUnit,
                                        const.attributeStructureDamageAmount,
                                        'ui_1_64_11'),
                 SHIELDBOOSTRATEACTIVE: (mls.UI_FITTING_SHIELD_BOOST_RATE_ACTIVE,
                                         const.groupShieldBooster,
                                         const.attributeShieldBonus,
                                         'ui_2_64_3')}
                (hint, groupID, attributeID, iconNum,) = dataSet[activeBestRepair]
                dgmAttrib = cfg.dgmattribs.Get(attributeID)
                activeBestRepairParent.hint = hint
                modules = modulesByGroupInShip.get(groupID, None)
                color = FONTCOLOR_DEFAULT
                if item and item.groupID == groupID:
                    if modules:
                        modules += [item]
                    else:
                        modules = [item]
                    color = FONTCOLOR_HILITE
                if modules:
                    data = self.CollectDogmaAttributes(modules, (const.attributeHp,
                     const.attributeShieldBonus,
                     const.attributeArmorDamageAmount,
                     const.attributeStructureDamageAmount,
                     const.attributeDuration))
                    durations = data.get(const.attributeDuration, None)
                    hps = data.get(attributeID, None)
                    if durations and hps:
                        commonCycleTime = None
                        for _ct in durations:
                            if commonCycleTime and _ct != commonCycleTime:
                                commonCycleTime = None
                                break
                            commonCycleTime = _ct

                        if commonCycleTime:
                            duration = commonCycleTime
                            activeRepairLabel.text = '%s%0.2f %s<br>%s %s' % (color,
                             sum(hps),
                             mls.UI_GENERIC_FITTING_HP,
                             duration / 1000.0,
                             mls.UI_GENERIC_SECONDVERYSHORT.lower())
                        else:
                            total = 0
                            for (i, ct,) in enumerate(durations):
                                if i >= len(hps):
                                    return 
                                total += hps[i] / (ct / 1000.0)

                        activeRepairLabel.text = '%s%d %s' % (color, total, mls.UI_GENERIC_FITTING_HPPERSEC)
                    activeBestRepairNumLabel.text = '%s<b>%s</b>' % (color, len(modules))
                    activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
                else:
                    activeRepairLabel.text = mls.UI_GENERIC_FITTING_NOMODULE
                    activeBestRepairNumLabel.text = '<b>0</b>'
                    activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
                activeBestRepairIcon.LoadIcon(iconNum, ignoreSize=True)
        turretAddition = 0
        launcherAddition = 0
        hiSlotAddition = 0
        medSlotAddition = 0
        lowSlotAddition = 0
        if self.shipID:
            godma = sm.StartService('godma')
            stateMgr = godma.GetStateManager()
            ship = godma.GetItem(self.shipID)
            subSystemSlot = typeAttributesByID.get(const.attributeSubSystemSlot, None)
            if subSystemSlot is not None:
                slotOccupant = self.dogmaLocation.GetSubSystemInFlag(self.shipID, int(subSystemSlot))
                if slotOccupant is not None:
                    attributesByName = self.dogmaLocation.dogmaStaticMgr.attributesByName
                    GTA = lambda attributeID: self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(slotOccupant.typeID, attributeID)
                    turretAddition = -GTA(attributesByName['turretHardPointModifier'].attributeID)
                    launcherAddition = -GTA(attributesByName['launcherHardPointModifier'].attributeID)
                    hiSlotAddition = -GTA(attributesByName['hiSlotModifier'].attributeID)
                    medSlotAddition = -GTA(attributesByName['medSlotModifier'].attributeID)
                    lowSlotAddition = -GTA(attributesByName['lowSlotModifier'].attributeID)
        turretAddition += typeAttributesByID.get(const.attributeTurretHardpointModifier, 0.0)
        turretSlotsLeft = self.GetShipAttribute(const.attributeTurretSlotsLeft)
        for (i, slot,) in enumerate(self.sr.turretSlots):
            if i < turretSlotsLeft:
                if i < turretSlotsLeft + turretAddition:
                    slot.color.SetRGB(1.0, 1.0, 1.0)
                    slot.LoadIcon('ui_73_16_194')
                else:
                    slot.color.SetRGB(1.0, 0.0, 0.0)
                    slot.LoadIcon('ui_73_16_194')
            elif i < turretSlotsLeft + turretAddition:
                slot.color.SetRGB(1.0, 1.0, 0.0)
                slot.LoadIcon('ui_73_16_194')
            else:
                slot.color.SetRGB(1.0, 1.0, 1.0)
                slot.LoadIcon('ui_73_16_193')

        launcherAddition += typeAttributesByID.get(const.attributeLauncherHardPointModifier, 0.0)
        launcherSlotsLeft = self.GetShipAttribute(const.attributeLauncherSlotsLeft)
        for (i, slot,) in enumerate(self.sr.launcherSlots):
            if i < launcherSlotsLeft:
                if i < launcherSlotsLeft + launcherAddition:
                    slot.color.SetRGB(1.0, 1.0, 1.0)
                    slot.LoadIcon('ui_73_16_194')
                else:
                    slot.color.SetRGB(1.0, 0.0, 0.0)
                    slot.LoadIcon('ui_73_16_194')
            elif i < launcherSlotsLeft + launcherAddition:
                slot.color.SetRGB(1.0, 1.0, 0.0)
                slot.LoadIcon('ui_73_16_194')
            else:
                slot.color.SetRGB(1.0, 1.0, 1.0)
                slot.LoadIcon('ui_73_16_193')

        hiSlotAddition += typeAttributesByID.get(const.attributeHiSlotModifier, 0.0)
        medSlotAddition += typeAttributesByID.get(const.attributeMedSlotModifier, 0.0)
        lowSlotAddition += typeAttributesByID.get(const.attributeLowSlotModifier, 0.0)
        self.ShowAddition(hiSlotAddition, medSlotAddition, lowSlotAddition)
        massLabel = self.sr.Get(('StatsLabel', const.attributeMass), None)
        if massLabel:
            massAddition = typeAttributesByID.get(const.attributeMassAddition, 0.0)
            mass = self.GetShipAttribute(const.attributeMass)
            value = mass + massAddition
            suffix = 'kg'
            if value > 10000.0:
                value = value / 1000.0
                suffix = 't'
            massLabel.text = '%s%s %s' % (self.GetXtraColor(massAddition), util.FmtAmt(value), suffix)
        maxVelocityLabel = self.sr.Get(('StatsLabel', const.attributeMaxVelocity), None)
        if maxVelocityLabel:
            xtraSpeed = typeAttributesByID.get(const.attributeSpeedBonus, 0.0) + typeAttributesByID.get(const.attributeMaxVelocity, 0.0)
            multiplyVelocity = typeAttributesByID.get(const.attributeVelocityModifier, None)
            if multiplyVelocity is not None:
                multiplyVelocity = 1 + multiplyVelocity / 100 * multiplySpeed
            else:
                multiplyVelocity = 1.0 * multiplySpeed
            maxVelocity = self.GetShipAttribute(const.attributeMaxVelocity)
            maxVelocityLabel.text = '%s%d %s' % (self.GetColor(xtraSpeed, multiplyVelocity), (maxVelocity + xtraSpeed) * multiplyVelocity, mls.UI_GENERIC_MPERS)
        agilityLabel = self.sr.Get(('StatsLabel', const.attributeAgility), None)
        if agilityLabel:
            agility = self.GetShipAttribute(const.attributeAgility)
            agilityLabel.text = '%.4fx' % agility
        baseWarpSpeedLabel = self.sr.Get(('StatsLabel', const.attributeBaseWarpSpeed), None)
        if baseWarpSpeedLabel:
            baseWarpSpeed = self.GetShipAttribute(const.attributeBaseWarpSpeed)
            warpSpeedMultiplier = self.GetShipAttribute(const.attributeWarpSpeedMultiplier)
            baseWarpSpeedLabel.text = '%s/%s' % (util.FmtDist(baseWarpSpeed * warpSpeedMultiplier * 3 * const.AU, 2), cfg.dgmunits.Get(const.unitMilliseconds).displayName)
        xtraLockedTargets = typeAttributesByID.get(const.attributeMaxLockedTargetsBonus, 0.0)
        maxLockedTargets = self.GetShipAttribute(const.attributeMaxLockedTargets)
        self.sr.targetingStatsParent.parent.parent.SetHeader(' %s(%ix)' % (self.GetXtraColor(xtraLockedTargets), maxLockedTargets + xtraLockedTargets), addon=1, hint=mls.UI_FITTING_MAXLOCKEDTARGETS + ': %d' % (maxLockedTargets + xtraLockedTargets))
        multiplyScanResolution = typeAttributesByID.get(const.attributeScanResolutionMultiplier, 1.0)
        if const.attributeScanResolutionBonus in typeAttributesByID:
            multiplyScanResolution *= 1 + typeAttributesByID[const.attributeScanResolutionBonus] / 100
        scanResolution = self.GetShipAttribute(const.attributeScanResolution)
        srt = '%s%i mm' % (self.GetMultiplyColor(multiplyScanResolution), scanResolution * multiplyScanResolution)
        statsLabel = self.sr.targetingStatsParent.sr.Get(('StatsLabel', const.attributeScanResolution), None)
        if statsLabel:
            statsLabel.text = srt
        maxTargetRange = self.GetShipAttribute(const.attributeMaxTargetRange)
        mtrt = '%s%i %s' % (self.GetMultiplyColor(multiplyMaxTargetRange), maxTargetRange * multiplyMaxTargetRange, mls.UI_GENERIC_METERSSHORT)
        statsLabel = self.sr.targetingStatsParent.sr.Get(('StatsLabel', const.attributeMaxTargetRange), None)
        if statsLabel:
            statsLabel.text = mtrt
        self.sr.targetingHeaderStatsParent.sr.statusText.text = srt + ' |' + mtrt
        (sensorStrengthAttributeID, maxSensorStrength,) = self.GetSensorStrengthAttribute()
        maxSensor = cfg.dgmattribs.Get(sensorStrengthAttributeID)
        attrIdx = sensorStrengthAttrs.index(maxSensor.attributeID)
        sensorBonusAttributeID = sensorStrengthBonusAttrs[attrIdx]
        sensorPercentAttributeID = sensorStrengthPercentAttrs[attrIdx]
        ssB = sensorStrengthBonus.get(sensorBonusAttributeID, None)
        ssP = sensorStrengthPercent.get(sensorPercentAttributeID, None)
        ssBValue = 1.0
        ssPValue = 1.0
        if ssB:
            ssBValue = 1.0 + ssB.value / 100.0
        if ssP:
            ssPValue = 1.0 + ssP.value / 100.0
        statsLabel = self.sr.targetingStatsParent.sr.Get(('StatsLabel', 'sensorStrength'), None)
        if statsLabel:
            statsLabel.text = '%s%s' % (self.GetColor(multi=(ssBValue + ssPValue) / 2.0), sm.GetService('info').GetFormatAndValue(maxSensor, maxSensorStrength * ssBValue * ssPValue))
            statsLabel.hint = maxSensor.displayName
        statsIcon = self.sr.targetingStatsParent.sr.Get(('StatsIcon', 'sensorStrength'), None)
        if statsIcon:
            statsIcon.hint = maxSensor.displayName
            statsIcon.LoadIcon(maxSensor.iconID, ignoreSize=True)
        signatureRadiusLabel = self.sr.targetingStatsParent.sr.Get(('StatsLabel', const.attributeSignatureRadius), None)
        if signatureRadiusLabel:
            signatureRadius = self.GetShipAttribute(const.attributeSignatureRadius)
            signatureRadiusAdd = typeAttributesByID.get(const.attributeSignatureRadiusAdd, 0.0)
            signatureRadiusLabel.text = '%s%i %s' % (self.GetXtraColor(signatureRadiusAdd), signatureRadius + signatureRadiusAdd, mls.UI_GENERIC_METERSSHORT)
        maxLockedTargetsLabel = self.sr.targetingStatsParent.sr.Get(('StatsLabel', const.attributeMaxLockedTargets), None)
        if maxLockedTargetsLabel:
            maxLockedTargets = self.GetShipAttribute(const.attributeMaxLockedTargets)
            maxLockedTargetsAdd = xtraLockedTargets
            maxLockedTargetsLabel.text = '%s%i' % (self.GetXtraColor(xtraLockedTargets), maxLockedTargets + maxLockedTargetsAdd)
        self.UpdateCapacitor(xtraCapacitor, multiplyRecharge, multiplyCapacitor, reload=1)
        self.UpdateCPUandPowerload(multiplyCpu, xtraCpuLoad, xtraCpu, xtraPower, multiplyPower, xtraPowerload)
        self.UpdateCalibration(multiplyCalibration, xtraCalibrationLoad, xtraCalibrationOutput)
        self.UpdateCargoDroneInfo(xtraCargoSpace, xtraDroneSpace)



    def ShowAddition(self, h, m, l):
        key = ['Hi', 'Med', 'Lo']
        for (gidx, attributeID,) in enumerate((const.attributeHiSlots, const.attributeMedSlots, const.attributeLowSlots)):
            totalslots = self.GetShipAttribute(attributeID)
            add = [h, m, l][gidx]
            modslots = add + totalslots
            for sidx in xrange(8):
                flag = getattr(const, 'flag%sSlot%s' % (key[gidx], sidx))
                slot = self.slots[flag]
                if sidx < modslots:
                    if sidx >= totalslots:
                        slot.ColorUnderlay((1.0, 1.0, 0.0))
                        slot.Hilite(1)
                        slot.opacity = 1.0
                    else:
                        slot.ColorUnderlay()
                        if slot.state == uiconst.UI_DISABLED:
                            slot.opacity = 0.25
                        else:
                            slot.opacity = 1.0
                elif sidx >= totalslots:
                    slot.ColorUnderlay()
                    if slot.state == uiconst.UI_DISABLED:
                        slot.opacity = 0.25
                    else:
                        slot.opacity = 1.0
                else:
                    slot.ColorUnderlay((1.0, 0.0, 0.0))
                    slot.Hilite(1)
                    slot.opacity = 1.0





    def CollectDogmaAttributes(self, modules, attributes):
        ret = {}
        for module in modules:
            info = sm.GetService('godma').GetItem(module.itemID)
            if info:
                for dgmAttribute in info.displayAttributes:
                    if dgmAttribute.attributeID in attributes:
                        if dgmAttribute.attributeID not in ret:
                            ret[dgmAttribute.attributeID] = []
                        ret[dgmAttribute.attributeID].append(dgmAttribute.value)

            else:
                for dgmAttribute in cfg.dgmtypeattribs.get(module.typeID, []):
                    if dgmAttribute.attributeID in attributes:
                        if dgmAttribute.attributeID not in ret:
                            ret[dgmAttribute.attributeID] = []
                        ret[dgmAttribute.attributeID].append(dgmAttribute.value)


        return ret



    def UpdateCenterShapePosition(self):
        (l, t, w, h,) = self.sr.wnd.GetAbsolute()
        lastLeft = getattr(self, '_lastLeftPanelWidth', None)
        self.sr.wnd.width = self._leftPanelWidth + self._centerOnlyWidth + self._rightPanelWidth
        if lastLeft is not None and lastLeft != self._leftPanelWidth:
            self.sr.wnd.left += lastLeft - self._leftPanelWidth
        self.left = self._leftPanelWidth
        self._lastLeftPanelWidth = self._leftPanelWidth
        self.sr.wnd._fixedWidth = self.sr.wnd.width
        self.sr.wnd._fixedHeight = self.sr.wnd.height



    def ToggleLeft(self, *args):
        current = settings.user.ui.Get('fittingPanelLeft', 1)
        settings.user.ui.Set('fittingPanelLeft', not current)
        uthread.new(self._ToggleSidePanel, 'left')



    def ToggleRight(self, *args):
        current = settings.user.ui.Get('fittingPanelRight', 1)
        settings.user.ui.Set('fittingPanelRight', not current)
        uthread.new(self._ToggleSidePanel, 'right')



    def _ToggleSidePanel(self, side):
        current = settings.user.ui.Get('fittingPanel%s' % side.capitalize(), 1)
        if current:
            endOpacity = 1.0
        else:
            endOpacity = 0.0
        panel = self.sr.Get('%sPanel' % side.lower(), None)
        btn = self.sr.Get('toggle%sBtn' % side.capitalize(), None)
        btn.state = uiconst.UI_DISABLED
        if side == 'left':
            begWidth = self._leftPanelWidth
            if current:
                self.sr.toggleLeftBtn.LoadIcon('ui_73_16_196')
            else:
                self.sr.toggleLeftBtn.LoadIcon('ui_73_16_195')
        else:
            begWidth = self._rightPanelWidth
            if current:
                self.sr.toggleRightBtn.LoadIcon('ui_73_16_195')
            else:
                self.sr.toggleRightBtn.LoadIcon('ui_73_16_196')
        if current:
            endWidth = self._fullPanelWidth
        else:
            endWidth = 0
        if panel:
            if endOpacity == 0.0:
                uicore.effect.MorphUI(panel, 'opacity', endOpacity, time=250.0, float=1, newthread=0)
                panel.state = uiconst.UI_DISABLED
            time = 250.0
            start = blue.os.GetTime()
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                if side == 'left':
                    self._leftPanelWidth = int(mathUtil.Lerp(begWidth, endWidth, ndt))
                else:
                    self._rightPanelWidth = int(mathUtil.Lerp(begWidth, endWidth, ndt))
                self.UpdateCenterShapePosition()
                blue.pyos.synchro.Yield()

            if endOpacity == 1.0:
                uicore.effect.MorphUI(panel, 'opacity', endOpacity, time=250.0, float=1)
                panel.state = uiconst.UI_PICKCHILDREN
        btn.state = uiconst.UI_NORMAL



    def RefreshChildren(self, parent):
        valid = [ each for each in parent.Find('trinity.Tr2Sprite2dContainer') if hasattr(each, '_OnResize') ]
        for each in valid:
            each._OnResize()




    def UpdateGauge(self, gauge, portion):
        (l, t, w, h,) = gauge.parent.GetAbsolute()
        new = int(w * portion)
        uicore.effect.MorphUI(gauge, 'width', new, 100.0, ifWidthConstrain=0)



    def MaxTargetRangeBonusMultiplier(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        for effect in typeeffects:
            if effect.effectID in (const.effectShipMaxTargetRangeBonusOnline, const.effectmaxTargetRangeBonus):
                return 1




    def ArmorOrShieldMultiplier(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        for effect in typeeffects:
            if effect.effectID == const.effectShieldResonanceMultiplyOnline:
                return 1




    def ArmorShieldStructureMultiplierPostPercent(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        ret = []
        for effect in typeeffects:
            if effect.effectID == const.effectModifyArmorResonancePostPercent:
                ret.append('armor')
            elif effect.effectID == const.effectModifyShieldResonancePostPercent:
                ret.append('shield')
            elif effect.effectID == const.effectModifyHullResonancePostPercent:
                ret.append('structure')

        return ret



    def GetXtraColor(self, xtra):
        if xtra != 0.0:
            return FONTCOLOR_HILITE
        return FONTCOLOR_DEFAULT



    def GetMultiplyColor(self, multiply):
        if multiply != 1.0:
            return FONTCOLOR_HILITE
        return FONTCOLOR_DEFAULT



    def GetColor(self, xtra = 0.0, multi = 1.0):
        if multi != 1.0 or xtra != 0.0:
            return FONTCOLOR_HILITE
        return FONTCOLOR_DEFAULT



    def UpdateCalibration(self, caliMultiply = 1.0, caliXtraLoad = 0.0, caliXtraCapacity = 0.0):
        if self.shipID is None:
            lg.Error('fitting', 'UpdateCalibration with no ship')
            return 
        calibrationLoad = self.GetShipAttribute(const.attributeUpgradeLoad) + caliXtraLoad
        calibrationOutput = (self.GetShipAttribute(const.attributeUpgradeCapacity) + caliXtraCapacity) * caliMultiply
        portion = 0.0
        if calibrationLoad and calibrationOutput > 0:
            portion = max(0, min(1, calibrationLoad / calibrationOutput))
        self.sr.calibrationstatustext.text = '<b>%s</b><br>%s%.2f%s / %s%.2f' % (mls.UI_GENERIC_CALIBRATION,
         self.GetXtraColor(caliXtraLoad),
         calibrationLoad,
         FONTCOLOR_DEFAULT,
         self.GetMultiplyColor(caliMultiply + caliXtraCapacity),
         calibrationOutput)
        GAUGE_OUTERRAD = self.width * 0.89 / 2
        self.updateCalibrationStatusTimer = base.AutoTimer(10, self.UpdateStatusBar, 'calibration', self.sr.calibrationStatusPoly, radius=GAUGE_OUTERRAD - GAUGE_THICKNESS * self._scaleFactor, outerRadius=GAUGE_OUTERRAD, fromDeg=CALIBRATION_GAUGE_ZERO - CALIBRATION_GAUGE_RANGE * portion, toDeg=CALIBRATION_GAUGE_ZERO, innerColor=CALIBRATION_GAUGE_COLOR, outerColor=CALIBRATION_GAUGE_COLOR)
        if calibrationOutput > 0:
            status = 100.0 * float(calibrationLoad) / float(calibrationOutput)
            status = '%0.1f' % status
        else:
            status = ''
        self.statusCpuPowerCalibr[2] = status



    def UpdateCPUandPowerload(self, cpuMultiply = 1.0, xtraLoad = 0.0, xtraCpu = 0.0, xtraPower = 0.0, powerMultiply = 1.0, xtraPowerload = 0.0):
        if self.shipID is None:
            lg.Error('fitting', 'UpdateCPUAndPowerload with no ship')
            return 
        if xtraCpu:
            skill = sm.GetService('skills').HasSkill(const.typeElectronics)
            if skill is not None:
                xtraCpu *= 1.0 + 0.05 * skill.skillLevel
        cpuLoad = self.GetShipAttribute(const.attributeCpuLoad) + xtraLoad
        output = (self.GetShipAttribute(const.attributeCpuOutput) + xtraCpu) * cpuMultiply
        cputext = '<right><b>%s</b><br> %s%.2f%s / %s%.2f' % (mls.UI_GENERIC_CPU,
         self.GetXtraColor(xtraLoad),
         cpuLoad,
         FONTCOLOR_DEFAULT,
         self.GetMultiplyColor(cpuMultiply + xtraCpu),
         output)
        portion = 0.0
        if cpuLoad:
            if output == 0:
                portion = 1
            else:
                portion = max(0, min(1, cpuLoad / output))
        GAUGE_OUTERRAD = self.width * 0.89 / 2
        self.updateCpuStatusTimer = base.AutoTimer(10, self.UpdateStatusBar, 'cpu', self.sr.cpuStatusPoly, radius=GAUGE_OUTERRAD - GAUGE_THICKNESS * self._scaleFactor, outerRadius=GAUGE_OUTERRAD, fromDeg=CPU_GAUGE_ZERO + CPU_GAUGE_RANGE * portion, toDeg=CPU_GAUGE_ZERO, innerColor=CPU_GAUGE_COLOR, outerColor=CPU_GAUGE_COLOR)
        if output > 0:
            status = 100.0 * float(cpuLoad) / float(output)
            status = '%0.1f' % status
        else:
            status = ''
        self.statusCpuPowerCalibr[0] = status
        if xtraPower:
            skill = sm.GetService('skills').HasSkill(const.typeEngineering)
            if skill is not None:
                xtraPower *= 1.0 + 0.05 * skill.skillLevel
        powerLoad = self.GetShipAttribute(const.attributePowerLoad) + xtraPowerload
        output = (self.GetShipAttribute(const.attributePowerOutput) + xtraPower) * powerMultiply
        powergridtext = '%s<b>%s</b><br>%s%.2f%s / %s%.2f' % (FONTCOLOR_DEFAULT,
         mls.UI_GENERIC_POWERGRID,
         self.GetXtraColor(xtraPowerload),
         powerLoad,
         FONTCOLOR_DEFAULT,
         self.GetColor(xtraPower, powerMultiply),
         output)
        portion = 0.0
        if powerLoad:
            if output == 0.0:
                portion = 1.0
            else:
                portion = min(1.0, max(0.0, powerLoad / output))
        self.updatePowergridStatusTimer = base.AutoTimer(10, self.UpdateStatusBar, 'powergrid', self.sr.powergridStatusPoly, radius=GAUGE_OUTERRAD - GAUGE_THICKNESS * self._scaleFactor, outerRadius=GAUGE_OUTERRAD, toDeg=POWERGRID_GAUGE_ZERO, fromDeg=POWERGRID_GAUGE_ZERO + POWERGRID_GAUGE_RANGE * portion, innerColor=POWERGRID_GAUGE_COLOR, outerColor=POWERGRID_GAUGE_COLOR)
        if output > 0:
            status = 100.0 * float(powerLoad) / float(output)
            status = '%0.1f' % status
        else:
            status = ''
        self.statusCpuPowerCalibr[1] = status
        self.sr.cpu_power_statustext.text = '%s<br>%s' % (cputext, powergridtext)



    def UpdateStatusBar(self, what, polyObject, radius, outerRadius, fromDeg, toDeg, innerColor, outerColor):
        if self.destroyed:
            return 
        currentRotation = getattr(polyObject, 'currentFromDeg', toDeg)
        diff = abs(fromDeg - currentRotation)
        if diff < 0.0001:
            setattr(self, 'update%sStatusTimer' % what.capitalize(), None)
            currentRotation = fromDeg
        else:
            step = diff / 8.0
            if fromDeg > currentRotation:
                currentRotation += step
            else:
                currentRotation -= step
        polyObject.MakeArc(radius=radius, outerRadius=outerRadius, fromDeg=currentRotation, toDeg=toDeg, innerColor=innerColor, outerColor=outerColor)
        polyObject.currentFromDeg = currentRotation



    def GetStatusCpuPowerCalibr(self):
        return self.statusCpuPowerCalibr



    def UpdateCargoDroneInfo(self, xtraCargo, xtraDroneSpace):
        if not self or self.dead:
            return 
        self.sr.cargoSlot.Update(xtraCargo)
        self.sr.droneSlot.Update(xtraDroneSpace)



    def OpenCargoHoldOfActiveShip(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()



    def OpenDroneBayOfActiveShip(self, *args):
        sm.GetService('window').OpenDrones(self.shipID, cfg.evelocations.Get(self.shipID).locationName)



    def UpdateCapacitor(self, xtraCapacitor = 0.0, rechargeMultiply = 1.0, multiplyCapacitor = 1.0, reload = 0):
        maxcap = (xtraCapacitor + self.GetShipAttribute(const.attributeCapacitorCapacity)) * multiplyCapacitor
        ccAttribute = cfg.dgmattribs.Get(const.attributeCapacitorCapacity)
        rrAttribute = cfg.dgmattribs.Get(const.attributeRechargeRate)
        info = sm.GetService('info')
        rechargeRate = self.GetShipAttribute(const.attributeRechargeRate) * rechargeMultiply
        (peakRechargeRate, totalCapNeed, loadBalance, TTL,) = self.dogmaLocation.CapacitorSimulator(self.shipID)
        colorGreen = '<color=0xff00ff00>'
        colorRed = '<color=0xffff0000>'
        if loadBalance > 0:
            sustainableText = colorGreen + mls.UI_FITTING_STABLE
        else:
            time = colorRed + util.FmtDate(TTL, 'ss') + FONTCOLOR_DEFAULT
            sustainableText = mls.UI_FITTING_CAPDEPLETES % {'time': time}
        self.sr.capacitorHeaderStatsParent.sr.statusText.text = sustainableText.replace('<br>', '')
        if self.sr.capacitorStatsParent.sr.Get('powerCore', None):
            if not reload and maxcap == getattr(self.sr.capacitorStatsParent, 'maxcap', None):
                return 
            capText = '%s%s / %s%s' % (self.GetColor(xtraCapacitor, multiplyCapacitor),
             info.GetFormatAndValue(ccAttribute, int(maxcap)),
             self.GetMultiplyColor(rechargeMultiply),
             info.GetFormatAndValue(rrAttribute, rechargeRate))
            powerCore = self.sr.capacitorStatsParent.sr.powerCore
            powerCore.Flush()
            sustainabilityModified = False
            if xtraCapacitor > 0 or multiplyCapacitor != 1.0 or rechargeMultiply != 1.0:
                sustainabilityModified = True
            self.sr.capacitorStatsParent.sr.sustainable.text = sustainableText
            if loadBalance > 0:
                self.sr.capacitorStatsParent.sr.sustainable.hint = mls.UI_FITTING_MODULESSUSTAINABLE
            else:
                self.sr.capacitorStatsParent.sr.sustainable.hint = mls.UI_FITTING_MODULESNOTSUSTAINABLE
            delta = ''
            delta += u'\u0394 '
            color = FONTCOLOR_DEFAULT
            if sustainabilityModified:
                color = FONTCOLOR_HILITE
            unit = cfg.dgmunits.Get(ccAttribute.unitID).displayName + '/' + cfg.dgmunits.Get(rrAttribute.unitID).displayName + ' '
            delta += color + str(round((peakRechargeRate - totalCapNeed) * 1000, 2)) + ' ' + unit
            delta += '('
            delta += str(round((peakRechargeRate - totalCapNeed) / peakRechargeRate * 100, 1)) + '%'
            delta += ')'
            self.sr.capacitorStatsParent.sr.statusText.text = capText
            self.sr.capacitorStatsParent.sr.delta.text = delta
            numcol = min(18, int(maxcap / 50))
            rotstep = 360.0 / max(1, numcol)
            colWidth = max(12, min(16, numcol and int(192 / numcol)))
            powerunits = []
            for i in range(numcol):
                powerColumn = uicls.Transform(parent=powerCore, name='powerColumn', pos=(0,
                 0,
                 colWidth,
                 45), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=mathUtil.DegToRad(i * -rotstep), idx=0)
                for ci in xrange(3):
                    newcell = uicls.Sprite(parent=powerColumn, name='pmark', pos=(0,
                     ci * 4,
                     8 - ci * 2,
                     4), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell.png', color=(0.94, 0.35, 0.19, 1.0), idx=0, blendMode=trinity.TR2_SBM_ADD)
                    powerunits.insert(0, newcell)


            self.sr.capacitorStatsParent.maxcap = maxcap
            self.capacitorDone = 1
            powerCore = self.sr.capacitorStatsParent.sr.powerCore
            bad = trinity.TriColor(70 / 256.0, 26 / 256.0, 13.0 / 256.0)
            good = trinity.TriColor(240 / 256.0, 90 / 256.0, 50.0 / 256.0)
            bad.Scale(1.0 - loadBalance)
            good.Scale(loadBalance)
            visible = max(0, min(len(powerunits), int(loadBalance * len(powerunits))))
            for (ci, each,) in enumerate(powerunits):
                if ci >= visible:
                    each.SetRGB(0.25, 0.25, 0.25, 0.75)
                else:
                    each.SetRGB(bad.r + good.r, bad.g + good.g, bad.b + good.b, 1.0)

            if loadBalance == 0:
                self.sr.capacitorStatsParent.hint = mls.UI_FITTING_CAPNOTSUSTAINABLE % {'TTL': util.FmtDate(TTL, 'ss')}
            else:
                self.sr.capacitorStatsParent.hint = mls.UI_FITTING_CAPSUSTAINABLE % {'balance': str(round(loadBalance * 100, 1)) + '%'}



    def DisableSlot(self, slot):
        slot.opacity = 0.25
        slot.state = uiconst.UI_DISABLED
        slot.sr.flagIcon.state = uiconst.UI_HIDDEN



    def StripFitting(self, *args):
        if eve.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            eve.GetInventoryFromId(self.shipID).StripFitting()
            uthread.new(self.ReloadFitting, self.shipID)



    def OnDropData(self, dragObj, nodes):
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem'):
                requiredSkills = sm.GetService('info').GetRequiredSkills(node.rec.typeID)
                for (skillID, level,) in requiredSkills:
                    if getattr(sm.GetService('skills').HasSkill(skillID), 'skillLevel', 0) < level:
                        sm.GetService('tutorial').OpenTutorialSequence_Check(uix.skillfittingTutorial)
                        break


        sm.GetService('menu').TryFit([ node.rec for node in nodes ])



    def OnActiveShipChange(self, shipid):
        uthread.new(self.ReloadFitting, shipid)



    def OnStartSlotLinkingMode(self, typeID, *args):
        for (flag, icon,) in self.slots.iteritems():
            if getattr(icon, 'module', None):
                if icon.module.typeID != typeID:
                    if hasattr(icon, 'color'):
                        icon.linkDragging = 1
                        icon.color.a = 0.1




    def OnResetSlotLinkingMode(self, *args):
        for (flag, icon,) in self.slots.iteritems():
            if getattr(icon, 'module', None):
                if getattr(icon, 'linkDragging', None):
                    icon.linkDragging = 0
                    if hasattr(icon, 'color'):
                        icon.color.a = 1.0




    def ReloadShipModel(self, newModel = None):
        newModel = newModel or self.CreateActiveShipModel()
        if newModel:
            if newModel.__bluetype__ == 'trinity.EveShip2' and self.sr.sceneContainer:
                self.sr.sceneContainer.AddToScene(newModel)
                self.sr.sceneContainer.camera.OrbitParent(8.0, 4.0)
                camera = self.sr.sceneContainer.camera
                navigation = self.sr.sceneNavigation
                rad = newModel.GetBoundingSphereRadius()
                minZoom = rad + camera.frontClip
                alpha = camera.fieldOfView / 2.0
                maxZoom = rad * (1 / math.tan(alpha)) * 2
                camera.translationFromParent.z = minZoom * 2
                navigation.SetMinMaxZoom(minZoom, maxZoom)



    def GetShipDogmaItem(self):
        return self.dogmaLocation.dogmaItems[self.shipID]



    def CreateActiveShipModel(self):
        ship = self.GetShipDogmaItem()
        try:
            techLevel = self.GetShipAttribute(const.attributeTechLevel)
            if techLevel == 3.0:
                try:
                    newModel = sm.GetService('station').MakeModularShipFromShipItem(self.GetShipDogmaItem())
                except:
                    log.LogException('failed bulding modular ship')
                    sys.exc_clear()
                    return 
            else:
                modelPath = cfg.invtypes.Get(ship.typeID).GraphicFile()
                newFilename = modelPath.lower().replace(':/model', ':/dx9/model')
                newFilename = newFilename.replace('.blue', '.red')
                newModel = trinity.Load(newFilename)
        except Exception as e:
            log.LogException(str(e))
            sys.exc_clear()
        if hasattr(newModel, 'ChainAnimationEx'):
            newModel.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        newModel.display = 1
        newModel.name = str(ship.itemID)
        self.UpdateHardpoints(newModel)
        return newModel



    def UpdateHardpoints(self, newModel = None):
        if newModel is None:
            newModel = self.GetSceneShip()
        if newModel is None:
            log.LogError('UpdateHardpoints - No model!')
            return 
        turret.TurretSet.FitTurrets(self.shipID, newModel)



    def ReloadFitting(self, shipID):
        cfg.evelocations.Prime([self.shipID])
        try:
            self.GetFitting()
        except:
            if self.destroyed:
                log.LogException(severity=log.LGWARN, toMsgWindow=0, toConsole=0)
                sys.exc_clear()
            else:
                raise 
        self.UpdateStats()



    def IsCharge(self, typeID):
        return cfg.invtypes.Get(typeID).Group().Category().id in (const.categoryCharge, const.groupFrequencyCrystal)



    def GetFitting(self):
        key = uix.FitKeys()
        shipName = cfg.evelocations.Get(self.shipID).name
        ship = self.dogmaLocation.dogmaItems[self.shipID]
        typeName = cfg.invtypes.Get(ship.typeID).typeName
        label = shipName
        self.sr.shipnametext.text = label
        self.sr.dragIcon.width = self.sr.shipnametext.width
        self.sr.shipnametext.hint = typeName
        self.sr.infolink.left = self.sr.shipnametext.textwidth + 6
        if self.sr.infolink.left + 50 > self.sr.shipnamecont.width:
            self.sr.infolink.left = 0
            self.sr.infolink.SetAlign(uiconst.TOPRIGHT)
        self.sr.infolink.UpdateInfoLink(ship.typeID, ship.itemID)
        modulesByFlag = {}
        for module in ship.GetFittedItems().itervalues():
            modulesByFlag[(module.flagID, self.IsCharge(module.typeID))] = module

        for (gidx, attributeID,) in enumerate((const.attributeHiSlots, const.attributeMedSlots, const.attributeLowSlots)):
            totalslots = self.GetShipAttribute(attributeID)
            for sidx in xrange(8):
                flag = getattr(const, 'flag%sSlot%s' % (key[gidx], sidx))
                slot = self.slots[flag]
                slot.state = uiconst.UI_NORMAL
                if sidx >= totalslots:
                    slot.SetFitting(None, self.dogmaLocation)
                    self.DisableSlot(slot)
                else:
                    module = modulesByFlag.get((flag, 0), None)
                    if module:
                        slot.SetFitting(module, self.dogmaLocation)
                    else:
                        slot.SetFitting(None, self.dogmaLocation)
                    charge = modulesByFlag.get((flag, 1), None)
                    if charge:
                        slot.SetFitting(charge, self.dogmaLocation)
                    for charge in self.dogmaLocation.GetSublocations(self.shipID):
                        if charge.flagID == flag:
                            slot.SetFitting(charge, self.dogmaLocation)
                            continue



        totalRigSlots = self.GetShipAttribute(const.attributeRigSlots)
        for i in xrange(3):
            rigFlag = getattr(const, 'flagRigSlot%s' % i, None)
            slot = self.GetSlot(rigFlag)
            if not slot:
                continue
            if i >= totalRigSlots:
                self.DisableSlot(slot)
            else:
                module = modulesByFlag.get((rigFlag, 0), None)
                slot.SetFitting(module, self.dogmaLocation)

        showSubsystems = bool(self.GetShipAttribute(const.attributeTechLevel) > 2)
        for i in xrange(5):
            subsystemFlag = getattr(const, 'flagSubSystemSlot%s' % i, None)
            slot = self.GetSlot(subsystemFlag)
            if not slot:
                continue
            module = modulesByFlag.get((subsystemFlag, 0), None)
            slot.SetFitting(module)
            if not showSubsystems:
                self.DisableSlot(slot)




    def GetSlot(self, flag):
        if self.slots.has_key(flag):
            return self.slots[flag]



    def HiliteSlots(self, item):
        if self.destroyed:
            return 
        hiliteSlotFlag = None
        powerType = None
        typeID = None
        if item:
            typeID = item.typeID
            if typeID in cfg.dgmtypeattribs:
                for attribute in cfg.dgmtypeattribs[typeID]:
                    if attribute.attributeID == const.attributeSubSystemSlot:
                        hiliteSlotFlag = int(attribute.value)
                        break

            if hiliteSlotFlag is None:
                if typeID in cfg.dgmtypeeffects:
                    for effect in cfg.dgmtypeeffects[typeID]:
                        if effect.effectID in [const.effectHiPower,
                         const.effectMedPower,
                         const.effectLoPower,
                         const.effectSubSystem,
                         const.effectRigSlot]:
                            powerType = effect.effectID
                            break

            if self.IsCharge(typeID):
                pass
        for slot in self.slots.itervalues():
            if hiliteSlotFlag is None and powerType is None:
                if slot.id is None:
                    slot.Hilite(0)
            elif slot.state != uiconst.UI_DISABLED and slot.id is None:
                if powerType is not None and slot.powerType == powerType:
                    slot.Hilite(1)
                if hiliteSlotFlag is not None and slot.locationFlag == hiliteSlotFlag:
                    slot.Hilite(1)

        self.UpdateStats(typeID, item)



    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if shipID != self.shipID:
            return 
        self.UpdateStats()
        if attributeID == const.attributeIsOnline:
            uthread.pool('Fitting::OnDogmaAttributeChanged', self.ProcessOnlineStateChange, itemID, value)



    def ProcessOnlineStateChange(self, itemID, value):
        try:
            dogmaItem = self.dogmaLocation.GetDogmaItem(itemID)
        except KeyError:
            return 
        slot = dogmaItem.flagID - const.flagHiSlot0 + 1
        if slot is not None:
            sceneShip = self.GetSceneShip()
            for turret in sceneShip.turretSets:
                if turret.locatorName.split('_')[-1] == str(slot):
                    if dogmaItem.IsOnline():
                        turret.EnterStateIdle()
                    else:
                        turret.EnterStateDeactive()




    def OnAttribute(self, attributeName, item, value, updateStats = 1):
        try:
            self.GetService('godma').GetItem(item.itemID)
        except AttributeError:
            sys.exc_clear()
            return 
        if updateStats:
            self.UpdateStats()



    def OnAttributes(self, changeList):
        if self is None or self.destroyed or not hasattr(self, 'sr') or not self.initialized:
            return 
        reanimate = False
        for (attributeName, item, value,) in changeList:
            self.OnAttribute(attributeName, item, value, 0)
            if attributeName in ('hiSlots', 'medSlots', 'lowSlots'):
                reanimate = True

        self.UpdateStats()
        if reanimate:
            uthread.new(self.DelayedAnim)



    def DelayedAnim(self):
        if self.isDelayedAnim:
            return 
        self.isDelayedAnim = True
        try:
            blue.pyos.synchro.Sleep(500)
            uthread.new(self.GetFitting)

        finally:
            self.isDelayedAnim = False




    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.OnActiveShipChange(shipID)
        self.shipID = shipID
        self.ReloadShipModel()
        self.UpdateStats()
        self.LoadCapacitorStats()



    def RegisterForMouseUp(self):
        self.sr.colorPickerCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)



    def OnGlobalMouseUp(self, fromwhere, *etc):
        if self.sr.colorPickerPanel:
            if uicore.uilib.mouseOver == self.sr.colorPickerPanel or uiutil.IsUnder(fromwhere, self.sr.colorPickerPanel) or fromwhere == self.sr.colorPickers[self._expandedColorIdx]:
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        if self.sr.colorPickerPanel and not self.sr.colorPickerPanel.destroyed:
            self.sr.colorPickerPanel.Close()
        self.sr.colorPickerPanel = None
        if self.sr.colorPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.colorPickerCookie)
        self.sr.colorPickerCookie = None
        return 0



    def ExpandBestRepair(self, *args):
        if self.sr.bestRepairPickerPanel is not None:
            self.PickBestRepair(None)
            return 
        self.sr.bestRepairPickerCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp_BestRepair)
        bestRepairParent = self.sr.defenceStatsParent.sr.activeBestRepairParent
        (l, t, w, h,) = bestRepairParent.GetAbsolute()
        (wl, wt, ww, wh,) = self.sr.wnd.GetAbsolute()
        bestRepairPickerPanel = uicls.Container(parent=self.sr.wnd, name='bestRepairPickerPanel', align=uiconst.TOPLEFT, width=150, height=100, left=l - wl, top=t - wt + h, state=uiconst.UI_NORMAL, idx=0, clipChildren=1)
        subpar = uicls.Container(parent=bestRepairPickerPanel, name='subpar', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        active = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        top = 0
        mw = 32
        for (flag, hint, iconNo,) in ((ARMORREPAIRRATEACTIVE, mls.UI_FITTING_ARMOR_REPAIR_RATE_ACTIVE, 'ui_1_64_11'),
         (HULLREPAIRRATEACTIVE, mls.UI_FITTING_HULL_REPAIR_RATE_ACTIVE, 'ui_1_64_11'),
         (PASSIVESHIELDRECHARGE, mls.UI_FITTING_PASSIVE_SHIELD_RECHARGE, 'ui_22_32_7'),
         (SHIELDBOOSTRATEACTIVE, mls.UI_FITTING_SHIELD_BOOST_RATE_ACTIVE, 'ui_2_64_3')):
            entry = uicls.Container(name='entry', parent=subpar, align=uiconst.TOTOP, height=32, state=uiconst.UI_NORMAL)
            icon = uicls.Icon(icon=iconNo, parent=entry, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), ignoreSize=True)
            label = uicls.Label(text=hint, parent=entry, left=icon.left + icon.width, linespace=10, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            entry.OnClick = (self.PickBestRepair, entry)
            entry.OnMouseEnter = (self.OnMouseEnterBestRepair, entry)
            entry.bestRepairFlag = flag
            entry.sr.hilite = uicls.Fill(parent=entry, state=uiconst.UI_HIDDEN)
            if active == flag:
                uicls.Fill(parent=entry, color=(1.0, 1.0, 1.0, 0.125))
            top += 32
            mw = max(label.textwidth + label.left + 6, mw)

        bestRepairPickerPanel.width = mw
        bestRepairPickerPanel.height = 32
        bestRepairPickerPanel.opacity = 0.0
        uicls.Frame(parent=bestRepairPickerPanel)
        uicls.Fill(parent=bestRepairPickerPanel, color=(0.0, 0.0, 0.0, 1.0))
        self.sr.bestRepairPickerPanel = bestRepairPickerPanel
        uicore.effect.MorphUI(bestRepairPickerPanel, 'height', top, 250.0)
        uicore.effect.MorphUI(bestRepairPickerPanel, 'opacity', 1.0, 250.0, float=1)



    def OnGlobalMouseUp_BestRepair(self, fromwhere, *etc):
        if self.sr.bestRepairPickerPanel:
            if uicore.uilib.mouseOver == self.sr.bestRepairPickerPanel or uiutil.IsUnder(fromwhere, self.sr.bestRepairPickerPanel) or fromwhere == self.sr.defenceStatsParent.sr.activeBestRepairParent:
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        if self.sr.bestRepairPickerPanel and not self.sr.bestRepairPickerPanel.destroyed:
            self.sr.bestRepairPickerPanel.Close()
        self.sr.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None
        return 0



    def PickBestRepair(self, entry):
        if entry:
            settings.user.ui.Set('activeBestRepair', entry.bestRepairFlag)
            self.UpdateStats()
        if self.sr.bestRepairPickerPanel and not self.sr.bestRepairPickerPanel.destroyed:
            self.sr.bestRepairPickerPanel.Close()
        self.sr.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None



    def OnMouseEnterBestRepair(self, entry):
        for each in entry.parent.children:
            if util.GetAttrs(each, 'sr', 'hilite'):
                each.sr.hilite.state = uiconst.UI_HIDDEN

        entry.sr.hilite.state = uiconst.UI_DISABLED



    def AddToSlotsWithMenu(self, slot):
        self.menuSlots[slot] = 1



    def ClearSlotsWithMenu(self):
        for slot in self.menuSlots.iterkeys():
            slot.HideUtilButtons()

        self.menuSlots = {}



    def GetSceneShip(self):
        for model in self.sr.sceneContainer.scene.objects:
            if getattr(model, 'name', None) == str(self.shipID):
                return model





class FittingDraggableText(uicls.Container):
    __guid__ = 'xtriui.FittingDraggableText'

    def GetDragData(self, *args):
        fittingSvc = sm.StartService('fittingSvc')
        fitting = util.KeyVal()
        (fitting.shipTypeID, fitting.fitData,) = fittingSvc.GetFittingDictForActiveShip()
        fitting.fittingID = None
        fitting.description = ''
        fitting.name = cfg.evelocations.Get(util.GetActiveShip()).locationName
        fitting.ownerID = 0
        entry = util.KeyVal()
        entry.fitting = fitting
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]




