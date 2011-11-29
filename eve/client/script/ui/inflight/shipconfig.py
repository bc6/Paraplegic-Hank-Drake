import listentry
import localization
import util
import moniker
import uicls
import uiconst
import uix

class ShipConfig(uicls.Window):
    __guid__ = 'form.ShipConfig'
    __notifyevents__ = ['ProcessSessionChange', 'OnShipCloneJumpUpdate']
    default_windowID = 'shipconfig'
    shipmodules = [('ShipMaintenanceBay', 'hasShipMaintenanceBay'), ('CloneFacility', 'canReceiveCloneJumps')]

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.shipid = eve.session.shipid
        self.slimItem = self.GetSlimItem()
        self.SetCaption(localization.GetByLabel('UI/Ship/ShipConfig/ShipConfig'))
        self.SetTopparentHeight(72)
        self.SetWndIcon()
        self.SetMinSize([300, 200])
        self.sr.top = uicls.Container(name='top', align=uiconst.TOTOP, parent=self.sr.topParent, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         64))
        icon = uicls.Icon(parent=self.sr.top, align=uiconst.TOLEFT, left=const.defaultPadding, size=64, state=uiconst.UI_NORMAL, typeID=self.slimItem.typeID)
        icon.GetMenu = self.ShipMenu
        uicls.Container(name='push', align=uiconst.TOLEFT, pos=(5, 0, 5, 0), parent=self.sr.top)
        uicls.EveHeaderMedium(name='label', text=cfg.evelocations.Get(self.shipid).name, parent=self.sr.top, align=uiconst.TOTOP, bold=True, state=uiconst.UI_NORMAL)
        uicls.EveLabelMedium(name='label', text=cfg.invtypes.Get(self.slimItem.typeID).name, parent=self.sr.top, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.ship = moniker.GetShipAccess()
        self.conf = self.ship.GetShipConfiguration()
        modules = self.GetShipModules()
        for module in modules:
            self.sr.Set('%sPanel' % module.lower(), uicls.Container(name=module, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, parent=self.sr.main, pos=(0, 0, 0, 0)))

        tabs = [ [name,
         self.sr.Get('%sPanel' % module.lower(), None),
         self,
         module] for (module, name,) in modules.iteritems() if self.sr.Get('%sPanel' % module.lower()) ]
        if tabs:
            self.sr.maintabs = uicls.TabGroup(name='tabparent', align=uiconst.TOTOP, height=18, parent=self.sr.main, idx=0, tabs=tabs, groupID='pospanel')
        else:
            uicls.CaptionLabel(text=localization.GetByLabel('UI/Ship/ShipConfig/ShipConfig'), parent=self.sr.main, size=18, uppercase=0, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding)



    def _OnClose(self, *args):
        self.shipid = None
        self.slimItem = None
        self.capacity = None
        self.tower = None



    def Load(self, key):
        eval('self.Show%s()' % key)



    def ShowShipMaintenanceBay(self):
        if not getattr(self, 'smbinited', 0):
            self.InitShipMaintenanceBayPanel()
        self.panelsetup = 1
        self.sr.smballowfleet.SetChecked(self.conf['allowFleetSMBUsage'])
        self.panelsetup = 0



    def ShowCloneFacility(self):
        if not getattr(self, 'cloneinited', 0):
            self.InitCloneFacilityPanel()
        godmaSM = sm.GetService('godma').GetStateManager()
        self.panelsetup = 1
        cloneRS = sm.GetService('clonejump').GetShipClones()
        scrolllist = []
        for each in cloneRS:
            charinfo = cfg.eveowners.Get(each['ownerID'])
            scrolllist.append(listentry.Get('User', {'charID': each['ownerID'],
             'info': charinfo,
             'cloneID': each['jumpCloneID']}))

        self.sr.clonescroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Name')])
        self.sr.clonescroll.ShowHint([localization.GetByLabel('UI/Ship/ShipConfig/NoClonesInstalledAtShip'), None][bool(scrolllist)])
        numClones = int(len(cloneRS))
        totalClones = int(getattr(godmaSM.GetItem(self.slimItem.itemID), 'maxJumpClones', 0))
        self.sr.cloneInfo.text = localization.GetByLabel('UI/Ship/ShipConfig/NumJumpClones', numClones=numClones, totalClones=totalClones)
        self.panelsetup = 0



    def InitShipMaintenanceBayPanel(self):
        godmaSM = sm.GetService('godma').GetStateManager()
        panel = self.sr.shipmaintenancebayPanel
        s = uicls.Container(parent=panel, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=22)
        self.sr.smballowfleet = uicls.Checkbox(text=localization.GetByLabel('UI/Ship/ShipConfig/AllowFleetMemberUsage'), parent=s, configName='', retval='chkfleet', callback=self.AllowFleetChange, pos=(const.defaultPadding,
         3,
         250,
         0), align=uiconst.TOPLEFT)
        edit = uicls.EditPlainText(setvalue='', parent=panel, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding), hideBackground=0, readonly=1)
        pilots = int(getattr(godmaSM.GetType(self.slimItem.typeID), 'maxOperationalUsers', 0))
        opRange = int(getattr(godmaSM.GetType(self.slimItem.typeID), 'maxOperationalDistance', 0))
        txt = localization.GetByLabel('UI/Ship/ShipConfig/ShipMaintenanceBaySettingText', pilots=pilots, range=opRange)
        edit.SetValue(txt)
        self.smbinited = 1



    def InitCloneFacilityPanel(self):
        panel = self.sr.clonefacilityPanel
        btns = [(localization.GetByLabel('UI/Ship/ShipConfig/Invite'),
          self.InviteClone,
          (),
          84), (localization.GetByLabel('UI/Ship/ShipConfig/Destroy'),
          self.DestroyClone,
          (),
          84)]
        uicls.ButtonGroup(btns=btns, parent=panel)
        cloneInfoContainer = uicls.Container(name='cloneinfo', align=uiconst.TOTOP, parent=panel, left=const.defaultPadding, top=const.defaultPadding, height=12)
        numClones = int(0)
        totalClones = int(getattr(sm.GetService('godma').GetItem(self.slimItem.itemID), 'maxJumpClones', 0))
        text = localization.GetByLabel('UI/Ship/ShipConfig/NumJumpClones', numClones=numClones, totalClones=totalClones)
        self.sr.cloneInfo = uicls.EveLabelSmall(text=text, parent=cloneInfoContainer, align=uiconst.TOALL, left=20, state=uiconst.UI_NORMAL)
        self.sr.clonescroll = uicls.Scroll(name='clonescroll', parent=panel, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.cloneinited = 1



    def AllowFleetChange(self, checkbox):
        if not self.panelsetup:
            self.conf['allowFleetSMBUsage'] = bool(checkbox.checked)
            self.ship.ConfigureShip(self.conf)



    def InviteClone(self, *args):
        if not sm.GetService('clonejump').HasCloneReceivingBay():
            eve.Message('InviteClone1')
            return 
        godmaSM = sm.GetService('godma').GetStateManager()
        opDist = getattr(godmaSM.GetType(self.slimItem.typeID), 'maxOperationalDistance', 0)
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        charIDs = [ slimItem.charID for slimItem in bp.slimItems.itervalues() if slimItem.charID if slimItem.charID != eve.session.charid if not util.IsNPC(slimItem.charID) if slimItem.surfaceDist <= opDist ]
        if not charIDs:
            eve.Message('InviteClone2')
            return 
        lst = []
        for charID in charIDs:
            char = cfg.eveowners.Get(charID)
            lst.append((char.name, charID, char.typeID))

        chosen = uix.ListWnd(lst, 'character', localization.GetByLabel('UI/Ship/ShipConfig/SelectAPilot'), None, 1, minChoices=1, isModal=1)
        if chosen:
            sm.GetService('clonejump').OfferShipCloneInstallation(chosen[1])



    def DestroyClone(self, *args):
        for each in self.sr.clonescroll.GetSelected():
            sm.GetService('clonejump').DestroyInstalledClone(each.cloneID)




    def GetSlimItem(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp and self.shipid in bp.slimItems:
            return bp.slimItems[self.shipid]



    def GetShipModules(self):
        typeID = self.slimItem.typeID
        godmaSM = sm.GetService('godma').GetStateManager()
        hasModules = {}
        for module in self.shipmodules:
            if getattr(godmaSM.GetType(typeID), module[1], 0):
                nameString = ''
                if module[0] == 'ShipMaintenanceBay':
                    nameString = localization.GetByLabel('UI/Ship/ShipConfig/ShipMaintenanceBay')
                elif module[0] == 'CloneFacility':
                    nameString = localization.GetByLabel('UI/Ship/ShipConfig/CloneFacility')
                hasModules[module[0]] = nameString

        return hasModules



    def ShipMenu(self):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(self.slimItem.itemID, self.slimItem.typeID)



    def ProcessSessionChange(self, isRemote, session, change):
        if session.shipid and 'shipid' in change:
            self.CloseByUser()
        elif 'solarsystemid' in change:
            self.CloseByUser()



    def OnShipCloneJumpUpdate(self):
        if self.sr.maintabs.GetSelectedArgs() == 'CloneFacility':
            self.ShowCloneFacility()




