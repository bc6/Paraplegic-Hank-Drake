import form
import xtriui
import uix
import uiutil
import util
import uthread
import uiconst
import uicls
import blue
from fleetcommon import *
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 440

class RegisterFleetWindow(uicls.Window):
    __guid__ = 'form.RegisterFleetWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        fleetInfo = attributes.fleetInfo
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_FLEET_REGISTERFLEET)
        self.SetWndIcon(None)
        self.windowHeight = WINDOW_HEIGHT
        if session.warfactionid is not None or session.allianceid is not None:
            self.windowHeight += 20
        self.SetMinSize([WINDOW_WIDTH, self.windowHeight])
        self.MakeUnResizeable()
        self.sr.scopeRadioButtons = []
        uix.Flush(self.sr.main)
        self.SetupContainers()
        self.SetupStuff(fleetInfo)



    def SetupContainers(self):
        self.sr.top = uicls.Container(name='top', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 120), padding=(0, 0, 0, 0))
        self.sr.rest = uicls.Container(name='rest', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.fleetNameParent = uicls.Container(name='fleetNameParent', parent=self.sr.top, align=uiconst.TOTOP, pos=(0, 0, 0, 30), padding=(6,
         const.defaultPadding,
         6,
         0))
        self.sr.detailsParent = uicls.Container(name='detailsParent', parent=self.sr.top, align=uiconst.TOTOP, pos=(0, 0, 0, 80), padding=(6,
         const.defaultPadding,
         6,
         0))
        self.sr.bottom = uicls.Container(name='bottom', parent=self.sr.rest, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 35), padding=(0, 0, 0, 0))
        self.sr.scopeParent = uicls.Container(name='scopeParent', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 30), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0))
        self.sr.filterParent = uicls.Container(name='filterParent', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 75), padding=(18,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.filterStanding = uicls.Container(name='filterStanding', parent=self.sr.filterParent, align=uiconst.TOTOP, pos=(0, 0, 0, 12), padding=(0, 0, 0, 0))
        self.sr.filterStandingRB = uicls.Container(name='filterStandingRB', parent=self.sr.filterParent, align=uiconst.TOTOP, pos=(0, 3, 0, 30), padding=(12, 0, 0, 0))
        self.sr.filterSecurity = uicls.Container(name='filterSecurity', parent=self.sr.filterParent, align=uiconst.TOTOP, pos=(0, 0, 0, 33), padding=(0, 2, 0, 0))
        self.sr.publicParent = uicls.Container(name='publicParent', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 16), padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.sr.publicFilterParent = uicls.Container(name='publicFilterParent', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 74), padding=(18,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.publicFilterStanding = uicls.Container(name='publicFilterStanding', parent=self.sr.publicFilterParent, align=uiconst.TOTOP, pos=(0, 0, 0, 12), padding=(0, 0, 0, 0))
        self.sr.publicFilterStandingRB = uicls.Container(name='publicFilterStandingRB', parent=self.sr.publicFilterParent, align=uiconst.TOTOP, pos=(0, 3, 0, 30), padding=(0, 0, 0, 0))
        self.sr.publicFilterSecurity = uicls.Container(name='publicFilterSecurity', parent=self.sr.publicFilterParent, align=uiconst.TOTOP, pos=(0, 0, 0, 33), padding=(0, 2, 0, 0))
        line = uicls.Container(name='line', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 1), padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        uicls.Line(parent=line, align=uiconst.TOALL)
        self.sr.optionsParent = uicls.Container(name='optionsParent', parent=self.sr.rest, align=uiconst.TOTOP, pos=(0, 0, 0, 30), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))



    def SetupStuff(self, fleetInfo = None):
        fleetName = mls.UI_FLEET_DEFAULTFLEETNAME % {'name': cfg.eveowners.Get(session.charid).name}
        inviteScope = INVITE_CORP
        description = ''
        needsApproval = False
        localMinStanding = None
        localMinSecurity = None
        publicMinStanding = None
        publicMinSecurity = None
        hideInfo = False
        myCorp = False
        myAlliance = False
        myMilitia = False
        isPublic = False
        publicIsGood = False
        publicIsHigh = False
        localIsGood = False
        localIsHigh = False
        if fleetInfo is not None:
            fleetName = fleetInfo.fleetName
            description = fleetInfo.description
            needsApproval = fleetInfo.joinNeedsApproval
            hideInfo = fleetInfo.hideInfo
            localMinStanding = fleetInfo.local_minStanding
            localMinSecurity = fleetInfo.local_minSecurity
            publicMinStanding = fleetInfo.public_minStanding
            publicMinSecurity = fleetInfo.public_minSecurity
            myCorp = IsOpenToCorp(fleetInfo)
            myAlliance = IsOpenToAlliance(fleetInfo)
            myMilitia = IsOpenToMilitia(fleetInfo)
            isPublic = IsOpenToPublic(fleetInfo)
            if publicMinStanding == const.contactGoodStanding:
                publicIsGood = True
            elif publicMinStanding == const.contactHighStanding:
                publicIsHigh = True
            if localMinStanding == const.contactGoodStanding:
                localIsGood = True
            elif localMinStanding == const.contactHighStanding:
                localIsHigh = True
        self.sr.fleetName = uicls.SinglelineEdit(name='fleetName', parent=self.sr.fleetNameParent, align=uiconst.TOALL, pos=(1, 13, 0, 0), maxLength=FLEETNAME_MAXLENGTH, label=mls.UI_FLEET_NAMEOFFLEET, setvalue=fleetName)
        uicls.Label(text=mls.UI_GENERIC_DESCRIPTION, parent=self.sr.detailsParent, top=6, fontsize=10, letterspace=1, linespace=9, uppercase=1)
        self.sr.description = uicls.EditPlainText(setvalue=description, parent=self.sr.detailsParent, align=uiconst.TOALL, maxLength=FLEETDESC_MAXLENGTH, top=22)
        openFleetText = uicls.Label(text=mls.UI_FLEET_OPENTO, parent=self.sr.scopeParent, align=uiconst.TOTOP, uppercase=1, fontsize=9, letterspace=2, state=uiconst.UI_NORMAL)
        openFleetText.padLeft = 3
        self.sr.myCorpButton = uicls.Checkbox(text=mls.UI_GENERIC_MYCORPORATION, parent=self.sr.scopeParent, configName='corp', retval='1', checked=myCorp)
        self.sr.myCorpButton.hint = mls.UI_FLEET_CORPONLY_HINT
        if session.allianceid is not None:
            self.sr.myAllianceButton = uicls.Checkbox(text=mls.UI_CONTRACTS_MYALLIANCE, parent=self.sr.scopeParent, configName='alliance', retval='1', checked=myAlliance)
            self.sr.myAllianceButton.hint = mls.UI_FLEET_ALLIANCEONLY_HINT
            self.sr.scopeParent.height += 16
        if session.warfactionid is not None:
            self.sr.myMilitiaButton = uicls.Checkbox(text=mls.UI_FLEET_MYMILITIA, parent=self.sr.scopeParent, configName='militia', retval='1', checked=myMilitia)
            self.sr.myMilitiaButton.hint = mls.UI_FLEET_MILITIAONLY_HINT
            self.sr.scopeParent.height += 16
        self.sr.requireLocalStandingButton = uicls.Checkbox(text='%s:' % mls.UI_FLEET_REQUIRESTANDING, parent=self.sr.filterStanding, configName='requireLocalStanding', retval='1', checked=bool(localMinStanding))
        self.sr.requireLocalStandingButton.hint = mls.UI_FLEET_REQUIRESTANDING_HINT
        self.sr.localGoodStandingCB = uicls.Checkbox(text=mls.UI_CONTACTS_GOODSTANDING, parent=self.sr.filterStandingRB, configName='localgood', reval=const.contactGoodStanding, checked=localIsGood, groupname='localStanding')
        self.sr.localHighStandingCB = uicls.Checkbox(text=mls.UI_CONTACTS_HIGHSTANDING, parent=self.sr.filterStandingRB, configName='localhigh', reval=const.contactHighStanding, checked=localIsHigh, groupname='localStanding')
        self.sr.requireLocalSecurityButton = uicls.Checkbox(text='%s:' % mls.UI_FLEET_REQUIRESECURITY, parent=self.sr.filterSecurity, configName='requireLocalSecurity', retval='1', checked=localMinSecurity is not None)
        self.sr.requireLocalSecurityButton.hint = mls.UI_FLEET_REQUIRESECURITY_HINT
        startVal = 0.5
        if localMinSecurity is not None:
            startVal = localMinSecurity / 20.0 + 0.5
        self.sr.localSecuritySlider = self.AddSlider(self.sr.filterSecurity, 'localSecurity', -10, 10.0, '', startVal=startVal)
        self.sr.localSecuritySlider.SetValue(startVal)
        self.sr.publicButton = uicls.Checkbox(text=mls.UI_FLEET_STANDINGONLY, parent=self.sr.publicParent, configName='public', retval='1', checked=isPublic)
        self.sr.publicButton.hint = mls.UI_FLEET_ADDPILOTS
        standingText = uicls.Label(text='%s:' % mls.UI_FLEET_REQUIRESTANDING, parent=self.sr.publicFilterStanding, align=uiconst.TOTOP, uppercase=1, fontsize=9, letterspace=2, state=uiconst.UI_NORMAL)
        standingText.padLeft = 3
        self.sr.publicGoodStandingCB = uicls.Checkbox(text=mls.UI_CONTACTS_GOODSTANDING, parent=self.sr.publicFilterStandingRB, configName='publicgood', reval=const.contactGoodStanding, checked=publicIsGood, groupname='publicStanding')
        self.sr.publicHighStandingCB = uicls.Checkbox(text=mls.UI_CONTACTS_HIGHSTANDING, parent=self.sr.publicFilterStandingRB, configName='publichigh', reval=const.contactHighStanding, checked=publicIsHigh, groupname='publicStanding')
        self.sr.requirePublicSecurityButton = uicls.Checkbox(text='%s:' % mls.UI_FLEET_REQUIRESECURITY, parent=self.sr.publicFilterSecurity, configName='requirePublicSecurity', retval='1', checked=publicMinSecurity is not None)
        self.sr.requirePublicSecurityButton.hint = mls.UI_FLEET_REQUIRESECURITY_HINT
        startVal = 0.5
        if publicMinSecurity is not None:
            startVal = publicMinSecurity / 20.0 + 0.5
        self.sr.publicSecuritySlider = self.AddSlider(self.sr.publicFilterSecurity, 'publicSecurity', -10, 10.0, '', startVal=startVal)
        self.sr.publicSecuritySlider.SetValue(startVal)
        self.sr.needsApprovalButton = uicls.Checkbox(text=mls.UI_FLEET_REQUIRESAPPROVAL, parent=self.sr.optionsParent, configName='needsApproval', retval='1', checked=needsApproval)
        self.sr.needsApprovalButton.hint = mls.UI_FLEET_REQUIRESAPPROVAL_HINT
        self.sr.hideInfoButton = uicls.Checkbox(text=mls.UI_FLEET_HIDEINFO, parent=self.sr.optionsParent, configName='hideInfo', retval='1', checked=hideInfo)
        self.sr.hideInfoButton.hint = mls.UI_FLEET_HIDEINFO_HINT
        self.sr.submitButtons = uicls.ButtonGroup(btns=[[mls.UI_CMD_SUBMIT, self.Submit, ()], [mls.UI_CMD_CANCEL, self.CloseX, ()]], parent=self.sr.bottom, idx=0)
        uthread.new(self.PostStartup)



    def PostStartup(self):
        self.SetHeight(self.windowHeight)



    def SlideIt(self, startVal):
        self.sr.slider.SlideTo(startVal, 1)



    def AddSlider(self, where, config, minval, maxval, header, hint = '', startVal = 0):
        h = 10
        _par = uicls.Container(name=config + '_slider', parent=where, align=uiconst.TOTOP, pos=(0, 0, 180, 10), padding=(0, 0, 0, 0))
        par = uicls.Container(name=config + '_slider_sub', parent=_par, align=uiconst.TOPLEFT, pos=(18, 0, 180, 10), padding=(0, 0, 0, 0))
        slider = xtriui.Slider(parent=par)
        lbl = uicls.Label(text='bla', parent=par, width=200, left=-34, top=0, fontsize=9, letterspace=2, autowidth=False, state=uiconst.UI_NORMAL)
        setattr(self.sr, '%sLabel' % config, lbl)
        lbl.name = 'label'
        slider.SetSliderLabel = getattr(self, 'SetSliderLabel_%s' % config)
        lbl.state = uiconst.UI_HIDDEN
        slider.Startup(config, minval, maxval, None, header, startVal=startVal)
        if startVal < minval:
            startVal = minval
        slider.value = startVal
        slider.name = config
        slider.hint = hint
        slider.OnSetValue = getattr(self, 'OnSetValue_%s' % config)
        return slider



    def SetSliderLabel_localSecurity(self, label, idname, dname, value):
        self.sr.localSecurityLabel.text = '%.1f' % value



    def SetSliderLabel_publicSecurity(self, label, idname, dname, value):
        self.sr.publicSecurityLabel.text = '%.1f' % value



    def OnSetValue_localSecurity(self, *args):
        self.sr.requireLocalSecurityButton.SetLabelText('%s: %.1f' % (mls.UI_FLEET_REQUIRESECURITY, float(self.sr.localSecurityLabel.text)))



    def OnSetValue_publicSecurity(self, *args):
        self.sr.requirePublicSecurityButton.SetLabelText('%s: %.1f' % (mls.UI_FLEET_REQUIRESECURITY, float(self.sr.publicSecurityLabel.text)))



    def Submit(self):
        fleetSvc = sm.GetService('fleet')
        info = util.KeyVal()
        info.fleetName = self.sr.fleetName.GetValue()
        info.description = self.sr.description.GetValue()
        info.inviteScope = INVITE_CLOSED
        info.public_minStanding = None
        info.public_minSecurity = None
        info.public_allowedEntities = set()
        info.local_minStanding = None
        info.local_minSecurity = None
        info.local_allowedEntities = set()
        if self.sr.myCorpButton.checked:
            info.inviteScope += INVITE_CORP
        if session.allianceid is not None:
            if self.sr.myAllianceButton.checked:
                info.inviteScope += INVITE_ALLIANCE
        if session.warfactionid is not None:
            if self.sr.myMilitiaButton.checked:
                info.inviteScope += INVITE_MILITIA
        if self.sr.publicButton.checked:
            info.inviteScope += INVITE_PUBLIC
            if self.sr.publicGoodStandingCB.checked:
                info.public_minStanding = const.contactGoodStanding
            elif self.sr.publicHighStandingCB.checked:
                info.public_minStanding = const.contactHighStanding
            else:
                raise UserError('FleetInviteAllWithoutStanding')
            info.public_allowedEntities = self.GetAllowedEntities(info.public_minStanding)
            if self.sr.requirePublicSecurityButton.checked:
                info.public_minSecurity = self.sr.publicSecuritySlider.value
        noAccess = False
        if IsOpenToCorp(info) or IsOpenToAlliance(info) or IsOpenToMilitia(info):
            if self.sr.requireLocalStandingButton.checked:
                if self.sr.localGoodStandingCB.checked:
                    info.local_minStanding = const.contactGoodStanding
                elif self.sr.localHighStandingCB.checked:
                    info.local_minStanding = const.contactHighStanding
                else:
                    raise UserError('FleetInviteAllWithoutStanding')
                info.local_allowedEntities = self.GetAllowedEntities(info.local_minStanding)
            elif IsOpenToCorp(info):
                info.local_allowedEntities.add(session.corpid)
            if session.allianceid is not None and IsOpenToAlliance(info):
                info.local_allowedEntities.add(session.allianceid)
            if session.warfactionid is not None and IsOpenToMilitia(info):
                info.local_allowedEntities.add(session.warfactionid)
            if self.sr.requireLocalSecurityButton.checked:
                info.local_minSecurity = self.sr.localSecuritySlider.value
        elif not IsOpenToPublic(info):
            noAccess = True
        if IsOpenToPublic(info) and info.public_minStanding is not None:
            if len(info.public_allowedEntities) + len(info.local_allowedEntities) == 0:
                noAccess = True
        if noAccess:
            if eve.Message('FleetNobodyHasAccess', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
        info.joinNeedsApproval = not not self.sr.needsApprovalButton.checked
        info.hideInfo = not not self.sr.hideInfoButton.checked
        fleetSvc.RegisterFleet(info)
        self.CloseX()



    def GetAllowedEntities(self, minRelationship):
        return sm.GetService('addressbook').GetContactsByMinRelationship(minRelationship)




