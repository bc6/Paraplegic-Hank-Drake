import uthread
import blue
import uicls
import uiconst
import localization

class Intro(uicls.LayerCore):
    __guid__ = 'form.Intro'

    def OnCloseView(self):
        sm.GetService('viewState').LogInfo('intro.OnCloseView')
        self.movie.Pause()
        self.movie = None
        sm.GetService('jukebox').Pause()
        sm.GetService('ui').ForceCursorUpdate()
        self.Flush()



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



    def InitMovie(self):
        self.sr.movieCont = uicls.Container(parent=self, name='movieCont', idx=0, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        moviePath = 'res:/video/Intro_1280_720.bik'
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
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part0'),
         0,
         10700,
         15000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part1'),
         0,
         17300,
         23200))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part2'),
         20,
         19200,
         23200))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part3'),
         0,
         24600,
         30600))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part4'),
         20,
         26000,
         30600))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part5'),
         0,
         32000,
         41200))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part6'),
         20,
         36000,
         41200))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part7'),
         0,
         43400,
         47400))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part8'),
         0,
         47600,
         52000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part9'),
         0,
         52500,
         60000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part10'),
         20,
         57000,
         60000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part11'),
         0,
         62000,
         66000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part12'),
         0,
         67000,
         72600))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part13'),
         20,
         68800,
         72600))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part14'),
         0,
         73000,
         80000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part15'),
         20,
         75000,
         80000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part16'),
         0,
         80800,
         88000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part17'),
         20,
         83200,
         88000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part18'),
         0,
         90000,
         96000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part19'),
         20,
         92000,
         96000))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part20'),
         0,
         97000,
         101600))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part21'),
         0,
         102600,
         105200))
        self.subtitles.append((localization.GetByLabel('UI/Login/IntroMovie/Subtitles/Part22'),
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
            blue.pyos.synchro.SleepWallclock(20)




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
        if sm.GetService('cc').GetCharactersToSelect():
            uthread.pool('viewState::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')
        else:
            uthread.pool('viewState::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charactercreation')



    def OnEsc(self):
        sm.GetService('viewState').LogInfo('OnEsc called')
        self.StopIntro()




