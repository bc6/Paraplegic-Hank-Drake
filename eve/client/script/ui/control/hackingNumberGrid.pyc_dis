#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/hackingNumberGrid.py
import uicls
import uiconst
import log
import uthread
import random
import blue
import math

class HackingNumberGrid(uicls.Container):
    __guid__ = 'uicls.HackingNumberGrid'
    default_name = 'hackingNumberGrid'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.cycling = False
        self.cyclingThread = None
        self.numCellRows = attributes.get('numCellRows', 5)
        maxCellsPerRow = attributes.get('maxCellsPerRow', 5)
        cellForegroundColor = attributes.get('cellForegroundColor', None)
        cellBackgroundColor = attributes.get('cellBackgroundColor', None)
        self.cellHeight = attributes.get('cellHeight', 20)
        self.cellWidth = attributes.get('cellWidth', 20)
        self.cellTextSize = attributes.get('cellTextSize', 16)
        self.cellsPerRow = attributes.get('cellsPerRow', 5)
        self.deadCells = []
        self.liveCells = []
        self.doneCells = []
        self.cellGlyphs = ['0',
         '1',
         '2',
         '3',
         '4',
         '5',
         '6',
         '7',
         '8',
         '9',
         'A',
         'B',
         'C',
         'D',
         'E',
         'F']
        self.cellRows = []
        self.cellRowContainers = []
        self.cellPaddingVertical = 0
        self.cellPaddingHorizontal = 0
        if cellForegroundColor is None:
            cellForegroundColor = (0.75, 0.0, 0.0, 0.75)
        if cellBackgroundColor is None:
            cellBackgroundColor = (0.5, 0.5, 0.5, 0.25)
        self.cellBackgroundColor = cellBackgroundColor
        self.progressColor = cellForegroundColor
        self.doneColor = (0.0, 0.5, 0.0, 0.5)
        self.flashColor = (0.75, 0.75, 0.75, 0.75)
        uicls.Frame(parent=self, color=(0.7, 0.7, 0.7, 0.5), idx=0)
        for x in xrange(0, self.numCellRows):
            newRow = []
            newRowContainer = uicls.Container(parent=self, name='hackingCellRow', align=uiconst.TOTOP, state=uiconst.UI_DISABLED, pos=(0,
             0,
             self.width,
             self.cellHeight))
            for y in xrange(0, self.cellsPerRow):
                newRow.append(self.CreateCell(newRowContainer, self.cellHeight, self.cellWidth, cellBackgroundColor, cellForegroundColor))

            self.cellRows.append(newRow)
            self.cellRowContainers.append(newRowContainer)

        self.cellRowSemaphore = uthread.Semaphore()

    def IsCycling(self):
        return self.cyclingThread is not None

    def CreateCell(self, parent, height, width, backgroundColorTuple, foregroundColorTuple):
        newCell = uicls.Container(parent=parent, name='hackingCell', align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, pos=(0,
         0,
         width,
         height), padding=(self.cellPaddingHorizontal,
         self.cellPaddingVertical,
         self.cellPaddingHorizontal,
         self.cellPaddingVertical))
        newCell.sr.background = uicls.Fill(parent=newCell, color=backgroundColorTuple)
        newCellFill = uicls.Container(parent=newCell, name='hackFill', align=uiconst.TOPLEFT, pos=(0,
         0,
         width,
         height), padding=(self.cellPaddingHorizontal,
         self.cellPaddingVertical,
         self.cellPaddingHorizontal,
         self.cellPaddingVertical))
        newCellFill.sr.background = uicls.Fill(parent=newCellFill, color=foregroundColorTuple)
        newCellFill.opacity = 0.0
        newCell.sr.fill = newCellFill
        newCell.sr.text = uicls.EveHeaderMedium(text=random.choice(self.cellGlyphs), parent=newCell, align=uiconst.CENTER, fontsize=self.cellTextSize, height=height, state=uiconst.UI_DISABLED)
        return newCell

    def SetProgress(self, progress):
        if self.cyclingThread is None:
            return
        progress = min(max(float(progress), 0.0), 1.0)
        self.cellRowSemaphore.acquire()
        try:
            numLockedCells = int(math.floor(progress * self.numCellRows * self.cellsPerRow))
            if numLockedCells < len(self.doneCells):
                returnedCells = self.doneCells[numLockedCells:]
                self.doneCells = self.doneCells[:numLockedCells]
                for cell in returnedCells:
                    cell.sr.background.SetRGBA(*self.cellBackgroundColor)
                    cell.sr.fill.opacity = 0.0
                    cell.sr.fill.sr.background.SetRGBA(*self.progressColor)
                    self.deadCells.append(cell)

            elif numLockedCells > len(self.doneCells):
                newlyLockedCells = random.sample(self.deadCells + self.liveCells, numLockedCells - len(self.doneCells))
                for cell in newlyLockedCells:
                    if cell in self.deadCells:
                        self.deadCells.remove(cell)
                    if cell in self.liveCells:
                        self.liveCells.remove(cell)
                    cell.sr.background.SetRGBA(*self.doneColor)
                    cell.sr.fill.sr.background.SetRGBA(*self.flashColor)
                    cell.sr.fill.opacity = 1.0
                    self.doneCells.append(cell)

        finally:
            self.cellRowSemaphore.release()

    def BeginColorCycling(self):
        if self.cyclingThread is not None:
            return
        self.state = uiconst.UI_DISABLED
        self.cycling = True
        self.deadCells = []
        self.liveCells = []
        self.doneCells = []
        for row in self.cellRows:
            for cell in row:
                cell.sr.background.SetRGBA(*self.cellBackgroundColor)
                cell.sr.fill.sr.background.SetRGBA(*self.progressColor)
                if cell.sr.fill.opacity <= 0.0:
                    self.deadCells.append(cell)

        self.cyclingThread = uthread.new(self._ColorCycle)

    def _ColorCycle(self):
        while 1:
            blue.pyos.synchro.SleepWallclock(100)
            self.cellRowSemaphore.acquire()
            try:
                if self.cycling:
                    newlyRevivedCell = None
                    if len(self.deadCells) > 0:
                        newlyRevivedCell = random.choice(self.deadCells)
                        newlyRevivedCell.sr.fill.opacity = 1.0
                        self.deadCells.remove(newlyRevivedCell)
                    for cell in self.deadCells:
                        cell.sr.text.text = random.choice(self.cellGlyphs)

                    for cell in self.liveCells[:]:
                        cell.sr.text.text = random.choice(self.cellGlyphs)
                        cell.sr.fill.opacity -= 0.05
                        if cell.sr.fill.opacity <= 0.0:
                            cell.sr.fill.opacity = 0.0
                            self.liveCells.remove(cell)
                            self.deadCells.append(cell)

                    if newlyRevivedCell is not None:
                        self.liveCells.append(newlyRevivedCell)
                else:
                    for cell in self.liveCells:
                        if cell.sr.fill.opacity > 0.0:
                            cell.sr.fill.opacity = max(0.0, cell.sr.fill.opacity - 0.05)

                for cell in self.doneCells:
                    if cell.sr.fill.opacity > 0.0:
                        cell.sr.fill.opacity = max(0.0, cell.sr.fill.opacity - 0.05)

            finally:
                self.cellRowSemaphore.release()

    def StopColorCycling(self):
        self.cycling = False
        uthread.new(self._Finish)

    def _Finish(self):
        blue.pyos.synchro.SleepWallclock(500)
        if self and not self.destroyed and self.cyclingThread is not None:
            self.cyclingThread.kill()
            self.cyclingThread = None