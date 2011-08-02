from catmaConfig import ATTRIB_FLAGS
from const import TYPEID_NONE
import catmaDB
import axiom2
import re

class BaseCheck(object):
    tag = 'base'
    prefix = None

    def __init__(self, runner):
        self._runner = runner



    def CheckForInvalidValues(self, typeInstance, db):
        criticalValues = typeInstance.GetAllValues(None, True, True, True)
        for (valueName, valueInfo,) in criticalValues.iteritems():
            value = valueInfo[0]
            attFlag = valueInfo[1]
            valueRange = valueInfo[2]
            if value is None:
                if attFlag & ATTRIB_FLAGS.NOT_NULL:
                    self._runner.ReportError(typeInstance, 'missing value: %s' % valueName)
            elif attFlag & ATTRIB_FLAGS.TYPE_REF and value != TYPEID_NONE:
                try:
                    referencedType = db.GetTypeByID(value)
                    checkErrors = self._runner.CheckEntry(referencedType, db)
                    if checkErrors:
                        self._runner.ReportError(typeInstance, "referenced catma type '%s' on %s has errors" % (referencedType.GetTypeName(), valueName))
                    if not referencedType.IsPublished():
                        self._runner.ReportError(typeInstance, "referenced catma type '%s' on %s is not published" % (referencedType.GetTypeName(), valueName))
                except catmaDB.CatmaDBError:
                    self._runner.ReportError(typeInstance, "couldn't find referenced catma type with typeID '%s'on %s" % (value, valueName))
            if valueRange is not None and value is not None:
                (rangeMin, rangeMax,) = valueRange
                if rangeMin is not None and value < rangeMin or rangeMax is not None and value > rangeMax:
                    self._runner.ReportError(typeInstance, "attribute '%s' value '%s' out of range: [%s, %s]" % (valueName,
                     value,
                     rangeMin,
                     rangeMax))




    def CheckType(self, db, typeInstance):
        self.CheckNamingConvention(typeInstance)
        self.CheckForInvalidValues(typeInstance, db)



    def CheckNamingConvention(self, entry):
        filterName = 'typeNameConvention' if entry.GetIsType() else 'folderNameConvention'
        regex = entry.GetValue(filterName, None)
        if regex and not re.match(regex, entry.GetTypeName()):
            self._runner.ReportError(entry, "CATMA name '%s' does not conform to regular expression '%s'" % (entry.GetTypeName(), regex))



    def CheckFolder(self, folder):
        self.CheckNamingConvention(folder)



    def Recognize(self, typeInstance):
        typeName = typeInstance.GetTypeName().lower()
        if self.prefix:
            for pfx in self.prefix:
                if typeName.find(pfx) == 0:
                    return True

        return False




class VehicleCheck(BaseCheck):
    tag = 'vehicle'
    prefix = ['veh_']

    def CheckType(self, db, typeInstance):
        super(VehicleCheck, self).CheckType(db, typeInstance)




class ModuleCheck(BaseCheck):
    tag = 'module'
    prefix = ['imod', 'vmod', 'imp']

    def CheckType(self, db, typeInstance):
        super(ModuleCheck, self).CheckType(db, typeInstance)




class InstallationCheck(BaseCheck):
    tag = 'installation'
    prefix = ['inst_']

    def CheckType(self, db, typeInstance):
        super(InstallationCheck, self).CheckType(db, typeInstance)




class CharacterCheck(BaseCheck):
    tag = 'character'
    prefix = ['char_']

    def CheckType(self, db, typeInstance):
        super(CharacterCheck, self).CheckType(db, typeInstance)




class WeaponCheck(BaseCheck):
    tag = 'weapon'
    prefix = ['twpn_', 'wpn_']

    def CheckType(self, db, typeInstance):
        super(WeaponCheck, self).CheckType(db, typeInstance)




class EffectorCheck(BaseCheck):
    tag = 'weapon effector'
    prefix = ['eft_']

    def CheckType(self, db, typeInstance):
        super(EffectorCheck, self).CheckType(db, typeInstance)




class GameTypeCheck(BaseCheck):
    tag = 'game type'

    def CheckType(self, db, typeInstance):
        super(GameTypeCheck, self).CheckType(db, typeInstance)




class TurretCheck(BaseCheck):
    prefix = ['tur_']

    def CheckType(self, db, typeInstance):
        super(TurretCheck, self).CheckType(db, typeInstance)




class CheckRunner(object):
    checkClasses = [VehicleCheck,
     ModuleCheck,
     InstallationCheck,
     CharacterCheck,
     WeaponCheck,
     EffectorCheck,
     TurretCheck]

    def __init__(self):
        self._checkedEntries = {}
        self._skippedEntries = []



    def GetNumCheckedEntries(self):
        return len(self._checkedEntries)



    def GetNumSkippedEntries(self):
        return len(self._skippedEntries)



    def GetCheckClass(self, catmaType):
        finalCheck = None
        for checkClass in self.checkClasses:
            check = checkClass(self)
            if check.Recognize(catmaType):
                finalCheck = check
                break

        if finalCheck is None:
            finalCheck = BaseCheck(self)
        return finalCheck



    def ReportError(self, entry, error):
        if entry in self._checkedEntries:
            self._checkedEntries[entry].append(error)
        else:
            self._checkedEntries[entry] = [error]



    def GetErrors(self):
        allErrors = {}
        for (entry, errors,) in self._checkedEntries.iteritems():
            if errors:
                allErrors[entry] = errors

        return allErrors



    def CheckEntry(self, entry, db):
        check = self.GetCheckClass(entry)
        if check:
            if entry not in self._checkedEntries:
                self._checkedEntries[entry] = []
                if entry.GetIsType():
                    check.CheckType(db, entry)
                else:
                    check.CheckFolder(entry)
            return self._checkedEntries[entry]
        if entry not in self._skippedEntries:
            self._skippedEntries.append(entry)



    def CheckAll(self, ax2, pathFilter = None):
        db = catmaDB.CatmaDB()
        dumpValueRangeFlag = ax2.GetFlag(axiom2.FLAG_DumpValueRange)
        ax2.SetFlag(axiom2.FLAG_DumpValueRange, True)
        ax2.GenerateDB(db, axiom2.EXPORT_ALL, True)
        ax2.SetFlag(axiom2.FLAG_DumpValueRange, dumpValueRangeFlag)
        self._checkedEntries = {}
        self._skippedEntries = []
        allEntries = db._folders
        for (entryPath, entry,) in allEntries.iteritems():
            if pathFilter is None or pathFilter in entryPath:
                self.CheckEntry(entry, db)

        printError = False
        if printError:
            print '==== %s entries checked, %s skipped ====' % (len(self._checkedEntries), len(self._skippedEntries))
            for (typeInstance, errors,) in self._checkedEntries.iteritems():
                if errors:
                    print '\n'
                    print '%s:' % typeInstance.GetTypeName()
                    for error in errors:
                        print '    %s' % error


            if False:
                print '==== skipped list ===='
                for skippedType in self._skippedEntries:
                    print '  %s' % skippedType.GetTypeName()





