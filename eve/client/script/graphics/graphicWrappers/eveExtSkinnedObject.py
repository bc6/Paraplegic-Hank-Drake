import util
import trinity
import graphicWrappers
import uthread
import blue

class WodExtSkinnedObject(util.BlueClassNotifyWrap('trinity.WodExtSkinnedObject'), graphicWrappers.TrinityTransformMatrixMixinWrapper):
    __guid__ = 'graphicWrappers.WodExtSkinnedObject'

    @staticmethod
    def Wrap(triObject, resPath):
        WodExtSkinnedObject(triObject)
        triObject.AddNotify('transform', triObject._TransformChange)
        return triObject



    @staticmethod
    def ConvertToInterior(triObject, resPath):
        returnObject = trinity.Tr2IntSkinnedObject()
        returnObject.visualModel = triObject.visualModel
        returnObject.animationUpdater = triObject.animationUpdater
        returnObject.lowDetailModel = triObject.lowDetailModel
        returnObject.mediumDetailModel = triObject.mediumDetailModel
        returnObject.highDetailModel = triObject.highDetailModel
        return returnObject



    def AddToScene(self, scene):
        scene.AddAvatarToScene(self)
        if hasattr(self.animationUpdater, 'grannyRes'):

            def PlayAnimation():
                while not (self.animationUpdater.grannyRes.isGood and self.animationUpdater.grannyRes.isPrepared):
                    blue.synchro.Sleep(50)

                if self.animationUpdater.grannyRes.animationCount:
                    clipName = self.animationUpdater.grannyRes.GetAnimationName(0)
                    self.animationUpdater.PlayAnimationEx(clipName, 0, 0, 1)


            uthread.new(PlayAnimation).context = 'graphicWrappers.WodExtSkinnedObject::PlayAnimation'



    def RemoveFromScene(self, scene):
        scene.RemoveAvatarFromScene(self)



    def _TransformChange(self, transform):
        self.OnTransformChange()



    def OnTransformChange(self):
        pass




