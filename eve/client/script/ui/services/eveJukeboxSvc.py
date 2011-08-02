import svc
import uix
import os

class EveJukeboxSvc(svc.jukebox):
    __guid__ = 'svc.eveJukebox'
    __replaceservice__ = 'jukebox'
    __exportedcalls__ = {}

    def __init__(self):
        svc.jukebox.__init__(self)
        self.ingamePlayList = 'mls://UI_SHARED_JUKEBOX_PLAYLIST_DEFAULT'
        if not self.HasPlaylist(self.ingamePlayList):
            self.AddPlaylist(self.ingamePlayList, 'res:/audio/Jukebox/inflight.m3u', isLocked=True)



    def ResetPlaylist(self):
        self.SetPlaylist(self.ingamePlayList)



    def TranslateTitle(self, title):
        pos = title.rfind('mls://')
        if pos > -1:
            mlskey = title[(pos + 6):]
        else:
            return title.lstrip()
        if mls.HasLabel(mlskey):
            return getattr(mls, mlskey)
        else:
            return title.lstrip()




