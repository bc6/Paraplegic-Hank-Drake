import uiconst
import uiutil
import uicls
import blue
import trinity
import uiconst
import uiutil
import uicls
import blue
import trinity

class LayerManager(object):
    __guid__ = 'uicls.LayerManager'

    def __getattr__(self, k):
        return self.GetLayer(k)



    def GetLayer(self, name):
        for layer in uicore.desktop.children:
            if hasattr(layer, 'GetLayer'):
                found = layer.GetLayer(name.lower())
                if found:
                    return found



    Get = GetLayer


class LayerCore(uicls.Container):
    __guid__ = 'uicls.LayerCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.isopen = 0
        self.isopening = 0
        self.sceneName = ''
        self.decoClass = None
        self.form = self
        self.uiwindow = self



    def GetLayer(self, name):
        if name.lower() == self.name[2:].lower():
            return self
        if name.lower() == self.name.lower():
            return self
        for layer in self.children:
            if hasattr(layer, 'GetLayer'):
                found = layer.GetLayer(name)
                if found:
                    return found




    def OpenView(self):
        if self.isopen or self.decoClass is None:
            return 
        if self.isopening:
            return 
        self.isopening = 1
        self.state = uiconst.UI_PICKCHILDREN
        self.OnOpenView()
        self.isopen = 1
        self.isopening = 0



    def OnOpenView(self, *args):
        pass



    def OnCloseView(self, *args):
        pass



    def CloseView(self, *args):
        if not self.isopen:
            return 
        for l in self.children[:]:
            if hasattr(l, 'CloseView'):
                l.CloseView()
            else:
                l.Close()

        wasopen = self.isopen
        self.isopen = 0
        if wasopen:
            self.OnCloseView()
        notifyevents = getattr(self, '__notifyevents__', None)
        if notifyevents:
            sm.UnregisterNotify(self)
        parent = None
        name = None
        if self.parent:
            parent = self.parent
            name = self.name
            idx = parent.children.index(self)
        self.Close()
        if parent is not None:
            (decoClass, subLayers,) = uicore.layerData.get(name, (None, None))
            parent.AddLayer(name, decoClass, subLayers, idx=idx)



    def AddLayer(self, name, decoClass = None, subLayers = None, idx = -1, loadLayerClass = False):
        if decoClass:
            layer = decoClass(parent=self, name=name, idx=idx, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        else:
            layer = uicls.LayerCore(parent=self, name=name, idx=idx, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        layer.decoClass = decoClass
        uicore.layerData[name] = (decoClass or uicls.LayerCore, subLayers)
        if name.startswith('l_'):
            setattr(uicore.layer, name[2:].lower(), layer)
        else:
            setattr(uicore.layer, name.lower(), layer)
        if subLayers is not None:
            for (_layerName, _decoClass, _subLayers,) in subLayers:
                layer.AddLayer(_layerName, _decoClass, _subLayers)

        return layer



    def LoadScene(self, scenefile, sceneName = ''):
        if not (sceneName and self.sceneName == sceneName):
            trinity.device.scene = blue.os.LoadObject(scenefile)
        self.sceneName = sceneName
        return trinity.device.scene



    def ClearScene(self):
        dev = trinity.device
        if dev is not None:
            dev.scene = trinity.Load('res:/Scene/emptyscene.red')
        self.sceneName = ''



    def IsClosed(self):
        return not self.isopen and not self.isopening




