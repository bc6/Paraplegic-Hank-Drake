#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\trinity\interiorVisualizations.py
import trinity
import log
import blue

class VisualizationBase(object):
    displayName = 'Base Visualization, do not use'

    def __init__(self):
        self.originalStepStates = []

    def SetStepAttr(self, rj, stepKey, attr, value):
        if rj.HasStep(stepKey):
            self.originalStepStates.append((stepKey, attr, getattr(rj.GetStep(stepKey), attr)))
            rj.SetStepAttr(stepKey, attr, value)

    def RestoreStepStates(self, rj):
        for step, attr, state in self.originalStepStates:
            rj.SetStepAttr(step, attr, state)


class VisualizerStepBase(VisualizationBase):
    displayName = 'VisualizerStepBase'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_NONE

    def __init__(self):
        VisualizationBase.__init__(self)
        self.renderJobs = []
        self.wireframeModeEnabled = False
        self.ssaoState = None

    def ApplyVisualization(self, rj):
        self.renderJobs.append(rj)
        rj.AddStep('SET_VISUALIZATION', trinity.TriStepSetVisualizationMode(rj.GetScene(), self.visualizationMode))
        ssao = rj.GetStep('RENDER_SSAO')
        if ssao is not None:
            self.ssaoState = ssao.enabled
        else:
            self.ssaoState = None
        self.SetStepAttr(rj, 'RENDER_SSAO', 'enabled', False)

    def RemoveVisualization(self, rj):
        rj.RemoveStep('SET_VISUALIZATION')
        self.SetEnableWireframeMode(False)
        if self.ssaoState is not None:
            ssao = rj.GetStep('RENDER_SSAO')
            if ssao is not None:
                ssao.enabled = self.ssaoState
        self.ssaoState = None
        if rj.GetScene():
            rj.GetScene().visualizeMethod = 0
        self.RestoreStepStates(rj)
        self.renderJobs.remove(rj)

    def SetEnableWireframeMode(self, enable):
        self.wireframeModeEnabled = enable
        if self.wireframeModeEnabled:
            for eachRenderJob in self.renderJobs:
                eachRenderJob.AddStep('ENABLE_WIREFRAME', trinity.TriStepEnableWireframeMode(True))
                eachRenderJob.AddStep('RESTORE_WIREFRAME', trinity.TriStepEnableWireframeMode(False))

        else:
            for eachRenderJob in self.renderJobs:
                eachRenderJob.RemoveStep('ENABLE_WIREFRAME')
                eachRenderJob.RemoveStep('RESTORE_WIREFRAME')


class EveAlbedoVisualization(VisualizationBase):
    displayName = 'Albedo'

    def ApplyVisualization(self, rj):
        trinity.AddGlobalSituationFlags(['OPT_VISUALIZE_TEXTURES'])
        trinity.RebindAllShaderMaterials()

    def RemoveVisualization(self, rj):
        trinity.RemoveGlobalSituationFlags(['OPT_VISUALIZE_TEXTURES'])
        trinity.RebindAllShaderMaterials()


class DisableVisualization(VisualizerStepBase):
    displayName = 'Disable visualizations'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_NONE

    def ApplyVisualization(self, rj):
        self.renderJobs.append(rj)
        rj.AddStep('SET_VISUALIZATION', trinity.TriStepSetVisualizationMode(rj.GetScene(), self.visualizationMode))


class WhiteVisualization(VisualizerStepBase):
    displayName = 'White'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_WHITE


class ObjectNormalVisualization(VisualizerStepBase):
    displayName = 'Object Normal'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_OBJECT_NORMAL


class TangentVisualization(VisualizerStepBase):
    displayName = 'Tangent'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_TANGENT


class BiTangentVisualization(VisualizerStepBase):
    displayName = 'BiTangent'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_BITANGENT


class TexCoord0Visualization(VisualizerStepBase):
    displayName = 'TexCoord0'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_TEXCOORD0


class TexCoord1Visualization(VisualizerStepBase):
    displayName = 'TexCoord1'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_TEXCOORD1


class TexelDensityVisualization(VisualizerStepBase):
    displayName = 'Texel Density'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_TEXELDENSITY0


class NormalMapVisualization(VisualizerStepBase):
    displayName = 'Normal Map Only'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_NORMALMAP


class DiffuseMapVisualization(VisualizerStepBase):
    displayName = 'Diffuse Map'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_DIFFUSEMAP


class SpecularMapVisualization(VisualizerStepBase):
    displayName = 'Specular Map'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_SPECULARMAP


class OverdrawVisualization(VisualizerStepBase):
    displayName = 'Overdraw'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_OVERDRAW


class EnlightenOnlyVisualization(VisualizerStepBase):
    displayName = 'Enlighten Lighting Only'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_ONLY


class EnlightenTargetDetailVisualization(VisualizerStepBase):
    displayName = 'Enlighten Target/Detail'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_TARGET_DETAIL


class EnlightenOutputDensityVisualization(VisualizerStepBase):
    displayName = 'Enlighten Output Density'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_OUTPUT_DENSITY


class EnlightenAlbedoVisualization(VisualizerStepBase):
    displayName = 'Enlighten Albedo'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_ALBEDO


class EnlightenEmissiveVisualization(VisualizerStepBase):
    displayName = 'Enlighten Emissive'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_EMISSIVE


class EnlightenObjectTexcoordVisualization(VisualizerStepBase):
    displayName = 'Enlighten Object Texcoords'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_OBJECT_TEXCOORD


class EnlightenNaughtyPixelsVisualization(VisualizerStepBase):
    displayName = 'Enlighten Naughty Pixels'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_NAUGHTY_PIXELS


class EnlightenDetailChartsVisualization(VisualizerStepBase):
    displayName = 'Enlighten Detail Mesh Charts'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_CHARTS


class EnlightenTargetChartsVisualization(VisualizerStepBase):
    displayName = 'Enlighten Target Mesh Charts'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_EN_TARGET_CHARTS


class DepthVisualization(VisualizerStepBase):
    displayName = 'Depth'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_DEPTH


class AllLightingVisualization(VisualizerStepBase):
    displayName = 'All Lighting'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_ALL_LIGHTING


class PrePassLightNormalVisualization(VisualizerStepBase):
    displayName = 'PrePass Lighting Normal'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_NORMALS


class PrePassLightDepthVisualization(VisualizerStepBase):
    displayName = 'PrePass Lighting Depth'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_DEPTH


class PrePassLightWorldPositionVisualization(VisualizerStepBase):
    displayName = 'PrePass Lighting World Position'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_WORLD_POSITION


class PrePassLightingOnlyVisualization(VisualizerStepBase):
    displayName = 'PrePass Lighting Only'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_LIGHTING


class PrePassLightOverdrawVisualization(VisualizerStepBase):
    displayName = 'Light Overdraw'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_LIGHT_OVERDRAW


class PrePassLightingDiffuseVisualization(VisualizerStepBase):
    displayName = 'PrePass Diffuse Lighting Only'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_DIFFUSE_LIGHTING


class PrePassLightingSpecularVisualization(VisualizerStepBase):
    displayName = 'PrePass Specular Lighting Only'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_LIGHT_PRE_PASS_SPECULAR_LIGHTING


class OcclusionVisualization(VisualizerStepBase):
    displayName = 'Occlusion Geometry'
    visualizationMode = trinity.Tr2InteriorVisualizerMethod.VM_OCCLUSION


class LightVolumeVisualizationBase(VisualizationBase):
    displayName = 'Light Volumes'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION

    def __init__(self):
        VisualizationBase.__init__(self)
        self.lightStates = []

    def ShouldLightBeVisualized(self, light):
        return True

    def ApplyVisualization(self, rj):
        scene = rj.GetScene()
        if scene is not None:
            for light in scene.lights:
                if self.ShouldLightBeVisualized(light):
                    self.lightStates.append((blue.BluePythonWeakRef(light), light.renderDebugInfo, light.renderDebugType))
                    light.renderDebugInfo = True
                    light.renderDebugType = self.lightDebugRenderType

    def RemoveVisualization(self, rj):
        self.RestoreStepStates(rj)
        for lightWR, rDI, rDT in self.lightStates:
            light = lightWR.object
            if light is not None:
                light.renderDebugInfo = rDI
                light.renderDebugType = rDT


class LightVolumeColorBaseVisualization(LightVolumeVisualizationBase):
    displayName = 'Light Volume base'

    def ShouldLightBeVisualized(self, light):
        return True


class LightVolumeWhiteVisualization(LightVolumeColorBaseVisualization):
    displayName = 'Light Volumes (White)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_WHITE_VOLUMES


class LightVolumeNormalVisualization(LightVolumeColorBaseVisualization):
    displayName = 'Light Volumes (Source)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_LIGHT_COLOR


class LightVolumeShadowResolutionVisualization(LightVolumeColorBaseVisualization):
    displayName = 'Light Volumes (Shadow Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION


class LightVolumeShadowRelativeResolutionVisualization(LightVolumeColorBaseVisualization):
    displayName = 'Light Volumes (Shadow Relative Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RELATIVE_RESOLUTION


class PrimaryLightVolumeColorBaseVisualization(LightVolumeVisualizationBase):
    displayName = 'Primary Light Volume base'

    def ShouldLightBeVisualized(self, light):
        if getattr(light, 'primaryLighting', True):
            return True
        else:
            return False


class PrimaryLightVolumeWhiteVisualization(PrimaryLightVolumeColorBaseVisualization):
    displayName = 'Primary Light Volumes (White)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_WHITE_VOLUMES


class PrimaryLightVolumeNormalVisualization(PrimaryLightVolumeColorBaseVisualization):
    displayName = 'Primary Light Volumes (Source)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_LIGHT_COLOR


class PrimaryLightVolumeShadowResolutionVisualization(PrimaryLightVolumeColorBaseVisualization):
    displayName = 'Primary Light Volumes (Shadow Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION


class PrimaryLightVolumeShadowRelativeResolutionVisualization(PrimaryLightVolumeColorBaseVisualization):
    displayName = 'Primary Light Volumes (Shadow Relative Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RELATIVE_RESOLUTION


class SecondaryLightVolumeColorBaseVisualization(LightVolumeVisualizationBase):
    displayName = 'Secondary Light Volume base'

    def ShouldLightBeVisualized(self, light):
        if getattr(light, 'secondaryLighting', True):
            return True
        else:
            return False


class SecondaryLightVolumeWhiteVisualization(SecondaryLightVolumeColorBaseVisualization):
    displayName = 'Secondary Light Volumes (White)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_WHITE_VOLUMES


class SecondaryLightVolumeNormalVisualization(SecondaryLightVolumeColorBaseVisualization):
    displayName = 'Secondary Light Volumes (Source)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_LIGHT_COLOR


class SecondaryLightVolumeShadowResolutionVisualization(SecondaryLightVolumeColorBaseVisualization):
    displayName = 'Secondary Light Volumes (Shadow Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION


class SecondaryLightVolumeShadowRelativeResolutionVisualization(SecondaryLightVolumeColorBaseVisualization):
    displayName = 'Secondary Light Volumes (Shadow Relative Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RELATIVE_RESOLUTION


class ShadowcastingLightVolumeColorBaseVisualization(LightVolumeVisualizationBase):
    displayName = 'Shadowcasting Light Volume base'

    def ShouldLightBeVisualized(self, light):
        if getattr(light, 'shadowCasterTypes', True):
            return True
        else:
            return False


class ShadowcastingLightVolumeWhiteVisualization(ShadowcastingLightVolumeColorBaseVisualization):
    displayName = 'Shadowcasting Light Volumes (White)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_WHITE_VOLUMES


class ShadowcastingLightVolumeNormalVisualization(ShadowcastingLightVolumeColorBaseVisualization):
    displayName = 'Shadowcasting Light Volumes (Source)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_LIGHT_COLOR


class ShadowcastingLightVolumeShadowResolutionVisualization(ShadowcastingLightVolumeColorBaseVisualization):
    displayName = 'Shadowcasting Light Volumes (Shadow Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION


class ShadowcastingLightVolumeShadowRelativeResolutionVisualization(ShadowcastingLightVolumeColorBaseVisualization):
    displayName = 'Shadowcasting Light Volumes (Shadow Relative Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RELATIVE_RESOLUTION


class TransparentLightVolumeColorBaseVisualization(LightVolumeVisualizationBase):
    displayName = 'Transparent Light Volume base'

    def ShouldLightBeVisualized(self, light):
        if getattr(light, 'affectTransparentObjects', True):
            return True
        else:
            return False


class TransparentLightVolumeWhiteVisualization(TransparentLightVolumeColorBaseVisualization):
    displayName = 'Transparent Light Volumes (White)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_WHITE_VOLUMES


class TransparentLightVolumeNormalVisualization(TransparentLightVolumeColorBaseVisualization):
    displayName = 'Transparent Light Volumes (Source)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_LIGHT_COLOR


class TransparentLightVolumeShadowResolutionVisualization(TransparentLightVolumeColorBaseVisualization):
    displayName = 'Transparent Light Volumes (Shadow Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RESOLUTION


class TransparentLightVolumeShadowRelativeResolutionVisualization(TransparentLightVolumeColorBaseVisualization):
    displayName = 'Transparent Light Volumes (Shadow Relative Resolution)'
    lightDebugRenderType = trinity.Tr2InteriorLightDebugRenderMode.DI_SHADOW_RELATIVE_RESOLUTION


class WoDEnlightenOnlyVisualization(VisualizerStepBase):
    displayName = 'Enlighten Lighting Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         1.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.SetStepAttr('RENDER_LIGHTS', 'enabled', False)
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])
        rj.SetStepAttr('RENDER_LIGHTS', 'enabled', True)


class WoDDiffuseLightOnlyVisualization(VisualizerStepBase):
    displayName = 'Diffuse Lighting Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         1.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDSpecularLightOnlyVisualization(VisualizerStepBase):
    displayName = 'Specular Lighting Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [1.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDDiffuseOnlyVisualization(VisualizerStepBase):
    displayName = 'Diffuse Color Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         1.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDSpecularOnlyVisualization(VisualizerStepBase):
    displayName = 'Specular Color Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         1.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDFinalDiffuseVisualization(VisualizerStepBase):
    displayName = 'Diffuse result Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         1.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDFinalSpecularVisualization(VisualizerStepBase):
    displayName = 'Specular result Only'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         1.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDNormalsVisualization(VisualizerStepBase):
    displayName = 'Normals as Color'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [1.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])


class WoDSurfaceStylesVisualization(VisualizerStepBase):
    displayName = 'Surface Style IDs'

    def __init__(self):
        VisualizerStepBase.__init__(self)

    def ApplyVisualization(self, rj):
        VisualizerStepBase.ApplyVisualization(self, rj)
        rj.gatherShader.parameters['VisFlags1'].value = [0.0,
         0.0,
         0.0,
         0.0]
        rj.gatherShader.parameters['VisFlags2'].value = [0.0,
         0.0,
         0.0,
         1.0]
        rj.gatherShader.BindLowLevelShader(['viz'])

    def RemoveVisualization(self, rj):
        VisualizerStepBase.RemoveVisualization(self, rj)
        rj.gatherShader.BindLowLevelShader(['none'])