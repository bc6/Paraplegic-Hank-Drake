#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/cylinderLightClient.py
import cef
import graphics
import graphicWrappers
import trinity
import util

class CylinderLightClientComponent:
    __guid__ = 'component.CylinderLightClientComponent'


class CylinderLightClient(graphics.LightClient):
    __guid__ = 'svc.cylinderLightClient'
    __componentTypes__ = [cef.CylinderLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = CylinderLightClientComponent()
        renderObject = trinity.Tr2InteriorCylinderLight()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        component.originalPrimaryLighting = bool(state['primaryLighting'])
        component.originalSecondaryLighting = bool(state['secondaryLighting'])
        component.performanceLevel = state['performanceLevel']
        renderObject.SetColor((state['red'], state['green'], state['blue']))
        renderObject.SetRadius(state['radius'])
        renderObject.SetLength(state['length'])
        renderObject.SetFalloff(state['falloff'])
        if 'sectorAngleOuter' in state:
            renderObject.sectorAngleOuter = float(state['sectorAngleOuter'])
        if 'sectorAngleInner' in state:
            renderObject.sectorAngleInner = float(state['sectorAngleInner'])
        renderObject.primaryLighting = bool(state['primaryLighting'])
        renderObject.secondaryLighting = bool(state['secondaryLighting'])
        renderObject.secondaryLightingMultiplier = state['secondaryLightingMultiplier']
        renderObject.projectedTexturePath = state['projectedTexturePath'].encode()
        renderObject.isStatic = bool(state['isStatic'])
        renderObject.specularIntensity = float(state.get('specularIntensity', '1'))
        renderObject.useKelvinColor = bool(state['useKelvinColor'])
        if renderObject.useKelvinColor:
            renderObject.kelvinColor.temperature = state['temperature']
            renderObject.kelvinColor.tint = state['tint']
            renderObject.kelvinColor.whiteBalance = int(state['whiteBalance'])
        component.useBoundingBox = bool(state['useBoundingBox'])
        if component.useBoundingBox:
            component.bbPos = util.UnpackStringToTuple(state['bbPos'])
            component.bbRot = util.UnpackStringToTuple(state['bbRot'])
            component.bbScale = util.UnpackStringToTuple(state['bbScale'])
            renderObject.boundingBox = trinity.Tr2InteriorOrientedBoundingBox()
        if '_spawnID' in state:
            component.renderObject.name = self.GetName(state['_spawnID'])
        return component

    def ApplyPerformanceLevelLightDisable(self, entity):
        component = entity.GetComponent('cylinderLight')
        if component is None:
            return
        appPerformanceLevel = sm.GetService('device').GetAppFeatureState('Interior.lightPerformanceLevel', 2)
        if component.performanceLevel > appPerformanceLevel:
            component.renderObject.primaryLighting = False
            component.renderObject.secondaryLighting = False
        else:
            component.renderObject.primaryLighting = component.originalPrimaryLighting
            component.renderObject.secondaryLighting = component.originalSecondaryLighting