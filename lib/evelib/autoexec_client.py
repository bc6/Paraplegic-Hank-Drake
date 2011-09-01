import autoexec_client_core
import eveLog
import stackless
stackless.getcurrent().block_trap = True
appCacheDirs = ['Browser',
 'Browser/Img',
 'Map',
 'Pictures',
 'Pictures/Alliances',
 'Pictures/Gids',
 'Pictures/Planets',
 'Pictures/Portraits',
 'Pictures/Characters',
 'Pictures/Characters/Chat',
 'Pictures/Types',
 'Pictures/Blueprints',
 'Temp',
 'Temp/Mapbrowser',
 'Texture',
 'Texture/Planets',
 'Texture/Planets/Visited',
 'Shader',
 'Fonts']
userCacheDirs = ['/EVE/capture',
 '/EVE/capture/Screenshots',
 '/EVE/capture/Portraits',
 '/EVE/logs',
 '/EVE/logs/Chatlogs',
 '/EVE/logs/Gamelogs',
 '/EVE/logs/Marketlogs',
 '/EVE/logs/Fleetlogs']

def builtinSetupHook():
    import eve
    import base
    import __builtin__
    evetmp = eve.eve
    evetmp.session = __builtin__.session
    del eve
    __builtin__.eve = evetmp


servicesToRun = ['addressbook',
 'clientStatsSvc',
 'dataconfig',
 'godma',
 'photo',
 'machoNet',
 'mailSvc',
 'notificationSvc',
 'objectCaching',
 'LSC',
 'patch',
 'inv',
 'pwn',
 'focus',
 'debug',
 'jumpQueue',
 'scanSvc',
 'browserHostManager',
 'jumpMonitor',
 'calendar',
 'liveUpdateSvc',
 'monitor',
 'processHealth',
 'devToolsClient']
if prefs.GetValue('enableDust', 0):
    dustServices = ['dustFlashpointSvc']
    servicesToRun += dustServices
preUIStartArgProcessHook = None
StartupUIServiceName = 'gameui'
startInline = ['config',
 'DB',
 'machoNet',
 'objectCaching',
 'dataconfig',
 'dogmaIM',
 'device']
autoexec_client_core.StartClient(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline, serviceManagerClass='EveServiceManager')

