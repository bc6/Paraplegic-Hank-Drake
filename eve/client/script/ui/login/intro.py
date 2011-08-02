import uthread
import base
import blue
import uicls
import uiconst

class Intro(uicls.LayerCore):
    __guid__ = 'form.Intro'
    __notifyevents__ = ['OnSetDevice']

    def OnSetDevice(self):
        print 'Realign'



    def OnCloseView(self):
        print '----------------------In OnCloseView-----------------------'
        self.movie = None
        sm.StartService('jukebox').Pause()
        sm.GetService('ui').ForceCursorUpdate()



    def OnOpenView(self):
        if not sm.GetService('connection').IsConnected():
            return 
        self.opened = 0
        self.movie = None
        self.sr.movieCont = None
        self.sr.subtitleCont = None
        self.subtitles = None
        self.fadeTime = 500
        self.InitMovie()
        self.InitSubtitles()
        sm.StartService('jukebox').Pause()
        self.PlayMovie()
        self.opened = 1
        sm.RegisterNotify(self)



    def InitMovie(self):
        self.sr.movieCont = uicls.Container(parent=self, name='movieCont', idx=0, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        moviePath = 'res/video/Intro_1280_720.bik'
        (x, y, contWidth, contHeight,) = self.sr.movieCont.GetAbsolute()
        (dimWidth, dimHeight,) = self.GetVideoDimensions(contWidth, contHeight, 1280, 720)
        self.movie = uicls.VideoSprite(parent=self.sr.movieCont, pos=(0,
         0,
         dimWidth,
         dimHeight), align=uiconst.CENTER, videoPath=moviePath, videoAutoPlay=False)



    def PlayMovie(self):
        self.movie.Play()
        uthread.new(self.WatchMovie)



    def InitSubtitles(self):
        (x, y, contWidth, contHeight,) = self.sr.movieCont.GetAbsolute()
        subsHeight = int(float(contHeight) * 0.1)
        self.sr.subtitleCont = uicls.Container(parent=self.sr.movieCont, name='subtitleCont', idx=0, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, height=subsHeight)
        self.sr.subtitleCont.Flush()
        self.subtitles = []
        self.subtitles.append((mls.G_INTRO_01,
         0,
         10700,
         15000))
        self.subtitles.append((mls.G_INTRO_02_A,
         0,
         17300,
         23200))
        self.subtitles.append((mls.G_INTRO_02_B,
         20,
         19200,
         23200))
        self.subtitles.append((mls.G_INTRO_03_A,
         0,
         24600,
         30600))
        self.subtitles.append((mls.G_INTRO_03_B,
         20,
         26000,
         30600))
        self.subtitles.append((mls.G_INTRO_04_A,
         0,
         32000,
         41200))
        self.subtitles.append((mls.G_INTRO_04_B,
         20,
         36000,
         41200))
        self.subtitles.append((mls.G_INTRO_05,
         0,
         43400,
         47400))
        self.subtitles.append((mls.G_INTRO_06,
         0,
         47600,
         52000))
        self.subtitles.append((mls.G_INTRO_07_A,
         0,
         52500,
         60000))
        self.subtitles.append((mls.G_INTRO_07_B,
         20,
         57000,
         60000))
        self.subtitles.append((mls.G_INTRO_08,
         0,
         62000,
         66000))
        self.subtitles.append((mls.G_INTRO_09_A,
         0,
         67000,
         72600))
        self.subtitles.append((mls.G_INTRO_09_B,
         20,
         68800,
         72600))
        self.subtitles.append((mls.G_INTRO_10_A,
         0,
         73000,
         80000))
        self.subtitles.append((mls.G_INTRO_10_B,
         20,
         75000,
         80000))
        self.subtitles.append((mls.G_INTRO_11_A,
         0,
         80800,
         88000))
        self.subtitles.append((mls.G_INTRO_11_B,
         20,
         83200,
         88000))
        self.subtitles.append((mls.G_INTRO_12_A,
         0,
         90000,
         96000))
        self.subtitles.append((mls.G_INTRO_12_B,
         20,
         92000,
         96000))
        self.subtitles.append((mls.G_INTRO_13,
         0,
         97000,
         101600))
        self.subtitles.append((mls.G_INTRO_14,
         0,
         102600,
         105200))
        self.subtitles.append((mls.G_INTRO_15,
         0,
         106000,
         110000))



    def UpdateSubtitles(self):
        (x, y, contWidth, contHeight,) = self.sr.movieCont.GetAbsolute()
        subsWidth = int(float(contWidth) * 0.6)
        currentTime = self.GetCurrentMovieTime()
        self.sr.subtitleCont.Flush()
        for subtitle in self.subtitles:
            if currentTime >= subtitle[2] and currentTime <= subtitle[3]:
                framesFromEnd = min(currentTime - subtitle[2], subtitle[3] - currentTime)
                alpha = min(1.0, float(framesFromEnd) / self.fadeTime)
                uicls.Label(text=subtitle[0], parent=self.sr.subtitleCont, fontsize=16, color=(1.0,
                 1.0,
                 1.0,
                 alpha), top=subtitle[1], align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)




    def GetCurrentMovieTime(self):
        currentFrame = self.movie.currentFrame
        fps = self.movie.videoFps
        if not fps:
            return 0
        return int(float(currentFrame) / float(fps) * 1000.0)



    def WatchMovie(self):
        while not self.destroyed:
            if getattr(self, 'movie', None):
                if self.movie.isFinished:
                    self.StopIntro()
                    return 
                self.UpdateSubtitles()
            else:
                return 
            blue.pyos.synchro.Sleep(20)




    def GetVideoDimensions(self, contWidth, contHeight, vidResWidth, vidResHeight):
        dimWidth = vidResWidth
        dimHeight = vidResHeight
        contFactor = float(contWidth) / float(contHeight)
        vidResFactor = float(vidResWidth) / float(vidResHeight)
        if vidResFactor > contFactor:
            widthFactor = float(contWidth) / float(vidResWidth)
            dimWidth *= widthFactor
            dimHeight *= widthFactor
        elif vidResFactor < contFactor:
            heightFactor = float(contHeight) / float(vidResHeight)
            dimWidth *= heightFactor
            dimHeight *= heightFactor
        else:
            dimWidth = contWidth
            dimHeight = contHeight
        return (int(dimWidth), int(dimHeight))



    def StopIntro(self):
        settings.public.generic.Set('showintro2', 0)
        uthread.pool('GameUI :: GoCharacterSelection', sm.GetService('gameui').GoCharacterSelection)



    def OnEsc(self):
        self.StopIntro()




