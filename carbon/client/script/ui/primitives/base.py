import uicls
import uiutil
import uiconst
import uthread
import blue
import types
import util
import base
import log
import trinity
import copy
import bluepy
import weakref
import uiconstLoaded
PUSHALIGNMENTS = (uiconst.TOLEFT,
 uiconst.TOTOP,
 uiconst.TORIGHT,
 uiconst.TOBOTTOM,
 uiconst.TOLEFT_PROP,
 uiconst.TOTOP_PROP,
 uiconst.TORIGHT_PROP,
 uiconst.TOBOTTOM_PROP)
AFFECTEDBYPUSHALIGNMENTS = PUSHALIGNMENTS + (uiconst.TOALL,)
alignCountStat = blue.statistics.Find('CarbonUI/alignCount')
if not alignCountStat:
    print "Registering new 'alignCount' stat"
    alignCountStat = blue.CcpStatisticsEntry()
    alignCountStat.name = 'CarbonUI/alignCount'
    alignCountStat.type = 1
    alignCountStat.resetPerFrame = True
    alignCountStat.description = 'The number of calls to UpdateAlignment per frame'
    blue.statistics.Register(alignCountStat)
flagNextCountStat = blue.statistics.Find('CarbonUI/flagNextCount')
if not flagNextCountStat:
    print "Registering new 'flagNextCount' stat"
    flagNextCountStat = blue.CcpStatisticsEntry()
    flagNextCountStat.name = 'CarbonUI/flagNextCount'
    flagNextCountStat.type = 1
    flagNextCountStat.resetPerFrame = True
    flagNextCountStat.description = 'The number of calls to FlagNextAlignment per frame'
    blue.statistics.Register(flagNextCountStat)

class Base(object):
    __guid__ = 'uicls.Base'
    __renderObject__ = None
    __members__ = ['name',
     'left',
     'top',
     'width',
     'height',
     'padLeft',
     'padTop',
     'padRight',
     'padBottom',
     'display',
     'align',
     'pickState',
     'parent',
     'renderObject']
    default_name = 'BaseUIObject'
    default_parent = None
    default_idx = -1
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_hint = None
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_padLeft = 0
    default_padTop = 0
    default_padRight = 0
    default_padBottom = 0
    default_cursor = None

    def _Initialize(self, *args, **kw):
        pass



    def __init__(self, **kw):
        self.sr = uiutil.Bunch()
        self.InitRenderObject()
        self._name = self.default_name
        self._cursor = self.default_cursor
        self._parentRef = None
        self._alignmentDirty = False
        self._left = 0
        self._top = 0
        self._width = 0
        self._height = 0
        self._align = None
        self._display = None
        self._displayDirty = None
        self.PrepareProperties()
        self.displayX = 0
        self.displayY = 0
        self.displayWidth = 0
        self.displayHeight = 0
        self.dead = False
        self.destroyed = False
        self.display = True
        self.pickState = uiconst.TR2_SPS_ON
        self.left = 0
        self.top = 0
        self.width = 0
        self.height = 0
        self.align = 0
        self._Initialize(**kw)
        self._attachedObjects = []
        self._attachedTo = None
        self._animationCurves = {}
        attributesBunch = uiutil.Bunch(kw)
        self.ApplyAttributes(attributesBunch)
        self.PostApplyAttributes(attributesBunch)
        if hasattr(self, 'init'):
            self.init()
        self.baseIsReady = True
        self.FlagAlignmentDirty()



    def __repr__(self):
        return '%s object at %s, name=%s, destroyed=%s>' % (self.__guid__,
         hex(id(self)),
         self.name.encode('utf8'),
         self.destroyed)



    def PrepareProperties(self):
        pass



    def ApplyAttributes(self, attributes):
        self.name = attributes.get('name', self.default_name)
        self.align = attributes.get('align', self.default_align)
        self.hint = attributes.get('hint', self.default_hint)
        self.cursor = attributes.get('cursor', self.default_cursor)
        (left, top, width, height,) = (self.default_left,
         self.default_top,
         self.default_width,
         self.default_height)
        if 'pos' in attributes and attributes.pos is not None:
            (left, top, width, height,) = attributes.pos
        if 'left' in attributes:
            left = attributes.left
        if 'top' in attributes:
            top = attributes.top
        if 'width' in attributes:
            width = attributes.width
        if 'height' in attributes:
            height = attributes.height
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        (padLeft, padTop, padRight, padBottom,) = (self.default_padLeft,
         self.default_padTop,
         self.default_padRight,
         self.default_padBottom)
        if 'padding' in attributes and attributes.padding is not None:
            if isinstance(attributes.padding, (tuple, list)):
                (padLeft, padTop, padRight, padBottom,) = attributes.padding
            else:
                padLeft = padTop = padRight = padBottom = attributes.padding
        if 'padLeft' in attributes:
            padLeft = attributes.padLeft
        if 'padTop' in attributes:
            padTop = attributes.padTop
        if 'padRight' in attributes:
            padRight = attributes.padRight
        if 'padBottom' in attributes:
            padBottom = attributes.padBottom
        self.padLeft = padLeft
        self.padTop = padTop
        self.padRight = padRight
        self.padBottom = padBottom
        self.SetParent(attributes.get('parent', self.default_parent), attributes.get('idx', self.default_idx))
        self.SetState(attributes.get('state', self.default_state))
        if attributes.get('bgParent', None):
            attributes.bgParent.background.append(self)



    def Close(self):
        if getattr(self, 'destroyed', False):
            return 
        self.destroyed = True
        uicore.uilib.ReleaseObject(self)
        notifyevents = getattr(self, '__notifyevents__', None)
        if notifyevents:
            sm.UnregisterNotify(self)
        attachedTo = getattr(self, '_attachedTo', None)
        if attachedTo:
            object = attachedTo[0]
            object._RemoveAttachment(self)
        self._OnClose()
        parent = self.GetParent()
        if parent and self in parent.children:
            parent.children.remove(self)
        self.dead = True
        self.destroyed = True
        self.StopAnimations()
        self.renderObject = None
        self._alignFunc = None



    def HasEventHandler(self, handlerName):
        (handlerArgs, handler,) = self.FindEventHandler(handlerName)
        if not handler:
            return False
        baseHandler = getattr(uicls.Base, handlerName, None)
        if baseHandler and getattr(handler, 'im_func', None) is baseHandler.im_func:
            return False
        return bool(handler)



    def FindEventHandler(self, handlerName):
        handler = getattr(self, handlerName, None)
        if not handler:
            return (None, None)
        if type(handler) == types.TupleType:
            handlerArgs = handler[1:]
            handler = handler[0]
        else:
            handlerArgs = ()
        return (handlerArgs, handler)



    def StopAnimations(self):
        for curveSet in self._animationCurves.values():
            curveSet.Stop()

        self._animationCurves = {}



    def AttachAnimationCurveSet(self, curveSet, attrName):
        currCurveSet = self._animationCurves.get(attrName, None)
        if currCurveSet:
            currCurveSet.Stop()
        self._animationCurves[attrName] = curveSet



    def ProcessEvent(self, eventID):
        uicore.uilib._TryExecuteHandler(eventID, self)



    def InitRenderObject(self):
        if self.__renderObject__:
            self.renderObject = RO = self.__renderObject__()
            uicore.uilib.RegisterObject(self, RO)
        else:
            self.renderObject = None



    def GetRenderObject(self):
        return self.renderObject



    def PostApplyAttributes(self, attributes):
        pass



    def SetParent(self, parent, idx = None):
        currentParent = self.GetParent()
        if currentParent:
            self.FlagNextObjectsDirty(lvl=0)
            currentParent.children.remove(self)
            currentParent.FlagAlignmentDirty()
        if parent is not None:
            if idx is None:
                idx = -1
            parent.children.insert(idx, self)
            parent.FlagAlignmentDirty()
            self.FlagNextObjectsDirty(lvl=0)



    def GetParent(self):
        if self._parentRef:
            return self._parentRef()


    parent = property(GetParent)

    def SetOrder(self, idx):
        parent = self.GetParent()
        if parent:
            currentIndex = parent.children.index(self)
            if currentIndex != idx:
                self.SetParent(parent, idx)
        self.FlagAlignmentDirty()



    @apply
    def left():
        doc = 'x-coordinate of UI element'

        def fget(self):
            return self._left



        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._left:
                self._left = adjustedValue
                self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def top():
        doc = 'y-coordinate of UI element'

        def fget(self):
            return self._top



        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._top:
                self._top = adjustedValue
                self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def width():
        doc = 'Width of UI element'

        def fget(self):
            return self._width



        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._width:
                self._width = adjustedValue
                self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def height():
        doc = 'Height of UI element'

        def fget(self):
            return self._height



        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._height:
                self._height = adjustedValue
                self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def padLeft():
        doc = 'Left padding'

        def fget(self):
            return self._padLeft



        def fset(self, value):
            self._padLeft = value
            self.FlagNextObjectsDirty()
            self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def padRight():
        doc = 'Right padding'

        def fget(self):
            return self._padRight



        def fset(self, value):
            self._padRight = value
            self.FlagNextObjectsDirty()
            self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def padTop():
        doc = 'Top padding'

        def fget(self):
            return self._padTop



        def fset(self, value):
            self._padTop = value
            self.FlagNextObjectsDirty()
            self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def padBottom():
        doc = 'Bottom padding'

        def fget(self):
            return self._padBottom



        def fset(self, value):
            self._padBottom = value
            self.FlagNextObjectsDirty()
            self.FlagAlignmentDirty()


        return property(**locals())



    @apply
    def display():
        doc = 'Is UI element displayed?'

        def fget(self):
            return self._display



        def fset(self, value):
            if value != self._display:
                self._display = value
                ro = self.renderObject
                if ro:
                    ro.display = value
                self.FlagNextObjectsDirty(lvl=0)
                self.FlagAlignmentDirty()
                self._displayDirty = True


        return property(**locals())



    def SetAlign(self, align):
        if align == self._align:
            return 
        if hasattr(self.renderObject, 'absoluteCoordinates'):
            if align == uiconst.ABSOLUTE:
                self.renderObject.absoluteCoordinates = True
            else:
                self.renderObject.absoluteCoordinates = False
        self._align = align
        if align == uiconst.NOALIGN:
            self._alignFunc = self.UpdateNoAlignment
        elif align == uiconst.TOLEFT:
            self._alignFunc = self.UpdateToLeftAlignment
        elif align == uiconst.TORIGHT:
            self._alignFunc = self.UpdateToRightAlignment
        elif align == uiconst.TOTOP:
            self._alignFunc = self.UpdateToTopAlignment
        elif align == uiconst.TOBOTTOM:
            self._alignFunc = self.UpdateToBottomAlignment
        elif align == uiconst.TOLEFT_PROP:
            self._alignFunc = self.UpdateToLeftProportionalAlignment
        elif align == uiconst.TORIGHT_PROP:
            self._alignFunc = self.UpdateToRightProportionalAlignment
        elif align == uiconst.TOTOP_PROP:
            self._alignFunc = self.UpdateToTopProportionalAlignment
        elif align == uiconst.TOBOTTOM_PROP:
            self._alignFunc = self.UpdateToBottomProportionalAlignment
        elif align == uiconst.TOALL:
            self._alignFunc = self.UpdateToAllAlignment
        elif align == uiconst.ABSOLUTE:
            self._alignFunc = self.UpdateAbsoluteAlignment
        elif align == uiconst.TOPLEFT:
            self._alignFunc = self.UpdateTopLeftAlignment
        elif align == uiconst.TOPRIGHT:
            self._alignFunc = self.UpdateTopRightAlignment
        elif align == uiconst.BOTTOMRIGHT:
            self._alignFunc = self.UpdateBottomRightAlignment
        elif align == uiconst.BOTTOMLEFT:
            self._alignFunc = self.UpdateBottomLeftAlignment
        elif align == uiconst.CENTER:
            self._alignFunc = self.UpdateCenterAlignment
        elif align == uiconst.CENTERBOTTOM:
            self._alignFunc = self.UpdateCenterBottomAlignment
        elif align == uiconst.CENTERTOP:
            self._alignFunc = self.UpdateCenterTopAlignment
        elif align == uiconst.CENTERLEFT:
            self._alignFunc = self.UpdateCenterLeftAlignment
        elif align == uiconst.CENTERRIGHT:
            self._alignFunc = self.UpdateCenterRightAlignment
        elif align == uiconst.ATTACHED:
            self._alignFunc = self.UpdateTopLeftAlignment
        else:
            raise NotImplementedError
        self.FlagAlignmentDirty()
        self.FlagNextObjectsDirty()



    def GetAlign(self):
        return self._align


    align = property(GetAlign, SetAlign)

    @apply
    def name():
        doc = 'Name of this UI element'

        def fget(self):
            return self._name



        def fset(self, value):
            self._name = value
            ro = self.renderObject
            if ro:
                ro.name = unicode(self._name)


        return property(**locals())



    @apply
    def translation():
        doc = '\n            Translation is a tuple of (displayX,displayY). Prefer this over setting\n            x and y separately.\n            '

        def fget(self):
            return (self._displayX, self._displayY)



        def fset(self, value):
            self._displayX = value[0]
            self._displayY = value[1]
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX
                ro.displayY = self._displayY


        return property(**locals())



    @apply
    def displayRect():
        doc = '\n            displayRect is a tuple of (displayX,displayY,displayWidth,displayHeight).\n            Prefer this over setting x, y, width and height separately if all are\n            being set.\n            '

        def fget(self):
            return (self._displayX,
             self._displayY,
             self._displayWidth,
             self._displayHeight)



        def fset(self, value):
            (self._displayX, self._displayY, self._displayWidth, self._displayHeight,) = value
            self._displayX = int(round(self._displayX))
            self._displayY = int(round(self._displayY))
            self._displayWidth = int(round(self._displayWidth))
            self._displayHeight = int(round(self._displayHeight))
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX
                ro.displayY = self._displayY
                ro.displayWidth = self._displayWidth
                ro.displayHeight = self._displayHeight


        return property(**locals())



    @apply
    def displayX():
        doc = 'x-coordinate of render object'

        def fget(self):
            return self._displayX



        def fset(self, value):
            self._displayX = int(round(value))
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX


        return property(**locals())



    @apply
    def displayY():
        doc = 'y-coordinate of render object'

        def fget(self):
            return self._displayY



        def fset(self, value):
            self._displayY = int(round(value))
            ro = self.renderObject
            if ro:
                ro.displayY = self._displayY


        return property(**locals())



    @apply
    def displayWidth():
        doc = 'Width of render object'

        def fget(self):
            return self._displayWidth



        def fset(self, value):
            self._displayWidth = int(round(value))
            ro = self.renderObject
            if ro:
                ro.displayWidth = self._displayWidth


        return property(**locals())



    @apply
    def displayHeight():
        doc = 'Height of render object'

        def fget(self):
            return self._displayHeight



        def fset(self, value):
            self._displayHeight = int(round(value))
            ro = self.renderObject
            if ro:
                ro.displayHeight = self._displayHeight


        return property(**locals())



    @apply
    def pickState():
        doc = 'Pick state of render object'

        def fget(self):
            return self._pickState



        def fset(self, value):
            self._pickState = value
            ro = self.renderObject
            if ro:
                ro.pickState = value


        return property(**locals())



    def FlagNextObjectsDirty(self, lvl = 0):
        flagNextCountStat.Inc()
        if not self.parent:
            return 
        align = self.align
        if align in PUSHALIGNMENTS:
            foundSelf = False
            for each in self.parent.children:
                if each is self:
                    foundSelf = True
                    continue
                if foundSelf and each.display and each.align in AFFECTEDBYPUSHALIGNMENTS:
                    each.FlagAlignmentDirty()




    def Disable(self, *args):
        self.pickState = uiconst.TR2_SPS_OFF



    def Enable(self, *args):
        self.pickState = uiconst.TR2_SPS_ON



    def SetFocus(self, *args):
        pass



    def SendMessage(self, *args, **kwds):
        pass



    def SetHint(self, hint):
        self.hint = hint or ''



    def GetHint(self):
        return getattr(self, 'hint', None)



    def SetDisplayRect(self, displayRect):
        align = self.GetAlign()
        if align != uiconst.NOALIGN:
            return 
        self.displayRect = displayRect



    def SetPadding(self, padLeft = None, padTop = None, padRight = None, padBottom = None):
        if padLeft is not None:
            self.padLeft = padLeft
        if padTop is not None:
            self.padTop = padTop
        if padRight is not None:
            self.padRight = padRight
        if padBottom is not None:
            self.padBottom = padBottom



    def GetPadding(self):
        return (self.padLeft,
         self.padTop,
         self.padRight,
         self.padBottom)



    def SetPosition(self, left, top):
        self.left = left
        self.top = top



    def GetPosition(self):
        return (self.left, self.top)



    def SetSize(self, width, height):
        self.width = width
        self.height = height



    def GetSize(self):
        return (self.width, self.height)



    def UpdateFromRoot(self, doPrint = False):
        chain = [self]
        parent = self.GetParent()
        while parent:
            if not parent.__dict__.get('_alignmentDirty', False):
                break
            chain.insert(0, parent)
            parent = parent.GetParent()
            if isinstance(parent, uicls.UIRoot):
                break

        lvl = 0
        for each in chain:
            each._alignmentDirty = False
            each.UpdateAlignment(ignoreFrameTime=True, hint='UpdateFromRoot', lvl=lvl)
            lvl += 1




    def GetAbsolute(self, doPrint = False):
        if not self.display:
            return (0, 0, 0, 0)
        (w, h,) = self.GetAbsoluteSize()
        (l, t,) = self.GetAbsolutePosition()
        return (l,
         t,
         w,
         h)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAbsoluteSize(self):
        if self.destroyed or not self.display:
            return (0, 0)
        else:
            if self.align in AFFECTEDBYPUSHALIGNMENTS:
                if self._alignmentDirty or self._displayDirty:
                    parent = self.parent
                    if parent:
                        prevParent = None
                        while parent and parent.display:
                            prevParent = parent
                            parent = parent.parent

                        parent = parent or prevParent
                        parent.UpdateAlignmentAsRoot()
                return (self.displayWidth, self.displayHeight)
            return (self.width, self.height)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAbsolutePosition(self):
        if self.destroyed or not self.display:
            return (0, 0)
        if self._alignmentDirty or self._displayDirty:
            parent = self.parent
            if parent:
                prevParent = None
                while parent and parent.display:
                    prevParent = parent
                    parent = parent.parent

                parent = parent or prevParent
                parent.UpdateAlignmentAsRoot()
        if self.renderObject:
            (l, t,) = (int(self.renderObject.displayX), int(self.renderObject.displayY))
        else:
            (l, t,) = (self.displayX, self.displayY)
        if self.align in (uiconst.ABSOLUTE, uiconst.NOALIGN):
            return (l, t)
        parent = self.GetParent()
        while parent and not parent.destroyed:
            l += int(parent.renderObject.displayX)
            t += int(parent.renderObject.displayY)
            if parent.align in (uiconst.ABSOLUTE, uiconst.NOALIGN):
                break
            parent = parent.GetParent()

        return (l, t)



    def GetAbsoluteLeft(self):
        (l, t,) = self.GetAbsolutePosition()
        return l


    absoluteLeft = property(GetAbsoluteLeft)

    def GetAbsoluteTop(self):
        (l, t,) = self.GetAbsolutePosition()
        return t


    absoluteTop = property(GetAbsoluteTop)

    def GetAbsoluteBottom(self):
        (l, t,) = self.GetAbsolutePosition()
        (w, h,) = self.GetAbsoluteSize()
        return t + h


    absoluteBottom = property(GetAbsoluteBottom)

    def GetAbsoluteRight(self):
        (l, t,) = self.GetAbsolutePosition()
        (w, h,) = self.GetAbsoluteSize()
        return l + w


    absoluteRight = property(GetAbsoluteRight)

    def SetState(self, state):
        if state == uiconst.UI_NORMAL:
            self.display = True
            self.pickState = uiconst.TR2_SPS_ON
        elif state == uiconst.UI_DISABLED:
            self.display = True
            self.pickState = uiconst.TR2_SPS_OFF
        elif state == uiconst.UI_HIDDEN:
            self.display = False
        elif state == uiconst.UI_PICKCHILDREN:
            self.display = True
            self.pickState = uiconst.TR2_SPS_CHILDREN



    def GetState(self):
        if not self.display:
            return uiconst.UI_HIDDEN
        if self.pickState == uiconst.TR2_SPS_CHILDREN:
            return uiconst.UI_PICKCHILDREN
        if self.pickState == uiconst.TR2_SPS_ON:
            return uiconst.UI_NORMAL
        if self.pickState == uiconst.TR2_SPS_OFF:
            return uiconst.UI_DISABLED


    state = property(GetState, SetState)

    def _RemoveAttachment(self, attachment):
        if attachment in self._attachedObjects:
            self._attachedObjects.remove(attachment)



    def _AddAttachment(self, attachment):
        if attachment not in self._attachedObjects:
            self._attachedObjects.append(attachment)
            self.UpdateAttachments()



    def ClearAttachTo(self):
        if self._attachedTo:
            self.SetAlign(uiconst.TOPLEFT)
            oldObject = self._attachedTo[0]
            oldObject._RemoveAttachment(self)
            self._attachedTo = None



    def GetMyAttachments(self):
        return self._attachedObjects



    def SetAttachTo(self, toObject, objectPoint, myPoint, offset = None):
        if self._attachedTo:
            oldObject = self._attachedTo[0]
            oldObject._RemoveAttachment(self)
            self._attachedTo = None
        toParent = toObject.GetParent()
        parent = self.GetParent()
        if toParent != parent:
            raise RuntimeError, 'SetAttachTo: toObject has to be on same level as the attachment'
        self.SetAlign(uiconst.ATTACHED)
        self._attachedTo = (toObject,
         objectPoint,
         myPoint,
         offset)
        toObject._AddAttachment(self)



    def FlagAlignmentDirty(self):
        self._alignmentDirty = True
        if self.align == uiconst.NOALIGN:
            uicore.uilib.alignIslands.append(self)
            return 
        parent = self.parent
        if parent:
            parent.FlagChildrenDirty()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAlignmentBudget(self):
        if self.align == uiconst.NOALIGN:
            budget = (0,
             0,
             self.width,
             self.height)
            return budget
        else:
            parent = self.GetParent()
            if parent:
                align = self.GetAlign()
                budget = (0, 0) + parent.GetAbsoluteSize()
                if align in AFFECTEDBYPUSHALIGNMENTS:
                    for each in parent.children:
                        if each is self:
                            return budget
                        budget = each.ConsumeBudget(budget)

                return budget
            print 'SOMEONE TRYING TO GET ALIGNMENT BUDGET FOR CHILD WHICH DOES NOT HAVE PARENT... FATAL',
            print self.name
            log.LogTraceback(extraText='GetAlignmentBudget called on an object with no parent and align={0}'.format(uiutil.GetDisplayAttribute('align', self.align)))
            log.LogError(repr(self))
            return (0, 0, 100, 100)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ConsumeBudget(self, budget, orgBudget):
        consumeBudget = self.display
        align = self.GetAlign()
        if consumeBudget and align in PUSHALIGNMENTS:
            (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
            if align == uiconst.TOLEFT:
                if self._width < 1.0:
                    width = int(float(orgBudget[2]) * self._width)
                else:
                    width = self._width
                budgetLeft = budgetLeft + self._padLeft + width + self._left + self._padRight
                budgetWidth = budgetWidth - self._padLeft - width - self._left - self._padRight
            elif align == uiconst.TORIGHT:
                if self._width < 1.0:
                    width = int(float(orgBudget[2]) * self._width)
                else:
                    width = self._width
                budgetWidth = budgetWidth - self._padLeft - width - self._padRight - self._left
            elif align == uiconst.TOTOP:
                if self._height < 1.0:
                    height = int(float(orgBudget[3]) * self._height)
                else:
                    height = self._height
                budgetTop = budgetTop + self._padTop + height + self._top + self._padBottom
                budgetHeight = budgetHeight - self._padTop - height - self._top - self._padBottom
            elif align == uiconst.TOBOTTOM:
                if self._height < 1.0:
                    height = int(float(orgBudget[3]) * self._height)
                else:
                    height = self._height
                budgetHeight = budgetHeight - self._padTop - height - self._padBottom - self._top
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToLeftAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        displayX = budgetLeft + self._padLeft + self._left
        displayY = budgetTop + self._padTop
        displayHeight = budgetHeight - self._padTop - self._padBottom
        displayWidth = self._width
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetLeft = budgetLeft + self._padLeft + self._width + self._left + self._padRight
            budgetWidth = budgetWidth - self._padLeft - self._width - self._left - self._padRight
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToLeftProportionalAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        width = int(float(orgBudget[2]) * self._width)
        displayX = budgetLeft + self._padLeft + self._left
        displayY = budgetTop + self._padTop
        displayHeight = budgetHeight - self._padTop - self._padBottom
        displayWidth = width
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetLeft = budgetLeft + self._padLeft + width + self._left + self._padRight
            budgetWidth = budgetWidth - self._padLeft - width - self._left - self._padRight
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToRightAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        displayX = budgetLeft + budgetWidth - self._width - self._padRight - self._left
        displayY = budgetTop + self._padTop
        displayHeight = budgetHeight - self._padTop - self._padBottom
        displayWidth = self._width
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetWidth = budgetWidth - self._padLeft - self._width - self._padRight - self._left
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToRightProportionalAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        width = int(float(orgBudget[2]) * self._width)
        displayX = budgetLeft + budgetWidth - width - self._padRight - self._left
        displayY = budgetTop + self._padTop
        displayHeight = budgetHeight - self._padTop - self._padBottom
        displayWidth = width
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetWidth = budgetWidth - self._padLeft - width - self._padRight - self._left
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToTopAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        displayX = budgetLeft + self._padLeft
        displayY = budgetTop + self._padTop + self._top
        displayWidth = budgetWidth - self._padLeft - self._padRight
        displayHeight = self._height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetTop = budgetTop + self._padTop + self._height + self._top + self._padBottom
            budgetHeight = budgetHeight - self._padTop - self._height - self._top - self._padBottom
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToTopProportionalAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        height = int(float(orgBudget[3]) * self._height)
        displayX = budgetLeft + self._padLeft
        displayY = budgetTop + self._padTop + self._top
        displayWidth = budgetWidth - self._padLeft - self._padRight
        displayHeight = height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetTop = budgetTop + self._padTop + height + self._top + self._padBottom
            budgetHeight = budgetHeight - self._padTop - height - self._top - self._padBottom
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToBottomAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        displayX = budgetLeft + self._padLeft
        displayY = budgetTop + budgetHeight - self._height - self._padBottom - self._top
        displayWidth = budgetWidth - self._padLeft - self._padRight
        displayHeight = self._height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetHeight = budgetHeight - self._padTop - self._height - self._padBottom - self._top
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToBottomProportionalAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        height = int(float(orgBudget[3]) * self._height)
        displayX = budgetLeft + self._padLeft
        displayY = budgetTop + budgetHeight - height - self._padBottom - self._top
        displayWidth = budgetWidth - self._padLeft - self._padRight
        displayHeight = height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        if self.display:
            budgetHeight = budgetHeight - self._padTop - height - self._padBottom - self._top
            budget = (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateToAllAlignment(self, budget, orgBudget):
        (budgetLeft, budgetTop, budgetWidth, budgetHeight,) = budget
        displayX = budgetLeft + self._padLeft + self._left
        displayY = budgetTop + self._padTop + self._top
        displayWidth = budgetWidth - self._padLeft - self._padRight - self._left - self._width
        displayHeight = budgetHeight - self._padTop - self._padBottom - self._top - self._height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAbsoluteAlignment(self, budget, orgBudget):
        (self._left, self._top, self._width, self._height,) = (self.left,
         self.top,
         self.width or 0,
         self.height or 0)
        displayX = self._left
        displayY = self._top
        displayWidth = self._width
        displayHeight = self._height
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateTopLeftAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = self._left + self._padLeft
        displayY = self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateTopRightAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = budgetWidth - self._width - self._left + self._padLeft
        displayY = self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateBottomRightAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = budgetWidth - self._width - self._left + self._padLeft
        displayY = budgetHeight - self._height - self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateBottomLeftAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = self._left + self._padLeft
        displayY = budgetHeight - self._height - self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCenterAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = int((budgetWidth - self._width) / 2 + self._left) + self._padLeft
        displayY = int((budgetHeight - self._height) / 2 + self._top) + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCenterBottomAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = int((budgetWidth - self._width) / 2 + self._left) + self._padLeft
        displayY = budgetHeight - self._height - self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCenterTopAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = int((budgetWidth - self._width) / 2 + self._left) + self._padLeft
        displayY = self._top + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCenterLeftAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = self._left + self._padLeft
        displayY = int((budgetHeight - self._height) / 2 + self._top) + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCenterRightAlignment(self, budget, orgBudget):
        parent = self.GetParent()
        (budgetWidth, budgetHeight,) = (parent.displayWidth, parent.displayHeight)
        displayX = budgetWidth - self._width - self._left + self._padLeft
        displayY = int((budgetHeight - self._height) / 2 + self._top) + self._padTop
        displayWidth = self._width - self._padLeft - self._padRight
        displayHeight = self._height - self._padTop - self._padBottom
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateNoAlignment(self, budget, orgBudget):
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAlignmentAsRoot(self):
        self._alignmentDirty = False
        self.displayWidth = self.width
        self.displayHeight = self.height
        if hasattr(self, 'children'):
            budget = (0,
             0,
             self.displayWidth,
             self.displayHeight)
            orgBudget = (0,
             0,
             self.displayWidth,
             self.displayHeight)
            for each in self.children:
                if each.display:
                    budget = each.Traverse(budget, orgBudget, 1)




    def Traverse(self, mbudget, orgBudget, lvl):
        if self.destroyed:
            return mbudget
        if self._alignmentDirty:
            mbudget = self.UpdateAlignment(mbudget, orgBudget, hint='traverse', lvl=lvl)
        else:
            mbudget = self.ConsumeBudget(mbudget, orgBudget)
        return mbudget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAlignment(self, budget, orgBudget, hint = None, lvl = 0, **kwds):
        alignCountStat.Inc()
        if self.destroyed:
            return budget
        align = self.align
        if align == uiconst.NOALIGN:
            self.UpdateAlignmentAsRoot()
            return budget
        self._alignmentDirty = False
        preDX = self.displayX
        preDY = self.displayY
        preDWidth = self.displayWidth
        preDHeight = self.displayHeight
        budget = self._alignFunc(budget, orgBudget)
        sizeChange = preDWidth != self.displayWidth or preDHeight != self.displayHeight
        posChange = preDX != self.displayX or preDY != self.displayY
        if sizeChange or posChange:
            if self._OnResize.im_func != Base._OnResize.im_func:
                self._OnResize()
        if sizeChange:
            self._OnSizeChange_NoBlock(self.displayWidth, self.displayHeight)
        self.UpdateAttachments()
        if sizeChange or self._displayDirty:
            children = getattr(self, 'children', None)
            if children:
                for child in children:
                    if child.display:
                        child._alignmentDirty = True
                        if self._displayDirty:
                            child._displayDirty = True

            self.FlagNextObjectsDirty(lvl=lvl)
        self._displayDirty = False
        return budget



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAttachments(self):
        attachedObjects = getattr(self, '_attachedObjects', None)
        if attachedObjects:
            for object in attachedObjects:
                object.UpdateAttachedPosition()




    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateAttachedPosition(self):
        parent = self.GetParent()
        if self._attachedTo and parent:
            (toObject, objectPoint, myPoint, offset,) = self._attachedTo
            (al, at, aw, ah,) = (toObject.displayX,
             toObject.displayY,
             toObject.displayWidth,
             toObject.displayHeight)
            if objectPoint in (uiconst.ANCH_TOPLEFT, uiconst.ANCH_CENTERTOP, uiconst.ANCH_TOPRIGHT):
                yPoint = at
            elif objectPoint in (uiconst.ANCH_CENTERLEFT, uiconst.ANCH_CENTER, uiconst.ANCH_CENTERRIGHT):
                yPoint = at + ah / 2
            elif objectPoint in (uiconst.ANCH_BOTTOMLEFT, uiconst.ANCH_CENTERBOTTOM, uiconst.ANCH_BOTTOMRIGHT):
                yPoint = at + ah
            if myPoint in (uiconst.ANCH_TOPLEFT, uiconst.ANCH_CENTERTOP, uiconst.ANCH_TOPRIGHT):
                self.top = yPoint
            elif myPoint in (uiconst.ANCH_CENTERLEFT, uiconst.ANCH_CENTER, uiconst.ANCH_CENTERRIGHT):
                self.top = yPoint - self.height / 2
            elif myPoint in (uiconst.ANCH_BOTTOMLEFT, uiconst.ANCH_CENTERBOTTOM, uiconst.ANCH_BOTTOMRIGHT):
                self.top = yPoint - self.height
            if objectPoint in (uiconst.ANCH_TOPLEFT, uiconst.ANCH_CENTERLEFT, uiconst.ANCH_BOTTOMLEFT):
                xPoint = al
            elif objectPoint in (uiconst.ANCH_CENTERTOP, uiconst.ANCH_CENTER, uiconst.ANCH_CENTERBOTTOM):
                xPoint = al + aw / 2
            elif objectPoint in (uiconst.ANCH_TOPRIGHT, uiconst.ANCH_CENTERRIGHT, uiconst.ANCH_BOTTOMRIGHT):
                xPoint = al + aw
            if myPoint in (uiconst.ANCH_TOPLEFT, uiconst.ANCH_CENTERLEFT, uiconst.ANCH_BOTTOMLEFT):
                self.left = xPoint
            elif myPoint in (uiconst.ANCH_CENTERTOP, uiconst.ANCH_CENTER, uiconst.ANCH_CENTERBOTTOM):
                self.left = xPoint - self.width / 2
            elif myPoint in (uiconst.ANCH_TOPRIGHT, uiconst.ANCH_CENTERRIGHT, uiconst.ANCH_BOTTOMRIGHT):
                self.left = xPoint - self.width
            if offset:
                (ox, oy,) = offset
                self.left += ox
                self.top += oy



    def Toggle(self, *args):
        if self.IsHidden():
            self.Show()
        else:
            self.Hide()



    def Hide(self, *args):
        self.display = False



    def Show(self, *args):
        self.display = True



    def IsHidden(self):
        return not self.display



    def FindParentByName(self, parentName):
        parent = self.GetParent()
        while parent:
            if parent.name == parentName:
                return parent
            parent = parent.GetParent()




    @apply
    def cursor():
        doc = 'Cursor value of this object. Triggers cursor update when set'

        def fget(self):
            return self._cursor



        def fset(self, value):
            self._cursor = value
            uicore.CheckCursor()


        return property(**locals())



    def _OnClose(self, *args, **kw):
        pass



    def _OnResize(self, *args):
        pass



    def _OnSizeChange_NoBlock(self, *args):
        pass



    def OnMouseUp(self, *args):
        pass



    def OnMouseDown(self, *args):
        pass



    def OnMouseEnter(self, *args):
        pass



    def OnMouseExit(self, *args):
        pass



    def OnMouseHover(self, *args):
        pass



    def OnClick(self, *args):
        pass



    @apply
    def __bluetype__():
        doc = 'legacy trinity name of object'

        def fget(self):
            if self.__renderObject__:
                return self.__renderObject__().__bluetype__


        return property(**locals())



    @apply
    def __typename__():
        doc = 'legacy type name of object'

        def fget(self):
            if self.__renderObject__:
                return self.__renderObject__().__typename__


        return property(**locals())



exports = {'uiconst.AFFECTEDBYPUSHALIGNMENTS': AFFECTEDBYPUSHALIGNMENTS,
 'uiconst.PUSHALIGNMENTS': PUSHALIGNMENTS}

