import blue
import uthread
import uicls
import uiutil
import uiconst
import base
import trinity
import log

class GraphRenderer(uicls.Base):
    __guid__ = 'uicls.GraphRenderer'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def ApplyAttributes(self, attributes):
        uicls.Base.ApplyAttributes(self, attributes)
        self.viewport = trinity.TriViewport()
        self.linegraph = trinity.Tr2LineGraph()
        self.linegraphSize = 0
        self.linegraph.name = 'FPS'
        self.linegraph.color = (0.9, 0.9, 0.9, 1)
        trinity.statistics.SetAccumulator(self.linegraph.name, self.linegraph)
        self.renderJob = trinity.CreateRenderJob('Graphs')
        self.renderObject.renderJob = self.renderJob
        self.renderJob.PythonCB(self.AdjustViewport)
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetStdRndStates(trinity.RM_SPRITE2D)
        self.renderer = self.renderJob.RenderLineGraph()
        self.renderer.showLegend = False
        self.renderer.lineGraphs.append(self.linegraph)



    def Close(self):
        uicls.Base.Close(self)
        self.renderer.scaleChangeCallback = None



    def AdjustViewport(self):
        (l, t,) = (self.displayX, self.displayY)
        parent = self.GetParent()
        while parent:
            l += parent.displayX
            t += parent.displayY
            parent = parent.GetParent()

        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = self._displayWidth
        self.viewport.height = self._displayHeight
        if self.linegraphSize != self._displayWidth:
            self.linegraph.SetSize(self._displayWidth)
            self.linegraphSize = self._displayWidth




class FpsMonitor(uicls.Window):
    __guid__ = 'uicls.FpsMonitor'
    default_caption = 'FPS Monitor'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(4)
        self.fpsLabel = uicls.Label(parent=self.sr.main, left=4, width=80, fontsize=18)
        self.fpsStat = blue.statistics.Find('FPS')
        self.legendContainer = uicls.GridContainer(parent=self.sr.main, align=uiconst.TORIGHT, width=28, columns=1, padRight=4, padBottom=4)
        self.exportBtn = uicls.Button(parent=self.sr.main, align=uiconst.TOPRIGHT, label='Export to clipboard', left=36, func=self.Export)
        self.labels = []
        for i in xrange(4):
            label = uicls.Label(parent=self.legendContainer, align=uiconst.TOTOP, width=20, top=-4)
            self.labels.append(label)

        graphContainer = uicls.Container(parent=self.sr.main, align=uiconst.TOALL, padLeft=4, padRight=4, padBottom=4)
        gr = uicls.GraphRenderer(parent=graphContainer, align=uiconst.TOALL)
        self.renderer = gr.renderer
        self.renderer.scaleChangeCallback = self.ScaleChangeHandler
        if self.fpsStat:
            uthread.new(self.UpdateFpsLabel)



    def ScaleChangeHandler(self):
        numLabels = len(self.labels)
        label = 1.0
        labelStep = 1.0 / float(numLabels)
        for i in xrange(numLabels):
            labelValue = int(label / self.renderer.scale * self.renderer.legendScale + 0.5)
            self.labels[i].SetText(str(labelValue))
            label -= labelStep




    def UpdateFpsLabel(self):
        while not self.destroyed:
            self.fpsLabel.text = '%6.2f' % self.fpsStat.value
            blue.synchro.Sleep(500)




    def Export(self, *args):
        accumulator = blue.statistics.GetAccumulator('FPS')
        fpsData = accumulator.GetStatsHistory()
        txt = ''
        for value in fpsData:
            txt += '%6.2f\n' % value

        isW = sm.StartService('device').GetSettings().Windowed
        r = sm.GetService('device').GetPreferedResolution(isW)
        header = 'Resolution: %sx%s - Windowed: %s - Audio: %s\nDrones: %s - Explosions: %s - Turrets: %s - Effects: %s - Missiles: %s - Shader: %s - Textures: %s - HDR: %s - Bloom: %s' % (r[0],
         r[1],
         isW,
         settings.public.audio.Get('audioEnabled', 1),
         settings.user.ui.Get('droneModelsEnabled', 1),
         settings.user.ui.Get('explosionEffectsEnabled', 1),
         settings.user.ui.Get('turretsEnabled', 1),
         settings.user.ui.Get('effectsEnabled', 1),
         settings.user.ui.Get('missilesEnabled', 1),
         prefs.GetValue('shaderQuality', 3),
         prefs.GetValue('textureQuality', 0),
         prefs.GetValue('hdrEnabled', 0),
         prefs.GetValue('bloomEnabled', 0))
        txt = header + '\n' + txt
        print txt
        blue.pyos.SetClipboardData(txt)




