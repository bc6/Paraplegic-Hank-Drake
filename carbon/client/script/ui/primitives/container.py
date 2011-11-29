import uiconst
import uicls
import uiutil
import uthread
import blue
import base
import trinity
import weakref

class Container(uicls.Base):
    __guid__ = 'uicls.Container'
    __renderObject__ = trinity.Tr2Sprite2dContainer
    __members__ = uicls.Base.__members__ + ['opacity',
     'children',
     'background',
     'clipChildren']
    default_name = 'container'
    default_clipChildren = False
    default_pickRadius = 0
    default_opacity = 1.0
    default_align = uiconst.TOALL
    default_state = uiconst.UI_PICKCHILDREN
    default_depthMin = 0.0
    default_depthMax = 0.0
    default_bgColor = None
    default_bgTexturePath = None

    def ApplyAttributes(self, attributes):
        self._childrenDirty = False
        self.children = self.GetChildrenList()
        self.background = uicls.BackgroundList(self)
        uicls.Base.ApplyAttributes(self, attributes)
        self._dragging = False
        self._dragAllowed = False
        self._dragData = None
        self._opacity = None
        self.depthMin = attributes.get('depthMin', self.default_depthMin)
        self.depthMax = attributes.get('depthMax', self.default_depthMax)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)
        self.opacity = attributes.get('opacity', self.default_opacity)
        self.clipChildren = attributes.get('clipChildren', self.default_clipChildren)
        bgColor = attributes.get('bgColor', self.default_bgColor)
        bgTexturePath = attributes.get('bgTexturePath', self.default_bgTexturePath)
        if bgTexturePath:
            uicls.Sprite(bgParent=self, texturePath=bgTexturePath, color=bgColor or (1.0, 1.0, 1.0, 1.0))
        elif bgColor:
            uicls.Fill(bgParent=self, color=bgColor)
        self.__dict__['containerIsReady'] = True



    def Close(self):
        if getattr(self, 'destroyed', False):
            return 
        for child in self.children[:]:
            child.Close()

        for child in self.background[:]:
            child.Close()

        uicls.Base.Close(self)



    def FlagChildrenDirty(self):
        if self._childrenDirty and not self._displayDirty:
            return 
        self._childrenDirty = True
        if self.align == uiconst.NOALIGN:
            uicore.uilib.alignIslands.append(self)
            return 
        parent = self.parent
        if parent:
            parent.FlagChildrenDirty()



    def Traverse(self, mbudget, orgBudget, lvl):
        if self.destroyed:
            return mbudget
        if self._alignmentDirty:
            mbudget = self.UpdateAlignment(mbudget, orgBudget, hint='traverse', lvl=lvl)
            self._childrenDirty = True
        else:
            mbudget = self.ConsumeBudget(mbudget, orgBudget)
        if self._childrenDirty:
            self._childrenDirty = False
            budget = (0,
             0,
             self.displayWidth,
             self.displayHeight)
            myOrgBudget = (0,
             0,
             self.displayWidth,
             self.displayHeight)
            for each in self.children:
                if each.display:
                    budget = each.Traverse(budget, myOrgBudget, lvl=lvl + 1)

        return mbudget



    def GetChildrenList(self):
        return uicls.UIChildrenList(self)



    def GetOpacity(self):
        return self.opacity



    def SetOpacity(self, opacity):
        self.opacity = opacity


    opacity = property(GetOpacity, SetOpacity)

    def AutoFitToContent(self):
        if self.align in uiconst.AFFECTEDBYPUSHALIGNMENTS:
            raise RuntimeError('AutoFitToContent: invalid alignment')
        minWidth = 0
        minHeight = 0
        totalAutoVertical = 0
        totalAutoHorizontal = 0
        for each in self.children:
            if each.align not in uiconst.AFFECTEDBYPUSHALIGNMENTS:
                minWidth = max(minWidth, each.left + each.width)
                minHeight = max(minHeight, each.top + each.height)
            elif each.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
                totalAutoVertical += each.padTop + each.height + each.padBottom
            elif each.align in (uiconst.TOLEFT, uiconst.TORIGHT):
                totalAutoHorizontal += each.padLeft + each.width + each.padRight

        self.width = max(minWidth, totalAutoHorizontal)
        self.height = max(minHeight, totalAutoVertical)



    def Flush(self):
        for child in self.children[:]:
            child.Close()




    def FindChild(self, *names, **kwds):
        if self.destroyed:
            return 
        ret = None
        searchFrom = self
        for name in names:
            ret = searchFrom._FindChildByName(name)
            if hasattr(ret, 'children'):
                searchFrom = ret

        if not ret or ret.name != names[-1]:
            if kwds.get('raiseError', False):
                raise RuntimeError('ChildNotFound', (self.name, names))
            return 
        return ret



    def _FindChildByName(self, name, lvl = 0):
        for child in self.children:
            if child.name == name:
                return child

        for child in self.children:
            if hasattr(child, 'children'):
                ret = child._FindChildByName(name, lvl + 1)
                if ret is not None:
                    return ret




    def Find(self, triTypeName):

        def FindType(under, typeName, addto):
            if under.__bluetype__ == typeName:
                addto.append(under)
            if hasattr(under, 'children'):
                for each in under.children:
                    FindType(each, typeName, addto)



        ret = []
        for child in self.children:
            FindType(child, triTypeName, ret)

        return ret



    def GetChild(self, *names):
        return self.FindChild(*names, **{'raiseError': True})



    @apply
    def depthMin():
        doc = 'Minimum depth value'

        def fget(self):
            return self._depthMin



        def fset(self, value):
            self._depthMin = value
            ro = self.renderObject
            if ro and hasattr(ro, 'depthMin'):
                ro.depthMin = value or 0.0


        return property(**locals())



    @apply
    def depthMax():
        doc = 'Maximum depth value'

        def fget(self):
            return self._depthMax



        def fset(self, value):
            self._depthMax = value
            ro = self.renderObject
            if ro and hasattr(ro, 'depthMax'):
                ro.depthMax = value or 0.0


        return property(**locals())



    @apply
    def clipChildren():
        doc = 'Clip children?'

        def fget(self):
            return self._clipChildren



        def fset(self, value):
            self._clipChildren = value
            ro = self.renderObject
            if ro and hasattr(ro, 'clip'):
                ro.clip = value


        return property(**locals())



    @apply
    def opacity():
        doc = 'Opacity'

        def fget(self):
            return self._opacity



        def fset(self, value):
            self._opacity = value
            ro = self.renderObject
            if ro and hasattr(ro, 'opacity'):
                ro.opacity = value or 0.0


        return property(**locals())



    @apply
    def pickRadius():
        doc = 'Pick radius'

        def fget(self):
            return self._pickRadius



        def fset(self, value):
            self._pickRadius = value
            ro = self.renderObject
            if ro and hasattr(ro, 'pickRadius'):
                ro.pickRadius = uicore.ScaleDpi(value) or 0.0


        return property(**locals())



    @apply
    def displayWidth():
        doc = 'Width of container. Background objects are always assigned this width as well'
        fget = uicls.Base.displayWidth.fget

        def fset(self, value):
            uicls.Base.displayWidth.fset(self, value)
            if hasattr(self, 'background'):
                for each in self.background:
                    each.displayWidth = value



        return property(**locals())



    @apply
    def displayHeight():
        doc = 'Height of container. Background objects are always assigned this height as well'
        fget = uicls.Base.displayHeight.fget

        def fset(self, value):
            uicls.Base.displayHeight.fset(self, value)
            if hasattr(self, 'background'):
                for each in self.background:
                    each.displayHeight = value



        return property(**locals())



    @apply
    def displayRect():
        doc = ''
        fget = uicls.Base.displayRect.fget

        def fset(self, value):
            uicls.Base.displayRect.fset(self, value)
            if len(self.background) > 0:
                rect = (0,
                 0,
                 self._displayWidth,
                 self._displayHeight)
                for each in self.background:
                    each.displayRect = rect



        return property(**locals())



    def _AppendChildRO(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO:
            RO.children.append(childRO)
        self.FlagAlignmentDirty()
        if child.align == uiconst.NOALIGN:
            child.UpdateAlignmentAsRoot()



    def _InsertChildRO(self, idx, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO:
            RO.children.insert(idx, childRO)
        self.FlagAlignmentDirty()
        if child.align == uiconst.NOALIGN:
            child.UpdateAlignmentAsRoot()



    def _RemoveChildRO(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO and childRO in RO.children:
            RO.children.remove(childRO)
        self.FlagAlignmentDirty()



    def AppendBackgroundObject(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO:
            RO.background.append(childRO)
        self.FlagAlignmentDirty()



    def InsertBackgroundObject(self, idx, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO:
            RO.background.insert(idx, childRO)
        self.FlagAlignmentDirty()



    def RemoveBackgroundObject(self, child):
        RO = self.GetRenderObject()
        if not RO:
            return 
        childRO = child.GetRenderObject()
        if childRO and childRO in RO.background:
            RO.background.remove(childRO)
        self.FlagAlignmentDirty()



    def IsDraggable(self):
        return hasattr(self, 'GetDragData')



    def IsBeingDragged(self):
        return getattr(self, '_dragging', False)



    def OnMouseDown(self, *args):
        if self.IsDraggable() and uicore.uilib.leftbtn:
            uicore.Message('DragDropGrab')
            self._dragMouseDown = (uicore.uilib.x, uicore.uilib.y)
            self._dragAllowed = True
        else:
            self._dragAllowed = False



    def OnMouseMove(self, *args):
        if self.IsBeingDragged():
            self.OnDragMove(self, self._dragData)
            where = uicore.uilib.mouseOver
            whereLast = getattr(self, '_dragLastOver', None)
            if where is not self:
                if hasattr(where, 'OnDragMove'):
                    uthread.new(where.OnDragMove, self, self._dragData)
                if whereLast is not where:
                    if hasattr(whereLast, 'OnDragExit'):
                        uthread.new(whereLast.OnDragExit, self, self._dragData)
                    if hasattr(where, 'OnDragEnter'):
                        uthread.new(where.OnDragEnter, self, self._dragData)
            self._dragLastOver = where
            return 
        if not self.IsDraggable() or not uicore.uilib.leftbtn or not self._dragAllowed or uicore.uilib.mouseTravel < 6:
            return 
        uthread.new(self.BeginDrag).context = 'Container::BeginDrag'



    def BeginDrag(self, *args):
        if getattr(self, 'Draggable_blockDrag', 0) or not getattr(self, '_dragAllowed', 0):
            return 
        dragData = self.GetDragData(self)
        if not dragData:
            return 
        self._dragAllowed = False
        self._dragging = True
        self._dragData = dragData
        dragContainer = uicls.DragContainer(name='dragContainer', align=uiconst.ABSOLUTE, idx=0, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, parent=uicore.layer.dragging)
        dragContainer.dragData = dragData
        uicore.uilib.KillClickThreads()
        self.DoDrag(dragContainer, dragData)



    def DoDrag(self, dragContainer, dragData):
        if dragContainer.dead:
            return 
        mouseOffset = self.PrepareDrag_(dragContainer, self)
        if self.destroyed:
            return 
        dragContainer.InitiateDrag(mouseOffset)
        if self.destroyed:
            uiutil.Flush(uicore.layer.dragging)
            return 
        dropLocation = uicore.uilib.mouseOver
        if self.IsBeingDragged():
            self._dragAllowed = False
            self._dragging = 0
            self._dragLastOver = None
            uiutil.Flush(uicore.layer.dragging)
            dropLocation = uicore.uilib.mouseOver
            if getattr(dropLocation, 'OnDropData', None) and self.VerifyDrop(dropLocation, dragData):
                uthread.new(dropLocation.OnDropData, self, dragData)
            else:
                self.OnDragCanceled_(self, dragData)
        self._dragData = None
        self.OnEndDrag_(self, dropLocation, dragData)



    def PrepareDrag_(self, dragContainer, dragSource, *args):
        return uiutil.PrepareDrag_Standard(dragContainer, dragSource)



    def OnDragCanceled_(self, dragSource, dragData, *args):
        pass



    def OnEndDrag_(self, dragSource, dropLocation, dragData, *args):
        pass



    def OnDragMove(self, dragSource, dragData, *args):
        pass



    def VerifyDrop(self, dragDestination, dragData, *args):
        return True




