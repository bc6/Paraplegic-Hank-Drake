import effects

class GasHarvest(effects.StandardWeapon):
    __guid__ = 'effects.CloudMining'
    __gfx__ = None

    def SetAmmoColor(self):
        targetBall = self.GetEffectTargetBall()
        targetModel = getattr(targetBall, 'model', None)
        materialList = [ x for x in targetModel.Find('trinity.TriMaterial') if x.name == 'ammo' ]
        if len(materialList):
            material = materialList[0]
        else:
            return 
        self.turret.SetAmmoColor(material.emissive)




