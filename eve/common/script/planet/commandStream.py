import util
COMMAND_CREATEPIN = 1
COMMAND_REMOVEPIN = 2
COMMAND_CREATELINK = 3
COMMAND_REMOVELINK = 4
COMMAND_SETLINKLEVEL = 5
COMMAND_CREATEROUTE = 6
COMMAND_REMOVEROUTE = 7
COMMAND_SETSCHEMATIC = 8
COMMAND_UPGRADECOMMANDCENTER = 9
COMMAND_ADDEXTRACTORHEAD = 10
COMMAND_KILLEXTRACTORHEAD = 11
COMMAND_MOVEEXTRACTORHEAD = 12
COMMAND_INSTALLPROGRAM = 13

class CommandStream():
    __guid__ = 'planet.CommandStream'
    __name__ = 'CommandStream'
    __commands__ = {COMMAND_CREATEPIN: 'CreatePin',
     COMMAND_REMOVEPIN: 'RemovePin',
     COMMAND_CREATELINK: 'CreateLink',
     COMMAND_REMOVELINK: 'RemoveLink',
     COMMAND_SETLINKLEVEL: 'SetLinkLevel',
     COMMAND_CREATEROUTE: 'CreateRoute',
     COMMAND_REMOVEROUTE: 'RemoveRoute',
     COMMAND_SETSCHEMATIC: 'SetSchematic',
     COMMAND_UPGRADECOMMANDCENTER: 'UpgradeCommandCenter',
     COMMAND_ADDEXTRACTORHEAD: 'AddExtractorHead',
     COMMAND_KILLEXTRACTORHEAD: 'KillExtractorHead',
     COMMAND_MOVEEXTRACTORHEAD: 'MoveExtractorHead',
     COMMAND_INSTALLPROGRAM: 'InstallProgram'}
    __antonyms__ = {COMMAND_REMOVEPIN: [COMMAND_CREATEPIN],
     COMMAND_REMOVELINK: [COMMAND_CREATELINK],
     COMMAND_REMOVEROUTE: [COMMAND_CREATEROUTE],
     COMMAND_KILLEXTRACTORHEAD: [COMMAND_ADDEXTRACTORHEAD],
     COMMAND_ADDEXTRACTORHEAD: [COMMAND_KILLEXTRACTORHEAD]}
    __heteronyms__ = {COMMAND_REMOVEPIN: [COMMAND_SETSCHEMATIC,
                         COMMAND_UPGRADECOMMANDCENTER,
                         COMMAND_ADDEXTRACTORHEAD,
                         COMMAND_KILLEXTRACTORHEAD,
                         COMMAND_MOVEEXTRACTORHEAD,
                         COMMAND_INSTALLPROGRAM],
     COMMAND_REMOVELINK: [COMMAND_SETLINKLEVEL],
     COMMAND_KILLEXTRACTORHEAD: [COMMAND_MOVEEXTRACTORHEAD]}
    __identifiers__ = {COMMAND_CREATEPIN: ['pinID'],
     COMMAND_REMOVEPIN: ['pinID'],
     COMMAND_CREATELINK: ['endpoint1', 'endpoint2'],
     COMMAND_REMOVELINK: ['endpoint1', 'endpoint2'],
     COMMAND_SETLINKLEVEL: ['endpoint1', 'endpoint2'],
     COMMAND_CREATEROUTE: ['routeID'],
     COMMAND_REMOVEROUTE: ['routeID'],
     COMMAND_SETSCHEMATIC: ['pinID'],
     COMMAND_UPGRADECOMMANDCENTER: ['pinID'],
     COMMAND_ADDEXTRACTORHEAD: ['pinID', 'headID'],
     COMMAND_KILLEXTRACTORHEAD: ['pinID', 'headID'],
     COMMAND_MOVEEXTRACTORHEAD: ['pinID', 'headID'],
     COMMAND_INSTALLPROGRAM: ['pinID']}
    __arguments__ = {COMMAND_CREATEPIN: ['typeID', 'latitude', 'longitude'],
     COMMAND_REMOVEPIN: [],
     COMMAND_CREATELINK: ['level'],
     COMMAND_REMOVELINK: [],
     COMMAND_SETLINKLEVEL: ['level'],
     COMMAND_CREATEROUTE: ['path', 'typeID', 'quantity'],
     COMMAND_REMOVEROUTE: [],
     COMMAND_SETSCHEMATIC: ['schematicID'],
     COMMAND_UPGRADECOMMANDCENTER: ['level'],
     COMMAND_ADDEXTRACTORHEAD: ['latitude', 'longitude'],
     COMMAND_KILLEXTRACTORHEAD: [],
     COMMAND_MOVEEXTRACTORHEAD: ['latitude', 'longitude'],
     COMMAND_INSTALLPROGRAM: ['typeID', 'headRadius']}

    def __init__(self):
        self.stream = []
        self.history = []



    def _IsIdentifierMatch(self, command1, command2):
        for identifier in self.__identifiers__[command1.id]:
            if not hasattr(command2, identifier):
                return False
            if getattr(command2, identifier) != getattr(command1, identifier):
                return False

        return True



    def _IsAntonymMatch(self, command1, command2):
        if not self._IsIdentifierMatch(command1, command2):
            return False
        else:
            if command1.id not in self.__antonyms__:
                return False
            return command2.id in self.__antonyms__[command1.id]



    def _IsHeteronymMatch(self, command1, command2):
        if not self._IsIdentifierMatch(command1, command2):
            return False
        else:
            if command1.id not in self.__heteronyms__:
                return False
            return command2.id in self.__heteronyms__[command1.id]



    def _HasIdenticalArguments(self, command1, command2):
        for argument in self.__arguments__[command1.id]:
            if not hasattr(command2, argument):
                return False
            if getattr(command2, argument) != getattr(command1, argument):
                return False

        return True



    def _RemoveSynonymsAndAntonyms(self, command):
        doNotEnqueue = False
        newStream = []
        for existingCommand in self.stream:
            if existingCommand.id == command.id:
                if self._IsIdentifierMatch(command, existingCommand):
                    continue
            elif self._IsHeteronymMatch(command, existingCommand):
                continue
            elif self._IsAntonymMatch(command, existingCommand):
                doNotEnqueue = True
                continue
            newStream.append(existingCommand)

        self.stream = newStream
        return doNotEnqueue



    def AddCommand(self, commandID, **kwargs):
        if commandID not in self.__commands__:
            raise RuntimeError('Command not recognized')
        newCommand = util.KeyVal(id=commandID)
        for identifier in self.__identifiers__[commandID]:
            if identifier not in kwargs:
                raise RuntimeError('Missing identifier in kwargs for command')
            setattr(newCommand, identifier, kwargs[identifier])

        for argument in self.__arguments__[commandID]:
            if argument not in kwargs:
                raise RuntimeError('Missing argument in kwargs for command')
            setattr(newCommand, argument, kwargs[argument])

        doNotEnqueue = self._RemoveSynonymsAndAntonyms(newCommand)
        if not doNotEnqueue:
            self.stream.append(newCommand)
        self.history.append(newCommand)



    def Reset(self):
        self.stream = []
        self.history = []



    def GetStreamLength(self):
        return len(self.stream)



    def Serialize(self):
        serializedStream = []
        for command in self.stream:
            if command.id == COMMAND_CREATEPIN:
                args = (command.pinID,
                 command.typeID,
                 command.latitude,
                 command.longitude)
            elif command.id == COMMAND_REMOVEPIN:
                args = (command.pinID,)
            elif command.id == COMMAND_CREATELINK:
                args = (command.endpoint1, command.endpoint2, command.level)
            elif command.id == COMMAND_REMOVELINK:
                args = (command.endpoint1, command.endpoint2)
            elif command.id == COMMAND_SETLINKLEVEL:
                args = (command.endpoint1, command.endpoint2, command.level)
            elif command.id == COMMAND_CREATEROUTE:
                args = (command.routeID,
                 command.path,
                 command.typeID,
                 command.quantity)
            elif command.id == COMMAND_REMOVEROUTE:
                args = (command.routeID,)
            elif command.id == COMMAND_SETSCHEMATIC:
                args = (command.pinID, command.schematicID)
            elif command.id == COMMAND_UPGRADECOMMANDCENTER:
                args = (command.pinID, command.level)
            elif command.id == COMMAND_ADDEXTRACTORHEAD:
                args = (command.pinID,
                 command.headID,
                 command.latitude,
                 command.longitude)
            elif command.id == COMMAND_KILLEXTRACTORHEAD:
                args = (command.pinID, command.headID)
            elif command.id == COMMAND_MOVEEXTRACTORHEAD:
                args = (command.pinID,
                 command.headID,
                 command.latitude,
                 command.longitude)
            elif command.id == COMMAND_INSTALLPROGRAM:
                args = (command.pinID, command.typeID, command.headRadius)
            else:
                raise RuntimeError('Streamed Command not supported by Serialize!')
            serializedStream.append((command.id, args))

        return serializedStream



    def Deserialize(self, serializedStream, overwrite = True):
        if overwrite:
            self.stream = []
        for (commandID, argTuple,) in serializedStream:
            newCommand = util.KeyVal(id=commandID)
            if commandID == COMMAND_CREATEPIN:
                (newCommand.pinID, newCommand.typeID, newCommand.latitude, newCommand.longitude,) = argTuple
            elif commandID == COMMAND_REMOVEPIN:
                (newCommand.pinID,) = argTuple
            elif commandID == COMMAND_CREATELINK:
                (newCommand.endpoint1, newCommand.endpoint2, newCommand.level,) = argTuple
            elif commandID == COMMAND_REMOVELINK:
                (newCommand.endpoint1, newCommand.endpoint2,) = argTuple
            elif commandID == COMMAND_SETLINKLEVEL:
                (newCommand.endpoint1, newCommand.endpoint2, newCommand.level,) = argTuple
            elif commandID == COMMAND_CREATEROUTE:
                (newCommand.routeID, newCommand.path, newCommand.typeID, newCommand.quantity,) = argTuple
            elif commandID == COMMAND_REMOVEROUTE:
                (newCommand.routeID,) = argTuple
            elif commandID == COMMAND_SETSCHEMATIC:
                (newCommand.pinID, newCommand.schematicID,) = argTuple
            elif commandID == COMMAND_UPGRADECOMMANDCENTER:
                (newCommand.pinID, newCommand.level,) = argTuple
            elif commandID == COMMAND_ADDEXTRACTORHEAD:
                (newCommand.pinID, newCommand.headID, newCommand.latitude, newCommand.longitude,) = argTuple
            elif commandID == COMMAND_KILLEXTRACTORHEAD:
                (newCommand.pinID, newCommand.headID,) = argTuple
            elif commandID == COMMAND_MOVEEXTRACTORHEAD:
                (newCommand.pinID, newCommand.headID, newCommand.latitude, newCommand.longitude,) = argTuple
            elif commandID == COMMAND_INSTALLPROGRAM:
                (newCommand.pinID, newCommand.typeID, newCommand.headRadius,) = argTuple
            else:
                raise RuntimeError('Streamed Command not supported by Deserialize!')
            self.stream.append(newCommand)




    def LogCommandStream(self, logger):
        logger.LogWarn('Logging out an error in the command stream')
        streamIndex = 0
        for command in self.history:
            if streamIndex < len(self.stream) and command == self.stream[streamIndex]:
                streamIndex += 1
                prefix = ''
            else:
                prefix = 'REMOVED!: '
            errorMsg = prefix + '%s\t' % self.__commands__[command.id]
            for each in self.__identifiers__[command.id]:
                errorMsg += '%s: %s ' % (each, getattr(command, each))

            for each in self.__arguments__[command.id]:
                errorMsg += '%s: %s ' % (each, getattr(command, each))

            logger.LogWarn(errorMsg)

        logger.LogWarn('Done logging error')



exports = util.AutoExports('planet', locals())

