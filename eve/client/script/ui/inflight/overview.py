import base
import blue
import const
import foo
import form
import listentry
import state
import uix
import uthread
import util
import xtriui
import uiutil
import uiconst
import uicls

class OverView(form.ActionPanel):
    __guid__ = 'form.OverView'
    __notifyevents__ = ['OnDestinationSet',
     'OnOverviewTabChanged',
     'OnEwarStart',
     'OnEwarEnd',
     'OnStateSetupChance',
     'OnSessionChanged']
    default_pinned = True
    default_top = 108
    default_height = 300

    def ApplyAttributes(self, attributes):
        form.ActionPanel.ApplyAttributes(self, attributes)
        self.cursor = uiconst.UICURSOR_HASMENU



    def default_left(self):
        dw = uicore.desktop.width
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return dw - 256 - 16 - rightpush



    def FlushEwarStates(self):
        self.jammers = {}



    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return 
        if not jammingType:
            return 
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        jammingID = sm.StartService('state').GetEwarGraphicID(jammingType)
        if not self.jammers.has_key(sourceBallID):
            self.jammers[sourceBallID] = {}
        if not self.jammers[sourceBallID].has_key(jammingID):
            self.jammers[sourceBallID][jammingID] = {}
            self.jammers[sourceBallID]['needReload'] = True
        self.jammers[sourceBallID][jammingID][moduleID] = True



    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return 
        if not jammingType:
            return 
        if not hasattr(self, 'jammers'):
            return 
        jammingID = sm.StartService('state').GetEwarGraphicID(jammingType)
        if not self.jammers.has_key(sourceBallID) or not self.jammers[sourceBallID].has_key(jammingID) or not self.jammers[sourceBallID][jammingID].has_key(moduleID):
            return 
        del self.jammers[sourceBallID][jammingID][moduleID]
        if self.jammers[sourceBallID][jammingID] == {}:
            self.jammers[sourceBallID]['needReload'] = True
            del self.jammers[sourceBallID][jammingID]



    def OnDestinationSet(self, *etc):
        if self and not self.destroyed:
            path = sm.GetService('starmap').GetDestinationPath()
            for entry in self.sr.scroll.GetNodes():
                if entry.panel is None or entry.slimItem is None or entry.slimItem() is None or entry.slimItem().groupID != const.groupStargate:
                    continue
                if entry.slimItem().jumps[0].locationID in path:
                    color = (1.0, 1.0, 0.0)
                else:
                    color = (1.0, 1.0, 1.0)
                entry.panel.sr.icon.color.SetRGB(*color)




    def OnOverviewTabChanged(self, tabsettings, oldtabsettings):
        if tabsettings == None:
            tabsettings = settings.user.overview.Get('tabsettings', {})
        newtabsettings = {}
        for (key, setting,) in tabsettings.iteritems():
            newtabsettings[key] = setting

        settings.user.overview.Set('tabsettings', newtabsettings)
        if hasattr(self, 'maintabs'):
            self.maintabs.Close()
        presets = settings.user.overview.Get('overviewPresets', {})
        tabs = []
        if len(tabsettings.keys()) == 0:
            overviewPreset = settings.user.overview.Get('activeOverviewPreset', None)
            if not overviewPreset:
                overviewPreset = 'default'
            tabs.append([mls.UI_GENERIC_DEFAULT,
             self.sr.scroll,
             self,
             (overviewPreset,
              None,
              mls.UI_GENERIC_DEFAULT,
              0),
             self.sr.scroll])
            if not tabsettings:
                settings.user.overview.Set('tabsettings', {0: {'overview': overviewPreset,
                     'bracket': None,
                     'name': mls.UI_GENERIC_DEFAULT}})
        else:
            for key in tabsettings.keys():
                bracketSettings = tabsettings[key].get('bracket', None)
                overviewSettings = tabsettings[key].get('overview', None)
                tabName = tabsettings[key].get('name', None)
                tabs.append([tabsettings[key]['name'],
                 self.sr.scroll,
                 self,
                 (overviewSettings,
                  bracketSettings,
                  tabName,
                  key),
                 self.sr.scroll])

        if hasattr(self, 'maintabs'):
            self.maintabs.Close()
        self.maintabs = uicls.TabGroup(name='tabparent', align=uiconst.TOTOP, parent=self.sr.topParent, idx=0, tabs=tabs, groupID='overviewTabs')



    def OnStateSetupChance(self, reason = None):
        for entry in self.sr.scroll.GetNodes():
            if entry.panel:
                uix.TakeTime('tactical::UpdateOverview --> UpdateIcon', entry.panel.UpdateIcon)




    def GetTabMenu(self, tab, *args):
        presets = settings.user.overview.Get('overviewPresets', {}).keys()
        overviewm = []
        bracketm = []
        ret = []
        isSelected = tab.IsSelected()
        tabName = tab.sr.args[2]
        tabKey = tab.sr.args[3]
        bracketm.append(('', (mls.UI_CMD_SHOWALLBRACKETS, self.ChangeBracketInTab, (None, isSelected, tabKey))))
        for key in presets:
            label = key
            if key == 'ccp_notsaved':
                overviewm.append(('', (mls.UI_GENERIC_NOTSAVED, self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                bracketm.append((' ', (mls.UI_GENERIC_NOTSAVED, self.ChangeBracketInTab, (key, isSelected, tabKey))))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewm.append((lowerLabel, (overviewName, self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                    bracketm.append((lowerLabel, (overviewName, self.ChangeBracketInTab, (key, isSelected, tabKey))))
                else:
                    overviewm.append((lowerLabel, (label, self.ChangeOverviewInTab, (key, isSelected, tabKey))))
                    bracketm.append((lowerLabel, (label, self.ChangeBracketInTab, (key, isSelected, tabKey))))

        overviewm = uiutil.SortListOfTuples(overviewm)
        bracketm = uiutil.SortListOfTuples(bracketm)
        ret = []
        ret.append((mls.UI_CMD_CHANGELABEL, self.ChangeTabName, (tabName, tabKey)))
        ret.append((mls.UI_CMD_LOAD_OVERVIEW_PROFILE, overviewm))
        ret.append((mls.UI_CMD_LOAD_BRACKET_PROFILE, bracketm))
        ret.append((mls.UI_CMD_DELETE_TAB, self.DeleteTab, (tabKey, isSelected)))
        ret.append((mls.UI_CMD_ADD_TAB, self.AddTab))
        return ret



    def ChangeTabName(self, tabName, tabKey):
        ret = uix.NamePopup(mls.UI_CMD_CHANGELABEL, mls.UI_INFLIGHT_TYPELABEL, tabName, maxLength=30)
        if not ret:
            return 
        tabsettings = settings.user.overview.Get('tabsettings', {})
        newTabName = ret['name']
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['name'] = newTabName
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)



    def ChangeOverviewInTab(self, overviewLabel, isSelected, tabKey):
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['overview'] = overviewLabel
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)
            if isSelected:
                sm.GetService('tactical').LoadPreset(overviewLabel, False)



    def ChangeBracketInTab(self, bracketLabel, isSelected, tabKey):
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if tabsettings.has_key(tabKey):
            oldtabsettings = tabsettings
            tabsettings[tabKey]['bracket'] = bracketLabel
            self.OnOverviewTabChanged(tabsettings, oldtabsettings)
            if isSelected:
                sm.GetService('tactical').LoadBracketPreset(bracketLabel)



    def DeleteTab(self, tabKey, isSelected):
        oldtabsettings = settings.user.overview.Get('tabsettings', {})
        if not oldtabsettings.has_key(tabKey):
            return 
        newtabsettings = {}
        i = 0
        for (key, dictItem,) in oldtabsettings.iteritems():
            if key == tabKey:
                continue
            newtabsettings[i] = dictItem
            i += 1

        self.OnOverviewTabChanged(newtabsettings, oldtabsettings)



    def AddTab(self):
        ret = uix.NamePopup(mls.UI_CMD_ADD_TAB, mls.UI_INFLIGHT_TYPELABEL, maxLength=15)
        if not ret:
            return 
        numTabs = 5
        tabsettings = settings.user.overview.Get('tabsettings', {})
        if len(tabsettings) >= numTabs:
            eve.Message('TooManyTabs', {'numTabs': numTabs})
            return 
        if len(tabsettings) == 0:
            newKey = 0
        else:
            newKey = max(tabsettings.keys()) + 1
        oldtabsettings = tabsettings
        tabsettings[newKey] = {'name': ret['name'],
         'overview': None,
         'bracket': None}
        if self.destroyed:
            return 
        self.OnOverviewTabChanged(tabsettings, oldtabsettings)



    def PostStartup(self):
        self.solarsystemHasChanged = True
        self.Cleanup()
        self.SetTopparentHeight(18)
        self.SetHeaderIcon()
        hicon = self.sr.headerIcon
        hicon.GetMenu = self.GetPresetsMenu
        hicon.expandOnLeft = 1
        hicon.hint = mls.UI_INFLIGHT_OVERVIEWTYPEPRESETS
        hicon.name = 'overviewHeaderIcon'
        self.sr.presetMenu = hicon
        scroll = uicls.Scroll(name='overviewscroll2', align=uiconst.TOALL, parent=self.sr.main, subSortBy=mls.UI_GENERIC_DISTANCE)
        scroll.bumpHeaders = 0
        scroll.slimHeaders = 1
        scroll.ignoreHeaderWidths = 1
        scroll.sr.id = 'overviewscroll2'
        scroll.multiSelect = 0
        scroll.sr.fixedColumns = {mls.UI_GENERIC_ICON: 24}
        scroll.OnColumnChanged = self.OnColumnChanged
        scroll.OnSelectionChange = self.OnScrollSelectionChange
        scroll.debug = 0
        scroll.OnChar = self.OnChar
        scroll.GetCombatCommandItemID = self.GetCombatCommandItemID
        (columns, displayColumns,) = sm.GetService('tactical').GetColumns()
        self.sr.scroll = scroll
        self.OnOverviewTabChanged(None, {})
        self.sr.scroll.Load(contentList=[], headers=displayColumns)
        uthread.new(self.UpdateAll)



    def OnSetActive_(self, *args):
        selected = self.sr.scroll.GetSelected()
        if selected is None:
            self.sr.scroll.SetSelected(0)



    def GetCombatCommandItemID(self, *args):
        selected = self.sr.scroll.GetSelected()
        if not selected:
            return 
        return selected[0].itemID



    def OnChar(self, *args):
        return False



    def LoadTabPanel(self, args, panel, tabgroup):
        tactical = sm.GetService('tactical')
        if len(args) > 2:
            tactical.LoadPreset(args[0], False)
            tactical.LoadBracketPreset(args[1])
        if len(args) >= 4:
            showSpecials = settings.user.overview.Get('tabsettings', {}).get(args[3], {}).get('showSpecials', False)
            showAll = settings.user.overview.Get('tabsettings', {}).get(args[3], {}).get('showAll', False)
            showNone = settings.user.overview.Get('tabsettings', {}).get(args[3], {}).get('showNone', False)
            bracketMgr = sm.GetService('bracket')
            bracketMgr.DoToggleShowSpecials(showSpecials)
            if showAll:
                bracketMgr.ShowAll()
            elif showNone:
                bracketMgr.ShowNone()
            else:
                bracketMgr.StopShowingAll()



    def OnColumnChanged(self, what, *args):
        if what is None:
            self.UpdateAll()
        else:
            self.OnStateSetupChance()



    def OnScrollSelectionChange(self, nodes, *args):
        if not nodes:
            return 
        node = nodes[0]
        if node and getattr(node, 'itemID', None):
            sm.GetService('state').SetState(node.itemID, state.selected, 1)
            if sm.GetService('target').IsTarget(node.itemID):
                sm.GetService('state').SetState(node.itemID, state.activeTarget, 1)



    def GetPresetsMenu(self):
        return sm.GetService('tactical').GetPresetsMenu()



    def Cleanup(self):
        self.updateoverview = None



    def Hidden(self):
        self.sr.scroll.Load(contentList=[])



    def UpdateAll(self, flush = 0, sleep = 1):
        if not self or self.destroyed:
            return 
        sm.GetService('tactical').LogInfo('Overview - starting update all')
        self.solarsystemHasChanged = False
        self.updateoverview = 0
        ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
        if ballpark is None:
            return 
        scrolllist = []
        (columns, displayColumns,) = sm.GetService('tactical').GetColumns()
        filtered = sm.GetService('tactical').GetFilteredStatesFunctionNames()
        count = 1
        sm.GetService('tactical').LogInfo('Overview - starting loop')
        for itemID in ballpark.balls.keys():
            if ballpark is None:
                break
            if itemID == eve.session.shipid:
                continue
            slimItem = ballpark.GetInvItem(itemID)
            if not sm.GetService('tactical').WantIt(slimItem, filtered):
                continue
            ball = ballpark.GetBall(itemID)
            if not (ball and slimItem):
                continue
            blue.pyos.BeNice(100)
            data = sm.GetService('tactical').GetEntryData(slimItem, ball)
            if slimItem.groupID == const.groupStation:
                data.name = 'overviewStation%s' % count
                count += 1
            if not self or self.destroyed:
                return 
            self.UpdateSortData(data, columns)
            scrolllist.append(listentry.Get('TacticalItem', data=data))

        ignoreSort = sm.StartService('ui').GetOverviewFreezeMode()
        sm.GetService('tactical').LogInfo('Overview - about to load scroll, num entries:', len(scrolllist))
        self.sr.scroll.Load(contentList=scrolllist, headers=displayColumns, scrollTo=getattr(self, 'cachedScrollPos', 0.0), ignoreSort=ignoreSort, noContentHint=mls.UI_GENERIC_NOTHINGFOUND)
        self.OnStateSetupChance()
        uthread.new(self.UpdateOverview)



    def UpdateForOneCharacter(self, charID, *args):
        ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
        if ballpark is None:
            return 
        ballID = None
        ballSlimItem = None
        for (itemID, slimItem,) in ballpark.slimItems.iteritems():
            if charID == getattr(slimItem, 'charID', None):
                ballID = itemID
                ballSlimItem = slimItem
                break

        if ballID is None:
            return 
        tacticalSvc = sm.GetService('tactical')
        entry = tacticalSvc.GetOverviewEntry(ballID)
        filtered = tacticalSvc.GetFilteredStatesFunctionNames()
        wantIt = tacticalSvc.WantIt(ballSlimItem, filtered)
        if entry is None:
            if wantIt:
                self.updateoverview = 0
                ball = ballpark.GetBall(ballID)
                data = tacticalSvc.GetEntryData(slimItem, ball)
                if not self or self.destroyed:
                    return 
                (columns, displayColumns,) = tacticalSvc.GetColumns()
                self.UpdateSortData(data, columns)
                entry = listentry.Get('TacticalItem', data=data)
                self.sr.scroll.AddEntries(-1, [entry])
                uthread.new(self.UpdateOverview)
            else:
                return 
        elif wantIt:
            if entry.updateItem:
                slimItem = entry.slimItem()
                if slimItem and entry.panel:
                    xtriui.UpdateEntry.Load_update(entry.panel, slimItem)
            return 
        self.updateoverview = 0
        self.sr.scroll.RemoveEntries([entry])
        uthread.new(self.UpdateOverview)



    def OnExpanded(self, *args):
        self.UpdateAll()



    def OnCollapsed(self, *args):
        self.updateoverview = 0
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        self.sr.scroll.Load(contentList=[])



    def OnEndMaximize_(self, *args):
        self.UpdateAll()



    def OnEndMinimize_(self, *args):
        self.updateoverview = 0
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        self.sr.scroll.Load(contentList=[])



    def UpdateOverview(self, *args):
        self.updateoverview = 1
        if getattr(self, 'updatingOverview', 0):
            return 
        escapedSortUpdate = 0
        self.updatingOverview = 1
        while not self.destroyed and self.updateoverview:
            if not eve.session.solarsystemid:
                self.updatingOverview = 0
                self.updateoverview = 0
                return 
            insider = uiutil.IsUnder(uicore.uilib.mouseOver, self)
            if self.destroyed:
                return 
            s = blue.os.GetTime(1)
            if self.sr and uiutil.IsVisible(self.sr.main) and not self.IsCollapsed() and not self.IsMinimized():
                tactical = sm.GetService('tactical')
                rm = []
                refreshSort = 0
                (columns, displayColumns,) = tactical.GetColumns()
                updateEntries = filter(None, [ self.UpdateSortData(entry, columns) for entry in self.sr.scroll.GetNodes() if entry.slimItem() ])
                if self.destroyed:
                    return 
                freezeOverview = sm.StartService('ui').GetOverviewFreezeMode()
                if updateEntries:
                    if insider or freezeOverview:
                        escapedSortUpdate = True
                    else:
                        uix.TakeTime('tactical::UpdateOverview --> RefreshSort', self.sr.scroll.RefreshSort)
                        escapedSortUpdate = False
                    updateEntries = [ each for each in updateEntries if getattr(each, 'needReload', 0) if each.panel if each.panel.display ]
                    idx = 0
                    step = 5
                    counter = 0
                    for entry in updateEntries:
                        if entry.needReload and entry.panel:
                            entry.panel.Load(entry)
                            counter += 1
                        if self.destroyed:
                            self.updatingOverview = 0
                            self.updateoverview = 0
                            return 
                        if counter >= step:
                            counter = 0
                            blue.pyos.synchro.Yield()

                    if not self.sr.scroll.GetNodes():
                        uix.TakeTime('tactical::UpdateOverview --> ShowHint 1', self.sr.scroll.ShowHint, mls.UI_GENERIC_NOTHINGFOUND)
                    else:
                        uix.TakeTime('tactical::UpdateOverview --> ShowHint 2', self.sr.scroll.ShowHint)
                elif escapedSortUpdate:
                    if not freezeOverview:
                        uix.TakeTime('tactical::UpdateOverview --> RefreshSort', self.sr.scroll.RefreshSort)
                        escapedSortUpdate = False
            diff = blue.os.TimeDiffInMs(s, blue.os.GetTime(1))
            sleep = max(500, 2500 - diff)
            blue.pyos.synchro.Sleep(sleep)
            if self.destroyed:
                return 

        self.updatingOverview = 0



    def UpdateSortData(self, data, columns):
        refreshSort = 0
        ball = data.ball()
        if not ball:
            return 
        else:
            data.columns = columns
            ball.GetVectorAt(blue.os.GetTime())
            surfaceDist = ball.surfaceDist
            if 'DISTANCE' in columns:
                mlsDist = mls.UI_GENERIC_DISTANCE
                currentDist = data.Get('sort_' + mlsDist)
                currentFmtDist = data.Get('fmt_' + mlsDist, None)
                if currentFmtDist:
                    newFmtDist = util.FmtDist(surfaceDist, maxdemicals=1)
                    if currentFmtDist != newFmtDist:
                        data.Set('sort_' + mlsDist, surfaceDist)
                        data.Set('fmt_' + mlsDist, newFmtDist)
                        refreshSort = 1
                elif surfaceDist != data.Get('sort_' + mlsDist):
                    data.Set('sort_' + mlsDist, surfaceDist)
                    data.Set('fmt_' + mlsDist, None)
                    refreshSort = 1
            if data.updateItem and ball.isFree:
                Memo = util.Memoized

                def _Me():
                    bp = sm.GetService('michelle').GetBallpark()
                    return bp and bp.GetBall(eve.session.shipid)


                Me = Memo(_Me)

                def IfMe(f):

                    def deco():
                        if Me():
                            return f()
                        else:
                            return 0


                    return deco



                def _Vel():
                    return ball.GetVectorDotAt(blue.os.GetTime()).Length()


                Vel = Memo(_Vel)

                def _CombVel():
                    return foo.Vector3(ball.vx - Me().vx, ball.vy - Me().vy, ball.vz - Me().vz)


                CombVel = Memo(_CombVel)

                def _RadNorm():
                    ret = foo.Vector3(ball.x - Me().x, ball.y - Me().y, ball.z - Me().z)
                    if (ret.x, ret.y, ret.z) != (0.0, 0.0, 0.0):
                        ret = ret.Normalize()
                    return ret


                RadNorm = Memo(_RadNorm)
                RadVel = Memo(IfMe(lambda : CombVel() * RadNorm()))
                TransVel = Memo(IfMe(lambda : (CombVel() - RadVel() * RadNorm()).Length()))
                AngVel = Memo(IfMe(lambda : TransVel() / max(1.0, surfaceDist)))
                for (name, func,) in [('VELOCITY', Vel),
                 ('RADIALVELOCITY', RadVel),
                 ('ANGULARVELOCITY', AngVel),
                 ('TRANSVERSALVELOCITY', TransVel)]:
                    if name not in columns:
                        continue
                    mlsStr = getattr(mls, 'UI_GENERIC_' + name)
                    if func() != data.Get('sort_' + mlsStr):
                        data.Set('sort_' + mlsStr, func())
                        data.Set('fmt_' + mlsStr, None)
                        refreshSort = 1

            if hasattr(self, 'jammers') and self.jammers.has_key(data.itemID):
                if self.jammers[data.itemID]['needReload']:
                    refreshSort = 1
                data.Set('ewar', self.jammers[data.itemID])
                self.jammers[data.itemID]['needReload'] = False
            data.needReload = data.Get('needReload', 0) or refreshSort
            if data.needReload:
                return data
            return 



    def GetSelectedTabArgs(self):
        if hasattr(self, 'maintabs'):
            return self.maintabs.GetSelectedArgs()



    def GetSelectedTabKey(self):
        if hasattr(self, 'maintabs'):
            selectedArgs = self.maintabs.GetSelectedArgs()
            if selectedArgs is None:
                return 
            else:
                return selectedArgs[3]



    def IncrementEntriesAdded(self, entries):
        entriesAdded = getattr(self, 'entriesAdded', 0)
        entriesToRemove = sm.StartService('tactical').GetOverviewEntriesToRemove()
        toAdd = []
        for entry in entries:
            if entry.itemID in entriesToRemove:
                oldEntry = entriesToRemove.pop(entry.itemID, None)
                if util.GetAttrs(oldEntry, 'panel', 'Load'):
                    oldEntry.panel.Load(oldEntry.panel.sr.node)
                continue
            toAdd.append(entry)

        if toAdd:
            entriesAdded += 1
            self.entriesAdded = entriesAdded
            self.sr.scroll.AddEntries(-1, toAdd, ignoreSort=1)



    def AddEntryToRemoveLater(self, entry):
        entries = sm.StartService('tactical').GetOverviewEntriesToRemove()
        entries[entry.itemID] = entry



    def RemoveDelayedEntries(self):
        entriesToRemove = sm.StartService('tactical').GetOverviewEntriesToRemove()
        if getattr(self, 'entriesAdded', 0) > 0:
            self.DoDelayedSort()
        if not entriesToRemove:
            return 
        values = entriesToRemove.values()
        self.sr.scroll.RemoveEntries(values)
        sm.StartService('tactical').ClearOverviewEntriesToRemove()



    def DoDelayedSort(self):
        self.sr.scroll.RefreshSort()
        self.entriesAdded = 0



    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change and self and not self.dead:
            self.solarsystemHasChanged = True




class TacticalItem(xtriui.UpdateEntry, listentry.Generic):
    __guid__ = 'listentry.TacticalItem'

    def Startup(self, *args):
        self.sr.label = uicls.Label(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, color=None, singleline=1, align=uiconst.CENTERLEFT)
        self.sr.label.cached = 1
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Icon(parent=self, idx=0, name='typeicon', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, top=1)
        events = ('OnClick', 'OnMouseDown', 'OnMouseUp', 'OnDblClick', 'OnMouseHover')
        for eventName in events:
            setattr(self.sr, eventName, None)

        self.sr.flag = None
        self.sr.bgColor = None
        self.sr.hostile_attacking = None
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.hilite = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_HIDDEN)
        xtriui.UpdateEntry.Startup_update(self)



    def UpdateLabel(self):
        newLabel = ''
        for column in self.sr.node.columns:
            if column == 'DISTANCE':
                if not self.sr.node.Get('fmt_' + mls.UI_GENERIC_DISTANCE):
                    self.sr.node.Set('fmt_' + mls.UI_GENERIC_DISTANCE, util.FmtDist(self.sr.node.Get('sort_' + mls.UI_GENERIC_DISTANCE), maxdemicals=1))
                newLabel += '<right>' + self.sr.node.Get('fmt_' + mls.UI_GENERIC_DISTANCE) + '<t>'
            elif column == 'ANGULARVELOCITY':
                tr = getattr(mls, 'UI_GENERIC_' + column)
                if not self.sr.node.Get('fmt_' + tr):
                    d = self.sr.node.Get('sort_' + tr)
                    if d:
                        fmtd = '%.7f %s' % (d, cfg.eveunits.Get(112).displayName)
                        if fmtd:
                            self.sr.node.Set('fmt_' + tr, fmtd)
                newLabel += (self.sr.node.Get('fmt_' + tr) or '') + '<t>'
            elif column in ('VELOCITY', 'RADIALVELOCITY', 'TRANSVERSALVELOCITY'):
                tr = getattr(mls, 'UI_GENERIC_' + column)
                if not self.sr.node.Get('fmt_' + tr):
                    d = self.sr.node.Get('sort_' + tr)
                    if d:
                        fmtd = '%s %s' % (util.FmtAmt(d), mls.UI_GENERIC_MPERS)
                        if fmtd:
                            self.sr.node.Set('fmt_' + tr, fmtd)
                newLabel += (self.sr.node.Get('fmt_' + tr) or '') + '<t>'
            else:
                newLabel += (self.sr.node.Get(column) or '') + '<t>'

        self.SetLabel(newLabel[:-3])
        uthread.new(self.UpdateHint_thread)



    def UpdateHint_thread(self):
        if util.GetAttrs(self, 'sr', 'node') is not None and not self.destroyed:
            self.hint = sm.GetService('bracket').GetBracketName(self.sr.node.itemID)



    def UpdateEwar(self):
        ewarState = self.sr.node.Get('ewar', {})
        left = 0
        for (jamType, (flag, iconID,),) in sm.GetService('state').GetEwarTypes():
            icon = self.sr.Get('ewar' + jamType, None)
            if icon:
                icon.state = uiconst.UI_HIDDEN
            smartFilters = sm.GetService('tactical').GetEwarFiltered()
            if jamType in smartFilters:
                continue
            if ewarState.has_key(iconID):
                iconName = 'ewar%s' % jamType
                icon = self.sr.Get(iconName, None)
                if icon:
                    icon.state = uiconst.UI_NORMAL
                    sprite = self.sr.Get('ewar' + jamType)
                    sprite.left = left
                else:
                    icon = uicls.Icon(parent=self, name=iconName, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, left=left, width=16, height=16, idx=0, hint=sm.GetService('state').GetEwarHint(jamType), graphicID=iconID, ignoreSize=True)
                    self.sr.Set(iconName, icon)
                left += 16




    def SetLabel(self, label):
        if self.sr.label.text != label or self.sr.node.label != label:
            self.sr.node.label = label
            self.sr.label.text = label



    def Load(self, node, updateLoad = 0):
        self.hint = sm.GetService('bracket').GetBracketName(self.sr.node.itemID)
        self.itemID = self.sr.node.itemID
        self.UpdateIcon()
        self.updateItem = self.sr.node.updateItem
        xtriui.UpdateEntry.Load_update(self, self.sr.node.slimItem())
        self.UpdateLabel()
        self.UpdateEwar()
        self.sr.node.needReload = 0
        if self.sr.node.itemID not in sm.StartService('tactical').GetOverviewEntriesToRemove():
            self.SetLabelAlpha(1.0)
        else:
            self.SetLabelAlpha(0.25)



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight('Aj', autoWidth=1, singleLine=1) + 4
        return node.height



    def GetIconLeft(self, target = 0):
        offset = 2
        if mls.UI_GENERIC_ICON in self.sr.node.scroll.sr.widthToHeaders:
            ret = max(3, self.sr.node.scroll.sr.widthToHeaders[mls.UI_GENERIC_ICON] + offset)
        else:
            ret = 5
        if not target:
            return ret
        return ret - 1



    def UpdateIcon(self):
        if 'ICON' in self.sr.node.columns:
            self.sr.icon.left = self.GetIconLeft()
            if self.sr.hostile_attacking:
                self.sr.hostile_attacking.left = self.sr.icon.left - 1
            sm.GetService('tactical').UpdateFlagPositions(self)
            self.sr.icon.LoadIcon(self.sr.node.iconNo)
            self.sr.icon.state = uiconst.UI_DISABLED
            self.UpdateTargetStates()
            self.UpdateWreckEmpty(self.sr.node.slimItem())
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN



    def Targeting(self, state):
        self.ClearTargetStates()
        if state and self.sr.icon.state != uiconst.UI_HIDDEN:
            left = self.GetIconLeft(1)
            par = uicls.Container(name='targeting', align=uiconst.TOPLEFT, width=19, height=19, left=left, top=-1, parent=self)
            subpar = uicls.Container(name='sub', align=uiconst.TOALL, parent=par)
            subpar1 = uicls.Container(name='sub', align=uiconst.TOTOP, height=5, parent=subpar)
            subpar2 = uicls.Container(name='sub', align=uiconst.TOBOTTOM, height=5, parent=subpar)
            subpar11 = uicls.Container(name='sub', align=uiconst.TOLEFT, width=5, parent=subpar1)
            subpar12 = uicls.Container(name='sub', align=uiconst.TORIGHT, width=5, parent=subpar1)
            subpar21 = uicls.Container(name='sub', align=uiconst.TOLEFT, width=5, parent=subpar2)
            subpar22 = uicls.Container(name='sub', align=uiconst.TORIGHT, width=5, parent=subpar2)
            i = 0
            for each in (subpar11,
             subpar12,
             subpar21,
             subpar22):
                uicls.Line(parent=each, align=[uiconst.TOBOTTOM, uiconst.TOTOP][(i > 1)], weight=2, color=(1.0, 1.0, 1.0, 0.5))
                uicls.Line(parent=each, align=[uiconst.TORIGHT, uiconst.TOLEFT][(1 & i)], weight=2, color=(1.0, 1.0, 1.0, 0.5))
                i += 1

            uthread.pool('Tactical::Targeting', self.AnimateTargeting, par)



    def AnimateTargeting(self, par):
        while par and not par.destroyed:
            p = par.children[0]
            for i in xrange(5):
                p.left = p.top = p.width = p.height = i
                blue.pyos.synchro.Sleep(50)





    def Targeted(self, state, tryActivate = 1):
        self.ClearTargetStates()
        if state and self.sr.icon.state != uiconst.UI_HIDDEN:
            if self.sr.icon.state != uiconst.UI_HIDDEN:
                targeted = self.GetTargetedUI()
                targeted.left = self.GetIconLeft(1)
        elif tryActivate:
            self.ActiveTarget(0)



    def ActiveTarget(self, activestate):
        self.ClearTargetStates()
        if activestate and self.sr.icon.state != uiconst.UI_HIDDEN:
            if self.sr.icon.state != uiconst.UI_HIDDEN:
                targeted = self.GetTargetedUI()
                targeted.left = self.GetIconLeft(1)
        else:
            (targeted,) = sm.GetService('state').GetStates(self.stateItemID, [state.targeted])
            self.Targeted(targeted, 0)



    def UpdateTargetStates(self):
        for each in self.children[:]:
            if getattr(each, 'name', None) in ('activetarget', 'targeted', 'targeting'):
                each.left = self.GetIconLeft(1)




    def ClearTargetStates(self):
        for each in self.children[:]:
            if getattr(each, 'name', None) in ('activetarget', 'targeted', 'targeting'):
                each.Close()




    def OnDblClick(self, *args):
        slimItem = self.sr.node.slimItem()
        if slimItem:
            sm.GetService('menu').Activate(slimItem)



    def OnMouseEnter(self, *args):
        if self.sr.node:
            listentry.Generic.OnMouseEnter(self, *args)
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 1)



    def OnMouseExit(self, *args):
        if self.sr.node:
            listentry.Generic.OnMouseExit(self, *args)
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 0)



    def OnClick(self, *args):
        if self.sr.node:
            listentry.Generic.OnClick(self, *args)
        uicore.cmd.ExecuteCombatCommand(self.sr.node.itemID, uiconst.UI_CLICK)



    def GetMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(self.sr.node.itemID)



    def WreckEmpty(self, true):
        xtriui.UpdateEntry.WreckEmpty(self, true)



    def SetLabelAlpha(self, alpha):
        self.sr.label.color.a = alpha




class BaseTacticalEntry(listentry.Generic):
    __guid__ = 'listentry.BaseTacticalEntry'
    __notifyevents__ = ['OnStateChange']
    __update_on_reload__ = 1

    def init(self):
        self.gaugesInited = 0
        self.gaugesVisible = 0
        self.sr.gaugeParent = None
        self.sr.gauge_shield = None
        self.sr.gauge_armor = None
        self.sr.gauge_struct = None
        self.sr.dmgTimer = None



    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        sm.RegisterNotify(self)



    def Load(self, node):
        data = node
        (selected,) = sm.GetService('state').GetStates(data.itemID, [state.selected])
        node.selected = selected
        listentry.Generic.Load(self, node)
        self.sr.label.left = 20 + 16 * data.sublevel
        self.UpdateDamage()



    def UpdateDamage(self):
        if not util.InBubble(self.GetShipID()):
            self.HideDamageDisplay()
            return False
        d = self.sr.node
        if not getattr(d, 'slimItem', None):
            typeOb = cfg.invtypes.Get(d.typeID)
            groupID = typeOb.groupID
            categoryID = typeOb.categoryID
        else:
            slimItem = d.slimItem()
            if not slimItem:
                self.HideDamageDisplay()
                return False
            groupID = slimItem.groupID
            categoryID = slimItem.categoryID
        shipID = self.GetShipID()
        ret = False
        if shipID and categoryID in (const.categoryShip, const.categoryDrone):
            dmg = self.GetDamage(shipID)
            if dmg is not None:
                ret = self.SetDamageState(dmg)
                if self.sr.dmgTimer is None:
                    self.sr.dmgTimer = base.AutoTimer(1000, self.UpdateDamage)
            else:
                self.HideDamageDisplay()
        return ret



    def ShowDamageDisplay(self):
        self.InitGauges()



    def HideDamageDisplay(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_HIDDEN



    def GetDamage(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.dmgTimer = None
            return 
        ret = bp.GetDamageState(itemID)
        if ret is None:
            self.sr.dmgTimer = None
        return ret



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = node.Get('height', 0) or 32
        return node.height



    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.sr.node.itemID)



    def GetShipID(self):
        if self.sr.node:
            return self.sr.node.itemID



    def _OnClose(self, *args):
        listentry.Generic._OnClose(self, *args)
        sm.UnregisterNotify(self)



    def OnMouseEnter(self, *args):
        listentry.Generic.OnMouseEnter(self, *args)
        if self.sr.node:
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 1)



    def OnMouseExit(self, *args):
        listentry.Generic.OnMouseExit(self, *args)
        if self.sr.node:
            sm.GetService('state').SetState(self.sr.node.itemID, state.mouseOver, 0)



    def OnStateChange(self, itemID, flag, true, *args):
        if util.GetAttrs(self, 'sr', 'node') is None:
            return 
        if self.sr.node.itemID != itemID:
            return 
        if flag == state.mouseOver:
            self.Hilite(true)
        elif flag == state.selected:
            self.Select(true)



    def Hilite(self, state):
        if self.sr.node:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]



    def Select(self, state):
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]
        self.sr.node.selected = state



    def SetDamageState(self, state):
        self.InitGauges()
        visible = 0
        gotDmg = False
        for (i, gauge,) in enumerate((self.sr.gauge_shield, self.sr.gauge_armor, self.sr.gauge_struct)):
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                oldWidth = gauge.sr.bar.width
                gauge.sr.bar.width = int(gauge.width * round(state[i], 3))
                if gauge.sr.bar.width < oldWidth:
                    gotDmg = True
                gauge.state = uiconst.UI_DISABLED
                visible += 1

        self.gaugesVisible = visible
        return gotDmg



    def InitGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_NORMAL
            return 
        par = uicls.Container(name='gauges', parent=self, align=uiconst.TORIGHT, width=68, height=0, state=uiconst.UI_NORMAL, top=2, idx=0)
        uicls.Container(name='push', parent=par, align=uiconst.TORIGHT, width=4)
        for each in ('SHIELD', 'ARMOR', 'STRUCT'):
            g = uicls.Container(name=each, align=uiconst.TOTOP, width=64, height=9, left=-2)
            uicls.Container(name='push', parent=g, align=uiconst.TOBOTTOM, height=2)
            uicls.Label(text=each[:2], parent=g, left=68, top=-1, width=64, height=12, state=uiconst.UI_DISABLED, fontsize=9, letterspace=1, autoheight=False, autowidth=False)
            g.name = 'gauge_%s' % each.lower()
            uicls.Line(parent=g, align=uiconst.TOTOP)
            uicls.Line(parent=g, align=uiconst.TOBOTTOM)
            uicls.Line(parent=g, align=uiconst.TOLEFT)
            uicls.Line(parent=g, align=uiconst.TORIGHT)
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            par.children.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)

        self.sr.gaugeParent = par
        self.gaugesInited = 1




class OverviewSettings(uicls.Window):
    __guid__ = 'form.OverviewSettings'
    __notifyevents__ = ['OnTacticalPresetChange', 'OnOverviewPresetSaved']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.currentKey = None
        self.specialGroups = sm.GetService('state').GetNPCGroups()
        self.scope = 'inflight'
        self.SetCaption(mls.UI_INFLIGHT_OVERVIEWSETTINGS)
        self.minWidth = 300
        self.minHeight = 250
        self.SetWndIcon()
        self.SetHeaderIcon()
        settingsIcon = self.sr.headerIcon
        settingsIcon.state = uiconst.UI_NORMAL
        settingsIcon.GetMenu = self.GetPresetsMenu
        settingsIcon.expandOnLeft = 1
        settingsIcon.hint = ''
        self.SetTopparentHeight(0)
        self.sr.main = uiutil.GetChild(self, 'main')
        statetop = uicls.Container(name='statetop', parent=self.sr.main, align=uiconst.TOTOP, height=100)
        cb = uicls.Checkbox(text=mls.UI_INFLIGHT_APPLYTOSHIPS, parent=statetop, configName='applyOnlyToShips', retval=None, checked=settings.user.overview.Get('applyOnlyToShips', 1), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOPLEFT, pos=(9, 50, 260, 16))
        self.sr.applyOnlyToShips = cb
        cb = uicls.Checkbox(text=mls.UI_INFLIGHT_USESMALLCOLORTAGS, parent=statetop, configName='useSmallColorTags', retval=None, checked=settings.user.overview.Get('useSmallColorTags', 0), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOPLEFT, pos=(9, 66, 260, 16))
        self.sr.useSmallColorTags = cb
        uicls.Label(text=mls.UI_INFLIGHT_OVERVIEWHINT1, parent=statetop, align=uiconst.TOTOP, padding=(10, 7, 10, 12), state=uiconst.UI_NORMAL)
        statebtns = uicls.ButtonGroup(btns=[[mls.UI_GENERIC_RESETALL,
          self.ResetStateSettings,
          (),
          None]], parent=self.sr.main, idx=0)
        coltop = uicls.Container(name='coltop', parent=self.sr.main, align=uiconst.TOTOP, height=40)
        uicls.Label(text=mls.UI_INFLIGHT_OVERVIEWHINT2, parent=coltop, align=uiconst.TOTOP, padding=(10, 7, 10, 12), state=uiconst.UI_NORMAL)
        colbtns = uicls.ButtonGroup(btns=[[mls.UI_INFLIGHT_RESETCOLUMNS,
          self.ResetColumns,
          (),
          None]], parent=self.sr.main, idx=0)
        filtertop = uicls.Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP, height=54)
        uicls.Container(name='push', parent=filtertop, align=uiconst.TOTOP, height=36, state=uiconst.UI_DISABLED)
        shiptop = uicls.Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP, height=57)
        presetMenu = uicls.MenuIcon()
        presetMenu.GetMenu = self.GetShipLabelMenu
        presetMenu.left = 6
        presetMenu.top = 10
        presetMenu.hint = ''
        shiptop.children.append(presetMenu)
        cb = uicls.Checkbox(text=mls.UI_INFLIGHT_OVERVIEWHINT3, parent=shiptop, configName='hideCorpTicker', retval=None, checked=settings.user.overview.Get('hideCorpTicker', 0), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, pos=(0, 30, 0, 16))
        cb.padLeft = 8
        self.sr.applyOnlyToShips = cb
        overviewtabbtns = uicls.ButtonGroup(btns=[[mls.UI_CMD_APPLY,
          self.UpdateOverviewTab,
          (),
          None]], parent=self.sr.main, idx=0)
        misctop = uicls.Container(name='misctop', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding)
        overviewBroadcastsToTop = uicls.Checkbox(text=mls.UI_INFLIGHT_OVERVIEW_BROADCASTS_TO_TOP, parent=misctop, configName='overviewBroadcastsToTop', retval=None, checked=settings.user.overview.Get('overviewBroadcastsToTop', 0), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         0,
         260,
         0))
        uicls.Button(parent=misctop, label=mls.UI_INFLIGHT_RESETOVERVIEW, func=self.ResetAllOverviewSettings, pos=(const.defaultPadding,
         overviewBroadcastsToTop.height + const.defaultPadding,
         0,
         0))
        left = 10
        overviewtabtop = uicls.Container(name='overviewtabtop', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        comboOptions = []
        comboOptions.append([' ', None])
        overviewOptions = [(' ', [' ', None])]
        bracketOptions = [('  ', [mls.UI_CMD_SHOWALLBRACKETS, None])]
        presets = settings.user.overview.Get('overviewPresets', {})
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [mls.UI_GENERIC_NOTSAVED, label]))
                bracketOptions.append(('   ', [mls.UI_GENERIC_NOTSAVED, label]))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewOptions.append((lowerLabel, [overviewName, label]))
                    bracketOptions.append((lowerLabel, [overviewName, label]))
                else:
                    overviewOptions.append((lowerLabel, [label, label]))
                    bracketOptions.append((lowerLabel, [label, label]))

        overviewOptions = uiutil.SortListOfTuples(overviewOptions)
        bracketOptions = uiutil.SortListOfTuples(bracketOptions)
        top = 30
        offset = 6
        topOffset = 6
        widthOverview = uix.GetTextWidth(mls.UI_INFLIGHT_OVERVIEWPROFILE, 11, uppercase=1, hspace=1)
        widthBracket = uix.GetTextWidth(mls.UI_INFLIGHT_BRACKETPROFILE, 11, uppercase=1, hspace=1)
        widthText = 150
        self.tabedit = {}
        self.comboTabOverview = {}
        self.comboTabBracket = {}
        tabsettings = settings.user.overview.Get('tabsettings', {})
        for i in range(5):
            tabeditVal = ''
            comboTabOverviewVal = None
            comboTabBracketVal = None
            if tabsettings.has_key(i):
                tabeditVal = tabsettings[i].get('name', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
                comboTabOverviewVal = tabsettings[i].get('overview', None)
            left = 6
            tabedit = uicls.SinglelineEdit(name='edit' + str(i), parent=overviewtabtop, align=uiconst.TOPLEFT, pos=(left,
             top,
             80,
             0), setvalue=tabeditVal)
            self.tabedit[i] = tabedit
            left += tabedit.width + offset
            comboTabOverview = uicls.Combo(label='', parent=overviewtabtop, options=overviewOptions, name='comboTabOverview', select=comboTabOverviewVal, pos=(left,
             top,
             0,
             0), align=uiconst.TOPLEFT, width=widthOverview)
            self.comboTabOverview[i] = comboTabOverview
            left += comboTabOverview.width + offset
            comboTabBracket = uicls.Combo(label='', parent=overviewtabtop, options=bracketOptions, name='comboTabBracket', select=comboTabBracketVal, pos=(left,
             top,
             0,
             0), width=widthBracket, align=uiconst.TOPLEFT)
            self.comboTabBracket[i] = comboTabBracket
            top += topOffset + tabedit.height

        left = 6
        top = 10
        uicls.Label(text=mls.UI_INFLIGHT_TAB_NAME, parent=overviewtabtop, left=left, top=top, fontsize=12, state=uiconst.UI_DISABLED, color=None, singleline=1, uppercase=1)
        left += tabedit.width + offset
        uicls.Label(text=mls.UI_INFLIGHT_OVERVIEWPROFILE, parent=overviewtabtop, left=left, top=top, fontsize=12, state=uiconst.UI_DISABLED, color=None, singleline=1, uppercase=1)
        left += comboTabOverview.width + offset
        uicls.Label(text=mls.UI_INFLIGHT_BRACKETPROFILE, parent=overviewtabtop, left=left, top=top, fontsize=12, state=uiconst.UI_DISABLED, color=None, singleline=1, uppercase=1)
        left = 6
        top = 30
        btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_SELECTALL,
          self.SelectAll,
          (),
          None], [mls.UI_CMD_DESELECTALL,
          self.DeselectAll,
          (),
          None]], parent=self.sr.main, idx=0)
        uicls.Label(text=mls.UI_INFLIGHT_PRESETS, parent=filtertop, width=200, left=14, top=6, fontsize=9, letterspace=2, uppercase=1)
        acs = settings.user.overview.Get('activeOverviewPreset', 'default')
        overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(acs)
        if overviewName is not None:
            acs = overviewName
        if acs == 'ccp_notsaved':
            acs = mls.UI_GENERIC_NOTSAVED
        self.sr.presetText = uicls.Label(text=acs, parent=filtertop, width=200, left=14, top=21, fontsize=9, letterspace=2, uppercase=1)
        self.sr.scroll = uicls.Scroll(name='scroll', parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.SelectAll = self.SelectAll
        self.sr.scroll.sr.content.OnDropData = self.MoveStuff
        self.Maximize()
        self.state = uiconst.UI_NORMAL
        self.sr.statetabs = uicls.TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=statetop, idx=0, tabs=[[mls.UI_GENERIC_COLORTAG,
          statebtns,
          self,
          'flag'], [mls.UI_GENERIC_BACKGROUND,
          statebtns,
          self,
          'background'], [mls.UI_GENERIC_EWAR,
          None,
          self,
          'smartFilters']], groupID='overviewstatesTab', autoselecttab=0)
        self.sr.filtertabs = uicls.TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=filtertop, tabs=[[mls.UI_GENERIC_TYPES,
          btns,
          self,
          'filtertypes'], [mls.UI_GENERIC_STATES,
          None,
          self,
          'filterstates']], groupID='overviewfilterTab', autoselecttab=0)
        self.sr.tabs = uicls.TabGroup(name='overviewsettingsTab', height=18, align=uiconst.TOTOP, parent=self.sr.main, idx=0, tabs=[[mls.UI_GENERIC_FILTERS,
          btns,
          self,
          'filters',
          filtertop],
         [mls.UI_GENERIC_APPEARANCE,
          statebtns,
          self,
          'appearance',
          statetop],
         [mls.UI_GENERIC_COLUMNS,
          colbtns,
          self,
          'columns',
          coltop],
         [mls.UI_GENERIC_SHIPS,
          [],
          self,
          'ships',
          shiptop],
         [mls.UI_GENERIC_MISC,
          [],
          self,
          'misc',
          misctop],
         [mls.UI_GENERIC_OVERVIEW_TABS,
          overviewtabbtns,
          self,
          'overviewTabs',
          overviewtabtop]], groupID='overviewsettingsTab', UIIDPrefix='overviewSettingsTab')
        self.sr.statetabs.align = uiconst.TOBOTTOM
        self.ResetMinSize()



    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        if self.currentKey is None:
            return 
        if self.currentKey == 'columns':
            self.MoveColumn(idx)
        elif self.currentKey in ('flag', 'background'):
            self.Move(idx)
        elif self.currentKey == 'ships':
            self.MoveShipLabel(idx)



    def OnTacticalPresetChange(self, label, preset):
        overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
        if overviewName is not None:
            label = overviewName
        if label == 'ccp_notsaved':
            label = mls.UI_GENERIC_NOTSAVED
        self.sr.presetText.text = label
        if uiutil.IsVisible(self.sr.filtertabs) and self.sr.filtertabs.GetSelectedArgs() in ('filtertypes', 'filterstates'):
            self.sr.filtertabs.ReloadVisible()



    def OnOverviewPresetSaved(self):
        overviewOptions = [(' ', [' ', None])]
        bracketOptions = [(' ', [' ', ' '], [mls.UI_CMD_SHOWALLBRACKETS, None])]
        tabsettings = settings.user.overview.Get('tabsettings', {})
        presets = settings.user.overview.Get('overviewPresets', {})
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [mls.UI_GENERIC_NOTSAVED, label]))
                bracketOptions.append(('  ', [mls.UI_GENERIC_NOTSAVED, label]))
            else:
                overviewName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    overviewOptions.append((lowerLabel, [overviewName, label]))
                    bracketOptions.append((lowerLabel, [overviewName, label]))
                else:
                    overviewOptions.append((lowerLabel, [label, label]))
                    bracketOptions.append((lowerLabel, [label, label]))

        overviewOptions = uiutil.SortListOfTuples(overviewOptions)
        bracketOptions = uiutil.SortListOfTuples(bracketOptions)
        for i in range(5):
            comboTabOverviewVal = None
            comboTabBracketVal = None
            if tabsettings.has_key(i):
                comboTabOverviewVal = tabsettings[i].get('overview', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
            self.comboTabOverview[i].LoadOptions(overviewOptions, comboTabOverviewVal)
            self.comboTabBracket[i].LoadOptions(overviewOptions, comboTabBracketVal)




    def ExportSettings(self, *args):
        pass



    def ResetAllOverviewSettings(self, *args):
        if eve.Message('ResetAllOverviewSettings', {}, uiconst.YESNO) == uiconst.ID_YES:
            oldTabs = settings.user.overview.Get('tabsettings', {})
            values = settings.user.overview.GetValues()
            keys = values.keys()
            for key in keys:
                settings.user.overview.Delete(key)

            sm.StartService('tactical').PrimePreset()
            overviewWindow = sm.StartService('window').GetWindow('overview')
            if overviewWindow:
                newTabs = settings.user.overview.Get('tabsettings', {})
                overviewWindow.OnOverviewTabChanged(newTabs, oldTabs)
            stateSvc = sm.StartService('state')
            stateSvc.SetDefaultShipLabel('default')
            stateSvc.ResetColors()
            default = sm.GetService('overviewPresetSvc').GetDefaultOverviewGroups('default')
            settings.user.overview.Set('overviewPresets', {'default': default})
            self.CloseX()



    def DoFontChange(self):
        self.ResetMinSize()



    def ResetMinSize(self):
        maxBtnWidth = max([ uiutil.GetChild(wnd, 'btns').width for wnd in self.sr.main.children if wnd.name == 'btnsmainparent' ])
        margin = 12
        minWidth = max(self.minWidth, maxBtnWidth + margin * 2)
        self.SetMinSize((minWidth, self.minHeight))


    ResetMinSize = uiutil.ParanoidDecoMethod(ResetMinSize, ('sr', 'main'))

    def SelectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        groups = []
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 1
                if entry.panel:
                    entry.panel.Load(entry)
            if entry.__guid__ == 'listentry.Group':
                for item in entry.groupItems:
                    if type(item[0]) == list:
                        groups += item[0]
                    else:
                        groups.append(item[0])


        if groups:
            sm.GetService('tactical').SetSettings('groups', groups)



    def DeselectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 0
                if entry.panel:
                    entry.panel.Load(entry)

        sm.GetService('tactical').SetSettings('groups', [])



    def GetPresetsMenu(self):
        return sm.GetService('tactical').GetPresetsMenu()



    def GetShipLabelMenu(self):
        return [('%s [CC]' % mls.UI_GENERIC_PILOT, self.SetDefaultShipLabel, ('default',)), ('%s [CC,AA]' % mls.UI_GENERIC_PILOT, self.SetDefaultShipLabel, ('ally',)), ('[CC] %s &lt;AA&gt;' % mls.UI_GENERIC_PILOT, self.SetDefaultShipLabel, ('corpally',))]



    def SetDefaultShipLabel(self, setting):
        sm.GetService('state').SetDefaultShipLabel(setting)
        self.LoadShips()



    def Load(self, key):
        if self.currentKey is None or self.currentKey != key:
            self.cachedScrollPos = 0
        self.currentKey = key
        self.sr.scroll.state = uiconst.UI_NORMAL
        if key == 'filtertypes':
            self.LoadTypes()
        elif key == 'filterstates':
            self.LoadStateFilters()
        elif key == 'columns':
            self.LoadColumns()
        elif key == 'appearance':
            self.sr.statetabs.AutoSelect()
        elif key == 'filters':
            self.sr.filtertabs.AutoSelect()
        elif key == 'ships':
            self.LoadShips()
        elif key == 'misc':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'overviewTabs':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'smartFilters':
            self.LoadSmartFilters()
        else:
            self.LoadFlags()



    def LoadStateFilters(self):
        scrolllist = []
        all = sm.GetService('state').GetStateProps()
        filtered = sm.GetService('tactical').GetFilteredStates() or []
        for (flag, props,) in all.iteritems():
            data = util.KeyVal()
            data.label = props[0]
            data.props = props
            data.checked = flag not in filtered
            data.cfgname = 'filteredStates'
            data.retval = flag
            data.flag = flag
            data.hint = props[3]
            data.OnChange = self.CheckBoxChange
            scrolllist.append((props[0].lower(), listentry.Get('FlagEntry', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def LoadSmartFilters(self, selected = None):
        scrolllist = []
        stateMgr = sm.GetService('state')
        all = stateMgr.GetSmartFilterProps()
        filtered = sm.GetService('tactical').GetEwarFiltered() or []
        ewarTypeByState = stateMgr.GetEwarTypeByEwarState()
        for (flag, props,) in all.iteritems():
            data = util.KeyVal()
            data.label = props[0]
            data.props = props
            data.checked = ewarTypeByState[flag] not in filtered
            data.cfgname = 'smartFilters'
            data.retval = flag
            data.flag = flag
            data.hint = props[3]
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('FlagEntry', data=data))

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def LoadFlags(self, selected = None):
        where = self.sr.statetabs.GetSelectedArgs()
        flagOrder = sm.GetService('state').GetStateOrder(where)
        scrolllist = []
        i = 0
        for flag in flagOrder:
            props = sm.GetService('state').GetStateProps(flag)
            data = util.KeyVal()
            data.label = props[0]
            data.props = props
            data.checked = sm.GetService('state').GetStateState(where, flag)
            data.cfgname = where
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = props[3]
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('FlagEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def LoadShips(self, selected = None):
        shipLabels = sm.GetService('state').GetShipLabels()
        allLabels = sm.GetService('state').GetAllShipLabels()
        self.sr.applyOnlyToShips.SetChecked(sm.GetService('state').GetHideCorpTicker())
        hints = {None: '',
         'corporation': mls.UI_CORP_CORPTICKER,
         'alliance': mls.UI_SHARED_ALLIANCE_TICKER,
         'pilot name': mls.UI_SHARED_PILOTNAME,
         'ship name': mls.UI_SHARED_SHIPNAME,
         'ship type': mls.UI_SHARED_SHIPTYPE}
        comments = {None: mls.UI_INFLIGHT_STATETXT25,
         'corporation': mls.UI_INFLIGHT_STATETXT26,
         'alliance': mls.UI_INFLIGHT_STATETXT27}
        newlabels = [ label for label in allLabels if label['type'] not in [ alabel['type'] for alabel in shipLabels ] ]
        shipLabels += newlabels
        scrolllist = []
        for (i, flag,) in enumerate(shipLabels):
            data = util.KeyVal()
            data.label = hints[flag['type']]
            data.checked = flag['state']
            data.cfgname = 'shiplabels'
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = hints[flag['type']]
            data.comment = comments.get(flag['type'], '')
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('ShipEntry', data=data))

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def Move(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return 
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeStateOrder(self.GetWhere(), selected.flag, newIdx)
            self.LoadFlags(newIdx)



    def GetWhere(self):
        where = self.sr.statetabs.GetSelectedArgs()
        return where



    def ResetStateSettings(self, *args):
        where = self.sr.statetabs.GetSelectedArgs()
        settings.user.overview.Set('flagOrder', None)
        settings.user.overview.Set('iconOrder', None)
        settings.user.overview.Set('backgroundOrder', None)
        settings.user.overview.Set('flagStates', None)
        settings.user.overview.Set('iconStates', None)
        settings.user.overview.Set('backgroundStates', None)
        settings.user.overview.Set('stateColors', {})
        sm.GetService('state').InitColors(1)
        settings.user.overview.Set('stateBlinks', {})
        settings.user.overview.Set('applyOnlyToShips', 1)
        self.sr.applyOnlyToShips.SetChecked(1, 0)
        settings.user.overview.Set('useSmallColorTags', 0)
        self.sr.useSmallColorTags.SetChecked(0, 0)
        self.LoadFlags()
        sm.GetService('state').NotifyOnStateSetupChance('reset')



    def LoadColumns(self, selected = None):
        (userSet, displayColumns,) = sm.GetService('tactical').GetColumns()
        userSetOrder = sm.GetService('tactical').GetColumnOrder()
        missingColumns = [ col for col in sm.GetService('tactical').GetAllColumns() if col not in userSetOrder ]
        userSetOrder += missingColumns
        i = 0
        scrolllist = []
        for label in userSetOrder:
            data = util.KeyVal()
            data.label = getattr(mls, 'UI_GENERIC_' + label, label)
            data.checked = label in userSet
            data.cfgname = 'columns'
            data.retval = label
            data.canDrag = True
            data.isSelected = selected == i
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('ColumnEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def LoadTypes(self):
        categoryList = {}
        for (groupID, name,) in sm.GetService('tactical').GetAvailableGroups():
            for (cat, groupdict,) in self.specialGroups.iteritems():
                for (group, groupIDs,) in groupdict.iteritems():
                    if groupID in groupIDs:
                        catName = cat
                        groupID = groupIDs
                        name = group
                        break
                else:
                    continue

                break
            else:
                catName = cfg.invcategories.Get(cfg.invgroups.Get(groupID).categoryID).name

            if catName not in categoryList:
                categoryList[catName] = [(groupID, name)]
            elif (groupID, name) not in categoryList[catName]:
                categoryList[catName].append((groupID, name))

        sortCat = categoryList.keys()
        sortCat.sort()
        scrolllist = []
        for catName in sortCat:
            data = {'GetSubContent': self.GetCatSubContent,
             'label': catName,
             'MenuFunction': self.GetSubFolderMenu,
             'id': ('GroupSel', catName),
             'groupItems': categoryList[catName],
             'showlen': 1,
             'sublevel': 0,
             'state': 'locked'}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist, scrolltotop=0, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def GetSubFolderMenu(self, node):
        m = [None, (mls.UI_CMD_SELECTALL, self.SelectGroup, (node, True)), (mls.UI_CMD_DESELECTALL, self.SelectGroup, (node, False))]
        return m



    def SelectGroup(self, node, isSelect):
        groups = []
        for entry in node.groupItems:
            if type(entry[0]) == list:
                for entry1 in entry[0]:
                    groups.append(entry1)

            else:
                groups.append(entry[0])

        sm.StartService('tactical').ChangeSettings('groups', groups, isSelect)



    def GetCatSubContent(self, nodedata, newitems = 0):
        userSettings = sm.GetService('tactical').GetGroups()
        scrolllist = []
        for (groupID, name,) in nodedata.groupItems:
            if type(groupID) == list:
                for each in groupID:
                    if each in userSettings:
                        checked = 1
                        break
                else:
                    checked = 0

            else:
                name = cfg.invgroups.Get(groupID).groupName
                checked = groupID in userSettings
            data = util.KeyVal()
            data.label = name
            data.checked = checked
            data.cfgname = 'groups'
            data.retval = groupID
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        return scrolllist



    def MoveColumn(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return 
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeColumnOrder(selected.retval, newIdx)
            self.LoadColumns(newIdx)



    def ResetColumns(self, *args):
        settings.user.overview.Set('overviewColumnOrder', None)
        settings.user.overview.Set('overviewColumns', None)
        self.LoadColumns()
        sm.GetService('state').NotifyOnStateSetupChance('column reset')



    def CheckBoxChange(self, checkbox):
        if self and not self.destroyed:
            self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if config == 'applyOnlyToShips':
                sm.GetService('state').InitFilter()
                sm.GetService('state').NotifyOnStateSetupChance('filter')
            elif config == 'hideCorpTicker':
                sm.GetService('bracket').UpdateLabels()
            elif config == 'useSmallColorTags':
                sm.GetService('state').NotifyOnStateSetupChance('filter')
        if checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'groups':
                sm.GetService('tactical').ChangeSettings(checkbox.data['key'], checkbox.data['retval'], checkbox.checked)
            elif key == 'columns':
                sm.GetService('state').ChangeColumnState(checkbox.data['retval'], checkbox.checked)
            elif key == 'filteredStates':
                sm.GetService('tactical').ChangeSettings('filteredStates', checkbox.data['retval'], not checkbox.checked)
            if key == 'smartFilters':
                sm.GetService('tactical').ChangeSettings('smartFilters', sm.GetService('state').GetEwarTypeByEwarState()[checkbox.data['retval']], not checkbox.checked)
            elif key == self.GetWhere():
                sm.GetService('state').ChangeStateState(self.GetWhere(), checkbox.data['retval'], checkbox.checked)
            elif key == 'shiplabels':
                sm.GetService('state').ChangeShipLabels(checkbox.data['retval'], checkbox.checked)
        blue.pyos.synchro.Yield()
        uicore.registry.SetFocus(self.sr.scroll)



    def EwarCheckBoxChanged(self, checkbox):
        sm.GetService('tactical').ChangeSettings('smartFilters', checkbox.name, checkbox.checked)



    def MoveShipLabel(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return 
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeLabelOrder(selected.idx, newIdx)
            self.LoadShips(newIdx)



    def UpdateOverviewTab(self, *args):
        tabSettings = {}
        for key in self.tabedit.keys():
            editContainer = self.tabedit.get(key, None)
            comboTabBracketContainer = self.comboTabBracket.get(key, None)
            comboTabOverviewContainer = self.comboTabOverview.get(key, None)
            if not (editContainer and comboTabOverviewContainer and comboTabBracketContainer):
                continue
            if not editContainer.text:
                continue
            tabSettings[key] = {'name': editContainer.text,
             'bracket': comboTabBracketContainer.selectedValue,
             'overview': comboTabOverviewContainer.selectedValue}

        oldtabsettings = settings.user.overview.Get('tabsettings', {})
        sm.ScatterEvent('OnOverviewTabChanged', tabSettings, oldtabsettings)




class DraggableOverviewEntry(listentry.Checkbox):
    __guid__ = 'listentry.DraggableOverviewEntry'

    def Startup(self, *args):
        listentry.Checkbox.Startup(self, args)
        self.sr.posIndicatorCont = uicls.Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicator = uicls.Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicator.state = uiconst.UI_HIDDEN
        self.canDrag = False



    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return 
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]



    def OnDropData(self, dragObj, nodes, *args):
        if util.GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if util.GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)



    def OnDragEnter(self, dragObj, nodes, *args):
        self.sr.posIndicator.state = uiconst.UI_DISABLED



    def OnDragExit(self, *args):
        self.sr.posIndicator.state = uiconst.UI_HIDDEN




class ColumnEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ColumnEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode



    def ClickDiode(self, *args):
        self.sr.checkbox.OnClick()



    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)




class FlagEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.FlagEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.flag = None
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode



    def Load(self, node):
        listentry.Checkbox.Load(self, node)
        if self.sr.flag:
            f = self.sr.flag
            self.sr.flag = None
            f.Close()
        if node.cfgname not in ('filteredStates', 'smartFilters'):
            col = sm.GetService('state').GetStateColor(node.flag)
            blink = sm.GetService('state').GetStateBlink(node.cfgname, node.flag)
            icon = [0, (node.props[4] + 1) * 10][(node.cfgname == 'flag')]
            new = uicls.Container(parent=self, pos=(3, 4, 9, 9), name='flag', state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT, idx=0)
            uicls.Sprite(parent=new, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE)
            uicls.Fill(parent=new, color=col)
            new.children[1].color.a *= 0.75
            if blink:
                sm.GetService('ui').BlinkSpriteA(new.children[0], 1.0, 500, None, passColor=0)
                sm.GetService('ui').BlinkSpriteA(new.children[1], 1.0, 500, None, passColor=0)
            new.children[0].rectLeft = icon
            self.sr.flag = new



    def ClickDiode(self, *args):
        self.sr.checkbox.OnClick()



    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)



    def GetMenu(self):
        colors = sm.GetService('state').GetStateColors()
        m = []
        for (colorName, color,) in colors.iteritems():
            colorName = mls.GetLabelIfExists('UI_GENERIC_COLOR%s' % colorName.upper()) or colorName
            m.append((colorName, self.ChangeColor, (color,)))

        if self.sr.node.cfgname in ('flag', 'background'):
            m.append(None)
            m.append((mls.UI_SHARED_TOGGLEBLINK, self.ToggleBlink))
        return m



    def ToggleBlink(self):
        current = sm.GetService('state').GetStateBlink(self.sr.node.cfgname, self.sr.node.flag)
        sm.GetService('state').SetStateBlink(self.sr.node.cfgname, self.sr.node.flag, not current)
        self.Load(self.sr.node)



    def ChangeColor(self, color):
        sm.GetService('state').SetStateColor(self.sr.node.flag, color)
        self.Load(self.sr.node)




class ShipEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ShipEntry'

    def Startup(self, *args):
        listentry.DraggableOverviewEntry.Startup(self, args)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        diode = uiutil.GetChild(self, 'diode')
        diode.state = uiconst.UI_NORMAL
        diode.OnClick = self.ClickDiode
        self.sr.preEdit = uicls.SinglelineEdit(name='edit', parent=self, align=uiconst.TOPLEFT, pos=(32, 0, 20, 0))
        self.sr.preEdit.OnChange = self.OnPreChange
        self.sr.postEdit = uicls.SinglelineEdit(name='edit', parent=self, align=uiconst.TOPLEFT, pos=(132, 0, 20, 0))
        self.sr.postEdit.OnChange = self.OnPostChange
        self.sr.comment = uicls.Label(text='', parent=self, left=160, top=2, state=uiconst.UI_DISABLED)



    def Load(self, node):
        listentry.Checkbox.Load(self, node)
        self.sr.label.left = 60
        self.sr.preEdit.SetValue(self.sr.node.flag['pre'])
        self.sr.postEdit.SetValue(self.sr.node.flag['post'])
        if self.sr.node.flag['type'] is None:
            self.sr.postEdit.state = uiconst.UI_HIDDEN
        else:
            self.sr.postEdit.state = uiconst.UI_NORMAL
        self.sr.comment.text = self.sr.node.comment



    def ClickDiode(self, *args):
        self.sr.checkbox.OnClick()



    def OnClick(self, *args):
        listentry.Generic.OnClick(self, *args)



    def OnPreChange(self, text, *args):
        if self.sr.node.flag['pre'] != text:
            self.sr.node.flag['pre'] = text.replace('<', '&lt;').replace('>', '&gt;')
            self.sr.node.OnChange(self.sr.checkbox)



    def OnPostChange(self, text, *args):
        if self.sr.node.flag['post'] != text:
            self.sr.node.flag['post'] = text.replace('<', '&lt;').replace('>', '&gt;')
            self.sr.node.OnChange(self.sr.checkbox)




