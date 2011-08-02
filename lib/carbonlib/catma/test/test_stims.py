from catma.stims import *
from catma import stims
import unittest

class TestStims(unittest.TestCase):
    seq = None
    MANNER_UNFIT = 'UNFIT'

    def setUp(self):
        if not self.seq:
            self.seq = Sequencer()



    def tearDown(self):
        if self.seq:
            pass



    def _TestAttributesChange(self, adapter, manner, modifiers, adapterAttributes):
        allValues = adapter.GetAttributeValues()
        expectedResult = {}
        for am in modifiers:
            attributeName = am.attributeName
            modifierType = am.modifierType
            modifierValue = am.modifierValue
            initialValue = adapterAttributes[attributeName]
            expectedValue = None
            if manner == self.MANNER_UNFIT:
                expectedValue = initialValue
            elif manner == MANNER_PASSIVE:
                if modifierType == MOD_ADD:
                    expectedValue = initialValue + modifierValue
                elif modifierType == MOD_MUL:
                    expectedValue = initialValue * modifierValue
                else:
                    expectedValue = modifierValue
            else:
                raise RuntimeError('Unsupported manner: {0}'.format(manner))
            (base, passive, active,) = allValues[attributeName]
            self.assertEqual(initialValue, base)
            self.assertEqual(expectedValue, passive)
            self.assertEqual(expectedValue, active)
            expectedResult[attributeName] = expectedValue

        (stateChanges, attribChanges, directAttribChanges,) = self.seq.UpdateTime(1.0)
        for c in attribChanges:
            if c[0] is adapter:
                result = dict(((e[0], e[1]) for e in c[1]))
                self.assertEqual(result, expectedResult)
                break

        (stateChanges, attribChanges, directAttribChanges,) = self.seq.UpdateTime(1.0)
        for c in attribChanges:
            self.assertTrue(c[0] is not adapter)




    def testAddAdapter(self):
        adapterAttributes = {'CPU': 500.0,
         'PG': 200.0,
         'maxSpeed': 160.0,
         'shieldHP': 85.0,
         'armorHP': 85.0,
         'weight': 2850.0,
         'maxTorque': 850.0}
        adapter = Adapter(typeID='lav_test', fittingInfo=[SLOTTYPE_VEHICLE_HIGH,
         SLOTTYPE_VEHICLE_HIGH,
         SLOTTYPE_VEHICLE_HIGH,
         SLOTTYPE_VEHICLE_LOW,
         SLOTTYPE_VEHICLE_LOW,
         SLOTTYPE_VEHICLE_LOW,
         SLOTTYPE_SMALL_WEAPON,
         SLOTTYPE_MEDIUM_WEAPON], attributes=adapterAttributes)
        self.seq.AddAdapter(adapter)
        parameters = {}
        parameters['typeID'] = 0
        parameters['slotType'] = SLOTTYPE_VEHICLE_HIGH
        parameters['duration'] = 5.0
        parameters['rechargeTime'] = 1.0
        parameters['cycles'] = 100
        parameters['activationTime'] = 0.0
        parameters['manner'] = MANNER_PASSIVE
        attributeModifiers = [['CPU', MOD_ADD, -40.0],
         ['PG', MOD_ADD, -45.0],
         ['maxSpeed', MOD_ADD, -15.0],
         ['armorHP', MOD_ADD, -15.0],
         ['weight', MOD_MUL, 1.2],
         ['shieldHP', MOD_BASE, 100]]
        attributeModifiers = [ dict(attributeName=e[0], modifierType=e[1], modifierValue=e[2]) for e in attributeModifiers ]
        activeAttributeModifiers = []
        attributeModifiers = [ stims.AttributeModifier(**e) for e in attributeModifiers ]
        activeAttributeModifiers = [ stims.AttributeModifier(**e) for e in activeAttributeModifiers ]
        moduleData = ModuleData(parameters, attributeModifiers, activeAttributeModifiers, stims.dummyLockOnSpec)
        module = Module(moduleData)
        adapter.FitModule(module, 0)
        self._TestAttributesChange(adapter, MANNER_PASSIVE, attributeModifiers, adapterAttributes)
        adapter.UnfitModule(0)
        self._TestAttributesChange(adapter, self.MANNER_UNFIT, attributeModifiers, adapterAttributes)



if __name__ == '__main__':
    unittest.main()

