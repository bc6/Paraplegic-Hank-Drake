import blue
import bluepy
import uthread
import sys
import _weakref
import log
import uiconst
import uiutil
import uicls
import weakref
import stackless
SCROLLMARGIN = 0
MINCOLUMNWIDTH = 24
VERSION = uiconst.SCROLLVERSION
TABMARGIN = 6

class ScrollCore(uicls.Container):
    __guid__ = 'uicls.ScrollCore'
    default_name = 'scroll'
    default_multiSelect = 1
    default_stickToBottom = 0
    default_smartSort = 0
    default_id = None
    default_state = uiconst.UI_NORMAL
    headerFontSize = 10
    scrollEnabled = True
    sortGroups = True

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.sr.maincontainer = uicls.Container(parent=self, name='maincontainer', padding=(1, 1, 1, 1), clipChildren=True)
        self.sr.scrollHeaders = uicls.Container(name='scrollHeaders', parent=self.sr.maincontainer, height=18, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP)
        self.sr.clipper = uicls.Container(name='__clipper', align=uiconst.TOALL, parent=self.sr.maincontainer, clipChildren=True)
        self.sr.clipper._OnSizeChange_NoBlock = self.OnClipperResize
        self.sr.content = uicls.Container(name='__content', align=uiconst.RELATIVE, parent=self.sr.clipper, state=uiconst.UI_NORMAL)
        self.Release()
        self.multiSelect = attributes.get('multiSelect', self.default_multiSelect)
        self.stickToBottom = attributes.get('stickToBottom', self.default_stickToBottom)
        self.smartSort = attributes.get('smartSort', self.default_smartSort)
        self.sr.id = attributes.get('id', self.default_id)
        self.sr.selfProxy = _weakref.proxy(self)
        self.Prepare_()



    def Prepare_(self):
        self.Prepare_ActiveFrame_()
        self.Prepare_Underlay_()
        self.Prepare_ScrollControls_()



    def Prepare_Underlay_(self):
        self.sr.underlay = uicls.Frame(name='__underlay', color=(0.0, 0.0, 0.0, 0.5), frameConst=uiconst.FRAME_FILLED_CORNER0, parent=self)



    def Prepare_ActiveFrame_(self):
        self.sr.activeframe = uicls.Frame(name='__activeframe', color=(1.0, 1.0, 1.0, 0.5), frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER0, parent=self, state=uiconst.UI_HIDDEN)



    def Prepare_ScrollControls_(self):
        self.sr.scrollcontrols = uicls.ScrollControls(name='__scrollcontrols', parent=self.sr.maincontainer, align=uiconst.TORIGHT, width=12, state=uiconst.UI_HIDDEN, idx=0)
        self.sr.scrollcontrols.Startup(self)



    def RemoveActiveFrame(self, *args):
        if uiutil.GetAttrs(self, 'sr', 'activeframe'):
            self.sr.activeframe.color.a = 0.0



    def HideBackground(self, alwaysHidden = 0):
        if uiutil.GetAttrs(self, 'sr', 'underlay'):
            self.sr.underlay.SetAlpha(0.0)
        self.RemoveActiveFrame()
        if alwaysHidden:
            self.SetNoBackgroundFlag(alwaysHidden)


    HideUnderLay = HideBackground

    def SetNoBackgroundFlag(self, hide = 0):
        self.noBackground = hide



    def Release(self):
        self.isTabStop = 1
        self._loading = 0
        self._position = 0
        self._totalHeight = 0
        self._fixedEntryHeight = None
        self._customColumnWidths = None
        self.sr.activeframe = None
        self.sr.scaleLine = None
        self.sr.columnHilite = None
        self.sr.headers = []
        self.sr.widthToHeaders = {}
        self.sr.tabs = []
        self.sr.nodes = []
        self.sr.overlays = []
        self.sr.underlays = []
        self.sr.fixedColumns = {}
        self.rightAlignHeaderLabels = []
        self.stretchLastHeader = False
        self.sr.maxDefaultColumns = {}
        self.sr.minColumnWidth = {}
        self.sr.defaultColumnWidth = {}
        self.sr.notSortableColumns = []
        self.sr.ignoreTabTrimming = 0
        self.showColumnLines = True
        self.sr.id = None
        self.sortBy = None
        self.sr.iconMargin = 0
        self.sr.hint = None
        self.scrollingRange = 0
        self.hiliteSorted = 1
        self.reversedSort = 0
        self.debug = 0
        self.scrolling = 0
        self.scalingcol = 0
        self.refreshingColumns = 0
        self.lastDrawnColumns = None
        self.allowFilterColumns = 0
        self.lastSelected = None
        self.lastHeaders = None
        self.bumpHeaders = 1
        self.slimHeaders = 0
        self.newColumns = 0
        self.trimFast = 0
        self.refs = []
        self.lastCharReceivedAt = 0
        self.currChars = ''
        self.noBackground = 0
        self._ignoreSort = 0



    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                self.parent.parent.sr.node.scroll.ShowNodeIdx(self.parent.parent.sr.node.idx)
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED



    def OnKillFocus(self, *args):
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_HIDDEN



    def DrawHeaders(self, headers, tabs = []):
        self.sr.scrollHeaders.state = uiconst.UI_HIDDEN
        if self.sr.columnHilite:
            self.sr.columnHilite.state = uiconst.UI_HIDDEN
        self.sr.scrollHeaders.Flush()
        for each in self.sr.clipper.children[:]:
            if each.name == '__columnLine':
                each.Close()

        self.lastDrawnColumns = None
        self.sr.widthToHeaders = {}
        if not (headers and tabs and len(headers) == len(tabs)):
            self.sr.headers = []
            self.sr.tabs = []
            return 
        if not self.sr.nodes:
            return 
        self.sr.scrollHeaders.state = uiconst.UI_NORMAL
        uiutil.SetOrder(self.sr.scrollHeaders, 0)
        uicls.Line(parent=self.sr.scrollHeaders, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.25))
        i = 0
        totalWidth = 0
        maxTextHeight = 0
        for header in headers:
            width = self.sr.fixedColumns.get(header, None)
            if width is None:
                if len(headers) == 1:
                    width = 128
                else:
                    width = tabs[i]
                    if i != 0:
                        width = width - tabs[(i - 1)]
            sortdir = self.GetSmartSortDirection(header)
            self.sr.widthToHeaders[header] = totalWidth
            headerparent = uicls.ScrollColumnHeader(parent=self.sr.scrollHeaders, label=header)
            headerparent.SetAlign(uiconst.TOLEFT)
            headerparent.width = width
            headerparent.state = uiconst.UI_NORMAL
            headerparent.sr.column = header
            headerparent.sr.idx = i
            headerparent.sr.sortdir = sortdir
            headerparent.scroll = weakref.ref(self)
            headerparent.sr.header = header
            headerparent.name = header
            headerparent.haveBar = 0
            if headerparent.width < headerparent.sr.label.textwidth:
                headerparent.hint = header
            if self.stretchLastHeader and header == headers[-1]:
                headerparent.SetAlign(uiconst.TOALL)
                headerparent.width = 0
            elif header not in self.sr.fixedColumns and self.sr.id:
                headerparent.width = width
                headerparent.haveBar = 1
                bar = uicls.Container(parent=headerparent, align=uiconst.TORIGHT, pos=(0, 0, 4, 0), state=uiconst.UI_NORMAL, idx=1)
                bar.name = 'scaler'
                bar.sr.column = header
                bar.OnMouseDown = (self.StartScaleCol, bar)
                bar.OnMouseUp = (self.EndScaleCol, bar)
                bar.OnMouseMove = (self.ScalingCol, bar)
                bar.OnDblClick = (self.DblClickCol, bar)
                bar.cursor = 18
                bar.columnWidth = width
                headerparent.bar = bar
                uicls.Line(parent=bar, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.25))
            if header in self.rightAlignHeaderLabels:
                headerparent.sr.label.SetAlign(uiconst.CENTERRIGHT)
            totalWidth += width
            if self.smartSort:
                if sortdir:
                    headerparent.ShowSortDirection(sortdir)
            if not (self.smartSort or self.allowFilterColumns):
                headerparent.GetMenu = None
            maxTextHeight = max(maxTextHeight, headerparent.sr.label.textheight)
            if headerparent.align != uiconst.TOALL and not self.sr.ignoreTabTrimming and self.sr.nodes and self.showColumnLines:
                line = uicls.Line(parent=self.sr.clipper, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.125), name='__columnLine')
                line.width = 1
                line.height = uicore.desktop.height
                line.top = 1
                line.left = totalWidth - 1
            i += 1

        self.sr.scrollHeaders.height = maxTextHeight + 3
        self.lastDrawnColumns = headers



    def ShowHint(self, hint = None):
        if self.sr.hint is None and hint:
            clipperWidth = self.GetContentWidth()
            self.sr.hint = uicls.Label(parent=self.sr.clipper, align=uiconst.TOPLEFT, left=16, top=32, width=clipperWidth - 32, text=hint, fontsize=20, linespace=20, uppercase=True, letterspace=1)
        elif self.sr.hint is not None and hint:
            self.sr.hint.text = hint
            self.sr.hint.state = uiconst.UI_DISABLED
        elif self.sr.hint is not None and not hint:
            self.sr.hint.state = uiconst.UI_HIDDEN



    def StartScaleCol(self, sender, *args):
        if uicore.uilib.rightbtn:
            return 
        self.scalingcol = uicore.uilib.x
        if self.sr.scaleLine is not None:
            self.sr.scaleLine.Close()
        (l, t, w, h,) = self.GetAbsolute()
        self.sr.scaleLine = uicls.Line(parent=self, align=uiconst.TOPLEFT, color=(1.0, 1.0, 1.0, 1.0), width=2, pos=(uicore.uilib.x - l - 1,
         1,
         0,
         h), idx=0)



    def ScalingCol(self, sender, *args):
        (l, t, w, h,) = self.GetAbsolute()
        minColumnWidth = self.sr.minColumnWidth.get(sender.sr.column, MINCOLUMNWIDTH)
        if self.scalingcol and self.sr.scaleLine:
            self.sr.scaleLine.left = max(minColumnWidth, min(w - minColumnWidth, uicore.uilib.x - l - 2))



    def EndScaleCol(self, sender, *args):
        if self.sr.scaleLine is not None:
            if self.sr.id and self.scalingcol != uicore.uilib.x:
                currentSettings = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                currentSettings.setdefault(self.sr.id, {})
                currentWidth = sender.columnWidth
                minColumnWidth = self.sr.minColumnWidth.get(sender.sr.column, MINCOLUMNWIDTH)
                if self.sr.scaleLine:
                    (l, t, w, h,) = self.GetAbsolute()
                    newLeft = self.sr.scaleLine.left + l
                else:
                    newLeft = uicore.uilib.x
                diff = newLeft - self.scalingcol
                newWidth = currentWidth + diff
                currentSettings[self.sr.id][sender.sr.column] = max(minColumnWidth, newWidth)
                settings.user.ui.Set('columnWidths_%s' % VERSION, currentSettings)
                uthread.pool('VirtualScroll::EndScaleCol-->UpdateTabStops', self.UpdateTabStops, 'EndScaleCol')
            scaleLine = self.sr.scaleLine
            self.sr.scaleLine = None
            scaleLine.Close()
        self.scalingcol = 0



    def OnColumnChanged(self, *args):
        pass



    def OnNewHeaders(self, *args):
        pass



    def DblClickCol(self, sender, *args):
        self.ResetColumnWidth(sender.sr.column)



    def ShowNodeIdx(self, idx, toTop = 1):
        if self.scrollingRange:
            node = self.GetNode(idx)
            fromTop = node.scroll_positionFromTop
            if fromTop is None:
                return 
            if self._position > fromTop:
                portion = fromTop / float(self.scrollingRange)
                self.ScrollToProportion(portion)
            (clipperWidth, clipperHeight,) = self.GetContentParentSize()
            nodeHeight = self.GetNodeHeight(node, clipperWidth)
            if self._position + clipperHeight < fromTop + nodeHeight:
                portion = (fromTop - clipperHeight + nodeHeight) / float(self.scrollingRange)
                self.ScrollToProportion(portion)



    def GetNodes(self, allowNone = False):
        ret = []
        for each in self.sr.nodes:
            if each.internalNodes:
                if allowNone:
                    ret += each.internalNodes
                else:
                    for internal in each.internalNodes:
                        if internal:
                            ret.append(internal)

            else:
                ret.append(each)

        return ret



    def SetSelected(self, idx):
        node = self.GetNode(idx)
        if node:
            self.SelectNode(node)
        self.ReportSelectionChange()



    def ActivateIdx(self, idx):
        node = self.GetNode(min(idx, len(self.GetNodes()) - 1))
        if node:
            self.SelectNode(node)
            self.ShowNodeIdx(node.idx)
        else:
            self.ReportSelectionChange()



    def _SelectNode(self, node):
        if getattr(node, 'selectable', 1) == 0:
            return 
        node.selected = 1
        self.UpdateSelection(node)



    def _DeselectNode(self, node):
        node.selected = 0
        self.UpdateSelection(node)



    def SelectNode(self, node, multi = 0, subnode = None, checktoggle = 1):
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        selected = node.get('selected', 0)
        if not self.multiSelect:
            self.DeselectAll(0)
            if control:
                if not selected:
                    self._SelectNode(node)
            else:
                self._SelectNode(node)
        elif not control and not shift:
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and not shift:
            if not selected:
                self._SelectNode(node)
            else:
                self._DeselectNode(node)
        elif not control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                self.DeselectAll(0)
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

                self.ReportSelectionChange()
                return 
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

        else:
            self.DeselectAll(0)
            self._SelectNode(node)
        self.lastSelected = node.idx
        self.ReportSelectionChange()



    def ReportSelectionChange(self):
        self.OnSelectionChange(self.GetSelected())



    def OnSelectionChange(self, *args):
        pass



    def DeselectAll(self, report = 1, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        if report:
            self.ReportSelectionChange()



    def SelectAll(self, *args):
        if not self.multiSelect:
            return 
        for node in self.GetNodes():
            if getattr(node, 'selectable', 1) == 0:
                continue
            node.selected = 1
            self.UpdateSelection(node)

        self.ReportSelectionChange()



    def ToggleSelected(self, *args):
        for node in self.GetNodes():
            node.selected = not node.get('selected', 0)
            self.UpdateSelection(node)

        self.ReportSelectionChange()



    def UpdateSelection(self, node):
        if node.panel:
            if node.panel.sr.selection:
                node.panel.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.selected]
            elif node.selected and hasattr(node.panel, 'Select'):
                node.panel.Select()
            elif not node.selected and hasattr(node.panel, 'Deselect'):
                node.panel.Deselect()



    def ClearSelection(self, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        self.lastSelected = None
        self.ReportSelectionChange()



    def GetSelectedNodes(self, node, toggle = 0):
        if not node.get('selected', 0) or toggle:
            self.SelectNode(node)
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel



    def GetSelected(self):
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel



    def GetSortBy(self):
        if self.smartSort:
            return None
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id][0]
        return self.sortBy



    def GetSortDirection(self):
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id][1]
        return self.reversedSort



    def GetSmartSortDirection(self, column):
        if self.sr.id and self.smartSort:
            if column not in self.sr.notSortableColumns:
                pr = settings.user.ui.Get('smartSortDirection_%s' % VERSION, {})
                if self.sr.id in pr:
                    return pr[self.sr.id].get(column, 1)
            else:
                return None
        return 1



    def ToggleSmartSortDirection(self, column):
        if self.sr.id and self.smartSort:
            current = self.GetSmartSortDirection(column)
            new = [1, -1][(current == 1)]
            pr = settings.user.ui.Get('smartSortDirection_%s' % VERSION, {})
            if self.sr.id not in pr:
                pr[self.sr.id] = {}
            pr[self.sr.id][column] = new
            settings.user.ui.Set('smartSortDirection_%s' % VERSION, pr)



    def GetSortValue(self, by, node, idx = None):
        ret = self._GetSortValue(by, node, idx)
        Deco = node.get('DecoSortValue', lambda x: x)
        return Deco(ret)



    def _GetSortValue(self, by, node, idx):
        val = node.Get('sort_' + by, None)
        if val is None:
            val = node.Get('sort_' + by.replace('<br>', ' '), None)
        if val is not None:
            try:
                val = val.lower()
            except:
                sys.exc_clear()
            return val
        if idx is not None:
            strings = (node.get('label', '') or node.get('text', '')).split('<t>')
            if len(strings) > idx:
                value = strings[idx].lower()
                try:
                    value = uicore.font.DeTag(value)
                    isAU = value.find('au') != -1
                    isKM = value.find('km') != -1
                    value = float(value.replace('m\xb3', '').replace('isk', '').replace('km', '').replace('au', '').replace(',', '').replace(' ', ''))
                    if isAU:
                        value *= const.AU
                    elif isKM:
                        value *= 1000
                    return value
                except:
                    sys.exc_clear()
                    rest = ''.join(strings[(idx + 1):])
                    return value + rest
            return 'aaa'
        val = node.Get(by, '-')
        try:
            val = val.lower()
        except:
            sys.exc_clear()
        return val



    def GetColumns(self):
        if self.sr.id and (self.smartSort or self.allowFilterColumns):
            if not self.sr.headers:
                return []
            orderedColumns = settings.user.ui.Get('columnOrder_%s' % VERSION, {}).get(self.sr.id, self.sr.headers)
            notInOrdered = [ header for header in self.sr.headers if header not in orderedColumns ]
            headers = [ header for header in orderedColumns + notInOrdered if header in self.sr.headers ]
            hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % VERSION, {}).get(self.sr.id, [])
            allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {}).get(self.sr.id, [])
            filterColumns = filter(lambda x: x not in allHiddenColumns, headers)
            return filterColumns
        else:
            return self.sr.headers



    def GetHeaderMenu(self, label):
        m = []
        if self.smartSort:
            m += [(mls.UI_CMD_MAKEPRIMARY, self.MakePrimary, (label,))]
        if self.smartSort or self.allowFilterColumns:
            if len(self.GetColumns()) > 1:
                m += [('%s %s' % (mls.UI_GENERIC_HIDE, label), self.HideColumn, (label,))]
            m += self.GetShowColumnMenu()
        return m



    def GetShowColumnMenu(self):
        m = []
        for label in self.sr.headers:
            if label not in self.GetColumns():
                m.append(('%s %s' % (mls.UI_GENERIC_SHOW, label), self.ShowColumn, (label,)))

        if m:
            m.insert(0, None)
        return m



    def MakePrimary(self, label, update = 1):
        all = settings.user.ui.Get('primaryColumn_%s' % VERSION, {})
        all[self.sr.id] = label
        settings.user.ui.Set('primaryColumn_%s' % VERSION, all)
        if update:
            self.ChangeColumnOrder(label, 0)



    def GetPrimaryColumn(self):
        return settings.user.ui.Get('primaryColumn_%s' % VERSION, {}).get(self.sr.id, None)



    def SetColumnsHiddenByDefault(self, columns, *args):
        if self.sr.id:
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            if self.sr.id not in filteredByDefault:
                filteredByDefault[self.sr.id] = columns
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)



    def HideColumn(self, label):
        if self.sr.id:
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            if self.sr.id not in filtered:
                filtered[self.sr.id] = []
            if label not in filtered[self.sr.id]:
                filtered[self.sr.id].append(label)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()



    def ShowColumn(self, label):
        if self.sr.id:
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            if self.sr.id in filtered and label in filtered[self.sr.id]:
                filtered[self.sr.id].remove(label)
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            if self.sr.id in filteredByDefault and label in filteredByDefault[self.sr.id]:
                filteredByDefault[self.sr.id].remove(label)
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()



    def HideTriangle(self, column):
        for each in self.sr.scrollHeaders.children:
            if not isinstance(each, uicls.ScrollColumnHeaderCore):
                continue
            if each.name == column and each.sr.triangle:
                each.sr.triangle.state = uiconst.UI_HIDDEN
                if each.sr.label.align == uiconst.CENTERRIGHT:
                    each.sr.label.left = 0




    def Sort(self, by = None, reversesort = 0, forceHilite = 0):
        if self.debug:
            log.LogInfo('vscroll', 'Sort' + strx(by) + ', ' + strx(reversesort))
        if self.smartSort:
            columns = self.GetColumns()
            primary = self.GetPrimaryColumn()
            sortcolumns = columns[:]
            if primary in columns:
                idx = columns.index(primary)
                sortcolumns = columns[idx:]
            if columns:
                sortData = []
                rm = []
                for node in self.sr.nodes:
                    nodeData = []
                    idx = 0
                    for header in columns:
                        if header not in sortcolumns:
                            self.HideTriangle(header)
                            continue
                        if idx in rm:
                            value = 0
                        else:
                            value = node.Get('sort_%s' % header, None)
                            if value is None:
                                log.LogWarn('Cannot find sortvalue for column ', header, ' in scroll ', self.sr.id)
                                rm.append(idx)
                                self.HideTriangle(header)
                                value = 0
                            else:
                                try:
                                    value = value.lower()
                                except:
                                    sys.exc_clear()
                        idx += 1
                        nodeData.append(value)

                    sortData.append([nodeData, node])

                sortOrder = [ (idx, self.GetSmartSortDirection(header)) for (idx, header,) in enumerate(sortcolumns) if idx not in rm ]
                sortData.sort(lambda x, y, sortOrder = sortOrder: uiutil.SmartCompare(x, y, sortOrder))
                self.SetNodes([ each[1] for each in sortData ])
                self.UpdatePositionThreaded(fromWhere='Sort(Smart)')
        else:
            idx = None
            headers = self.GetColumns()
            if by in headers:
                idx = headers.index(by)
            endOrder = []
            self.SortAsRoot(self.sr.nodes, endOrder, by, idx, reversesort)
            self.SetNodes(endOrder)
            self.UpdatePosition(fromWhere='Sort')
            if self.sortBy != by or forceHilite:
                self.HiliteSorted(by, reversesort)
                self.sortBy = by



    def SortAsRoot(self, nodes, endOrder, columnName, columnIndex, reversedSorting = 0, groupIndex = None):
        groups = []
        rootSortList_Groups = []
        rootSortList_NotGroups = []
        for node in nodes:
            if groupIndex is None and node.isSub:
                continue
            val = self.GetSortValue(columnName, node, columnIndex)
            val = (val, node.get('label', '').lower() or node.get('text', '').lower())
            if issubclass(node.decoClass, uicls.SE_ListGroupCore):
                rootSortList_Groups.append((val, node))
            else:
                rootSortList_NotGroups.append((val, node))

        if self.sortGroups:
            rootSortList_Groups = uiutil.SortListOfTuples(rootSortList_Groups)
        else:
            rootSortList_Groups = [ node for (val, node,) in rootSortList_Groups ]
        rootSortList_NotGroups = uiutil.SortListOfTuples(rootSortList_NotGroups)
        if reversedSorting:
            rootSortList_NotGroups.reverse()
        combinedGroupsAndOthers = rootSortList_Groups + rootSortList_NotGroups
        if groupIndex is not None:
            for (subIndex, subNode,) in enumerate(combinedGroupsAndOthers):
                endOrder.insert(groupIndex + subIndex + 1, subNode)

        else:
            endOrder.extend(combinedGroupsAndOthers)
        if rootSortList_Groups:
            for groupNode in rootSortList_Groups:
                groupIdx = endOrder.index(groupNode)
                subNodes = groupNode.get('subNodes', [])
                self.SortAsRoot(subNodes, endOrder, columnName, columnIndex, reversedSorting, groupIndex=groupIdx)

        return nodes



    def RefreshSort(self, forceHilite = 0):
        if self.debug:
            log.LogInfo('vscroll', 'RefreshSort')
        if self.smartSort:
            self.Sort()
        else:
            sortby = self.GetSortBy()
            if sortby:
                self.Sort(sortby, self.GetSortDirection(), forceHilite=forceHilite)



    def ChangeSortBy(self, by, *args):
        if self.debug:
            log.LogInfo('vscroll', 'ChangeSortBy')
        if self.smartSort:
            self.MakePrimary(by, 0)
            self.ToggleSmartSortDirection(by)
            for header in self.sr.scrollHeaders.children:
                if not isinstance(header, uicls.ScrollColumnHeaderCore):
                    continue
                sortdir = self.GetSmartSortDirection(header.sr.column)
                header.sr.sortdir = sortdir
                header.ShowSortDirection(sortdir)

            self.Sort()
        elif self.sortBy == by:
            self.reversedSort = not self.reversedSort
        else:
            self.reversedSort = 0
        self.sortBy = by
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            pr[self.sr.id] = (self.sortBy, self.reversedSort)
            settings.user.ui.Set('scrollsortby_%s' % VERSION, pr)
        self.RefreshSort(1)



    def ChangeColumnOrder(self, column, toIdx):
        if self.debug:
            log.LogInfo('vscroll', 'ChangeColumnOrder')
        if self.sr.id and self.smartSort:
            all = settings.user.ui.Get('columnOrder_%s' % VERSION, {})
            currentOrder = all.get(self.sr.id, self.sr.headers)[:]
            if column in currentOrder:
                currentOrder.remove(column)
            currentOrder.insert(toIdx, column)
            all[self.sr.id] = currentOrder
            settings.user.ui.Set('columnOrder_%s' % VERSION, all)
            self.OnColumnChanged(None)
            self.OnNewHeaders()



    def HiliteSorted(self, by, rev, *args):
        if self.debug:
            log.LogInfo('vscroll', 'HiliteSorted')
        totalWidth = 0
        for header in self.sr.scrollHeaders.children:
            if not isinstance(header, uicls.ScrollColumnHeaderCore):
                continue
            header.Deselect()
            if self.hiliteSorted and header.sr.column == by:
                header.Select(rev)
                if not self.sr.ignoreTabTrimming:
                    if not self.sr.columnHilite:
                        self.sr.columnHilite = uicls.Fill(parent=self.sr.maincontainer, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.0625), pos=(header.left - 4,
                         0,
                         header.width,
                         1200), name='columnHilite')
                    self.sr.columnHilite.width = header.width + 1
                    self.sr.columnHilite.left = totalWidth - 1
                    self.sr.columnHilite.state = uiconst.UI_DISABLED
            totalWidth += header.width




    def Clear(self):
        if self.debug:
            log.LogInfo('vscroll', 'Clear')
        self.LoadContent()



    def ReloadNodes(self):
        for node in self.GetNodes():
            self.PrepareSubContent(node, threadedUpdate=False)
            if node.panel:
                node.panel.Load(node)




    def LoadContent(self, fixedEntryHeight = None, contentList = [], sortby = None, reversesort = 0, headers = [], scrollTo = None, customColumnWidths = False, showScrollTop = False, noContentHint = '', ignoreSort = False, scrolltotop = False, keepPosition = False):
        if self.destroyed:
            return 
        if scrolltotop:
            scrollTo = 0.0
        elif scrollTo is None or keepPosition:
            scrollTo = self.GetScrollProportion()
        self._loading = 1
        self._fixedEntryHeight = fixedEntryHeight
        self._customColumnWidths = customColumnWidths
        self._ignoreSort = ignoreSort
        wnd = uiutil.GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        if self.debug:
            log.LogInfo('vscroll', 'Load %s %s %s %s' % (len(contentList),
             sortby,
             reversesort,
             headers))
        self.sr.nodes = self.sr.entries = []
        self.sr.content.Flush()
        self._position = self.sr.content.top = 0
        if showScrollTop:
            self.sr.scrollcontrols.state = uiconst.UI_NORMAL
        self.sortBy = sortby
        self.reversedSort = reversesort
        self.AddNodes(0, contentList, initing=True)
        if sortby and not ignoreSort:
            self.Sort(sortby, reversesort)
        if self.destroyed:
            return 
        if noContentHint and not contentList:
            self.ShowHint(noContentHint)
            self._ScrollCore__LoadHeaders([])
        else:
            self.ShowHint()
            self._ScrollCore__LoadHeaders(headers)
        if self.destroyed:
            return 
        self.RefreshNodes(fromWhere='LoadContent')
        self.ScrollToProportion(scrollTo, threaded=False)
        self.UpdateTabStops('LoadContent')
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        self._loading = 0


    Load = LoadContent

    def LoadHeaders(self, headers):
        wnd = uiutil.GetWindowAbove(self)
        try:
            if self._ScrollCore__LoadHeaders(headers):
                self.OnColumnChanged(self.sr.tabs)

        finally:
            if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
                wnd.HideLoad()




    def __LoadHeaders(self, headers):
        self.sr.headers = headers
        self.UpdateTabStops('__LoadHeaders')
        if self.destroyed:
            return 
        if headers:
            if not self.smartSort:
                sortby = self.GetSortBy()
                reversesort = self.GetSortDirection()
                if not sortby or sortby not in headers:
                    sortby = headers[0]
                if not self._ignoreSort:
                    self.Sort(sortby, reversesort)
                else:
                    self.UpdatePositionThreaded(fromWhere='__LoadHeaders')
            else:
                self.Sort()
        if len(self.sr.nodes) or not headers:
            self.lastHeaders = headers
        return 1



    def ResetColumnWidths(self):
        for header in self.GetColumns():
            self.ResetColumnWidth(header)




    def ResetColumnWidth(self, header, onlyReset = 0):
        if self.debug:
            log.LogInfo('vscroll', 'ResetColumnWidth')
        if self.sr.id is None or self.refreshingColumns:
            return 
        if not onlyReset:
            wnd = uiutil.GetWindowAbove(self)
            if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
                wnd.ShowLoad()
        self.refreshingColumns = 1
        if header not in self.sr.fixedColumns and self.sr.id:
            headertab = [(header,
              self.headerFontSize,
              2,
              TABMARGIN + 8 + 20,
              1)]
        else:
            headertab = [(header,
              self.headerFontSize,
              2,
              0,
              1)]
        if header in self.GetColumns():
            idx = self.GetColumns().index(header)
            width = None
            if self._customColumnWidths:
                headerWidth = uicore.font.GetTextWidth(header, fontsize=self.headerFontSize, letterspace=0, uppercase=True)
                headerWidth += TABMARGIN + 8 + 20
                normHeader = header.replace('<br>', ' ')
                width = max([headerWidth] + [ node.GetColumnWidthFunction(None, node, normHeader) for node in self.sr.nodes if node.get('GetColumnWidthFunction', None) is not None ])
            else:
                fontsize = 12
                letterspace = 0
                shift = 0
                strengir = []
                for node in self.sr.nodes:
                    tabs = (node.get('label', '') or node.get('text', '')).split('<t>')
                    if len(tabs) <= idx:
                        continue
                    if node.panel and node.panel.sr.label:
                        label = node.panel.sr.label
                        fontsize = label.fontsize
                        letterspace = label.letterspace
                        if idx == 0:
                            shift = label.left
                    strengir.append((tabs[idx],
                     fontsize,
                     letterspace,
                     shift,
                     0))

                tabstops = uicore.font.MeasureTabstops(headertab + strengir)
                if len(tabstops):
                    width = max(MINCOLUMNWIDTH, tabstops[0])
            if width is not None:
                current = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                current.setdefault(self.sr.id, {})[header] = width
                settings.user.ui.Set('columnWidths_%s' % VERSION, current)
                self.UpdateTabStops('ResetColumnWidth')
        if not onlyReset and wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        self.refreshingColumns = 0



    def ApplyTabstopsToNode(self, node, fromWhere = ''):
        if self.sr.ignoreTabTrimming or not self.GetColumns():
            return 
        tabStops = self.sr.tabs
        node.tabs = tabStops
        if tabStops and uiutil.GetAttrs(node, 'panel', 'OnColumnResize'):
            cols = []
            last = 0
            for tab in tabStops:
                cols.append(tab - last)
                last = tab

            cols[0] -= self.sr.maincontainer.left
            node.panel.OnColumnResize(cols)
        elif tabStops and node.panel and node.panel.sr.label:
            label = node.panel.sr.label
            subTract = label.left
            if isinstance(label, uicls.LabelCore):
                newtext = node.label or node.text
                if getattr(label, 'tabs', None) != tabStops or label.xShift != -subTract:
                    label.xShift = -subTract
                    label.tabs = tabStops
                    label.text = newtext



    def UpdateTabStops(self, fromWhere = None, updatePosition = True):
        headers = self.GetColumns()
        if self.debug:
            log.LogInfo('vscroll', 'UpdateTabStops %s %s' % (headers, fromWhere))
        headertabs = []
        if headers is not None and len(headers):
            headertabs = [('<t>'.join(headers),
              self.headerFontSize,
              2,
              TABMARGIN + 2,
              1)]
        strengir = []
        fontsize = 12
        letterspace = 0
        shift = 0
        for node in self.sr.nodes:
            t = node.get('label', '') or node.get('text', '')
            if not t:
                continue
            if node.panel and node.panel.sr.label:
                label = node.panel.sr.label
                fontsize = label.fontsize
                letterspace = label.letterspace
                shift = label.left
            strengir.append((t,
             fontsize,
             letterspace,
             shift,
             0))

        tabstops = uicore.font.MeasureTabstops(strengir + headertabs)
        if self.sr.id and headers:
            userDefined = settings.user.ui.Get('columnWidths_%s' % VERSION, {}).get(self.sr.id, {})
            i = 0
            total = 0
            former = 0
            for header in headers:
                if header in self.sr.fixedColumns:
                    stopSize = self.sr.fixedColumns[header]
                else:
                    userSetWidth = userDefined.get(header, None) or self.sr.defaultColumnWidth.get(header, None)
                    minColumnWidth = self.sr.minColumnWidth.get(header, MINCOLUMNWIDTH)
                    if userSetWidth is not None:
                        stopSize = max(userSetWidth, minColumnWidth)
                    else:
                        stopSize = tabstops[i] - former
                        if header in self.sr.maxDefaultColumns:
                            stopSize = min(self.sr.maxDefaultColumns.get(header, minColumnWidth), stopSize)
                total += stopSize
                former = tabstops[i]
                tabstops[i] = total
                i += 1

        didChange = tabstops != self.sr.tabs
        self.sr.tabs = tabstops
        if headers != self.lastDrawnColumns or didChange:
            self.DrawHeaders(headers, tabstops)
            if didChange:
                if not self.smartSort:
                    self.HiliteSorted(self.GetSortBy(), self.GetSortDirection(), 'UpdateTabStops')
                if not self._loading:
                    self.OnColumnChanged(tabstops)
        if updatePosition:
            self.UpdatePositionThreaded('UpdateTabStops')
        return tabstops



    def AddNode(self, idx, node, isSub = 0, initing = False):
        if self.debug:
            log.LogInfo('vscroll', 'AddNode', idx)
        if idx == -1:
            idx = len(self.sr.nodes)
        node.panel = None
        node.open = 0
        node.idx = idx
        node.isSub = isSub
        node.scroll = self.sr.selfProxy
        node.selected = node.get('isSelected', 0)
        if node.get('PreLoadFunction', None):
            node.PreLoadFunction(node)
            if self.destroyed:
                return 
        self.sr.nodes.insert(idx, node)
        self.PrepareSubContent(node, initing=initing)
        return node



    def PrepareSubContent(self, node, initing = False, threadedUpdate = True):
        if node.id:
            if node.get('subNodes', []):
                rm = node.subNodes
                node.subNodes = []
                node.open = 0
                self.RemoveNodes(rm)
            if node.Get('GetSubContent', None) is not None and uicore.registry.GetListGroupOpenState(node.id, default=node.get('openByDefault', False)):
                subcontent = node.GetSubContent(node)
                if not node.Get('hideNoItem', False) and not len(subcontent):
                    noItemText = node.get('noItemText', mls.UI_GENERIC_NOITEM)
                    subcontent.append(self.GetNoItemNode(text=noItemText, sublevel=node.get('sublevel', 0) + 1))
                if not self.destroyed:
                    self.AddNodes(node.idx + 1, subcontent, node, initing=initing, threadedUpdate=threadedUpdate)
                    node.subNodes = subcontent
                    node.open = 1
                    return subcontent



    def RemoveNodesRaw(self, nodes):
        wnd = uiutil.GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        for node in nodes:
            if node.panel:
                node.panel.Close()
            if node in self.sr.nodes:
                self.sr.nodes.remove(node)

        self.RefreshNodes()
        self.UpdatePositionThreaded('RemoveNodesRaw')
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()



    def InsertNodesRaw(self, fromIdx, nodesData):
        wnd = uiutil.GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        addedNodes = []
        idx = fromIdx
        for data in nodesData:
            newnode = self.AddNode(idx, data)
            addedNodes.append(newnode)
            idx += 1

        self.RefreshNodes()
        self.UpdatePositionThreaded('InsertNodesRaw')
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        return addedNodes



    def SetNodes(self, nodes):
        self.sr.nodes = nodes
        self.RefreshNodes()



    @bluepy.CCP_STATS_ZONE_METHOD
    def RefreshNodes(self, fromWhere = None):
        if self.destroyed:
            return 
        (clipperWidth, clipperHeight,) = (self.sr.clipper.displayWidth, self.sr.clipper.displayHeight)
        if not clipperWidth or not clipperHeight:
            (clipperWidth, clipperHeight,) = self.sr.clipper.GetAbsoluteSize()
        fromTop = 0
        for (nodeidx, node,) in enumerate(self.sr.nodes):
            node.idx = nodeidx
            nodeheight = self.GetNodeHeight(node, clipperWidth)
            node.scroll_positionFromTop = fromTop
            if node.panel:
                node.panel.align = uiconst.TOPLEFT
                node.panel.left = 0
                node.panel.top = fromTop
                node.panel.width = clipperWidth
                node.panel.height = nodeheight
                node.panel.name = node.name or 'entry_%s' % node.idx
            fromTop += nodeheight

        for (overlay, attrs, x, y,) in self.sr.overlays + self.sr.underlays:
            fromTop = max(fromTop, attrs.top + attrs.height)

        atBottom = self._position and self._position == self.scrollingRange
        self._totalHeight = fromTop
        self.scrollingRange = max(0, self._totalHeight - clipperHeight)
        if self.scrollingRange and self.scrollEnabled:
            self.sr.scrollcontrols.state = uiconst.UI_NORMAL
        else:
            self.sr.scrollcontrols.state = uiconst.UI_HIDDEN
        if not self.scrollingRange or atBottom or self.stickToBottom:
            self._position = self.scrollingRange
        self._position = min(self._position, self.scrollingRange)
        self.sr.content.height = max(clipperHeight, self._totalHeight)
        self.sr.content.width = clipperWidth
        if self.sr.overlays_content:
            self.sr.overlays_content.height = self.sr.content.height
            self.sr.overlays_content.width = clipperWidth
        if self.sr.underlays_content:
            self.sr.underlays_content.height = self.sr.content.height
            self.sr.underlays_content.width = clipperWidth



    def AddNodes(self, fromIdx, nodesData, parentNode = None, ignoreSort = 0, initing = False, threadedUpdate = True):
        if self.debug:
            log.LogInfo('vscroll', 'AddNodes start')
        wnd = uiutil.GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        isSub = 0
        if parentNode:
            isSub = parentNode.get('sublevel', 0) + 1
        nodes = []
        idx = fromIdx
        for data in nodesData:
            newnode = self.AddNode(idx, data, isSub=isSub, initing=initing)
            if newnode is None:
                continue
            subs = self.CollectSubNodes(newnode, clear=0)
            idx = newnode.idx + 1 + len(subs)
            nodes.append(newnode)

        if parentNode:
            parentNode.subNodes = nodes
        self.UpdateTabStops('AddNodes', updatePosition=False)
        if not initing:
            if self.GetSortBy() and not (self._ignoreSort or ignoreSort):
                self.RefreshSort()
            elif threadedUpdate:
                self.RefreshNodes()
                self.UpdatePositionThreaded(fromWhere='AddNodes')
            else:
                self.RefreshNodes()
                self.UpdatePosition(fromWhere='AddNodes')
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        if self.debug:
            log.LogInfo('vscroll', 'AddNodes done')
        return nodes


    AddEntries = AddNodes

    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveNodes(self, nodes):
        if self.debug:
            log.LogInfo('vscroll', 'RemoveNodes start')
        wnd = uiutil.GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        subs = []
        for node in nodes:
            subs.extend(self.CollectSubNodes(node))

        for nodeList in (nodes, subs):
            for node in nodeList:
                if node.panel:
                    node.panel.Close()
                if node in self.sr.nodes:
                    self.sr.nodes.remove(node)


        self.RefreshNodes()
        self.UpdatePosition()
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        if self.debug:
            log.LogInfo('vscroll', 'RemoveNodes done')


    RemoveEntries = RemoveNodes

    def CollectSubNodes(self, node, nodes = None, clear = 1):
        if nodes is None:
            nodes = []
        inNodes = [ id(each) for each in nodes ]
        for subnode in node.get('subNodes', []):
            if subnode is None:
                continue
            self.CollectSubNodes(subnode, nodes, clear)
            if id(subnode) not in inNodes:
                nodes.append(subnode)

        if clear:
            node.subNodes = []
        return nodes



    def GetNodeHeight(self, node, clipperWidth):
        func = node.GetHeightFunction
        newStyle = getattr(node.decoClass, 'GetDynamicHeight', None)
        allowDynamicResize = node.get('allowDynamicResize', True)
        if func:
            if not node.height or allowDynamicResize and node._lastClipperWidth != clipperWidth:
                node.height = apply(func, (None, node, clipperWidth))
                node._lastClipperWidth = clipperWidth
        elif newStyle:
            if not node.height or allowDynamicResize and node._lastClipperWidth != clipperWidth:
                node.height = newStyle(node, clipperWidth)
                node._lastClipperWidth = clipperWidth
        elif self._fixedEntryHeight:
            node.height = self._fixedEntryHeight
        else:
            node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        if not node.height:
            if func:
                apply(func, (None, node, clipperWidth))
            else:
                node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        return node.height



    def GetContentWidth(self):
        (w, h,) = self.GetContentParentSize()
        return w



    def GetContentHeight(self):
        return self._totalHeight


    GetTotalHeight = GetContentHeight

    def GetContentParentSize(self):
        (w, h,) = self.sr.clipper.GetAbsoluteSize()
        return (w, h)



    def UpdatePositionThreaded(self, fromWhere = None):
        loopThread = getattr(self, 'loopThread', None)
        if loopThread is None:
            self.loopThread = uthread.new(self.UpdatePositionLoop)



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdatePositionLoop(self, fromWhere = None):
        if self.destroyed:
            return 
        while True:
            nodeCreatedOrRefreshed = self.UpdatePosition(fromWhere='UpdatePositionLoop', doYield=True)
            blue.pyos.BeNice()
            if self.destroyed:
                return 
            if not nodeCreatedOrRefreshed:
                break

        self.loopThread = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdatePosition(self, fromWhere = None, doYield = False):
        if self.destroyed:
            return 
        (clipperWidth, clipperHeight,) = self.sr.clipper.GetAbsoluteSize()
        self.sr.content.top = int(-self._position)
        if self.sr.overlays_content:
            self.sr.overlays_content.top = self.sr.content.top
        if self.sr.underlays_content:
            self.sr.underlays_content.top = self.sr.content.top
        self.UpdateScrollHandle(clipperHeight, fromWhere='UpdatePosition')
        tabStops = self.sr.tabs
        scrollPosition = self._position
        ignoreTabstops = self.sr.ignoreTabTrimming
        nodeLoaded = False
        for (nodeCount, node,) in enumerate(self.sr.nodes):
            if nodeCount != node.idx or node.scroll_positionFromTop is None or node.height is None:
                self.RefreshNodes(fromWhere='UpdatePosition')
            nodeheight = node.height
            posFromTop = node.scroll_positionFromTop
            displayScrollEntry = node.panel
            if scrollPosition > posFromTop + nodeheight or scrollPosition + clipperHeight < posFromTop:
                if displayScrollEntry:
                    displayScrollEntry.state = uiconst.UI_HIDDEN
                if doYield:
                    blue.pyos.BeNice()
                continue
            forceTabstops = False
            if not displayScrollEntry:
                decoClass = node.decoClass
                displayScrollEntry = decoClass(parent=self.sr.content, align=uiconst.TOPLEFT, pos=(0,
                 posFromTop,
                 clipperWidth,
                 nodeheight), state=uiconst.UI_NORMAL, name=node.name or 'entry_%s' % node.idx)
                displayScrollEntry.sr.node = node
                node.panel = displayScrollEntry
                node.scroll = self.sr.selfProxy
                if hasattr(displayScrollEntry, 'Startup'):
                    displayScrollEntry.Startup(self.sr.selfProxy)
                displayScrollEntry.Load(node)
                forceTabstops = True
                nodeLoaded = True
            elif not displayScrollEntry.display:
                displayScrollEntry.state = uiconst.UI_NORMAL
                if not node.isStatic:
                    displayScrollEntry.Load(node)
                forceTabstops = True
                nodeLoaded = True
            if not ignoreTabstops:
                updateTabs = node.tabs != tabStops
                if forceTabstops or updateTabs:
                    self.ApplyTabstopsToNode(node, 'UpdatePosition')

        self.OnUpdatePosition(self)
        return nodeLoaded



    def UpdateScrollHandle(self, clipperHeight, fromWhere = ''):
        if self.destroyed or not self.sr.scrollcontrols:
            return 
        self.sr.scrollcontrols.SetScrollHandleSize(clipperHeight, self._totalHeight)
        if self._position and self.scrollingRange:
            self.sr.scrollcontrols.SetScrollHandlePos(self._position / float(self.scrollingRange))
        else:
            self.sr.scrollcontrols.SetScrollHandlePos(0.0)



    def OnChar(self, enteredChar, *args):
        if enteredChar < 32:
            return False
        if not self.sr.nodes:
            return True
        if blue.os.TimeAsDouble() - self.lastCharReceivedAt < 1.0 and self.currChars is not None:
            self.currChars += unichr(enteredChar).lower()
        else:
            self.currChars = unichr(enteredChar).lower()
        if enteredChar == uiconst.VK_SPACE:
            selected = self.GetSelected()
            if len(selected) == 1 and self.currChars == ' ' and uiutil.GetAttrs(selected[0], 'panel', 'OnCharSpace') is not None:
                selected[0].panel.OnCharSpace(enteredChar)
                return True
        uthread.new(self._OnCharThread, enteredChar)
        self.lastCharReceivedAt = blue.os.TimeAsDouble()
        return True



    def _OnCharThread(self, enteredChar):
        if self.destroyed:
            return 
        charsBefore = self.currChars
        blue.pyos.synchro.Sleep(100)
        if self.destroyed:
            return 
        if self.currChars != charsBefore:
            return 
        selected = self.GetSelected()
        if not selected:
            selected = self.sr.nodes
        selected = selected[0]
        numEntries = len(self.sr.nodes)
        if selected not in self.sr.nodes:
            return 
        startIndex = self.sr.nodes.index(selected)
        if len(self.currChars) == 1:
            startIndex += 1
        entryRange = range(numEntries)[startIndex:] + range(numEntries)[:startIndex]
        for i in entryRange:
            entry = self.sr.nodes[i]
            if entry.charIndex and entry.charIndex.startswith(self.currChars):
                self.SelectNode(entry)
                entryPos = self.sr.nodes.index(entry)
                self.ScrollToProportion(float(entryPos) / numEntries)
                break




    def OnDelete(self):
        pass



    def OnUpdatePosition(self, *args):
        pass



    def CheckOverlaysAndUnderlays(self):
        for (overlay, attrs, x, y,) in self.sr.overlays + self.sr.underlays:
            if overlay is None or overlay.destroyed:
                continue
            if attrs.Get('align', None) == 'right':
                overlay.left = self.GetContentWidth() - overlay.width - attrs.left
            if not overlay.loaded:
                overlay.top = attrs.top
                overlay.SetAlign(uiconst.RELATIVE)
                overlay.state = uiconst.UI_NORMAL
                overlay.Load()




    def GetNode(self, idx, checkInternalNodes = False):
        if checkInternalNodes:
            allNodes = self.GetNodes(allowNone=True)
        else:
            allNodes = self.sr.nodes
        if idx == -1:
            if allNodes:
                return allNodes[-1]
            else:
                return None
        if len(allNodes) > idx:
            return allNodes[idx]



    def OnKeyDown(self, key, flag):
        if uiconst.VK_DELETE == key:
            self.OnDelete()



    def Resizing(self):
        pass



    def OnClipperResize(self, clipperWidth, clipperHeight, *args, **kw):
        self.OnContentResize(clipperWidth, clipperHeight, *args, **kw)



    def OnContentResize(self, clipperWidth, clipperHeight, *args, **kw):
        if self.sr.hint:
            (w, h,) = (clipperWidth, clipperHeight)
            newWidth = w - self.sr.hint.left * 2
            if abs(newWidth - self.sr.hint.width) > 12:
                self.sr.hint.width = newWidth
        if self.sr.content:
            self.RefreshNodes(fromWhere='OnContentResize')
            self.UpdatePositionThreaded(fromWhere='OnContentResize')
        if not self.destroyed:
            self.Resizing()



    def BrowseNodes(self, up):
        sel = self.GetSelected()
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if sel:
            shiftIdx = None
            if not control and shift:
                r = [ node.idx for node in sel ]
                if up:
                    if r[0] < self.lastSelected:
                        shiftIdx = r[0] - 1
                    else:
                        shiftIdx = r[-1] - 1
                elif r[0] < self.lastSelected:
                    shiftIdx = r[0] + 1
                shiftIdx = r[-1] + 1
            if shiftIdx is None:
                if len(sel) > 1:
                    idx = sel[[-1, 0][up]].idx
                else:
                    idx = sel[-1].idx
                idx += [1, -1][up]
            else:
                idx = shiftIdx
            total = len(self.GetNodes())
            if 0 <= idx < total:
                self.ActivateIdx(idx)
                return 1
        return 0


    BrowseEntries = BrowseNodes

    def OnUp(self):
        if not self.GetSelected():
            self.ActivateIdx(len(self.sr.entries) - 1)
            return 
        if not self.BrowseNodes(1):
            self.Scroll(1 + 10 * uicore.uilib.Key(uiconst.VK_SHIFT))



    def OnDown(self):
        if not self.GetSelected():
            self.ActivateIdx(0)
            return 
        if not self.BrowseNodes(0):
            self.Scroll(-1 - 10 * uicore.uilib.Key(uiconst.VK_SHIFT))



    def OnHome(self):
        self.ScrollToProportion(0.0)



    def OnEnd(self):
        self.ScrollToProportion(1.0)



    def OnMouseWheel(self, *etc):
        if getattr(self, 'wheeling', 0):
            return 1
        self.wheeling = 1
        self.Scroll(uicore.uilib.dz / 240.0)
        self.wheeling = 0
        return 1



    def Scroll(self, dz):
        if self.debug:
            log.LogInfo('vscroll', 'Scroll %s' % (dz,))
        step = 37
        pos = max(0, min(self.scrollingRange, self._position - step * dz))
        if pos != self._position:
            self._position = int(pos)
            self.stickToBottom = False
            self.UpdatePositionThreaded(fromWhere='Scroll')



    def GetScrollProportion(self):
        if self.scrollingRange:
            return self._position / float(self.scrollingRange)
        return 0.0



    @bluepy.CCP_STATS_ZONE_METHOD
    def ScrollToProportion(self, proportion, threaded = True):
        proportion = min(1.0, max(0.0, proportion))
        pos = int(max(0, self.scrollingRange * proportion))
        self._position = int(pos)
        if threaded:
            self.UpdatePositionThreaded(fromWhere='ScrollToPorportion')
        else:
            self.UpdatePosition(fromWhere='ScrollToPorportion')



    def GetMinSize(self):
        return (64, 64)



    def GetNoItemNode(self, text, sublevel = 0, *args):
        return uicls.ScrollEntryNode(label=text, sublevel=sublevel)




class ScrollControlsCore(uicls.Container):
    __guid__ = 'uicls.ScrollControlsCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.Prepare_()



    def Prepare_(self):
        uicls.Line(parent=self, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.underlay = uicls.Frame(name='__underlay', color=(0.0, 0.0, 0.0, 0.5), frameConst=uiconst.FRAME_FILLED_CORNER0, parent=self)
        self.Prepare_ScrollHandle_()



    def Prepare_ScrollHandle_(self):
        subparent = uicls.Container(name='subparent', parent=self, align=uiconst.TOALL, padding=(-1, 0, 0, 0))
        self.sr.scrollhandle = uicls.ScrollHandle(name='__scrollhandle', parent=subparent, align=uiconst.TOPLEFT, pos=(0, 0, 2, 2), state=uiconst.UI_NORMAL, idx=0)



    def Startup(self, dad):
        self.dad = weakref.ref(dad)
        self.sr.scrollhandle.Startup(dad)



    def AccessScroll(self):
        if self.dad:
            return self.dad()



    def OnMouseDown(self, *args):
        scrollTop = self.sr.scrollhandle
        (l, t, w, h,) = self.GetAbsolute()
        absTop = t + scrollTop.width + scrollTop.height / 2
        absBottom = t + h - scrollTop.width - scrollTop.height / 2
        proportion = (uicore.uilib.y - absTop) / float(absBottom - absTop)
        proportion = min(1.0, max(0.0, proportion))
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.stickToBottom = 0
            scrollControl.ScrollToProportion(proportion, threaded=False)



    def SetScrollHandleSize(self, displayHeight, contentHeight):
        if self.sr.scrollhandle:
            self.sr.scrollhandle.UpdateSize(displayHeight, contentHeight)



    def SetScrollHandlePos(self, posFraction):
        if self.sr.scrollhandle:
            self.sr.scrollhandle.ScrollToProportion(posFraction)




class ScrollHandleCore(uicls.Container):
    __guid__ = 'uicls.ScrollHandleCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.sr.hilite = None
        self._dragging = False
        self.Prepare_()



    def Prepare_(self):
        uicls.Fill(name='__activeframe', color=(1.0, 1.0, 1.0, 0.25), parent=self, padding=(2, 1, 1, 1))
        self.Prepare_Hilite_()



    def Prepare_Hilite_(self):
        self.sr.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.5), padding=(2, 1, 1, 1), state=uiconst.UI_HIDDEN)



    def Startup(self, dad):
        self.dad = weakref.ref(dad)



    def AccessScroll(self):
        if self.dad:
            return self.dad()



    def UpdateSize(self, displayHeight, contentHeight):
        if displayHeight and contentHeight:
            sizePortion = max(0.0, min(1.0, float(displayHeight) / contentHeight))
        else:
            sizePortion = 0.0
        scrollAreaHeight = displayHeight - self.parent.padTop - self.parent.padBottom
        self.height = max(16, int(scrollAreaHeight * sizePortion))
        self.width = self.parent.parent.width - self.left * 2



    def ScrollToProportion(self, proportion):
        proportion = min(1.0, max(0.0, proportion))
        self.top = int((self.parent.displayHeight - self.height) * proportion)



    def OnMouseDown(self, btn, *args):
        if btn != uiconst.MOUSELEFT:
            return 
        self.startdragdata = (uicore.uilib.y, self.top)
        self._dragging = 1
        self.top = self.top + 1
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.sr.content.state = uiconst.UI_DISABLED
            scrollControl.stickToBottom = 0



    def OnMouseMove(self, *etc):
        self.MouseMove()



    def MouseMove(self, *args):
        if not self._dragging:
            return 
        if not uicore.uilib.leftbtn:
            self._dragging = 0
            return 
        (y0, top0,) = self.startdragdata
        range_ = self.parent.displayHeight - self.height
        self.top = max(0, min(range_, top0 - y0 + uicore.uilib.y))
        scrollTo = 0.0
        if range_ and self.top:
            scrollTo = self.top / float(range_)
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.ScrollToProportion(scrollTo)



    def OnMouseUp(self, btn, *args):
        if btn == uiconst.MOUSELEFT:
            self._dragging = 0
        self.top = self.top - 1
        uicore.uilib.RecalcWindows()
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.sr.content.state = uiconst.UI_NORMAL
            scrollControl.UpdatePositionThreaded(fromWhere='OnMouseUp')



    def OnMouseEnter(self, *args):
        if self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.hilite:
            self.sr.hilite.state = uiconst.UI_HIDDEN




class ScrollBtnCore(uicls.Container):
    __guid__ = 'uicls.ScrollBtnCore'

    def Startup(self, dad, direction):
        self.wannascroll = 0
        self.dad = weakref.ref(dad)
        self.sr.direction = direction



    def AccessScroll(self):
        if self.dad:
            return self.dad()



    def OnMouseEnter(self, *args):
        if self.sr.hilite:
            self.sr.hilite.state = uiutil.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.hilite:
            self.sr.hilite.state = uiutil.UI_HIDDEN



    def OnMouseDown(self, *args):
        self.wannascroll = 1
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.stickToBottom = 0
        uthread.pool('ScrollBtn::OnMouseDown-->Scroll', self.Scroll)



    def OnMouseUp(self, *args):
        self.wannascroll = 0
        self.children[0].top = [1, -1][(self.sr.direction < 0)]



    def Scroll(self):
        while self.wannascroll:
            scrollControl = self.AccessScroll()
            if scrollControl:
                scrollControl.Scroll(self.sr.direction)
                self.children[0].top = [2, 0][(self.sr.direction < 0)]
            else:
                break
            blue.pyos.synchro.Sleep(100)





class ColumnHeaderCore(uicls.Container):
    __guid__ = 'uicls.ScrollColumnHeaderCore'
    headerFontSize = 10
    letterspace = 1

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.Prepare_Divider_()
        self.Prepare_Label_()
        self.sr.label.text = attributes.label
        self.draggingAllowed = 0
        self.sr.triangle = None
        self.sr.selection = None



    def Prepare_Divider_(self):
        uicls.Line(parent=self, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.25))



    def Prepare_Label_(self):
        textclipper = uicls.Container(name='textclipper', parent=self, align=uiconst.TOALL, padding=(6, 2, 6, 0), state=uiconst.UI_PICKCHILDREN, clipChildren=1)
        self.sr.label = uicls.Label(text='', parent=textclipper, letterspace=self.letterspace, fontsize=self.headerFontSize, hilightable=1, state=uiconst.UI_DISABLED, uppercase=1, autowidth=1, autoheight=1)



    def _OnClose(self):
        if self.sr.selection:
            s = self.sr.selection
            self.sr.selection = None
            s.Close()
        uicls.Container._OnClose(self)



    def _OnEndDrag(self, *args):
        if self.sr.frame:
            f = self.sr.frame
            self.sr.frame = None
            f.Close()
        for each in self.children:
            if each.name == 'scaler':
                each.state = uiconst.UI_NORMAL

        if hasattr(uicore.uilib.mouseOver, 'OnDropColumn'):
            uicore.uilib.mouseOver.OnDropColumn(self)



    def _OnStartDrag(self, *args):
        for each in self.children:
            if each.name == 'scaler':
                each.state = uiconst.UI_HIDDEN

        self.sr.frame = uicls.Frame(parent=self, idx=0)



    def OnDropColumn(self, droppings):
        if droppings == self:
            return 
        (l, t, w, h,) = self.GetAbsolute()
        if uicore.uilib.x < l + w / 2:
            newIdx = self.sr.idx
        else:
            newIdx = self.sr.idx + 1
        if self.scroll and self.scroll():
            self.scroll().ChangeColumnOrder(droppings.sr.column, newIdx)



    def OnDblClick(self, *args):
        if self.scroll and self.scroll():
            self.scroll().ResetColumnWidth(self.sr.column)



    def OnClick(self, *args):
        if self.sr.sortdir is not None:
            if self.scroll and self.scroll():
                self.scroll().ChangeSortBy(self.sr.header)



    def GetMenu(self, *args):
        if self.scroll and self.scroll():
            return self.scroll().GetHeaderMenu(self.sr.column)



    def Deselect(self):
        if self.sr.triangle:
            self.sr.triangle.state = uiconst.UI_HIDDEN
            if self.sr.label.align == uiconst.CENTERRIGHT:
                self.sr.label.left = 0
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def Select(self, rev, *args):
        self.ShowSortDirection([1, -1][rev])



    def ShowSortDirection(self, direction):
        if direction is None:
            return 
        if not self.sr.triangle:
            self.sr.triangle = uicls.Icon(align=uiconst.CENTERRIGHT, pos=(3, 0, 16, 16), parent=self, idx=0, name='directionIcon', icon='ui_1_16_16')
        self.sr.triangle.state = uiconst.UI_DISABLED
        if self.sr.label.align == uiconst.CENTERRIGHT:
            self.sr.label.left = 8
        if direction == 1:
            uiutil.MapIcon(self.sr.triangle, 'ui_1_16_16')
        else:
            uiutil.MapIcon(self.sr.triangle, 'ui_1_16_15')




