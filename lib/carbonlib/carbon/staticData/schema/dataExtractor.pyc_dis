#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\dataExtractor.py


def ExtractFromDict(obj, schema, fieldValueMap):
    if CheckSchemaNode(schema, fieldValueMap):
        return {'found': True,
         'object': obj}
    foundSomeData = False
    extractedObject = {}
    for each in obj:
        data = WalkSchema(obj[each], schema.get('valueTypes'), fieldValueMap)
        if data['found']:
            foundSomeData = True
            extractedObject[each] = data['object']

    return {'found': foundSomeData,
     'object': extractedObject}


def ExtractFromList(obj, schema, fieldValueMap):
    if CheckSchemaNode(schema, fieldValueMap):
        return {'found': True,
         'object': obj}
    foundSomeData = False
    extractedObject = []
    for each in obj:
        data = WalkSchema(each, schema.get('itemTypes'), fieldValueMap)
        if data['found']:
            foundSomeData = True
            extractedObject.append(data['object'])

    return {'found': foundSomeData,
     'object': extractedObject}


def ExtractFromObject(obj, schema, fieldValueMap):
    if CheckSchemaNode(schema, fieldValueMap):
        return {'found': True,
         'object': obj}
    foundSomeData = False
    extractedObject = {}
    for each in obj:
        data = WalkSchema(obj[each], schema.get('attributes')[each], fieldValueMap)
        if data['found']:
            foundSomeData = True
            extractedObject[each] = data['object']

    return {'found': foundSomeData,
     'object': extractedObject}


def ExtractFromLeafNode(obj, schema, fieldValueMap):
    if CheckSchemaNode(schema, fieldValueMap):
        return {'found': True,
         'object': obj}
    return {'found': False,
     'object': None}


def CheckSchemaNode(schema, fieldValueMap):
    for eachField in fieldValueMap:
        if schema.get(eachField, None) == fieldValueMap[eachField]:
            return True

    return False


builtInExtractionFunctions = {'dict': ExtractFromDict,
 'list': ExtractFromList,
 'object': ExtractFromObject}

def WalkSchema(obj, schemaNode, fieldValueMap):
    attributeType = schemaNode['type']
    if attributeType is None:
        return {'found': False,
         'object': None}
    if attributeType in builtInExtractionFunctions:
        newData = builtInExtractionFunctions[attributeType](obj, schemaNode, fieldValueMap)
    else:
        newData = ExtractFromLeafNode(obj, schemaNode, fieldValueMap)
    return newData


def ExtractData(obj, schema, fieldValueMap):
    newData = WalkSchema(obj, schema, fieldValueMap)
    if 'object' in newData:
        return newData['object']