import trinity
import blue
import bluepy
import ctypes
import math
import time
import geo2
import struct
import itertools
import weakref
import uthread
import paperDoll as PD
import log
import random

class SkinRaytracing():
    __guid__ = 'paperDoll.SkinRaytracing'

    def printMem(self, str):
        print str,
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'



    def __init__(self, ptxFolder, width, height):
        log.LogInfo('[Optix] init')
        optix = trinity.Tr2Optix()
        self.optix = optix
        self.printMem('')
        optix.SetRayTypeCount(1)
        optix.SetEntryPointCount(2)
        optix.SetPrintEnabled(True)
        optix.SetPrintBufferSize(4096)
        optix.SetInteropDevice()
        optix.SetUInt('shadow_ray_type', 0)
        optix.SetUInt('radiance_ray_type', 0)
        optix.SetFloat('scene_epsilon', 0.001)
        optix.SetFloat3('light_pos', 0, 3.6, 1.0)
        if trinity.device.scene2 is not None:
            self.createScene(optix, ptxFolder)
        view = trinity.GetViewPosition()
        log.LogInfo('[Optix] setting eye pos to', view)
        optix.SetFloat3('eye_pos', view[0], view[1], view[2])
        raygen = trinity.Tr2OptixProgram(ptxFolder + '/skin_diffuse_ray_request.ptx', 'ray_request')
        optix.SetRayGenerationProgram(0, raygen)
        raygen_spec = trinity.Tr2OptixProgram(ptxFolder + '/skin_diffuse_ray_request.ptx', 'ray_request_spec')
        optix.SetRayGenerationProgram(1, raygen_spec)
        miss = trinity.Tr2OptixProgram(ptxFolder + '/constantbg.ptx', 'miss')
        optix.SetMissProgram(0, miss)
        optix.SetFloat3('bg_color', 1.0, 0, 0)
        optix.SetExceptionProgram(0, trinity.Tr2OptixProgram(ptxFolder + '/constantbg.ptx', 'exception'))
        optix.SetStackSize(2048)
        self.width = width
        self.height = height
        self.bbWidth = trinity.device.GetBackBuffer().width
        self.bbHeight = trinity.device.GetBackBuffer().height
        bufDiffuseLight = trinity.Tr2OptixBuffer()
        bufDiffuseLight.CreateUChar4(self.width, self.height, trinity.OPTIX_BUFFER_INPUT)
        optix.SetBuffer('shadow_buffer', bufDiffuseLight)
        bufSpecularLight = trinity.Tr2OptixBuffer()
        bufSpecularLight.CreateUChar4(self.bbWidth, self.bbHeight, trinity.OPTIX_BUFFER_INPUT)
        self.optix = optix
        self.bufDiffuseLight = bufDiffuseLight
        self.bufSpecularLight = bufSpecularLight



    def __del__(self):
        del self.optix
        del self.bufDiffuseLight
        del self.bufSpecularLight



    @staticmethod
    def SetOptixMatrixFromTrinity(optix, matrixName):
        proj = trinity.TriProjection()
        view = trinity.TriView()
        view.transform = trinity.GetViewTransform()
        proj.PerspectiveFov(trinity.GetFieldOfView(), trinity.GetAspectRatio(), trinity.GetFrontClip(), trinity.GetBackClip())
        projToView = geo2.MatrixInverse(proj.transform)
        viewToWorld = geo2.MatrixInverse(view.transform)
        projToWorld = geo2.MatrixMultiply(projToView, viewToWorld)
        r0 = projToWorld[0]
        r1 = projToWorld[1]
        r2 = projToWorld[2]
        r3 = projToWorld[3]
        mat = trinity.TriMatrix(r0[0], r0[1], r0[2], r0[3], r1[0], r1[1], r1[2], r1[3], r2[0], r2[1], r2[2], r2[3], r3[0], r3[1], r3[2], r3[3])
        optix.SetMatrix4x4(matrixName, mat)
        r0 = view.transform[0]
        r1 = view.transform[1]
        r2 = view.transform[2]
        r3 = view.transform[3]
        mat = trinity.TriMatrix(r0[0], r0[1], r0[2], r0[3], r1[0], r1[1], r1[2], r1[3], r2[0], r2[1], r2[2], r2[3], r3[0], r3[1], r3[2], r3[3])
        optix.SetMatrix4x4('viewTransform', mat)
        return mat



    @staticmethod
    def CreateSamplerForTexture(name, map, waitForFinish):
        rt = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, map.width, map.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, True)
        job = trinity.CreateRenderJob()
        job.PushRenderTarget(rt)
        job.PushDepthStencil(None)
        vp = trinity.TriViewport()
        vp.x = 0
        vp.y = 0
        vp.width = map.width
        vp.height = map.height
        job.SetViewport(vp)
        job.SetStdRndStates(trinity.RM_FULLSCREEN)
        job.RenderTexture(map)
        job.PopDepthStencil()
        job.PopRenderTarget()
        job.ScheduleOnce()
        if waitForFinish:
            job.WaitForFinish()
        sampler = trinity.Tr2OptixTextureSampler()
        sampler.CreateFromSurface(rt)
        sampler.SetNormalizedIndexingMode(True)
        if False:
            rdesc = rt.GetDesc()
            surface = trinity.TriSurfaceManaged(trinity.device.CreateOffscreenPlainSurface, rdesc['Width'], rdesc['Height'], rdesc['Format'], trinity.TRIPOOL_SYSTEMMEM)
            trinity.device.GetRenderTargetData(rt, surface)
            surface.SaveSurfaceToFile('c:/depot/interop' + name + '.dds')
        return (sampler, rt)



    @staticmethod
    def FindAllTextureResources(dynamic):
        d = {}
        for mesh in dynamic.visualModel.meshes:
            for area in itertools.chain(mesh.opaqueAreas, mesh.decalAreas, mesh.transparentAreas):
                if area.effect:
                    for r in area.effect.resources:
                        if type(r) == trinity.TriTexture2DParameter and r.resource is not None:
                            d[r.name] = r.resource
                        elif type(r) == trinity.TriTextureCubeParameter and r.resource is not None:
                            log.LogInfo('[Optix] ', r.name, ': Optix does not support CubeMaps yet, sorry :(')



        return d



    @staticmethod
    def InteropTexture(optix, name, texture, waitForFinish):
        if texture.pool == trinity.TRIPOOL_DEFAULT and texture.format == trinity.TRIFMT_A8R8G8B8:
            sampler = trinity.Tr2OptixTextureSampler()
            sampler.CreateFromTexture(texture)
            sampler.SetNormalizedIndexingMode(True)
            optix.SetSampler(name, sampler)
            log.LogInfo('[Optix] No-Copy Interop for', name)
            return (sampler, None)
        if texture.type == trinity.TRIRTYPE_CUBETEXTURE:
            log.LogInfo('[Optix] Copy-Interop for cubes not supported, skipping', name)
            return 
        sampler_rt = SkinRaytracing.CreateSamplerForTexture(name, texture, waitForFinish)
        if sampler_rt is None or len(sampler_rt) < 1:
            log.LogInfo('[Optix] InteropTexture failed for', name)
        else:
            optix.SetSampler(name, sampler_rt[0])
            log.LogInfo('[Optix] Interop for', name)
        return sampler_rt



    @staticmethod
    def InteropAllTextures(optix, dynamic, waitForFinish):
        d = SkinRaytracing.FindAllTextureResources(dynamic)
        samplers = []
        for (name, texture,) in d.iteritems():
            sampler = SkinRaytracing.InteropTexture(optix, name, texture, waitForFinish)
            if sampler is not None:
                samplers.append(sampler)

        return samplers



    @staticmethod
    def CopyParametersToContext(effect, instance):
        for p in effect.parameters:
            if type(p) is trinity.Tr2Vector4Parameter:
                instance.SetFloat4(p.name, p.value[0], p.value[1], p.value[2], p.value[3])
            elif type(p) is trinity.TriFloatParameter:
                instance.SetFloat4(p.name, p.value, 0, 0, 0)




    @staticmethod
    def CreateBufferForLights(scene):
        lights = scene.lights
        bufEveLights = trinity.Tr2OptixBuffer()
        bufEveLights.CreateUserData(64, len(lights), trinity.OPTIX_BUFFER_OUTPUT, False)
        bufEveLights.MapUser()
        buffer = ''
        for light in lights:
            innerAngle = light.coneAlphaInner
            outerAngle = light.coneAlphaOuter
            if innerAngle + 1.0 > outerAngle:
                innerAngle = outerAngle - 1.0
            innerAngle = math.cos(innerAngle * 3.1415927 / 180.0)
            outerAngle = math.cos(outerAngle * 3.1415927 / 180.0)
            coneDir = geo2.Vec3Normalize((light.coneDirection[0], light.coneDirection[1], light.coneDirection[2]))
            import struct
            buffer += struct.pack('16f', light.position[0], light.position[1], light.position[2], light.radius, math.pow(light.color[0], 2.2), math.pow(light.color[1], 2.2), math.pow(light.color[2], 2.2), light.falloff, coneDir[0], coneDir[1], coneDir[2], outerAngle, innerAngle, 0, 0, 0)

        bufEveLights.SetUserDataFromStruct(buffer)
        bufEveLights.UnmapUser()
        return bufEveLights



    def createScene(self, optix, ptxFolder):
        self.printMem('[Optix] before createScene')
        any_hit_shader = trinity.Tr2OptixProgram(ptxFolder + '/eve_shadow.ptx', 'any_hit_shadow')
        any_hit_material = trinity.Tr2OptixMaterial()
        any_hit_material.SetAnyHit(0, any_hit_shader)
        bufEveLights = self.CreateBufferForLights(trinity.device.scene2.lights)
        optix.SetBuffer('eve_lights', bufEveLights)
        vertex_buffer = trinity.Tr2OptixBuffer()
        index_buffer = trinity.Tr2OptixBuffer()
        vertex_count = 0
        index_count = 0
        if False:
            path = 'C:/depot/games/eve-dev/eve/client/res/graphics/character/modular/female/head/head_generic/cd_female_head.gr2'
            import granny
            gf = granny.GrannyReadEntireFile(path)
            gi = granny.GrannyGetFileInfo(gf)
            print gi.contents.MeshCount,
            print 'meshes'
            for i in xrange(gi.contents.MeshCount):
                m = gi.contents.Meshes[i]
                if not m.contents.Name.startswith('CD_Head'):
                    continue
                vertex_count = m.contents.PrimaryVertexData.contents.VertexCount
                index_count = m.contents.PrimaryTopology.contents.IndexCount
                print vertex_count,
                print 'vertices',
                print index_count,
                print 'indices'
                vertex_buffer.CreateUserData(12, vertex_count, trinity.OPTIX_BUFFER_OUTPUT)
                vertex_buffer.MapUser()
                granny.GrannyCopyMeshVertices(m, granny.GrannyP3VertexType, vertex_buffer.GetUserDataBuffer())
                vertex_buffer.UnmapUser()
                index_buffer.CreateUserData(12, index_count / 3, trinity.OPTIX_BUFFER_OUTPUT)
                index_buffer.MapUser()
                granny.GrannyCopyMeshIndices(m, 4, index_buffer.GetUserDataBuffer())
                index_buffer.UnmapUser()
                break

            del gi
            del gf
        elif False:
            mesh = trinity.device.scene2.dynamics[0].visualModel.meshes[15]
            print mesh.name,
            res = mesh.geometry
            vertex_buffer.CreateFromGeometryRes(res, 9, True)
            vertex_count = vertex_buffer.GetSize1D()
            index_buffer.CreateFromGeometryRes(res, 9, False)
            index_count = index_buffer.GetSize1D() * 3
        else:
            dynamic = trinity.device.scene2.dynamics[0]
            output = optix.CreateFromSkinnedModel(dynamic, ptxFolder + '/triangle.ptx', 'mesh_intersect', 'mesh_bounds')
            geoms = output[0]
            group = trinity.Tr2OptixGeometryGroup()
            group.SetChildCount(len(geoms))
            for i in xrange(len(geoms)):
                instance = trinity.Tr2OptixGeometryInstance()
                instance.SetGeometry(geoms[i])
                instance.SetMaterial(any_hit_material)
                group.SetChild(i, instance)

            group.SetAcceleration('Bvh', 'Bvh')
            print 'interop scene created'
        if False:
            print 'vertex_count',
            print vertex_count,
            print 'index_count',
            print index_count
            self.printMem('after granny')
            mesh = trinity.Tr2OptixGeometry()
            mesh.InitializeFromProgram(ptxFolder + '/triangle.ptx', 'mesh_intersect', 'mesh_bounds')
            mesh.SetPrimitiveCount(index_count / 3)
            optix.SetBuffer('vertex_buffer', vertex_buffer)
            optix.SetBuffer('index_buffer', index_buffer)
            instance = trinity.Tr2OptixGeometryInstance()
            instance.SetGeometry(mesh)
            instance.SetMaterial(any_hit_material)
        if False:
            import struct
            fhair = file('c:/depot/optix/hair/curves.dat', 'rb')
            hair_count = struct.unpack('=I', fhair.read(4))[0]
            print hair_count,
            print 'hairs'
            hair_buffer = trinity.Tr2OptixBuffer()
            hair_buffer.CreateUserData(64, hair_count, trinity.OPTIX_BUFFER_OUTPUT)
            hair_buffer.MapUser()
            minx = 999
            miny = 999
            minz = 999
            maxx = -999
            maxy = -999
            maxz = -999
            for i in xrange(hair_count):
                for vec in xrange(4):
                    pos = struct.unpack('=ffff', fhair.read(16))
                    if pos[0] < minx:
                        minx = pos[0]
                    if pos[1] < miny:
                        miny = pos[1]
                    if pos[2] < minz:
                        minz = pos[2]
                    if pos[0] > maxx:
                        maxx = pos[0]
                    if pos[1] > maxy:
                        maxy = pos[1]
                    if pos[2] > maxz:
                        maxz = pos[2]
                    pos = (pos[0] * 0.1,
                     pos[1] * 0.1 + 1.7,
                     -pos[2] * 0.1,
                     pos[3] * 0.05)
                    for j in xrange(4):
                        hair_buffer.SetUserDataF(i * 64 + (vec * 4 + j) * 4, pos[j])



            hair_buffer.UnmapUser()
            print 'bbox (',
            print minx,
            print miny,
            print minz,
            print ') - (',
            print maxx,
            print maxy,
            print maxz,
            print ')'
            hair_geom = trinity.Tr2OptixGeometry()
            hair_geom.InitializeFromProgram(ptxFolder + '/bezier_curves.ptx', 'intersect', 'bounds')
            subdivide_depth = 2
            hair_geom.SetPrimitiveCount(hair_count * (1 << subdivide_depth))
            optix.SetUInt('presubdivide_depth', subdivide_depth)
            optix.SetBuffer('curves', hair_buffer)
            hair_instance = trinity.Tr2OptixGeometryInstance()
            hair_instance.SetGeometry(hair_geom)
            hair_instance.SetMaterial(any_hit_material)
            del fhair
        if False:
            group = trinity.Tr2OptixGeometryGroup()
            group.SetChildCount(1)
            group.SetChild(0, instance)
            group.SetAcceleration('Bvh', 'Bvh')
        optix.SetGroup('shadow_casters', group)
        self.printMem('[Optix] after createScene')



    def createScene2(self, optix, ptxFolder):
        any_hit_shader = trinity.Tr2OptixProgram(ptxFolder + '/eve_shadow.ptx', 'any_hit_shadow')
        any_hit_material = trinity.Tr2OptixMaterial()
        any_hit_material.SetAnyHit(0, any_hit_shader)
        sphere = trinity.Tr2OptixGeometry()
        sphere.InitializeFromProgram(ptxFolder + '/sphere.ptx', 'intersect', 'bounds')
        sphere.SetFloat4('sphere', 2, 1.6, 0, 0.025)
        instance = trinity.Tr2OptixGeometryInstance()
        instance.SetGeometry(sphere)
        instance.SetMaterial(any_hit_material)
        group = trinity.Tr2OptixGeometryGroup()
        group.SetChildCount(1)
        group.SetChild(0, instance)
        group.DisableAcceleration()
        optix.SetGroup('shadow_casters', group)



    def Run(self, rtWorldPosUV, rtWorldNormalUV, rtWorldPos, rtWorldNormal, rtDiffuseLight, rtSpecularLight):
        self.printMem('[Optix] before Run')
        oxWorldPosUVSampler = trinity.Tr2OptixTextureSampler()
        oxWorldPosUVSampler.CreateFromSurface(rtWorldPosUV)
        self.optix.SetSampler('request_buffer', oxWorldPosUVSampler)
        oxWorldNormalUVSampler = trinity.Tr2OptixTextureSampler()
        oxWorldNormalUVSampler.CreateFromSurface(rtWorldNormalUV)
        self.optix.SetSampler('world_normal_buffer', oxWorldNormalUVSampler)
        oxWorldPosSampler = trinity.Tr2OptixTextureSampler()
        oxWorldPosSampler.CreateFromSurface(rtWorldPos)
        oxWorldNormalSampler = trinity.Tr2OptixTextureSampler()
        oxWorldNormalSampler.CreateFromSurface(rtWorldNormal)
        self.optix.Compile()
        self.optix.Validate()
        print '[Optix] after Compile and Validate:',
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'
        print '[Optix] Run 1 - building BVH',
        start = time.clock()
        self.optix.Run(0, 0, 0)
        print str(time.clock() - start),
        print 'seconds',
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'
        print '[Optix] Run 1 - diffuse',
        print self.width,
        print 'x',
        print self.height,
        start = time.clock()
        self.optix.Run(0, self.width, self.height)
        print str(time.clock() - start),
        print 'seconds',
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'
        self.optix.SetBuffer('shadow_buffer', self.bufSpecularLight)
        self.optix.SetSampler('request_buffer', oxWorldPosSampler)
        self.optix.SetSampler('world_normal_buffer', oxWorldNormalSampler)
        print '[Optix] Run 2 - building BVH',
        start = time.clock()
        self.optix.Run(0, 0, 0)
        print str(time.clock() - start),
        print 'seconds',
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'
        print '[Optix] Run 2 - specular',
        print self.bbWidth,
        print 'x',
        print self.bbHeight,
        start = time.clock()
        self.optix.Run(1, self.bbWidth, self.bbHeight)
        print str(time.clock() - start),
        print 'seconds',
        print self.optix.GetDeviceAvailableMemory() / 1024,
        print '/',
        print self.optix.GetDeviceTotalMemory() / 1024,
        print 'KB'
        print '[Optix] CopyToSurface',
        start = time.clock()
        self.bufDiffuseLight.CopyToSurface(rtDiffuseLight)
        self.bufSpecularLight.CopyToSurface(rtSpecularLight)
        print str(time.clock() - start),
        print 'seconds'
        print '[Optix] All done'




class FullOptixRenderer():
    __guid__ = 'paperDoll.FullOptixRenderer'
    instance = None

    @staticmethod
    def matEqual(m1, m2):
        return m1._11 == m2._11 and m1._12 == m2._12 and m1._13 == m2._13 and m1._14 == m2._14 and m1._21 == m2._21 and m1._22 == m2._22 and m1._23 == m2._23 and m1._24 == m2._24 and m1._31 == m2._31 and m1._32 == m2._32 and m1._33 == m2._33 and m1._34 == m2._34 and m1._41 == m2._41 and m1._42 == m2._42 and m1._43 == m2._43 and m1._44 == m2._44



    @staticmethod
    def FuncWrapper(weakSelf, func):
        if weakSelf():
            func(weakSelf())



    def AddCallback(self, func, name, rj):
        cb = trinity.TriStepPythonCB()
        weakSelf = weakref.ref(self)
        cb.SetCallback(lambda : FullOptixRenderer.FuncWrapper(weakSelf, func))
        cb.name = name
        rj.steps.append(cb)



    @staticmethod
    def RaytraceFrame(selfRef):
        start = time.time()
        VP = SkinRaytracing.SetOptixMatrixFromTrinity(selfRef.optix, 'clipToWorld')
        if not FullOptixRenderer.matEqual(VP, selfRef.previousVP):
            selfRef.previousVP = VP
            selfRef.bufShadows.Clear()
            selfRef.framecount = 0
            model = selfRef.skinnedObject
            pos1 = model.GetBonePosition(model.GetBoneIndex('fj_eyeballLeft'))
            pos2 = model.GetBonePosition(model.GetBoneIndex('fj_eyeballRight'))
            dist1 = geo2.Vec3Distance(pos1, trinity.GetViewPosition())
            dist2 = geo2.Vec3Distance(pos2, trinity.GetViewPosition())
            selfRef.optix.SetFloat3('depthOfField', min(dist1, dist2) - trinity.GetFrontClip(), selfRef.settings['lens_radius'], 0)
        else:
            selfRef.framecount += 1
        selfRef.optix.SetUInt('frameIteration', selfRef.framecount)
        selfRef.ResetRayCount()
        time1 = time.time()
        selfRef.optix.Run(0, selfRef.width, selfRef.height)
        time2 = time.time()
        sec = time2 - time1
        raycount = selfRef.GetRayCount()
        raysec = raycount / float(sec)
        time3 = time.time()
        if selfRef.framecount % 16 == 0:
            invFC = 1.0 / selfRef.framecount if selfRef.framecount > 0 else 1.0
            selfRef.blitcolor.value = (invFC,
             invFC,
             invFC,
             1.0)
            selfRef.bufShadows.CopyToSurface(selfRef.RTShadows)
            stop = time.time()
            print 'time %05.3f / %05.3f / %05.3f / %05.3f msec' % (float(time1 - start) * 1000,
             float(time2 - time1) * 1000,
             float(time3 - time2) * 1000,
             float(stop - time3) * 1000),
            print '%d rays in %05.3f ms / %10d Krays/sec' % (raycount, sec * 1000, raysec / 1000)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixPositionsUV(self):
        PD.SkinLightmapRenderer.DoChangeEffect('oxPosWorldUVEffect', self.oxMeshes)
        if self.skinnedObject is not None and self.skinnedObject.visualModel is not None:
            self.savedMeshes = self.skinnedObject.visualModel.meshes[:]
        filteredMeshes = [ ref.object for ref in self.oxMeshes.iterkeys() if ref.object is not None ]
        PD.SkinLightmapRenderer.DoCopyMeshesToVisual(self.skinnedObject, filteredMeshes)
        self.scene2.filterList.removeAt(-1)
        self.scene2.filterList.append(self.skinnedObject)
        self.scene2.useFilterList = True



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnBeforeOptixNormalsUV(self):
        PD.SkinLightmapRenderer.DoChangeEffect('oxNormalWorldUVEffect', self.oxMeshes)



    def OnAfterOptix(self):
        PD.SkinLightmapRenderer.DoRestoreShaders(meshes=self.oxMeshes)
        PD.SkinLightmapRenderer.DoCopyMeshesToVisual(self.skinnedObject, self.savedMeshes)
        del self.savedMeshes
        self.scene2.useFilterList = False
        self.scene2.filterList.removeAt(-1)



    def _InitUVUnwrap(self):
        self.oxMeshes = {}
        self.scatterFX = set()
        self.unwrapSize = 1024
        posUV = PD.SkinLightmapRenderer.PreloadEffect(PD.SkinLightmapRenderer.OPTIX_POSWORLD_UV_EFFECT)
        normalUV = PD.SkinLightmapRenderer.PreloadEffect(PD.SkinLightmapRenderer.OPTIX_NORMALWORLD_UV_EFFECT)
        deriv = PD.SkinLightmapRenderer.PreloadEffect(PD.SkinLightmapRenderer.STRETCHMAP_RENDERER_EFFECT)
        self.oxDepth = trinity.TriSurfaceManaged(trinity.device.CreateDepthStencilSurface, self.unwrapSize, self.unwrapSize, trinity.TRIFMT_D24S8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        for mesh in self.skinnedObject.visualModel.meshes:
            if PD.SkinLightmapRenderer.IsScattering(mesh):
                m = PD.SkinLightmapRenderer.Mesh()
                m.ExtractOrigEffect(mesh)
                m.CreateOptixEffects(includeStretchMap=True)
                PD.AddWeakBlue(self, 'oxMeshes', mesh, m)
                fx = PD.GetEffectsFromMesh(mesh)
                for f in fx:
                    self.scatterFX.add(f)


        self.oxWorldPosMapUV = PD.SkinLightmapRenderer.CreateRenderTarget(self.unwrapSize, self.unwrapSize, trinity.TRIFMT_A32B32G32R32F, useRT=True)
        self.oxWorldNormalMapUV = PD.SkinLightmapRenderer.CreateRenderTarget(self.unwrapSize, self.unwrapSize, trinity.TRIFMT_A32B32G32R32F, useRT=True)
        self.stretchMap = PD.SkinLightmapRenderer.CreateRenderTarget(self.unwrapSize / 2, self.unwrapSize / 2, trinity.TRIFMT_A32B32G32R32F, useRT=True)
        rj = trinity.CreateRenderJob('Optix UV Unwrap')
        rj.PushRenderTarget(self.oxWorldPosMapUV)
        rj.PushDepthStencil(self.oxDepth)
        rj.Clear((0, 0, 0, 0), 1.0)
        rj.SetStdRndStates(trinity.RM_FULLSCREEN)
        vp = trinity.TriViewport()
        vp.x = 0
        vp.y = 0
        vp.width = self.unwrapSize
        vp.height = self.unwrapSize
        rj.SetViewport(vp)
        PD.SkinLightmapRenderer.AddCallback(self, FullOptixRenderer.OnBeforeOptixPositionsUV, 'onBeforeOptixPositionsUV', rj)
        rj.RenderScene(self.scene2).name = 'Optix WorldPos (UV space)'
        PD.SkinLightmapRenderer.AddCallback(self, lambda weakSelf: PD.SkinLightmapRenderer.DoChangeEffect('oxNormalWorldUVEffect', meshes=weakSelf.oxMeshes), '', rj)
        rj.SetRenderTarget(self.oxWorldNormalMapUV)
        rj.Clear((0, 0, 0, 0), 1.0)
        rj.RenderScene(self.scene2).name = 'Optix Normals (UV space)'
        rj.SetRenderTarget(self.stretchMap)
        rj.Clear((0, 0, 0, 0), 1.0)
        vp2 = trinity.TriViewport()
        vp2.x = 0
        vp2.y = 0
        vp2.width = self.unwrapSize / 2
        vp2.height = self.unwrapSize / 2
        rj.SetViewport(vp2)
        PD.SkinLightmapRenderer.AddCallback(self, lambda weakSelf: PD.SkinLightmapRenderer.DoChangeEffect('stretchmapRenderEffect', meshes=weakSelf.oxMeshes), '', rj)
        rj.RenderScene(self.scene2).name = 'Stretchmap'
        PD.SkinLightmapRenderer.AddCallback(self, FullOptixRenderer.OnAfterOptix, 'onAfterOptix', rj)
        rj.PopRenderTarget()
        rj.PopDepthStencil()
        rj.ScheduleOnce()
        rj.WaitForFinish()
        if False:
            PD.SkinLightmapRenderer.SaveTarget(self.oxWorldPosMapUV, 'c:/depot/oxworldposuv2.dds', isRT=True)
            PD.SkinLightmapRenderer.SaveTarget(self.oxWorldNormalMapUV, 'c:/depot/oxworldnormaluv2.dds', isRT=True)
            PD.SkinLightmapRenderer.SaveTarget(self.stretchMap, 'c:/depot/stretchmap2.dds', isRT=True)



    def ResetRayCount(self):
        self.ray_count_buffer.Map()
        self.ray_count_buffer.SetUserDataI(0, 0)
        self.ray_count_buffer.Unmap()



    def GetRayCount(self):
        self.ray_count_buffer.Map()
        count = self.ray_count_buffer.GetUserDataI(0)
        self.ray_count_buffer.Unmap()
        return count



    def _DoInit(self, scene2 = None):
        model = None
        if scene2 is None:
            scene2 = PD.SkinLightmapRenderer.Scene()
        self.scene2 = scene2
        self.previousVP = trinity.TriMatrix()
        self.framecount = 1
        if scene2 is None:
            log.LogWarn('[Optix] No scene!')
            return 
        for dynamic in scene2.dynamics:
            if dynamic.__typename__ == 'Tr2IntSkinnedObject':
                model = dynamic
                break
        else:
            log.LogWarn('[Optix] No Tr2IntSkinnedObject found')
            return 

        if model is None:
            log.LogWarn('[Optix] No Tr2IntSkinnedObject found')
            return 
        self.skinnedObject = model
        if self.skinnedObject.visualModel is None:
            log.LogWarn('[Optix] skinnedObject has no visualMeshes')
            return 
        bg = trinity.device.GetBackBuffer()
        self.width = bg.width
        self.height = bg.height
        self.blitfx = trinity.Tr2Effect()
        self.blitfx.effectFilePath = 'res:/graphics/effect/utility/compositing/colorcopyblitToGamma.fx'
        if self.blitfx.effectResource is None:
            return 
        while self.blitfx.effectResource.isLoading:
            blue.synchro.Yield()

        self._InitUVUnwrap()
        self.blitfx.PopulateParameters()
        self.blitfx.RebuildCachedData()
        self.blitcolor = trinity.Tr2Vector4Parameter()
        self.blitcolor.name = 'Color'
        self.blitfx.parameters.append(self.blitcolor)
        for steps in trinity.device.scheduledRecurring:
            if steps.name == 'FullOptixRenderer':
                steps.UnscheduleRecurring()

        start = time.clock()
        optix = trinity.Tr2Optix()
        self.optix = optix
        optix.SetInteropDevice()
        optix.SetRayTypeCount(4)
        optix.SetEntryPointCount(1)
        optix.EnableAllExceptions()
        optix.SetPrintEnabled(True)
        optix.SetPrintBufferSize(16384)
        optix.SetUInt('radiance_ray_type', 0)
        optix.SetUInt('shadow_ray_type', 1)
        optix.SetUInt('translucency_ray_type', 2)
        optix.SetUInt('translucency_ray_type', 3)
        optix.SetFloat('scene_epsilon', 0.001)
        optix.SetUInt('frameIteration', 0)
        self.ApplySettings()
        path = str(blue.rot.PathToFilename('res:/graphics/effect/optix/'))
        log.LogInfo('[Optix] Getting files from', path)
        everything = []
        shader_shadow = trinity.Tr2OptixProgram(path + 'eve_shadow.ptx', 'any_hit_shadow')
        shader_shadow_blend = trinity.Tr2OptixProgram(path + 'eve_shadow.ptx', 'any_hit_shadow_blend')
        shader_diffuse_only_feeler = trinity.Tr2OptixProgram(path + 'eve_bounce.ptx', 'closest_hit_DiffuseOnlyFeeler2')
        any_hit_cutout = trinity.Tr2OptixProgram(path + 'eve_cutout.ptx', 'any_hit_CutoutMask')
        any_hit_diffuse_feeler_blend = trinity.Tr2OptixProgram(path + 'eve_shadow.ptx', 'any_hit_diffuse_feeler_blend')
        everything.append(shader_shadow)
        everything.append(shader_shadow_blend)
        everything.append(shader_diffuse_only_feeler)
        everything.append(any_hit_cutout)
        skin_single_shade = trinity.Tr2OptixProgram(path + 'eve_skin.ptx', 'closest_hit_ShadeSinglePassSkin_Single2')
        skin_single_material = trinity.Tr2OptixMaterial()
        skin_single_material.SetClosestHit(0, skin_single_shade)
        skin_single_material.SetAnyHit(1, shader_shadow)
        skin_single_material.SetClosestHit(3, shader_diffuse_only_feeler)
        skin_single_material.SetFloat3('shading_color', 1, 0.25, 1)
        everything.append(skin_single_shade)
        everything.append(skin_single_material)
        skin_single_shade_scatter = trinity.Tr2OptixProgram(path + 'eve_skin.ptx', 'closest_hit_ShadeSinglePassSkin_Single_Scatter2')
        skin_single_material_scatter = trinity.Tr2OptixMaterial()
        skin_single_material_scatter.SetClosestHit(0, skin_single_shade_scatter)
        skin_single_material_scatter.SetAnyHit(1, shader_shadow)
        skin_single_material_scatter.SetClosestHit(3, shader_diffuse_only_feeler)
        skin_single_material_scatter.SetFloat3('shading_color', 1, 0.25, 1)
        everything.append(skin_single_shade_scatter)
        everything.append(skin_single_material_scatter)
        skin_single_material_decal = trinity.Tr2OptixMaterial()
        skin_single_material_decal.SetClosestHit(0, skin_single_shade)
        skin_single_material_decal.SetAnyHit(0, any_hit_cutout)
        skin_single_material_decal.SetAnyHit(1, shader_shadow_blend)
        skin_single_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        skin_single_material_decal.SetAnyHit(3, any_hit_cutout)
        skin_single_material_decal.SetFloat3('shading_color', 1, 0.25, 1)
        everything.append(skin_single_material_decal)
        glasses_shade = trinity.Tr2OptixProgram(path + 'eve_glasses.ptx', 'glasses_shade')
        glasses_shadow = trinity.Tr2OptixProgram(path + 'eve_glasses.ptx', 'glasses_shadow')
        glass_material = trinity.Tr2OptixMaterial()
        glass_material.SetAnyHit(0, glasses_shade)
        glass_material.SetAnyHit(1, glasses_shadow)
        glass_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(glasses_shade)
        everything.append(glasses_shadow)
        vizualizer_shade = trinity.Tr2OptixProgram(path + 'eve_basic.ptx', 'closest_hit_VizNormal')
        vizualizer = trinity.Tr2OptixMaterial()
        vizualizer.SetClosestHit(0, vizualizer_shade)
        vizualizer.SetAnyHit(1, shader_shadow)
        vizualizer.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(vizualizer_shade)
        everything.append(vizualizer)
        vizualizer_decal = trinity.Tr2OptixMaterial()
        vizualizer_decal.SetClosestHit(0, vizualizer_shade)
        vizualizer_decal.SetAnyHit(0, any_hit_cutout)
        vizualizer_decal.SetAnyHit(1, shader_shadow)
        vizualizer_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        vizualizer_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(vizualizer_decal)
        skin_double_shade = trinity.Tr2OptixProgram(path + 'eve_skin.ptx', 'closest_hit_ShadeSinglePassSkin_Double2')
        skin_double_material = trinity.Tr2OptixMaterial()
        skin_double_material.SetClosestHit(0, skin_double_shade)
        skin_double_material.SetAnyHit(1, shader_shadow)
        skin_double_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(skin_double_shade)
        everything.append(skin_double_material)
        skin_double_shade_blend = trinity.Tr2OptixProgram(path + 'eve_skin.ptx', 'closest_hit_ShadeSinglePassSkin_Double2_Blend')
        skin_double_material_decal = trinity.Tr2OptixMaterial()
        skin_double_material_decal.SetClosestHit(0, skin_double_shade_blend)
        skin_double_material_decal.SetAnyHit(0, any_hit_cutout)
        skin_double_material_decal.SetAnyHit(1, shader_shadow_blend)
        skin_double_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        skin_double_material_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(skin_double_material_decal)
        avatar_brdf_shade = trinity.Tr2OptixProgram(path + 'eve_brdf.ptx', 'closest_hit_ShadeAvatarBRDF_Single2')
        avatar_brdf_material = trinity.Tr2OptixMaterial()
        avatar_brdf_material.SetClosestHit(0, avatar_brdf_shade)
        avatar_brdf_material.SetAnyHit(1, shader_shadow)
        avatar_brdf_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(avatar_brdf_shade)
        everything.append(avatar_brdf_material)
        avatar_brdf_material_decal = trinity.Tr2OptixMaterial()
        avatar_brdf_material_decal.SetClosestHit(0, avatar_brdf_shade)
        avatar_brdf_material_decal.SetAnyHit(0, any_hit_cutout)
        avatar_brdf_material_decal.SetAnyHit(1, shader_shadow_blend)
        avatar_brdf_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        avatar_brdf_material_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(avatar_brdf_material_decal)
        avatar_brdf_double_shade = trinity.Tr2OptixProgram(path + 'eve_brdf.ptx', 'closest_hit_ShadeAvatarBRDF_Double2')
        avatar_brdf_double_material = trinity.Tr2OptixMaterial()
        avatar_brdf_double_material.SetClosestHit(0, avatar_brdf_double_shade)
        avatar_brdf_double_material.SetAnyHit(1, shader_shadow)
        avatar_brdf_double_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(avatar_brdf_double_shade)
        everything.append(avatar_brdf_double_material)
        avatar_brdf_double_material_decal = trinity.Tr2OptixMaterial()
        avatar_brdf_double_material_decal.SetClosestHit(0, avatar_brdf_double_shade)
        avatar_brdf_double_material_decal.SetAnyHit(0, any_hit_cutout)
        avatar_brdf_double_material_decal.SetAnyHit(1, shader_shadow_blend)
        avatar_brdf_double_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        avatar_brdf_double_material_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(avatar_brdf_double_material_decal)
        avatar_hair_shade = trinity.Tr2OptixProgram(path + 'eve_hair.ptx', 'closest_hit_ShadeAvatarHair2_Blend')
        avatar_hair_material = trinity.Tr2OptixMaterial()
        avatar_hair_material.SetClosestHit(0, avatar_hair_shade)
        avatar_hair_material.SetAnyHit(1, shader_shadow_blend)
        avatar_hair_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(avatar_hair_shade)
        everything.append(avatar_hair_material)
        avatar_hair_material_decal = trinity.Tr2OptixMaterial()
        avatar_hair_material_decal.SetClosestHit(0, avatar_hair_shade)
        avatar_hair_material_decal.SetAnyHit(0, any_hit_cutout)
        avatar_hair_material_decal.SetAnyHit(1, shader_shadow_blend)
        avatar_hair_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        avatar_hair_material_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(avatar_hair_material_decal)
        eye_shade = trinity.Tr2OptixProgram(path + 'eve_eyes.ptx', 'closest_hit_ShadeEye')
        eye_material = trinity.Tr2OptixMaterial()
        eye_material.SetClosestHit(0, eye_shade)
        eye_material.SetAnyHit(1, shader_shadow)
        everything.append(eye_shade)
        everything.append(eye_material)
        eye_wetness_shade = trinity.Tr2OptixProgram(path + 'eve_eyes.ptx', 'closest_hit_ShadeEyeWetness')
        eye_wetness_material = trinity.Tr2OptixMaterial()
        eye_wetness_material.SetClosestHit(0, eye_wetness_shade)
        eye_wetness_material.SetAnyHit(1, shader_shadow)
        everything.append(eye_wetness_shade)
        everything.append(eye_wetness_material)
        portrait_basic_shade = trinity.Tr2OptixProgram(path + 'eve_basic.ptx', 'closest_hit_ShadePortraitBasic')
        portrait_basic_material = trinity.Tr2OptixMaterial()
        portrait_basic_material.SetClosestHit(0, portrait_basic_shade)
        portrait_basic_material.SetAnyHit(1, shader_shadow)
        portrait_basic_material.SetClosestHit(3, shader_diffuse_only_feeler)
        everything.append(portrait_basic_shade)
        everything.append(portrait_basic_material)
        portrait_basic_material_decal = trinity.Tr2OptixMaterial()
        portrait_basic_material_decal.SetClosestHit(0, portrait_basic_shade)
        portrait_basic_material_decal.SetAnyHit(0, any_hit_cutout)
        portrait_basic_material_decal.SetAnyHit(1, shader_shadow_blend)
        portrait_basic_material_decal.SetClosestHit(3, shader_diffuse_only_feeler)
        portrait_basic_material_decal.SetAnyHit(3, any_hit_cutout)
        everything.append(portrait_basic_material_decal)
        log.LogInfo('[FOR] global setup OK', time.clock() - start, 'seconds')
        oxWorldPosUVSampler = trinity.Tr2OptixTextureSampler()
        oxWorldPosUVSampler.CreateFromSurface(self.oxWorldPosMapUV)
        oxWorldPosUVSampler.SetNormalizedIndexingMode(True)
        optix.SetSampler('world_pos_uv_buffer', oxWorldPosUVSampler)
        log.LogInfo('[Optix] No-Copy Interop for world_pos_uv_buffer')
        everything.append(oxWorldPosUVSampler)
        oxWorldNormalUVSampler = trinity.Tr2OptixTextureSampler()
        oxWorldNormalUVSampler.CreateFromSurface(self.oxWorldNormalMapUV)
        oxWorldNormalUVSampler.SetNormalizedIndexingMode(True)
        optix.SetSampler('world_normal_uv_buffer', oxWorldNormalUVSampler)
        log.LogInfo('[Optix] No-Copy Interop for world_normal_uv_buffer')
        everything.append(oxWorldNormalUVSampler)
        stretchMapSampler = trinity.Tr2OptixTextureSampler()
        stretchMapSampler.CreateFromSurface(self.stretchMap)
        stretchMapSampler.SetNormalizedIndexingMode(True)
        optix.SetSampler('stretchmap_buffer', stretchMapSampler)
        log.LogInfo('[Optix] No-Copy Interop for stretchmap_buffer')
        everything.append(stretchMapSampler)
        start = time.clock()
        self.skinnedOptix = optix.CreateFromSkinnedModel(model, 72, path + 'triangle.ptx', 'mesh_intersect', 'mesh_bounds', 64, path + 'triangle64.ptx', 'mesh_intersect', 'mesh_bounds')
        batchGeoms = self.skinnedOptix[0]
        batchFx = self.skinnedOptix[2]
        batchSkin = self.skinnedOptix[3]
        totalGeoms = 0
        for geoms in batchGeoms:
            totalGeoms += len(geoms)

        haveBeard = False
        for mesh in model.visualModel.meshes:
            for area in mesh.decalAreas:
                if PD.IsBeard(area):
                    haveBeard = True
                    break


        if haveBeard:
            print 'Beard found'
            optix.SetFloat3('beardOptions', self.settings['beardLength'][0], self.settings['beardLength'][1], self.settings['beardGravity'])
        else:
            print 'Beard NOT found'
        group = trinity.Tr2OptixGeometryGroup()
        groupChildren = []

        def SetAlphaRef(instance, batchType):
            if batchType == 1:
                instance.SetFloat4('alphaRef', 0.75, 0, 0, 0)
            elif batchType == 2:
                instance.SetFloat4('alphaRef', 0.01, 0, 0, 0)


        ray_count_buffer = trinity.Tr2OptixBuffer()
        ray_count_buffer.CreateUInt1(1, 1, trinity.OPTIX_BUFFER_INPUT_OUTPUT)
        ray_count_buffer.Map()
        ray_count_buffer.SetUserDataI(0, 0)
        ray_count_buffer.Unmap()
        optix.SetBuffer('ray_count', ray_count_buffer)
        self.ray_count_buffer = ray_count_buffer
        start = time.clock()
        samplers = SkinRaytracing.InteropAllTextures(optix, model, waitForFinish=True)
        everything.append(samplers)
        backdrop = trinity.TriTexture2DParameter()
        backdrop.resourcePath = self.settings['backgroundBitmap']
        skinmap = trinity.TriTexture2DParameter()
        skinmap.resourcePath = 'res:/Graphics/Character/Modular/Female/head/head_generic/SkinMap.png'
        blue.resMan.Wait()
        everything.append(SkinRaytracing.InteropTexture(optix, 'BackgroundEnvMap', backdrop.resource, waitForFinish=True))
        everything.append(SkinRaytracing.InteropTexture(optix, 'SkinMap', skinmap.resource, waitForFinish=True))
        log.LogInfo('[FOR] texture interop OK', time.clock() - start, 'seconds')
        if haveBeard:
            beardProgram = trinity.Tr2OptixProgram(path + 'eve_beard_kernel.ptx', 'kernel')
            curve_output = trinity.Tr2OptixBuffer()
            curve_count = 512
            curve_output.CreateUserData(64, curve_count * curve_count, trinity.OPTIX_BUFFER_INPUT_OUTPUT, True)
            optix.SetBuffer('output', curve_output)
            optix.SetRayTypeCount(1)
            optix.SetRayGenerationProgram(0, beardProgram)
            optix.Run(0, curve_count, curve_count)
            optix.SetRayTypeCount(4)
            hair_geom = trinity.Tr2OptixGeometry()
            hair_geom.InitializeFromProgram(path + 'bezier_curves.ptx', 'intersect', 'bounds')
            subdivide_depth = 2
            hair_geom.SetPrimitiveCount(curve_count * curve_count * (1 << subdivide_depth))
            optix.SetUInt('presubdivide_depth', subdivide_depth)
            optix.SetBuffer('curves', curve_output)
            hair_instance = trinity.Tr2OptixGeometryInstance()
            hair_instance.SetGeometry(hair_geom)
            hair_shader = trinity.Tr2OptixProgram(path + 'eve_beard_shader.ptx', 'closest_hit_BeardShader')
            hair_material = trinity.Tr2OptixMaterial()
            hair_material.SetClosestHit(0, hair_shader)
            hair_material.SetAnyHit(1, shader_shadow)
            hair_instance.SetMaterial(hair_material)
            groupChildren.append(hair_instance)
        if True:
            print '*** Tesselation phase ***'
            ptx = {}
            ptx[72] = path + 'eve_skinning_kernel.ptx'
            ptx[64] = path + 'eve_skinning_kernel64.ptx'
            for (bytes, ptxfile,) in ptx.iteritems():
                log.LogInfo('[FOR] Processing ', bytes, 'bytes/vertex')
                skinningProgram = trinity.Tr2OptixProgram(ptxfile, 'kernel_no_tesselation')
                skinningProgramTesselate = trinity.Tr2OptixProgram(ptxfile, 'kernel_tesselation')
                optix.SetEntryPointCount(2)
                optix.SetRayGenerationProgram(0, skinningProgram)
                optix.SetRayGenerationProgram(1, skinningProgramTesselate)
                for batchType in range(len(batchGeoms)):
                    geoms = batchGeoms[batchType]
                    fx = batchFx[batchType]
                    skin = batchSkin[batchType]
                    out = []

                    def doTesselation(fx):
                        return 'skinnedavatarhair_detailed.fx' in fx.effectFilePath.lower()


                    for i in xrange(len(geoms)):
                        if 'furshell' in fx[i].effectFilePath.lower():
                            out.append(None)
                            continue
                        tesselate = doTesselation(fx[i])
                        triangle_count = skin[i][4]
                        bytes_per_vertex = skin[i][6]
                        if bytes_per_vertex != bytes:
                            out.append(None)
                            continue
                        vertex_buffer_output = trinity.Tr2OptixBuffer()
                        vertex_buffer_output.CreateUserData(bytes_per_vertex, triangle_count * 3 * 4 if tesselate else triangle_count * 3, trinity.OPTIX_BUFFER_INPUT_OUTPUT, True)
                        out.append(vertex_buffer_output)

                    for i in xrange(len(geoms)):
                        if 'furshell' in fx[i].effectFilePath.lower():
                            continue
                        triangle_count = skin[i][4]
                        tesselate = doTesselation(fx[i])
                        bytes_per_vertex = skin[i][6]
                        if bytes_per_vertex != bytes:
                            continue
                        if tesselate:
                            log.LogInfo('[FOR] Tesselating geometry ', i, '/', batchType)
                        else:
                            log.LogInfo('[FOR] Skinning geometry ', i, '/', batchType)
                        optix.SetBuffer('vertex_buffer', skin[i][0])
                        optix.SetBuffer('index_buffer', skin[i][1])
                        optix.SetBuffer('vertex_buffer_output', out[i])
                        optix.SetUInt('first_index_index', skin[i][3])
                        optix.SetBuffer('matrix_buffer', skin[i][5])
                        program = int(tesselate)
                        optix.Run(program, triangle_count, 1)
                        geoms[i].SetBuffer('vertex_buffer', out[i])
                        if tesselate:
                            geoms[i].SetPrimitiveCount(triangle_count * 4)



            print '*** Raytracing phase ***'
        for batchType in range(len(batchGeoms)):
            isOpaque = batchType == 0
            geoms = batchGeoms[batchType]
            fx = batchFx[batchType]
            for i in xrange(len(geoms)):
                if 'furshell' in fx[i].effectFilePath.lower():
                    continue
                instance = trinity.Tr2OptixGeometryInstance()
                everything.append(instance)
                instance.SetGeometry(geoms[i])
                r = random.random()
                g = random.random()
                b = random.random()
                instance.SetFloat4('viz_constant_color', r, g, b, 1.0)
                fxpath = fx[i].effectFilePath.lower()
                if False:
                    instance.SetMaterial(vizualizer if isOpaque else vizualizer_decal)
                elif 'glassshader' in fxpath:
                    instance.SetMaterial(glass_material)
                elif 'skinnedavatarbrdfsinglepassskin_single.fx' in fxpath:
                    if fx[i] in self.scatterFX:
                        instance.SetMaterial(skin_single_material_scatter)
                    else:
                        instance.SetMaterial(skin_single_material if isOpaque else skin_single_material_decal)
                    SetAlphaRef(instance, batchType)
                elif 'skinnedavatarbrdfsinglepassskin_double.fx' in fxpath:
                    instance.SetMaterial(skin_double_material if isOpaque else skin_double_material_decal)
                    SetAlphaRef(instance, batchType)
                elif 'skinnedavatarbrdflinear.fx' in fxpath:
                    instance.SetMaterial(avatar_brdf_material if isOpaque else avatar_brdf_material_decal)
                elif 'skinnedavatarbrdfdoublelinear.fx' in fxpath:
                    instance.SetMaterial(avatar_brdf_double_material if isOpaque else avatar_brdf_double_material_decal)
                elif 'skinnedavatarhair_detailed.fx' in fxpath:
                    instance.SetMaterial(avatar_hair_material if isOpaque else avatar_hair_material_decal)
                    instance.SetFloat4('alphaRef', 0.01, 0, 0, 0)
                elif 'eyeshader.fx' in fxpath:
                    instance.SetMaterial(eye_material)
                elif 'eyewetnessshader.fx' in fxpath:
                    instance.SetMaterial(eye_wetness_material)
                elif 'portraitbasic.fx' in fxpath:
                    instance.SetMaterial(portrait_basic_material if isOpaque else portrait_basic_material_decal)
                else:
                    instance.SetMaterial(vizualizer if isOpaque else vizualizer_decal)
                SkinRaytracing.CopyParametersToContext(fx[i], instance)
                groupChildren.append(instance)


        group.SetChildCount(len(groupChildren))
        for x in xrange(len(groupChildren)):
            group.SetChild(x, groupChildren[x])

        everything.append(group)
        group.SetAcceleration('Bvh', 'Bvh')
        log.LogInfo('[FOR] scene interop OK', time.clock() - start, 'seconds')
        start = time.clock()
        bufEveLights = SkinRaytracing.CreateBufferForLights(scene2)
        optix.SetBuffer('eve_lights', bufEveLights)
        log.LogInfo('[FOR] lights interop OK', time.clock() - start, 'seconds')
        start = time.clock()
        optix.SetGroup('top_scene', group)
        optix.SetGroup('shadow_casters', group)
        raygen = trinity.Tr2OptixProgram(path + 'pinhole_ray.ptx', 'ray_request')
        optix.SetRayGenerationProgram(0, raygen)
        optix.SetRayGenerationProgram(1, raygen)
        optix.SetEntryPointCount(1)
        everything.append(raygen)
        miss = trinity.Tr2OptixProgram(path + 'eve_miss.ptx', 'miss')
        optix.SetMissProgram(3, miss)
        optix.SetFloat3('bg_color', 1.0, 0, 0)
        everything.append(miss)
        exception = trinity.Tr2OptixProgram(path + 'eve_miss.ptx', 'exception')
        optix.SetExceptionProgram(0, exception)
        everything.append(exception)
        optix.SetStackSize(4096)
        self.everything = everything
        self.RTShadows = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, self.width, self.height, trinity.TRIFMT_A32B32G32R32F, trinity.TRIMULTISAMPLE_NONE, 0, True)
        self.bufShadows = trinity.Tr2OptixBuffer()
        self.bufShadows.CreateFloat4(self.width, self.height, trinity.OPTIX_BUFFER_INPUT_OUTPUT)
        optix.SetBuffer('shadow_buffer', self.bufShadows)
        SkinRaytracing.SetOptixMatrixFromTrinity(optix, 'clipToWorld')
        log.LogInfo('[FOR] general setup OK', time.clock() - start, 'seconds')
        optix.ReportObjectCounts()
        start = time.clock()
        optix.Compile()
        log.LogInfo('[FOR] compile OK', time.clock() - start, 'seconds')
        start = time.clock()
        optix.Validate()
        log.LogInfo('[FOR] validate OK', time.clock() - start, 'seconds')
        start = time.clock()
        optix.Run(0, 0, 0)
        log.LogInfo('[FOR] BVH OK', time.clock() - start, 'seconds')
        start = time.clock()
        RTShadowsTexture = trinity.device.CreateTexture(self.width, self.height, 1, 0, trinity.TRIFMT_A32B32G32R32F, trinity.TRIPOOL_MANAGED)
        tex = trinity.TriTexture2DParameter()
        tex.name = 'Texture'
        tex.SetResource(RTShadowsTexture)
        self.blitfx.resources.append(tex)
        rj = trinity.CreateRenderJob('FullOptixRenderer')
        rj.PushRenderTarget(self.RTShadows)
        rj.PushDepthStencil(None)
        self.AddCallback(FullOptixRenderer.RaytraceFrame, 'Raytrace Frame', rj)
        rj.CopyRtToTexture(RTShadowsTexture)
        rj.PopDepthStencil()
        rj.PopRenderTarget()
        rj.SetStdRndStates(trinity.RM_FULLSCREEN)
        rj.RenderEffect(self.blitfx)
        rj.steps.append(trinity.TriStepRenderFps())
        rj.ScheduleRecurring(insertFront=False)
        self.renderJob = rj
        log.LogInfo('[FOR] final setup OK', time.clock() - start, 'seconds')
        self.EnablePaperDollJobs(False)



    @staticmethod
    def EnablePaperDollJobs(enable):
        for job in trinity.device.scheduledRecurring:
            if 'paperdollrenderjob' in job.name.lower():
                for step in job.steps:
                    step.enabled = enable


        if not enable:
            trinity.device.tickInterval = 10
        else:
            trinity.device.tickInterval = 0



    def ApplySettings(self):
        self.optix.SetFloat('light_size', self.settings['light_size'])
        self.optix.SetFloat3('depthOfField', 1.0, self.settings['lens_radius'], 0)
        self.optix.SetFloat('HairShadows', self.settings['HairShadows'])
        self.optix.SetFloat('EnvMapBoost', self.settings['EnvMapBoost'])
        self.previousVP.Identity()



    def SetLensRadius(self, lens_radius):
        self.settings['lens_radius'] = lens_radius
        self.ApplySettings()



    def SetLightSize(self, light_size):
        self.settings['light_size'] = light_size
        self.ApplySettings()



    def SetHairShadowsEnabled(self, enabled):
        self.settings['HairShadows'] = float(enabled)
        self.ApplySettings()



    def SetBackgroundIntensity(self, intensity):
        self.settings['EnvMapBoost'] = intensity
        self.ApplySettings()



    def __init__(self, scene2 = None, backgroundBitmap = None, memento = None, beardLength = (0.01, 0.01), beardGravity = 0.0005):
        log.LogInfo('[FOR] init', self)
        blue.motherLode.maxMemUsage = 0
        blue.resMan.ClearAllCachedObjects()
        self.framecount = 0
        if memento is not None:
            self.settings = memento
        else:
            self.settings = {}
            self.settings['light_size'] = 0.25
            self.settings['lens_radius'] = 0.001
            self.settings['HairShadows'] = 1.0
            self.settings['EnvMapBoost'] = 1.0
            self.settings['backgroundBitmap'] = backgroundBitmap if backgroundBitmap is not None else 'res:/texture/global/red_blue_ramp.dds'
            self.settings['beardLength'] = beardLength
            self.settings['beardGravity'] = beardGravity
        uthread.new(self._DoInit, scene2=scene2)



    def GetMemento(self):
        return self.settings



    def __del__(self):
        log.LogInfo('[FOR] deleting', self)
        if hasattr(self, 'renderJob'):
            self.renderJob.UnscheduleRecurring()
            self.renderJob = None
        del self.ray_count_buffer
        del self.bufShadows
        del self.skinnedOptix
        del self.everything
        log.LogInfo('[FOR] Post-cleanup leak check:')
        self.optix.ReportObjectCounts()
        self.EnablePaperDollJobs(True)



    @staticmethod
    def Pause():
        if FullOptixRenderer.instance is not None:
            FullOptixRenderer.instance.renderJob.UnscheduleRecurring()



    @staticmethod
    def NotifyUpdate():
        if FullOptixRenderer.instance is not None:
            memento = FullOptixRenderer.instance.GetMemento()
            FullOptixRenderer.instance = None
            FullOptixRenderer.instance = FullOptixRenderer(memento=memento)




