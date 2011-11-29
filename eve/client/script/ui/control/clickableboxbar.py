import util
import uix
import blue
import uicls
import uiconst
import localization

class ClickableBoxBar(uicls.Container):
    __guid__ = 'uicls.ClickableBoxBar'
    __nonpersistvars__ = ['boxes',
     'boxValues',
     'value',
     'boxWidth',
     'boxHeight',
     'boxMargin',
     'boxSpacing',
     'minimumIndex',
     'maximumIndex',
     'isReadOnly',
     'colors',
     'hintFormat']
    COLOR_BELOWMINIMUM = 0
    COLOR_SELECTED = 1
    COLOR_UNSELECTED = 2
    COLOR_ABOVEMAXIMUM = 3
    default_name = 'ClickableBoxBar'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.isTabStop = 0
        self.boxes = []
        self.value = None
        self.minimumIndex = None
        self.maximumIndex = None
        self.isReadOnly = False
        self.colors = {}
        self.hintFormat = None
        numBoxes = attributes.get('numBoxes')
        boxValues = attributes.get('boxValues', [])
        initialValue = attributes.get('initialValue')
        boxWidth = attributes.get('boxWidth', 20)
        boxHeight = attributes.get('boxHeight', 20)
        boxMargin = attributes.get('boxMargin', 2)
        boxSpacing = attributes.get('boxSpacing', 1)
        minimumValue = attributes.get('minimumValue')
        maximumValue = attributes.get('maximumValue')
        readonly = attributes.get('readonly', False)
        colorDict = attributes.get('colorDict')
        backgroundColor = attributes.get('backgroundColor')
        hintFormat = attributes.get('hintFormat')
        subHint = attributes.get('subHint')
        aboveMaxHint = attributes.get('aboveMaxHint')
        belowMaxHint = attributes.get('belowMaxHint')
        if boxValues is not None and len(boxValues) > 0 and len(boxValues) != numBoxes:
            raise RuntimeError('Unable to create a ClickableBoxBar with a defined boxValues array of a different size than the number of boxes')
        if boxValues is None or len(boxValues) == 0:
            self.boxValues = range(1, numBoxes + 1)
        else:
            self.boxValues = boxValues
        if initialValue is not None and initialValue not in self.boxValues:
            raise RuntimeError('Unable to create a ClickableBoxBar with an initialValue outside its range of values')
        if minimumValue is not None and minimumValue - 1 not in self.boxValues:
            raise RuntimeError('Unable to create a ClickableBoxBar with a minimumValue outside its range of values')
        self.boxWidth = boxWidth
        self.boxHeight = boxHeight
        self.boxMargin = boxMargin
        self.boxSpacing = boxSpacing
        self.isReadOnly = readonly
        self.colors = colorDict
        self.hintFormat = hintFormat
        self.aboveMaxHint = aboveMaxHint
        self.belowMaxHint = belowMaxHint
        if colorDict is None:
            self.colors = {self.COLOR_BELOWMINIMUM: (0.95, 0.95, 0.95, 0.75),
             self.COLOR_SELECTED: (0.5, 1.0, 0.5, 0.75),
             self.COLOR_UNSELECTED: (0.4, 0.4, 0.4, 0.75),
             self.COLOR_ABOVEMAXIMUM: (0.1, 0.1, 0.1, 0.75)}
        if minimumValue is not None:
            if minimumValue in self.boxValues:
                self.minimumIndex = self.boxValues.index(minimumValue)
            else:
                self.minimumIndex = len(boxValues)
        if maximumValue is not None:
            self.maximumIndex = self.boxValues.index(maximumValue)
        i = 0
        while i < numBoxes:
            clickable = not self.isReadOnly
            initialState = self.COLOR_UNSELECTED
            if self.minimumIndex is not None:
                clickable = clickable and i >= self.minimumIndex
                if i < self.minimumIndex:
                    initialState = self.COLOR_BELOWMINIMUM
            if self.maximumIndex is not None:
                clickable = clickable and i <= self.maximumIndex
                if initialState == self.COLOR_UNSELECTED and i > self.maximumIndex:
                    initialState = self.COLOR_ABOVEMAXIMUM
            self.boxes.append(self.CreateBox(i, self.colors, clickable, initialState, subHint))
            i += 1

        bgColor = backgroundColor
        if backgroundColor is None:
            bgColor = (0.0, 0.0, 0.0, 0.9)
        uicls.Fill(parent=self, color=bgColor)
        if initialValue is not None:
            self.SetValue(initialValue)
        self.CreateUIElements()



    def CreateUIElements(self):
        self.sr.frame = uicls.Frame(parent=self, padding=(-1, -1, -1, -1), color=(0.6, 0.6, 0.6, 1.0), idx=0)
        self.sr.frame.state = uiconst.UI_DISABLED



    def Increment(self):
        if self.value not in self.boxValues:
            idx = -1
        else:
            idx = self.boxValues.index(self.value)
        if idx + 1 >= len(self.boxValues) or self.maximumIndex is not None and idx + 1 > self.maximumIndex:
            return False
        self._OnBoxClicked(idx + 1)
        return True



    def Decrement(self):
        if self.value not in self.boxValues:
            return False
        idx = self.boxValues.index(self.value)
        if idx == 0:
            oldValue = self.value
            self.value = 0
            for x in xrange(0, len(self.boxValues)):
                self.boxes[x].SetColor(self.COLOR_UNSELECTED)

            self.OnValueChanged(oldValue, self.value)
            return True
        if idx - 1 < 0 or self.minimumIndex is not None and idx - 1 < self.minimumIndex:
            return False
        self._OnBoxClicked(idx - 1)
        return True



    def GetValue(self):
        return self.value



    def SetValue(self, value):
        if value == self.value:
            return 
        if value not in self.boxValues:
            self.value = 0
            for x in xrange(0, len(self.boxValues)):
                self.boxes[x].SetColor(self.COLOR_UNSELECTED)

            return 
        idx = self.boxValues.index(value)
        self._OnBoxClicked(idx)



    def CreateBox(self, boxIndex, colors, clickable, initialState, subHint):
        boxLeft = self.boxMargin + boxIndex * (self.boxSpacing + self.boxWidth)
        newBox = uicls.ClickableBoxBarBox(name='box', parent=self, align=uiconst.TOPLEFT, left=boxLeft, top=self.boxMargin, height=self.boxHeight, width=self.boxWidth, state=uiconst.UI_NORMAL)
        newBox.Startup(boxIndex, defaultColor=colors[initialState], stateColors=colors, clickable=clickable, subHint=subHint)
        return newBox



    def _OnBoxClicked(self, boxIndex):
        if self.value is not None and not self.OnAttemptBoxClicked(self.value, self.boxValues[boxIndex]):
            return 
        startIdx = 0 if self.minimumIndex is None else self.minimumIndex
        finishIdx = self.maximumIndex + 1 if self.maximumIndex is not None else len(self.boxValues)
        if self.minimumIndex is not None:
            for x in xrange(0, min(startIdx, boxIndex + 1)):
                self.boxes[x].SetColor(self.COLOR_BELOWMINIMUM)

        for x in xrange(startIdx, boxIndex + 1):
            self.boxes[x].SetColor(self.COLOR_SELECTED)

        for x in xrange(boxIndex + 1, finishIdx):
            self.boxes[x].SetColor(self.COLOR_UNSELECTED)

        oldValue = self.value
        self.value = self.boxValues[boxIndex]
        self.OnBoxClicked(boxIndex, self.value)
        if oldValue != self.value:
            self.OnValueChanged(oldValue, self.value)



    def _OnBoxDoubleClicked(self, boxIndex):
        self.OnBoxDoubleClicked(boxIndex, self.boxValues[boxIndex])



    def _OnClose(self, *args):
        self.boxes = None
        self.boxValues = None



    def OnBoxClicked(self, boxIndex, boxValue):
        pass



    def OnBoxDoubleClicked(self, boxIndex, boxValue):
        pass



    def OnValueChanged(self, oldValue, newValue):
        pass



    def OnAttemptBoxClicked(self, oldValue, newValue):
        return True



    def GetHint(self, box, *args):
        hintText = ''
        if self.hintFormat is not None:
            hintText = localization.GetByLabel(self.hintFormat, value=self.value)
        if box.identifier < self.minimumIndex and self.belowMaxHint is not None:
            hintText += self.belowMaxHint % self.GetIndexValue(box.identifier)
        if box.identifier > self.maximumIndex and self.aboveMaxHint is not None:
            hintText += self.aboveMaxHint % self.GetIndexValue(box.identifier)
        if hintText == '':
            return 
        return hintText



    def GetIndexValue(self, index):
        if index < 0 or index >= len(self.boxValues):
            return None
        else:
            return self.boxValues[index]




class ClickableBoxBarBox(uicls.Container):
    __guid__ = 'uicls.ClickableBoxBarBox'
    __nonpersistvars__ = ['identifier',
     'defaultColor',
     'colors',
     'fill',
     'subHint']

    def init(self):
        self.identifier = None
        self.defaultColor = None
        self.colors = None
        self.fill = None
        self.subHint = None



    def Startup(self, boxIdentifier, defaultColor = (1.0, 1.0, 1.0, 0.5), stateColors = {}, clickable = True, subHint = None):
        self.identifier = boxIdentifier
        self.defaultColor = defaultColor
        self.colors = stateColors
        self.clickable = clickable
        self.subHint = subHint
        self.SetupUIElements()



    def SetupUIElements(self):
        self.sr.highlight = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.4))
        self.sr.highlight.state = uiconst.UI_HIDDEN
        self.fill = uicls.Fill(parent=self, color=self.defaultColor)



    def SetColor(self, state):
        if state in self.colors:
            newColor = self.colors[state]
        else:
            newColor = self.defaultColor
        self.fill.SetRGBA(*newColor)



    def OnClick(self, *args):
        if self.clickable:
            self.parent._OnBoxClicked(self.identifier)



    def OnDoubleClick(self, *args):
        if self.clickable:
            self.parent._OnDoubleClick(self.identifier)



    def OnMouseEnter(self, *args):
        if self.clickable:
            self.sr.highlight.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.clickable:
            self.sr.highlight.state = uiconst.UI_HIDDEN



    def GetHint(self, *args):
        if self.subHint is not None and self.clickable:
            hintText = self.parent.GetHint(self, *args)
            if hintText is None:
                hintText = ''
            hintText += self.subHint % self.parent.GetIndexValue(self.identifier)
            return hintText
        else:
            return self.parent.GetHint(self, *args)




