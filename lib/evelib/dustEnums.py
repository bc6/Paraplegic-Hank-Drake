from catma.axiom import Enumerate

def PopulateEnums(ax2):
    typeDef = ax2.CreateType('EDustGameObjectiveType', Enumerate)
    typeDef.AddElement('GameObjectiveType_None')
    typeDef.AddElement('GameObjectiveType_Primary')
    typeDef.AddElement('GameObjectiveType_Secondary')
    typeDef = ax2.CreateType('EKillType', Enumerate)
    typeDef.AddElement('KT_Enemy', description='killed by enemy')
    typeDef.AddElement('KT_Team', description='killed by teammate')
    typeDef.AddElement('KT_Suicide', description='suicide')
    typeDef.AddElement('KT_Accident', description='killed by entity which is not controlled by anyone. i.e. by a falling rock')
    typeDef.AddElement('KT_Invalid', description="the entity gets killed is not controlled by anyone, or doesn't belong to any team")



