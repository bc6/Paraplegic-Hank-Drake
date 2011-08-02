import uix
import uiconst
import uiutil
import planet
import uicls
import uthread
import blue
from service import ROLE_GML
MAX_DISPLAY_QUALTY = const.planetResourceMaxValue * 255 * 0.5

class ResourceController(uicls.Container):
    __guid__ = 'planet.ui.ResourceController'
    __notifyevents__ = []
    default_name = 'ResourceController'
    default_align = uiconst.TOALL
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.CreateLayout()
        sm.RegisterNotify(self)



    def CreateLayout(self):
        legend = planet.ui.ResourceLegend(parent=self, pos=(0, 0, 292, 30))
        planetUI = sm.GetService('planetUI')
        self.resourceList = planet.ui.ResourceList(parent=self, pos=(0, 35, 288, 300))
        planetObject = sm.GetService('planetSvc').GetPlanet(planetUI.planetID)
        resourceInfo = planetObject.remoteHandler.GetPlanetResourceInfo()
        sortedList = []
        for (typeID, quality,) in resourceInfo.iteritems():
            name = cfg.invtypes.Get(typeID).name
            sortedList.append((name, (typeID, quality)))

        sortedList = uiutil.SortListOfTuples(sortedList)
        for (typeID, quality,) in sortedList:
            qualityRemapped = quality / MAX_DISPLAY_QUALTY
            self.resourceList.AddItem(typeID, quality=max(0, min(1.0, qualityRemapped)))




    def StopLoadingResources(self, resourceTypeID):
        self.resourceList.StopLoading(resourceTypeID)



    def StartLoadingResources(self):
        self.resourceList.StartLoading()



    def ResourceSelected(self, resourceTypeID):
        for item in self.resourceList.children:
            if item.typeID == resourceTypeID:
                self.resourceList.SelectItem(item)




    def EnterSurveyMode(self):
        self.resourceList.SetOpacity(0.5)
        self.resourceList.state = uiconst.UI_DISABLED



    def ExitSurveyMode(self):
        self.resourceList.SetOpacity(1)
        self.resourceList.state = uiconst.UI_PICKCHILDREN




class ResourceLegend(uicls.Container):
    __guid__ = 'planet.ui.ResourceLegend'
    default_name = 'ResourceLegend'
    default_align = uiconst.TOTOP
    default_legendWidth = 256
    default_state = uiconst.UI_PICKCHILDREN
    LINE_COLOR = (1, 1, 1, 0.5)
    RAMP_HEIGHT = 8
    HEIGHT = 4
    ADJUSTER_WIDTH = 16
    MIN_COLOR_RANGE = 26

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.legendWidth = attributes.get('legendWidth', self.default_legendWidth)
        self.leftSpacerMaxWidth = self.ADJUSTER_WIDTH + self.legendWidth - self.MIN_COLOR_RANGE
        self.CreateLayout()



    def CreateLayout(self):
        scale = uicls.Container(name='scale', parent=self, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.HEIGHT), padding=(4, 2, 4, 2))
        uicls.Line(name='scaleBase', parent=scale, align=uiconst.TOTOP, color=self.LINE_COLOR)
        uicls.Line(name='leftTick', parent=scale, align=uiconst.TOLEFT, color=self.LINE_COLOR)
        uicls.Line(name='rightTick', parent=scale, align=uiconst.TORIGHT, color=self.LINE_COLOR)
        uicls.Line(name='centerTick', parent=scale, align=uiconst.RELATIVE, color=self.LINE_COLOR, pos=(self.legendWidth / 2,
         1,
         1,
         self.HEIGHT))
        for x in (0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9):
            left = int(self.legendWidth * x)
            uicls.Line(name='miniorTick_%f' % x, parent=scale, align=uiconst.RELATIVE, color=self.LINE_COLOR, pos=(left,
             1,
             1,
             self.HEIGHT / 2))

        self.legendContainer = uicls.Container(parent=self, name='colorFilterContainer', align=uiconst.RELATIVE, statestate=uiconst.UI_PICKCHILDREN, pos=(0,
         8,
         self.legendWidth + 2 * self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH))
        self.leftSpacer = uicls.Container(parent=self.legendContainer, name='leftSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        self.centerSpacer = uicls.Container(parent=self.legendContainer, name='centerSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.legendWidth,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        self.rightSpacer = uicls.Container(parent=self.legendContainer, name='rightSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        adjusterMin = uicls.Icon(iname='leftAdjuster', icon='ui_73_16_185', parent=self.leftSpacer, align=uiconst.TORIGHT, pos=(0,
         0,
         self.ADJUSTER_WIDTH - 2,
         self.ADJUSTER_WIDTH), state=uiconst.UI_NORMAL, hint=mls.UI_PI_RESOURCE_ADJUST_MIN, color=(1, 1, 1, 0.5))
        adjusterMax = uicls.Icon(name='rightAdjuster', icon='ui_73_16_186', parent=self.rightSpacer, align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH - 2,
         self.ADJUSTER_WIDTH), state=uiconst.UI_NORMAL, hint=mls.UI_PI_RESOURCE_ADJUST_MAX, color=(1, 1, 1, 0.5))
        adjusterMin.OnMouseDown = (self.OnAdjustMouseDown, adjusterMin)
        adjusterMin.OnMouseUp = (self.OnAdjustMouseUp, adjusterMin)
        adjusterMin.OnMouseMove = (self.OnAdjustMouseMove, adjusterMin)
        adjusterMin.OnMouseEnter = (self.OnAdjusterMouseEnter, adjusterMin)
        adjusterMin.OnMouseExit = (self.OnAdjusterMouseExit, adjusterMin)
        adjusterMax.OnMouseDown = (self.OnAdjustMouseDown, adjusterMax)
        adjusterMax.OnMouseUp = (self.OnAdjustMouseUp, adjusterMax)
        adjusterMax.OnMouseMove = (self.OnAdjustMouseMove, adjusterMax)
        adjusterMax.OnMouseEnter = (self.OnAdjusterMouseEnter, adjusterMax)
        adjusterMax.OnMouseExit = (self.OnAdjusterMouseExit, adjusterMax)
        colorRamp = uicls.Sprite(name='ColorRamp', parent=self.centerSpacer, texturePath='res:/dx9/model/worldobject/planet/resource_colorramp.dds', color=(1, 1, 1, 0.75), padding=(0, 4, 0, 4), state=uiconst.UI_NORMAL, align=uiconst.TOALL)
        colorRamp.OnMouseDown = (self.OnAdjustMouseDown, colorRamp)
        colorRamp.OnMouseUp = (self.OnAdjustMouseUp, colorRamp)
        colorRamp.OnMouseMove = (self.OnMoveRange, colorRamp)
        (low, hi,) = settings.char.ui.Get('planet_resource_display_range', (0.0, 1.0))
        scalar = self.legendWidth - 1
        self.leftSpacer.width = int(low * scalar) + self.ADJUSTER_WIDTH
        self.centerSpacer.width = int((hi - low) * scalar)



    def OnAdjusterMouseEnter(self, adjuster, *args):
        adjuster.color.SetRGB(1, 1, 1, 0.75)



    def OnAdjusterMouseExit(self, adjuster, *args):
        adjuster.color.SetRGB(1, 1, 1, 0.5)



    def OnAdjustMouseDown(self, adjuster, button):
        if button == 0:
            adjuster.dragging = True



    def OnAdjustMouseUp(self, adjuster, button):
        if button == 0:
            adjuster.dragging = False



    def OnAdjustMouseMove(self, adjuster, *args):
        if getattr(adjuster, 'dragging', False) and uicore.uilib.leftbtn:
            if adjuster.name.startswith('right'):
                self.centerSpacer.width += uicore.uilib.dx
                if self.centerSpacer.width + self.leftSpacer.width - self.ADJUSTER_WIDTH > self.legendWidth:
                    self.centerSpacer.width = self.legendWidth - (self.leftSpacer.width - self.ADJUSTER_WIDTH)
                elif self.centerSpacer.width < self.MIN_COLOR_RANGE:
                    self.centerSpacer.width = self.MIN_COLOR_RANGE
            else:
                width = self.leftSpacer.width
                dx = uicore.uilib.dx
                if self.centerSpacer.width - uicore.uilib.dx < self.MIN_COLOR_RANGE:
                    dx = self.centerSpacer.width - self.MIN_COLOR_RANGE
                width += dx
                if width < self.ADJUSTER_WIDTH:
                    width = self.ADJUSTER_WIDTH
                elif width > self.leftSpacerMaxWidth:
                    width = self.leftSpacerMaxWidth
                dx = width - self.leftSpacer.width
                self.leftSpacer.width = width
                self.centerSpacer.width -= dx
            self.UpdateColorRamp()



    def OnMoveRange(self, adjuster, *args):
        if getattr(adjuster, 'dragging', False):
            self.leftSpacer.width += uicore.uilib.dx
            if self.centerSpacer.width + self.leftSpacer.width - self.ADJUSTER_WIDTH > self.legendWidth:
                self.leftSpacer.width = self.legendWidth - (self.centerSpacer.width - self.ADJUSTER_WIDTH)
            elif self.leftSpacer.width < self.ADJUSTER_WIDTH:
                self.leftSpacer.width = self.ADJUSTER_WIDTH
            self.UpdateColorRamp()



    def UpdateColorRamp(self):
        low = self.leftSpacer.width - self.ADJUSTER_WIDTH
        hi = low + self.centerSpacer.width
        sm.GetService('planetUI').SetResourceDisplayRange(low / float(self.legendWidth - 1), hi / float(self.legendWidth - 1))




class ResourceList(uicls.Container):
    __guid__ = 'planet.ui.ResourceList'
    default_name = 'ResourceList'
    default_left = 0
    default_top = 300
    default_width = 300
    default_height = 300
    default_align = uiconst.RELATIVE
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.AddItem(None)



    def AddItem(self, typeID, quality = None):
        planet.ui.ResourceListItem(parent=self, typeID=typeID, quality=quality)



    def ClearItems(self):
        self.children.Clear()



    def SelectItem(self, selectedItem):
        for item in self.children:
            if item != selectedItem:
                item.Deselect()
            else:
                item.Select()




    def StopLoading(self, typeID):
        item = self.GetItemByType(typeID)
        item.StopLoading()



    def GetItemByType(self, typeID):
        for item in self.children:
            if item.typeID == typeID:
                return item




    def GetSelected(self):
        for item in self.children:
            if item.selected:
                return item





class ResourceListItem(uicls.Container):
    __guid__ = 'planet.ui.ResourceListItem'
    ITEM_HEIGHT = 24
    SELECT_BLOCK_PADDING = 1
    LEVEL_COLOR = (0.85, 0.85, 0.85, 1)
    LEVEL_BG_COLOR = (0.85, 0.85, 0.85, 0.25)
    LEVEL_WIDTH = 136
    LEVEL_HEIGHT = 10
    LEVEL_LEFT = 150
    SELECT_FILL_COLOR = (1.0, 1.0, 1.0, 0.25)
    HOVER_FILL_COLOR = (1.0, 1.0, 1.0, 0.25)
    EMPTY_COLOR = (1, 1, 1, 0)
    ICON_SIZE = 24
    ICON_LEFT = 0
    default_name = 'ResourceListItem'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = ITEM_HEIGHT
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_typeID = None
    default_selected = False
    default_quality = None

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', self.default_typeID)
        self.quality = attributes.get('quality', self.default_quality)
        if self.typeID is None:
            self.selected = True
        else:
            self.selected = False
        self.CreateLayout()



    def CreateLayout(self):
        if self.typeID is None:
            text = mls.UI_INFLIGHT_NOFILTER.upper()
            self.icon = None
            self.loadingIcon = None
        else:
            self.icon = uicls.Icon(parent=self, align=uiconst.RELATIVE, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), state=uiconst.UI_DISABLED, ignoreSize=True, typeID=self.typeID, size=self.ICON_SIZE)
            text = cfg.invtypes.Get(self.typeID).typeName
            self.loadingIcon = uicls.Transform(parent=self, align=uiconst.RELATIVE, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), state=uiconst.UI_HIDDEN)
            load = uicls.Icon(icon='ui_77_32_13', parent=self.loadingIcon, IgnoreSize=True, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), align=uiconst.CENTER)
        self.container = uicls.Container(parent=self, name='mainContainer', align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.resourceName = uicls.Label(text=text, parent=self, autowidth=1, autoheight=1, left=4 + (self.ICON_SIZE if self.typeID is not None else 0), top=6, fontsize=12, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        if self.typeID is not None:
            self.levelBar = uicls.Container(name='levelBar', parent=self, pos=(self.LEVEL_LEFT,
             7,
             self.LEVEL_WIDTH,
             self.LEVEL_HEIGHT), align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
            self.level = uicls.Fill(parent=self.levelBar, pos=(0,
             0,
             int(self.LEVEL_WIDTH * (self.quality or 0.0)),
             0), align=uiconst.TOLEFT, color=self.LEVEL_COLOR)
            self.levelFill = uicls.Fill(parent=self.levelBar, align=uiconst.TOALL, color=self.LEVEL_BG_COLOR)
            if self.quality is None:
                self.levelBar.state = uiconst.UI_HIDDEN
        self.selectBlock = uicls.Fill(parent=self, name='selectBlock', state=uiconst.UI_DISABLED, align=uiconst.TOALL, padding=(0,
         self.SELECT_BLOCK_PADDING,
         0,
         self.SELECT_BLOCK_PADDING), color=self.SELECT_FILL_COLOR if self.selected else self.EMPTY_COLOR)



    def OnMouseEnter(self, *args):
        if not self.selected:
            self.selectBlock.color.SetRGB(*self.HOVER_FILL_COLOR)



    def OnMouseExit(self, *args):
        if not self.selected:
            self.selectBlock.color.SetRGB(*self.EMPTY_COLOR)



    def OnClick(self, *args):
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_scanning_switch_play')
        selected = self.parent.GetSelected()
        if selected == self:
            return 
        self.parent.SelectItem(self)
        sm.GetService('planetUI').ShowResource(self.typeID)



    def Select(self):
        self.selectBlock.color.SetRGB(*self.SELECT_FILL_COLOR)
        if self.loadingIcon:
            self.loadingIcon.state = uiconst.UI_DISABLED
            self.icon.state = uiconst.UI_HIDDEN
            uthread.new(self.loadingIcon.StartRotationCycle, 1.0, 4000.0)
        self.selected = True



    def Deselect(self):
        self.selectBlock.color.SetRGB(*self.EMPTY_COLOR)
        self.selected = False



    def StopLoading(self):
        if self.loadingIcon:
            self.loadingIcon.StopRotationCycle()
            self.loadingIcon.state = uiconst.UI_HIDDEN
            self.icon.state = uiconst.UI_DISABLED



    def GetMenu(self):
        if self.typeID is None:
            return []
        ret = [(mls.UI_CMD_SHOWINFO, sm.GetService('info').ShowInfo, [self.typeID])]
        if session.role & ROLE_GML == ROLE_GML:
            ret.append((mls.UI_CMD_GMEXTRAS, self.GetGMMenu()))
        return ret



    def GetGMMenu(self):
        ret = []
        ret.append((mls.UI_CMD_COPY, self.CopyTypeID))
        ret.append((mls.UI_PI_CMD_SHOW_RESOURCE_DETAILS_CURRENT, sm.GetService('planetUI').GMShowResource, (self.typeID, 'current')))
        ret.append((mls.UI_PI_CMD_SHOW_RESOURCE_DETAILS_PLAYER, sm.GetService('planetUI').GMShowResource, (self.typeID, 'player')))
        ret.append((mls.UI_PI_CMD_SHOW_RESOURCE_DETAILS_BASE, sm.GetService('planetUI').GMShowResource, (self.typeID, 'base')))
        ret.append((mls.UI_PI_CMD_SHOW_RESOURCE_DETAILS_DEPLETION, sm.GetService('planetUI').GMShowResource, (self.typeID, 'depletion')))
        ret.append((mls.UI_PI_CMD_SHOW_RESOURCE_DETAILS_NUGGETS, sm.GetService('planetUI').GMShowResource, (self.typeID, 'nuggets')))
        ret.append(None)
        ret.append(('Create nugget layer', sm.GetService('planetUI').GMCreateNuggetLayer, (self.typeID,)))
        return ret



    def CopyTypeID(self):
        blue.pyos.SetClipboardData(str(self.typeID))




