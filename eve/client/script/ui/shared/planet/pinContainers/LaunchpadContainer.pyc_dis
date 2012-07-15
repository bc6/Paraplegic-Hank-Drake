#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/pinContainers/LaunchpadContainer.py
import uiconst
import util
import uicls
import planet
import planetCommon
import localization

class LaunchpadContainer(planet.ui.StorageFacilityContainer):
    __guid__ = 'planet.ui.LaunchpadContainer'
    default_name = 'LaunchpadContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_LAUNCH, panelCallback=self.PanelLaunch), util.KeyVal(id=planetCommon.PANEL_STORAGE, panelCallback=self.PanelShowStorage)]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns

    def PanelLaunch(self):
        bp = sm.GetService('michelle').GetBallpark()
        text = None
        if bp is not None and not self.pin.IsInEditMode():
            customsOfficeIDs = sm.GetService('planetInfo').GetOrbitalsForPlanet(sm.GetService('planetUI').planetID, const.groupPlanetaryCustomsOffices)
            if len(customsOfficeIDs) > 0:
                try:
                    customsOfficeID = None
                    for ID in customsOfficeIDs:
                        customsOfficeID = ID
                        break

                    sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID, self.pin.id)
                    self.CloseByUser()
                    return
                except UserError as e:
                    if e.msg == 'ShipCloaked':
                        text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadWhileCloaked')
                    else:
                        message = cfg.GetMessage(e.msg)
                        text = message.text

        if text is None:
            if self.pin.IsInEditMode():
                text = localization.GetByLabel('UI/PI/Common/CustomsOfficeNotBuilt')
            else:
                solarSystemID = sm.GetService('planetUI').GetCurrentPlanet().solarSystemID
                if solarSystemID == session.locationid:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadNotThere')
                else:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadLocation')
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        editBox = self._DrawEditBox(cont, text)
        cont.height = editBox.height + 4
        return cont