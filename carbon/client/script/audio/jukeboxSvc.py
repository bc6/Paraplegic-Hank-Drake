import service
import blue
import yaml
import util
import sys
import os
import random
import localization

class JukeboxSvc(service.Service):
    __guid__ = 'svc.jukebox'
    __sessionparams__ = []
    __exportedcalls__ = {'Play': [],
     'PlayStinger': [],
     'Pause': [],
     'StopJukebox': [],
     'AdvanceTrack': [],
     'GetPlaylist': [],
     'GetTrackIndex': [],
     'GetVolume': [],
     'GetState': [],
     'SetPlaylist': [],
     'AddPlaylist': [],
     'SavePlaylist': [],
     'RemovePlaylist': [],
     'HasPlaylist': [],
     'SetVolume': [],
     'PlayTrack': [],
     'TranslateTitle': [],
     'Sort': [],
     'RegisterVolumeObserver': [],
     'UnregisterVolumeObserver': [],
     'ReportJukeboxChange': [],
     'SetState': []}
    __startupdependencies__ = ['audio', 'settings']
    __notifyevents__ = ['ProcessSessionChange',
     'OnAudioActivated',
     'OnAudioDeactivated',
     'OnWiseJukeboxEventReceived']

    def __init__(self):
        service.Service.__init__(self)
        self.playlists = {}
        self.playlist = None
        self.currentTrackIndex = self.GetAudioSetting('jukeboxTrackIndex', -1)
        self.currTrackStartedAt = 0
        self.currTrackPausedAt = None
        self.shuffleActive = self.GetAudioSetting('jukeboxShuffle', False)
        self.stingerMessage = None
        self.messageQueue = []
        self.resumeOnActivate = self.GetAudioSetting('resumeJukeboxOnActivate', False)
        self.jukeboxState = self.GetAudioSetting('ampState', 'play')
        self.volume = 0.0
        self.playlistLoaded = False
        self.ingamePlayList = ''
        self.volumeObservers = []
        cachePath = blue.os.ResolvePathForWriting(u'cache:/Jukebox/')
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)



    def Run(self, ms = None):
        self.SetVolume(self.GetVolume())
        cachePath = blue.os.ResolvePathForWriting(u'cache:/Jukebox/')
        if os.path.exists(cachePath):
            for (root, folders, playlists,) in os.walk(unicode(cachePath)):
                for playlist in playlists:
                    try:
                        self.AddPlaylist(playlist[:playlist.rfind('.')], os.path.join(cachePath, playlist))
                    except UserError:
                        self.LogWarn('Discovered non-loadable playlists during start up. These will not be available in the jukebox.')
                        sys.exc_clear()





    def RegisterVolumeObserver(self, obs):
        if obs not in self.volumeObservers:
            self.volumeObservers.append(obs)



    def UnregisterVolumeObserver(self, obs):
        if obs in self.volumeObservers:
            self.volumeObservers.remove(obs)



    def NotifyObservers(self, volume):
        for obs in self.volumeObservers:
            if hasattr(obs, 'OnVolumeUpdate'):
                obs.OnVolumeUpdate(volume)
            else:
                self.volumeObservers.remove(obs)




    def GetAudioSetting(self, settingName, defaultValue):
        return settings.public.audio.Get(settingName, defaultValue)



    def SetAudioSetting(self, settingName, value):
        settings.public.audio.Set(settingName, value)



    def OnAudioActivated(self):
        self.SetVolume(self.GetVolume())
        if len(self.playlists) == 0:
            self.AddPlaylist('mls://Carbon/Audio/Jukebox/DefaultPlaylist', self.ingamePlayList)
        if self.playlist is None:
            self.SetPlaylist('mls://Carbon/Audio/Jukebox/DefaultPlaylist')
        if self.resumeOnActivate:
            self.Play()



    def OnAudioDeactivated(self):
        if self.GetState() == 'play':
            self.StopJukebox()
            self.resumeOnActivate = True
        else:
            self.resumeOnActivate = False
        self.SetAudioSetting('resumeJukeboxOnActivate', self.resumeOnActivate)



    def OnWiseJukeboxEventReceived(self, soundIdentifier):
        if soundIdentifier in self.messageQueue:
            self.messageQueue.remove(soundIdentifier)
        if soundIdentifier == self.stingerMessage:
            self.stingerMessage = None
        if len(self.messageQueue) == 0 and self.stingerMessage is None:
            self.AdvanceTrack(automatic=True)



    def ProcessSessionChange(self, *args):
        if not getattr(session, 'charid', None):
            return 
        if not self.playlistLoaded:
            try:
                desiredPlaylist = self.GetAudioSetting('jukeboxPlaylist', self.ingamePlayList)
                if desiredPlaylist not in self.playlists:
                    desiredPlaylist = self.ingamePlayList
                self.SetPlaylist(desiredPlaylist)
                self.playlistLoaded = True
                userDesiredState = self.GetAudioSetting('ampState', 'play')
                if userDesiredState == 'play' and self.audio.IsActivated():
                    desiredTrackIndex = self.GetAudioSetting('jukeboxTrackIndex', 0)
                    if desiredTrackIndex >= self.playlist.GetLength():
                        desiredTrackIndex = 0
                    self.PlayTrack(desiredTrackIndex)
            except RuntimeError as err:
                self.LogError('Runtime error in session change', err)
                sys.exc_clear()



    def TranslateTitle(self, title):
        pos = title.rfind('mls://')
        if pos > -1:
            mlskey = title[(pos + 6):]
        else:
            return title.lstrip()
        if localization.IsValidLabel(mlskey):
            return localization.GetByLabel(mlskey)
        else:
            return title.lstrip()



    def Play(self):
        currentState = self.GetState()
        if currentState == 'pause':
            self.Pause()
        elif self.playlist is None:
            self.LogError('Jukebox cannot play - no playlist!')
            return 
        if self.playlist.GetLength() <= 0:
            self.LogWarn('Jukebox cannot play - empty playlist.')
            return 
        self.PlayTrack(max(0, min(self.currentTrackIndex, self.playlist.GetLength() - 1)))



    def PlayStinger(self, wiseMessage, debugInfo):
        if self.GetState() != 'play':
            self.LogInfo('Jukebox ignoring stinger track', wiseMessage, '- jukebox is not playing')
            return 
        if not wiseMessage:
            self.LogWarn('Jukebox ignorning stinger track with invalid wiseMessage for', debugInfo)
            return 
        if wiseMessage.startswith('res:/'):
            self.LogError('Jukebox ignoring request to play old stinger:', wiseMessage)
            return 
        self.stingerMessage = wiseMessage
        if self.stingerMessage.startswith('wise:/'):
            self.stingerMessage = self.stingerMessage[6:]
        self.audio.SendJukeboxEvent(u'music_global_stop_for_stinger')
        self.audio.SendJukeboxEvent(self.stingerMessage)
        self.SetState('play')
        self.ReportJukeboxChange('stinger')



    def StopStinger(self):
        if self.stingerMessage is not None:
            self.AdvanceTrack()



    def SetShuffle(self, shuffle):
        self.SetAudioSetting('jukeboxShuffle', shuffle)
        self.shuffleActive = shuffle



    def Pause(self):
        currentState = self.GetState()
        if currentState == 'stop':
            self.LogWarn('Jukebox received pause while stopped. Ignoring this nonsensical command.')
        elif currentState == 'play':
            self.audio.SendJukeboxEvent('music_global_pause')
            self.SetState('pause', persist=True)
            self.currTrackPausedAt = blue.os.TimeAsDouble(blue.os.GetWallclockTime())
        elif currentState == 'pause':
            self.audio.SendJukeboxEvent('music_global_resume')
            if self.currTrackPausedAt is not None:
                self.currTrackStartedAt += blue.os.TimeAsDouble(blue.os.GetWallclockTime()) - self.currTrackPausedAt
                self.currTrackPausedAt = None
            self.SetState('play', persist=True)
        else:
            self.LogWarn('Jukebox received nonsensical pause command, state is', currentState)



    def StopJukebox(self):
        if self.GetState() != 'stop':
            self.currentTrack = None
            self.currentTrackStartedAt = 0
            self.audio.SendJukeboxEvent('music_global_stop')
            self.SetState('stop')



    def AdvanceTrack(self, forward = True, automatic = False):
        playlistlen = self.playlist.GetLength()
        newTrackIndex = -1
        if self.shuffleActive:
            while playlistlen > 1:
                newTrackIndex = random.randint(0, playlistlen - 1)
                if newTrackIndex != self.currentTrackIndex:
                    break

        elif forward:
            if playlistlen > 0:
                newTrackIndex = (self.currentTrackIndex + 1) % playlistlen
        else:
            newTrackIndex = self.currentTrackIndex - 1
            if newTrackIndex < 0:
                newTrackIndex = playlistlen - 1
        if self.GetState() == 'play':
            self.PlayTrack(newTrackIndex, not automatic)
        else:
            self.currentTrack = self.playlist.tracks[newTrackIndex] if newTrackIndex > -1 else None
            self.currentTrackIndex = newTrackIndex
            self.ReportJukeboxChange('track')



    def GetCurrentTrack(self):
        return self.currentTrack



    def GetCurrentTrackElapsedTime(self):
        if self.GetState() == 'pause':
            return int(self.currTrackPausedAt - self.currTrackStartedAt)
        else:
            return int(blue.os.TimeAsDouble(blue.os.GetWallclockTime()) - self.currTrackStartedAt)



    def GetCurrentPlaylist(self):
        return self.playlist



    def GetPlaylist(self, playlistName):
        if playlistName not in self.playlists:
            return []
        if not self.playlists[playlistName].isLoaded:
            self.playlists[playlistName].Load()
        return self.playlists[playlistName]



    def GetTrackIndex(self):
        return self.currentTrackIndex



    def GetVolume(self):
        return self.GetAudioSetting('eveampGain', 0.4)



    def GetState(self):
        return self.jukeboxState



    def GetPlaylists(self):
        return self.playlists



    def HasPlaylist(self, playlistName):
        return playlistName.lower() in [ p.lower() for p in self.playlists ]



    def RemovePlaylist(self, playlistName):
        if self.GetPlaylist(playlistName).isLocked:
            return 
        try:
            del self.playlists[playlistName]
            os.remove(blue.os.ResolvePathForWriting(u'cache:/Jukebox/%s.m3u' % playlistName))

        finally:
            if playlistName == self.playlist.name:
                self.StopJukebox()
                self.SetPlaylist(self.playlists[self.ingamePlayList].name)
            self.ReportJukeboxChange('playlist')




    def AddPlaylist(self, playlistName, playlistPath = None, isLocked = False, isHidden = False, isNew = False):
        if playlistPath is not None:
            self.LogInfo('Adding playlist with name', playlistName, 'located at path', playlistPath)
        else:
            self.LogInfo('Adding playlist with name', playlistName)
        playlist = PlaylistForWise(playlistName, isLocked, isHidden, isNew)
        self.playlists[playlist.name] = playlist
        try:
            if playlistPath is not None:
                self.playlists[playlistName].Load(playlistPath)

        finally:
            self.ReportJukeboxChange('playlist')

        return playlist



    def SetPlaylist(self, newplaylist, persist = True):
        if newplaylist not in self.playlists:
            self.LogWarn('Invalid playlist specified.')
            return 
        if self.playlist is not None and self.playlist == self.playlists[newplaylist]:
            return 
        self.LogInfo('Jukebox loading playlist', newplaylist)
        if self.playlist is not None:
            self.StopJukebox()
            self.messageQueue = []
        if persist:
            self.SetAudioSetting('jukeboxPlaylist', newplaylist)
        self.playlist = self.playlists[newplaylist]
        self.LogInfo('Jukebox initializing with playlist', newplaylist, 'at path', blue.rot.PathToFilename(self.playlist.path))
        try:
            if not self.playlist.isLoaded:
                self.playlist.Load(self.playlist.path)

        finally:
            pass

        if self.playlist.GetLength() == 0:
            self.LogInfo("empty playlist set as current playlist - acting like we'd have none.")
            self.currentTrackIndex = -1
            self.StopJukebox()
            return 
        self.playlist.Sort(self.GetSortAttr(), self.GetSortDirection())



    def Sort(self, sortAttr, reversesort = False, playlistName = None):
        self.SetAudioSetting('jukebox_sortBy', sortAttr)
        self.SetAudioSetting('jukebox_sortOrder', reversesort)
        if playlistName is None or playlistName not in self.playlists:
            self.playlist.Sort(sortAttr, reversesort)
            for (i, track,) in enumerate(self.playlist.tracks):
                if track == self.currentTrack:
                    self.currentTrackIndex = i
                    break

        else:
            self.playlists[playlistName].Sort(sortAttr, reversesort)



    def GetSortAttr(self):
        return self.GetAudioSetting('jukebox_sortBy', 'id')



    def GetSortDirection(self):
        return self.GetAudioSetting('jukebox_sortOrder', False)



    def SetVolume(self, volume = 1.0, persist = True):
        volume = min(max(volume, 0.0), 1.0)
        self.volume = volume
        self.audio.SetMusicVolume(volume, persist)
        self.NotifyObservers(volume)



    def PlayTrack(self, trackindex, forceFade = True, ignoreState = False):
        if self.playlist is None:
            return False
        playlistLength = self.playlist.GetLength()
        if playlistLength <= 0:
            return False
        if trackindex is None:
            trackindex = self.current
        elif trackindex < 0:
            trackindex = 0
        elif trackindex >= playlistLength:
            trackindex = playlistLength - 1
        track = self.playlist.GetTrack(trackindex)
        if track.message is not None:
            if not ignoreState:
                self.SetAudioSetting('jukeboxTrackIndex', trackindex)
            self.currentTrackIndex = trackindex
            self.messageQueue.append(track.message)
            self.stingerMessage = None
            if forceFade:
                self.audio.SendJukeboxEvent('music_global_stop')
            if track.message[track.message.rfind('.'):].lower() == '.mp3':
                self.audio.PlayJukeboxTrack(track.message)
            else:
                self.audio.SendJukeboxEvent(track.message)
            self.ReportJukeboxChange('track')
            self.SetState('play', persist=not ignoreState)
            self.currTrackStartedAt = blue.os.TimeAsDouble(blue.os.GetWallclockTime())
            self.currTrackPausedAt = None
            self.currentTrack = self.playlist.tracks[self.currentTrackIndex]
            return True
        self.LogWarn('JUKEBOX HALTING - Invalid track', track.title, 'at position', trackindex, 'in playlist', self.playlist.GetList())
        return False



    def ReportJukeboxChange(self, changeType):
        sm.ScatterEvent('OnJukeboxChange', changeType)



    def SetState(self, newState, persist = False):
        if newState not in ('play', 'pause', 'stop'):
            raise RuntimeError('Invalid jukebox state!')
        if newState is self.jukeboxState:
            return 
        self.jukeboxState = newState
        if persist:
            self.SetAudioSetting('ampState', newState)
        self.ReportJukeboxChange(newState)




class PlaylistForWise():
    __guid__ = 'util.PlaylistForWise'

    def __init__(self, playlistname, isLocked = False, isHidden = False, isNew = False):
        self.tracks = []
        self.isLocked = isLocked
        self.isHidden = isHidden
        self.path = ''
        self.relBasePath = u'c:/ '
        self.seedID = 0
        self.isLoaded = False
        if isNew:
            self.SaveAsM3U(newFile=True)
            self.SetDisplayName(playlistname)
        else:
            self.name = playlistname
        self.displayName = self.GetDisplayName()



    def Load(self, resPath = None):
        if resPath is None:
            resPath = self.path
        if len(resPath) == 0:
            return 
        resPath = resPath.lower()
        trackList = []
        loader = self._PlaylistForWise__DecideLoadingStrategy(resPath)
        trackList = loader(resPath)
        for track in trackList:
            self.AddTrack(track['message'], track['title'], int(track['duration']))

        self.path = resPath
        self.isLoaded = True



    def GetDisplayName(self):
        playlistNameMap = settings.user.ui.Get('JukeboxPlaylistNameMap', {})
        return playlistNameMap.get(self.name, self.name)



    def SetDisplayName(self, newName):
        playlistNameMap = settings.user.ui.Get('JukeboxPlaylistNameMap', {})
        playlistNameMap[self.name] = newName
        settings.user.ui.Set('JukeboxPlaylistNameMap', playlistNameMap)



    def GetList(self):
        return self.tracks[:]



    def AddTrack(self, trackMessageName, trackTitle, trackDuration):
        if (trackMessageName, trackTitle) not in self.tracks:
            item = util.KeyVal()
            item.message = trackMessageName.lower()
            item.title = trackTitle
            item.duration = int(trackDuration)
            item.id = self.seedID
            self.seedID += 1
            self.tracks.append(item)



    def RemoveTrack(self, id):
        for (i, track,) in enumerate(self.tracks):
            if track.id == id:
                self.tracks.pop(i)
                return True

        return False



    def Clear(self):
        self.tracks = []
        self.path = ''
        self.isLoaded = False



    def GetLength(self):
        return len(self.tracks)



    def GetTrack(self, idx):
        if idx < 0 or idx >= len(self.tracks):
            raise RuntimeError('Cannot retrieve track', idx, 'from playlist - invalid index')
        return self.tracks[idx]



    def FindTrack(self, trackMessageName):
        idx = 0
        for track in self.tracks:
            if track.message == trackMessageName:
                return idx
            idx += 1

        return -1



    def SwapTracks(self, idx1, idx2):
        playlistLength = len(self.tracks)
        if idx1 < 0 or idx2 < 0 or idx1 >= playlistLength or idx2 >= playlistLength:
            raise RuntimeError('Cannot swap tracks', idx1, 'and', idx2, ' - invalid index passed in')
        if idx1 == idx2:
            return 
        tmp = self.tracks[idx1]
        self.tracks[idx1] = self.tracks[idx2]
        self.tracks[idx2] = tmp



    def Shuffle(self):
        trackList = self.GetList()
        self.tracks = []
        while len(trackList) > 0:
            returnTrackIdx = int(random.randint(0, len(trackList) - 1))
            self.tracks.append(trackList[returnTrackIdx])
            del trackList[returnTrackIdx]




    def Sort(self, attribute = 'id', reverse = False):
        if attribute == 'title':

            def SortTitle(a, b):
                return cmp(sm.GetService('jukebox').TranslateTitle(a.title), sm.GetService('jukebox').TranslateTitle(b.title))


            self.tracks.sort(SortTitle, reverse=reverse)
        else:
            self.tracks.sort(lambda a, b: cmp(getattr(a, attribute), getattr(b, attribute)), reverse=reverse)



    def GetPath(self):
        return self.path



    def __DecideLoadingStrategy(self, resPath):
        tmpPath = os.path.normpath(resPath)
        strategy = None
        if not hasattr(self, 'strategies'):
            self.strategies = {'.pink': self._PlaylistForWise__LoadPinkFilePlaylist,
             '.m3u': self._PlaylistForWise__LoadM3uPlaylist,
             '.ram': self._PlaylistForWise__LoadRamPlaylist,
             '.pls': self._PlaylistForWise__LoadPlsPlaylist,
             '.mp3': self._PlaylistForWise__LoadMP3s,
             'path': self._PlaylistForWise__LoadPathAsPlaylist}
        suffix = tmpPath[tmpPath.rfind('.'):]
        if os.path.isdir(tmpPath):
            suffix = 'path'
        url = False
        if resPath.find('://') > -1:
            url = True
        invalidStrategy = suffix not in self.strategies.keys()
        if invalidStrategy or url:
            raise UserError('JukeboxUnsupportedFileFormat')
        return self.strategies[suffix]



    def __GetFile(self, path):
        file = []
        resFile = None
        if path.startswith('res:/'):
            self.relBasePath = blue.os.ResolvePath(u'res:/audio/jukebox/')
            resFile = blue.os.CreateInstance('blue.ResFile')
            if resFile is None or not resFile.Open(path):
                raise UserError('JukeboxUnsupportedFileFormat')
            file = resFile.Read().split('\r\n')
        else:
            try:
                self.relBasePath = os.path.dirname(path)
                file = open(path, 'r')
            except IOError:
                raise UserError('JukeboxUnsupportedFileFormat')
        return file



    def __NormalizePath(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.relBasePath, path)
        path = os.path.normpath(path)
        path = path.strip('\r')
        path = path.strip('\n')
        return path



    def __LoadPathAsPlaylist(self, path):
        trackList = []
        for (root, folders, files,) in os.walk(unicode(path)):
            for folder in folders:
                l = self._PlaylistForWise__LoadPathAsPlaylist(os.path.join(path, folder))
                for i in l:
                    if i:
                        trackList.append(i)


            for name in files:
                if name[name.rfind('.'):].lower() == '.mp3':
                    trackInfo = self._PlaylistForWise__GetTrackInformation(os.path.join(path, name))
                    if trackInfo:
                        trackList.append(trackInfo)


        return trackList



    def __LoadMP3s(self, path):
        trackList = []
        trackInfo = self._PlaylistForWise__GetTrackInformation(path)
        if trackInfo:
            trackList.append(trackInfo)
        return trackList



    def __LoadPinkFilePlaylist(self, path):
        pinkFile = blue.os.CreateInstance('blue.ResFile')
        if pinkFile is None or not pinkFile.Open(path):
            raise UserError('JukeboxUnsupportedFileFormat')
        pinkText = pinkFile.Read()
        return yaml.load(pinkText)



    def __LoadPlsPlaylist(self, path):
        trackList = []
        file = self._PlaylistForWise__GetFile(path)
        for line in file:
            if line.startswith('File'):
                line = self._PlaylistForWise__NormalizePath(line[(line.find('=') + 1):])
                if line[line.rfind('.'):].lower() == '.mp3':
                    trackInfo = None
                    trackInfo = self._PlaylistForWise__GetTrackInformation(line)
                    if trackInfo:
                        trackList.append(trackInfo)

        if file.__class__ == 'file':
            file.close()
        return trackList



    def __LoadRamPlaylist(self, path):
        trackList = []
        file = self._PlaylistForWise__GetFile(path)
        for line in file:
            if line.startswith('file://'):
                line = self._PlaylistForWise__NormalizePath(line[7:])
                if line[line.rfind('.'):].lower() == '.mp3':
                    trackInfo = self._PlaylistForWise__GetTrackInformation(line)
                    if trackInfo:
                        trackList.append(trackInfo)

        if file.__class__ == 'file':
            file.close()
        return trackList



    def __LoadM3uPlaylist(self, path):
        file = self._PlaylistForWise__GetFile(path)
        trackList = []
        trackInfo = None
        for line in file:
            line = line.decode('utf-8')
            if line.startswith('#EXTM3U'):
                continue
            if line.startswith('#EXTINF:'):
                trackInfo = line[8:].split(',')[:2]
                (duration, title,) = trackInfo
                if 'mls://' in title:
                    title = title[title.find('mls://'):].strip()
                    trackInfo = (duration, title)
                continue
            line = self._PlaylistForWise__NormalizePath(line)
            if line[line.rfind('.'):].lower() == '.mp3' and line.find('://') == -1:
                (duration, title,) = trackInfo
                trackList.append({'message': line,
                 'title': title,
                 'duration': duration})
                trackInfo = None

        if file.__class__ == 'file':
            file.close()
        return trackList



    def __GetTrackInformation(self, mp3file):
        blue.pyos.BeNice()
        player = sm.GetService('audio').jukeboxPlayer
        if player is None:
            return 
        info = player.GetTrackInfo(unicode(mp3file))
        if info is not None:
            if info.Title and info.Artist:
                title = u'%s - %s' % (info.Artist, info.Title)
            elif info.Title:
                title = info.Title
            elif info.Artist:
                title = info.Artist
            else:
                title = mp3file
            duration = info.Duration / 1000
            return {'message': mp3file,
             'title': title,
             'duration': duration}



    def SaveAsM3U(self, newFile = False):
        if self.isLocked:
            return 
        if self.path.startswith('res:/'):
            return 
        if newFile:
            i = 0
            while 1:
                saveFilePath = '%s//Playlist%s.m3u' % (os.path.normpath(os.path.join(blue.os.ResolvePath(u'cache:/Jukebox'))), i)
                if not os.path.exists(saveFilePath):
                    self.name = 'Playlist%s' % i
                    break
                i += 1

        else:
            saveFilePath = '%s//%s.m3u' % (os.path.normpath(os.path.join(blue.os.ResolvePath(u'cache:/Jukebox'))), self.name)
        f = open(unicode(saveFilePath), 'w')
        try:
            f.write('#EXTM3U\n')
            for track in self.tracks:
                f.write('#EXTINF:%d,%s\n' % (track.duration, track.title.encode('utf-8')))
                f.write(track.message.encode('utf-8') + '\n')


        finally:
            f.close()





