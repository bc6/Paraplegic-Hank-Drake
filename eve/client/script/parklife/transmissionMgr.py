import form
import service
import sys
import uix
import uiutil
import uthread
import util
import uicls
import uiconst
import log

class TransmissionSvc(service.Service):
    __guid__ = 'svc.transmission'
    __sessionparams__ = []
    __exportedcalls__ = {'CloseTransmission': [service.ROLE_IGB]}
    __dependencies__ = []
    __notifyevents__ = ['OnIncomingTransmission', 'OnIncomingAgentMessage']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.delayedTransmission = None



    def Stop(self, stream):
        service.Service.Stop(self)
        self.Cleanup()



    def Cleanup(self):
        for each in uicore.layer.main.children[:]:
            if each.name == 'telecom':
                each.Close()




    def OnIncomingTransmission(self, transmission, isAgentMission = 0, *args):
        if transmission.header.startswith('[d]'):
            transmission.header = transmission.header[3:]
            self.delayedTransmission = transmission
        else:
            self.ShowTransmission(transmission)



    def ShowTransmission(self, transmission):
        wnd = sm.GetService('window').GetWindow('telecom', decoClass=form.Telecom, create=1, transmission=transmission)
        if wnd:
            wnd.ShowMessage(transmission)
            if wnd.state == uiconst.UI_HIDDEN:
                wnd.Blink()



    def CloseTransmission(self, *args):
        self.Cleanup()



    def StopWarpIndication(self):
        if self.delayedTransmission:
            self.ShowTransmission(self.delayedTransmission)
            self.delayedTransmission = None



    def OnIncomingAgentMessage(self, agentID, message):
        self.ShowAgentAlert(agentID, message)



    def ShowAgentAlert(self, agentID, message):
        agentsService = sm.StartService('agents')
        standing = sm.StartService('standing')
        cc = sm.StartService('cc')
        agentSays = message
        agent = agentsService.GetAgentByID(agentID)
        agentCorpID = agent.corporationID
        agentDivision = agentsService.GetDivisions()[agent.divisionID].divisionName.replace('&', '&amp;')
        standingsSet = [standing.GetEffectiveStanding(agent.factionID, eve.session.charid)[0], standing.GetEffectiveStanding(agent.corporationID, eve.session.charid)[0], standing.GetEffectiveStanding(agent.agentID, eve.session.charid)[0]]
        if min(standingsSet) <= -2.0:
            effectiveStanding = '<b>%-2.1f</b>' % min(standingsSet)
        else:
            effectiveStanding = '%-2.1f' % (max(standingsSet) or 0.0)
        agentBloodline = cc.GetData('bloodlines', ['bloodlineID', agent.bloodlineID])
        agentRace = cc.GetData('races', ['raceID', agentBloodline.raceID])
        raceName = Tr(agentRace.raceName, 'character.races.raceName', agentRace.dataID)
        bloodlineName = Tr(agentBloodline.bloodlineName, 'character.bloodlines.bloodlineName', agentBloodline.dataID)
        agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (agentsService.GetAgentInventoryTypeByBloodline(agent.bloodlineID), agentID, mls.UI_CMD_SHOWINFO)
        agentLocationWrap = agentsService.GetAgentMoniker(agentID).GetAgentLocationWrap()
        props = {'agentDivision': agentDivision,
         'agentCorpName': cfg.eveowners.Get(agentCorpID).name,
         'agentName': cfg.eveowners.Get(agentID).name,
         'agentLevel': agent.level,
         'agentRace': raceName,
         'agentBloodline': bloodlineName,
         'agentInfoIcon': agentInfoIcon,
         'agentLocation': agentLocationWrap,
         'charName': cfg.eveowners.Get(eve.session.charid).name,
         'corpName': cfg.eveowners.Get(eve.session.corpid).name,
         'effectiveStanding': effectiveStanding,
         'agentSays': agentSays,
         'agentID': agentID,
         'agentCorpID': agentCorpID,
         'blurbConversation': mls.AGT_DIALOGUE_BLURBCONVERSATION,
         'blurbName': mls.AGT_DIALOGUE_BLURBNAME,
         'blurbCorporation': mls.AGT_DIALOGUE_BLURBCORPORATION,
         'blurbDivision': mls.AGT_DIALOGUE_AGENTDIVISION % {'external.agentDivision': agentDivision},
         'blurbRace': mls.AGT_DIALOGUE_BLURBRACE,
         'blurbBloodline': mls.AGT_DIALOGUE_BLURBBLOODLINE,
         'blurbEffectiveStanding': mls.AGT_DIALOGUE_EFFECTIVESTANDING % {'external.effectiveStanding': effectiveStanding}}
        head = '\n            <HTML>\n            <HEAD>\n            \n            <TITLE>%(blurbConversation)s - %(agentName)s</TITLE>\n            </HEAD>\n            <BODY background-color=#00000000 link=#FFA800>\n            ' % props
        body = '\n            <br>\n            <TABLE border=0 cellpadding=1 cellspacing=1>\n                <TR>\n                    <TD valign=top >\n                        <TABLE border=0 cellpadding=1 cellspacing=1>\n                            <TR>\n                            </TR>\n                            <TR>\n                            </TR>\n                            <TR>\n                            </TR>\n                            <TR>\n                                <TD valign=top><img src="portrait:%(agentID)d" width=120 height=120 size=256 align=left style=margin-right:10></TD>\n                            </TR>\n                        </TABLE>\n                    </TD>\n                    <TD valign=top>\n                            <TABLE border=0 width=350 cellpadding=1 cellspacing=1>\n                            <TR>\n                                <TD width=120 valign=top colspan=2><font size=24>%(agentName)s</font> %(agentInfoIcon)s</TD>\n                            </TR>\n                            <TR>\n                                <TD>%(blurbDivision)s</TD>\n                            </TR>\n                            <TR>\n                                <TD height=12> </TD>\n                            </TR>\n                            <TR>\n                                <TD>%(agentLocation)s</TD>\n                            </TR>\n                            <TR>\n                                <TD height=12> </TD>\n                            </TR>\n                            <TR>\n                                <TD>%(blurbEffectiveStanding)s</TD>\n                            </TR>\n                        </TABLE>\n                    </TD>\n                </TR>\n            </TABLE>\n            \n            <table width=480 cellpadding=2>\n            <tr>\n            <td width=40 valign=top><img style:vertical-align:bottom src="icon:ui_9_64_2" size="32"></td>\n            <td>\n            <font size=12>%(agentSays)s</font>\n            </td>\n            </tr>\n            </table>\n            ' % props
        foot = '\n            </BODY>\n            </HTML>\n            ' % props
        html = head + body + foot
        browser = sm.GetService('window').GetWindow('agentalert_%s' % agentID, decoClass=form.AgentBrowser, create=1, maximize=1)
        browser.SetMinSize([512, 512])
        browser.LockWidth(512)
        uthread.new(browser.LoadHTML, html)




class Telecom(uicls.Window):
    __guid__ = 'form.Telecom'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        transmission = attributes.transmission
        self.isDockWnd = 0
        caption = getattr(transmission, 'caption', None) or mls.UI_INFLIGHT_TRANSMISSIONS
        hasDungeonWarp = getattr(transmission, 'hasDungeonWarp', False)
        self.scope = 'inflight'
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(parent=self.sr.topParent, align=uiconst.TOBOTTOM)
        uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TOLEFT, width=70)
        self.sr.header = uicls.CaptionLabel(text=' ', parent=self.sr.topParent, align=uiconst.TOTOP, autowidth=0, autoHeight=1)
        self.sr.header.padTop = 16
        self.sr.messageArea = uicls.Edit(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), readonly=1, hideBackground=1)
        self.NoSeeThrough()
        self.SetMinSize([360, 240], 1)
        self.SetCaption(caption)
        self.MakeUnResizeable()
        self.MakeUnMinimizable()
        self.MakeUnKillable()
        self.SetTopparentHeight(58)
        if not hasDungeonWarp:
            self.DefineButtons(uiconst.OK, okLabel=mls.UI_CMD_CLOSETRANSMISSIONS, okFunc=self.SelfDestruct)
        else:
            self.sr.instanceID = getattr(transmission.rec.rec, 'instanceID', 0)
            self.sr.solarSystemID = getattr(transmission.rec.rec, 'solarSystemID', 0)
            if self.sr.solarSystemID == eve.session.solarsystemid:
                okLabel = mls.UI_CMD_WARPTO
                okFunc = self.WarpToEPLocation
            else:
                checkFleet = [bool(eve.session.fleetid), 'You are in fleet', 'You are not in fleet']
                checkIfImLeader = [sm.GetService('menu').ImFleetLeaderOrCommander(), mls.UI_MENUHINT_CHECKIFIMLEADER, mls.UI_MENUHINT_CHECKIFIMLEADERNOT]
                if checkFleet[0] and checkIfImLeader[0]:
                    okLabel = sm.GetService('menu').BroadcastCaption('TRAVELTO')
                    okFunc = self.SetFleetDestination
                else:
                    okLabel = mls.UI_CMD_SETDESTINATION
                    okFunc = self.SetDestination
            if self.sr.instanceID and self.sr.solarSystemID:
                self.DefineButtons(uiconst.OKCANCEL, okLabel=okLabel, okFunc=okFunc, cancelLabel=mls.UI_CMD_CLOSETRANSMISSIONS, cancelFunc=self.SelfDestruct)
            else:
                self.DefineButtons(uiconst.OK, okLabel=mls.UI_CMD_CLOSETRANSMISSIONS, okFunc=self.SelfDestruct)



    def SetDestination(self, *args):
        sm.StartService('starmap').SetWaypoint(self.sr.solarSystemID, 1)
        self.SelfDestruct()



    def SetFleetDestination(self, *args):
        sol = self.sr.solarSystemID
        sm.StartService('fleet').SendBroadcast_TravelTo(sol)
        self.SetDestination()



    def WarpToEPLocation(self, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if self.sr.instanceID is not None and bp is not None:
            bp.WarpToStuff('epinstance', self.sr.instanceID)
        self.SelfDestruct()



    def ShowMessage(self, transmission):
        self.sr.header.text = transmission.header
        icon = transmission.icon
        if icon:
            try:
                icon = util.IconFile(int(icon.split(' ', 1)[0]))
                self.SetWndIcon(icon, mainTop=-3)
                if icon.startswith('c_'):
                    uiutil.GetChild(self, 'clippedicon').state = uiconst.UI_HIDDEN
            except:
                self.SetWndIcon('ui_40_64_14', mainTop=-3)
                log.LogWarn('Failed adding ', icon, ' as icon in transmission window')
                sys.exc_clear()
        else:
            self.SetWndIcon('ui_40_64_14', mainTop=-6)
        message = transmission.text
        message = '\n            <html>\n            < head >\n            <link rel="stylesheet" type="text/css"HREF="res:/ui/css/dungeontm.css">\n            </head>\n            <body>\n            %s\n            </body>\n            </html>\n        ' % message
        self.sr.messageArea.LoadHTML(message)



    def SetNetResIcon(self, wnd, iconNum = None, headerIcon = 0, scaling = 0.25, fullPath = None):
        return self.SetWndIcon(iconNum, headerIcon, int(256 * scaling), fullPath, mainTop=-6)




