import service
import copy
import random
import util
import uiutil
import bluepy
import uthread
import log

class CCSvc(service.Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.cc'
    __exportedcalls__ = {}
    __dependencies__ = []

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        util.LookupConstValue('', '')
        self.chars = None
        self.charCreationInfo = None
        (self.raceData, self.raceDataByID,) = (None, None)
        self.currentCharsPaperDollData = {}
        (self.bloodlineDataByRaceID, self.bloodlineDataByID,) = (None, None)
        self.dollState = None
        self.availableTypeIDs = None



    def GetCharactersToSelect(self, force = 0):
        self.LogInfo('CC::GetCharactersToSelect::force=%s' % force)
        if self.chars is None or force:
            chars = sm.RemoteSvc('charUnboundMgr').GetCharactersToSelect()
            self.chars = util.Rowset(chars.columns, list(chars))
        return self.chars



    def GetCharCreationInfo(self):
        if self.charCreationInfo is None:
            uthread.Lock(self)
            try:
                if self.charCreationInfo is None:
                    o = uiutil.Bunch()
                    o.update(sm.RemoteSvc('charUnboundMgr').GetCharCreationInfo())
                    o.update(sm.RemoteSvc('charUnboundMgr').GetCharNewExtraCreationInfo())
                    self.charCreationInfo = o

            finally:
                uthread.UnLock(self)

        return self.charCreationInfo



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetData(self, attribute, keyVal = None, shuffle = 0):
        ccinfo = self.GetCharCreationInfo()
        if attribute in ('races', 'bloodlines', 'ancestries', 'schools') and hasattr(ccinfo, attribute):
            retval = getattr(ccinfo, attribute)
            if keyVal:
                try:
                    retval = [ each for each in retval if getattr(each, keyVal[0]) == keyVal[1] ]
                except:
                    retval = []
            if shuffle:
                retval = copy.copy(retval)
                random.shuffle(retval)
            if len(retval) == 1:
                return retval[0]
            else:
                if len(retval) == 0:
                    return None
                return retval
        else:
            return None



    def GoBack(self, *args):
        gameui = sm.StartService('gameui')
        gameui.GoCharacterSelection()



    def ClearCurrentPaperDollData(self):
        self.currentCharsPaperDollData = {}



    def GetPaperDollData(self, charID):
        currentCharsPaperDollData = self.currentCharsPaperDollData.get(charID, None)
        if currentCharsPaperDollData is not None:
            return currentCharsPaperDollData
        uthread.Lock(self)
        try:
            if self.currentCharsPaperDollData.get(charID, None) is None:
                self.currentCharsPaperDollData[charID] = sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
            return self.currentCharsPaperDollData.get(charID, None)

        finally:
            uthread.UnLock(self)




    def ConvertAndSavePaperDoll(self, charID):
        sm.RemoteSvc('paperDollServer').ConvertAndSavePaperDoll(charID)
        self.StoreCurrentDollState(const.paperdollStateResculpting)



    def GoCharacterCreation(self, charID, gender, bloodlineID, dollState = None):
        uicore.layer.charactercreation.SetCharDetails(charID, gender, bloodlineID, dollState=dollState)



    def CreateCharacterWithDoll(self, charactername, bloodlineID, genderID, ancestryID, charInfo, portraitInfo, schoolID, *args):
        self.LogInfo('charInfo:', charInfo)
        charID = sm.RemoteSvc('charUnboundMgr').CreateCharacterWithDoll(charactername, bloodlineID, genderID, ancestryID, charInfo, portraitInfo, schoolID)
        return charID



    def UpdateExistingCharacterFull(self, charID, dollInfo, portraitInfo, dollExists):
        sm.RemoteSvc('paperDollServer').UpdateExistingCharacterFull(charID, 0, dollInfo, portraitInfo, dollExists)
        self.ClearCurrentPaperDollData()



    def UpdateExistingCharacterLimited(self, charID, dollInfo, portraitInfo, dollExists):
        dollData = dollInfo.copy()
        dollData.sculpts = []
        appearanceID = dollData.appearance.appearanceID
        self.LogInfo('UpdateExistingCharacterLimited', charID, appearanceID)
        if appearanceID == 0:
            appearanceID = None
        sm.RemoteSvc('paperDollServer').UpdateExistingCharacterLimited(charID, appearanceID, dollData, portraitInfo, dollExists)
        self.ClearCurrentPaperDollData()



    def UpdateExistingCharacterBloodline(self, charID, dollInfo, portraitInfo, dollExists, bloodlineID):
        print 'trying to UpdateExistingCharacterBloodline'
        self.ClearCurrentPaperDollData()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPortraitData(self, charID):
        data = sm.RemoteSvc('paperDollServer').GetPaperDollPortraitDataFor(charID)
        if len(data):
            return data[0]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetRaceData(self, *args):
        if self.raceData is None:
            self.PrepareRaceData()
        return self.raceData



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetRaceDataByID(self, *args):
        if self.raceDataByID is None:
            self.PrepareRaceData()
        return self.raceDataByID



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBloodlineDataByRaceID(self, *args):
        if self.bloodlineDataByRaceID is None:
            (self.bloodlineDataByRaceID, self.bloodlineDataByID,) = self.PrepareBloodlineData()
        return self.bloodlineDataByRaceID



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBloodlineDataByID(self, *args):
        if self.bloodlineDataByID is None:
            (self.bloodlineDataByRaceID, self.bloodlineDataByID,) = self.PrepareBloodlineData()
        return self.bloodlineDataByID



    @bluepy.CCP_STATS_ZONE_METHOD
    def PrepareRaceData(self, *args):
        raceDict = {}
        raceList = []
        for each in self.GetData('races', shuffle=1):
            if each.raceID in [const.raceCaldari,
             const.raceMinmatar,
             const.raceGallente,
             const.raceAmarr]:
                raceDict[each.raceID] = each
                raceList.append(each)

        (self.raceData, self.raceDataByID,) = (raceList, raceDict)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PrepareBloodlineData(self, *args):
        bloodlinesByRaceID = {}
        bloodlinesByID = {}
        for raceID in [const.raceCaldari,
         const.raceMinmatar,
         const.raceGallente,
         const.raceAmarr]:
            bloodlines = []
            for each in self.GetData('bloodlines', shuffle=1):
                if each.raceID == raceID:
                    bloodlines.append(each)
                    bloodlinesByID[each.bloodlineID] = each

            bloodlinesByRaceID[raceID] = bloodlines

        return (bloodlinesByRaceID, bloodlinesByID)



    def StoreCurrentDollState(self, state, *args):
        self.dollState = state



    def NoExistingCustomization(self, *arags):
        return self.dollState == const.paperdollStateNoExistingCustomization



    def ClearMyAvailabelTypeIDs(self, *args):
        self.availableTypeIDs = None



    def GetMyApparel(self):
        if getattr(self, 'availableTypeIDs', None) is not None:
            return self.availableTypeIDs
        availableTypeIDs = set()
        if session.stationid:
            try:
                inv = eve.GetInventory(const.containerHangar)
                availableTypeIDs.update({i.typeID for i in inv.List() if i.categoryID == const.categoryApparel})
                inv = eve.GetInventoryFromId(session.charid)
                availableTypeIDs.update({i.typeID for i in inv.List() if i.flagID == const.flagWardrobe})
            except Exception as e:
                log.LogException()
        self.availableTypeIDs = availableTypeIDs
        return self.availableTypeIDs




