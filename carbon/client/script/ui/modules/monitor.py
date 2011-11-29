import blue
import uthread
import uicls
import uiutil
import uiconst
import base
import trinity
import log
import util
KB = 1024
import math

def niceNum(num, precision):
    accpow = math.floor(math.log10(precision))
    if num < 0:
        digits = int(math.fabs(num / pow(10, accpow) - 0.5))
    else:
        digits = int(math.fabs(num / pow(10, accpow) + 0.5))
    result = ''
    if digits > 0:
        for i in range(0, int(accpow)):
            if i % 3 == 0 and i > 0:
                result = '0,' + result
            else:
                result = '0' + result

        curpow = int(accpow)
        while digits > 0:
            adigit = chr(digits % 10 + ord('0'))
            if curpow % 3 == 0 and curpow != 0 and len(result) > 0:
                if curpow < 0:
                    result = adigit + ' ' + result
                else:
                    result = adigit + ',' + result
            elif curpow == 0 and len(result) > 0:
                result = adigit + '.' + result
            else:
                result = adigit + result
            digits = digits / 10
            curpow = curpow + 1

        for i in range(curpow, 0):
            if i % 3 == 0 and i != 0:
                result = '0 ' + result
            else:
                result = '0' + result

        if curpow <= 0:
            result = '0.' + result
        if num < 0:
            result = '-' + result
    else:
        result = '0'
    return result



def FormatMemory(val):
    if val < KB:
        label = 'B'
    elif val > KB and val < KB ** 2:
        label = 'KB'
        val = val / KB
    elif val > KB ** 2 and val < KB ** 3:
        label = 'MB'
        val = val / KB ** 2
    elif val > KB ** 3:
        label = 'GB'
        val = val / KB ** 3
    return str(round(val, 2)) + label



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
            blue.synchro.SleepWallclock(500)




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




class GraphsWindow(uicls.Window):
    __guid__ = 'form.GraphsWindow'
    default_caption = 'Blue stats graphs'
    default_minSize = (600, 500)

    def ApplyAttributes(self, attributes):
        self._ready = False
        uicls.Window.ApplyAttributes(self, attributes)
        self.graphs = trinity.GraphManager()
        self.graphs.SetEnabled(True)
        if hasattr(self, 'SetTopparentHeight'):
            self.SetTopparentHeight(0)
            self.container = uicls.Container(parent=self.sr.main, align=uiconst.TOALL)
        else:
            self.container = uicls.Container(parent=self.sr.content, align=uiconst.TOALL)
        self.settingsContainer = uicls.Container(parent=self.container, align=uiconst.TOTOP, height=30)
        self.showTimersChk = uicls.Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Timers', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showMemoryChk = uicls.Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Memory counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showLowCountersChk = uicls.Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Low counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showHighCountersChk = uicls.Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='High counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.resetBtn = uicls.Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Reset peaks', width=120, height=30, func=self.PopulateScroll)
        self.refreshBtn = uicls.Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Refresh', width=120, height=30, func=self.PopulateScroll)
        self.scroll = uicls.Scroll(parent=self.container, id='blueGraphsScroll', align=uiconst.TOTOP, height=200)
        self.graphsContainer = uicls.Container(parent=self.container, align=uiconst.TOALL)
        self._ready = True
        self.PopulateScroll()



    def Close(self, *args, **kwargs):
        self.graphs.SetEnabled(False)
        uicls.Window.Close(self, *args, **kwargs)



    def DelayedRefresh_thread(self):
        blue.synchro.SleepWallclock(600)
        self.PopulateScroll()



    def DelayedRefresh(self):
        uthread.new(self.DelayedRefresh_thread)



    def ResetPeaks(self, *args):
        blue.CcpStatistics().ResetPeaks()
        self.DelayedRefresh()



    def PopulateScroll(self, *args):
        typesIncluded = []
        if self.showTimersChk.GetValue():
            typesIncluded.append('time')
        if self.showMemoryChk.GetValue():
            typesIncluded.append('memory')
        if self.showLowCountersChk.GetValue():
            typesIncluded.append('counterLow')
        if self.showHighCountersChk.GetValue():
            typesIncluded.append('counterHigh')
        statsObject = blue.CcpStatistics()
        stats = statsObject.GetValues()
        desc = statsObject.GetDescriptions()
        contentList = []
        for (key, value,) in desc.iteritems():
            type = value[1]
            if type in typesIncluded:
                peak = stats[key][1]
                if type == 'memory':
                    label = '%s<t>%s<t>%s' % (key, FormatMemory(peak), value[0])
                elif type.startswith('counter'):
                    label = '%s<t>%s<t>%s' % (key, niceNum(peak, 1), value[0])
                elif type == 'time':
                    label = '%s<t>%s<t>%s' % (key, niceNum(peak, 1e-10), value[0])
                listEntry = uicls.ScrollEntryNode(decoClass=uicls.SE_Generic, id=id, name=key, peak=peak, desc=value[0], label=label, GetMenu=self.GetListEntryMenu, OnDblClick=self.OnListEntryDoubleClicked)
                contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['Name', 'Peak', 'Description'], noContentHint='No Data available')



    def GetListEntryMenu(self, listEntry):
        return (('Right-click action 1', None), ('Right-click action 2', None))



    def OnListEntryDoubleClicked(self, listEntry):
        node = listEntry.sr.node
        if self.graphs.HasGraph(node.name):
            self.graphs.RemoveGraph(node.name)
        else:
            self.graphs.AddGraph(node.name)



    def _OnResize(self):
        if self._ready:
            (l, t, w, h,) = self.graphsContainer.GetAbsolute()
            scaledAbs = (uicore.ScaleDpi(l),
             uicore.ScaleDpi(t),
             uicore.ScaleDpi(w),
             uicore.ScaleDpi(h))
            self.graphs.AdjustViewports(scaledAbs)




