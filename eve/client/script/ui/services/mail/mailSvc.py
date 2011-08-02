import service
import blue
import sys
import log
import os
import const
import uiconst
import shelve
import util
import zlib
import form
import xtriui
import uiutil
import uthread
import uix
import copy
import uicls
MAIL_PATH = blue.rot.PathToFilename('cache:/EveMail/')
BODIES_IN_CACHE = 30
MAIL_FILE_HEADER_VERSION = 5
MAIL_FILE_BODY_VERSION = 1
ALL_LABELS = 255
swatchColors = {0: ('ffffff', 0),
 1: ('ffff01', 1),
 2: ('ff6600', 2),
 3: ('fe0000', 3),
 4: ('9a0000', 4),
 5: ('660066', 5),
 6: ('0000fe', 6),
 7: ('0099ff', 7),
 8: ('01ffff', 8),
 9: ('00ff33', 9),
 10: ('349800', 10),
 11: ('006634', 11),
 12: ('666666', 12),
 13: ('999999', 13),
 14: ('e6e6e6', 14),
 15: ('ffffcd', 15),
 16: ('99ffff', 16),
 17: ('ccff9a', 17)}

class mailSvc(service.Service):
    __guid__ = 'svc.mailSvc'
    __displayname__ = 'Mail service'
    __exportedcalls__ = {'MoveMessagesToTrash': [],
     'MoveMessagesFromTrash': [],
     'MarkMessagesAsUnread': [],
     'MarkMessagesAsRead': [],
     'MoveAllToTrash': [],
     'MoveToTrashByLabel': [],
     'MoveToTrashByList': [],
     'MoveAllFromTrash': [],
     'MarkAllAsUnread': [],
     'MarkAsUnreadByLabel': [],
     'MarkAsUnreadByList': [],
     'MarkAllAsRead': [],
     'MarkAsReadByLabel': [],
     'MarkAsReadByList': [],
     'EmptyTrash': [],
     'DeleteMails': [],
     'GetBody': [],
     'GetMailsByLabelOrListID': [],
     'SyncMail': [],
     'GetLabels': [],
     'EditLabel': [],
     'CreateLabel': [],
     'DeleteLabel': [],
     'AssignLabels': [],
     'RemoveLabels': [],
     'SaveChangesToDisk': [],
     'ClearCache': [],
     'SendMail': [],
     'IsFileCacheCorrupted': [],
     'PrimeOwners': []}
    __notifyevents__ = ['OnMailSent',
     'OnMailDeleted',
     'OnMailUndeleted',
     'OnSessionChanged']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.mailSynced = 0
        self.cacheFileCorruption = False



    def Run(self, ms = None):
        self.state = service.SERVICE_START_PENDING
        self.mailMgr = sm.RemoteSvc('mailMgr')
        self.mailHeaders = {}
        self.mailBodies = {}
        self.mailBodiesOrder = []
        self.labels = None
        self.needToSaveHeaders = False
        self.isSaving = False
        self.blinkTab = False
        self.blinkNeocom = False
        self.donePrimingRecipients = False
        if session.charid:
            self.mailFileHeaders = MAIL_PATH + 'mailheaders_' + str(session.charid)
            self.mailFileBodies = MAIL_PATH + 'mailbodies_' + str(session.charid)
        try:
            if not os.path.exists(MAIL_PATH):
                os.mkdir(MAIL_PATH)
        except:
            self.LogError('Error creating mail cache folder. charid:', str(session.charid))
            self.cacheFileCorruption = True
            self.TryCloseMailWindow()
            raise UserError('MailCacheFileError')
        self.state = service.SERVICE_RUNNING



    def OnSessionChanged(self, isremote, session, change):
        if 'charid' in change and session.charid:
            self.mailFileHeaders = MAIL_PATH + 'mailheaders_' + str(session.charid)
            self.mailFileBodies = MAIL_PATH + 'mailbodies_' + str(session.charid)



    def PrimeOwners(self, owners):
        uthread.Lock(self, 'Prime')
        try:
            toprime = []
            for ownerID in owners:
                if ownerID not in cfg.eveowners:
                    toprime.append(ownerID)

            if len(toprime) > 0:
                primed = self.mailMgr.PrimeOwners(toprime)
                for ownerID in primed:
                    cfg.eveowners.data[ownerID] = primed[ownerID]


        finally:
            uthread.UnLock(self, 'Prime')




    def TrySyncMail(self):
        if not self.mailSynced:
            try:
                self.SyncMail()
            except UserError as e:
                raise 
            except Exception as e:
                log.LogException('mail failed to load')
                raise UserError('CustomInfo', {'info': mls.UI_EVEMAIL_FAILEDTOLOAD})



    def SyncMail(self):
        self.LogInfo('Syncing mail')
        uthread.Lock(self)
        try:
            if self._mailSvc__ReadFromHeaderFile('version') != MAIL_FILE_HEADER_VERSION:
                self._mailSvc__ClearHeaderCache()
                self._mailSvc__WriteToHeaderFile('version', MAIL_FILE_HEADER_VERSION)
            if self._mailSvc__ReadFromBodyFile('version') != MAIL_FILE_BODY_VERSION:
                self._mailSvc__ClearBodyCache()
                self._mailSvc__WriteToBodyFile('version', MAIL_FILE_BODY_VERSION)
            self.mailHeaders = self._mailSvc__ReadFromHeaderFile('mail')
            if self.mailHeaders is None:
                self.mailHeaders = {}
                self._mailSvc__WriteToHeaderFile('mail', {})
            lastID = 0
            firstID = sys.maxint
            for messageID in self.mailHeaders:
                if messageID > lastID:
                    lastID = messageID
                if messageID < firstID:
                    firstID = messageID

            if lastID == 0:
                firstID = None
            mailbox = self.mailMgr.SyncMail(firstID, lastID)
            toPrime = set()
            incoming = mailbox.newMail
            if mailbox.oldMail is not None:
                incoming.extend(mailbox.oldMail)
            for mailRow in incoming:
                toPrime.add(mailRow.senderID)
                toListID = mailRow.toListID
                toCharacterIDs = []
                if mailRow.toCharacterIDs:
                    toCharacterIDs = [ int(x) for x in mailRow.toCharacterIDs.split(',') ]
                m = util.KeyVal(messageID=mailRow.messageID, senderID=mailRow.senderID, toCharacterIDs=toCharacterIDs, toListID=toListID, toCorpOrAllianceID=mailRow.toCorpOrAllianceID, subject=mailRow.title, sentDate=mailRow.sentDate)
                self.mailHeaders[mailRow.messageID] = m

            toDelete = self.mailHeaders.keys()
            toFetch = {}
            for statusRow in mailbox.mailStatus:
                if statusRow.messageID not in self.mailHeaders:
                    m = util.KeyVal(messageID=statusRow.messageID, read=statusRow.statusMask & const.mailStatusMaskRead == const.mailStatusMaskRead, replied=statusRow.statusMask & const.mailStatusMaskReplied == const.mailStatusMaskReplied, forwarded=statusRow.statusMask & const.mailStatusMaskForwarded == const.mailStatusMaskForwarded, trashed=statusRow.statusMask & const.mailStatusMaskTrashed == const.mailStatusMaskTrashed, statusMask=statusRow.statusMask, labels=self.GetLabelMaskAsList(statusRow.labelMask), labelMask=statusRow.labelMask)
                    toFetch[statusRow.messageID] = m
                else:
                    toDelete.remove(statusRow.messageID)
                    mail = self.mailHeaders[statusRow.messageID]
                    if getattr(mail, 'statusMask', None) != statusRow.statusMask:
                        mail.statusMask = statusRow.statusMask
                        mail.read = mail.statusMask & const.mailStatusMaskRead == const.mailStatusMaskRead
                        mail.replied = mail.statusMask & const.mailStatusMaskReplied == const.mailStatusMaskReplied
                        mail.forwarded = mail.statusMask & const.mailStatusMaskForwarded == const.mailStatusMaskForwarded
                        mail.trashed = mail.statusMask & const.mailStatusMaskTrashed == const.mailStatusMaskTrashed
                    if getattr(mail, 'labelMask', None) != statusRow.labelMask:
                        mail.labelMask = statusRow.labelMask
                        mail.labels = self.GetLabelMaskAsList(mail.labelMask)
                    if mail.statusMask & const.mailStatusMaskAutomated > 0 and mail.senderID == mail.toListID and mail.senderID in toPrime:
                        toPrime.remove(mail.senderID)

            if len(toFetch) > 0:
                revivedMail = self.mailMgr.GetMailHeaders(toFetch.keys())
                for mailRow in revivedMail:
                    toListID = mailRow.toListID
                    toCharacterIDs = []
                    if mailRow.toCharacterIDs:
                        toCharacterIDs = [ int(x) for x in mailRow.toCharacterIDs.split(',') ]
                    mail = toFetch[mailRow.messageID]
                    mail.senderID = mailRow.senderID
                    mail.toCharacterIDs = toCharacterIDs
                    mail.toListID = toListID
                    mail.toCorpOrAllianceID = mailRow.toCorpOrAllianceID
                    mail.subject = mailRow.title
                    mail.sentDate = mailRow.sentDate
                    if mail.statusMask & const.mailStatusMaskAutomated == 0 or mail.senderID != mail.toListID:
                        toPrime.add(mail.senderID)
                    self.mailHeaders[mailRow.messageID] = mail

            self.PrimeOwners(list(toPrime))
            for mail in self.mailHeaders.itervalues():
                if hasattr(mail, 'senderName'):
                    continue
                if mail.senderID is None:
                    raise RuntimeError('Invalid mail item', mail)
                if mail.statusMask & const.mailStatusMaskAutomated and mail.senderID == mail.toListID:
                    mail.senderName = sm.GetService('mailinglists').GetDisplayName(mail.senderID)
                else:
                    try:
                        mail.senderName = cfg.eveowners.Get(mail.senderID).name
                    except IndexError:
                        mail.senderName = mls.UI_GENERIC_UNKNOWN

            for messageID in toDelete:
                del self.mailHeaders[messageID]
                self._mailSvc__DeleteFromBodyFile(messageID)

            self._mailSvc__WriteToHeaderFile('mail', self.mailHeaders)
            self.mailSynced = 1

        finally:
            uthread.UnLock(self)

        self.LogInfo('Done syncing mail')



    def GetLabelMaskAsList(self, mask):
        if mask < 0:
            raise RuntimeError('Invalid label mask', mask)
        counter = 0
        labels = []
        while mask != 0:
            (mask, bitSet,) = divmod(mask, 2)
            if bitSet == 1:
                labels.append(pow(2, counter))
            counter += 1

        return labels



    def GetUnreadCounts(self):
        self.LogInfo('GetUnreadCounts')
        unreadCounts = util.KeyVal(labels={}, lists={})
        totalUnread = 0
        for (messageID, message,) in self.mailHeaders.iteritems():
            if not message.read and not message.trashed:
                totalUnread += 1
                mask = message.labelMask
                counter = 0
                while mask != 0:
                    (mask, bitSet,) = divmod(mask, 2)
                    if bitSet == 1:
                        labelID = pow(2, counter)
                        if labelID in unreadCounts.labels:
                            unreadCounts.labels[labelID] += 1
                        else:
                            unreadCounts.labels[labelID] = 1
                    counter += 1

                if message.toListID is not None:
                    if message.toListID in unreadCounts.lists:
                        unreadCounts.lists[message.toListID] += 1
                    else:
                        unreadCounts.lists[message.toListID] = 1

        unreadCounts.labels[None] = totalUnread
        self.LogInfo('unreadCounts:', unreadCounts)
        return unreadCounts



    def CheckShouldStopBlinking(self, *args):
        allUnreadGroups = self.GetUnreadCounts()
        allUnread = allUnreadGroups.labels.get(None, 0)
        if allUnread == 0:
            self.StopMailBlinking()



    def StopMailBlinking(self, *args):
        self.SetBlinkTabState(False)
        sm.ScatterEvent('OnMailStartStopBlinkingTab', 'mail', 0)
        self.SetBlinkNeocomState(False)
        if not settings.user.ui.Get('notification_blinkNecom', 1) or sm.GetService('notificationSvc').ShouldNeocomBlink() == False:
            sm.GetService('neocom').BlinkOff('mail')



    def MoveMessagesToTrash(self, messageIDs):
        self.LogInfo('Move to trash', messageIDs)
        self.mailMgr.MoveToTrash(messageIDs)
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            mail.trashed = True
            mail.statusMask = mail.statusMask | const.mailStatusMaskTrashed

        self.needToSaveHeaders = True
        self.CheckShouldStopBlinking()



    def MoveMessagesFromTrash(self, messageIDs):
        self.LogInfo('Move from trash', messageIDs)
        self.mailMgr.MoveFromTrash(messageIDs)
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            mail.trashed = False
            mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskTrashed

        self.needToSaveHeaders = True



    def MarkMessagesAsUnread(self, messageIDs):
        self.LogInfo('Mark as unread', messageIDs)
        self.mailMgr.MarkAsUnread(messageIDs)
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            mail.read = False
            mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskRead

        self.needToSaveHeaders = True
        sm.ScatterEvent('OnMailCountersUpdate')



    def MarkMessagesAsRead(self, messageIDs, notifyServer = True):
        self.LogInfo('Mark as read', messageIDs, notifyServer)
        if notifyServer:
            self.mailMgr.MarkAsRead(messageIDs)
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            mail.read = True
            mail.statusMask = mail.statusMask | const.mailStatusMaskRead

        self.needToSaveHeaders = True
        sm.ScatterEvent('OnMailCountersUpdate')
        self.CheckShouldStopBlinking()



    def MoveAllToTrash(self):
        self.LogInfo('Move all to trash')
        self.mailMgr.MoveAllToTrash()
        for mail in self.mailHeaders.itervalues():
            mail.trashed = True
            mail.statusMask = mail.statusMask | const.mailStatusMaskTrashed

        self.needToSaveHeaders = True



    def MoveToTrashByLabel(self, labelID):
        self.LogInfo('Move label to trash', labelID)
        self.mailMgr.MoveToTrashByLabel(labelID)
        for mail in self.mailHeaders.itervalues():
            if mail.labelMask & labelID == labelID:
                mail.trashed = True
                mail.statusMask = mail.statusMask | const.mailStatusMaskTrashed

        self.needToSaveHeaders = True



    def MoveToTrashByList(self, listID):
        self.LogInfo('Move list to trash', listID)
        self.mailMgr.MoveToTrashByList(listID)
        for mail in self.mailHeaders.itervalues():
            if mail.toListID is not None and listID == mail.toListID:
                mail.trashed = True
                mail.statusMask = mail.statusMask | const.mailStatusMaskTrashed

        self.needToSaveHeaders = True



    def MarkAllAsUnread(self):
        self.LogInfo('Mark all as unread')
        self.mailMgr.MarkAllAsUnread()
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed:
                mail.read = False
                mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MarkAsUnreadByLabel(self, labelID):
        self.LogInfo('Mark label unread', labelID)
        self.mailMgr.MarkAsUnreadByLabel(labelID)
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed and mail.labelMask & labelID == labelID:
                mail.read = False
                mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MarkAsUnreadByList(self, listID):
        self.LogInfo('Mark list unread', listID)
        self.mailMgr.MarkAsUnreadByList(listID)
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed and mail.toListID is not None and listID == mail.toListID:
                mail.read = False
                mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MarkAllAsRead(self):
        self.LogInfo('Mark all read')
        self.mailMgr.MarkAllAsRead()
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed:
                mail.read = True
                mail.statusMask = mail.statusMask | const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MarkAsReadByLabel(self, labelID):
        self.LogInfo('Mark label read', labelID)
        self.mailMgr.MarkAsReadByLabel(labelID)
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed and mail.labelMask & labelID == labelID:
                mail.read = True
                mail.statusMask = mail.statusMask | const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MarkAsReadByList(self, listID):
        self.LogInfo('Mark list read', listID)
        self.mailMgr.MarkAsReadByList(listID)
        for mail in self.mailHeaders.itervalues():
            if not mail.trashed and mail.toListID is not None and listID == mail.toListID:
                mail.read = True
                mail.statusMask = mail.statusMask | const.mailStatusMaskRead

        self.needToSaveHeaders = True



    def MoveAllFromTrash(self):
        self.LogInfo('Move all from trash')
        self.mailMgr.MoveAllFromTrash()
        for mail in self.mailHeaders.itervalues():
            mail.trashed = False
            mail.statusMask = mail.statusMask & ALL_LABELS - const.mailStatusMaskTrashed

        self.needToSaveHeaders = True



    def EmptyTrash(self):
        self.LogInfo('Empty trash')
        self.mailMgr.EmptyTrash()
        deleted = []
        for (messageID, mail,) in self.mailHeaders.iteritems():
            if mail.trashed:
                deleted.append(messageID)

        self.LogInfo('Deleted', len(deleted), 'messages')
        for messageID in deleted:
            del self.mailHeaders[messageID]
            if messageID in self.mailBodies:
                del self.mailBodies[messageID]
            if messageID in self.mailBodiesOrder:
                self.mailBodiesOrder.remove(messageID)
            self._mailSvc__DeleteFromBodyFile(messageID)

        self.needToSaveHeaders = True



    def DeleteMails(self, messageIDs):
        self.LogInfo('Delete', messageIDs)
        self.mailMgr.DeleteMail(messageIDs)
        for messageID in messageIDs:
            if messageID in self.mailHeaders:
                del self.mailHeaders[messageID]
            if messageID in self.mailBodies:
                del self.mailBodies[messageID]
            if messageID in self.mailBodiesOrder:
                self.mailBodiesOrder.remove(messageID)
            self._mailSvc__DeleteFromBodyFile(messageID)

        self.needToSaveHeaders = True



    def GetBody(self, messageID):
        self.LogInfo('GetMailBody', messageID)
        if messageID in self.mailBodies:
            self.LogInfo('Cached')
            if not self.mailHeaders[messageID].read:
                self.MarkMessagesAsRead([messageID])
            return self.mailBodies[messageID]
        if len(self.mailBodiesOrder) > BODIES_IN_CACHE:
            try:
                self.LogInfo('Must make room in cache')
                del self.mailBodies[self.mailBodiesOrder.pop(0)]
            except KeyError:
                pass
        if messageID in self.mailHeaders:
            body = self._mailSvc__ReadFromBodyFile(messageID)
            if body is None:
                compressedBody = self.mailMgr.GetBody(messageID, not self.mailHeaders[messageID].read)
                if compressedBody is None:
                    return ''
                body = zlib.decompress(compressedBody).decode('utf-8')
                self._mailSvc__WriteToBodyFile(messageID, body)
            self.MarkMessagesAsRead([messageID], False)
            self.mailBodies[messageID] = body
            self.mailBodiesOrder.append(messageID)
            return body
        self.LogError("Asking me to get a body, but I can't find the messageID asked for in self.mailHeaders. messageID:", messageID)



    def GetMailsByLabelOrListID(self, labelID = None, orderBy = mls.UI_EVEMAIL_RECEIVED, ascending = False, pos = 0, count = 20, listID = None):
        self.LogInfo('Get messages', labelID, orderBy, ascending, pos, count, listID)
        tmpList = []
        isSentitems = labelID == const.mailLabelSent
        if isSentitems and orderBy == mls.UI_EVEMAIL_SENDER:
            mails = []
            for message in self.mailHeaders.itervalues():
                if labelID in message.labels:
                    mails.append(message)

            self.TryPrimeRecipients(mails, setDone=True)
        for message in self.mailHeaders.itervalues():
            if message.trashed:
                continue
            if listID is not None:
                if message.toListID is not None and listID == message.toListID:
                    tmpList.append(self.PrepareOrder(message, orderBy, ascending, isSentitems))
                continue
            if labelID is None or message.labelMask & labelID == labelID:
                tmpList.append(self.PrepareOrder(message, orderBy, ascending, isSentitems))

        ret = util.KeyVal()
        ret.totalNum = len(tmpList)
        ret.sorted = self.DoSort(tmpList, ascending=ascending, pos=pos, count=count)
        if isSentitems and orderBy != mls.UI_EVEMAIL_SENDER:
            self.TryPrimeRecipients(ret.sorted)
        return ret



    def GetTrashedMails(self, orderBy = mls.UI_EVEMAIL_RECEIVED, ascending = False, pos = 0, count = 20):
        self.LogInfo('Get trash', orderBy, ascending, pos, count)
        tmpList = []
        for message in self.mailHeaders.itervalues():
            if not message.trashed:
                continue
            tmpList.append(self.PrepareOrder(message, orderBy, ascending))

        ret = util.KeyVal()
        ret.totalNum = len(tmpList)
        ret.sorted = self.DoSort(tmpList, ascending=ascending, pos=pos, count=count)
        return ret



    def PrepareOrder(self, message, orderBy = mls.UI_EVEMAIL_RECEIVED, ascending = False, sentItems = 0):
        if ascending:
            secondarySortID = message.messageID
        else:
            secondarySortID = -message.messageID
        if orderBy == mls.UI_EVEMAIL_RECEIVED:
            return (message.messageID, secondarySortID)
        if orderBy == mls.UI_EVEMAIL_SUBJECT:
            return (message.subject.lower(), secondarySortID)
        if orderBy == mls.UI_EVEMAIL_SENDER:
            if sentItems:
                name = self.GetRecipient(message, getName=1)
            else:
                name = message.senderName
            return (name.lower(), secondarySortID)
        if orderBy == mls.UI_EVEMAIL_STATUS:
            order = 4
            if not message.read:
                order = 1
            elif message.replied:
                order = 2
            elif message.forwarded:
                order = 3
            return (order, secondarySortID)



    def DoSort(self, list, ascending = False, pos = 0, count = 20):
        self.LogInfo('Sort', ascending, pos, count)
        retMails = []
        list.sort(reverse=ascending)
        for message in list[pos:(pos + count)]:
            retMails.append(self.mailHeaders[abs(message[1])])

        return retMails



    def GetMailsByIDs(self, messageIDs):
        mailDict = {}
        for messageID in messageIDs:
            mailDict[messageID] = self.GetMailByID(messageID)

        return mailDict



    def GetMailByID(self, messageID):
        try:
            return self.mailHeaders[messageID]
        except KeyError:
            return None



    def TryPrimeRecipients(self, messages, setDone = False):
        if getattr(self, 'donePrimingRecipients', False):
            return 
        idSet = set()
        for msg in messages:
            entityID = self.GetRecipient(msg, getName=0)
            if entityID > 0:
                idSet.add(entityID)

        owners = list(idSet)
        self.PrimeOwners(owners)
        if setDone:
            self.donePrimingRecipients = True



    def GetRecipient(self, message, getName = 1):
        toCharIDs = message.toCharacterIDs or []
        toListID = message.toListID
        if message.toCorpOrAllianceID is not None:
            toCorpIDs = [message.toCorpOrAllianceID]
        else:
            toCorpIDs = []
        if toListID is not None:
            numSentTo = 1
        else:
            numSentTo = 0
        numSentTo += len(toCharIDs) + len(toCorpIDs)
        if numSentTo > 1:
            if getName:
                return mls.UI_EVEMAIL_MULTIPLE
            else:
                return -1
        for each in toCharIDs + toCorpIDs:
            if getName:
                return cfg.eveowners.Get(each).ownerName
            return each

        if toListID is not None:
            if getName:
                return sm.GetService('mailinglists').GetDisplayName(toListID)
            else:
                return -1
        self.LogWarn('In GetRecipient: message = ', message)
        if getName:
            return ''
        else:
            return -1



    def GetLabels(self):
        if self.labels is None:
            self.labels = self.mailMgr.GetLabels()
        return self.labels



    def GetAllLabels(self, assignable = 0):
        self.LogInfo('GetAllLabels')
        allLabels = copy.copy(self.GetLabels())
        static = [(mls.UI_EVEMAIL_LABEL_ALLIANCE, const.mailLabelAlliance),
         (mls.UI_EVEMAIL_LABEL_CORP, const.mailLabelCorporation),
         (mls.UI_EVEMAIL_LABEL_INBOX, const.mailLabelInbox),
         (mls.UI_EVEMAIL_LABEL_SENT, const.mailLabelSent)]
        for (name, id,) in static:
            keyVal = allLabels.get(id, None)
            if keyVal is not None:
                keyVal.static = 1
                keyVal.name = name
            else:
                keyVal = util.KeyVal()
                keyVal.name = name
                keyVal.labelID = id
                keyVal.static = 1
                keyVal.color = None
                allLabels[id] = keyVal

        self.labels = allLabels.copy()
        if assignable:
            allLabels.pop(const.mailLabelSent, None)
        return allLabels



    def EditLabel(self, labelID, name = None, color = None):
        self.LogInfo('EditLabel', labelID, name, color)
        if name is None and color is None or name == '':
            raise UserError('MailLabelMustProvideName')
        self.mailMgr.EditLabel(labelID, name, color)
        staticLabels = [const.mailLabelSent,
         const.mailLabelInbox,
         const.mailLabelCorporation,
         const.mailLabelAlliance]
        self.GetLabels()
        if labelID not in self.labels and labelID not in staticLabels:
            raise RuntimeError("Invalid label cache, can't update", labelID, name)
        if name is not None:
            self.labels[labelID].name = name
        if color is not None:
            self.labels[labelID].color = color
        sm.ScatterEvent('OnMyLabelsChanged', 'mail_labels', None)



    def CreateLabel(self, name, color = None):
        self.LogInfo('CreateLabel', name, color)
        labelID = self.mailMgr.CreateLabel(name, color)
        self.GetLabels()
        self.labels[labelID] = util.KeyVal(labelID=labelID, name=name, color=color)
        sm.ScatterEvent('OnMyLabelsChanged', 'mail_labels', labelID)
        return labelID



    def DeleteLabel(self, labelID):
        self.LogInfo('DeleteLabel', labelID)
        self.mailMgr.DeleteLabel(labelID)
        self.GetLabels()
        try:
            del self.labels[labelID]
        except KeyError:
            raise RuntimeError("Invalid label cache, can't remove", labelID)
        for message in self.mailHeaders.itervalues():
            if labelID in message.labels:
                message.labelMask = message.labelMask & const.maxInt - labelID
                message.labels = self.GetLabelMaskAsList(message.labelMask)

        sm.ScatterEvent('OnMyLabelsChanged', 'mail_labels', None)



    def AssignLabels(self, messageIDs, labelID):
        self.LogInfo('AssignLabels', messageIDs, labelID)
        mailsToGetLabel = {}
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            if labelID & mail.labelMask != labelID:
                mailsToGetLabel[messageID] = mail

        if len(mailsToGetLabel) > 0:
            self.mailMgr.AssignLabels(mailsToGetLabel.keys(), labelID)
        for mail in mailsToGetLabel.itervalues():
            mail.labelMask = mail.labelMask | labelID
            mail.labels = self.GetLabelMaskAsList(mail.labelMask)

        self.needToSaveHeaders = True
        sm.ScatterEvent('OnMailCountersUpdate')



    def RemoveLabels(self, messageIDs, labelID):
        self.LogInfo('RemoveLabels', messageIDs, labelID)
        mailsToRemoveLabelFrom = {}
        for messageID in messageIDs:
            mail = self.mailHeaders[messageID]
            if labelID & mail.labelMask > 0:
                mailsToRemoveLabelFrom[messageID] = mail

        if len(mailsToRemoveLabelFrom) > 0:
            self.mailMgr.RemoveLabels(mailsToRemoveLabelFrom.keys(), labelID)
        for mail in mailsToRemoveLabelFrom.itervalues():
            mail.labelMask = mail.labelMask & const.maxInt - labelID
            mail.labels = self.GetLabelMaskAsList(mail.labelMask)

        self.needToSaveHeaders = True
        sm.ScatterEvent('OnMailCountersUpdate')



    def SaveChangesToDisk(self):
        if not self.needToSaveHeaders or self.isSaving:
            self.LogInfo('SaveChangesToDisk - nothing to do')
            return 
        self.isSaving = True
        try:
            uthread.Lock(self)
            try:
                self.LogInfo('SaveChangesToDisk - saving')
                self._mailSvc__WriteToHeaderFile('mail', self.mailHeaders)
                self.needToSaveHeaders = False

            finally:
                uthread.UnLock(self)


        finally:
            self.isSaving = False




    def TryCloseMailWindow(self):
        wnd = sm.GetService('window').GetWindow('mail', 0, decoClass=form.MailWindow)
        if wnd is not None:
            wnd.CloseX()



    def ClearMailCache(self):
        if eve.Message('AskClearMailCache', {}, uiconst.YESNO) == uiconst.ID_YES:
            self.TryCloseMailWindow()
            self.ClearCache()



    def ClearCache(self):
        uthread.Lock(self)
        try:
            self._mailSvc__ClearHeaderCache()
            self._mailSvc__ClearBodyCache()

        finally:
            uthread.UnLock(self)




    def __ClearHeaderCache(self):
        try:
            if os.path.exists(self.mailFileHeaders + '.dir'):
                os.remove(self.mailFileHeaders + '.dir')
            if os.path.exists(self.mailFileHeaders + '.dat'):
                os.remove(self.mailFileHeaders + '.dat')
            if os.path.exists(self.mailFileHeaders + '.bak'):
                os.remove(self.mailFileHeaders + '.bak')
        except:
            self.cacheFileCorruption = True
            self.LogError('Error deleting header mail cache files. charid:', str(session.charid))
            raise UserError('MailCacheFileError')
        self.mailHeaders = {}
        self.labels = None
        self.needToSaveHeaders = False
        self.cacheFileCorruption = False
        self.mailSynced = 0



    def __ClearBodyCache(self):
        try:
            if os.path.exists(self.mailFileBodies + '.dir'):
                os.remove(self.mailFileBodies + '.dir')
            if os.path.exists(self.mailFileBodies + '.dat'):
                os.remove(self.mailFileBodies + '.dat')
            if os.path.exists(self.mailFileBodies + '.bak'):
                os.remove(self.mailFileBodies + '.bak')
        except:
            self.cacheFileCorruption = True
            self.LogError('Error deleting body mail cache files. charid:', str(session.charid))
            raise UserError('MailCacheFileError')
        self.mailBodies = {}
        self.mailBodiesOrder = []
        self.cacheFileCorruption = False
        self.mailSynced = 0



    def __WriteToShelveFile(self, fileName, key, value):
        self.LogInfo('WriteToShelve', fileName, key)
        s = blue.os.GetTime(1)
        key = str(key)
        try:
            fileHandle = shelve.open(fileName)
            fileHandle[key] = value
            fileHandle.close()
        except:
            self.LogError('Error writing to shelve file (', fileName, ', ', key, ',', value, ')')
            self.cacheFileCorruption = True
            self.TryCloseMailWindow()
            raise UserError('MailCacheFileError')
        self.LogInfo('Writing', blue.os.TimeDiffInMs(s, blue.os.GetTime(1)))



    def __ReadFromShelveFile(self, fileName, key):
        self.LogInfo('ReadingFromShelve', fileName, key)
        s = blue.os.GetTime(1)
        key = str(key)
        retValue = None
        try:
            fileHandle = shelve.open(fileName)
            if key in fileHandle:
                retValue = fileHandle[key]
            fileHandle.close()
            return retValue
        except:
            self.LogError('Error reading from shelve file (', fileName, ', ', key, ')')
            self.cacheFileCorruption = True
            self.TryCloseMailWindow()
            raise UserError('MailCacheFileError')
        self.LogInfo('Reading', blue.os.TimeDiffInMs(s, blue.os.GetTime(1)))



    def __WriteToHeaderFile(self, key, value):
        self._mailSvc__WriteToShelveFile(self.mailFileHeaders, key, value)



    def __ReadFromHeaderFile(self, key):
        return self._mailSvc__ReadFromShelveFile(self.mailFileHeaders, key)



    def __WriteToBodyFile(self, key, value):
        self._mailSvc__WriteToShelveFile(self.mailFileBodies, key, value)



    def __ReadFromBodyFile(self, key):
        return self._mailSvc__ReadFromShelveFile(self.mailFileBodies, key)



    def __DeleteFromBodyFile(self, key):
        self.LogInfo('DeletingFromShelve', key)
        s = blue.os.GetTime(1)
        key = str(key)
        try:
            fileHandle = shelve.open(self.mailFileBodies)
            if key in fileHandle:
                del fileHandle[key]
            fileHandle.close()
        except:
            self.LogError('Error deleting from body shelve file (', key, ')')
            self.cacheFileCorruption = True
            self.TryCloseMailWindow()
            raise UserError('MailCacheFileError')
        self.LogInfo('Deleting', blue.os.TimeDiffInMs(s, blue.os.GetTime(1)))



    def IsFileCacheCorrupted(self):
        return self.cacheFileCorruption



    def SendMail(self, toCharacterIDs = [], toListID = None, toCorpOrAllianceID = None, title = '', body = '', isReplyTo = 0, isForwardedFrom = 0):
        self.LogInfo('SendMail', toCharacterIDs, toListID, toCorpOrAllianceID, isReplyTo, isForwardedFrom)
        if toListID is not None:
            myLists = sm.GetService('mailinglists').GetMyMailingLists()
            if toListID not in myLists:
                raise UserError('EveMailCanOnlySendToOwnMailinglists')
        messageID = util.CSPAChargedAction('CSPAMailCheck', self.mailMgr, 'SendMail', toCharacterIDs, toListID, toCorpOrAllianceID, title, body, isReplyTo, isForwardedFrom)
        if messageID is None:
            return 
        if len(self.mailBodiesOrder) > BODIES_IN_CACHE:
            try:
                del self.mailBodies[self.mailBodiesOrder.pop(0)]
            except KeyError:
                pass
        self._mailSvc__WriteToBodyFile(messageID, body)
        self.mailBodies[messageID] = body
        self.mailBodiesOrder.append(messageID)
        if isReplyTo > 0:
            if isReplyTo in self.mailHeaders:
                mail = self.mailHeaders[isReplyTo]
                mail.replied = 1
                mail.statusMask = mail.statusMask | const.mailStatusMaskReplied
                self.needToSaveHeaders = True
        if isForwardedFrom > 0:
            if isForwardedFrom in self.mailHeaders:
                mail = self.mailHeaders[isForwardedFrom]
                mail.forwarded = 1
                mail.statusMask = mail.statusMask | const.mailStatusMaskForwarded
                self.needToSaveHeaders = True
        self.OnMailSent(messageID, session.charid, blue.os.GetTime() / MIN * MIN, toCharacterIDs, toListID, toCorpOrAllianceID, title, 0)
        sm.ScatterEvent('OnMailStatusUpdate', isReplyTo, isForwardedFrom)
        return messageID



    def SendMsgDlg(self, toCharacterIDs = [], toListID = None, toCorpOrAllianceID = [], isForwardedFrom = 0, isReplyTo = 0, subject = None, body = None):
        if session.userType == const.userTypeTrial:
            n = 1
            t = getattr(self, 'lastMessageTime', blue.os.GetTime() - 10 * const.mailTrialAccountTimer * MIN)
            if blue.os.GetTime() - t < n * const.mailTrialAccountTimer * MIN:
                raise UserError('TrialAccountRestriction', {'what': mls.UI_SHARED_EVEMAILRESTRICTIONTIME % {'timeleft': util.FmtDate(t + n * MIN - blue.os.GetTime())}})
        sendPage = sm.GetService('window').GetWindow('newmessage', 1, decoClass=form.NewNewMessage, ignoreCurrent=1, toCharacterIDs=toCharacterIDs, toListID=toListID, toCorpOrAllianceID=toCorpOrAllianceID, isForwardedFrom=isForwardedFrom, isReplyTo=isReplyTo, subject=subject, body=body)
        return sendPage



    def GetReplyWnd(self, msg, all = 0, *args):
        if msg is None:
            return 
        toListID = None
        toCorpOrAllianceID = []
        toCharacterIDs = []
        senders = []
        if all:
            if msg.toCharacterIDs is not None:
                toCharacterIDs = msg.toCharacterIDs[:]
                if session.charid in toCharacterIDs:
                    toCharacterIDs.remove(session.charid)
            toCharacterIDs.append(msg.senderID)
            if msg.toCorpOrAllianceID is not None:
                toCorpOrAllianceID = [msg.toCorpOrAllianceID]
            toListID = msg.toListID
        else:
            toCharacterIDs = [msg.senderID]
        receiversText = self.GetReceiverText(msg)
        newmsg = self.SendMsgDlg(toCharacterIDs=toCharacterIDs, toListID=toListID, toCorpOrAllianceID=toCorpOrAllianceID, isReplyTo=msg.messageID)
        newmsgText = self.GetReplyMessage(msg)
        newmsg.sr.subjecField.SetValue('%s %s' % (mls.UI_GENERIC_INBOXRE, msg.subject))
        newmsg.messageedit.SetValue(newmsgText, scrolltotop=1)



    def GetReceiverText(self, mail, format = 0):
        receiversChar = mail.toCharacterIDs
        receiversMaillistID = mail.toListID
        receiversCorp = mail.toCorpOrAllianceID or ''
        receiversText = ''
        if receiversMaillistID is not None:
            name = sm.GetService('mailinglists').GetDisplayName(receiversMaillistID)
            if format:
                name = '<b>%s</b>' % name
            receiversText += '%s, ' % name
        if receiversCorp:
            name = cfg.eveowners.Get(receiversCorp).ownerName
            toAdd = '%s' % name
            if format:
                toAdd = '<b>%s</b>' % toAdd
            receiversText += '%s, ' % toAdd
        charsIDs = [ charID for charID in receiversChar if charID not in (-1, None) ]
        self.PrimeOwners(charsIDs)
        charNameList = []
        for each in charsIDs:
            name = cfg.eveowners.Get(each).ownerName
            text = '<a href="showinfo:1377//%s">%s</a>,  ' % (each, name)
            charNameList.append((name.lower(), text))

        charNameList = uiutil.SortListOfTuples(charNameList)
        for each in charNameList:
            receiversText += each

        return receiversText



    def GetMailText(self, node):
        msg = node
        body = self.GetBody(msg.messageID)
        subject = msg.subject
        senderID = msg.senderID
        senderName = msg.senderName
        date = msg.sentDate
        receiversText = self.GetReceiverText(msg, format=1)
        if msg.statusMask & const.mailStatusMaskAutomated == const.mailStatusMaskAutomated:
            senderText = '<b>%s</b>' % senderName
        else:
            senderText = '<a href="showinfo:1377//%s">%s</a>' % (senderID, senderName)
        txt = '\n<font size=22>%(subject)s</font>\n<br>\n<font size=12><b>%(from)s: </b>%(senderText)s</font>\n<br>\n<font size=12><b>%(sent)s: </b>%(date)s</font>\n<br>\n<font size=12><b>%(to)s: </b>%(receivers)s</font>\n<font size=12>\n<br>\n<br>\n%(body)s</font>\n' % {'from': mls.UI_EVEMAIL_FROM,
         'sent': mls.UI_EVEMAIL_SENT,
         'to': mls.UI_EVEMAIL_TO,
         'subject': subject,
         'senderText': senderText,
         'body': body,
         'date': util.FmtDate(date, 'ls'),
         'receivers': receiversText}
        return txt



    def GetReplyMessage(self, msg):
        if msg is None:
            return ''
        receiversText = self.GetReceiverText(msg)
        if msg.statusMask & const.mailStatusMaskAutomated == const.mailStatusMaskAutomated:
            senderText = '<b>%s</b>' % msg.senderName
        else:
            senderText = '<a href="showinfo:1377//%s">%s</a>' % (msg.senderID, cfg.eveowners.Get(msg.senderID).ownerName)
        body = self.GetBody(msg.messageID)
        newmsgText = '\n<br><br>%(line)s<br>\n%(subject)s\n<br>\n%(from)s: %(senders)s\n<br>\n%(sent)s: %(date)s\n<br>\n%(to)s: %(receivers)s\n<br>\n<br>\n%(body)s\n' % {'line': '--------------------------------',
         'subject': msg.subject,
         'from': mls.UI_EVEMAIL_FROM,
         'senders': senderText,
         'sent': mls.UI_EVEMAIL_SENT,
         'date': util.FmtDate(msg.sentDate, 'ls'),
         'to': mls.UI_EVEMAIL_TO,
         'receivers': receiversText,
         'body': body}
        maxLen = const.mailMaxBodySize * 0.9
        if len(newmsgText) > maxLen:
            while len(newmsgText) > maxLen:
                try:
                    brIndex = newmsgText.rindex('<br>', int(maxLen * 0.7))
                    newmsgText = newmsgText[:brIndex]
                except ValueError:
                    lastIndex = int(len(newmsgText) * 0.9)
                    newmsgText = newmsgText[:lastIndex]

            newmsgText += '<br>...'
        return newmsgText



    def GetForwardWnd(self, msg):
        if msg is None:
            return 
        newmsg = self.SendMsgDlg(isForwardedFrom=msg.messageID)
        newmsgText = self.GetReplyMessage(msg)
        newmsg.sr.subjecField.SetValue('%s %s' % ('FW:', msg.subject))
        newmsg.messageedit.SetValue(newmsgText, scrolltotop=1)



    def OnMailSent(self, messageID, senderID, sentDate, toCharacterIDs, toListID, toCorpOrAllianceID, title, statusMask):
        uthread.Lock(self)
        try:
            if messageID in self.mailHeaders:
                return 
            labelMask = 0
            read = False
            if session.charid in toCharacterIDs:
                labelMask = const.mailLabelInbox
            if senderID == session.charid:
                if labelMask == 0 and toCorpOrAllianceID is None and toListID is None:
                    read = True
                    statusMask = statusMask | 1
                labelMask = labelMask | const.mailLabelSent
            if toCorpOrAllianceID is not None:
                if util.IsCorporation(toCorpOrAllianceID):
                    labelMask = labelMask | const.mailLabelCorporation
                else:
                    labelMask = labelMask | const.mailLabelAlliance
            self.mailHeaders[messageID] = util.KeyVal(messageID=messageID, senderID=senderID, toCharacterIDs=toCharacterIDs, toListID=toListID, toCorpOrAllianceID=toCorpOrAllianceID, subject=title, sentDate=sentDate, read=read, replied=False, forwarded=False, trashed=False, statusMask=statusMask, labelMask=labelMask, labels=self.GetLabelMaskAsList(labelMask))
            if statusMask & const.mailStatusMaskAutomated > 0 and senderID == toListID:
                self.mailHeaders[messageID].senderName = sm.GetService('mailinglists').GetDisplayName(senderID)
            else:
                try:
                    self.mailHeaders[messageID].senderName = cfg.eveowners.Get(senderID).name
                except IndexError:
                    self.mailHeaders[messageID].senderName = mls.UI_GENERIC_UNKNOWN
            self.needToSaveHeaders = True
            if not read:
                self.OnNewMailReceived(self.mailHeaders[messageID])

        finally:
            uthread.UnLock(self)




    def OnMailDeleted(self, messageIDs):
        uthread.Lock(self)
        try:
            for messageID in messageIDs:
                if messageID in self.mailHeaders:
                    del self.mailHeaders[messageID]
                    self.needToSaveHeaders = True
                if messageID in self.mailBodies:
                    del self.mailBodies[messageID]
                if messageID in self.mailBodiesOrder:
                    self.mailBodiesOrder.remove(messageID)
                self._mailSvc__DeleteFromBodyFile(messageID)

            sm.ScatterEvent('OnMailTrashedDeleted', None, 1)

        finally:
            uthread.UnLock(self)




    def OnMailUndeleted(self, messageIDs):
        self.SyncMail()
        sm.ScatterEvent('OnNewMailReceived')



    def OnNewMailReceived(self, msg, *args):
        self.SetBlinkTabState(True)
        self.SetBlinkNeocomState(True)
        sm.ScatterEvent('OnNewMailReceived')
        if settings.user.ui.Get('mail_blinkNecom', 1):
            sm.GetService('neocom').Blink('mail')
        if settings.user.ui.Get('mail_showNotification', 1):
            self.GetMailNotification(msg)



    def GetMailNotification(self, msg):
        header = mls.UI_EVEMAIL_NEWMAILHEADER
        senderName = msg.senderName
        text1 = '%s: %s' % (mls.UI_EVEMAIL_FROM, senderName)
        subject = msg.subject
        if len(subject) > 100:
            text2 = '%s...' % subject[:100]
        else:
            text2 = subject
        icon = self.ShowMailNotification(header, text1, text2)
        icon.OnClick = (self.OnClickingMailPopup, icon, msg)
        icon.GetMenu = self.MailMenu



    def OnClickingMailPopup(self, popup, msg, *args):
        self.OnOpenPopupMail(msg)
        if popup and not popup.destroyed:
            popup.CloseNotification()



    def GetMailAndNotificationNotification(self, mailCount, notificationCount, time = 5000, shouldBlinkNeocom = False):
        blue.pyos.synchro.Sleep(3000)
        if shouldBlinkNeocom:
            sm.GetService('neocom').Blink('mail')
        blue.pyos.synchro.Sleep(7000)
        header = mls.UI_EVEMAIL_NEWMAILHEADER
        text1 = ''
        text2 = ''
        if mailCount > 0:
            text1 = mls.UI_EVEMAIL_NEWMAILS % {'numMails': mailCount}
        if notificationCount > 0:
            text2 = mls.UI_EVEMAIL_NEWNOTIFICATIONS % {'num': notificationCount}
        if text1 == '':
            text1 = text2
            text2 = ''
        icon = self.ShowMailNotification(header, text1, text2)
        icon.OnClick = (self.OnClickingPopup, icon)



    def OnClickingPopup(self, popup, *args):
        sm.GetService('cmd').OpenMail()
        popup.CloseNotification()



    def ShowMailNotification(self, header, text1, text2, number = (0, 0), time = 5000, *args):
        ahidden = sm.GetService('neocom').GetAHidden() or settings.user.windows.Get('neoalign', 'left') != 'left'
        BIG = settings.user.windows.Get('neowidth', 1) and not ahidden
        left = [[36, 2], [132, 2]][BIG][ahidden] + 14
        data = util.KeyVal()
        data.headerText = header
        data.text1 = text1
        data.text2 = text2
        data.iconNum = 'ui_94_64_8'
        data.time = time
        icon = uiutil.FindChild(uicore.layer.abovemain, 'newmail')
        if not icon:
            icon = xtriui.PopupNotification(name='newmail', parent=None, align=uiconst.TOPLEFT, pos=(left,
             60,
             230,
             60), idx=0)
            icon.state = uiconst.UI_NORMAL
            uicore.layer.abovemain.children.insert(0, icon)
            icon.Startup()
        icon.Load(data)
        return icon



    def OnOpenPopupMail(self, msg, *args):
        wndName = 'mail_readingWnd_%s' % msg.messageID
        wnd = sm.GetService('window').GetWindow(wndName, 1, decoClass=form.MailReadingWnd, windowPrefsID='mailReadingWnd', mail=msg, msgID=msg.messageID, txt='', toolbar=1, trashed=msg.trashed, type=const.mailTypeMail)
        if not msg.read:
            sm.ScatterEvent('OnMailStatusUpdate', None, None, [msg.messageID])
        if wnd is not None:
            wnd.Maximize()
            blue.pyos.synchro.Sleep(1)
            wnd.SetText(self.GetMailText(msg))



    def CheckNewMessages(self, mailCount, notificationCount):
        shouldBlink = 0
        shouldShowPopup = 0
        if mailCount:
            self.SetBlinkNeocomState(True)
            if settings.user.ui.Get('mail_blinkNecom', 1):
                self.SetBlinkTabState(True)
                shouldBlink = 1
            if settings.user.ui.Get('mail_showNotification', 1):
                shouldShowPopup = 1
            if settings.user.ui.Get('mail_blinkTab', 1):
                self.SetBlinkTabState(True)
        if notificationCount:
            sm.GetService('notificationSvc').SetBlinkNeocomState(True)
            if settings.user.ui.Get('notification_blinkNecom', 1):
                sm.GetService('notificationSvc').SetBlinkTabState(True)
                shouldBlink = 1
            if settings.user.ui.Get('notification_showNotification', 1):
                shouldShowPopup = 1
            if settings.user.ui.Get('notification_blinkTab', 1):
                sm.GetService('notificationSvc').SetBlinkTabState(True)
        if shouldShowPopup:
            self.GetMailAndNotificationNotification(mailCount, notificationCount, time=10000, shouldBlinkNeocom=shouldBlink)



    def MailMenu(self, *args):
        m = [(mls.UI_EVEMAIL_DISABLENOTIFICATION, self.DisableNotification)]
        return m



    def DisableNotification(self, *args):
        settings.user.ui.Set('mail_showNotification', 0)



    def GetMailWindow(self, create = 1, *args):
        if self.IsFileCacheCorrupted():
            raise UserError('MailCacheFileError')
        wnd = sm.GetService('window').GetWindow('mail', create, decoClass=form.MailWindow)
        return wnd



    def CheckLabelName(self, dict, *args):
        name = dict.get('name', '').strip()
        myLabelNames = [ label.name for label in self.GetAllLabels(assignable=0).values() ]
        if name in myLabelNames:
            return mls.UI_EVEMAIL_LABELNAMETAKEN



    def RenameLabelFromUI(self, labelID):
        ret = uix.NamePopup(mls.UI_EVEMAIL_LABELNAME, mls.UI_EVEMAIL_LABELNAME2, maxLength=const.mailMaxLabelSize, validator=self.CheckLabelName)
        if ret is None:
            return 
        name = ret.get('name', '')
        name = name.strip()
        if name:
            self.EditLabel(labelID, name=name)



    def ChangeLabelColorFromUI(self, color, labelID):
        allLabels = self.GetAllLabels()
        label = allLabels.get(labelID, None)
        if label is None:
            return 
        if color != label.color:
            self.EditLabel(labelID, color=color)



    def GetSwatchColors(self, *args):
        return swatchColors



    def DeleteLabelFromUI(self, labelID, labelName):
        if eve.Message('DeleteMailLabel', {'labelName': labelName}, uiconst.YESNO) == uiconst.ID_YES:
            self.DeleteLabel(labelID)



    def ShouldTabBlink(self, *args):
        return self.blinkTab



    def SetBlinkTabState(self, state = False):
        self.blinkTab = state



    def ShouldNeocomBlink(self, *args):
        return self.blinkNeocom



    def SetBlinkNeocomState(self, state = False):
        self.blinkNeocom = state



    def GetAssignColorWnd(self, labelID, doneCallBack = None, doneArgs = (), width = 104, height = 74, *args):
        colorpar = xtriui.MailAssignColorWnd(name='colorpar', parent=uicore.layer.menu, idx=0, align=uiconst.TOPLEFT, pos=(0,
         0,
         width,
         height))
        colorpar.Startup(labelID, doneCallBack, doneArgs)




