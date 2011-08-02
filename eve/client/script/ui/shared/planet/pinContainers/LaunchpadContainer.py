import uiconst
import util
import uicls
import planet

class LaunchpadContainer(planet.ui.StorageFacilityContainer):
    __guid__ = 'planet.ui.LaunchpadContainer'
    default_name = 'LaunchpadContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)



    def _GetActionButtons(self):
        btns = [util.KeyVal(name=mls.UI_PI_LAUNCH, panelCallback=self.PanelLaunch, icon='ui_44_32_6'), util.KeyVal(name=mls.UI_PI_STORAGE, panelCallback=self.PanelShowStorage, icon='ui_44_32_3')]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns



    def PanelLaunch(self):
        bp = sm.GetService('michelle').GetBallpark()
        text = None
        if bp is not None and not self.pin.IsInEditMode():
            cargoLinkIDs = bp.GetCargoLinksForPlanet(sm.GetService('planetUI').planetID)
            if cargoLinkIDs is not None and len(cargoLinkIDs) > 0:
                try:
                    sm.GetService('planetUI').OpenPlanetCargoLinkImportWindow(cargoLinkIDs[0], self.pin.id, True)
                    self.CloseX()
                    return 
                except UserError as e:
                    if e.msg == 'ShipCloaked':
                        text = mls.UI_PI_CANNOTACCESSLAUNCHPADWHILECLOAKED
                    else:
                        message = cfg.GetMessage(e.msg)
                        text = message.text
        if text is None:
            if self.pin.IsInEditMode():
                text = mls.UI_PI_CUSTOMSOFFICEINACCESSIBLENOTBUILT
            else:
                text = mls.UI_PI_SPACEPORT_CANNOTACCESSCARGOLINK
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        editBox = self._DrawEditBox(cont, text)
        cont.height = editBox.height + 4
        return cont




