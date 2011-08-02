import svc
import paperDollUtil
import bluepy
from ccConst import TEXTURE_RESOLUTIONS

class EvePaperDollClient(svc.paperDollClient):
    __guid__ = 'svc.evePaperDollClient'
    __replaceservice__ = 'paperDollClient'
    __notifyevents__ = svc.paperDollClient.__notifyevents__ + ['OnGraphicSettingsChanged']
    __dependencies__ = ['info', 'character', 'device']

    @bluepy.CCP_STATS_ZONE_METHOD
    def GetDollDNA(self, scene, entity, dollGender, dollDnaInfo, typeID):
        bloodlineID = self.info.GetBloodlineByTypeID(typeID).bloodlineID
        return self.character.GetDNAFromDBRowsForEntity(entity.entityID, dollDnaInfo, dollGender, bloodlineID)



    def SetupComponent(self, entity, component):
        svc.paperDollClient.SetupComponent(self, entity, component)
        if session.charid == entity.entityID:
            import paperDoll
            doll = component.doll.doll
            cs = paperDoll.CompressionSettings(compressTextures=True, generateMipmap=False)
            cs.compressNormalMap = False
            doll.compressionSettings = cs
        self.SetBoneOffsets(entity, component)



    def SetBoneOffsets(self, entity, component):
        avatar = self.GetPaperDollByEntityID(entity.entityID).avatar
        gender = self.GetDBGenderToPaperDollGender(component.gender)
        bloodlineID = self.info.GetBloodlineByTypeID(component.typeID).bloodlineID
        bloodline = paperDollUtil.bloodlineAssets[bloodlineID]
        self.character.AdaptDollAnimationData(bloodline, avatar, gender)



    def GetInitialTextureResolution(self):
        textureQuality = prefs.GetValue('charTextureQuality', self.device.GetDefaultCharTextureQuality())
        return TEXTURE_RESOLUTIONS[textureQuality]



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if 'charTextureQuality' in changes:
            textureQuality = prefs.GetValue('charTextureQuality', self.device.GetDefaultCharTextureQuality())
            resolution = TEXTURE_RESOLUTIONS[textureQuality]
            for character in self.paperDollManager:
                character.doll.SetTextureSize(resolution)
                character.Update()





