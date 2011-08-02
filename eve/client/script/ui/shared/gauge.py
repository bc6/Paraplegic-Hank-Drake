import uix
import xtriui
import blue
import uicls
YELLOWY = 0.5625
YELLOWMIN = 0.497
YELLOWMAX = 0.206
YELLOWRANGE = YELLOWMAX - YELLOWMIN

class Gauge(uicls.Container):
    __guid__ = 'xtriui.Gauge'
    __nonpersistvars__ = ['gaugemin', 'gaugerange']

    def init(self):
        self.SetType('yellow')



    def SetType(self, gaugetype):
        if gaugetype == 'yellow':
            self.control.model.areas[0].areaTextures[2].scaling.x = 0.3
            self.control.model.areas[0].areaTextures[2].translation.y = YELLOWY
            self.gaugemin = YELLOWMIN
            self.gaugerange = YELLOWRANGE
        else:
            raise RuntimeError('Unknown gauge type!', gaugetype)



    def SetProportion(self, proportion):
        self.control.model.areas[0].areaTextures[2].translation.x = self.gaugemin + self.gaugerange * proportion




