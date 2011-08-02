from catma.catmaConfig import *
from catma import stims
from catma.axiom import Enumerate
from extraCatmaConfig import *
try:
    from dust.catmaExtension import AttributeReference, AttribRefForModAttribModifier
except ImportError:
    import sys
    import blue
    import os
    sys.path.append(os.path.abspath(blue.os.rootpath + '..\\common\\modules'))
    from dust.catmaExtension import AttributeReference, AttribRefForModAttribModifier

def _InitEnumTypes(ax2):
    typeDef = ax2.CreateType('EModuleEvent', Enumerate, group=GROUPS.Logic)
    typeDef.AddElement('EME_DID_FIT')
    typeDef.AddElement('EME_WILL_UNFIT')
    typeDef.AddElement('EME_IS_IDLE')
    typeDef.AddElement('EME_IS_ACTIVATING')
    typeDef.AddElement('EME_DID_START_PULSE')
    typeDef.AddElement('EME_DID_FINISH_PULSE')
    typeDef.AddElement('EME_IS_CHARGING')
    typeDef.AddElement('EME_DID_CHARGE')
    typeDef.AddElement('EME_OWNER_DID_DIE')



def PopulateMSEs(ax2):
    _InitEnumTypes(ax2)
    typeDef = ax2.CreateType('DustMSE', standalone=True, group=GROUPS.Logic)
    typeDef.AddMember('EModuleEvent eventsOfInterest', caption='Triggers', text='For which triggers the MSE internally takes an action', attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.IS_SET)
    typeDef.AddMember('String mUE3Class', caption='UE3 Class', text='The UE3 object class used to create this object')
    typeDef = ax2.CreateType('DustMSEPlayEffect', standalone=True, group=GROUPS.Logic, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('TaggedEffect effects', text='The (particle effect) this MSE will play.', attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.IS_SET)
    typeDef = ax2.CreateType('DustMSEExplosiveSuicide', standalone=True, group=GROUPS.Logic)
    typeDef.AddMember('Float mBaseDamage = 500', group=GROUPS.Combat, caption='Explosion Damage Amount', range=(0.0, None))
    typeDef.AddMember('Meter mDamageRadius = 10', group=GROUPS.Combat, caption='Explosion Damage Radius', range=(0.0, None))
    typeDef.AddMember('Float mMomentum = 100', group=GROUPS.Combat, caption='Explosion Damage Momentum', range=(0.0, None))
    typeDef.AddMember('TypeReference mExplosionType', allowedClasses='ExplosionContent', text='The type id used to spawn explosion', group=GROUPS.Content, caption='Explosion Type ID')
    typeDef = ax2.CreateType('DustMSEChameleonField', standalone=True, forUE3=False, group=GROUPS.Logic)
    typeDef.AddMember('ContentReference mVisualEffectMaterial', group=GROUPS.Content, caption='Visual Effect Material', text='The material applied to the object to make the visual effect.')
    typeDef.AddMember('Name mInterpParamName = RDV_Cloaking', group=GROUPS.Content, caption='Visual Effect Interpolation Parameter', text='The name of the parameter in the material used to control the visual effect interpolation.')
    typeDef.AddMember('Float mInterpDuration = 3', group=GROUPS.Logic, range=(0.0, None), caption='Visual Effect Interpolation Duration', text='The duration of the visual effect interpolation.')
    typeDef = ax2.CreateType('DustMSESpeedBlur', standalone=True, forUE3=False, group=GROUPS.Logic)
    typeDef.AddMember('MeterPerSecond mMinBlurSpeed = 2', group=GROUPS.Logic, range=(0.0, None), caption='Min Blur Speed', text='The min speed which and below which the blur scale is considered to 0.')
    typeDef.AddMember('MeterPerSecond mMaxBlurSpeed = 10', group=GROUPS.Logic, range=(0.0, None), caption='Max Blur Speed', text='The max speed which and above which the max blur scale is considered to be applied.')
    typeDef.AddMember('Float mMaxBlurScale = 2', group=GROUPS.Logic, range=(0.0, None), caption='Max Blur Scale', text='The max amount of scale that should be applied for the blur effect.')



def PopulateUniqueModules(ax2):
    typeDef = ax2.CreateType('ModuleCloaking', standalone=True, forUE3=False, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('ContentReference mMaterialOverride', group=GROUPS.Content, caption='Material to Override', text='The material applied to the object when the module is activated')
    typeDef = ax2.CreateType('RepairSpec', standalone=False, forUE3=True)
    typeDef.AddMember('Float armorRepairRate = 0', range=(0, None), caption='Armor Repair Rate')
    typeDef.AddMember('Float shieldRepairRate = 0', range=(0, None), caption='Shield Repair Rate')
    typeDef.AddMember('Float healthRepairRate = 0', range=(0, None), caption='Health Repair Rate')
    typeDef.AddMember('Bool asPercentage = False', caption='Rate as Percentage?')
    typeDef = ax2.CreateType('ModuleGenericRepair', standalone=True, group=GROUPS.Logic, forUE3=True, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('Bool mAllowUsedOnHost', caption='Can use on host')
    typeDef.AddMember('RepairSpec mInfantrySpec', caption='Repair Spec - Infanry')
    typeDef.AddMember('RepairSpec mVehicleSpec', caption='Repair Spec - Vehicle')
    typeDef.AddMember('ContentReference mSpecialEffectTemplate', caption='Special Effect', group=GROUPS.Content, attributeFlag=DEFAULT_ATTRIB_FLAGS ^ ATTRIB_FLAGS.EXPORTED)



def PopulateModules(ax2):
    PopulateMSEs(ax2)
    typeDef = ax2.CreateType('EModuleCreationCondition', Enumerate, forUE3=True)
    typeDef.AddElement('MNU_LocalOnly', description='Local Only')
    typeDef.AddElement('MNU_ServerOnly', description='Server Only')
    typeDef.AddElement('MNU_ServerAndOwningClient', description='Server and Owning Client')
    typeDef.AddElement('MNU_ServerAndClients', description='Server and All Clients')
    typeDef = ax2.CreateType('AttribRefForModAttribModifier', AttribRefForModAttribModifier)
    typeDef = ax2.CreateType('EModuleType', Enumerate, forUE3=False)
    typeDef.AddElement('MT_General')
    typeDef.AddElement('MT_Spawn')
    typeDef = ax2.CreateType('EModuleMannerOfUse', Enumerate, forUE3=False)
    for manner in stims.MOD_MANNERS_OF_USE_ALL:
        typeDef.AddElement(manner)

    typeDef = ax2.CreateType('ESlotType', Enumerate, forUE3=False)
    for (slotType, slotDesc,) in stims.slotTypes.items():
        typeDef.AddElement(slotType, '%s : %s' % (slotType, slotDesc))

    typeDef = ax2.CreateType('EAttributeModifier', Enumerate, forUE3=False)
    for modifier in stims.MOD_ALL:
        typeDef.AddElement(modifier)

    typeDef = ax2.CreateType('EModuleAttributeType', Enumerate, forUE3=False, modifyFlag=MODIFY_REMOVED)
    typeDef = ax2.CreateType('AttributeModifier', standalone=False, group=GROUPS.Logic, forUE3=False, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('AttribRefForModAttribModifier attributeName', modifyFlag=MODIFY_TYPE_CHANGED, allowedAttributeFlags=ATTRIB_FLAGS.MODULIZED, text='The name of the attribute to be modified', caption='Attribute Name')
    typeDef.AddMember('Float modifierValue', text='The value to apply', caption='Modifier Value')
    typeDef.AddMember('EAttributeModifier modifierType', text='The modifier type in terms of operation', caption='Modifier Type')
    typeDef.AddMember('Bool modifierValueBool', modifyFlag=MODIFY_REMOVED, text='The value of boolean modifier, can only be used with replace(2) operation', caption='Modifier Value Bool', attributeFlag=DEFAULT_ATTRIB_FLAGS)
    typeDef.AddMember('EModuleAttributeType attributeType', modifyFlag=MODIFY_REMOVED, text='Module attribute types', caption='Module Attribute Types')
    typeDef = ax2.CreateType('DustModule', standalone=True, group=GROUPS.Logic, forUE3=False, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('EModuleType moduleType = MT_General', text='The type of this module', caption='Module Type')
    typeDef.AddMember('ESlotType slotType', text='Which type of slot this module is compatible with', caption='Slot Type')
    typeDef.AddMember('String mModifierClasses', text="a list of CATMA class names connected by '+' whose attributes with the 'Modulized' flag will be considered as valid modifier attribute name", caption='Modifier Classes')
    typeDef.AddMember('AttributeModifier modifier', caption='Attribute Modifiers', text='Attribute modifiers applied regardless module is activated or not.', attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.IS_SET)
    typeDef.AddMember('TypeReference requiredSkill', allowedClasses='Skill', text='A character must have this skill to use this module', caption='Required Skill')
    typeDef = ax2.CreateType('DustModuleAdvanced', standalone=True, group=GROUPS.Logic, forUE3=False, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('Bool isPassive = True', text='Whether this is a passive module', caption='Passive?', modifyFlag=MODIFY_REMOVED)
    typeDef.AddMember('Bool isTogglable = False', text='If true, module can be turned on/off manually (by a player that is)', caption='Is Togglable', modifyFlag=MODIFY_REMOVED)
    typeDef.AddMember('EModuleMannerOfUse manner = ' + stims.MANNER_PASSIVE, text='In which manner the module is to be used', caption='Manner Of Use')
    typeDef.AddMember('Second activationTime', range=(0, None), text='How long it takes for this module to become active. <=0 for indefinitely', caption='Activation Time')
    typeDef.AddMember('Second rechargeTime', range=(0, None), text='The recharge time of the module, in seconds. <=0 for instant recharging', caption='Recharge Time')
    typeDef.AddMember('Second duration', range=(0, None), text='Time in seconds this module lasts active for an activation.', caption='Active Duration')
    typeDef.AddMember('Int cycles', range=(0, None), text='Number of cycles in an activation.', caption='Num. of Cycles')
    typeDef.AddMember('Second pulseDuration', range=(0, None), text="Time in seconds that the module stays 'on' during a cycle, must be less than the duration of a cycle (duration / cycles)", caption='Pulse Duration')
    typeDef.AddMember('AttributeModifier activeAttributeModifiers', caption='Active Attribute Modifiers', text='Attribute modifiers applied only when this module is in active states.', attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.IS_SET)
    typeDef.AddMember('TypeReference sideEffects', caption='Module Special Features', allowedClasses='DustMSE', text='Special features (a.k.a. MSEs) the module offers', attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.IS_SET)
    typeDef.AddMember('SimpleSound mSoundEffect', caption='Sound Effect', text='The sound effect for the whole cycle of the module, we use RTPC value to do the transition within wwise')
    typeDef = ax2.CreateType('SlotInfo', standalone=False, group=GROUPS.Logic, forUE3=False, attributeFlag=DEFAULT_ATTRIB_FLAGS | ATTRIB_FLAGS.NOT_NULL)
    typeDef.AddMember('ESlotType slotType', text='The type of this slot', caption='Slot Type')
    typeDef.AddMember('String boneSocketName = none', text='The socket name of this slot in mesh skeleton-bone', caption='Bone Socket Name')
    typeDef.AddMember('TypeReference defaultModuleType = -1', modifyFlag=MODIFY_TYPE_CHANGED, text='The default module for this slot.', caption='Default Module')
    typeDef.AddMember('Bool mandatory = False', text='Set as true to make the mandatory that this slot MUST have a module to fit on it', caption='Mandatory')
    PopulateUniqueModules(ax2)



