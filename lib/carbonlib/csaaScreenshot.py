import trinity

def csaaScreenshot(useNVidiaAA, width, height, scene):
    try:
        csaaFmt = trinity.TRIMULTISAMPLE_8_SAMPLES if useNVidiaAA else trinity.TRIMULTISAMPLE_NONE
        csaaQty = 2 if useNVidiaAA else 0
        buffer = trinity.device.CreateRenderTarget(width, height, trinity.TRIFMT_X8R8G8B8, csaaFmt, csaaQty, False)
        depth = trinity.device.CreateDepthStencilSurface(width, height, trinity.TRIFMT_D24S8, csaaFmt, csaaQty, False)
        job = trinity.CreateRenderJob('CSAA screenshot')
        job.SetRenderTarget(buffer)
        job.SetDepthStencil(depth)
        vp = trinity.TriViewport()
        vp.x = 0
        vp.y = 0
        vp.width = width
        vp.height = height
        job.SetViewport(vp)
        job.Clear((0, 0, 0, 0), 1.0)
        job.RenderScene(scene)
        trinity.SetPerspectiveProjection(trinity.GetFieldOfView(), trinity.GetFrontClip(), trinity.GetBackClip(), 1.0)
        job.ScheduleOnce()
        return (job, buffer)
    except Exception:
        return None



