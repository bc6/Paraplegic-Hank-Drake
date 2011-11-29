import form
import service
import sys
import uiutil
import uthread
import util
import uicls
import uiconst
import log
import localization

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
        wnd = form.Telecom.Open(transmission=transmission)
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
        agentSays = message
        agent = agentsService.GetAgentByID(agentID)
        agentDivision = agentsService.GetDivisions()[agent.divisionID].divisionName.replace('&', '&amp;')
        standingsSet = [standing.GetEffectiveStanding(agent.factionID, eve.session.charid)[0], standing.GetEffectiveStanding(agent.corporationID, eve.session.charid)[0], standing.GetEffectiveStanding(agent.agentID, eve.session.charid)[0]]
        if min(standingsSet) <= -2.0:
            blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStandingLow', effectiveStanding=min(standingsSet))
        else:
            blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStanding', effectiveStanding=max(standingsSet) or 0.0)
        agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (agentsService.GetAgentInventoryTypeByBloodline(agent.bloodlineID), agentID, uiutil.StripTags(localization.GetByLabel('UI/Commands/ShowInfo'), stripOnly=['localized']))
        html = '\n        <HTML>\n        <BODY background-color=#00000000 link=#FFA800>\n            <br>\n            <TABLE border=0 cellpadding=1 cellspacing=1>\n                <TR>\n                    <TD valign=top >\n                        <TABLE border=0 cellpadding=1 cellspacing=1>\n                            <TR>\n                            </TR>\n                            <TR>\n                            </TR>\n                            <TR>\n                            </TR>\n                            <TR>\n                                <TD valign=top><img src="portrait:%(agentID)d" width=120 height=120 size=256 align=left style=margin-right:10></TD>\n                            </TR>\n                        </TABLE>\n                    </TD>\n                    <TD valign=top>\n                            <TABLE border=0 width=350 cellpadding=1 cellspacing=1>\n                            <TR>\n                                <TD width=120 valign=top colspan=2><font size=24>%(agentName)s</font> %(agentInfoIcon)s</TD>\n                            </TR>\n                            <TR>\n                                <TD>%(blurbDivision)s</TD>\n                            </TR>\n                            <TR>\n                                <TD height=12> </TD>\n                            </TR>\n                            <TR>\n                                <TD>%(agentLocation)s</TD>\n                            </TR>\n                            <TR>\n                                <TD height=12> </TD>\n                            </TR>\n                            <TR>\n                                <TD>%(blurbEffectiveStanding)s</TD>\n                            </TR>\n                        </TABLE>\n                    </TD>\n                </TR>\n            </TABLE>\n            \n            <table width=480 cellpadding=2>\n            <tr>\n            <td width=40 valign=top><img style:vertical-align:bottom src="icon:ui_9_64_2" size="32"></td>\n            <td>\n            <font size=12>%(agentSays)s</font>\n            </td>\n            </tr>\n            </table>\n        </BODY>\n        </HTML>\n        ' % {'agentID': agentID,
         'agentName': cfg.eveowners.Get(agentID).name,
         'agentInfoIcon': agentInfoIcon,
         'blurbDivision': localization.GetByLabel('UI/Agents/Dialogue/AgentDivision', agentDivision=agentDivision),
         'agentLocation': agentsService.GetAgentMoniker(agentID).GetAgentLocationWrap(),
         'blurbEffectiveStanding': blurbEffectiveStanding,
         'agentSays': agentSays}
        conversationTitle = uiutil.StripTags(localization.GetByLabel('UI/Agents/Dialogue/AgentConversationWith', agentID=agentID), stripOnly=['localized'])
        browser = form.AgentBrowser.Open(windowID='agentalert_%s' % agentID)
        browser.SetMinSize([512, 512])
        browser.LockWidth(512)
        browser.SetCaption(conversationTitle)
        uthread.new(browser.LoadHTML, html)




class Telecom(uicls.Window):
    __guid__ = 'form.Telecom'
    default_windowID = 'telecom'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        transmission = attributes.transmission
        self.isDockWnd = 0
        caption = getattr(transmission, 'caption', None) or localization.GetByLabel('UI/Generic/Information')
        hasDungeonWarp = getattr(transmission, 'hasDungeonWarp', False)
        self.scope = 'inflight'
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(parent=self.sr.topParent, align=uiconst.TOBOTTOM)
        uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TOLEFT, width=70)
        self.sr.header = uicls.EveCaptionMedium(text=' ', parent=self.sr.topParent, align=uiconst.TOTOP, padTop=8)
        self.sr.messageArea = uicls.EditPlainText(parent=self.sr.main, padding=const.defaultPadding, readonly=1)
        self.sr.messageArea.HideBackground()
        self.sr.messageArea.RemoveActiveFrame()
        self.NoSeeThrough()
        self.SetMinSize([360, 240], 1)
        self.SetCaption(caption)
        self.MakeUnResizeable()
        self.MakeUnKillable()
        self.SetTopparentHeight(58)
        if not hasDungeonWarp:
            self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Generic/Close'), okFunc=self.Close)
        else:
            self.sr.instanceID = getattr(transmission.rec.rec, 'instanceID', 0)
            self.sr.solarSystemID = getattr(transmission.rec.rec, 'solarSystemID', 0)
            if self.sr.solarSystemID == eve.session.solarsystemid:
                okLabel = localization.GetByLabel('UI/Commands/WarpTo')
                okFunc = self.WarpToEPLocation
            else:
                inFleet = bool(eve.session.fleetid)
                isLeader = sm.GetService('menu').ImFleetLeaderOrCommander()
                if inFleet and isLeader:
                    okLabel = localization.GetByLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo')
                    okFunc = self.SetFleetDestination
                else:
                    okLabel = localization.GetByLabel('UI/Inflight/SetDestination')
                    okFunc = self.SetDestination
            if self.sr.instanceID and self.sr.solarSystemID:
                self.DefineButtons(uiconst.OKCANCEL, okLabel=okLabel, okFunc=okFunc, cancelLabel=localization.GetByLabel('UI/Generic/Close'), cancelFunc=self.Close)
            else:
                self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Generic/Close'), okFunc=self.Close)



    def SetDestination(self, *args):
        sm.StartService('starmap').SetWaypoint(self.sr.solarSystemID, clearOtherWaypoints=True)
        self.Close()



    def SetFleetDestination(self, *args):
        sol = self.sr.solarSystemID
        sm.StartService('fleet').SendBroadcast_TravelTo(sol)
        self.SetDestination()



    def WarpToEPLocation(self, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if self.sr.instanceID is not None and bp is not None:
            bp.WarpToStuff('epinstance', self.sr.instanceID)
        self.Close()



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
        self.sr.messageArea.SetValue(transmission.text)



    def SetNetResIcon(self, wnd, iconNum = None, headerIcon = 0, scaling = 0.25, fullPath = None):
        return self.SetWndIcon(iconNum, headerIcon, int(256 * scaling), fullPath, mainTop=-6)




