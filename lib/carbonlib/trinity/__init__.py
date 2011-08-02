import blue
args = blue.pyos.GetArg()
if boot.role in ('server', 'proxy') and '/jessica' not in args and '/minime' not in args:
    raise RuntimeError("Don't import trinity on the proxy or server")
import blue.win32
import bluepy
import sys
import os
import log
import yaml
D3DX_FILENAME = 'd3dx9_42.dll'
D3DCOMPILER_FILENAME = 'd3dcompiler_42.dll'

def GetEnumValueName(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for (enumKeyName, (enumKeyValue, enumKeydocString,),) in enum.values.iteritems():
            if enumKeyValue == value:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result



def GetEnumValueNameAsBitMask(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for (enumKeyName, (enumKeyValue, enumKeydocString,),) in enum.values.iteritems():
            if enumKeyValue & value == enumKeyValue:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result



def ConvertTriFileToGranny(path):
    helper = TriGeometryRes()
    return helper.ConvertTriFileToGranny(path)



def Load(path, nonCached = False):
    if nonCached:
        blue.motherLode.Delete(path)
    obj = blue.os.LoadObject(path)
    return obj



def LoadDone(evt):
    evt.isDone = True



def WaitForResourceLoads():
    blue.resMan.Wait()



def WaitForUrgentResourceLoads():
    blue.resMan.WaitUrgent()



def LoadUrgent(path):
    blue.resMan.SetUrgentResourceLoads(True)
    obj = Load(path)
    blue.resMan.SetUrgentResourceLoads(False)
    return obj



def GetResourceUrgent(path, extra = ''):
    blue.resMan.SetUrgentResourceLoads(True)
    obj = blue.resMan.GetResource(path, extra)
    blue.resMan.SetUrgentResourceLoads(False)
    return obj



def Save(obj, path):
    blue.motherLode.Delete(path)
    if path.endswith('.red'):
        return blue.os.SaveObject(obj, path)
    else:
        return obj.SaveTo(path)



def SavePurple(obj, path):
    blue.motherLode.Delete(path)
    blue.os.SaveObject(obj, path)



def GetD3DXVersion():
    return GetFileVersionWow64(D3DX_FILENAME)



def GetD3DCompilerVersion():
    return GetFileVersionWow64(D3DCOMPILER_FILENAME)



def PlayBinkVideo(path):
    effect = Tr2Effect()
    effect.effectFilePath = 'res:/Effect/Post_Bink.fxo'
    effect.technique = 'Main'
    r = TriTextureBinkParameter()
    r.name = 'video'
    player = TriBinkPlayer()
    r.resource = player
    player.resourcePath = path
    effect.resources.append(r)
    device.videoOverlayEffect = effect
    player.Play()
    return (effect, player)



def IsDXVersionOK():
    musthave = (9, 0, 'c')
    ver = GetDXVersion()
    if ver < musthave:
        (major, minor, letter,) = ver
        (major2, minor2, letter2,) = musthave
        msg = 'DirectX %s.%s%s detected but this application needs %s.%s%s.\r\n'
        msg += 'Click Yes to continue, but the application may not run.\r\n'
        msg += 'Click No to go to support web page where you can download the '
        msg += 'latest DirectX runtime files.'
        msg = mls.TRINITY_DX_OUTDATED_MSG % {'currMajor': major,
         'currMinor': minor,
         'currLetter': letter,
         'reqMajor': major2,
         'reqMinor': minor2,
         'reqLetter': letter2}
        ret = blue.win32.MessageBox(msg, mls.TRINITY_DX_OUTDATED_TITLE, 4132)
        if ret == 6:
            return True
        url = 'http://www.eveonline.com/directx'
        url += '?dxversion=%s.%s%s' % (major, minor, letter)
        url += '&' + GetVersionArg()
        blue.os.ShellExecute(url)
        blue.pyos.Quit('DirectX version check failed.')
        return False
    return True



def GetFileVersion(f):
    sysdir = blue.win32.GetSystemDirectory()
    try:
        vi = blue.win32.GetFileVersionInfo(sysdir + '\\' + f)
        return vi['\\']['FileVersion']
    except:
        sys.exc_clear()
        return None



def GetFileVersionWow64(f):
    sysdir = blue.win32.GetSystemDirectory()
    if blue.win32.IsWow64Process():
        sysdir = blue.win32.GetSystemWow64Directory()
    try:
        vi = blue.win32.GetFileVersionInfo(sysdir + '\\' + f)
        return vi['\\']['FileVersion']
    except:
        sys.exc_clear()
        return None



def Long(a, b, c, d):
    return long(a) << 48 | long(b) << 32 | long(c) << 16 | long(d)



def Hiword(l):
    return l >> 48



def GetDXVersion():
    sysdir = blue.win32.GetSystemDirectory()
    ver = ()
    ddraw = GetFileVersion('ddraw.dll')
    if ddraw:
        if ddraw >= Long(4, 2, 0, 95):
            ver = (1, 0, '')
        if ddraw >= Long(4, 3, 0, 1096):
            ver = (2, 0, '')
        if ddraw >= Long(4, 4, 0, 68):
            ver = (3, 0, '')
    d3drg8 = GetFileVersion('d3drg8x.dll')
    if d3drg8:
        if d3drg8 >= Long(4, 4, 0, 70):
            ver = (3, 0, 'a')
    if ddraw:
        if ddraw >= Long(4, 5, 0, 155):
            ver = (5, 0, '')
        if ddraw >= Long(4, 6, 0, 318):
            ver = (6, 0, '')
        if ddraw >= Long(4, 6, 0, 436):
            ver = (6, 1, '')
    dplayx = GetFileVersion('dplayx.dll')
    if dplayx:
        if dplayx >= Long(4, 6, 3, 518):
            ver = (6, 1, 'a')
    if ddraw:
        if ddraw >= Long(4, 7, 0, 700):
            ver = (7, 0, '')
    dinput = GetFileVersion('dinput.dll')
    if dinput:
        if dinput >= Long(4, 7, 0, 716):
            ver = (7, 0, 'a')
    if ddraw:
        if Hiword(ddraw) == 4 and ddraw >= Long(4, 8, 0, 400):
            ver = (8, 0, '')
        if Hiword(ddraw) == 5 and ddraw >= Long(5, 1, 2258, 400):
            ver = (8, 0, '')
    d3d8 = GetFileVersion('d3d8.dll')
    if d3d8:
        if Hiword(d3d8) == 4 and d3d8 >= Long(4, 8, 1, 881):
            ver = (8, 1, '')
        if Hiword(d3d8) == 5 and d3d8 >= Long(5, 1, 2600, 881):
            ver = (8, 1, '')
        if Hiword(d3d8) == 4 and d3d8 >= Long(4, 8, 1, 901):
            ver = (8, 1, 'a')
        if Hiword(d3d8) == 5 and d3d8 >= Long(5, 1, 2600, 901):
            ver = (8, 1, 'a')
    mpg2splt = GetFileVersion('mpg2splt.ax')
    if mpg2splt:
        if mpg2splt >= Long(6, 3, 1, 885):
            ver = (8, 1, 'b')
    dpnet = GetFileVersion('dpnet.dll')
    if dpnet:
        if Hiword(dpnet) == 4 and dpnet >= Long(4, 9, 0, 134):
            ver = (8, 2, '')
        if Hiword(dpnet) == 5 and dpnet >= Long(5, 2, 3677, 901):
            ver = (8, 2, '')
    d3d9 = GetFileVersion('d3d9.dll')
    if d3d9:
        ver = (9, 0, '')
        if Hiword(d3d9) == 4 and d3d9 >= Long(4, 9, 0, 902):
            ver = (9, 0, 'b')
        if Hiword(d3d9) == 5 and d3d9 >= Long(5, 3, 1, 902):
            ver = (9, 0, 'b')
        if Hiword(d3d9) == 4 and d3d9 >= Long(4, 9, 0, 904):
            ver = (9, 0, 'c')
        if Hiword(d3d9) == 5 and d3d9 >= Long(5, 3, 1, 904):
            ver = (9, 0, 'c')
        if Hiword(d3d9) == 6:
            ver = (9, 0, 'c')
    return ver



def EnsureD3DXVersion():
    d3dx9 = GetD3DXVersion()
    d3dcompiler = GetD3DCompilerVersion()
    if d3dx9 == None or d3dcompiler == None:
        installMsg = 'Installing D3DX ...'
        print installMsg
        log.general.Log(installMsg)
        oldDir = os.getcwdu()
        os.chdir(blue.os.binpath)
        dxSetupCmd = 'RedistD3DXOnly.exe'
        exit_status = os.system(dxSetupCmd)
        os.chdir(oldDir)
        retString = 'command -> exit_status : ' + dxSetupCmd + ' -> ' + str(exit_status)
        if exit_status:
            log.general.Log(retString, log.LGERR)
        else:
            log.general.Log(retString)
        if GetD3DXVersion() == None:
            ret = blue.win32.MessageBox(mls.TRINITY_D3DX_NOTFOUND_MSG2 % {'pathName': D3DX_FILENAME}, mls.TRINITY_D3DX_NOTFOUND_TITLE2, 4132)
            if ret == 6:
                return True
            blue.pyos.Quit('D3DX version check failed.')
            return False
    return True



def GetVersionArg():
    try:
        buildno = '%s.%s' % (boot.keyval['version'].split('=', 1)[1], boot.build)
    except:
        try:
            buildno = str(boot.build)
        except:
            buildno = '501'
        sys.exc_clear()
    return 'buildno=' + buildno


skipChecksForDX = blue.pyos.packaged or blue.win32.IsTransgaming()
if skipChecksForDX or IsDXVersionOK() and EnsureD3DXVersion():
    args = blue.pyos.GetArg()
    dev = None
    nvperfhud = None
    trinitymem = None
    rightHanded = None
    deploy = None
    for arg in args:
        if arg.startswith('/trinitydeploy'):
            deploy = 1
        if arg.startswith('/trinitydev'):
            dev = 1
            if ':' in arg:
                dev = int(arg.split(':')[1])
        if arg == '/nvperfhud':
            nvperfhud = 1
        if arg == '/trinitymem':
            trinitymem = 1
        if arg == '/righthanded':
            rightHanded = True
    else:
        if boot.keyval.get('trinitydev', None):
            dev = int(boot.keyval['trinitydev'].split('=', 1)[1])

    if dev not in (None, 9, 10):
        dev = 9
    if blue.pyos.packaged or deploy:
        try:
            print 'Starting up Trinity through _trinity_deploy.dll ...'
            from _trinity_deploy import *
        except ImportError:
            print 'Falling back to _trinity.dll'
            from _trinity import *
    elif dev:
        print 'Starting up Trinity through _trinity_dev%s.dll ...' % dev
        try:
            if dev == 10:
                from _trinity_dev10 import *
            else:
                from _trinity_dev9 import *
            print 'Success!'
        except ImportError:
            print 'not found, fallback to _trinity'
            from _trinity import *
    if nvperfhud:
        print 'Starting up Trinity through _trinity_nvperfhud.dll ...'
        try:
            from _trinity_nvperfhud import *
            print 'Success - profiling with NVPerfHUD should now work'
        except ImportError:
            print 'not found, fallback to _trinity'
            from _trinity import *
    elif trinitymem:
        print 'Starting up Trinity through _trinity_dev9_mem.dll ...'
        try:
            from _trinity_dev9_mem import *
            print 'Success - memory tracking now enabled'
        except ImportError:
            print 'not found, fallback to _trinity'
            from _trinity import *
    else:
        from _trinity import *
if rightHanded:
    SetRightHanded(True)
    settings.SetValue('geometryResNormalizeOnLoad', True)
    print 'Trinity is using a right-handed coordinate system'

def GetDevice():
    return blue.rot.GetInstance('tri:/dev', 'trinity.TriDevice')


device = GetDevice()

def GetDirect3D():
    return blue.rot.GetInstance('tri:/Direct3D', 'trinity.TriDirect3D')


d3d = GetDirect3D()
app = blue.rot.GetInstance('app:/App', 'triui.App')
if hasattr(blue, 'CcpStatistics'):
    statistics = blue.CcpStatistics()

def TriSurfaceManaged(method, *args):

    def Create():
        return method(*args)


    surface = Create()
    surface.prepareCallback = Create
    return surface


from trinity.renderJob import CreateRenderJob
from trinity.renderJobUtils import *

def IsFpsEnabled():
    return bool('FPS' in (j.name for j in device.scheduledRecurring))



def SetFpsEnabled(enable, viewPort = None):
    if enable:
        if IsFpsEnabled():
            return 
        fpsJob = CreateRenderJob('FPS')
        fpsJob.SetViewport(viewPort)
        fpsJob.RenderFps()
        fpsJob.ScheduleRecurring(insertFront=False)
    else:
        for job in device.scheduledRecurring:
            if job.name == 'FPS':
                device.scheduledRecurring.remove(job)




def AddRenderJobText(text, x, y, renderJob, color = 4278255360L):
    steps = [ step for step in renderJob.steps if step.name == 'RenderDebug' ]
    step = None
    if len(steps) > 0:
        step = steps[0]
    else:
        return 
    step.Print2D(x, y, color, text)
    return renderJob



def CreateDebugRenderJob(renderJobName, viewPort, renderJobIndex = -1):
    renderJob = trinity.CreateRenderJob(renderJobName)
    renderJob.SetViewport(viewPort)
    step = renderJob.RenderDebug()
    step.name = 'RenderDebug'
    step.autoClear = False
    if renderJobIndex is -1:
        renderJob.ScheduleRecurring()
    else:
        trinity.device.scheduledRecurring.insert(renderJobIndex, renderJob)
    return renderJob


from trinity.GraphManager import GraphManager
graphs = GraphManager()

def SetupDefaultGraphs():
    graphs.Clear()
    graphs.AddGraph('frameTime')
    graphs.AddGraph('devicePresent')
    graphs.AddGraph('primitiveCount')
    graphs.AddGraph('batchCount')
    graphs.AddGraph('pendingLoads')
    graphs.AddGraph('pendingPrepares')
    graphs.AddGraph('textureResBytes')



def AddFrameTimeMarker(name):
    line = GetLineGraphFrameTime()
    if line is not None:
        line.AddMarker(name)



class FrameTimeMarkerStopwatch(object):

    def __init__(self, stopwatchName):
        self.started = blue.os.GetCycles()[0]
        self.stopwatchName = stopwatchName



    def __str__(self):
        return '%s %i ms' % (self.stopwatchName, int(1000 * ((blue.os.GetCycles()[0] - self.started) / float(blue.os.GetCycles()[1]))))



    def __del__(self):
        AddFrameTimeMarker(str(self))




def CreateBinding(cs, src, srcAttr, dst, dstAttr):
    binding = TriValueBinding()
    binding.sourceObject = src
    binding.sourceAttribute = srcAttr
    binding.destinationObject = dst
    binding.destinationAttribute = dstAttr
    if cs:
        cs.bindings.append(binding)
    return binding



def CreatePythonBinding(cs, src, srcAttr, dst, dstAttr):
    binding = Tr2PyValueBinding()
    binding.sourceObject = src
    binding.sourceAttribute = srcAttr
    binding.destinationObject = dst
    binding.destinationAttribute = dstAttr
    if cs:
        cs.bindings.append(binding)
    return binding


if not blue.pyos.packaged:
    SetFpsEnabled(True)
if blue.win32.IsTransgaming():
    settings.SetValue('strictShaderCompilation', True)
shaderManager = GetShaderManager()
for (path, dirs, files,) in bluepy.walk('res:/Graphics/Shaders/ShaderDescriptions'):
    for f in files:
        filepath = path + '/' + f
        if filepath.endswith('.red'):
            highLevelShader = Load(filepath)
            if highLevelShader is not None:
                try:
                    shaderManager.shaderLibrary.append(highLevelShader)
                except blue.error as e:
                    log.general.Log('Exception loading High Level Shader: %s' % filepath, log.LGERR)
                    log.LogException()
                    sys.exc_clear()
            else:
                log.general.Log('Unable to find shader library object: %s' % filepath, log.LGERR)



