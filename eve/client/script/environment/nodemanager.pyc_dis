#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/nodemanager.py
import blue
import trinity
import timecurves
import random
import log
import sys

def FindNodes(source, name, typename):
    nodes = []
    if source.__typename__ == 'List':
        thingsToSearch = source
    else:
        thingsToSearch = [source]
    for item in thingsToSearch:
        tr = item.Find(typename)
        matches = [ t for t in tr if t.name.startswith(name) ]
        nodes.extend(matches)

    return nodes


def FindNode(source, name, typename):
    tr = source.Find(typename)
    for t in tr:
        if t.name.startswith(name):
            return t


def FindTransform(source, name):
    return FindNode(source, name, 'trinity.TriTransform')


def SmoothExit(transform, source, duration = 1.0):
    moverModel = blue.resMan.LoadObject('res:/Model/Global/SmoothMover.blue')
    mover = FindNode(moverModel, 'mover', 'trinity.TriStretch')
    container = FindNode(moverModel, 'container', 'trinity.TriStretch')
    mover.source = source
    del container.children[:]
    timecurves.SetDuration(moverModel, duration)
    timecurves.ResetTimeCurves(moverModel)
    models = moverModel.Find('trinity.TriTransform')
    for model in models:
        if model.object != None:
            model.display = 0

    container.children.append(transform)
    return moverModel


def SmoothEntry(transform, duration = 1.0):
    moverModel = blue.resMan.LoadObject('res:/Model/Global/SmoothMoveOrient.blue')
    tfs = moverModel.Find('trinity.TriTransform')
    for t in tfs:
        if t.object:
            t.object.display = 0

    container = FindNode(moverModel, 'upPointer', 'trinity.TriStretch')
    del container.children[:]
    timecurves.SetDuration(moverModel, duration)
    container.children.append(transform)
    return moverModel


def RigEntry(entryGuy, target):
    mover = FindNode(entryGuy, 'mover', 'trinity.TriStretch')
    destUpContainer = FindNode(entryGuy, 'destUpContainer', 'trinity.TriStretch')
    mover.source = target
    destUpContainer.source = target
    destUpContainer.dest = target
    timecurves.ReverseTimeCurves(mover)
    timecurves.ResetTimeCurves(mover)
    timecurves.ReverseTimeCurves(destUpContainer)
    timecurves.ResetTimeCurves(destUpContainer)
    blue.pyos.synchro.SleepSim(int(timecurves.MaxLen(mover) * 1000))


def UnRigEntry(entryGuy):
    mover = FindNode(entryGuy, 'mover', 'trinity.TriStretch')
    destUpContainer = FindNode(entryGuy, 'destUpContainer', 'trinity.TriStretch')
    timecurves.ReverseTimeCurves(mover)
    timecurves.ResetTimeCurves(mover)
    timecurves.ReverseTimeCurves(destUpContainer)
    timecurves.ResetTimeCurves(destUpContainer)
    blue.pyos.synchro.SleepSim(int(timecurves.MaxLen(mover) * 1000))
    mover.source = trinity.TriSplTransform()
    destUpContainer.source = mover.source
    destUpContainer.dest = mover.source
    mover.source.name = 'nothing'


def SetVertexTarget(target, thingToKeepClose = None):
    if target.__typename__ == 'TriLODGroup':
        if not hasattr(target.children[0], 'object'):
            return [[], target]
        if target.children[0].object == None:
            depth = 2
            targetobject = None
            for child in target.children[0].children:
                if child.display == 0 or targetobject is not None:
                    continue
                if child.__typename__ == 'TriTransform':
                    if child.object is not None:
                        if child.object.__typename__ == 'TriModel':
                            if child.object.display == 1:
                                targetobject = child
                                break

            if targetobject == None:
                for c in target.children[0].children:
                    if hasattr(c, 'children'):
                        for child in c.children:
                            if child.__typename__ == 'TriTransform':
                                if child.object is not None:
                                    if child.object.__typename__ == 'TriModel':
                                        if child.object.display == 1:
                                            targetobject = child
                                            break

        else:
            depth = 1
            targetobject = target.children[0]
    else:
        depth = 0
        targetobject = target
    if targetobject.object == None:
        targetobject = None
    if targetobject == None:
        log.general.Log('Nodemanager: targetobject is None')
        return [[], target]
    vx = targetobject.object.vertexRes.vertexBuffer
    if vx == None:
        log.general.Log('vx is None')
        return [[], target]
    vx.LockBuffer()
    potentialLocators = []
    if thingToKeepClose:
        counter = 40
    else:
        counter = 1
    for v in range(counter):
        owners = []
        i = random.randint(1, vx.vertexCount) - 1
        t = vx.GetVertexElementData(i, trinity.TRIVSDE_POSITION)
        pos = trinity.TriVector(t[0], t[1], t[2])
        tfpos = pos.CopyTo()
        tfpos.TransformCoord(targetobject.worldTransform)
        if thingToKeepClose:
            thingToKeepClosePos = trinity.TriVector()
            thingToKeepClosePos.TransformCoord(thingToKeepClose.worldTransform)
            distanceV = tfpos - thingToKeepClosePos
            distance = distanceV.Length()
        else:
            distance = 0.0
        distanceTuple = [distance, i]
        potentialLocators.append(distanceTuple)

    potentialLocators.sort()
    closestTuple = potentialLocators[0]
    i = closestTuple[1]
    t = vx.GetVertexElementData(i, trinity.TRIVSDE_POSITION)
    pos = trinity.TriVector(t[0], t[1], t[2])
    n = vx.GetVertexElementData(i, trinity.TRIVSDE_NORMAL)
    normal = trinity.TriVector(n[0], n[1], n[2])
    vxTarget = blue.classes.CreateInstance('trinity.TriSplTransform')
    vxTarget.scaling.Scale(0.2)
    vxTarget.translation = pos.CopyTo()
    vxNormal = normal
    fwd = trinity.TriVector(0.0, 0.0, 1.0)
    vxTarget.rotation.SetRotationArc(fwd, vxNormal)
    vxTarget.name = 'vertexTarget of ' + target.name
    if target.__typename__ == 'TriLODGroup':
        for child in target.children:
            if depth == 1:
                if vxTarget not in child.children:
                    child.children.append(vxTarget)
                    owners.append(child)
            elif len(child.children) > 0:
                if vxTarget not in child.children[0].children:
                    child.children[0].children.append(vxTarget)
                owners.append(child.children[0])
            elif vxTarget not in child.children:
                child.children.append(vxTarget)
                owners.append(child)

    else:
        target.children.append(vxTarget)
        owners.append(target)
    log.general.Log('done setting vertexobject')
    return [owners, vxTarget]


def SetVertexTargetNoNormal(target, thingToKeepClose = None):
    turrStart = blue.os.GetWallclockTimeNow()
    if target.__typename__ == 'TriLODGroup':
        if not hasattr(target.children[0], 'object'):
            log.general.Log('the target has no object attr')
            return [[], target]
        if target.children[0].object == None:
            targetobject = None
            for child in target.children[0].children:
                if targetobject is not None:
                    continue
                if child.__typename__ == 'TriTransform' and child.display == 1:
                    if child.object is not None:
                        if child.object.__typename__ == 'TriModel':
                            if child.object.vertices != 'res:/Model/Global/locatorObject.tri':
                                if child.object.display == 1:
                                    depth = 2
                                    targetobject = child
                                    break

            if targetobject == None:
                for child in target.children[0].children:
                    if targetobject is not None:
                        continue
                    if hasattr(child, 'children') and child.display == 1:
                        for child in child.children:
                            if child.__typename__ == 'TriTransform':
                                if child.object is not None:
                                    if child.object.__typename__ == 'TriModel':
                                        if child.object.vertices != 'res:/Model/Global/locatorObject.tri':
                                            if child.object.display == 1:
                                                targetobject = child
                                                depth = 3
                                                break

        else:
            depth = 1
            targetobject = target.children[0]
            log.general.Log('set depth 1')
    else:
        depth = 0
        log.general.Log('set depth 0')
        targetobject = target
    if not hasattr(targetobject, 'object'):
        log.general.Log('targetobject has to object attribute')
        return [[], target]
    if targetobject.object == None:
        targetobject = None
    if targetobject == None:
        log.general.Log('Nodemanager: targetobject is None')
        return [[], target]
    if thingToKeepClose:
        potentialLocators = []
        thingToKeepClosePos = trinity.TriVector()
        thingToKeepClosePos.TransformCoord(thingToKeepClose.worldTransform)
        for v in range(40):
            pos = targetobject.RandomSurfacePoint()
            if not pos:
                return [[], target]
            tfpos = pos.CopyTo()
            tfpos.TransformCoord(targetobject.worldTransform)
            dv = tfpos - thingToKeepClosePos
            d = dv.LengthSq()
            potentialLocators.append((d, pos))

        potentialLocators.sort()
        pos = potentialLocators[0][1]
    else:
        pos = targetobject.RandomSurfacePoint()
        if not pos:
            return [[], target]
    vxTarget = blue.classes.CreateInstance('trinity.TriSplTransform')
    vxTarget.scaling.Scale(0.2)
    vxTarget.translation = pos.CopyTo()
    vxTarget.name = 'vertexTarget of ' + target.name
    owners = []
    if target.__typename__ == 'TriLODGroup':
        for child in target.children:
            if depth == 1:
                if vxTarget not in child.children:
                    child.children.append(vxTarget)
                    log.general.Log('--->adding d1 vertexobject to %s ' % child.name)
                    owners.append(child)
            elif len(child.children) > 0:
                for grandchild in child.children:
                    if hasattr(grandchild, 'display'):
                        if grandchild.display == 0:
                            continue
                    if hasattr(grandchild, 'children'):
                        break

                if vxTarget not in grandchild.children:
                    grandchild.children.append(vxTarget)
                    log.general.Log('--->adding lne> 0 vertexobject to %s ' % grandchild.name)
                    owners.append(grandchild)
            elif vxTarget not in child.children:
                child.children.append(vxTarget)
                owners.append(child)
                log.general.Log('--->adding len = 0 vertexobject to %s ' % child.name)

    else:
        target.children.append(vxTarget)
        owners.append(target)
    turrEnd = blue.os.GetWallclockTimeNow()
    log.general.Log('--->vertexobject set in  %f ms' % blue.os.TimeDiffInMs(turrStart, turrEnd))
    return [owners, vxTarget]


def SetVertexTargetNoNormal2(targetOwner, thingToKeepClose = None):
    target = targetOwner.model
    turrStart = blue.os.GetWallclockTimeNow()
    if target.__typename__ == 'TriLODGroup':
        if not hasattr(target.children[0], 'object'):
            log.general.Log('the target has no object attr')
            return [[], target]
        if target.children[0].object == None:
            targetobject = None
            targetTransforms = []
            for child in target.children[0].children:
                if targetobject is not None:
                    continue
                if child.__typename__ == 'TriTransform' and child.display == 1:
                    if child.object is not None:
                        if child.object.__typename__ == 'TriModel':
                            if child.object.vertices != 'res:/Model/Global/locatorObject.tri':
                                if child.object.display == 1:
                                    depth = 2
                                    targetobject = child
                                    targetTransforms = [target.children[0], child]
                                    break

            if targetobject == None:
                for child in target.children[0].children:
                    if targetobject is not None:
                        continue
                    if hasattr(child, 'children') and child.display == 1:
                        for child2 in child.children:
                            if child2.__typename__ == 'TriTransform':
                                if child2.object is not None:
                                    if child2.object.__typename__ == 'TriModel':
                                        if child2.object.vertices != 'res:/Model/Global/locatorObject.tri':
                                            if child2.object.display == 1:
                                                targetobject = child2
                                                targetTransforms = [target.children[0], child, child2]
                                                depth = 3
                                                break

        else:
            depth = 1
            targetobject = target.children[0]
            targetTransforms = [target.children[0]]
            log.general.Log('set depth 1')
    else:
        depth = 0
        targetTransforms = [target]
        log.general.Log('set depth 0')
        targetobject = target
    if not hasattr(targetobject, 'object'):
        log.general.Log('targetobject has to object attribute')
        return [[], target]
    if targetobject.object == None:
        targetobject = None
    if targetobject == None:
        log.general.Log('Nodemanager: targetobject is None')
        return [[], target]
    generatedLocators = []
    thingToKeepClosePos = trinity.TriVector()
    thingToKeepClosePos.TransformCoord(thingToKeepClose.worldTransform)
    transformCopyList = []
    for transformDepthIndex in range(len(targetTransforms)):
        transformCopy = blue.classes.CreateInstance('trinity.TriTransform')
        if hasattr(targetTransforms[transformDepthIndex], 'scalingCurve') and targetTransforms[transformDepthIndex].scalingCurve is not None:
            transformCopy.scalingCurve = targetTransforms[transformDepthIndex].scalingCurve.CopyTo()
        if hasattr(targetTransforms[transformDepthIndex], 'rotationCurve') and targetTransforms[transformDepthIndex].rotationCurve is not None:
            transformCopy.rotationCurve = targetTransforms[transformDepthIndex].rotationCurve.CopyTo()
        if hasattr(targetTransforms[transformDepthIndex], 'translationCurve') and targetTransforms[transformDepthIndex].translationCurve is not None:
            transformCopy.translationCurve = targetTransforms[transformDepthIndex].translationCurve.CopyTo()
        transformCopy.scaling = targetTransforms[transformDepthIndex].scaling.CopyTo()
        transformCopy.rotation = targetTransforms[transformDepthIndex].rotation.CopyTo()
        transformCopy.translation = targetTransforms[transformDepthIndex].translation.CopyTo()
        transformCopyList.append(transformCopy)
        if transformDepthIndex > 0:
            transformCopyList[transformDepthIndex - 1].children.append(transformCopy)

    for v in range(40):
        pos = targetobject.RandomSurfacePoint()
        if not pos:
            return [[], target]
        newDamageLocator = blue.classes.CreateInstance('trinity.TriSplTransform')
        newDamageLocator.scaling.Scale(0.2)
        newDamageLocator.name = 'locator_damage_generated' + str(v)
        newDamageLocator.translation = pos.CopyTo()
        targetobject.children.append(newDamageLocator)
        transformCopyList[-1].children.append(newDamageLocator)
        generatedLocators.append(newDamageLocator)

    for lodGroup in target.children[1:]:
        lodGroup.children.append(transformCopyList[0])

    targetOwner.targets = generatedLocators
    turrEnd = blue.os.GetWallclockTimeNow()
    log.general.Log('Damage Locator targets generated in %f ms' % blue.os.TimeDiffInMs(turrStart, turrEnd), log.LGWARN)


def RemoveVertexTarget(ownerTargetList):
    try:
        owners = ownerTargetList[0]
        vxTarget = ownerTargetList[1]
        for owner in owners:
            owner.children.remove(vxTarget)

    except:
        sys.exc_clear()
        sm.GetService('FxSequencer').LogError('Fuxor while removing vxTarget. Talk to Nonni')


def DoDummyEffect(model):
    ball = blue.resMan.LoadObject('res:/Model/Effect/placeholder.blue')
    model.children.append(ball)
    timecurves.ResetTimeCurves(ball)
    blue.pyos.synchro.SleepSim(int(timecurves.MaxLen(ball) * 1000))
    model.children.remove(ball)


exports = {'nodemanager.FindNodes': FindNodes,
 'nodemanager.FindTransform': FindTransform,
 'nodemanager.FindNode': FindNode,
 'nodemanager.SmoothExit': SmoothExit,
 'nodemanager.SmoothEntry': SmoothEntry,
 'nodemanager.RigEntry': RigEntry,
 'nodemanager.UnRigEntry': UnRigEntry,
 'nodemanager.SetVertexTarget': SetVertexTarget,
 'nodemanager.RemoveVertexTarget': RemoveVertexTarget,
 'nodemanager.SetVertexTargetNoNormal': SetVertexTargetNoNormal,
 'nodemanager.SetVertexTargetNoNormal2': SetVertexTargetNoNormal2,
 'nodemanager.DoDummyEffect': DoDummyEffect}