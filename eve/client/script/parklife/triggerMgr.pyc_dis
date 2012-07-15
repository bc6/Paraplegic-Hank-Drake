#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/parklife/triggerMgr.py
import uthread
import blue
import base
import uix
import service
import localization

class Triggers(service.Service):
    __guid__ = 'svc.trigger'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnDungeonTriggerMessage', 'OnDungeonTriggerAudio']
    __dependencies__ = ['audio']

    def __init__(self):
        service.Service.__init__(self)

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.audio = None

    def OnDungeonTriggerMessage(self, messageType, messageID):
        color = self.GetMessageColor(messageType)
        body = localization.GetByMessageID(messageID)
        sm.GetService('LSC').LocalEchoAll('<color=%s>%s</color>' % (color, body), localization.GetByLabel('UI/Common/Message'))

    def OnDungeonTriggerAudio(self, audioUrl):
        if not self.audio:
            self.audio = sm.StartService('audio')
        self.audio.PlaySound(audioUrl)

    def GetMessageColor(self, messageType):
        return {const.dunEventMessageMood: '0xffa3fc80',
         const.dunEventMessageStory: '0xffa3fc80',
         const.dunEventMessageMissionInstruction: '0xff48ff00',
         const.dunEventMessageMissionObjective: '0xff48ff00',
         const.dunEventMessageImminentDanger: '0xffff0000',
         const.dunEventMessageEnvironment: '0xffa3fc80',
         const.dunEventMessageNPC: '0xff80d8fc',
         const.dunEventMessageWarning: '0xffffd800'}.get(messageType, '0xffe0e0e0')