import uthread
import service
import blue
import sys
import log
import os
import trinity
import const
import form

class EveShip2BuildEvent:

    def __init__(self):
        self.isDone = False
        self.succeeded = False



    def __call__(self, success):
        self.isDone = True
        self.succeeded = success



    def Wait(self):
        while not self.isDone:
            blue.pyos.synchro.Yield()





class t3ShipSvc(service.Service):
    __guid__ = 'svc.t3ShipSvc'
    __displayname__ = 'Tech 3 Ship Builder'
    __exportedcalls__ = {'GetTech3ShipFromDict': []}

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING



    def GetTech3ShipFromDict(self, shipTypeID, subSystems, itemID = None):
        t = subSystems.values()
        t.sort()
        uniqueComboID = '_'.join([ str(id) for id in t ])
        redFileCachePath = 'cache:/ships/%s_%s.red' % (shipTypeID, uniqueComboID)
        gr2FileCachePath = 'cache:/ships/%s_%s.gr2' % (shipTypeID, uniqueComboID)
        redFilePath = blue.rot.PathToFilename(redFileCachePath)
        gr2FilePath = blue.rot.PathToFilename(gr2FileCachePath)
        if os.path.exists(redFilePath) and os.path.exists(gr2FilePath):
            self.LogInfo('Loading existing modular ship from', redFileCachePath)
            model = trinity.LoadUrgent(redFileCachePath)
            trinity.WaitForUrgentResourceLoads()
            if itemID:
                sm.ScatterEvent('OnModularShipReady', itemID, redFileCachePath)
            return model
        try:
            self.LogInfo('Starting to build modular ship at', redFileCachePath)
            builder = trinity.EveShip2Builder()
            builder.weldThreshold = 0.01
            builder.electronic = cfg.invtypes.Get(subSystems[const.groupElectronicSubSystems]).GraphicFile()
            builder.defensive = cfg.invtypes.Get(subSystems[const.groupDefensiveSubSystems]).GraphicFile()
            builder.engineering = cfg.invtypes.Get(subSystems[const.groupEngineeringSubSystems]).GraphicFile()
            builder.offensive = cfg.invtypes.Get(subSystems[const.groupOffensiveSubSystems]).GraphicFile()
            builder.propulsion = cfg.invtypes.Get(subSystems[const.groupPropulsionSubSystems]).GraphicFile()
            builder.highDetailOutputName = 'cache:/ships/%s_%s.gr2' % (shipTypeID, uniqueComboID)
            doneChannel = uthread.Channel()
            uthread.new(self.BuildShip, builder, redFilePath, doneChannel)
            doneChannel.receive()
            self.LogInfo('Done building modular ship at', redFileCachePath)
            model = trinity.LoadUrgent(redFileCachePath)
            trinity.WaitForUrgentResourceLoads()
            if itemID:
                sm.ScatterEvent('OnModularShipReady', itemID, redFileCachePath)
            return model
        except (Exception,) as e:
            self.LogError('Error building modular ship')
            log.LogException()
            sys.exc_clear()
            raise e



    def SaveModelToCache(self, model, filePath):
        shipsDir = blue.rot.PathToFilename('cache:/ships/')
        if not os.path.exists(shipsDir):
            os.makedirs(blue.rot.PathToFilename('cache:/ships/'))
        trinity.Save(model, filePath)



    def BuildShip(self, builder, path, doneChannel):
        shipsDir = blue.rot.PathToFilename('cache:/ships/')
        if not os.path.exists(shipsDir):
            os.makedirs(blue.rot.PathToFilename('cache:/ships/'))
        if builder.PrepareForBuild():
            trinity.WaitForResourceLoads()
            evt = EveShip2BuildEvent()
            builder.BuildAsync(evt)
            evt.Wait()
            if evt.succeeded:
                log.LogInfo('Modular model built successfully:', path)
                ship = builder.GetShip()
                ship.shadowEffect = trinity.Tr2Effect()
                ship.shadowEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/Ship/Shadow.fx'
                self.SaveModelToCache(ship, path)
                doneChannel.send(True)
                return 
            log.LogError('Failed building ship:', path)
        doneChannel.send(False)



    def MakeModularShipFromShipItem(self, ship):
        subSystemIds = {}
        for fittedItem in ship.GetFittedItems().itervalues():
            if fittedItem.categoryID == const.categorySubSystem:
                subSystemIds[fittedItem.groupID] = fittedItem.typeID

        if len(subSystemIds) < const.visibleSubSystems:
            windowID = 'assembleWindow_modular'
            form.AssembleShip.CloseIfOpen(windowID=windowID)
            form.AssembleShip.Open(windowID=windowID, ship=ship, groupIDs=subSystemIds.keys())
            return 
        return self.GetTech3ShipFromDict(ship.typeID, subSystemIds)




