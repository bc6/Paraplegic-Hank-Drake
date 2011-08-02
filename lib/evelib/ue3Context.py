import sys
import os
import logging
from const import TYPEID_NONE
from catma import stims
from catma import catmaDB
from catma import stimsFactory
from catma import catmaConfig
import time
import gc
import re
from dust import stats
from dust.stats import LogMemoryUsage, GetTotalMemoryUsage
DEBUG = True
ctx = None
import sake.platform
logger = logging.getLogger('DUST.UE3Context')

class UE3Context(object):

    def __init__(self):
        logger.info('===================== Initializing UE3 Context ========================')
        if not gc.isenabled():
            logger.info('python garbage collection is disabled, enable now!')
            gc.enable()
        thresholds = gc.get_threshold()
        logger.info('gc threshold0: %s, threshold1: %s, threshold2: %s' % thresholds)
        gc.set_debug(gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
        LogMemoryUsage('starting')
        self.miniapp = None
        self.StartMini()
        LogMemoryUsage('mini framework started')
        self.sequencer = stims.Sequencer()
        self.compResult = None
        self.sequencer.UpdateTime(time.time())
        LogMemoryUsage('stims started')
        catmaDB.GetDB()
        LogMemoryUsage('CATMA DB loaded')
        self.ParseCmdLineOptions()
        logger.info('=============================================')



    def ParseCmdLineOptions(self):
        logger.info('Parsing cmd line argument: %s' % sys.argv)
        switches = {'-IgnoreInventory': 'ignoreInventory'}
        for (switchName, flagName,) in switches.iteritems():
            value = switchName in sys.argv
            setattr(sys, flagName, value)
            logger.info(' %s = %s' % (flagName, value))




    def ReloadCatmaDB(self, filePath, findModifiedTypes = False, ignoreVersionCheck = False):
        currMemory = GetTotalMemoryUsage()
        if not filePath:
            from sake.app import app
            filePath = app.services.vaultClient.GetFilePath(catmaConfig.GetPickleName())
        logger.info('Reload CATMA data from: %s' % filePath)
        handle = open(filePath, 'rb')
        newCatmaDB = catmaDB.LoadData(handle)
        handle.close()
        currDB = catmaDB.GetDB()
        if ignoreVersionCheck or newCatmaDB._bsdChangeID is None or newCatmaDB._bsdChangeID != currDB._bsdChangeID:
            self.compResult = catmaDB.CatmaComparisonResult(currDB, newCatmaDB) if findModifiedTypes else None
            catmaDB.SetDB(newCatmaDB)
        else:
            newCatmaDB.TearOff()
            del newCatmaDB
        self.GCCollect()
        logger.info('Memory, CATMA DB reloaded: %s Mb increased' % (float(GetTotalMemoryUsage() - currMemory) / 1048576))



    def GetChangedTypeNames(self):
        if self.compResult:
            return self.compResult.GetModifiedTypeNames()



    def CreateAdapter(self, typeName):
        adapter = stimsFactory.CreateAdapter(typeName, catmaDB.GetDB())
        self.sequencer.AddAdapter(adapter)
        return adapter



    def CreateModule(self, typeName):
        module = stimsFactory.CreateModule(typeName, catmaDB.GetDB())
        return module



    def ApplyFitting(self, adapter, moduleList, autoFitting = False):
        moduleList = [ int(typeID) if typeID != str(TYPEID_NONE) else None for typeID in moduleList.split(',') ]
        stimsFactory.ApplyFitting(catmaDB.GetDB(), adapter, moduleList, autoFitting)



    def ApplyDefaultFitting(self, adapter):
        stimsFactory.ApplyDefaultFitting(catmaDB.GetDB(), adapter)



    def GetSlotAttributeValue(self, adapterTypeID, index, attributeName):
        return stimsFactory.GetSlotAttributeValue(adapterTypeID, index, attributeName, catmaDB.GetDB())



    def GetAllSpawnedAdapterModuleType(self, adapterTypeID):
        return stimsFactory.GetAllSpawnedAdapterModuleType(adapterTypeID)



    def ClearModules(self, adapter):
        adapter.ClearModules()



    def StartMini(self):
        import dust.startmini
        import sake.app
        self.miniapp = sake.app.app
        sys.ue3_rpc_timeout = 3600.0



    def TickSequencer(self):
        with stats.MakeUE3ContextTickStimsContext():
            changes = self.sequencer.UpdateTime(time.time())
        with stats.MakeUE3ContextTickMiniContext():
            if self.miniapp and self.miniapp.running:
                self.miniapp.Pump()
        return changes



    def PreLevelReset(self):
        logger.info('PreLevelReset called in ue3Context')
        self.sequencer.FlushAll()
        gc.collect()



    def GetNumAdapters(self):
        numAdapter = 0
        if self.sequencer:
            numAdapter = len(self.sequencer.adapters)
        return numAdapter



    def _pythonExec(self, code):
        try:
            exec code
        except Exception as e:
            import traceback
            traceback.print_exc(e)



    def Exec(self, command):
        if command.startswith('>'):
            pythonCode = command[1:]
            from sake.app import app
            app.process.New(self._pythonExec, pythonCode)
        command = command.lower()
        if command == 'collect':
            self.GCCollect()
        elif command == 'garbagelist':
            logger.info('============= begin garbage list, numn = %s =============' % len(gc.garbage))
            for obj in gc.garbage:
                logger.info(str(obj))

            logger.info('============= end garbage list =============')
        elif command == 'gcinfo':
            logger.info('python gc enabled' if gc.isenabled() else 'disabled')
            logger.info('num of tracked objects: %s' % len(gc.get_objects()))
            logger.info('num of garbage objects: %s' % len(gc.garbage))
        elif command == 'listcatmadb':
            numInstance = 0
            for obj in gc.get_objects():
                if isinstance(obj, catmaDB.CatmaDB):
                    numInstance += 1
                    logger.info('found CATMA DB instance: %s' % obj)

            logger.info('total number of CATMA DB instance: ', numInstance)
        else:
            if command.startswith('dir'):
                nameFilter = command.split(' ', 1)[1:]
                cdb = catmaDB.GetDB()
                typeNames = cdb.GetAllTypeNames()
                if nameFilter:
                    if nameFilter[0] == '-h':
                        return 'Usage: dir [regex filter]\nLists out catma type names that match the filter'
                    typeNames = [ i for i in typeNames if re.search(nameFilter[0], i.lower()) ]
                typeNames.sort()
                ret = '%s types found:\n' % len(typeNames)
                ret += '\n'.join(typeNames)
                return ret
            else:
                return '$unhandled$'



    def GCCollect(self):
        numUnreachable = gc.collect()
        logger.info('num unreachable objects: %s' % numUnreachable)




def InitContext():
    global ctx
    if ctx is None:
        ctx = UE3Context()



