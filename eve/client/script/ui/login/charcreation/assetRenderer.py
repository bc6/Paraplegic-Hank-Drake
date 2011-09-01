import service
import uicls
import uiconst
import blue
import trinity
import cameras
import geo2
import paperDoll
import paperDollUtil
import util
import ccUtil
import ccConst
import random
import shutil
import log
import uiutil
import math
import GameWorld
import types
SETUP = {ccConst.eyes: ('fj_eyeballRight', (0.15,
                 0,
                 0,
                 math.pi / 2 + 0.15,
                 math.pi / 2 - 0.07), None),
 ccConst.lipstick: ('fj_lip_lower_center', (0.2,
                     0,
                     0,
                     math.pi / 2 + 0.4,
                     math.pi / 2 + 0.05), None),
 ccConst.eyeshadow: ('fj_eyeballRight', (0.2,
                      0,
                      0,
                      math.pi / 2 + 0.3,
                      math.pi / 2 + 0.05), None),
 ccConst.eyelashes: ('fj_eyeballRight', (0.15,
                      0,
                      0,
                      math.pi / 2 + 0.3,
                      math.pi / 2 + 0.05), None),
 ccConst.eyeliner: ('fj_eyeballRight', (0.15,
                     0,
                     0,
                     math.pi / 2 + 0.3,
                     math.pi / 2 + 0.05), None),
 ccConst.eyebrows: ('fj_eyeballRight', (0.2,
                     0,
                     0,
                     math.pi / 2 + 0.3,
                     math.pi / 2 + 0.05), None),
 ccConst.hair: ('Head_End', (1.1,
                 0,
                 0,
                 math.pi / 2 - 0.3,
                 math.pi / 2 + 0.3), None),
 ccConst.beard: ('fj_lip_lower_center', (0.4,
                  0,
                  -0.015,
                  math.pi / 2 + 0.1,
                  math.pi / 2 + 0.3), None),
 ccConst.blush: ('Head', (0.6,
                  0,
                  0,
                  math.pi / 2 - 0.3,
                  math.pi / 2 + 0.3), 'SoftCenterRimSides'),
 ccConst.glasses: ('Head', (0.65,
                    0,
                    -0.02,
                    math.pi / 2 - 0.2,
                    math.pi / 2 + 0.3), None),
 ccConst.topmiddle: ('Spine3', (3.0,
                      0,
                      0,
                      math.pi / 2 - 0.3,
                      math.pi / 2 + 0.3), None),
 ccConst.topouter: ('Spine3', (3.0,
                     0,
                     0,
                     math.pi / 2 - 0.3,
                     math.pi / 2 + 0.3), None),
 ccConst.outer: ('Spine1', (3.5,
                  0,
                  0,
                  math.pi / 2 - 0.3,
                  math.pi / 2 + 0.3), None),
 ccConst.bottomouter: ('LeftLeg', (3.5,
                        0,
                        0,
                        math.pi / 2 + 0.5,
                        math.pi / 2 + 0.3), None),
 ccConst.feet: ('LeftFoot', (1.5,
                 0,
                 0,
                 math.pi / 2 + 0.5,
                 math.pi / 2 + 0.3), None),
 ccConst.p_earslow: ('fj_ear_wiggle', (0.4,
                      -0.025,
                      0,
                      math.pi + 0.1,
                      math.pi / 2), None),
 ccConst.p_earshigh: ('fj_ear_wiggle', (0.27,
                       -0.005,
                       0,
                       math.pi + 0.2,
                       math.pi / 2), None),
 ccConst.p_nose: ('fj_nose_left', (0.25,
                   0.02,
                   -0.01,
                   math.pi / 2 - 0.2,
                   math.pi / 2 + 0.3), None),
 ccConst.p_nostril: ('fj_nose_left', (0.2,
                      -0.01,
                      -0.01,
                      math.pi / 2 + 0.35,
                      math.pi / 2 + 0.2), None),
 ccConst.p_brow: ('fj_eyeballRight', (0.18,
                   0.005,
                   -0.005,
                   math.pi / 2 + 0.15,
                   math.pi / 2 - 0.07), None),
 ccConst.p_lips: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), None),
 ccConst.p_chin: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), None),
 ccConst.t_head: ('Head_End', (0.8,
                   0,
                   0,
                   math.pi / 2 - 0.1,
                   math.pi / 2), None),
 ccConst.s_head: ('Head_End', (0.65,
                   0,
                   0,
                   math.pi / 2 - 0.05,
                   math.pi / 2), None)}
DRESSCODE = {ccConst.eyes: (ccConst.eyebrows,),
 ccConst.eyeshadow: (ccConst.eyebrows,),
 ccConst.eyelashes: (ccConst.eyebrows,),
 ccConst.eyeliner: (ccConst.eyebrows,),
 ccConst.lipstick: (ccConst.eyebrows,),
 ccConst.blush: (ccConst.eyebrows,),
 ccConst.hair: (ccConst.topmiddle, ccConst.eyebrows),
 ccConst.eyebrows: (ccConst.hair,),
 ccConst.bottomouter: (ccConst.topmiddle, ccConst.feet),
 ccConst.topmiddle: (ccConst.bottomouter, ccConst.eyebrows, ccConst.hair),
 ccConst.topouter: (ccConst.bottomouter,
                    ccConst.topmiddle,
                    ccConst.eyebrows,
                    ccConst.hair),
 ccConst.outer: (ccConst.bottomouter,
                 ccConst.topmiddle,
                 ccConst.eyebrows,
                 ccConst.hair),
 ccConst.glasses: (ccConst.topmiddle, ccConst.eyebrows, ccConst.hair),
 ccConst.beard: (ccConst.hair, ccConst.eyebrows, ccConst.topmiddle),
 ccConst.feet: (ccConst.bottomouter,),
 ccConst.p_earslow: (ccConst.eyebrows, ccConst.hair),
 ccConst.p_earshigh: (ccConst.eyebrows, ccConst.hair),
 ccConst.p_nose: (ccConst.eyebrows, ccConst.hair),
 ccConst.p_nostril: (ccConst.eyebrows, ccConst.hair),
 ccConst.p_brow: (ccConst.eyebrows, ccConst.hair),
 ccConst.p_lips: (ccConst.eyebrows,),
 ccConst.t_head: (ccConst.eyebrows, ccConst.hair),
 ccConst.s_head: (ccConst.eyebrows, ccConst.hair)}
DRESSCODEINDEX = {ccConst.hair: 'shortcut'}
TUCKINDEX = {ccConst.bottomouter: 1}
EXAGGERATE = [(ccConst.blush, ccConst.GENDERID_MALE), (ccConst.eyeliner, ccConst.GENDERID_MALE), (ccConst.lipstick, ccConst.GENDERID_MALE)]
BLOODLINES = ((1, 'caldari_deteis'),
 (2, 'caldari_civire'),
 (11, 'caldari_achura'),
 (7, 'gallente_gallente'),
 (8, 'gallente_intaki'),
 (12, 'gallente_jinmei'),
 (3, 'minmatar_sebiestor'),
 (4, 'minmatar_brutor'),
 (14, 'minmatar_vherokior'),
 (5, 'amarr_amarr'),
 (13, 'amarr_khanid'),
 (6, 'amarr_nikunni'))
SCARGROUPS = {('scars/head/heroscar01', 'v0', ''): 'r_eye',
 ('scars/head/heroscar09', '', ''): 'r_eye',
 ('scars/head/heroscar01', 'v1', ''): 'l_eye',
 ('scars/head/heroscar09', 'v1', ''): 'l_eye',
 ('scars/head/heroscar02', '', ''): 'mouth',
 ('scars/head/heroscar02', 'v1', ''): 'mouth',
 ('scars/head/heroscar05', '', ''): 'forhead',
 ('scars/head/heroscar05', 'v1', ''): 'forhead',
 ('scars/head/heroscar18', '', ''): 'forhead',
 ('scars/head/heroscar11', '', ''): 'forhead',
 ('scars/head/heroscar11', 'v1', ''): 'forhead',
 ('scars/head/heroscar18', 'v1', ''): 'forhead',
 ('scars/head/heroscar08', '', ''): 'chin',
 ('scars/head/heroscar08', 'v1', ''): 'chin',
 ('scars/head/heroscar10', '', ''): 'nose',
 ('scars/head/heroscar10', 'v1', ''): 'nose',
 ('scars/head/heroscar12', '', ''): 'nose',
 ('scars/head/heroscar12', 'v1', ''): 'nose',
 ('scars/head/heroscar06', 'v1', ''): 'r_side',
 ('scars/head/heroscar13', '', ''): 'r_side',
 ('scars/head/heroscar14', '', ''): 'r_side',
 ('scars/head/heroscar15', 'v1', ''): 'r_side',
 ('scars/head/heroscar16', '', ''): 'r_side',
 ('scars/head/heroscar17', '', ''): 'r_side',
 ('scars/head/heroscar03', '', ''): 'r_side',
 ('scars/head/heroscar04', 'v1', ''): 'r_side',
 ('scars/head/heroscar07', 'v1', ''): 'r_side',
 ('scars/head/heroscar03', 'v1', ''): 'l_side',
 ('scars/head/heroscar04', '', ''): 'l_side',
 ('scars/head/heroscar07', '', ''): 'l_side',
 ('scars/head/heroscar06', '', ''): 'l_side',
 ('scars/head/heroscar13', 'v1', ''): 'l_side',
 ('scars/head/heroscar14', 'v1', ''): 'l_side',
 ('scars/head/heroscar15', '', ''): 'l_side',
 ('scars/head/heroscar16', 'v1', ''): 'l_side',
 ('scars/head/heroscar17', 'v1', ''): 'l_side'}
SCARCAMERASETINGS = {'l_eye': ('fj_eyeballLeft', (0.25,
            0,
            0,
            math.pi / 2 + 0.15,
            math.pi / 2 - 0.07), None),
 'r_eye': ('fj_eyeballRight', (0.25,
            0,
            0,
            math.pi / 2 + 0.15,
            math.pi / 2 - 0.07), None),
 'mouth': ('fj_lip_lower_center', (0.2,
            0,
            0,
            math.pi / 2 + 0.4,
            math.pi / 2 + 0.05), None),
 'l_cheek': ('Head', (0.6,
              0,
              0,
              math.pi / 2 - 0.6,
              math.pi / 2 + 0.3), None),
 'r_cheek': ('Head', (0.6,
              0,
              0,
              math.pi / 2 + 0.5,
              math.pi / 2 + 0.3), None),
 'l_side': ('Head', (0.65,
             0.025,
             -0.05,
             math.pi / 2 - 0.9,
             math.pi / 2 + 0.3), None),
 'r_side': ('Head', (0.65,
             0.025,
             0.05,
             math.pi / 2 + 1.0,
             math.pi / 2 + 0.3), None),
 'nose': ('fj_nose_left', (0.25,
           0.015,
           -0.01,
           math.pi / 2 - 0.2,
           math.pi / 2 + 0.3), None),
 'chin': ('fj_lip_lower_center', (0.25,
           0,
           0,
           math.pi / 2 + 0.4,
           math.pi / 2 + 0.05), None),
 'forhead': ('fj_foreheadLower_centerLeft', (0.35,
              0,
              -0.018,
              math.pi / 2 - 0.05,
              math.pi / 2), None)}
LIGHTLOCATION = 'res:/Graphics/Character/Global/PaperdollSettings/LightSettings/'
PIERCINGCATEGORIES = (ccConst.p_lips,
 ccConst.p_brow,
 ccConst.p_nostril,
 ccConst.p_nose,
 ccConst.p_earshigh,
 ccConst.p_earslow,
 ccConst.p_chin)
PIERCINGRIGHTGROUPS = {ccConst.p_earslow: ('fj_ear_wiggle', (0.3,
                      -0.01,
                      0,
                      math.pi + 0.1,
                      math.pi / 2), 'Normal'),
 ccConst.p_earshigh: ('fj_ear_wiggle', (0.27,
                       0,
                       0,
                       math.pi + 0.2,
                       math.pi / 2), 'Normal'),
 ccConst.p_nose: ('fj_nose_left', (0.25,
                   0.02,
                   -0.01,
                   math.pi / 2 - 0.2,
                   math.pi / 2 + 0.3), 'SoftCenterRimSides'),
 ccConst.p_nostril: ('fj_nose_left', (0.2,
                      -0.01,
                      -0.01,
                      math.pi / 2 + 0.35,
                      math.pi / 2 + 0.2), 'SoftCenterRimSides'),
 ccConst.p_brow: ('fj_eyeballRight', (0.18,
                   0.005,
                   -0.005,
                   math.pi / 2 + 0.15,
                   math.pi / 2 - 0.07), 'SoftCenterRimSides'),
 ccConst.p_lips: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides'),
 ccConst.p_chin: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides')}
PIERCINGLEFTGROUPS = {ccConst.p_earslow: ('fj_ear_wiggle', (0.3,
                      -0.01,
                      0,
                      -0.06,
                      math.pi / 2), 'TopRightRimSides'),
 ccConst.p_earshigh: ('fj_ear_wiggle', (0.27,
                       0,
                       0,
                       -0.08,
                       math.pi / 2), 'TopRightRimSides'),
 ccConst.p_nose: ('fj_nose_left', (0.25,
                   0.02,
                   -0.01,
                   math.pi / 2 - 0.2,
                   math.pi / 2 + 0.3), 'SoftCenterRimSides'),
 ccConst.p_nostril: ('fj_nose_left', (0.2,
                      -0.01,
                      -0.01,
                      math.pi / 2 + 0.35,
                      math.pi / 2 + 0.2), 'SoftCenterRimSides'),
 ccConst.p_brow: ('fj_eyeballLeft', (0.18,
                   0.005,
                   +0.005,
                   math.pi / 2 + 0.15,
                   math.pi / 2 - 0.07), 'SoftCenterRimSides'),
 ccConst.p_lips: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides'),
 ccConst.p_chin: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides')}
PIERCINGPAIRGROUPS = {ccConst.p_earslow: ('Head_End', (0.65,
                      0,
                      0,
                      math.pi / 2 - 0.05,
                      math.pi / 2), 'SoftCenterRimSides'),
 ccConst.p_earshigh: ('Head_End', (0.65,
                       0,
                       0,
                       math.pi / 2 - 0.05,
                       math.pi / 2), 'SoftCenterRimSides'),
 ccConst.p_nose: ('fj_nose_left', (0.25,
                   0.02,
                   -0.01,
                   math.pi / 2 - 0.2,
                   math.pi / 2 + 0.3), 'SoftCenterRimSides'),
 ccConst.p_nostril: ('fj_nose_left', (0.2,
                      -0.01,
                      -0.01,
                      math.pi / 2 + 0.35,
                      math.pi / 2 + 0.2), 'SoftCenterRimSides'),
 ccConst.p_brow: ('Head_End', (0.65,
                   0,
                   0,
                   math.pi / 2 - 0.05,
                   math.pi / 2), 'SoftCenterRimSides'),
 ccConst.p_lips: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides'),
 ccConst.p_chin: ('fj_lip_lower_center', (0.2,
                   0,
                   0,
                   math.pi / 2 + 0.4,
                   math.pi / 2 + 0.05), 'SoftCenterRimSides')}
HAIRBG = (0.2, 0.2, 0.2, 1.0)
MANNEQUINBG = (0.4, 0.4, 0.4, 1.0)
GREENSCREEN = (0.0, 1.0, 0.0, 1.0)
GLASSESBG = (0.0, 0.0, 0.0, 1.0)

def GetPaperDollResource(typeID, genderID):
    assets = []
    for each in cfg.paperdollResources:
        if each.typeID == typeID:
            assets.append(each)

    if len(assets) == 1:
        return assets[0]
    if len(assets) > 1:
        for asset in assets:
            if genderID == asset.resGender:
                return asset

    log.LogError('PreviewWnd::PreviewType - No asset matched the typeID: %d' % typeID)



class AssetRenderer(object):
    __guid__ = 'cc.AssetRenderer'
    __exportedcalls__ = {}

    def AddCheckbox(self, cbName, parent, groupname = None):
        setting = uiutil.Bunch(settings.user.ui.Get('assetRenderState', {}))
        cb = uicls.Checkbox(parent=parent, text=cbName, checked=bool(setting.Get(cbName, None)), callback=self.CBChange, groupname=groupname)
        cb.name = cbName
        return cb



    def CBChange(self, checkbox, *args):
        setting = settings.user.ui.Get('assetRenderState', {})
        setting[checkbox.name] = checkbox.GetValue()
        settings.user.ui.Set('assetRenderState', setting)
        if not getattr(self, 'spreadingValue', False):
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            if ctrl:
                self.spreadingValue = True
                if checkbox in self.bloodlines:
                    for each in self.bloodlines:
                        each.SetValue(checkbox.GetValue())

                elif checkbox in self.checkboxes:
                    for each in self.checkboxes:
                        each.SetValue(checkbox.GetValue())

                self.spreadingValue = False



    def __init__(self, showUI = True):
        trinity.SetFpsEnabled(False)
        if uicore.layer.charactercreation.isopen:
            uicore.layer.charactercreation.TearDown()
            uicore.layer.charactercreation.Flush()
        uicore.layer.login.CloseView()
        uicore.layer.charsel.CloseView()
        for each in uicore.layer.main.children[:]:
            each.Close()

        uicore.device.ForceSize()
        self.oldNonRandomize = getattr(prefs, 'NoRandomize', False)
        prefs.NoRandomize = True
        self.factory = sm.GetService('character').factory
        self.factory.compressTextures = False
        col1 = uicls.Container(parent=uicore.layer.main, align=uiconst.TOLEFT, width=100, padLeft=20, padTop=10)
        self.femaleCB = self.AddCheckbox('female', col1)
        self.maleCB = self.AddCheckbox('male', col1)
        col2 = uicls.Container(parent=uicore.layer.main, align=uiconst.TOLEFT, width=160, padTop=10)
        self.bloodlines = []
        for (bloodlineID, each,) in BLOODLINES:
            cb = self.AddCheckbox(each, col2)
            cb.bloodlineID = bloodlineID
            if bloodlineID in (1, 4, 14):
                cb.padLeft = -4
            self.bloodlines.append(cb)

        cb = self.AddCheckbox('mannequin', col2)
        cb.bloodlineID = -1
        cb.padTop = 10
        self.mannequinCB = cb
        cb = self.AddCheckbox('greenscreenCB', col1, 'bgCBs')
        cb.color = GREENSCREEN
        cb.padTop = 50
        self.greenscreenCB = cb
        cb = self.AddCheckbox('greyCB', col1, 'bgCBs')
        cb.color = HAIRBG
        self.greyCB = cb
        cb = self.AddCheckbox('blackCB', col1, 'bgCBs')
        cb.color = GLASSESBG
        self.blackCB = cb
        cb = self.AddCheckbox('mannequinCB', col1, 'bgCBs')
        cb.color = MANNEQUINBG
        self.mannequinBGCB = cb
        cb = self.AddCheckbox('otherCB', col1, 'bgCBs')
        cb.color = -1
        self.otherCB = cb
        (l, t, w, h,) = cb.GetAbsolute()
        self.otherEdit = uicls.SinglelineEdit(name='otherEdit', parent=col1, setvalue='', pos=(0,
         t + 6,
         100,
         16), hinttext='ex: (0.5, 0.5, 0.5, 1.0)')
        col3 = uicls.Container(parent=uicore.layer.main, align=uiconst.TOLEFT, width=140, padTop=10)
        self.checkboxes = []
        categs = SETUP.keys()
        categs.sort()
        for each in categs:
            cb = self.AddCheckbox(each, col3)
            self.checkboxes.append(cb)

        cb.padBottom = 20
        self.altCheckboxes = []
        for each in ('poses', 'lights'):
            cb = self.AddCheckbox(each, col3)
            self.altCheckboxes.append(cb)

        b1 = uicls.Button(parent=uicore.layer.main, label='Render', align=uiconst.CENTERBOTTOM, func=self.RenderLoopAll, top=20)
        b2 = uicls.Button(parent=uicore.layer.main, label='Try one item', align=uiconst.BOTTOMLEFT, func=self.RenderLoopTry, top=20, left=20)
        if not showUI:
            for each in [col1,
             col2,
             col3,
             b1,
             b2]:
                each.display = False




    def RenderLoopTry(self, *args):
        self.RenderLoop(tryout=True)



    def RenderLoopAll(self, *args):
        self.RenderLoop(tryout=False)



    def RenderLoop(self, tryout = False, fromWebtools = False):
        uicore.device.ForceSize()
        if getattr(self, 'renderJob', None):
            if self.renderJob in trinity.device.scheduledRecurring:
                trinity.device.scheduledRecurring.remove(self.renderJob)
        self.renderJob = None
        characterSvc = sm.GetService('character')
        characterSvc.characters = {}
        characterSvc.TearDown()
        uicore.layer.charactercreation.OpenView()
        uicore.layer.charactercreation.Flush()
        trinity.SetRightHanded(True)
        charID = 0
        for (layerName, layer,) in uicore.layer.__dict__.iteritems():
            if isinstance(layer, uicls.LayerCore):
                layer.display = False

        sm.GetService('sceneManager').SetSceneType(0)
        uicore.layer.charactercreation.SetupScene(ccConst.SCENE_PATH_CUSTOMIZATION)
        scene = uicore.layer.charactercreation.scene
        lightIntensity = 0.5
        lightScene = trinity.Load('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
        lightColorScene = trinity.Load('res:/Graphics/Character/Global/PaperdollSettings/LightColors/Normal.red')
        ccUtil.SetupLighting(scene, lightScene, lightColorScene, lightIntensity)
        uicore.layer.charactercreation.cameraUpdateJob = None
        uicore.layer.charactercreation.camera = cameras.CharCreationCamera(None)
        uicore.layer.charactercreation.SetupCameraUpdateJob()
        camera = uicore.layer.charactercreation.camera
        for each in trinity.device.scheduledRecurring:
            if each.name == 'cameraUpdate':
                trinity.device.scheduledRecurring.remove(each)
            elif each.name == 'Scene Render Job':
                for child in each.steps:
                    if isinstance(child, trinity.TriStepClear):
                        child.enabled = False


        rj = trinity.CreateRenderJob('Thumbnail RenderJob')
        updateScene = rj.Update(scene)
        updateScene.name = 'Update Scene'
        rj.Clear((0.0, 1.0, 0.0, 1.0), 1.0)
        rj.SetProjection(camera.projectionMatrix)
        rj.SetView(camera.viewMatrix)
        renderInteriorSceneStep = rj.RenderScene(scene)
        renderInteriorSceneStep.name = 'Render Scene'
        trinity.device.scheduledRecurring.insert(0, rj)
        self.renderJob = rj
        if fromWebtools:
            rj.Clear(MANNEQUINBG, 1.0)
        else:
            for cb in (self.greenscreenCB,
             self.greyCB,
             self.blackCB,
             self.mannequinBGCB):
                if cb.GetValue():
                    rj.Clear(cb.color, 1.0)
            else:
                if self.otherCB.GetValue() and self.otherEdit.GetValue():
                    text = self.otherEdit.GetValue()
                    evalText = eval(text)
                    if text and type(evalText) is tuple and len(evalText) == 4:
                        rj.Clear(evalText, 1.0)

        SWEETSPOTY = 1.7
        blue.pyos.synchro.Sleep(2000)
        for cb in self.altCheckboxes:
            if not cb.GetValue():
                continue
            altCategory = cb.name
            for (gender, genderID, genderCB,) in [('female', 0, getattr(self, 'femaleCB', None)), ('male', 1, getattr(self, 'maleCB', None))]:
                if genderCB and not genderCB.GetValue():
                    continue
                uicore.layer.charactercreation.genderID = genderID
                for bloodlineCB in self.bloodlines:
                    if not bloodlineCB.GetValue():
                        continue
                    characterSvc.RemoveCharacter(charID)
                    bloodlineID = bloodlineCB.bloodlineID
                    uicore.layer.charactercreation.ResetDna()
                    characterSvc.AddCharacterToScene(charID, scene, ccUtil.GenderIDToPaperDollGender(genderID), bloodlineID=bloodlineID)
                    doll = characterSvc.GetSingleCharactersDoll(charID)
                    doll.overrideLod = paperDoll.LOD_SKIN
                    doll.useCachedRenderTargets = True
                    doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[1]
                    characterSvc.SetDollBloodline(charID, bloodlineID)
                    characterSvc.ApplyItemToDoll(charID, 'head', paperDollUtil.bloodlineAssets[bloodlineID], doUpdate=False)
                    characterSvc.UpdateDoll(charID, fromWhere='RenderLoop')
                    for dcCategory in DRESSCODE[ccConst.hair]:
                        dcTypeData = characterSvc.GetAvailableTypesByCategory(dcCategory, genderID, bloodlineID)
                        if dcTypeData:
                            dcItemType = dcTypeData[0]
                            dcModifier = characterSvc.ApplyTypeToDoll(charID, dcItemType)

                    character = characterSvc.GetSingleCharacter(charID)
                    doll = character.doll
                    while len(scene.dynamics) < 1:
                        blue.synchro.Yield()

                    blue.synchro.Yield()
                    while doll.busyUpdating:
                        blue.synchro.Yield()

                    trinity.WaitForResourceLoads()
                    if genderID == 0:
                        camera.SetPointOfInterest((0.0, 1.6, 0.0))
                    else:
                        camera.SetPointOfInterest((0.0, 1.7, 0.0))
                    camera.distance = 1.4
                    camera.SetFieldOfView(0.3)
                    camera.Update()
                    if altCategory == 'poses':
                        characterSvc.StartPosing(charID)
                        character.avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 2)
                        for i in xrange(ccConst.POSERANGE):
                            characterSvc.ChangePose(i, charID)
                            blue.pyos.synchro.Sleep(100)
                            outputPath = 'C:/Temp/Thumbnails/%s_g%s_b%s.png' % ('pose_%s' % i, genderID, bloodlineID)
                            self.SaveScreenShot(outputPath)

                    elif altCategory == 'lights':
                        lightingList = ccConst.LIGHT_SETTINGS_ID
                        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
                        for each in lightingList:
                            for color in lightingColorList:
                                uicore.layer.charactercreation.SetLightsAndColor(each, color)
                                blue.synchro.Yield()
                                blue.resMan.Wait()
                                trinity.WaitForResourceLoads()
                                for i in xrange(10):
                                    blue.pyos.synchro.Sleep(100)

                                camera.Update()
                                outputPath = 'C:/Temp/Thumbnails/%s_g%s_b%s.png' % ('light_%s_%s' % (each, color), genderID, bloodlineID)
                                self.SaveScreenShot(outputPath)





        for (gender, genderID, genderCB,) in [('male', 1, getattr(self, 'maleCB', None)), ('female', 0, getattr(self, 'femaleCB', None))]:
            if not fromWebtools and genderCB and not genderCB.GetValue():
                continue
            if fromWebtools or getattr(self, 'mannequinCB', None) and self.mannequinCB.GetValue():
                mannequin = paperDoll.PaperDollCharacter(self.factory)
                mannequin.doll = paperDoll.Doll('mannequin', gender=ccUtil.GenderIDToPaperDollGender(genderID))
                if genderID == ccConst.GENDERID_MALE:
                    mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/MaleMannequin.prs', self.factory)
                else:
                    mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/FemaleMannequin.prs', self.factory)
                while mannequin.doll.busyUpdating:
                    blue.synchro.Yield()

                doll = mannequin.doll
                resolution = ccConst.TEXTURE_RESOLUTIONS[1]
                doll.overrideLod = paperDoll.LOD_SKIN
                doll.textureResolution = resolution
                mannequin.Spawn(scene, usePrepass=False)
                avatar = mannequin.avatar
                networkPath = ccConst.CHARACTER_CREATION_NETWORK
                self.factory.CreateGWAnimation(avatar, networkPath)
                network = avatar.animationUpdater.network
                if network is not None:
                    network.SetControlParameter('ControlParameters|BindPose', 1.0)
                    if doll.gender == 'female':
                        network.SetAnimationSetIndex(0)
                    else:
                        network.SetAnimationSetIndex(1)
                blue.pyos.synchro.Sleep(500)
                avatar.animationUpdater.network.SetControlParameter('ControlParameters|isAlive', 0)
                avatar.animationUpdater.network.update = False
                blue.pyos.synchro.Sleep(500)
                for checkBox in self.checkboxes:
                    if not fromWebtools and not checkBox.GetValue():
                        continue
                    if genderID == ccConst.GENDERID_MALE:
                        mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/MaleMannequin.prs', self.factory)
                    else:
                        mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/FemaleMannequin.prs', self.factory)
                    while mannequin.doll.busyUpdating:
                        blue.synchro.Yield()

                    lightScene = trinity.Load('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
                    ccUtil.SetupLighting(scene, lightScene, lightColorScene, lightIntensity)
                    category = checkBox.name
                    typeData = characterSvc.GetAvailableTypesByCategory(category, genderID, -1)
                    cameraSetup = self.SetUpCamera(camera, category, mannequin, SETUP, scene, lightColorScene, lightIntensity)
                    for itemType in typeData:
                        typeID = itemType[2]
                        if typeID is None:
                            continue
                        asset = GetPaperDollResource(typeID, genderID)
                        path = asset.resPath
                        modifier = doll.SetItemType(self.factory, path, weight=1.0)
                        mannequin.Update()
                        while doll.busyUpdating:
                            blue.synchro.Yield()

                        if paperDoll.SkinSpotLightShadows.instance is not None:
                            paperDoll.SkinSpotLightShadows.instance.Clear(killThread=True)
                            del paperDoll.SkinSpotLightShadows.instance
                            paperDoll.SkinSpotLightShadows.instance = None
                        ss = paperDoll.SkinSpotLightShadows(scene, debugVisualize=False, size=2048)
                        ss.SetupSkinnedObject(avatar)
                        paperDoll.SkinSpotLightShadows.instance = ss
                        blue.pyos.synchro.Sleep(500)
                        if fromWebtools:
                            outputPath = '%s/EVE/capture/Screenshots/Renders/%s.png' % (blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL), typeID)
                        else:
                            outputPath = 'C:/Temp/Thumbnails/%s_%s.png' % (typeID, itemType[0])
                        self.SaveScreenShot(outputPath)
                        doll.RemoveResource(modifier.GetResPath(), self.factory)
                        if tryout:
                            break


                if avatar and avatar in scene.dynamics:
                    scene.dynamics.remove(avatar)
            for bloodlineCB in self.bloodlines:
                if fromWebtools or not bloodlineCB.GetValue():
                    continue
                characterSvc.RemoveCharacter(charID)
                bloodlineID = bloodlineCB.bloodlineID
                uicore.layer.charactercreation.ResetDna()
                characterSvc.AddCharacterToScene(charID, scene, ccUtil.GenderIDToPaperDollGender(genderID), bloodlineID=bloodlineID)
                doll = characterSvc.GetSingleCharactersDoll(charID)
                doll.overrideLod = paperDoll.LOD_SKIN
                doll.useCachedRenderTargets = True
                doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[1]
                characterSvc.SetDollBloodline(charID, bloodlineID)
                characterSvc.ApplyItemToDoll(charID, 'head', paperDollUtil.bloodlineAssets[bloodlineID], doUpdate=False)
                characterSvc.UpdateDoll(charID, fromWhere='RenderLoop')
                character = characterSvc.GetSingleCharacter(charID)
                character.avatar.translation = (0.0, 0.0, 0.0)
                doll = character.doll
                while len(scene.dynamics) < 1:
                    blue.synchro.Yield()

                blue.synchro.Yield()
                while doll.busyUpdating:
                    blue.synchro.Yield()

                character.avatar.animationUpdater.network.SetControlParameter('ControlParameters|isAlive', 0)
                character.avatar.animationUpdater.network.update = False
                trinity.WaitForResourceLoads()
                for checkBox in self.checkboxes:
                    lightScene = trinity.Load('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
                    ccUtil.SetupLighting(scene, lightScene, lightColorScene, lightIntensity)
                    if not checkBox.GetValue():
                        continue
                    category = checkBox.name
                    typeData = characterSvc.GetAvailableTypesByCategory(category, genderID, bloodlineID)
                    cameraSetup = self.SetUpCamera(camera, category, character, SETUP, scene, lightColorScene, lightIntensity)
                    removeDcModifers = []
                    if category in DRESSCODE:
                        for dcCategory in DRESSCODE[category]:
                            dcTypeData = characterSvc.GetAvailableTypesByCategory(dcCategory, genderID, bloodlineID)
                            if dcTypeData:
                                useIndex = DRESSCODEINDEX.get(dcCategory, 0)
                                if type(useIndex) in types.StringTypes:
                                    for (_idx, _itemType,) in enumerate(dcTypeData):
                                        if useIndex in _itemType[1][0]:
                                            useIndex = _idx
                                            break
                                    else:
                                        useIndex = -1

                                dcItemType = dcTypeData[useIndex]
                                var = None
                                if dcCategory == ccConst.hair:
                                    var = self.GetHairColor(genderID, bloodlineID)
                                dcModifier = characterSvc.ApplyTypeToDoll(charID, dcItemType, rawColorVariation=var)
                                if dcModifier:
                                    removeDcModifers.append(dcModifier.GetResPath())
                                while doll.busyUpdating:
                                    blue.synchro.Yield()

                                blue.resMan.Wait()

                    for itemType in typeData:
                        modifer = characterSvc.ApplyTypeToDoll(charID, itemType)
                        if not modifer:
                            continue
                        typeInfo = itemType[1]
                        if typeInfo[0].startswith('scars'):
                            self.SetCameraForScar(typeInfo, character, camera)
                        if typeInfo[0].startswith(PIERCINGCATEGORIES):
                            self.SetCameraAndLightPiercings(category, typeInfo, character, camera, scene, lightColorScene, lightIntensity)
                        if category in TUCKINDEX:
                            (tuckPath, requiredModifier, subKey,) = ccConst.TUCKMAPPING[category]
                            tuckModifier = sm.GetService('character').GetModifierByCategory(charID, tuckPath)
                            if tuckModifier:
                                tuckVariations = tuckModifier.GetVariations()
                                tuckStyle = tuckModifier.GetResPath().split('/')[-1]
                                characterSvc.ApplyItemToDoll(charID, category, tuckStyle, variation=tuckVariations[TUCKINDEX[category]])
                        cat = category
                        if category in (ccConst.beard, ccConst.hair, ccConst.eyebrows):
                            cat = ccConst.hair
                        try:
                            if not typeInfo[1] and not typeInfo[2]:
                                categoryColors = characterSvc.GetAvailableColorsForCategory(cat, genderID, bloodlineID)
                                if categoryColors:
                                    (primary, secondary,) = categoryColors
                                    primaryVal = (primary[1][0], primary[1][2])
                                    if primary and secondary:
                                        secondaryVal = (secondary[1][0], secondary[1][2])
                                        characterSvc.SetColorValueByCategory(charID, cat, primaryVal, secondaryVal)
                                    else:
                                        characterSvc.SetColorValueByCategory(charID, cat, primaryVal, None)
                        except:
                            pass
                        if category in (ccConst.beard, ccConst.hair, ccConst.eyebrows):
                            sm.GetService('character').SetHairDarkness(0, 0.5)
                        if (category, genderID) in EXAGGERATE:
                            if getattr(modifer, 'weight', None) is not None:
                                modifer.weight = 1.5 * modifer.weight
                        characterSvc.UpdateDoll(charID, fromWhere='RenderLoop')
                        while doll.busyUpdating:
                            blue.synchro.Yield()

                        blue.resMan.Wait()
                        trinity.WaitForResourceLoads()
                        if paperDoll.SkinSpotLightShadows.instance is not None:
                            paperDoll.SkinSpotLightShadows.instance.Clear(killThread=True)
                            del paperDoll.SkinSpotLightShadows.instance
                            paperDoll.SkinSpotLightShadows.instance = None
                        ss = paperDoll.SkinSpotLightShadows(scene, debugVisualize=False, size=2048)
                        ss.SetupSkinnedObject(character.avatar)
                        paperDoll.SkinSpotLightShadows.instance = ss
                        if tryout:
                            break
                        blue.pyos.synchro.Sleep(500)
                        outputPath = 'C:/Temp/Thumbnails/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), genderID, bloodlineID)
                        self.SaveScreenShot(outputPath)
                        doll.RemoveResource(modifer.GetResPath(), characterSvc.factory)

                    for dcResPath in removeDcModifers:
                        doll.RemoveResource(dcResPath, characterSvc.factory)


                if tryout:
                    break

            if tryout:
                break

        uicore.layer.main.display = True
        print 'DONE'
        prefs.NoRandomize = self.oldNonRandomize



    def SetCameraAndLightPiercings(self, category, typeInfo, character, camera, scene, colorScene, intensity):
        (typeName, a, b,) = typeInfo
        if typeName.endswith('left', 0, -1):
            dictToUse = PIERCINGLEFTGROUPS
        elif typeName.endswith('right', 0, -1):
            dictToUse = PIERCINGRIGHTGROUPS
        else:
            dictToUse = PIERCINGPAIRGROUPS
        self.SetUpCamera(camera, category, character, dictToUse, scene, colorScene, intensity)



    def SetCameraForScar(self, typeInfo, character, camera, scene, colorScene, intensity):
        group = SCARGROUPS.get(typeInfo, None)
        if group is None:
            print 'couldnt find the group, return'
            return 
        self.SetUpCamera(camera, group, character, SCARCAMERASETINGS, scene, colorScene, intensity)



    def SetCamera(self, camera, poi, distance, yaw, pitch):
        camera.SetPointOfInterest(poi)
        camera.distance = distance
        camera.SetFieldOfView(0.3)
        camera.SetYaw(yaw)
        camera.SetPitch(pitch)
        camera.Update()



    def SetUpCamera(self, camera, category, character, categoryList = SETUP, scene = None, colorScene = None, intensity = None):
        if category in categoryList:
            (boneName, offset, lightSetting,) = categoryList[category]
            if lightSetting:
                path = '%s%s.red' % (LIGHTLOCATION, lightSetting)
                lightScene = trinity.Load(path)
                ccUtil.SetupLighting(scene, lightScene, colorScene, intensity)
            joint = 4294967295L
            while joint == 4294967295L:
                joint = character.avatar.GetBoneIndex(boneName)
                blue.synchro.Yield()

            poi = character.avatar.GetBonePosition(joint)
            (distance, yOffset, xOffset, yaw, pitch,) = offset
            (x, y, z,) = poi
            if yOffset:
                y += yOffset
            if xOffset:
                x += xOffset
            poi = (x, y, z)
            if category in (ccConst.bottomouter, ccConst.feet):
                poi = (0.0, y, z)
            self.SetCamera(camera, poi, distance, yaw, pitch)
            return (distance,
             yaw,
             pitch,
             poi)
        else:
            return None



    def GetHairColor(self, genderID, bloodlineID):
        (colorsA, colorsB,) = sm.GetService('character').GetAvailableColorsForCategory(ccConst.hair, genderID, bloodlineID)
        colorA = []
        colorB = []
        var = None
        colorizeData = None
        (color1Value, color1Name, color2Name, variation,) = (None, None, None, None)
        if len(colorsA) > 0:
            indexA = int(len(colorsA) * 0.3)
            colorA = colorsA[indexA]
            colorB = None
            if len(colorsB) > 0:
                colorB = colorsB[0]
            (color1Value, color1Name, color2Name, variation,) = sm.GetService('character').GetColorsToUse(colorA, colorB)
        if color1Value:
            colorizeData = color1Value
        elif colorB:
            var = variation
        elif len(colorA) > 0:
            var = colorA[1]
        return var



    def SaveScreenShot(self, path):
        dev = trinity.device
        backBuffer = dev.GetBackBuffer(0)
        tileWidth = backBuffer.width
        tileHeight = backBuffer.height
        backBufferSys = dev.CreateOffscreenPlainSurface(tileWidth, tileHeight, backBuffer.format, trinity.TRIPOOL_SYSTEMMEM)
        dev.GetRenderTargetData(backBuffer, backBufferSys)
        backBufferSys.SaveSurfaceToFile(path, trinity.TRIIFF_PNG)
        print 'SaveScreenShot',
        print path



    def RemoveSkin(self, avatar):
        meshes = avatar.Find('trinity.Tr2Mesh')
        for m in meshes:
            moveList = []
            doubleSided = False
            for a in m.opaqueAreas:
                effect = a.effect
                doubleSided = False
                if effect.name.lower().startswith('c_skin') or effect.name.lower().startswith('c_eye') or effect.name.lower().startswith('c_teeth'):
                    if a not in moveList:
                        moveList.append(a)
                else:
                    doubleSided = True

            if doubleSided:
                a2 = a.CopyTo()
                a2.reversed = True
                m.opaqueAreas.append(a2)
            for a in moveList:
                m.opaqueAreas.remove(a)
                m.decalAreas.append(a)
                a2 = a.CopyTo()
                a2.effect = a.effect
                a2.reversed = True
                m.decalAreas.append(a2)

            if m.name.startswith('head'):
                m.debugIsHidden = True





