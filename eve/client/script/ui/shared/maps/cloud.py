import util
import trinity
import xtriui
import uiutil
import bluepy

class LabelTracker(bluepy.WrapBlueClass('trinity.TriTransform')):
    __guid__ = 'xtriui.LabelTracker'
    __persistvars__ = ['sr']

    def __init__(self):
        self.sr = uiutil.Bunch()
        self.wr = util.WeakRefAttrObject()



    def Initialize(self, name, itemID):
        self.sr.itemID = itemID



    def SetTranslation(self, x = 0.0, y = 0.0, z = 0.0, factor = None):
        self.translation.SetXYZ(x, y, z)
        if factor:
            self.translation.Scale(factor)




