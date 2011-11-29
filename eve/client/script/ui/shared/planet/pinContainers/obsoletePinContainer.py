import planet
import util
import planetCommon
import localization

class ObsoletePinContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.ObsoletePinContainer'

    def _GetActionButtons(self):
        typeObj = cfg.invtypes.Get(self.pin.typeID)
        btns = [util.KeyVal(id=planetCommon.PANEL_DECOMMISSION, panelCallback=self.PanelDecommissionPin, hint=localization.GetByLabel('UI/PI/Common/ObsoletePinReimbursementHint', pinName=typeObj.typeName, iskAmount=util.FmtISK(typeObj.basePrice)))]
        return btns




