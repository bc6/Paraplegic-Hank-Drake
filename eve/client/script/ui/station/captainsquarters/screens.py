import blue
import trinity
import uicls
import uiconst
import uthread
import uiutil

def UpdateCQMainScreen(width, height, desktop, entityID):
    sm.GetService('holoscreen').OnMainScreenDesktopCreated(desktop, entityID)
    while True:
        blue.pyos.synchro.Sleep(1000)




def UpdatePIScreen(width, height, desktop, entityID):
    sm.GetService('holoscreen').OnPIScreenDesktopCreated(desktop, entityID)
    while True:
        blue.pyos.synchro.Sleep(1000)




def UpdateCorpFinderScreen(width, height, desktop, entityID):
    sm.GetService('holoscreen').OnCorpFinderScreenDesktopCreated(desktop, entityID)
    while True:
        blue.pyos.synchro.Sleep(1000)




def UpdateStationLogo(width, height, desktop, entityID):
    desktop.Flush()
    desktop.renderObject.backgroundColor = (0, 0, 0, 0)
    corpID = eve.stationItem.ownerID
    logo = uiutil.GetLogoIcon(itemID=corpID, parent=desktop, acceptNone=False, state=uiconst.UI_DISABLED, width=128, height=128, align=uiconst.CENTER)
    trinity.WaitForResourceLoads()
    desktop.UpdateAlignmentAsRoot()



def SetupCqMainScreen(paramString):
    if uicore.isRunning:
        return trinity.TriTextureRes()
    else:
        return blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/Screen_Center_Fallback.dds')



def SetupCqAgentFinderScreen(paramString):
    if uicore.isRunning:
        return trinity.TriTextureRes()
    else:
        return blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/Screen_Left_Fallback.dds')



def SetupCqPIScreen(paramString):
    if uicore.isRunning:
        return trinity.TriTextureRes()
    else:
        return blue.resMan.GetResource('res:/Graphics/Shared_Texture/Global/Screen_Right_Fallback.dds')



def SetupCqStationLogo(paramString):
    if uicore.isRunning:
        return trinity.TriTextureRes()
    else:
        return blue.resMan.GetResource('res:/UI/Texture/Corps/1_128_1.png')


LIVE_UPDATES = True
STATIC_IMAGE = False
AUTO_MIPMAP = True
NO_MIPMAPS = False
ARGB_FORMAT = trinity.TRIFORMAT.TRIFMT_A8R8G8B8
XRGB_FORMAT = trinity.TRIFORMAT.TRIFMT_X8R8G8B8
if blue.win32.IsTransgaming():
    AUTO_MIPMAP = False
CqMainScreen = (1280,
 720,
 XRGB_FORMAT,
 LIVE_UPDATES,
 AUTO_MIPMAP,
 UpdateCQMainScreen)
CqStationLogo = (256,
 256,
 ARGB_FORMAT,
 STATIC_IMAGE,
 AUTO_MIPMAP,
 UpdateStationLogo)
CqPIScreen = (540,
 720,
 XRGB_FORMAT,
 LIVE_UPDATES,
 AUTO_MIPMAP,
 UpdatePIScreen)
CqCorpFinderScreen = (540,
 720,
 XRGB_FORMAT,
 LIVE_UPDATES,
 AUTO_MIPMAP,
 UpdateCorpFinderScreen)
blue.resMan.RegisterResourceConstructor('CqMainScreen', SetupCqMainScreen)
blue.resMan.RegisterResourceConstructor('CqAgentFinderScreen', SetupCqAgentFinderScreen)
blue.resMan.RegisterResourceConstructor('cqpiscreen', SetupCqPIScreen)
blue.resMan.RegisterResourceConstructor('stationlogo', SetupCqStationLogo)
exports = {'screens.cqmainscreen': CqMainScreen,
 'screens.cqpiscreen': CqPIScreen,
 'screens.cqagentfinderscreen': CqCorpFinderScreen,
 'screens.stationlogo': CqStationLogo}

