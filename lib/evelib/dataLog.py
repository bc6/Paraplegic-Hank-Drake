import cStringIO
import collections
import os
from dust import catmaExtension
from catma.axiom2 import Axiom2, AxiomError, ClassType, Enumerate, TypeOrderComparer, TypeInstance
import codeGeneration
from codeGeneration import UE3_VAR_PREFIX, OUTPUT_SINGLE_TABLE_COLUMN, OUTPUT_SINGLE_SPROC_INPUT, ERROR_CANT_OPEN_FILE, INFO_FILE_UNCHANGED, OUTPUT_FILE_HEADER_COMMENT, IX_COLUMNNAME, IX_DATATYPE
DATALOG_SCHEMA_NAME = 'dustDataLog'
NUMBER_OF_COMMON_COLUMNS = 3
SHORT_FILENAME = os.path.basename(__file__)
OUTPUT_FILE_HEADER_COMMENT = OUTPUT_FILE_HEADER_COMMENT.replace('{filename}', SHORT_FILENAME)
UE3_TIME_VARIABLE_NAME = 'secondsPassed'

class DataLog(Axiom2):

    def CreateType(self, typeName, typeClass = None, **kw):
        kw['typeClass'] = typeClass if typeClass else DataLogClassType
        return Axiom2.CreateType(self, typeName, **kw)



    def GeneratePythonCode(self, path):
        files = []
        validPath = 'common'
        if validPath not in path:
            raise AxiomError('Script path is invalid: %s, it should contain %s' % (path, validPath))
        (helperClasses, standaloneClasses, enums,) = self.GetDefinitionElements()
        filename = os.path.join(path, 'modules', 'dust', 'dataLogSource.py')
        MARKER = '## MARKER ##'
        oldContents = open(filename, 'r').read()
        idxStart = oldContents.find(MARKER)
        if idxStart == -1:
            print 'Failed to find starting marker in %s' % filename
            return []
        idxEnd = oldContents.rfind(MARKER)
        if idxEnd == idxStart:
            print 'Failed to find two distinct markers in %s' % filename
            return []
        idxStart = oldContents.find('\n', idxStart) + 1
        idxEnd = oldContents.rfind('\n', 0, idxEnd) + 1
        sio = cStringIO.StringIO()
        sio.write(oldContents[:idxStart])
        sio.write('entryCategories = (\n')
        for eachClass in helperClasses:
            sio.write('    "%s",\n' % eachClass.className)

        sio.write(')\n')
        sio.write(oldContents[idxEnd:])
        sNew = sio.getvalue()
        if oldContents == sNew:
            print INFO_FILE_UNCHANGED.format(filename)
            return []
        codeGeneration.AutoCheckoutMagic(filename)
        try:
            f = open(filename, 'w')
        except IOError:
            print ERROR_CANT_OPEN_FILE.format(filename)
            return []
        f.write(sNew)
        f.close()
        files.append(filename)
        return files



    def GenerateCppCode(self, path):
        files = []
        validPath = 'Development\\Src\\DustGame\\Inc'
        if validPath not in path:
            raise AxiomError('Script path is invalid: %s, it should contain %s' % (path, validPath))
        (helperClasses, standaloneClasses, enums,) = self.GetDefinitionElements()
        filename = os.path.join(path, 'DustDataLogGenerated.h')
        f = cStringIO.StringIO()
        f.write(OUTPUT_FILE_HEADER_COMMENT.format('//'))
        f.write('void UDustDataLog::Clear()\n{\n    SCOPE_CYCLE_COUNTER( STAT_DataLogTime );\n')
        for eachClass in helperClasses:
            f.write('    m%sEntries.Empty();\n' % eachClass.className)

        f.write('    SET_MEMORY_STAT( STAT_DataLogMemory, 0 );\n')
        f.write('}\n\n')
        for eachClass in helperClasses:
            cd = {'name': eachClass.className}
            f.write('void UDustDataLog::Add_%(name)s( ' % cd)
            cnt = 0
            for (memberName, memberType,) in eachClass._members.items():
                if not memberType.IsRemoved() and memberType.IsExported():
                    commaMaybe = '' if cnt == 0 else ','
                    ue3Type = catmaExtension.GetUE3Type(memberType.GetBaseType())
                    if ue3Type == 'int':
                        cppType = 'INT'
                    elif ue3Type == 'float':
                        cppType = 'FLOAT'
                    elif ue3Type == 'bool':
                        cppType = 'UBOOL'
                    elif isinstance(memberType, TypeInstance) and isinstance(memberType.GetBaseType(), Enumerate):
                        if len(memberType.GetBaseType().elements) < 256:
                            cppType = 'BYTE'
                        else:
                            cppType = ue3Type
                    else:
                        cppType = 'F' + ue3Type + ''
                    f.write('%s %s %s%s' % (commaMaybe,
                     cppType,
                     UE3_VAR_PREFIX,
                     memberName))
                cnt += 1

            f.write(' )\n{\n    SCOPE_CYCLE_COUNTER( STAT_DataLogTime );\n    struct F%(name)sEntry entry;\n\n' % cd)
            for (memberName, memberType,) in eachClass._members.items():
                if not memberType.IsRemoved() and memberType.IsExported():
                    f.write('    entry.%s%s = %s%s;\n' % (UE3_VAR_PREFIX,
                     memberName,
                     UE3_VAR_PREFIX,
                     memberName))

            f.write('    entry.%s%s = GWorld->GetWorldInfo( )->RealTimeSeconds;\n' % (UE3_VAR_PREFIX, UE3_TIME_VARIABLE_NAME))
            f.write('\n')
            f.write('    DWORD numBytes = m%(name)sEntries.GetAllocatedSize();\n' % cd)
            f.write('    m%(name)sEntries.AddItem( entry );\n' % cd)
            f.write('    INC_MEMORY_STAT_BY( STAT_DataLogMemory, m%(name)sEntries.GetAllocatedSize() - numBytes );\n' % cd)
            f.write('}\n\n')

        sNew = f.getvalue()
        if os.path.exists(filename):
            sOld = open(filename, 'r').read()
            if sOld == sNew:
                print INFO_FILE_UNCHANGED.format(filename)
                return []
            codeGeneration.AutoCheckoutMagic(filename)
        try:
            fReal = open(filename, 'w')
        except IOError:
            print ERROR_CANT_OPEN_FILE.format(filename)
            return []
        fReal.write(sNew)
        fReal.close()
        files.append(filename)
        return files



    def GenerateUE3Code(self, path):
        files = []
        validPath = 'Development\\Src\\DustGame\\Classes'
        if validPath not in path:
            raise AxiomError('Script path is invalid: %s, it should contain %s' % (path, validPath))
        (helperClasses, standaloneClasses, enums,) = self.GetDefinitionElements()
        f = cStringIO.StringIO()
        f.write(OUTPUT_FILE_HEADER_COMMENT.format('//'))
        f2 = cStringIO.StringIO()
        f2.write(OUTPUT_FILE_HEADER_COMMENT.format('//'))
        decl = '  var(%(group)s) %(uemodifier)s %(type)s %(prefix)s%(name)s;%(text)s\n'
        for eachClass in helperClasses:
            header = 'struct native %sEntry\n{\n' % eachClass.className
            f.write(header)
            memberGroup = None
            for (memberName, memberType,) in eachClass._members.items():
                if not memberType.IsRemoved() and memberType.IsExported():
                    ue3Type = catmaExtension.GetUE3Type(memberType.GetBaseType())
                    if ue3Type == 'bool':
                        ue3Type = 'int'
                    memberGroup = memberType.group if memberType.group else ''
                    fmt = {'group': memberGroup,
                     'type': 'array<%s>' % ue3Type if memberType.IsSet() else ue3Type,
                     'name': memberName,
                     'text': ' // %s' % memberType.text if memberType.text else '',
                     'uemodifier': getattr(memberType, 'uemodifier', ''),
                     'prefix': UE3_VAR_PREFIX}
                    f.write(decl % fmt)

            fmt = {'group': memberGroup,
             'type': 'float',
             'name': UE3_TIME_VARIABLE_NAME,
             'text': '',
             'uemodifier': '',
             'prefix': UE3_VAR_PREFIX}
            f.write(decl % fmt)
            f.write('};\n\n')

        for eachClass in helperClasses:
            f.write('var array<%(name)sEntry> m%(name)sEntries;\n' % {'name': eachClass.className})

        f.write('\n')
        for eachClass in helperClasses:
            cd = {'name': eachClass.className}
            f.write('native function Add_%(name)s(' % cd)
            cnt = 0
            for (memberName, memberType,) in eachClass._members.items():
                if not memberType.IsRemoved() and memberType.IsExported():
                    commaMaybe = '' if cnt == 0 else ','
                    f.write('%s %s %s%s' % (commaMaybe,
                     catmaExtension.GetUE3Type(memberType.GetBaseType()),
                     UE3_VAR_PREFIX,
                     memberName))
                cnt += 1

            f.write(' );\n')

        for eachClass in helperClasses:
            cd = {'name': eachClass.className}
            f2.write('function array<%(name)sEntry> Get%(name)sEntries()\n{\n' % cd)
            f2.write("    return DustTeamGame(class'WorldInfo'.static.GetWorldInfo().Game).GetDataLog().m%(name)sEntries;\n}\n\n" % cd)

        writables = {}
        filename1 = os.path.join(path, 'DustDataLog.uci')
        writables[filename1] = f.getvalue()
        filename2 = os.path.join(path, 'DustUISvcDataLog.uci')
        writables[filename2] = f2.getvalue()
        badFiles = []
        for (filename, sNew,) in writables.items():
            if os.path.exists(filename):
                s = open(filename, 'r').read()
                if s == sNew:
                    print INFO_FILE_UNCHANGED.format(filename)
                    continue
                codeGeneration.AutoCheckoutMagic(filename)
            try:
                currentFile = open(filename, 'w')
            except IOError:
                badFiles.append(filename)
                continue
            currentFile.write(sNew)
            currentFile.close()
            files.append(filename)

        if badFiles:
            for filename in badFiles:
                print ERROR_CANT_OPEN_FILE.format(filename)

        return files



    def GetDefinitionElements(self):
        helperClasses = []
        standaloneClasses = []
        enums = []
        for (typeName, typeDef,) in self._typeDefs.items():
            if isinstance(typeDef, ClassType):
                if typeDef.standalone:
                    if catmaExtension.IsForUE3(typeDef):
                        standaloneClasses.append(typeDef)
                elif catmaExtension.IsForUE3(typeDef):
                    helperClasses.append(typeDef)
            elif isinstance(typeDef, Enumerate) and catmaExtension.IsForUE3(typeDef):
                enums.append(typeDef)

        helperClasses.sort(TypeOrderComparer)
        return (helperClasses, standaloneClasses, enums)



    def GenerateSQLTableDefinitions(self, path):
        files = []
        (classes, _, _,) = self.GetDefinitionElements()
        basicTypes = ['float', 'int']
        tableColumns = {}
        tableNames = {}
        for classDef in classes:
            tableName = classDef.className
            nameData = {}
            nameData['schemaName'] = DATALOG_SCHEMA_NAME
            nameData['lowerTableName'] = codeGeneration.MakeLowerTableName(tableName)
            nameData['dbTableName'] = nameData['lowerTableName'] + 's'
            nameData['keyName'] = nameData['lowerTableName'] + 'ID'
            nameData['insertProcName'] = tableName + 's_Insert'
            tableNames[tableName] = nameData
            columnList = []
            tableColumns[classDef.className] = columnList
            columnList.append((nameData['keyName'], 'bigint', 'IDENTITY(1, 1)'))
            columnList.append(('dataLogDate', 'datetime2(0)'))
            columnList.append(('matchID', 'int'))
            for (memberName, memberType,) in classDef._members.items():
                if not memberType.IsRemoved() and memberType.IsExported():
                    textType = catmaExtension.GetUE3Type(memberType.GetBaseType())
                    numColumns = len(columnList)
                    if textType in basicTypes:
                        columnList.append((memberName, textType))
                    elif textType == 'Bool' or textType == 'bool':
                        columnList.append((memberName, 'bit'))
                    elif isinstance(memberType, TypeInstance):
                        baseType = memberType.GetBaseType()
                        if isinstance(baseType, Enumerate):
                            columnList.append((memberName, 'int'))
                        elif isinstance(baseType, ClassType):
                            for (fieldName, memberType,) in baseType.GetMembers().iteritems():
                                columnList.append((memberName + '_' + fieldName, memberType.type))

                    if len(columnList) == numColumns:
                        print "Unrecognized data type '{0}' --not generating SQL files for dataLog event '{1}'!".format(memberType, tableName)
                        del tableColumns[tableName]
                        break


        tableSizes = {}
        for (tableName, columnList,) in tableColumns.items():
            tableSizes[tableName] = codeGeneration.GetSQLColumnSizeData(columnList)

        for (tableName, columnList,) in tableColumns.items():
            sizeData = tableSizes[tableName]
            nameData = tableNames[tableName]
            filename = codeGeneration.WriteSQLTableFile(nameData, columnList, sizeData, SHORT_FILENAME, lineBreaksAfter=[NUMBER_OF_COMMON_COLUMNS])
            if filename:
                files.append(filename)
            filename = codeGeneration.WriteSQLInsertProcFile(nameData, columnList, sizeData, SHORT_FILENAME, omitColumns=[nameData['keyName']])
            if filename:
                files.append(filename)

        return files




class OrderedDict(dict):

    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.keyOrder = []



    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        dict.__setitem__(self, key, value)



    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.keyOrder.remove(key)



    def __str__(self):
        return '{' + ', '.join([ '{0}: {1}'.format(key, value) for (key, value,) in self.iteritems() ]) + '}'



    def __iter__(self):
        for key in self.keyOrder:
            yield key




    def iterkeys(self):
        for key in self.keyOrder:
            yield key




    def keys(self):
        return [ key for key in self.iterkeys() ]



    def itervalues(self):
        for key in self.keyOrder:
            yield self[key]




    def values(self):
        return [ value for value in self.itervalues() ]



    def iteritems(self):
        for key in self.keyOrder:
            yield (key, self[key])




    def items(self):
        return [ (key, value) for (key, value,) in self.iteritems() ]




class DataLogClassType(ClassType):

    def __init__(self, *args, **kw):
        ClassType.__init__(self, *args, **kw)
        self._members = OrderedDict()




