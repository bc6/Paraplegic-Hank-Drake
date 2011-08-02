import util
import log

def GetQuote(blueprintTypeID, activityID, materialLevel = 0):
    blueprint = cfg.invbptypes.Get(blueprintTypeID)
    skills = util.Rowset(['skillTypeID', 'level'])
    materials = util.Rowset(['materialTypeID', 'quantity', 'waste'])
    extras = util.Rowset(['extraTypeID', 'quantity', 'damage'])
    matIdx = {}
    if activityID == const.activityManufacturing:
        for row in cfg.invtypematerials.get(blueprint.productTypeID, []):
            matIdx[row.materialTypeID] = row.quantity

    if (blueprintTypeID, activityID) in cfg.ramtyperequirements:
        for row in cfg.ramtyperequirements[(blueprintTypeID, activityID)]:
            reqType = cfg.invtypes.Get(row.requiredTypeID)
            if reqType.categoryID == const.categorySkill:
                skills.append([row.requiredTypeID, row.quantity])
                if row.damagePerJob or row.recycle:
                    log.LogTraceback('Bogus skill data in facItemTypeRequirements: %s' % row)
            else:
                if row.recycle:
                    for deduct in cfg.invtypematerials.get(row.requiredTypeID, []):
                        if deduct.materialTypeID in matIdx:
                            matIdx[deduct.materialTypeID] -= deduct.quantity
                        else:
                            matIdx[deduct.materialTypeID] = deduct.quantity

                    if row.damagePerJob != 1.0:
                        log.LogTraceback('Bogus recycle data in facItemTypeRequirements: %s' % row)
                extras.append([row.requiredTypeID, row.quantity, row.damagePerJob])

    wasteFactor = blueprint.wasteFactor / 100.0 / (materialLevel + 1)
    for (materialTypeID, quantity,) in matIdx.items():
        if quantity > 0:
            waste = int(round(quantity * wasteFactor))
            materials.append([materialTypeID, quantity, waste])

    quote = util.KeyVal(skills=skills, materials=materials, extras=extras, __doc__='RamQuote for [%s,%s]' % (blueprintTypeID, activityID))
    return quote



def Benchmark(blueprintTypeID, activityID, materialLevel = 0):
    sw = util.Stopwatch()
    for i in xrange(1000):
        GetQuote(blueprintTypeID, activityID, materialLevel)

    print sw


exports = {'ramCalculator.GetQuote': GetQuote,
 'ramCalculator.Benchmark': Benchmark}

