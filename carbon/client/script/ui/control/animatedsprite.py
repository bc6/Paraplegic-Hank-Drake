import uicls
import uiconst
import blue
import uthread

class AnimSpriteCore(uicls.IconCore):
    __guid__ = 'uicls.AnimSpriteCore'
    default_icons = [ 'ui_1_16_%s' % (82 + i) for i in xrange(8) ]

    def ApplyAttributes(self, attributes):
        self.icons = attributes.get('icons', self.default_icons)
        attributes.icon = self.icons[0]
        uicls.IconCore.ApplyAttributes(self, attributes)
        self.steps = len(self.icons)
        self.step = 0
        self.play = 0
        self.playing = 0



    def Loop(self):
        while not self.destroyed:
            self.playing = 1
            self.state = uiconst.UI_NORMAL
            if self.step >= self.steps:
                self.step = 0
            self.LoadIcon(self.icons[self.step], ignoreSize=True)
            blue.pyos.synchro.SleepWallclock(125)
            if self.destroyed:
                return 
            if not self.play and self.step == 0:
                self.state = uiconst.UI_HIDDEN
                break
            self.step += 1

        if not self.destroyed:
            self.playing = 0



    def Stop(self):
        self.play = 0
        self.step = 0



    def Play(self):
        self.play = 1
        if not self.playing:
            self.playing = 1
            uthread.new(self.Loop)




