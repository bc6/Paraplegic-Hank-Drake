#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\GameWorld\aidefinitionhelpers.py
import blue
import log

def AddAperiodic(aiDef, name, priority, TPF, maxCalls):
    fld = aiDef.GetFolder('Aperiodic', name)
    fld.SetAttribute('Priority', str(priority))
    fld.SetAttribute('Tpf', str(TPF))
    fld.SetAttribute('MaxCall', str(maxCalls))


def AddPeriodic(aiDef, name, freq):
    fld = aiDef.MakeFolder('Periodic', name)
    fld.SetAttribute('Period', str(freq))


def AddEntity(aiDef, name, className, actionClass, brain, profile = 'Human'):
    fld = aiDef.GetFolder('Entity', name)
    fld.SetAttribute('Class', className)
    if actionClass != '':
        fld.SetAttribute('ActionClass', actionClass)
    if brain != '':
        fld.SetAttribute('Brain', brain)
    if profile != '':
        fld.SetAttribute('Profile', profile)


def AddBrain(aiDef, name, className, serviceList, agents):
    fld = aiDef.AddBrain(className, name)
    for each in serviceList:
        fld.SetAttribute('Service', each)

    for each in agents:
        fld.SetAttribute('Agent', each)

    return fld


def AddModifier(svc, typeName, name, className, defModifier):
    fld = svc.GetFolder('Modifiers_%s' % typeName, '')
    fld.SetAttribute('Default', defModifier)
    fld2 = fld.GetFolder(typeName, name)
    fld2.SetAttribute('Class', className)
    return (fld, fld2)


def AddDatabase(fld, pathDBName, pathDBFilePath, concreteSlotsCount = None, maxGraphHandles = 500):
    dbFld = fld.GetFolder('Database', pathDBName)
    dbFld.SetAttribute('HandleAIMeshes', 'True')
    if concreteSlotsCount is not None:
        dbFld.SetAttribute('ConcreteSlotsCount', str(concreteSlotsCount))
    dbFld.SetAttribute('MaxGraphHandles', str(maxGraphHandles))
    dbFld.SetAttribute('Path', pathDBFilePath)


def DefineGraphDatabase(aiDef, pathDBName, pathDBFilePath, concreateSlotsCount = None, maxGraphHandles = 500):
    svc = aiDef.AddService('Fpd::CGraphManager', 'GraphManager', True)
    return svc


def DefinePathFinder(aiDef, dbName, layers):
    svc = aiDef.AddService('Fpd::CPathFinder', 'Path_finder', False)
    svc.SetAttribute('Database', dbName)
    AddModifier(svc, 'ICanGo', 'CCanGo_AiMesh', 'Fpd::CCanGo_AiMesh', 'CCanGo_AiMesh')
    AddModifier(svc, 'IDetectGoalReached', 'DetectGoalReached_Distance2D5', 'Fpd::CDetectGoalReached_Distance2D5', 'DetectGoalReached_Distance2D5')
    AddModifier(svc, 'IGoto', 'Goto_GapDynamicAvoidance', 'Fpd::CGoto_GapDynamicAvoidance', 'Goto_GapDynamicAvoidance')
    AddModifier(svc, 'IRefineGoal', 'CRefineGoal_OutsideAiMesh', 'Fpd::CRefineGoal_OutsideAiMesh', 'CRefineGoal_OutsideAiMesh')
    AddModifier(svc, 'ISelectPathNodeCandidate', 'CSelectPathNodeCandidate_NextPathNode', 'Fpd::CSelectPathNodeCandidate_NextPathNode', 'CSelectPathNodeCandidate_NextPathNode')
    AddModifier(svc, 'IFindNodesFromPositions', 'CFindNodesFromPositions_NearestReachable', 'Fpd::CFindNodesFromPositions_NearestReachable', 'CFindNodesFromPositions_NearestReachable')
    AddModifier(svc, 'IComputeTargetPoint', 'CComputeTargetPoint_ShortCut', 'Fpd::CComputeTargetPoint_ShortCut', 'CComputeTargetPoint_ShortCut')
    AddModifier(svc, 'ISteering', 'CSteering_SimpleBiped', 'Fpd::CSteering_SimpleBiped', 'CSteering_SimpleBiped')
    AddModifier(svc, 'ISteering', 'BipedSteeringModifier', 'BipedSteeringModifier', 'BipedSteeringModifier')


def DefineWanderTraversal(svc):
    fld = svc.GetFolder('Traversal', 'WanderTraversal')
    fld.SetAttribute('Class', 'Fpd::CWanderTraversal')
    fld.SetAttribute('InstanceCount', '1')
    fld.SetAttribute('AperiodicTask', 'Fpd::CWanderAgent::FindPoint')
    fld.SetAttribute('WanderDistance', '15')
    fld.SetAttribute('WanderPropagationAngle', '100')


def DefineFleeTraversal(svc):
    fld = svc.GetFolder('Traversal', 'FleeingTraversal')
    fld.SetAttribute('Class', 'Fpd::CFleeingTraversal')
    fld.SetAttribute('InstanceCount', '1')
    fld.SetAttribute('AperiodicTask', 'AStarTraversalTask')


def DefineMeshLayerManager(aiDef, dbName, layers, maxMeshCount = 500, maxObstacles = 1000, maxProjections = 4000):
    if layers == []:
        return
    svc = aiDef.AddService('CAiMeshLayerManager', 'MeshLayerManager', True)
    for each in layers:
        lyr = svc.GetFolder('Layer', each)
        lyr.SetAttribute('Class', 'CObstaclesLayer')
        lyr.SetAttribute('MaxMeshCount', str(maxMeshCount))
        lyr.SetAttribute('MaxObstacles', str(maxObstacles))
        lyr.SetAttribute('MaxProjections', str(maxProjections))
        aiAcc = lyr.GetFolder('AiMeshAccessor', '')
        aiAcc.SetAttribute('Class', 'Fpd::CAdditionalAiMeshAccessor')
        aiAcc.SetAttribute('Database', dbName)
        obAcc = lyr.GetFolder('ObstaclesAccessor', '')
        obAcc.SetAttribute('Class', 'CObstaclesAccessor_EntityOutline')


def AddStep(bldSvc, className, stepName):
    step = bldSvc.GetFolder('Step', stepName)
    step.SetAttribute('Class', className)
    return step


def AddSeedPoint(seedPoints, point):
    seed = seedPoints.MakeFolder('SeedPoint', '')
    seed.SetAttribute('Right', str(-point.x))
    seed.SetAttribute('Up', str(point.y))
    seed.SetAttribute('Front', str(point.z))


def AddGlobalBounds(fld, worldBounds):
    bb = fld.GetFolder('GlobalBoundingBox', '')
    bb.SetAttribute('RightMin', str(-worldBounds[1][0]))
    bb.SetAttribute('RightMax', str(-worldBounds[0][0]))
    bb.SetAttribute('UpMin', str(worldBounds[0][1]))
    bb.SetAttribute('UpMax', str(worldBounds[1][1]))
    bb.SetAttribute('FrontMin', str(worldBounds[0][2]))
    bb.SetAttribute('FrontMax', str(worldBounds[1][2]))


def DefinePortalBuildStep(bldSvc, sectorsPath, portalFile, portalPositions):
    graphDir = sectorsPath + 'SeedGraphs'
    step = AddStep(bldSvc, 'SeedGraphMakerStepForPortals', 'PathObjectMakerForPortals')
    step.SetAttribute('GraphDirectory', str(graphDir))
    step.SetAttribute('ImportPathObjectFile', sectorsPath + 'portals.xml')
    currentID = 1
    for position in portalPositions:
        currentPathObject = portalFile.SetAttribute('PathObject', '')
        currentPathObject.SetTypeInfo('Name', 'PortalPathObject')
        currentPathObject.SetTypeInfo('posX', str(-position[0]))
        currentPathObject.SetTypeInfo('posY', str(position[1]))
        currentPathObject.SetTypeInfo('posZ', str(position[2]))
        currentPathObject.SetTypeInfo('yaw', str(-position[3]))
        currentPathObject.SetTypeInfo('UID', str(currentID))
        currentPathObject.SetTypeInfo('Width', str(3))
        currentPathObject.SetTypeInfo('Length', str(1))
        currentID += 1

    portalFile.Dump(str(sectorsPath + 'portals.xml'))
    coordinateSystem = step.GetFolder('CoordinateSystem', '')
    coordinateSystem.SetAttribute('Right', 'X')
    coordinateSystem.SetAttribute('Up', 'Y')
    coordinateSystem.SetAttribute('Front', 'Z')


def DefineSharedBuildData(bldSvc, sectorsPath, databasePath, worldBounds, seedPoints, entityRadius, entityHeight, distEdgeMax, stepHeight):
    shared = bldSvc.GetFolder('Shared', '')
    shared.SetAttribute('SectorsDefinitionFile', sectorsPath + 'sectors.xml')
    shared.SetAttribute('SectorsOutputDirectory', sectorsPath + 'sectors')
    shared.SetAttribute('FpdOutputDirectory', databasePath)
    AddGlobalBounds(shared, worldBounds)
    fld = shared.GetFolder('MapBuilder', '')
    fld.SetAttribute('Class', 'CMapBuilder')
    fld.SetAttribute('OutputGraphType', 'fsg')
    fld.SetAttribute('GraphAccuracy', '2')
    fld.SetAttribute('CollisionModel', 'SweptSphere')
    fld.SetAttribute('EntityRadius', str(entityRadius))
    fld.SetAttribute('EntityHeight', str(entityHeight))
    fld.SetAttribute('DistEdgeMax', str(distEdgeMax))
    fld.SetAttribute('StepMax', str(stepHeight))
    fld.SetAttribute('Pitch', '0.2')
    seedPointsFolder = shared.GetFolder('SeedPoints', '')
    for each in seedPoints:
        AddSeedPoint(seedPointsFolder, each)