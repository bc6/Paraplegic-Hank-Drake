import spaceObject
import nodemanager
import blue

class WarpGate(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.WarpGate'

    def Assemble(self):
        self.SetStaticDirection()
        self.model.boundingSphereRadius = 12000.0
        self.UpdateOnOffState()



    def UpdateOnOffState(self):
        if self.model is None:
            return 
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is None:
            return 
        if not hasattr(slimItem, 'dunOpenUntil'):
            return 
        onCurve = None
        scalarCurves = self.model.Find('trinity.TriScalarCurve')
        for curve in scalarCurves:
            if curve.name == 'onCurve':
                onCurve = curve
                break

        if onCurve is None:
            return 
        dunOpenUntil = slimItem.dunOpenUntil
        if dunOpenUntil is not None:
            onCurve.start = slimItem.dunOpenUntil
        else:
            onCurve.start = blue.os.GetTime() + YEAR




