import blue
import trinity
import bluepy
import re

class CausticsRenderJob(object):
    __cid__ = 'trinity.TriRenderJob'
    __metaclass__ = bluepy.BlueWrappedMetaclass

    def Initialize(self, size, speed, amplitude, tiling, texturePath):

        def TextureDestroyed():
            self.Destroy()


        texture = trinity.device.CreateTexture(size, size, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_DEFAULT)
        self.name = 'Caustics'
        self.size = size
        self.texture = blue.BluePythonWeakRef(texture)
        self.texture.callback = TextureDestroyed
        self.steps.append(trinity.TriStepPushRenderTarget(texture.GetSurfaceLevel(0)))
        self.steps.append(trinity.TriStepClear((0, 0, 0, 0)))
        self.steps.append(trinity.TriStepSetStdRndStates(trinity.RM_FULLSCREEN))
        material = trinity.Tr2ShaderMaterial()
        material.highLevelShaderName = 'Caustics'
        param = trinity.TriTexture2DParameter()
        param.name = 'Texture'
        param.resourcePath = texturePath
        material.parameters['Texture'] = param
        param = trinity.Tr2FloatParameter()
        param.name = 'Speed'
        param.value = speed
        material.parameters['Speed'] = param
        param = trinity.Tr2FloatParameter()
        param.name = 'Amplitude'
        param.value = amplitude
        material.parameters['Amplitude'] = param
        param = trinity.Tr2FloatParameter()
        param.name = 'Tiling'
        param.value = tiling
        material.parameters['Tiling'] = param
        material.BindLowLevelShader([])
        self.steps.append(trinity.TriStepRenderFullScreenShader(material))
        self.steps.append(trinity.TriStepPopRenderTarget())
        trinity.device.scheduledRecurring.append(self)
        return texture



    def Destroy(self):
        trinity.device.scheduledRecurring.remove(self)
        self.texture = None



    def DoPrepareResources(self):
        if self.texture is not None and self.texture.object is not None:
            self.texture.object.AttachToTexture(trinity.device.CreateTexture(self.size, self.size, 1, trinity.TRIUSAGE_RENDERTARGET, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_DEFAULT))
        for step in self.steps:
            if type(step) is trinity.TriStepPushRenderTarget:
                step.target = self.texture.object.GetSurfaceLevel(0)




    def DoReleaseResources(self, level):
        if self.texture is not None and self.texture.object is not None:
            self.texture.object.AttachToTexture(None)




def Caustics(paramString):
    params = {'size': 256,
     'speed': 1,
     'amplitude': 1,
     'tiling': 1,
     'texture': 'res:/Texture/Global/caustic.dds'}
    expr = re.compile('&?(\\w+)=([^&]*)')
    pos = 0
    while True:
        match = expr.match(paramString, pos)
        if match is None:
            break
        params[match.group(1)] = match.group(2)
        pos = match.end()

    rj = CausticsRenderJob()
    return rj.Initialize(int(params['size']), float(params['speed']), float(params['amplitude']), float(params['tiling']), params['texture'])


blue.resMan.RegisterResourceConstructor('caustics', Caustics)

