import uix
import uiutil
import xtriui
import uthread
import form
import blue
import util
import trinity
import service
import listentry
import base
import math
import draw
import sys
import uicls
import uiconst

class DroneSettings(uicls.Window):
    __guid__ = 'form.DroneSettings'
    __notifyevents__ = ['OnDroneSettingChanges']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.droneBehaviour = sm.GetService('godma').GetStateManager().GetDroneSettingAttributes()
        self.fafDefVal = cfg.dgmattribs.Get(const.attributeFighterAttackAndFollow).defaultValue
        self.droneAggressionDefVal = cfg.dgmattribs.Get(const.attributeDroneIsAggressive).defaultValue
        self.droneFFDefVal = cfg.dgmattribs.Get(const.attributeDroneFocusFire).defaultValue
        if not self.droneBehaviour.has_key(const.attributeDroneIsAggressive):
            self.droneBehaviour[const.attributeDroneIsAggressive] = settings.char.ui.Get('droneSettingAttributeID ' + str(const.attributeDroneIsAggressive), 0)
        self.tempStuff = []
        self.scope = 'inflight'
        self.SetCaption(mls.UI_INFLIGHT_DRONE_SETTINGS)
        self.MakeUnResizeable()
        self.SetTopparentHeight(4)
        self.SetWndIcon(None)
        self.HideMainIcon()
        self.height = 140
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, width=5)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=5)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=5)
        parent = uicls.Container(name='parent', parent=self.sr.main, align=uiconst.TOALL)
        self.aggressionParent = uicls.Container(name='aggressionParent', parent=parent, align=uiconst.TOTOP, height=40, width=const.defaultPadding, left=const.defaultPadding)
        droneFocusFireParent = uicls.Container(name='droneFocusFireParent', parent=parent, align=uiconst.TOTOP, height=20, width=const.defaultPadding, left=const.defaultPadding)
        fighterFollowParent = uicls.Container(name='fighterFollowParent', parent=parent, align=uiconst.TOTOP, height=40, width=const.defaultPadding, left=const.defaultPadding)
        self.aggresssionRadioButton = uicls.Container(name='aggresssionRadioButton', parent=self.aggressionParent, pos=(0, 0, 0, 0))
        self.aggresssionRadioButton.left = 10
        for (cfgname, value, label, checked, group,) in [['droneAggression',
          0,
          mls.UI_INFLIGHT_DRONE_ISPASSIVE,
          settings.char.ui.Get('droneAggression', self.droneAggressionDefVal) == 0,
          'aggression'], ['droneAggression',
          1,
          mls.UI_INFLIGHT_DRONE_ISAGGRESSIVE,
          settings.char.ui.Get('droneAggression', self.droneAggressionDefVal) == 1,
          'aggression']]:
            self.tempStuff.append(uicls.Checkbox(text=label, parent=self.aggresssionRadioButton, configName=cfgname, retval=value, checked=checked, groupname=group, callback=self.CheckBoxChange))

        self.aggression = self.tempStuff
        droneFFContainer = uicls.Container(name='droneFocusFireParent', parent=droneFocusFireParent, pos=(0, 0, 0, 0))
        droneFFContainer.left = 10
        self.droneIsFocusFire = uicls.Checkbox(text=mls.UI_INFLIGHT_FOCUS_FIRE, parent=droneFFContainer, configName='droneFocusFire', retval=None, checked=settings.char.ui.Get('droneFocusFire', self.droneFFDefVal), callback=self.CheckBoxChange)
        uix.GetContainerHeader(mls.UI_INFLIGHT_FIGHTER_SETTINGS, fighterFollowParent, 0)
        fafContainer = uicls.Container(name='droneFocusFireParent', parent=fighterFollowParent, pos=(0, 0, 0, 0))
        fafContainer.left = 10
        self.fighterAttackAndFollow = uicls.Checkbox(text=mls.UI_INFLIGHT_DRONE_ATTACK_AND_FOLLOW, parent=fafContainer, configName='fighterAttackAndFollow', retval=None, checked=settings.char.ui.Get('fighterAttackAndFollow', self.fafDefVal), callback=self.CheckBoxChange)



    def CheckBoxChange(self, checkbox):
        if checkbox.data.has_key('config'):
            if checkbox.data['config'] == 'droneAggression':
                if checkbox.data['value'] == settings.char.ui.Get('droneAggression', self.droneAggressionDefVal):
                    return 
                settings.char.ui.Set('droneAggression', checkbox.data['value'])
            if checkbox.data['config'] == 'fighterAttackAndFollow':
                settings.char.ui.Set('fighterAttackAndFollow', checkbox.checked)
            if checkbox.data['config'] == 'droneFocusFire':
                settings.char.ui.Set('droneFocusFire', checkbox.checked)
            self.OnChange()



    def OnChange(self):
        droneSettingChanges = {}
        droneSettingChanges[const.attributeDroneIsAggressive] = settings.char.ui.Get('droneAggression', self.droneAggressionDefVal)
        droneSettingChanges[const.attributeFighterAttackAndFollow] = settings.char.ui.Get('fighterAttackAndFollow', self.fafDefVal)
        droneSettingChanges[const.attributeDroneFocusFire] = settings.char.ui.Get('droneFocusFire', self.droneFFDefVal)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettingChanges)



    def OnDroneSettingChanges(self):
        c = 1
        isAggressive = settings.char.ui.Get('droneAggression', self.droneAggressionDefVal)
        passive = self.aggression[0]
        aggressive = self.aggression[1]
        aggressive.SetChecked(isAggressive, report=0)
        passive.SetChecked((isAggressive + 1) % 2, report=0)
        isFocusFire = settings.char.ui.Get('droneFocusFire', self.droneFFDefVal)
        self.droneIsFocusFire.SetChecked(isFocusFire, report=0)
        isFaf = settings.char.ui.Get('fighterAttackAndFollow', self.fafDefVal)
        self.fighterAttackAndFollow.SetChecked(isFaf, report=0)




