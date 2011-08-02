import xtriui
import uix
import uthread
import log
import uiutil
import util
import listentry
import uiconst
import draw
import base
import uicls
MINHEIGHT = 400
MINWIDTH = 250
COLLAPSEDHEIGHT = 103

def GetJukeboxMenu():
    ret = []
    jukeboxSvc = sm.GetService('jukebox')
    if jukeboxSvc.jukeboxState == 'play':
        ret += [(mls.UI_SHARED_JUKEBOXPAUSE, lambda *args: jukeboxSvc.Pause())]
    else:
        ret += [(mls.UI_SHARED_JUKEBOXPLAY, lambda *args: jukeboxSvc.Play())]
    ret += [(mls.UI_SHARED_JUKEBOXNEXT, lambda *args: jukeboxSvc.AdvanceTrack()), (mls.UI_SHARED_JUKEBOXPREV, lambda *args: jukeboxSvc.AdvanceTrack(forward=False))]
    return ret



class JukeboxSvcWrapper():
    __guid__ = 'util.JukeboxSvcWrapper'

    def Startup(self):
        self.jukeboxSvc = sm.GetService('jukebox')
        self.jukeboxSvc.RegisterVolumeObserver(self)
        self.shuffleActive = self.jukeboxSvc.shuffleActive
        self.muted = not self.jukeboxSvc.GetVolume() > 0.0
        self.oldVolume = 0.0
        self.updateTime = 1000
        if self.jukeboxSvc.GetCurrentTrack() is not None:
            self.displayCurrentTrackTimer = base.AutoTimer(self.updateTime, self.UpdateElapsedTime)
        else:
            self.displayCurrentTrackTimer = None



    def GetMenu(self, *args):
        m = GetJukeboxMenu()
        m.append(None)
        m += uicls.Window.GetMenu(self, *args)
        return m



    def UpdateElapsedTime(self):
        self.elapsedTrackTime = self.jukeboxSvc.GetCurrentTrackElapsedTime()
        self.UpdateCurrTrackEdit()



    def DrawButtons(self, buttonCont):
        self.buttons = {}
        playing = self.jukeboxSvc.GetState() == 'play'
        buttons = [util.KeyVal(name='play', iconID='ui_73_16_225', left=22, function=self.Play, hidden=playing, hint=mls.UI_SHARED_JUKEBOXPLAY),
         util.KeyVal(name='pause', iconID='ui_73_16_226', left=22, function=self.Pause, hidden=not playing, hint=mls.UI_SHARED_JUKEBOXPAUSE),
         util.KeyVal(name='previous', iconID='ui_73_16_229', left=0, function=self.PlayPreviousTrack, hidden=False, hint=mls.UI_SHARED_JUKEBOXPREVIOUSTRACK),
         util.KeyVal(name='next', iconID='ui_73_16_228', left=44, function=self.PlayNextTrack, hidden=False, hint=mls.UI_SHARED_JUKEBOXNEXTTRACK),
         util.KeyVal(name='shuffleOff', iconID='ui_73_16_8', left=71, function=self.ShuffleOff, hidden=not self.shuffleActive, hint=mls.UI_SHARED_JUKEBOXTURNSHUFFLEOFF),
         util.KeyVal(name='shuffleOn', iconID='ui_73_16_3', left=71, function=self.ShuffleOn, hidden=self.shuffleActive, hint=mls.UI_SHARED_JUKEBOXTURNSHUFFLEON)]
        for b in buttons:
            btn = uix.GetBigButton(size=20, where=buttonCont, left=b.left, top=0, menu=0, iconMargin=0, hint=b.hint)
            btn.OnClick = b.function
            btn.OnDblClick = None
            if b.hidden:
                btn.state = uiconst.UI_HIDDEN
            uiutil.MapIcon(btn.sr.icon, b.iconID, ignoreSize=True)
            self.buttons[b.name] = btn




    def Play(self, *args):
        if hasattr(self, 'playlistSelected'):
            if self.playlistSelected != self.jukeboxSvc.GetCurrentPlaylist():
                self.jukeboxSvc.SetPlaylist(self.playlistSelected.name)
            selected = self.sr.tracksScroll.GetSelected()
            if selected:
                if selected[0].track != self.jukeboxSvc.GetCurrentTrack():
                    self.jukeboxSvc.PlayTrack(selected[0].trackIndex)
                    return 
        self.jukeboxSvc.Play()



    def Pause(self, *args):
        self.jukeboxSvc.Pause()



    def PlayNextTrack(self, *args):
        self.jukeboxSvc.AdvanceTrack()



    def PlayPreviousTrack(self, *args):
        self.jukeboxSvc.AdvanceTrack(forward=False)



    def ShuffleOn(self, *args):
        self.shuffleActive = True
        self.jukeboxSvc.SetShuffle(self.shuffleActive)
        self.buttons['shuffleOn'].state = uiconst.UI_HIDDEN
        self.buttons['shuffleOff'].state = uiconst.UI_NORMAL



    def ShuffleOff(self, *args):
        self.shuffleActive = False
        self.jukeboxSvc.SetShuffle(self.shuffleActive)
        self.buttons['shuffleOn'].state = uiconst.UI_NORMAL
        self.buttons['shuffleOff'].state = uiconst.UI_HIDDEN



    def Stop(self, *args):
        self.jukeboxSvc.StopJukebox()



    def SetVolume(self, slider):
        self.jukeboxSvc.SetVolume(slider.value)
        self.muted = not slider.value > 0.0
        self._ToggleMutedIcon()



    def OnVolumeUpdate(self, volume):
        volumeHandle = uiutil.GetChild(self.volumeSlider, 'volumeSlider')
        volumeHandle.SlideTo(volume)
        self.muted = not volume > 0.0
        self._ToggleMutedIcon()



    def DrawVolumeSlider(self, container):
        self.volumeIcon = uicls.Icon(icon='ui_73_16_230', parent=container, pos=(2, -3, 16, 16), ignoreSize=1, state=[uiconst.UI_HIDDEN, uiconst.UI_NORMAL][(not self.muted)])
        self.volumeIconMuted = uicls.Icon(icon='ui_73_16_37', parent=container, pos=(5, -3, 8, 16), ignoreSize=1, state=[uiconst.UI_HIDDEN, uiconst.UI_NORMAL][self.muted])
        self.volumeIconMuted.rectWidth = 8
        self.volumeIcon.OnClick = self.volumeIconMuted.OnClick = self.ToggleMuted
        self.maxVolumeIcon = uicls.Icon(icon='ui_73_16_35', parent=container, pos=(85, -3, 16, 16), ignoreSize=1)
        self.maxVolumeIcon.OnClick = self.SetMaxVolume
        self.volumeSlider = uix.GetSlider(name='volumeSlider', where=container, minval=0.0, maxval=1.0, hint=mls.UI_GENERIC_SOUNDVOLUME, align=uiconst.RELATIVE, width=60, height=10, left=20, setlabelfunc=lambda *args: None, endsliderfunc=self.SetVolume)
        self.volumeHandle = uiutil.GetChild(self.volumeSlider, 'volumeSlider')
        self.volumeHandle.SlideTo(self.jukeboxSvc.GetVolume())
        self.volumeHandle.SetValue(self.jukeboxSvc.GetVolume())



    def ToggleMuted(self):
        self.muted = not self.muted
        if self.muted:
            self.oldVolume = self.jukeboxSvc.GetVolume()
            settings.user.ui.Set('jukeboxOldVolume', self.oldVolume)
            self.volumeHandle.SlideTo(0.0)
            self.jukeboxSvc.SetVolume(0.0)
        else:
            self.oldVolume = settings.user.ui.Get('jukeboxOldVolume', self.jukeboxSvc.GetVolume())
            self.volumeHandle.SlideTo(self.oldVolume)
            self.jukeboxSvc.SetVolume(self.oldVolume)
        self._ToggleMutedIcon()



    def _ToggleMutedIcon(self):
        if self.muted:
            self.volumeIcon.state = uiconst.UI_HIDDEN
            self.volumeIconMuted.state = uiconst.UI_NORMAL
        else:
            self.volumeIcon.state = uiconst.UI_NORMAL
            self.volumeIconMuted.state = uiconst.UI_HIDDEN



    def SetMaxVolume(self):
        self.volumeHandle.SlideTo(1.0)
        self.jukeboxSvc.SetVolume(1.0)
        if self.muted:
            self.muted = False
            self._ToggleMutedIcon()



    def UpdateCurrTrackEdit(self):
        pass



    def OnJukeboxChange(self, event):
        if not self or self.destroyed:
            return 
        if event == 'track':
            trackIndex = self.jukeboxSvc.GetTrackIndex()
            if self.sr.Get('tracksScroll', None) is not None:
                self.sr.tracksScroll.DeselectAll()
                viewingCurrentPlaylist = self.playlistSelected == self.jukeboxSvc.GetCurrentPlaylist()
                if trackIndex > -1 and viewingCurrentPlaylist:
                    self.sr.tracksScroll.SetSelected(trackIndex)
                self.trackPlaying = self.jukeboxSvc.GetCurrentTrack()
            if self.jukeboxSvc.jukeboxState == 'play':
                if self.displayCurrentTrackTimer is None:
                    self.displayCurrentTrackTimer = base.AutoTimer(self.updateTime, self.UpdateElapsedTime)
                if self.buttons['play'].state == uiconst.UI_NORMAL:
                    self.buttons['pause'].state = uiconst.UI_NORMAL
                    self.buttons['play'].state = uiconst.UI_HIDDEN
            if getattr(self, 'UpdateScrollPosition', None):
                self.UpdateScrollPosition(trackIndex)
        elif event in ('stop', 'stinger'):
            self.buttons['pause'].state = uiconst.UI_HIDDEN
            self.buttons['play'].state = uiconst.UI_NORMAL
            self.trackPlaying = None
            self.elapsedTrackTime = 0
            if self.displayCurrentTrackTimer:
                self.UpdateCurrTrackEdit()
                self.displayCurrentTrackTimer = None
        elif event in self.buttons.keys():
            for each in self.buttons.keys():
                self.buttons[each].active = 0

            self.buttons[event].active = 1
            if event == 'play':
                if self.displayCurrentTrackTimer is None:
                    self.displayCurrentTrackTimer = base.AutoTimer(self.updateTime, self.UpdateElapsedTime)
                self.buttons['pause'].state = uiconst.UI_NORMAL
                self.buttons['play'].state = uiconst.UI_HIDDEN
            elif event == 'pause':
                self.displayCurrentTrackTimer = None
                self.buttons['pause'].state = uiconst.UI_HIDDEN
                self.buttons['play'].state = uiconst.UI_NORMAL
        elif event == 'playlist':
            pass
        else:
            log.LogWarn('jukebox', 'Unknown change?', event)




class JukeboxPlaylist(listentry.Generic):
    __guid__ = 'listentry.JukeboxPlaylist'

    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.line.state = uiconst.UI_HIDDEN




class JukeboxTrack(listentry.Generic):
    __guid__ = 'listentry.JukeboxTrack'

    def Startup(self, *args):
        listentry.Generic.Startup(self)
        self.sr.icon = uicls.Icon(icon='ui_73_16_225', parent=self, pos=(3, 3, 12, 12), ignoreSize=1)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        isPlaying = self.sr.node.track == sm.GetService('jukebox').GetCurrentTrack()
        if isPlaying:
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.icon.color.a = 0.9
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN



    def GetMenu(self):
        if len(self.sr.node.scroll.GetSelectedNodes(self.sr.node)) <= 1:
            self.OnClick()
        return self.sr.node.GetMenu(self)




class Jukebox(uicls.Window, JukeboxSvcWrapper):
    __guid__ = 'form.jukebox'
    __notifyevents__ = ['OnJukeboxChange', 'OnAudioDeactivated']
    default_width = 600
    default_height = 450

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        JukeboxSvcWrapper.Startup(self)
        self.SetCaption(mls.UI_SHARED_JUKEBOX)
        self.SetWndIcon('ui_12_64_5', hidden=True)
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([MINWIDTH, MINHEIGHT])
        self.MakeUnstackable()
        self.playlistExpanded = bool(settings.user.ui.Get('JukeboxPlaylistExpanded', 1))
        self.elapsedTrackTime = 0
        jukeboxMinimized = sm.GetService('window').GetWindow('JukeboxMinimized')
        if jukeboxMinimized is not None:
            jukeboxMinimized.CloseX()
        self.sr.playerCont = uicls.Container(name='playerCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 55), padding=(5, 6, 5, 5))
        self.sr.currTrackContainer = uicls.Container(name='currTrackContainer', parent=self.sr.playerCont, align=uiconst.TOTOP, pos=(0, 0, 0, 19), clipChildren=True)
        self.sr.currTrackTimeEdit = uicls.Label(text='', parent=self.sr.currTrackContainer, align=uiconst.TOPLEFT, left=5, top=2, state=uiconst.UI_NORMAL)
        self.sr.currTrackNameEdit = uicls.Label(text='', parent=self.sr.currTrackContainer, align=uiconst.TOPLEFT, left=55, top=2, state=uiconst.UI_NORMAL)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(parent=self.sr.currTrackContainer, padding=(-1, -1, -1, -1))
        buttonCont = uicls.Container(name='buttonCont', parent=self.sr.playerCont, align=uiconst.TOTOP, pos=(0, 0, 0, 15), padding=(0, 10, 0, 0))
        self.DrawButtons(buttonCont)
        self.DrawVolumeSlider(uicls.Container(parent=self.sr.playerCont, align=uiconst.TOPRIGHT, pos=(0, 35, 100, 30)))
        uicls.Line(parent=self.sr.main, align=uiconst.TOTOP)
        self.sr.playlistsHeaderCont = uicls.Container(name='playlistsHeaderCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 16), padding=(0, 3, 0, 0))
        self.sr.bottomCont = uicls.Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(3, 0, 3, 0))
        self.sr.playlistsCont = uicls.Container(name='playlistsCont', parent=self.sr.bottomCont, align=uiconst.TOLEFT, pos=(0, 0, 120, 0))
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.bottomCont, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.playlistsCont, 'width', 'x', 80, 200)
        self.sr.currPlaylistCont = uicls.Container(name='currPlaylistCont', parent=self.sr.bottomCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.expanderCont = uicls.Container(name='expanderCont', parent=self.sr.playlistsHeaderCont, align=uiconst.TOPLEFT, pos=(5, -1, 10, 10))
        self.expanderButton = uicls.ExpanderButton(align=uiconst.TOPRIGHT, parent=self.sr.expanderCont, expanded=not self.playlistExpanded, expandFunc=self.ExpandPlaylists, collapseFunc=self.CollapsePlaylists)
        uicls.Label(text=mls.UI_SHARED_JUKEBOXPLAYLISTS.upper(), parent=uicls.Container(parent=self.sr.playlistsHeaderCont, align=uiconst.TOPLEFT, pos=(18, 1, 0, 14)), align=uiconst.TOPLEFT, fontsize=10, letterspace=1, state=uiconst.UI_NORMAL)
        attrToHeader = {'title': mls.UI_SHARED_JUKEBOXTITLE,
         'duration': mls.UI_SHARED_JUKEBOXDURATION,
         'id': mls.UI_SHARED_JUKEBOXNUMBER}
        self.sortBy = attrToHeader[self.jukeboxSvc.GetSortAttr()]
        self.reverseSort = self.jukeboxSvc.GetSortDirection()
        btns = [[mls.UI_GENERIC_NEW,
          self.CreatePlaylist,
          None,
          81]]
        uicls.ButtonGroup(btns=btns, parent=self.sr.playlistsCont, line=False)
        self.sr.playlistsScroll = uicls.Scroll(parent=self.sr.playlistsCont, name='playlistsScroll')
        self.sr.playlistsScroll.multiSelect = False
        self.sr.playlistsScroll.Confirm = self.Play
        self.sr.playlistsScroll.OnSelectionChange = self.OnPlaylistSelectionChanged
        btns = [[mls.UI_SHARED_JUKEBOXADDTRACKS,
          self.AddTracksToPlaylist,
          (),
          81]]
        self.btnGroup = uicls.ButtonGroup(btns=btns, parent=self.sr.currPlaylistCont, line=False)
        self.sr.tracksScroll = uicls.Scroll(parent=self.sr.currPlaylistCont, name='currPlaylistScroll')
        self.sr.tracksScroll.sr.id = 'JukeboxCurrPlaylistScroll'
        self.sr.tracksScroll.Confirm = self.Play
        self.sr.tracksScroll.Sort = self.SortTracks
        self.trackPlaying = self.jukeboxSvc.GetCurrentTrack()
        self.PopulatePlaylistsScroll()
        self.UpdateCurrTrackEdit()
        if not self.playlistExpanded:
            uthread.new(self.CollapsePlaylists)



    def SortTracks(self, by = None, reversesort = 0, forceHilite = 0, playlistName = None):
        validAttributes = {mls.UI_SHARED_JUKEBOXTITLE: 'title',
         mls.UI_SHARED_JUKEBOXDURATION: 'duration',
         mls.UI_SHARED_JUKEBOXNUMBER: 'id'}
        sortAttr = validAttributes[by]
        if playlistName is None:
            playlistName = self.playlistSelected.name
        self.sortBy = by
        self.reverseSort = reversesort
        self.jukeboxSvc.Sort(sortAttr, reversesort, playlistName)
        self.PopulateTracksScroll(self.playlistSelected)
        self.sr.tracksScroll.HiliteSorted(by, reversesort)
        self.sr.tracksScroll.sortBy = by



    def OnPlaylistSelectionChanged(self, selectedPlaylists):
        if len(selectedPlaylists) == 0:
            index = 0
            if self.playlistSelected:
                index = self.playlistSelected.idx
            self.sr.playlistsScroll.SetSelected(index)
            return 
        self.playlistSelected = self.jukeboxSvc.GetPlaylist(selectedPlaylists[0].name)
        self.PopulateTracksScroll(self.playlistSelected)
        self.SortTracks(self.sortBy, self.reverseSort, playlistName=selectedPlaylists[0].name)
        if self.playlistSelected == self.jukeboxSvc.GetCurrentPlaylist():
            self.sr.tracksScroll.SetSelected(self.jukeboxSvc.GetTrackIndex())
        btn = self.btnGroup.GetBtnByLabel(mls.UI_SHARED_JUKEBOXADDTRACKS)
        if self.playlistSelected and not self.playlistSelected.isLocked:
            btn.Enable()
        else:
            btn.Disable()



    def OnJukeboxChange(self, event):
        if not self or self.destroyed:
            return 
        JukeboxSvcWrapper.OnJukeboxChange(self, event)
        if event == 'playlist':
            self.PopulatePlaylistsScroll()
        self.RefreshEntries(self.sr.tracksScroll)



    def UpdateScrollPosition(self, trackIndex):
        numEntries = max(1, len(self.sr.tracksScroll.GetNodes()) - 1)
        self.sr.tracksScroll.ScrollToProportion(float(trackIndex) / numEntries)



    def OnAudioDeactivated(self, *args):
        self.CloseX()



    def OnDblClick(self, *args):
        self.dblclicktimer = None
        self = sm.GetService('window').GetWindow('jukeboxMinimized', create=1, expandIfCollapsed=False)



    def ExpandPlaylists(self, *args):
        self.playlistExpanded = True
        self.sr.bottomCont.state = uiconst.UI_PICKCHILDREN
        self.UnlockHeight()
        newHeight = int(settings.user.ui.Get('JukeboxExpandedHeight', MINHEIGHT))
        if newHeight < MINHEIGHT:
            newHeight = MINHEIGHT
        self.height = newHeight
        settings.user.ui.Set('JukeboxPlaylistExpanded', 1)



    def CollapsePlaylists(self, *args):
        self.playlistExpanded = False
        settings.user.ui.Set('JukeboxExpandedHeight', self.height)
        self.LockHeight(COLLAPSEDHEIGHT)
        self.sr.bottomCont.state = uiconst.UI_HIDDEN
        settings.user.ui.Set('JukeboxPlaylistExpanded', 0)



    def OnExpanded(self, *args):
        if getattr(self, 'expanderButton', False):
            self.expanderButton.SetButtonState(expanded=self.playlistExpanded)



    def PopulatePlaylistsScroll(self):
        playlists = self.jukeboxSvc.GetPlaylists()
        scrolllist = []
        for (key, playlist,) in playlists.iteritems():
            if playlist.isHidden:
                continue
            data = util.KeyVal(name=key, tracks=playlist.tracks)
            data.label = self.GetTrackTitle('', playlist.GetDisplayName())
            data.hint = self.GetTrackTitle('', key)
            data.OnDblClick = self.Play
            data.GetMenu = self.GetPlaylistMenu
            data.ignoreRightClick = 1
            data.isLocked = playlist.isLocked
            sortBy = playlist.GetDisplayName().lower()
            if playlist.isLocked:
                sortBy = ' ' + sortBy
            scrolllist.append((sortBy, listentry.Get('JukeboxPlaylist', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.sr.playlistsScroll.Load(contentList=scrolllist)
        if getattr(self, 'playlistSelected', None):
            playlistName = self.playlistSelected.name
        else:
            playlistName = self.jukeboxSvc.GetCurrentPlaylist().name
        for entry in self.sr.playlistsScroll.GetNodes():
            if entry.name == playlistName:
                self.sr.playlistsScroll.SelectNode(entry)
                return 




    def GetPlaylistMenu(self, playlist):
        m = [[mls.UI_SHARED_JUKEBOXPLAY, self.LoadAndPlayPlaylist, (playlist.sr.node,)]]
        if not playlist.sr.node.isLocked:
            m.append([mls.UI_CMD_DELETE, self.RemovePlaylist, (playlist.sr.node.name,)])
            m.append([mls.UI_CMD_RENAME, self.RenamePlaylist, (playlist.sr.node,)])
        return m



    def RenamePlaylist(self, node):
        retval = self.GetNewPlaylistNameWindow(node.label)
        if retval is not None:
            p = self.jukeboxSvc.GetPlaylist(node.name)
            p.SetDisplayName(unicode(retval[mls.UI_SHARED_JUKEBOXPLAYLISTNAME]))
            self.PopulatePlaylistsScroll()



    def RemovePlaylist(self, playlistName):
        if playlistName == self.playlistSelected.name:
            self.playlistSelected = None
        self.jukeboxSvc.RemovePlaylist(playlistName)



    def PopulateTracksScroll(self, playlist):
        scrolllist = []
        self.UpdateCurrTrackEdit()
        for (i, track,) in enumerate(playlist.tracks):
            data = util.KeyVal(track.__dict__)
            title = self.GetTrackTitle(track.message, track.title)
            data.label = '<t>%s<t>%s<t>%d:%.2d' % (1 + track.id,
             title,
             int(track.duration // 60),
             int(track.duration % 60))
            data.height = 20
            data.OnDblClick = self.Play
            data.GetMenu = self.GetTrackMenu
            data.trackIndex = i
            data.track = track
            data.playlist = playlist
            data.charIndex = title.lower()
            scrolllist.append(listentry.Get('JukeboxTrack', data=data))

        self.sr.tracksScroll.Load(contentList=scrolllist, noContentHint=mls.UI_SHARED_JUKEBOXNOTRACKS, headers=['',
         mls.UI_SHARED_JUKEBOXNUMBER,
         mls.UI_SHARED_JUKEBOXTITLE,
         mls.UI_SHARED_JUKEBOXDURATION], ignoreSort=True, reversesort=self.reverseSort)



    def GetTrackMenu(self, *args):
        tracks = self.sr.tracksScroll.GetSelected()
        m = []
        if not self.playlistSelected.isLocked:
            m.append([mls.UI_SHARED_JUKEBOXREMOVEFROM, self.RemoveSelectedTracks])
        return m



    def RemoveSelectedTracks(self, *args):
        for track in self.sr.tracksScroll.GetSelected():
            if track.track == self.trackPlaying:
                self.Stop()
                self.trackPlaying = None
            self.playlistSelected.RemoveTrack(track.id)

        self.PopulateTracksScroll(self.playlistSelected)
        self.playlistSelected.SaveAsM3U()



    def UpdateCurrTrackEdit(self):
        if self.trackPlaying is not None:
            trackName = self.GetTrackTitle('', self.trackPlaying.title)
            self.sr.currTrackTimeEdit.text = util.FmtTime(self.elapsedTrackTime * SEC)
            self.sr.currTrackNameEdit.text = trackName
        else:
            self.sr.currTrackTimeEdit.text = util.FmtTime(0 * SEC)
            self.sr.currTrackNameEdit.text = ''



    def LoadAndPlayPlaylist(self, node, *args):
        self.sr.playlistsScroll.SelectNode(node)
        self.Play()



    def AddTracksToPlaylist(self):
        eve.Message('JukeboxAddTracks')
        ret = uix.GetFileDialog(path=None, fileExtensions=['mp3'], multiSelect=True, selectionType=uix.SEL_BOTH)
        if ret is None:
            return 
        total = len(ret.folders + ret.files)
        for (i, f,) in enumerate(ret.folders + ret.files):
            self.playlistSelected.Load(f)
            sm.GetService('loading').ProgressWnd('Loading track information', portion=i, total=total)

        sm.GetService('loading').ProgressWnd('Loading track information', portion=total, total=total)
        self.PopulateTracksScroll(self.playlistSelected)
        self.playlistSelected.SaveAsM3U()



    def CreatePlaylist(self, *args):
        self._CreateImportPlaylist(create=True)



    def _CreateImportPlaylist(self, create):
        path = None
        if not create:
            path = uix.GetFileDialog(fileExtensions=['.m3u', '.pls'], selectionType=uix.SEL_BOTH)
            if path is not None:
                if len(path.get('files')) > 0:
                    path = path.get('files')[0]
                else:
                    path = path.get('folders')[0]
        retval = self.GetNewPlaylistNameWindow()
        if retval is not None:
            playlistName = unicode(retval[mls.UI_SHARED_JUKEBOXPLAYLISTNAME]).strip()
            playlist = self.jukeboxSvc.AddPlaylist(playlistName, path, isNew=True)
            playlist.SaveAsM3U()



    def GetNewPlaylistNameWindow(self, name = ''):
        format = [{'type': 'text',
          'text': mls.UI_SHARED_JUKEBOXPLAYLISTNAME,
          'frame': 0}, {'type': 'edit',
          'setvalue': name,
          'width': 140,
          'label': '_hide',
          'key': mls.UI_SHARED_JUKEBOXPLAYLISTNAME,
          'maxlength': 20,
          'required': 1}, {'type': 'errorcheck',
          'errorcheck': self.PlaylistNameErrorCheck}]
        return uix.HybridWnd(format, mls.UI_SHARED_JUKEBOXENTERNAME, 1, None, uiconst.OKCANCEL, minW=200, minH=110, icon=uiconst.QUESTION)



    def PlaylistNameErrorCheck(self, retval):
        playlistName = unicode(retval[mls.UI_SHARED_JUKEBOXPLAYLISTNAME]).strip().lower()
        if playlistName in [ self.GetTrackTitle('', n.GetDisplayName()).lower() for n in self.jukeboxSvc.GetPlaylists().values() ]:
            return mls.UI_SHARED_JUKEBOXALREADYEXISTS
        return ''



    def GetTrackTitle(self, wiseMessage = None, trackName = None):
        if wiseMessage is None:
            return trackName
        else:
            if wiseMessage.startswith('music_'):
                wiseMessage = wiseMessage[6:]
            if wiseMessage.endswith('_play'):
                wiseMessage = wiseMessage[:5]
            pos = trackName.rfind('mls://')
            if pos > -1:
                mlskey = trackName[(pos + 6):]
            else:
                mlskey = 'UI_AUDIO_' + wiseMessage.upper()
            if mls.HasLabel(mlskey):
                return getattr(mls, mlskey)
            return trackName.lstrip()



    def RefreshEntries(self, scroll):
        for e in scroll.sr.entries:
            if hasattr(e.panel, 'Load'):
                e.panel.Load(e)




    def OnClose_(self, *args):
        self.jukeboxSvc.UnregisterVolumeObserver(self)




class JukeboxMinimized(uicls.Window, JukeboxSvcWrapper):
    __guid__ = 'form.jukeboxMinimized'
    __notifyevents__ = ['OnJukeboxChange', 'OnAudioDeactivated']
    default_width = 250
    default_height = 40

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        JukeboxSvcWrapper.Startup(self)
        self.SetCaption(mls.UI_SHARED_JUKEBOX)
        self.SetWndIcon('ui_12_64_5', hidden=True)
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        self.MakeUnstackable()
        self.MakeUncollapseable()
        self.sr.main = uiutil.GetChild(self, 'main')
        buttonCont = uicls.Container(name='buttonCont', parent=self.sr.main, align=uiconst.TOPLEFT, pos=(1, 1, 100, 50), padding=(0, 0, 0, 0))
        self.DrawButtons(buttonCont)
        self.DrawVolumeSlider(uicls.Container(parent=self.sr.main, align=uiconst.TOPRIGHT, pos=(8, 6, 100, 30)))
        jukebox = sm.GetService('window').GetWindow('jukebox')
        if jukebox is not None:
            jukebox.CloseX()
        uthread.new(self.SetCorrectSize)



    def OnDblClick(self, *args):
        sm.GetService('window').GetWindow('jukebox', create=1)



    def OnExpanded(self, *args):
        self.LockHeight(40)



    def SetCorrectSize(self):
        self.SetMinSize([250, 40])
        self.LockHeight(40)



    def OnAudioDeactivated(self, *args):
        self.CloseX()



    def OnClose_(self, *args):
        self.jukeboxSvc.UnregisterVolumeObserver(self)



exports = {'util.GetJukeboxMenu': GetJukeboxMenu}

