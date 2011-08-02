import util
import corpObject
import blue
import uthread

class SharesO(corpObject.base):
    __guid__ = 'corpObject.shares'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.myShares = None
        self.corpShares = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.corpShares = None
        if 'charid' in change:
            self.myShares = None



    def Reset(self):
        self.corpShares = None



    def GetSharesByShareholder(self, corpShares = 0):
        res = self.GetCorpRegistry().GetSharesByShareholder(corpShares)
        if res is None:
            return []
        if corpShares:
            res = self.corpShares = util.IndexRowset(res.header, res.lines, 'corporationID')
        else:
            res = self.myShares = util.IndexRowset(res.header, res.lines, 'corporationID')
        return res



    def GetShareholders(self):
        return self.GetCorpRegistry().GetShareholders(eve.session.corpid)



    def MoveCompanyShares(self, corporationID, toShareholderID, numberOfShares):
        return self.GetCorpRegistry().MoveCompanyShares(corporationID, toShareholderID, numberOfShares)



    def MovePrivateShares(self, corporationID, toShareholderID, numberOfShares):
        return self.GetCorpRegistry().MovePrivateShares(corporationID, toShareholderID, numberOfShares)



    def OnShareChange(self, shareholderID, corporationID, change):
        uthread.new(self.OnShareChange_thread, shareholderID, corporationID, change).context = 'svc.corp.OnShareChange'



    def OnShareChange_thread(self, shareholderID, corporationID, change):
        if self.myShares is None and self.corpShares is None:
            return 
        IWasAShareholderInMyCorp = self.myShares is not None and self.myShares.has_key(eve.session.corpid)
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        rowset = None
        key = corporationID
        if shareholderID == eve.session.charid:
            rowset = self.myShares
        else:
            rowset = self.corpShares
        if rowset is not None and type(rowset) != type([]) and len(rowset) > 0:
            if bAdd:
                for row in rowset.itervalues():
                    line = []
                    for columnName in row.header:
                        line.append(change[columnName][1])

                    rowset[key] = line
                    break

            elif bRemove:
                if rowset.has_key(key):
                    del rowset[key]
            elif rowset.has_key(key):
                row = rowset[key]
                for columnName in change.iterkeys():
                    setattr(row, columnName, change[columnName][1])

        IAmAShareholderInMyCorp = self.myShares is not None and self.myShares.has_key(eve.session.corpid)
        if IAmAShareholderInMyCorp != IWasAShareholderInMyCorp:
            sm.GetService('corpui').ResetWindow(bShowIfVisible=1)




