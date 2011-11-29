import svc

class EveJukeboxSvc(svc.jukebox):
    __guid__ = 'svc.eveJukebox'
    __replaceservice__ = 'jukebox'
    __exportedcalls__ = {}

    def __init__(self):
        svc.jukebox.__init__(self)
        self.ingamePlayList = 'mls://UI/Jukebox/EveDefaultPlaylist'
        if not self.HasPlaylist(self.ingamePlayList):
            self.AddPlaylist(self.ingamePlayList, 'res:/audio/Jukebox/inflight.m3u', isLocked=True)



    def ResetPlaylist(self):
        self.SetPlaylist(self.ingamePlayList)




