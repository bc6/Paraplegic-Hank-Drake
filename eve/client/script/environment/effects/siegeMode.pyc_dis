#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/effects/siegeMode.py
import effects
import blue

class SiegeMode(effects.GenericEffect):
    __guid__ = 'effects.SiegeMode'

    def Stop(self):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        if getattr(shipBall, 'model', None) is not None:
            self.ReverseModelTimeCurvesAndPlay(shipBall.model)
            if hasattr(shipBall.model, 'ChainAnimationEx'):
                shipBall.model.ChainAnimation('EndSiege')
                shipBall.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)

    def Prepare(self):
        pass

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        if getattr(shipBall, 'model', None) is not None:
            self.ReverseModelTimeCurvesAndPlay(shipBall.model)
            if hasattr(shipBall.model, 'ChainAnimationEx'):
                shipBall.model.ChainAnimation('StartSiege')
                shipBall.model.ChainAnimationEx('SiegeLoop', 0, 0, 1.0)

    def Repeat(self, duration):
        pass

    def ReverseModelTimeCurvesAndPlay(self, tf):
        self.fxSequencer.LogInfo('SiegeMode.ReverseModelTimeCurvesAndPlay')
        curveTypes = ['trinity.TriScalarCurve',
         'trinity.TriVectorCurve',
         'trinity.TriRotationCurve',
         'trinity.TriColorCurve']
        allCurves = tf.Find(curveTypes)
        curves = []
        for x in allCurves:
            if x.name == 'siegeCurve':
                curves.append(x)

        soundNodes = tf.Find(['audio.Node', 'audio.SoundNode'])
        done = {}
        for curve in curves:
            length = curve.length
            if length > 0.0:
                if curve in done:
                    continue
                curve.Sort()
                curve.ScaleTime(-1.0)
                for key in curve.keys:
                    key.time = key.time + length

                curve.Sort()
                done[curve] = 1

        now = blue.os.GetSimTime()
        for soundNode in soundNodes:
            if soundNode.name.startswith('Siege'):
                soundNode.Play()

        for curve in done:
            curve.start = now