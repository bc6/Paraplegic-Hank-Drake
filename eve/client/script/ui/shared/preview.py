from service import *
import sys
import blue
import trinity
import log
import xtriui
import math
import uix
import uiutil
import form
import uthread
import random
import util
import listentry
import uicls
import uiconst
import paperDoll as pd
import GameWorld
import ccUtil
import ccConst
import geo2
import turret
MESH_NAMES_BY_GROUPID = {1083: 'accessories',
 1084: pd.BODY_CATEGORIES.TATTOO,
 1085: 'TODO',
 1086: pd.BODY_CATEGORIES.SCARS,
 1087: pd.BODY_CATEGORIES.TOPINNER,
 1088: pd.BODY_CATEGORIES.OUTER,
 1089: pd.BODY_CATEGORIES.TOPINNER,
 1090: pd.BODY_CATEGORIES.BOTTOMOUTER,
 1091: pd.BODY_CATEGORIES.FEET,
 1092: pd.DOLL_PARTS.HAIR,
 1093: pd.HEAD_CATEGORIES.MAKEUP}
paperDollCategories = [30]

def GetPaperDollResource(typeID):
    assets = []
    for each in cfg.paperdollResources:
        if each.typeID == typeID:
            assets.append(each)

    if len(assets) == 1:
        return assets[0]
    if len(assets) > 1:
        for asset in assets:
            if eve.session.genderID == asset.resGender:
                return asset

    log.LogError('PreviewWnd::PreviewType - No asset matched the typeID: %d' % typeID)



class Preview(Service):
    __exportedcalls__ = {'PreviewType': []}
    __dependencies__ = []
    __update_on_reload__ = 0
    __guid__ = 'svc.preview'
    __servicename__ = 'preview'
    __displayname__ = 'Preview Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting Preview Service')



    def PreviewType(self, typeID, subsystems = None):
        wnd = sm.GetService('window').GetWindow('PreviewWnd', create=1)
        wnd.PreviewType(typeID, subsystems)




class PreviewWnd(uicls.Window):
    __guid__ = 'form.PreviewWnd'
    __notifyevents__ = ['OnSetDevice', 'OnResizeUpdate']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.typeID = None
        self.scope = 'all'
        self.SetCaption(mls.UI_GENERIC_PREVIEW)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([420, 320])
        self.sr.rightSide = rightSide = uicls.Container(name='rightSide', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(6, 6, 6, 6), clipChildren=1)
        self.loadingWheel = uicls.LoadingWheel(parent=self.sr.rightSide, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        listbtn = uicls.MenuIcon(size=24, ignoreSize=True)
        listbtn.sr.owner = self
        listbtn.state = uiconst.UI_NORMAL
        listbtn.align = uiconst.NOALIGN
        listbtn.left = 2
        listbtn.top = 10
        listbtn.hint = mls.UI_SHARED_LISTITEMSINSOLARSYSTEM
        listbtn.GetMenu = self.GetShipMenu
        self.listbtn = listbtn
        self.sr.title = t = uicls.Label(text='', parent=rightSide, left=17, top=4, letterspace=1, fontsize=20, state=uiconst.UI_NORMAL, idx=0, uppercase=1)
        t.mmbold = 0.5
        self.sr.title.GetMenu = self.GetShipMenu
        self.sr.title.expandOnLeft = 1
        self.sr.subtitle = t = uicls.Label(text='', parent=rightSide, left=19, top=28, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, idx=0, uppercase=1)
        self.textCont = uicls.Container(parent=self.sr.rightSide, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 150))
        self.desc = uicls.Edit(parent=self.textCont, readonly=1, hideBackground=1, padding=(6, 6, 6, 6), fontsize=12)
        sc = form.SceneContainer(parent=self.sr.rightSide, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        sc.Startup()
        self.sr.sceneContainer = sc
        nav = form.SceneContainerBaseNavigation(parent=self.sr.rightSide, state=uiconst.UI_NORMAL)
        nav.Startup(sc)
        nav.OnClick = self.OnClickNav
        self.sr.navigation = nav
        self.mannequin = None



    def OnClose_(self, *args):
        self.CloseSubSystemWnd()
        self.sr.sceneContainer.scene = None
        self.sr.sceneContainer = None
        self.mannequin = None



    def OnClickNav(self, *args):
        self.BringToFront()



    def BringToFront(self):
        self.Maximize()
        wnd = sm.GetService('window').GetWindow('PreviewSubSystems', create=0)
        if wnd:
            wnd.Maximize()



    def GetShipMenu(self, *args):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, getattr(self, 'typeID', None), ignoreMarketDetails=False, filterFunc=[mls.UI_CMD_PREVIEW])



    def PreviewType(self, typeID, subsystems = None):
        typeID = int(typeID)
        if typeID != self.typeID:
            self.CloseSubSystemWnd()
        isFirst = self.typeID is None
        typeOb = cfg.invtypes.Get(typeID)
        groupID = typeOb.groupID
        groupOb = cfg.invgroups.Get(groupID)
        categoryID = groupOb.categoryID
        self.categoryID = categoryID
        self.groupID = groupID
        self.typeID = typeID
        self.sr.title.text = '%s' % cfg.invtypes.Get(typeID).name
        raceID = typeOb.raceID
        races = sm.GetService('cc').GetData('races')
        raceName = ''
        radius2 = typeOb.radius * 2.0
        rad = 4.0
        self.textCont.display = False
        self.SetMinSize([420, 320])
        self.SetMaxSize([None, None])
        for r in races:
            if r.raceID == raceID:
                raceName = '%s - ' % Tr(r.raceName, 'character.races.raceName', r.dataID)
                break

        if self.categoryID not in paperDollCategories:
            self.sr.subtitle.text = '%s%s (%s)' % (raceName, groupOb.groupName, mls.UI_GENERIC_AXISLENGTH % {'length': util.FmtDist(radius2)})
        else:
            self.sr.subtitle.text = ''
        godma = sm.GetService('godma')
        try:
            techLevel = godma.GetTypeAttribute(typeID, const.attributeTechLevel)
        except:
            techLevel = 1.0
        self.loadingWheel.Show()
        if categoryID == const.categoryShip and techLevel == 3.0:
            self.sr.sceneContainer.PrepareSpaceScene()
            if subsystems is None:
                subsystems = {}
                subSystemsForType = {}
                for group in cfg.groupsByCategories.get(const.categorySubSystem, []):
                    if group.groupID not in subSystemsForType:
                        subSystemsForType[group.groupID] = []
                    for t in cfg.typesByGroups.get(group.groupID, []):
                        if t.published and godma.GetTypeAttribute(t.typeID, const.attributeFitsToShipType) == typeID:
                            subSystemsForType[group.groupID].append(t.typeID)


                for (k, v,) in subSystemsForType.iteritems():
                    subsystems[k] = random.choice(v)

            model = sm.StartService('t3ShipSvc').GetTech3ShipFromDict(typeID, subsystems)
            kv = util.KeyVal(typeID=typeID)
            wnd = sm.GetService('window').GetWindow('PreviewSubSystems', create=1, decoClass=form.AssembleShip, ship=kv, groupIDs=None, isPreview=True)
            wnd.SetSelected(subsystems)
        elif self.categoryID in paperDollCategories:
            desc = typeOb.description
            desc = desc or ''
            for each in ('<b>', '</b>', '\r'):
                desc = desc.replace(each, '')

            desc = desc.replace('\n', '<br>')
            self.desc.SetValue(desc)
            self.textCont.display = True
            self.SetMinSize([320, 470])
            self.SetMaxSize([800, 950])
            self.sr.sceneContainer.cameraParent.translation = trinity.TriVector(9.0, -1000, 0.0)
            self.sr.sceneContainer.PrepareInteriorScene()
            scene = self.sr.sceneContainer.scene
            factory = pd.Factory()
            asset = GetPaperDollResource(typeID)
            if asset is None:
                log.LogError('PreviewWnd::PreviewType - Invalid asset')
                self.loadingWheel.Hide()
                return 
            path = asset.resPath
            genderID = asset.resGender
            self.mannequin = pd.PaperDollCharacter(factory)
            self.mannequin.doll = pd.Doll('mannequin', gender=ccUtil.GenderIDToPaperDollGender(genderID))
            if genderID == ccConst.GENDERID_MALE:
                self.mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/MaleMannequin.prs', factory)
            else:
                self.mannequin.doll.Load('res:/Graphics/Character/DNAFiles/Mannequin/FemaleMannequin.prs', factory)
            while self.mannequin.doll.busyUpdating:
                blue.synchro.Yield()
                if self.mannequin is None:
                    return 

            textureQuality = prefs.GetValue('charTextureQuality', sm.GetService('device').GetDefaultCharTextureQuality())
            resolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
            self.mannequin.doll.overrideLod = 0
            self.mannequin.doll.textureResolution = resolution
            self.mannequin.Spawn(scene, usePrepass=False)
            while self.mannequin.doll.busyUpdating:
                blue.synchro.Yield()
                if self.mannequin is None:
                    return 

            meshListPre = self.mannequin.doll.buildDataManager.GetMeshes(includeClothMeshes=True)
            self.mannequin.doll.SetItemType(factory, path, weight=1.0)
            self.mannequin.Update()
            while self.mannequin.doll.busyUpdating:
                blue.synchro.Yield()
                if self.mannequin is None:
                    return 

            meshListPost = self.mannequin.doll.buildDataManager.GetMeshes(includeClothMeshes=True)
            animationUpdater = GameWorld.GWAnimation('res:/Animation/MorphemeIncarna/Export/Mannequin/Mannequin.mor')
            if animationUpdater is not None:
                self.mannequin.avatar.animationUpdater = animationUpdater
                if self.mannequin.doll.gender == pd.GENDER.FEMALE:
                    animationUpdater.network.SetAnimationSetIndex(0)
                else:
                    animationUpdater.network.SetAnimationSetIndex(1)
            bBox = (geo2.Vector(1000.0, 1000.0, 1000.0), geo2.Vector(-1000.0, -1000.0, -1000.0))
            if groupID in MESH_NAMES_BY_GROUPID:
                meshName = MESH_NAMES_BY_GROUPID[groupID]
                found = False
                for mesh in meshListPost:
                    if mesh.name.startswith(meshName) or mesh not in meshListPre:
                        fromMesh = mesh.geometry.GetBoundingBox(0)
                        bBox[0].x = min(bBox[0].x, fromMesh[0].x)
                        bBox[0].y = min(bBox[0].y, fromMesh[0].y)
                        bBox[0].z = min(bBox[0].z, fromMesh[0].z)
                        bBox[1].x = max(bBox[1].x, fromMesh[1].x)
                        bBox[1].y = max(bBox[1].y, fromMesh[1].y)
                        bBox[1].z = max(bBox[1].z, fromMesh[1].z)
                        found = True

                if not found:
                    bBox = (geo2.Vector(-0.1, 1.6, -0.1), geo2.Vector(0.1, 1.8, 0.1))
            center = ((bBox[1].x + bBox[0].x) / 2.0, (bBox[1].y + bBox[0].y) / 2.0, (bBox[1].z + bBox[0].z) / 2.0)
            rad = geo2.Vec3Length(bBox[0] - bBox[1])
            rad = max(rad, 0.3)
            self.sr.sceneContainer.cameraParent.translation = trinity.TriVector(*center)
            floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            scene.dynamics.append(floor)
            model = None
        elif self.groupID in const.turretModuleGroups:
            self.sr.sceneContainer.PrepareSpaceScene(0.0, 'res:/dx9/scene/fitting/previewTurrets.red')
            model = trinity.Load('res:/dx9/model/ship/IconPreview/PreviewTurretShip.red')
            turretSet = turret.TurretSet.FitTurret(model, None, typeID, 1, checkSettings=False)
            if turretSet is not None:
                boundingSphere = turretSet.turretSets[0].boundingSphere
                model.boundingSphereRadius = boundingSphere[3]
                model.boundingSphereCenter = boundingSphere[:3]
                if model.boundingSphereCenter[1] < 2.0:
                    model.boundingSphereCenter = (boundingSphere[0], 2.0, boundingSphere[2])
                for ts in turretSet.turretSets:
                    ts.bottomClipHeight = 0.0
                    ts.FreezeHighDetailLOD()
                    ts.ForceStateDeactive()
                    ts.EnterStateIdle()

                self.sr.subtitle.text = '%s (%s)' % (groupOb.groupName, mls.UI_GENERIC_AXISLENGTH % {'length': util.FmtDist(model.boundingSphereRadius)})
        else:
            self.sr.sceneContainer.PrepareSpaceScene()
            fileName = typeOb.GraphicFile()
            if fileName == '':
                log.LogWarn('type', typeID, 'has no graphicFile')
                self.loadingWheel.Hide()
                return 
            fileName = fileName.replace(':/Model', ':/dx9/Model').replace('.blue', '.red')
            fileName = fileName.partition(' ')[0]
            model = trinity.Load(fileName)
            if model is None:
                self.sr.sceneContainer.ClearScene()
                self.loadingWheel.Hide()
                raise UserError('PreviewNoModel')
            if getattr(model, 'boosters', None) is not None:
                model.boosters = None
            if getattr(model, 'modelRotationCurve', None) is not None:
                model.modelRotationCurve = None
            if getattr(model, 'modelTranslationCurve', None) is not None:
                model.modelTranslationCurve = None
        if hasattr(model, 'ChainAnimationEx'):
            model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.sr.sceneContainer.AddToScene(model)
        camera = self.sr.sceneContainer.camera
        navigation = self.sr.navigation
        spaceObject = False
        if hasattr(model, 'GetBoundingSphereRadius'):
            rad = model.GetBoundingSphereRadius()
            spaceObject = True
        minZoom = rad + self.sr.sceneContainer.frontClip
        alpha = self.sr.sceneContainer.fieldOfView / 2.0
        if spaceObject:
            maxZoom = max(rad * (1 / math.tan(alpha)) * 2, 1.0)
            camera.translationFromParent.z = minZoom * 2
        else:
            maxZoom = min(rad * (1 / math.tan(alpha * 1.5)), 7.0)
            camera.translationFromParent.z = minZoom * 3
        navigation.SetMinMaxZoom(minZoom, maxZoom)
        self.sr.sceneContainer.UpdateViewPort()
        self.BringToFront()
        if isFirst:
            uthread.new(self.OrbitParent)
        self.loadingWheel.Hide()



    def OrbitParent(self):
        self.sr.sceneContainer.camera.OrbitParent(8.0, 5.0)



    def CloseSubSystemWnd(self):
        wnd = sm.GetService('window').GetWindow('PreviewSubSystems')
        if wnd:
            wnd.Close()



    def OnResize_(self, *args):
        self.OnResizeUpdate()



    def OnMove(self, *args):
        if self.sr.Get('sceneContainer'):
            self.sr.sceneContainer.UpdateViewPort()



    def OnResizeUpdate(self, *args):
        if self.sr.Get('sceneContainer'):
            self.sr.sceneContainer.UpdateViewPort()



    def OnSetDevice(self):
        uthread.new(self.sr.sceneContainer.UpdateViewPort)



    def BuyType(self, typeID, *args):
        sm.GetService('store').TryBuyType(typeID)




