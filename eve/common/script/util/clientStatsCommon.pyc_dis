#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/clientStatsCommon.py
import util
import blue
import collections
STATE_STARTUP = 1
STATE_LOGINWINDOW = 2
STATE_LOGINSTARTED = 4
STATE_LOGINDONE = 8
STATE_BULKDATASTARTED = 16
STATE_BULKDATADONE = 32
STATE_CHARSELECTION = 64
STATE_GAMEENTERED = 128
STATE_GAMEEXITING = 256
STATE_DISCONNECT = 512
STATE_GAMESHUTDOWN = 1024
STATE_UNINITIALIZEDSTART = 2048
STAT_PYTHONMEMORY = 0
STAT_MACHONET_AVG_PINGTIME = 1
STAT_CPU = 2
STAT_FATAL_DESYNCS = 3
STAT_RECOVERABLE_DESYNCS = 4
STAT_TIME_SINCE_LAST_STATE = 5
STAT_SAMPLE_SIZE = 6
SEC = 10000000L
MINUTE = 60L * SEC
HOUR = 60L * MINUTE
DAY = 24L * HOUR
MSEC = SEC / 1000L
PLATFORM_WINDOWS = 1
PLATFORM_MACOS = 2
PLATFORM_LINUX = 3
CONTENT_TYPE_CLASSIC = 1
CONTENT_TYPE_PREMIUM = 2
STATE_STRINGS = {1: 'Startup',
 2: 'Login Window Displayed',
 4: 'Login Initiated',
 8: 'Authenticated',
 16: 'Bulk Data Download Start',
 32: 'Bulk Data Download End',
 64: 'Character Selection',
 128: 'Game Entered',
 256: 'Game Exiting',
 512: 'Unexpected Server Disconnection',
 1024: 'Shutdown',
 2048: 'Uninitialized Start'}
SHORT_STATE_STRINGS = {1: 'Startup',
 2: 'Login Disp',
 4: 'Login Init',
 8: 'Authent',
 16: 'BDD Start',
 32: 'BDD End',
 64: 'Char Sel',
 128: 'Game Enter',
 256: 'Game Exit',
 512: 'Discon',
 1024: 'Shutdown',
 2048: 'Uninitialized'}

def ClientStatsDict():
    stats = collections.OrderedDict()
    stats['gpuVendorId'] = None
    stats['gpuDeviceId'] = None
    stats['gpuDriverVersion'] = None
    stats['osPlatform'] = None
    stats['osMajor'] = None
    stats['osMinor'] = None
    stats['osBuild'] = None
    stats['eveBuild'] = None
    stats['otherClients'] = None
    stats['windowed'] = None
    stats['deviceWidth'] = None
    stats['deviceHeight'] = None
    stats['presentInterval'] = None
    stats['hdr'] = None
    stats['antiAliasing'] = None
    stats['postProcessingQuality'] = None
    stats['shaderQuality'] = None
    stats['textureQuality'] = None
    stats['lodQuality'] = None
    stats['shadowQuality'] = None
    stats['interiorGraphicsQuality'] = None
    stats['interiorShaderQuality'] = None
    stats['audioEnabled'] = None
    stats['timeInState'] = None
    stats['memoryPython'] = None
    stats['memoryPythonPeak'] = None
    stats['memoryMalloc'] = None
    stats['memoryMallocPeak'] = None
    stats['memoryWorkingSet'] = None
    stats['memoryWorkingSetPeak'] = None
    stats['memoryPageFileUsage'] = None
    stats['memoryPageFileUsagePeak'] = None
    stats['frameTimeMean'] = None
    stats['frameTimeStdDev'] = None
    stats['frameTimePeak'] = None
    stats['shutdown'] = 0
    stats['loadObjectCalls'] = 0
    stats['loadObjectCacheHits'] = 0
    stats['loadObjectShared'] = 0
    stats['getResourceCalls'] = 0
    stats['getResourceCacheHits'] = 0
    stats['getResourceShared'] = 0
    stats['loadObject'] = 0
    stats['frameTimeAbove100ms'] = 0
    stats['frameTimeAbove200ms'] = 0
    stats['frameTimeAbove300ms'] = 0
    stats['frameTimeAbove400ms'] = 0
    stats['frameTimeAbove500ms'] = 0
    stats['browserRequests'] = 0
    return stats


exports = util.AutoExports('clientStatsCommon', locals())