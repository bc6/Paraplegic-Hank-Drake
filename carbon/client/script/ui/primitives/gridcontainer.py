import uicls
import uiconst
import trinity
import bluepy
import math

class GridContainer(uicls.Container):
    __guid__ = 'uicls.GridContainer'
    default_name = 'gridContainer'
    default_columns = 0
    default_lines = 0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.columns = attributes.get('columns', self.default_columns)
        self.lines = attributes.get('lines', self.default_lines)



    @apply
    def lines():
        doc = 'Number of lines in the grid'

        def fget(self):
            return self._lines



        def fset(self, value):
            self._lines = value
            self.FlagMyChildrenAlignmentDirty()


        return property(**locals())



    @apply
    def columns():
        doc = 'Number of columns in the grid'

        def fget(self):
            return self._columns



        def fset(self, value):
            self._columns = value
            self.FlagMyChildrenAlignmentDirty()


        return property(**locals())



    def FlagMyChildrenAlignmentDirty(self):
        self.FlagAlignmentDirty()
        for each in self.children:
            each._alignmentDirty = True




    def Traverse(self, mbudget, orgBudget, lvl):
        if self.destroyed:
            return mbudget
        if self._alignmentDirty:
            mbudget = self.UpdateAlignment(mbudget, orgBudget, hint='traverse', lvl=lvl)
            self._childrenDirty = True
        else:
            mbudget = self.ConsumeBudget(mbudget, orgBudget)
        if self._childrenDirty:
            numChildren = len(self.children)
            numColumns = self.columns
            numLines = self.lines
            if numColumns < 1:
                if numLines > 0:
                    numColumns = int(float(numChildren) / float(numLines) + 0.5)
                    if numColumns * numLines < numChildren:
                        numColumns += 1
            if numLines < 1:
                if numColumns < 1:
                    aspectRatio = float(self.displayWidth) / float(self.displayHeight)
                    numColumns = int(math.sqrt(numChildren) * aspectRatio + 0.5)
                    numLines = int(float(numChildren) / float(numColumns) + 0.5)
                    if numColumns * numLines < numChildren:
                        numLines += 1
                    if self.displayWidth > self.displayHeight:
                        while numColumns * numLines > numChildren:
                            numColumns -= 1

                        if numColumns * numLines < numChildren:
                            numColumns += 1
                    else:
                        while numColumns * numLines > numChildren:
                            numLines -= 1

                        if numColumns * numLines < numChildren:
                            numLines += 1
                else:
                    numLines = int(float(numChildren) / float(numColumns) + 0.5)
                    if numColumns * numLines < numChildren:
                        numLines += 1
            w = int(self.displayWidth / numColumns + 0.5)
            h = int(self.displayHeight / numLines + 0.5)
            for line in xrange(numLines):
                for column in xrange(numColumns):
                    ix = line * numColumns + column
                    if ix < numChildren:
                        budget = (w * column,
                         h * line,
                         w,
                         h)
                        orgBudget = (w * column,
                         h * line,
                         w,
                         h)
                        child = self.children[ix]
                        child._alignmentDirty = True
                        child.Traverse(budget, orgBudget, lvl=lvl + 1)


            self._childrenDirty = False
        return mbudget




