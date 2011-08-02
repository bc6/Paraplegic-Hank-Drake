import cef

class CollisionMeshComponentView(cef.BaseComponentView):
    __guid__ = 'cef.CollisionMeshComponentView'
    __COMPONENT_ID__ = const.cef.COLLISION_MESH_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'CollisionMesh'
    __COMPONENT_CODE_NAME__ = 'collisionMesh'
    GRAPHIC_ID = 'graphicID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GRAPHIC_ID, -1, cls.OPTIONAL, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Graphic ID')



CollisionMeshComponentView.SetupInputs()

