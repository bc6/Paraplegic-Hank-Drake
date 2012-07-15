#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/edit_components.py
import blue
import util
import html
import _weakref
import base
import parser
import types
import uthread
import service
import sys
import log
import uiutil
import uicls
import uiconst

class hr(uicls.SE_BaseClassCore):
    __guid__ = 'uicls.SE_hr'
    __params__ = []

    def Startup(self, *args):
        self.sr.leftmargin = uicls.Container(name='leftmargin', parent=self, align=uiconst.TOLEFT)
        self.sr.rightmargin = uicls.Container(name='rightmargin', parent=self, align=uiconst.TORIGHT)
        self.sr.line = uicls.Container(name='lineparent', parent=self)

    def Load(self, node):
        self.sr.leftmargin.width = node.Get('leftmargin', 0)
        self.sr.rightmargin.width = node.Get('rightmargin', 0)
        uiutil.Flush(self.sr.line)
        uicls.Fill(parent=self.sr.line, color=uiutil.ParseHTMLColor(node.attrs.color or '#88ffffff', 1))
        align = uiconst.RELATIVE
        if node.attrs.width:
            if unicode(node.attrs.width).endswith('%'):
                node.attrs.width = self.sr.node.scroll.GetContentWidth() * int(node.attrs.width[:-1]) / 100
            self.sr.line.width = int(node.attrs.width)
            if node.attrs.align and node.attrs.align.lower() in ('left', 'right'):
                if node.attrs.align.lower() == 'right':
                    align = uiconst.TORIGHT
                else:
                    align = uiconst.TOLEFT
            elif node.attrs.align is None:
                align = uiconst.RELATIVE
            else:
                align = uiconst.CENTER
        else:
            self.sr.line.left = self.sr.line.width = 0
            align = uiconst.TOALL
        self.sr.line.SetAlign(align)

    def GetHeight(self, *args):
        node, width = args
        if node.attrs.size:
            node.height = int(node.attrs.size)
        else:
            node.height = 1
        return node.height


class VirtualTable(uicls.SE_BaseClassCore):
    __guid__ = 'uicls.SE_table'

    def Startup(self, browser, *args):
        self.browser = _weakref.proxy(browser)
        self.taken = []
        self.tableloaded = 0
        self.name = 'table'
        self.sr.cells = None
        attrs = self.data.attrs
        self.charset = attrs.Get('charset', 'cp1252')
        self.stack = self.browser.attrStack[-1].copy()
        if not self.tableloaded:
            self.RefreshSizes()
            if self.destroyed:
                return
            s = self.stack
            self.AddBackground(self, s)
            self.tableloaded = 1

    def Load(self):
        if not self.loaded:
            self.loaded = 1
            uthread.new(self.Load_thread).context = 'uicls.SE_table.Load'

    def Load_thread(self):
        while not getattr(self, 'tableloaded', None):
            blue.pyos.synchro.SleepWallclock(50)

        if self.destroyed:
            return
        self.state = uiconst.UI_PICKCHILDREN
        if self.sr.cells:
            for cell in self.sr.cells:
                cell.LoadContent(cell.sr.lines)

    def GetValue(self):
        selectionString = ''
        row = 0
        col = 0
        for cell in self.children:
            if getattr(cell, '__guid__', None) != 'table.Cell':
                continue
            if cell.rowIdx != row:
                selectionString += '\r\n'
            for cellentry in cell.sr.content.children:
                if hasattr(cellentry, 'GetCopyData'):
                    selectionString += cellentry.GetCopyData(0, -1) or ''

            selectionString += '\t'
            row = cell.rowIdx

        return selectionString

    def AddBackground(self, where, s):
        for i, side in enumerate(['top',
         'left',
         'right',
         'bottom']):
            if s['border-%s-width' % side]:
                align = [uiconst.TOTOP,
                 uiconst.TOLEFT,
                 uiconst.TORIGHT,
                 uiconst.TOBOTTOM][i]
                uicls.Line(parent=where, align=align, weight=s['border-%s-width' % side], color=s['border-%s-color' % side], idx=0)

        if s['background-image'] and where.sr.background:
            browser = uiutil.GetBrowser(self)
            currentURL = None
            if browser:
                currentURL = browser.sr.currentURL
            texture, tWidth, tHeight = sm.GetService('browserImage').GetTextureFromURL(s['background-image'], currentURL, fromWhere='VirtualTable::AddBackground')
            pic = uicls.Sprite()
            pic.left = pic.top = 0
            pic.width = tWidth
            pic.height = tHeight
            pic.texture = texture
            row = uicls.Container(name='row', align=uiconst.TOTOP, pos=(0,
             0,
             0,
             tHeight), clipChildren=1)
            if s['background-repeat'] in ('repeat', 'repeat-x'):
                for x in xrange(max(where.width / tWidth, 2) + 1):
                    row.children.append(pic.CopyTo())
                    pic.left += pic.width

            else:
                row.children.append(pic.CopyTo())
            if s['background-repeat'] in ('repeat', 'repeat-y'):
                for y in xrange(max(where.height / tHeight, 2) + 1):
                    row.height = min(where.height - tHeight * y, row.height)
                    where.sr.background.children.append(row.CopyTo())

            else:
                where.sr.background.children.append(row.CopyTo())
        if s['background-color']:
            uicls.Fill(parent=where, color=s['background-color'])

    def GetInt(self, string):
        value = filter(lambda x: x in '0123456789', unicode(string))
        try:
            value = int(value)
        except:
            sys.exc_clear()

        return value

    def RefreshSizes(self):
        self.drows = []
        self.dcols = []
        self.fcols = []
        if not self or self.destroyed:
            return
        w = self.data.attrs.Get('width', None)
        contentWidth = self.browser.GetContentWidth()
        singleWordMax = contentWidth - self.browser.xmargin * 2
        if w:
            if isinstance(w, basestring) and (w.endswith('%') or w.endswith('\x89')):
                w = self.GetInt(w)
                w = int(float(w) / 100.0 * singleWordMax)
            else:
                w = self.GetInt(w)
        h = self.data.attrs.Get('height', None)
        if h and isinstance(h, basestring) and (h.endswith('%') or h.endswith('\x89')):
            h = self.GetInt(h)
            if self.browser.sr.clipper:
                h = float(h) / 100.0 * self.browser.sr.clipperHeight
            else:
                h = float(h) / 100.0 * self.browser.height
        else:
            h = self.GetInt(h)
        for col in self.data.attrs.Get('colgroups', []):
            if unicode(col).isdigit():
                self.dcols.append(int(col))
                self.fcols.append(int(col))
            elif col and isinstance(col, basestring) and (col.endswith('%') or col.endswith('\x89')):
                col = self.GetInt(col)
                col = float(col) / 100.0 * ((w or contentWidth - self.browser.xmargin * 2) - int(self.browser.attrStack[-1]['border-left-width']) - int(self.browser.attrStack[-1]['border-right-width']))
                self.dcols.append(int(col))
                self.fcols.append(int(col))
            else:
                self.dcols.append(0)
                self.fcols.append(0)

        cells = []
        needMore = []
        rowIdx = 0
        bCollapse = self.browser.attrStack[-1]['border-collapse']
        for rowdata in self.data.attrs.Get('rows', []):
            for celldata in rowdata.cols:
                colIdx = self.GetColIdx(rowIdx)
                while len(self.dcols) < colIdx + int(celldata.colspan or 1):
                    self.dcols.append(0)
                    self.fcols.append(0)

                cell = Cell(parent=self, name='tablecell', align=uiconst.RELATIVE)
                wd = celldata.width
                if wd and isinstance(wd, basestring) and (wd.endswith('%') or wd.endswith('\x89')):
                    wd = self.GetInt(wd)
                    if wd == 100:
                        wd = 0
                    else:
                        wd = float(wd) / 100.0 * contentWidth - self.browser.xmargin * 2
                    celldata.width = int(wd)
                elif wd:
                    celldata.width = self.GetInt(wd)
                else:
                    celldata.width = None
                cell.name = 'tablecell %s-%s' % (rowIdx, colIdx)
                cell.Startup(self)
                cell.charset = getattr(self, 'charset', 'cp1252')
                cell.celldata = celldata
                cell.rowdata = rowdata
                cell.rowspan = int(celldata.rowspan or 1)
                cell.colspan = int(celldata.colspan or 1)
                cell.rowIdx = rowIdx
                cell.colIdx = colIdx
                styles = celldata.styles
                styles['border-left-width'] = styles['border-left-width'] or [self.stack['border-left-width'], 0][colIdx == 0 and bCollapse]
                styles['border-top-width'] = styles['border-top-width'] or [self.stack['border-top-width'], 0][rowIdx == 0 and bCollapse]
                styles['border-right-width'] = styles['border-right-width'] or [self.stack['border-right-width'], 0][bCollapse]
                styles['border-bottom-width'] = styles['border-bottom-width'] or [self.stack['border-bottom-width'], 0][bCollapse]
                cell.celldata.content.insert(0, ('AddStyles', (styles, celldata.css)))
                if not self or self.destroyed:
                    return
                mw, sw = cell.GetMinWidth(singleWordMax)
                mw += self.stack.get('spacing-left', 0) + self.stack.get('spacing-right', 0)
                if not self or getattr(self, 'sr', None) is None:
                    return
                colsdone = 0
                for y in xrange(rowIdx, rowIdx + cell.rowspan):
                    if cell.colspan == 1:
                        self.fcols[colIdx] = int(max(self.fcols[colIdx], sw))
                        self.dcols[colIdx] = int(max(self.dcols[colIdx], mw))
                    for x in xrange(colIdx, colIdx + cell.colspan):
                        self.MarkCellTaken(x, y)

                    colsdone = 1

                cells.append(cell)

            self.drows.append(2)
            rowIdx += 1

        maxTableWidth = int(w or contentWidth - self.browser.xmargin * 2)
        currentWidth = sum(self.dcols)
        toDivide = max(0, maxTableWidth - currentWidth)
        getMore = []
        for cell in cells:
            cell.width = sum(self.dcols[cell.colIdx:cell.colIdx + cell.colspan])
            if cell.totalWidth > cell.width and sum(self.fcols[cell.colIdx:cell.colIdx + cell.colspan]) == 0:
                getMore.append(cell)

        for cell in getMore:
            cols = [ col for col in xrange(cell.colIdx, cell.colIdx + cell.colspan) if self.fcols[col] == 0 ]
            if len(cols) == 0:
                continue
            add = int(min((cell.totalWidth - cell.width) / len(cols), toDivide / len(getMore) / len(cols)))
            for x in cols:
                self.dcols[x] += add

        if w:
            borders = int(self.stack['border-left-width']) + int(self.stack['border-right-width']) + int(self.stack.get('spacing-left', 0)) + int(self.stack.get('spacing-right', 0))
            totalWidth = sum(self.dcols[:]) + borders
            setWidth = int(w)
            if totalWidth:
                setWidth -= borders
                totalWidth -= borders
                oind = sind = 0
                for i in xrange(len(self.dcols)):
                    osave = self.dcols[i]
                    if self.fcols[i] == 0:
                        self.dcols[i] = int((oind + self.dcols[i]) * setWidth / totalWidth - sind)
                    oind += osave
                    sind += self.dcols[i]

        if not self or self.destroyed:
            return
        for cell in cells:
            cell.width = int(sum(self.dcols[cell.colIdx:cell.colIdx + cell.colspan])) - self.stack.get('spacing-left', 0) - self.stack.get('spacing-right', 0)
            mh = cell.GetMinHeight()
            mh += self.stack.get('spacing-top', 0) + self.stack.get('spacing-bottom', 0)
            for i in xrange(cell.rowIdx, cell.rowIdx + cell.rowspan):
                self.drows[i] = max(self.drows[i], mh / cell.rowspan)

        if h:
            borders = int(self.stack['border-top-width']) + int(self.stack['border-bottom-width'])
            totalHeight = sum(self.drows[:]) + borders
            setHeight = int(h)
            if setHeight > totalHeight:
                setHeight -= borders
                totalHeight -= borders
                oind = sind = 0
                for i in xrange(len(self.drows)):
                    osave = self.drows[i]
                    self.drows[i] = (oind + self.drows[i]) * setHeight / totalHeight - sind
                    oind += osave
                    sind += self.drows[i]

        w, h = (0, 0)
        for cell in cells:
            cell.width = sum(self.dcols[cell.colIdx:cell.colIdx + cell.colspan]) - self.stack.get('spacing-left', 0) - self.stack.get('spacing-right', 0)
            cell.height = sum(self.drows[cell.rowIdx:cell.rowIdx + cell.rowspan]) - self.stack.get('spacing-top', 0) - self.stack.get('spacing-bottom', 0)
            cell.left = sum(self.dcols[:cell.colIdx]) + self.stack['border-left-width'] + self.stack.get('spacing-right', 0) + self.stack.get('spacing-left', 0)
            cell.top = sum(self.drows[:cell.rowIdx]) + self.stack['border-top-width'] + self.stack.get('spacing-bottom', 0) + self.stack.get('spacing-top', 0)
            w = max(w, cell.left + cell.width)
            h = max(h, cell.top + cell.height)
            cell.VAlignContent()
            self.AddBackground(cell, cell.celldata.styles)

        if not self or not self.sr:
            return
        self.sr.cells = cells
        self.width = w + self.stack['border-right-width'] + self.stack.get('spacing-right', 0) + self.stack.get('spacing-left', 0)
        self.height = h + self.stack['border-bottom-width'] + self.stack.get('spacing-bottom', 0) + self.stack.get('spacing-top', 0)

    def GetColIdx(self, rowIdx):
        if len(self.taken) <= rowIdx:
            return 0
        row = self.taken[rowIdx]
        if 0 in row:
            return row.index(0)
        return len(row)

    def MarkCellTaken(self, xIdx, yIdx):
        while len(self.taken) < yIdx + 1:
            self.taken.append([])

        row = self.taken[yIdx]
        while len(row) < xIdx + 1:
            row.append(0)

        row[xIdx] = 1

    def GetHeight(self, *args):
        node, width = args
        node.height = self.height
        return node.height


class Cell(parser.ParserBase, uicls.SE_BaseClassCore):
    __guid__ = 'table.Cell'

    def _OnClose(self):
        uicls.SE_BaseClassCore._OnClose(self)
        self.Load = None
        self.celldata = None
        self.sr.lines = None
        self.sr.overlays = None
        self.sr.entries = None

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        parser.ParserBase.Prepare(self)
        self.sr.selfProxy = _weakref.proxy(self)
        self.htmldebug = 0
        self.xmargin = 0
        self.sr.entries = []
        self.sr.overlays = []
        self.sr.overlays_content = uicls.Container(name='overlays', parent=self, padding=(1, 1, 1, 1))
        self.sr.content = uicls.Container(name='content', parent=self)
        self.sr.underlays_content = uicls.Container(name='underlays_content', parent=self, padding=(1, 1, 1, 1))
        self.sr.background = uicls.Container(name='background', parent=self)
        self.sr.backgroundColorContainer = uicls.Container(name='backgroundColorContainer', parent=self)
        browser = uiutil.GetBrowser(self)
        self.sr.browser = browser

    def GetContentWidth(self, *args):
        return self.sr.width or 200

    def Load(self, contentList = [], scrolltotop = 0, scrollTo = 0.0, *args):
        browser = uiutil.GetBrowser(self)
        if browser:
            self.attrStack = browser.attrStack
            self.css = browser.css
            self.LoadFont()
        self.LoadContent(contentList)

    def Startup(self, *args):
        pass

    def GetNodes(self):
        return self.sr.entries

    def LoadContent(self, contentList = [], *args):
        for data in contentList:
            if not data.panel:
                entry = self.AddEntry(data)

        self.sr.overlays_content.left = self.attrStack[-1]['border-left-width']
        self.sr.overlays_content.top = self.attrStack[-1]['border-top-width']
        self.CheckOverlaysAndUnderlays()

    def GetMinWidth(self, singleWordMax):
        s = self.celldata.styles
        sideAddon = s['border-left-width'] + s['border-right-width'] + s['padding-left'] + s['padding-right'] + s['margin-left'] + s['margin-right']
        self.LoadBuffer(self.celldata.content[:], getWidths=1, singleWordMax=singleWordMax)
        if not self or getattr(self, 'sr', None) is None:
            return (0, 0)
        setWidth = int(self.celldata.Get('width', None) or 0)
        minOverlay = 0
        for overlay, attrs, x, y in self.sr.overlays:
            minOverlay = max(minOverlay, x + int(attrs.width) + int((attrs.Get('border', 0) or 0) * 2))

        return (max(self.minWidth + sideAddon + minOverlay, setWidth), setWidth)

    def GetMinHeight(self):
        if not self.celldata or self.destroyed:
            return 0
        h = int(self.celldata.Get('height', None) or self.rowdata.Get('height', None) or 1)
        s = self.celldata.styles
        topAddon = s['border-top-width'] + s['border-bottom-width'] + s['padding-top'] + s['padding-bottom'] + s['margin-top'] + s['margin-bottom']
        self.attrStack.append(s)
        self.LoadBuffer(self.celldata.content[:], setWidth=self.width)
        if self.destroyed:
            return 0
        minOverlay = 0
        for overlay, attrs, x, y in self.sr.overlays:
            minOverlay = max(minOverlay, y + int(attrs.height) + int((attrs.Get('border', 0) or 0) * 2))

        return max(h, self.contentHeight + topAddon, minOverlay)

    def VAlignContent(self):
        if not self or self.destroyed:
            return
        s = self.celldata.styles
        if s['vertical-align'] == html.ALIGNMIDDLE:
            self.sr.content.top = s['padding-top'] + s['margin-top'] - s['border-top-width'] + (self.height - s['padding-top'] - s['margin-top'] - s['padding-bottom'] - s['margin-bottom'] - self.contentHeight) / 2
        elif s['vertical-align'] == html.ALIGNBOTTOM:
            self.sr.content.top = self.height - self.contentHeight - s['border-top-width'] - s['border-bottom-width'] - s['padding-bottom'] - s['margin-bottom']
        elif s['vertical-align'] == html.ALIGNTOP:
            self.sr.content.top = s['padding-top'] + s['margin-top']
        self.sr.content.left = -s['border-left-width']

    def AddEntry(self, entry):
        entry.panel = None
        entry.open = 0
        entry.idx = len(self.sr.entries)
        entry.isSub = 0
        entry.selected = entry.Get('isSelected', 0)
        if entry.Get('PreLoadFunction', None):
            entry.PreLoadFunction(entry)
        self.sr.entries.append(entry)
        self.AddPanel(entry)

    def AddPanel(self, entry):
        w = entry.decoClass(parent=self.sr.content, align=uiconst.TOTOP)
        entry.panel = w
        entry.scroll = self.sr.selfProxy
        if hasattr(w, 'Startup'):
            w.Startup()
        entry.panel.height = entry.Get('maxBaseHeight', 1)
        w.sr.node = entry
        entry.SelectionHandler = None
        w.name = 'cellContent'
        w.Load(entry)
        w.state = uiconst.UI_PICKCHILDREN

    def CheckOverlaysAndUnderlays(self):
        for overlay, attrs, x, y in self.sr.overlays:
            if not overlay.loaded:
                overlay.Load()
            overlay.top = attrs.top
            overlay.left = attrs.left
            self.contentHeight = max(self.contentHeight, overlay.top + overlay.height)

    def GetInt(self, string):
        value = filter(lambda x: x in '0123456789', unicode(string))
        try:
            value = int(value)
        except:
            sys.exc_clear()

        return value


class DivOverlay(Cell):
    __guid__ = 'uicls.SE_div'
    __params__ = []

    def Startup(self, *args):
        attrs = self.data.attrs
        self.name = 'div'
        browser = uiutil.GetBrowser(self)
        contentWidth = browser.GetContentWidth()
        self.width = width = self.GetPercent(attrs.stack['width'] or contentWidth - attrs.stack.get('left', 0), contentWidth - attrs.stack.get('left', 0))
        self.height = attrs.stack['height'] or 32
        self.SetAlign(uiconst.RELATIVE)
        self.AddBackground(self, attrs.stack)
        self.LoadBuffer(self.data.attrs.content, setWidth=self.width)
        self.CheckOverlaysAndUnderlays()
        self.width = attrs.width = width or self.contentWidth
        self.height = attrs.height = attrs.stack.get('height', None) or self.contentHeight
        if attrs.stack['position'] == 'absolute':
            self.left = attrs.left = attrs.stack.get('left', 0)
            self.top = attrs.top = attrs.stack.get('top', 0)
        elif attrs.stack['position'] == 'relative' and attrs.stack['align']:
            if attrs.stack['align'] == 'center':
                aL, aT, aW, aH = self.parent.GetAbsolute()
                self.left = attrs.left = (aW - self.width) / 2
            elif attrs.stack['align'] == 'right':
                aL, aT, aW, aH = self.parent.GetAbsolute()
                self.left = attrs.left = aW - self.width
            else:
                self.left = attrs.left
            self.top = attrs.top
        elif attrs.stack['float'] in ('left', 'right'):
            self.left = attrs.left
            self.top = attrs.top

    def FindCellAbove(self, wnd):
        if wnd is uicore.desktop:
            return None
        if isinstance(wnd, uicls.SE_div):
            return wnd
        return self.FindCellAbove(wnd.parent)

    def Load(self):
        if not self.loaded:
            self.loaded = 1
            Cell.Load(self, contentList=self.sr.lines)
            self.state = uiconst.UI_NORMAL

    def AddBackground(self, where, s):
        contentWidth = uiutil.GetBrowser(self).GetContentWidth()
        for i, side in enumerate(['top',
         'left',
         'right',
         'bottom']):
            align = [uiconst.TOTOP,
             uiconst.TOLEFT,
             uiconst.TORIGHT,
             uiconst.TOBOTTOM][i]
            if s['margin-%s' % side]:
                s['margin-%s' % side] = self.GetPercent(s['margin-%s' % side], contentWidth)
                uicls.Container(name='margin-%s' % side, parent=where, align=align, padding=(0,
                 0,
                 int(s['margin-%s' % side]),
                 int(s['margin-%s' % side])), idx=0)
            if s['border-%s-width' % side]:
                uicls.Line(parent=where, align=align, weight=s['border-%s-width' % side], color=s['border-%s-color' % side])

        if s['background-color']:
            uicls.Fill(parent=where, color=s['background-color'])


class BorderUnderlay(uicls.SE_BaseClassCore):
    __guid__ = 'uicls.SE_border'
    __params__ = []

    def Startup(self, *args):
        self.width = self.data.attrs.width or 1
        self.height = self.data.attrs.height or 1
        self.left = self.data.attrs.left

    def Load(self):
        if not self.loaded:
            i = 0
            for each in ('tb', 'bb', 'lb', 'rb'):
                if self.data.attrs.Get(each + 'style', None) in (None, 1, 2):
                    style = self.data.attrs.Get(each + 'style', 1)
                    color = self.data.attrs.Get(each + 'color', None)
                    weight = self.data.attrs.Get(each + 'width', None)
                    align = [uiconst.TOTOP,
                     uiconst.TOBOTTOM,
                     uiconst.TOLEFT,
                     uiconst.TORIGHT][i]
                    uicls.Line(parent=self, align=align, weight=weight, color=color)
                i += 1

            color = self.data.attrs.Get('bgcolor', None)
            if color:
                uicls.Fill(parent=self, state=uiconst.UI_DISABLED, color=color)
            self.state = uiconst.UI_NORMAL
            self.width = (self.data.attrs.width or 1) + (int(self.data.attrs.border or 0) + 0)
            self.height = (self.data.attrs.height or 1) + (int(self.data.attrs.border or 0) + 0)
            self.loaded = 1


class ImgListentry(uicls.SE_BaseClassCore):
    __guid__ = 'uicls.SE_img'

    def Startup(self, parser, *args):
        attrs = self.data.attrs
        self.width = (attrs.width or 1) + (attrs.leftmargin + attrs.rightmargin + attrs.leftborder + attrs.rightborder)
        self.height = (attrs.height or 1) + (attrs.topmargin + attrs.bottommargin + attrs.topborder + attrs.bottomborder)
        contentWidth = parser.GetContentWidth()
        if attrs.Get('align', None) == 'right':
            self.left = contentWidth - self.width - attrs.left
            self.name = 'rightdude'
        elif attrs.Get('align', None) == 'left':
            self.left = self.data.attrs.left
        self.AddBorders(self, attrs)
        attrs.pictureLeft = attrs.leftmargin + attrs.leftborder
        attrs.pictureTop = attrs.topmargin + attrs.topborder
        self.picloaded = 0
        self.pic = None

    def AddBorders(self, where, attrs):
        for i, side in enumerate(['top',
         'left',
         'right',
         'bottom']):
            align = [uiconst.TOTOP,
             uiconst.TOLEFT,
             uiconst.TORIGHT,
             uiconst.TOBOTTOM][i]
            if attrs.Get('%smargin' % side, 0):
                uicls.Container(name='margin-%s' % side, parent=where, align=align, padding=(0,
                 0,
                 attrs.Get('%smargin-' % side, 0),
                 attrs.Get('%smargin-' % side, 0)), idx=0)
            if attrs.Get('%sborder' % side, 0):
                uicls.Line(parent=where, align=align, weight=attrs.Get('%sborder' % side, 0), color=attrs.Get('%scolor' % side, None))

    def Load(self):
        if not self.loaded:
            self.loaded = 1
            if not self.picloaded:
                self.LoadPicture()
            self.state = uiconst.UI_PICKCHILDREN
            self.SetAlign(uiconst.RELATIVE)

    def GetValue(self):
        return '<img:%s>' % self.data.attrs.src

    def LoadPicture(self):
        if self.pic is None:
            self.pic = uicls.Image(name='img', align=uiconst.RELATIVE)
        self.children.append(self.pic)
        self.pic.Load(self.data.attrs)
        self.pic.attrs.texture = None
        self.picloaded = 1