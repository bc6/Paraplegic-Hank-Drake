import util
import corpObject
import uthread
import sys
import blue

class CorporationRecruitmentO(corpObject.base):
    __guid__ = 'corpObject.recruitment'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self._CorporationRecruitmentO__lock = uthread.Semaphore()
        self.corpRecruitment = None
        self.myRecruitment = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change:
            self.myRecruitment = None
        if 'corpid' in change:
            self.corpRecruitment = None



    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' not in change:
            return 
        (oldID, newID,) = change['corpid']
        if newID is None:
            return 



    def OnCorporationRecruitmentAdChanged(self, corporationID, adID, change):
        recruitments = self.corpRecruitment
        if recruitments is not None:
            (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
            key = (corporationID, adID)
            if bAdd:
                header = None
                for example in recruitments.itervalues():
                    if type(example) == blue.DBRow:
                        header = example.__columns__
                    else:
                        header = example.header
                    break

                if header is None:
                    header = change.keys()
                line = []
                for columnName in header:
                    line.append(change[columnName][1])

                recruitment = util.Row(header, line)
                recruitments[key] = recruitment
            elif bRemove:
                if recruitments.has_key(key):
                    del recruitments[key]
            elif recruitments.has_key(key):
                recruitment = recruitments[key]
                for columnName in change.iterkeys():
                    setattr(recruitment, columnName, change[columnName][1])

                recruitments[key] = recruitment
        sm.GetService('corpui').OnCorporationRecruitmentAdChanged(corporationID, adID, change)



    def __len__(self):
        return len(self.GetRecruitmentAdsForCorporation())



    def GetRecruitmentAdsForCorporation(self):
        if self.corpRecruitment is None:
            self.corpRecruitment = {}
            recruitments = self.GetCorpRegistry().GetRecruitmentAdsForCorporation()
            for recruitment in recruitments:
                key = (recruitment.corporationID, recruitment.adID)
                self.corpRecruitment[key] = recruitment

        res = []
        for recruitment in self.corpRecruitment.itervalues():
            if res == []:
                if type(recruitment) == blue.DBRow:
                    res = util.Rowset(recruitment.__columns__)
                else:
                    res = util.Rowset(recruitment.header)
            res.lines.append(recruitment)

        return res



    def CreateRecruitmentAd(self, days, typeMask, allianceID, description = None, channelID = None, recruiters = (), title = None):
        return self.GetCorpRegistry().CreateRecruitmentAd(days, typeMask, allianceID, description, channelID, recruiters, title)



    def UpdateRecruitmentAd(self, adID, typeMask, description = None, channelID = None, recruiters = (), title = None, addedDays = 42):
        return self.GetCorpRegistry().UpdateRecruitmentAd(adID, typeMask, description, channelID, recruiters, title, addedDays)



    def DeleteRecruitmentAd(self, adID):
        return self.GetCorpRegistry().DeleteRecruitmentAd(adID)



    def GetRecruiters(self, corpID, adID):
        return self.GetCorpRegistry().GetRecruiters(corpID, adID)




