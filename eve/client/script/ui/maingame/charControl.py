import uicls
import uiconst
import GameWorld
import util
import uthread
import uiutil
import geo2
import blue

class EveCharControl(uicls.CharControlCore):
    __guid__ = 'uicls.CharControl'

    def ApplyAttributes(self, *args, **kw):
        uicls.CharControlCore.ApplyAttributes(self, *args, **kw)
        self.entityID = None
        self.cameraClient = sm.GetService('cameraClient')
        self.mouseInputHandler = sm.GetService('mouseInput')
        self.contextMenuClient = sm.GetService('contextMenuClient')
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.navigation = sm.GetService('navigation')
        self.entityClient = sm.GetService('entityClient')
        self.entityClient.RegisterForSceneLifeCycle(self)
        self.loadingBackground = uicls.Container(name='loadingBackground', parent=self, bgColor=util.Color.BLACK, state=uiconst.UI_HIDDEN)
        self.bracketContainer = uicls.Container(name='bracketContainer', parent=self)
        self.bracketContainer.GetMenu = self.GetMenu



    def Startup(self):
        pass



    def OnOpenView(self):
        uicls.CharControlCore.OnOpenView(self)
        self.state = uiconst.UI_PICKCHILDREN
        sm.GetService('bracketClient').ReloadBrackets()
        self.ShowLoadingBackground()
        self.cameraClient.ResetLayerInfo()
        self.cameraClient.Enable()
        self.navigation.Reset()
        player = self.entityClient.GetPlayerEntity()
        if player is not None:
            player.animation.controller.Reset()



    def ShowLoadingBackground(self):
        blue.statistics.SetTimelineSectionName('loading')
        isLoadingScreen = prefs.GetValue('loadstationenv', 1)
        height = uicore.desktop.height
        width = 1.6 * height
        if isLoadingScreen:
            self.loadingText = uicls.Label(parent=self.loadingBackground, text=uiutil.UpperCase(mls.UI_GENERIC_LOADING), fontsize=50, align=uiconst.CENTER, top=100, color=util.Color.WHITE, glowFactor=1.0, glowColor=(1.0, 1.0, 1.0, 0.1))
            uicore.animations.FadeIn(self.loadingText)
            uicls.Sprite(name='aura', parent=self.loadingBackground, texturePath='res:/UI/Texture/Classes/CQLoadingScreen/loadingScreen.png', align=uiconst.CENTER, width=width, height=height)
        else:
            uicls.Sprite(name='aura', parent=self.loadingBackground, texturePath='res:/UI/Texture/Classes/CQLoadingScreen/IncarnaDisabled.png', align=uiconst.CENTER, width=width, height=height)
        uicore.animations.FadeIn(self.loadingBackground)
        self.loadingBackground.Show()
        self.loadingBackground.opacity = 1.0
        if isLoadingScreen:
            uthread.new(self.WaitForSceneToLoad)



    def WaitForSceneToLoad(self):
        uicore.animations.MorphScalar(self.loadingText, 'glowExpand', startVal=0.0, endVal=2.0, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        uicore.animations.MorphScalar(self.loadingText, 'opacity', startVal=0.0, endVal=1.0, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        playerEntity = sm.GetService('entityClient').GetPlayerEntity(canBlock=True)
        paperdoll = playerEntity.GetComponent('paperdoll')
        while paperdoll.doll.doll.busyUpdating:
            blue.synchro.Yield()

        sceneRj = sm.GetService('sceneManager').GetIncarnaRenderJob()
        if sm.GetService('sceneManager').secondarySceneContext is None:
            sceneRj.Enable()
        self.loadingText.StopAnimations()
        uicore.animations.BlinkOut(self.loadingText, sleep=True)
        uicore.animations.FadeOut(self.loadingBackground, duration=0.6, sleep=True)
        self.loadingBackground.Hide()
        self.loadingBackground.Flush()
        blue.statistics.SetTimelineSectionName('done loading')



    def OnCloseView(self):
        uicls.CharControlCore.OnCloseView(self)
        self.cameraClient.ResetLayerInfo()
        self.cameraClient.Disable()



    def OnMouseDown(self, button, *args):
        self.entityID = self._PickObject(uicore.uilib.x, uicore.uilib.y)
        self.mouseInputHandler.OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def OnMouseUp(self, button, *args):
        self.entityID = self._PickObject(uicore.uilib.x, uicore.uilib.y)
        self.mouseInputHandler.OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def GetMenu(self):
        self.contextMenuClient = sm.GetService('contextMenuClient')
        entityID = self._PickObject(uicore.uilib.x, uicore.uilib.y)
        if entityID:
            return self.contextMenuClient.GetMenuForEntityID(entityID)



    def OnMouseWheel(self, *args):
        self.mouseInputHandler.OnMouseWheel(uicore.uilib.dz)



    def OnMouseMove(self, *args):
        self.mouseInputHandler.OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entityID)



    def OnClick(self, *args):
        pass



    def OnDblClick(self, *args):
        self.mouseInputHandler.OnDoubleClick(self.entityID)



    def _PickObject(self, x, y):
        if not isinstance(self.parent, uicls.CharControl):
            return 
        else:
            if not self.gameWorldClient.HasGameWorld(session.worldspaceid):
                return 
            gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
            if gameWorld is None:
                return 
            (startPoint, endPoint,) = self.cameraClient.GetActiveCamera().GetRay(x, y)
            collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
            p = gameWorld.LineTestEntId(startPoint, endPoint, session.charid, collisionGroups)
            if p is not None:
                return p[2]
            return p



    def OverridePick(self, x, y):
        overrideObject = None
        entityID = self._PickObject(x, y)
        if entityID:
            entity = sm.GetService('entityClient').FindEntityByID(entityID)
            if entity.HasComponent('UIDesktopComponent') and entity.HasComponent('uvPicking'):
                (startPoint, endPoint,) = self.cameraClient.GetActiveCamera().GetRay(x, y)
                direction = geo2.Subtract(endPoint, startPoint)
                uv = sm.GetService('uvPickingClient').Pick(entity, startPoint, direction)
                if uv:
                    desktopComponent = entity.GetComponent('UIDesktopComponent')
                    desktop = desktopComponent.uiDesktop
                    u = int(uv[0] * desktop.width)
                    v = int(uv[1] * desktop.height)
                    triobj = desktopComponent.uiDesktop.renderObject.PickObject(u, v, None, None, None)
                    if triobj:
                        overrideObject = uicore.uilib.GetPyObjectFromRenderObject(triobj)
        return overrideObject




