#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/accountsvc.py
import uiconst
import service
import blue
import util
import localization
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L

class Account(service.Service):
    __exportedcalls__ = {'GetKeyMap': [],
     'GetEntryTypes': [],
     'GetJournal': [],
     'GetWalletDivisionsInfo': [],
     'GetDefaultContactCost': [],
     'SetDefaultContactCost': [],
     'AskYesNoQuestion': [service.ROLE_SERVICE]}
    __guid__ = 'svc.account'
    __notifyevents__ = ['ProcessSessionChange', 'OnAccountChange', 'ProcessUIRefresh']
    __servicename__ = 'account'
    __displayname__ = 'Accounting Service'

    def __init__(self):
        service.Service.__init__(self)
        self.dataLifeTime = MIN * 1
        self.data = {}
        self.walletDivisionsInfo = None
        self.defaultContactCost = None
        self.blocked = None
        self.nocharge = None

    def Run(self, memStream = None):
        self.LogInfo('Starting AccountSvc')
        self.journalData = {}
        self.ReleaseAccountSvc()

    def Stop(self, memStream = None):
        self.ReleaseAccountSvc()

    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change:
            self.ReleaseAccountSvc()

    def OnAccountChange(self, accountKey, ownerID, balance):
        self.journalData = {}

    def GetAccountSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            return self.moniker
        self.moniker = sm.RemoteSvc('account')
        return self.moniker

    def ReleaseAccountSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            self.moniker = None
            self.data = {}

    def ProcessUIRefresh(self):
        self.data = {}

    def GetStaticData(self, itemName, trCol = None, trID = None, *args):
        if not self.data.has_key(itemName):
            account = self.GetAccountSvc()
            data = getattr(account, itemName)(*args)
            for rec in data:
                messageID = getattr(rec, trID, None)
                translated = localization.GetByMessageID(messageID)
                setattr(rec, trCol, translated)

            self.data[itemName] = data
        return self.data[itemName]

    def GetKeyMap(self):
        return self.GetStaticData('GetKeyMap', 'keyName', 'keyNameID')

    def GetAccountKeyByID(self, accountKey):
        for rec in self.GetKeyMap():
            if rec.keyID == accountKey:
                return rec

    def GetEntryTypes(self):
        return self.GetStaticData('GetEntryTypes', 'entryTypeName', 'entryTypeNameID')

    def GetRefTypeKeyByID(self, entryTypeID):
        for rec in self.GetEntryTypes():
            if rec.entryTypeID == entryTypeID:
                return rec

    def GetJournal(self, accountKey, fromDate = None, entryTypeID = None, corpAccount = 0, transactionID = None, rev = 0):
        if entryTypeID in const.derivedTransactionParentMapping:
            entryTypeID = const.derivedTransactionParentMapping[entryTypeID]
        key = (accountKey,
         fromDate,
         entryTypeID,
         corpAccount,
         transactionID,
         rev)
        if key in self.journalData:
            return self.journalData[key]
        self.journalData[key] = self.GetAccountSvc().GetJournal(accountKey, fromDate, entryTypeID, corpAccount, transactionID, rev)
        return self.journalData[key]

    def GetJournalForAccounts(self, accountKeys, fromDate = None, entryTypeID = None, corpAccount = 0, transactionID = None, rev = 0):
        if entryTypeID in const.derivedTransactionParentMapping:
            entryTypeID = const.derivedTransactionParentMapping[entryTypeID]
        key = (str(accountKeys),
         fromDate,
         entryTypeID,
         corpAccount,
         transactionID,
         rev)
        if key in self.journalData:
            return self.journalData[key]
        self.journalData[key] = self.GetAccountSvc().GetJournalForAccounts(accountKeys, fromDate, entryTypeID, corpAccount, transactionID, rev)
        return self.journalData[key]

    def GetWalletDivisionsInfo(self, force = False):
        now = blue.os.GetWallclockTime()
        if self.walletDivisionsInfo is None or self.walletDivisionsInfo.expires < now or force:
            self.walletDivisionsInfo = util.KeyVal(info=self.GetAccountSvc().GetWalletDivisionsInfo(), expires=now + 5 * MIN)
        return self.walletDivisionsInfo.info

    def AskYesNoQuestion(self, question, props, defaultChoice = 1):
        if defaultChoice:
            defaultChoice = uiconst.ID_YES
        else:
            defaultChoice = uiconst.ID_NO
        return eve.Message(question, props, uiconst.YESNO, defaultChoice) == uiconst.ID_YES

    def SetDefaultContactCost(self, cost):
        if cost < 0:
            raise UserError('ContactCostNegativeAmount')
        self.GetAccountSvc().SetContactCost(cost)
        self.defaultContactCost = cost

    def GetDefaultContactCost(self):
        if self.defaultContactCost is None:
            self.defaultContactCost = self.GetAccountSvc().GetDefaultContactCost()
            if self.defaultContactCost is None:
                self.defaultContactCost = -1
        return self.defaultContactCost

    def BlockAll(self):
        self.GetAccountSvc().SetContactCost(None)
        self.defaultContactCost = -1