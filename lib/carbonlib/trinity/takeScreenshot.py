import wx
import trinity
import math
import os
from trinity.sceneRenderJobBase import SceneRenderJobBase
oldProjections = {}
oldViewports = {}
noSetProjectionRjList = []
noSetViewportRjList = []

def GetProjection(rj):
    if hasattr(rj, 'GetCameraProjection'):
        proj = rj.GetCameraProjection()
        if proj is not None:
            proj = proj.object
            if proj is not None:
                return proj
    if hasattr(rj, 'GetStep'):
        projStep = rj.GetStep('SET_PROJECTION')
        if projStep is not None:
            if projStep.projection is not None:
                return projStep.projection
    for step in rj.steps:
        if type(step) is trinity.TriStepRunJob:
            if step is not None and step.job is not None:
                for step2 in step.job.steps:
                    if step2.name == 'SET_PROJECTION':
                        if step2.projection is not None:
                            return step2.projection


    noSetProjectionRjList.append(rj)



def GetViewport(rj):
    if hasattr(rj, 'GetViewport'):
        vp = rj.GetViewport()
        if vp is not None:
            vp = vp.object
            if vp is not None:
                return vp
    if hasattr(rj, 'GetStep'):
        vpStep = rj.GetStep('SET_VIEWPORT')
        if vpStep is not None:
            if vpStep.viewport is not None:
                return vpStep.viewport
    for step in rj.steps:
        if type(step) is trinity.TriStepRunJob:
            if step is not None and step.job is not None:
                for step2 in step.job.steps:
                    if step2.name == 'SET_VIEWPORT':
                        if step2.viewport is not None:
                            return step2.viewport


    noSetViewportRjList.append(rj)



def SetProjection(rj, newProj):
    if hasattr(rj, 'CallMethodOnChildren'):
        rj.CallMethodOnChildren('SetCameraProjection', newProj)
        rj.CallMethodOnChildren('AddStep', 'SET_PROJECTION', trinity.TriStepSetProjection(newProj))
        return 
    if hasattr(rj, 'GetStep'):
        projStep = rj.GetStep('SET_PROJECTION')
        if projStep is not None:
            projStep.projection = newProj
        else:
            rj.SetCameraProjection(newProj)



def SetViewport(rj, newVP):
    if hasattr(rj, 'CallMethodOnChildren'):
        rj.CallMethodOnChildren('AddStep', 'SET_VIEWPORT', trinity.TriStepSetViewport(newVP))
        return 
    if hasattr(rj, 'GetStep'):
        vpStep = rj.GetStep('SET_VIEWPORT')
        if vpStep is not None:
            vpStep.viewport = newVP
        else:
            print rj.__klass__
            rj.SetViewport(newVP)



def BackupAllProjectionsAndViewports(rjList):
    global oldViewports
    global oldProjections
    for rj in rjList:
        oldProjections[rj] = GetProjection(rj)
        oldViewports[rj] = GetViewport(rj)




def RestoreAllProjectionsAndViewports():
    for (rj, projection,) in oldProjections.iteritems():
        SetProjection(rj, projection)

    for rj in noSetProjectionRjList:
        rj.SetCameraProjection(None)

    for (rj, viewport,) in oldViewports.iteritems():
        SetViewport(rj, viewport)

    for rj in noSetViewportRjList:
        rj.SetViewport(None)




def OverrideAllProjectionsAndViewports(rjList, newProj, newVP):
    for rj in rjList:
        SetProjection(rj, newProj)
        SetViewport(rj, newVP)




def TakeScreenshot(filename, tilesAcross):
    successful = False
    performanceOverlayRJ = 0
    dev = trinity.device
    fov = trinity.GetFieldOfView()
    aspect = trinity.GetAspectRatio()
    zNear = trinity.GetFrontClip()
    zFar = trinity.GetBackClip()
    height = 2.0 * zNear * math.tan(fov / 2.0)
    width = height * aspect
    disabledJobsStates = {}
    sceneRenderJobs = []
    for rj in dev.scheduledRecurring:
        if SceneRenderJobBase in rj.__bases__:
            sceneRenderJobs.append(rj)
        else:
            disabledJobsStates[rj] = rj.enabled
            rj.enabled = False

    BackupAllProjectionsAndViewports(sceneRenderJobs)
    try:
        if filename == None or filename == '':
            raise ValueError('No filename given')
        if not tilesAcross or tilesAcross == 0:
            raise ValueError('tilesAcross must be greater than 0')
        basefilename = filename[:-4]
        tilesAcross = int(tilesAcross)
        heightSlice = height / tilesAcross
        widthSlice = width / tilesAcross
        backBuffer = dev.GetBackBuffer(0)
        tileWidth = backBuffer.width
        tileHeight = backBuffer.height
        twd4 = math.floor(tileWidth / 4)
        thd4 = math.floor(tileHeight / 4)
        diffW = tileWidth - twd4 * 4
        diffH = tileHeight - thd4 * 4
        backBufferSys = dev.CreateOffscreenPlainSurface(tileWidth, tileHeight, backBuffer.format, trinity.TRIPOOL_SYSTEMMEM)
        screenShot = dev.CreateOffscreenPlainSurface(tileWidth * tilesAcross, tileHeight * tilesAcross, backBuffer.format, trinity.TRIPOOL_SYSTEMMEM)
        info = wx.BusyInfo('Hold on, generating snazzy snapshot ...')
        tileOffset = trinity.TriPoint()
        halfAcross = tilesAcross / 2.0
        for x in range(tilesAcross):
            left = (x - halfAcross) * widthSlice
            right = left + widthSlice
            tileOffset.x = x * tileWidth
            for y in range(tilesAcross):
                top = (halfAcross - y) * heightSlice
                bottom = top - heightSlice
                tileOffset.y = y * tileHeight
                for x_off in [(-widthSlice / 4, -twd4, 0), (widthSlice / 4, twd4, diffW)]:
                    for y_off in [(heightSlice / 4, -thd4, 0), (-heightSlice / 4, thd4, diffH)]:
                        newProj = trinity.TriProjection()
                        newProj.PerspectiveOffCenter(left + x_off[0], right + x_off[0], bottom + y_off[0], top + y_off[0], zNear, zFar)
                        newViewport = trinity.TriViewport()
                        newViewport.x = 0
                        newViewport.y = 0
                        newViewport.width = tileWidth
                        newViewport.height = tileHeight
                        newViewport.minZ = 0.0
                        newViewport.maxZ = 1.0
                        OverrideAllProjectionsAndViewports(sceneRenderJobs, newProj, newViewport)
                        dev.Render()
                        dev.Render()
                        dev.GetRenderTargetData(backBuffer, backBufferSys)
                        offset = trinity.TriPoint(int(x_off[1] + tileOffset.x), int(y_off[1] + tileOffset.y))
                        rect = trinity.TriRect(int(twd4), int(thd4), int(3 * twd4 + x_off[2]), int(3 * thd4 + y_off[2]))
                        dev.UpdateSurface(backBufferSys, rect, screenShot, offset)



            RestoreAllProjectionsAndViewports()

        baseDir = os.path.dirname(filename)
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
        screenShot.SaveSurfaceToFile(basefilename + '.bmp', trinity.TRIIFF_BMP)
        del info
        successful = True
    except Exception:
        import traceback
        traceback.print_exc()
    for (rj, state,) in disabledJobsStates.iteritems():
        rj.enabled = state

    return successful



