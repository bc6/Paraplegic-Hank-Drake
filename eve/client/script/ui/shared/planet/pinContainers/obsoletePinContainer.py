import planet
import util

class ObsoletePinContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.ObsoletePinContainer'

    def _GetActionButtons(self):
        typeObj = cfg.invtypes.Get(self.pin.typeID)
        btns = [util.KeyVal(name=mls.UI_PI_DECOMMISSION, panelCallback=self.PanelDecommissionPin, icon='ui_44_32_4', hint=mls.UI_PI_OBSOLETEPINREIMBURSEMENTHINT % {'typeName': typeObj.typeName,
          'isk': util.FmtISK(typeObj.basePrice)})]
        return btns




