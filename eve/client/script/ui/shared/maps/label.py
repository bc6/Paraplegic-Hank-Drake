import bluepy
import uix
import uthread
import trinity
import xtriui
import blue
import uicls
import uiconst
NEUTRAL_COLOR = (1.0, 1.0, 1.0, 0.5)
HIGHLIGHT_COLOR = (1.0, 1.0, 1.0, 0.5)

class MapLabel(uicls.Bracket):
    __guid__ = 'xtriui.MapLabel'

    def init(self):
        self.state = uiconst.UI_PICKCHILDREN
        self.preFullAlpha = None



    def Startup(self, name, itemID, typeID, tracker, cloud, mylocation = None):
        self.trackTransform = tracker
        self.sr.cloud = cloud
        self.sr.id = itemID
        self.sr.typeID = typeID
        self.name = name
        if name in ('', 'myDest', 'myloc'):
            return 
        frame = None
        if itemID > 0:
            if typeID == const.typeConstellation:
                label = xtriui.ParentLabel(text='<b>' + name + '</b>', parent=self, left=154, top=4, fontsize=12, uppercase=1, state=uiconst.UI_NORMAL)
                frame = uicls.Frame(parent=self, align=uiconst.RELATIVE, weight=2, padLeft=3, padRight=4, padTop=4, padBottom=4)
            else:
                label = xtriui.ParentLabel(text=name, parent=self, left=154, top=7, letterspace=1, fontsize=9, uppercase=1, state=uiconst.UI_NORMAL)
        else:
            label = xtriui.ParentLabel(text=name, parent=self, left=154, top=7, letterspace=1, fontsize=9, uppercase=1, state=uiconst.UI_NORMAL)
        if not mylocation:
            if self.sr.id < 0:
                label.color.SetRGB(1.0, 0.96, 0.78, 1.0)
        if typeID != const.typeSolarSystem:
            label.left = (self.width - label.width) / 2
        if frame:
            frame.left = label.left - 5
            frame.width = label.width + 10
            frame.top = label.top - 3
            frame.height = label.height + 6
        label.state = uiconst.UI_NORMAL
        return self



    def OnMouseEnter(self, *args):
        return 
        self.ShowFullAlpha()
        if self.sr.id > 0:
            sm.GetService('starmap').UpdateLines(self.sr.id)



    def ShowFullAlpha(self):
        if self.preFullAlpha is None:
            self.preFullAlpha = self.children[0].color.a
        self.children[0].color.a = 1.0



    def OnMouseExit(self, *args):
        return 
        if self.sr.id > 0:
            if self.sr.typeID == const.typeConstellation:
                sm.GetService('starmap').UpdateLines(None)
        self.ResetFullAlpha()



    def ResetFullAlpha(self):
        if self.preFullAlpha is not None:
            self.children[0].color.a = self.preFullAlpha
            self.preFullAlpha = None



    def OnClick(self, *args):
        sm.GetService('starmap').SetInterest(self.sr.id)



    def GetMenu(self):
        starmap = sm.GetService('starmap')
        m = []
        if self.sr.id >= 0:
            m += starmap.GetItemMenu(self.sr.id)
        else:
            m.append((self.name, sm.GetService('info').ShowInfo, (self.sr.typeID, self.sr.id)))
            m.append((mls.UI_CMD_CENTERONSCREEN, starmap.SetInterest, (self.sr.id, 1)))
        return m



    def OnMouseWheel(self, *etc):
        lib = uicore.uilib
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        if hasattr(camera, 'translationCurve'):
            targetTrans = camera.translationCurve.GetVectorAt(blue.os.GetTime(1)).z * (1.0 + -lib.dz * 0.001)
            if targetTrans < 2.0:
                targetTrans = 2.0
            if targetTrans > 10000.0:
                targetTrans = 10000.0
            camera.translationCurve.keys[1].value.z = targetTrans
        uthread.new(sm.GetService('starmap').CheckLabelDist)




class ParentLabel(uicls.Label):
    __guid__ = 'xtriui.ParentLabel'

    def OnMouseEnter(self, *etc):
        self.parent.OnMouseEnter(*etc)



    def OnMouseExit(self, *etc):
        self.parent.OnMouseExit(*etc)



    def OnClick(self, *etc):
        self.parent.OnClick(*etc)



    def OnMouseWheel(self, *etc):
        self.parent.OnMouseWheel(self, *etc)



    def GetMenu(self, *etc):
        return self.parent.GetMenu(*etc)




class TransformableLabel(object):
    __guid__ = 'xtriui.TransformableLabel'
    __persistvars__ = ['shader']

    def __init__(self, text, parent, size = 72, shadow = 0, hspace = 8):
        self.transform = trinity.EveTransform()
        self.transform.mesh = trinity.Tr2Mesh()
        self.transform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        self.transform.modifier = 1
        kwargs = {'fontsize': size,
         'align': uiconst.TOPLEFT,
         'autowidth': 1,
         'autoheight': 1,
         'state': uiconst.UI_NORMAL,
         'letterspace': hspace,
         'uppercase': 1}
        if not shadow:
            kwargs['shadow'] = []
        textObject = uicls.Label(text=('<b>' + text + '</b>'), parent=None, **kwargs)
        textObject.Render()
        self.transform.scaling = (textObject.width, textObject.height, 0)
        tr = trinity.device.CreateTexture(textObject.width, textObject.height, 1, 0, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_MANAGED)
        surface = tr.GetSurfaceLevel(0)
        textObject.texture.atlasTexture.CopyToSurface(surface)
        textObject.Close()
        area = trinity.Tr2MeshArea()
        self.transform.mesh.transparentAreas.append(area)
        area.effect = effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        diffuseColor = trinity.TriVector4Parameter()
        diffuseColor.name = 'DiffuseColor'
        effect.parameters.append(diffuseColor)
        self.diffuseColor = diffuseColor
        diffuseMap = trinity.TriTexture2DParameter()
        diffuseMap.name = 'DiffuseMap'
        diffuseMap.SetResource(tr)
        effect.resources.append(diffuseMap)
        parent.children.append(self.transform)



    def SetDiffuseColor(self, color):
        self.diffuseColor.value = color



    def SetHighlight(self, highlight):
        if highlight:
            self.diffuseColor.value = HIGHLIGHT_COLOR
        else:
            self.diffuseColor.value = NEUTRAL_COLOR



    def SetDisplay(self, display):
        self.transform.display = display




