import sys

class Field:
    __guid__ = 'naiveXML.Field'

    def __init__(self):
        self.value = None
        self.klass = ''
        self.attributes = {}
        self.subFields = None



    def FindField(self, lineNo):
        line = self.value[lineNo]
        ix = line.find('<')
        if ix != -1:
            if line[(ix + 1):(ix + 2)] != '/':
                return (line[(ix + 1):line.find('>')], ix)
        return (None, None)



    def FindClosure(self, startLine, startIx, field):
        nested = 1
        ix = self.value[startLine][startIx:].find(field)
        if ix != -1:
            return (startLine, startIx + ix)
        for i in range(startLine + 1, len(self.value)):
            ix = self.value[i].find(field)
            if ix == -1:
                continue
            preceding = self.value[i][(ix - 1):ix]
            if preceding == '/':
                nested -= 1
                if not nested:
                    return (i, ix)
            elif preceding == '<' and self.value[i][ix:].find('>'):
                nested += 1

        errStr = 'no closure found for "' + field + '" at ' + str(startLine)
        raise RuntimeError(errStr)



    def FindAttributes(self, lineNo, field):
        line = self.value[lineNo]
        sub = line[(line.find(field) + len(field) + 1):]
        attribsStr = sub[:sub.find('>')]
        if not attribsStr:
            return None
        attribs = attribsStr.split()
        d = {}
        for each in attribs:
            (key, value,) = each.split('=')
            d[key] = value[1:-1]

        return d



    def InitSubFields(self):
        if self.subFields != None:
            return 
        self.subFields = []
        if type(self.value) != type([]):
            print 'not list'
        lineNo = 0
        print 'len:',
        print len(self.value)
        while lineNo < len(self.value):
            print lineNo
            (fieldName, startPlace,) = self.FindField(lineNo)
            if fieldName:
                endPlace = startPlace + len(fieldName)
                actualFieldName = fieldName.split(' ', 1)
                actualFieldName = actualFieldName[0]
                (endLine, endIx,) = self.FindClosure(lineNo, endPlace, actualFieldName)
                f = Field()
                f.klass = actualFieldName
                f.attributes = self.FindAttributes(lineNo, actualFieldName)
                if lineNo == endLine:
                    f.value = self.value[lineNo][(endPlace + 2):(endIx - 2)]
                else:
                    f.value = self.value[(lineNo + 1):endLine]
                lineNo = endLine
                self.subFields.append(f)
            lineNo += 1




    def InitFromTextfile(self, file):
        self.value = file[1:-1]
        firstline = file[0]
        self.klass = firstline[firstline.find('<'):firstline.find('>')]



    def GetData(self, name):

        class PrivData:
            pass
        self.InitSubFields()
        for field in self.subFields:
            if field.klass == 'data' and field.attributes.get('name', None) == name:
                ret = PrivData()
                for (key, val,) in field.attributes.iteritems():
                    setattr(ret, key, val)

                setattr(ret, 'data', field.value)
                return ret




    def GetField(self, name):
        self.InitSubFields()
        for field in self.subFields:
            if field.klass == name:
                return field




    def GetFields(self, name):
        self.InitSubFields()
        ret = []
        for field in self.subFields:
            if field.klass == name:
                ret.append(field)

        return ret




class Obj:
    pass

def Extract(field):
    obj = Obj()
    field.InitSubFields()
    for subfield in field.subFields:
        if subfield.klass == 'data':
            aname = subfield.attributes.get('name')
            data = field.GetData(aname)
            if data.type == 'list':
                l = []
                for line in data.data:
                    l.append(eval(line[:-2]))

                setattr(obj, aname, l)
            elif data.type == 'dict':
                d = {}
                for line in data.data:
                    l = line.strip()
                    (key, value,) = line.split(':')
                    d[key] = eval(value[:-2])

                setattr(obj, aname, d)
            else:
                if type(data.data) == type([]):
                    someData = data.data[0][:-2]
                else:
                    someData = data.data
                try:
                    setattr(obj, aname, eval(someData))
                except:
                    setattr(obj, aname, str(someData))
                    sys.exc_clear()
            continue
        if subfield.attributes:
            aType = subfield.attributes.get('type', None)
            if aType == 'list':
                setattr(obj, subfield.klass, [])
                nameOfItems = subfield.attributes.get('name', None)
                if not nameOfItems:
                    raise RuntimeError('no name of things in list')
                fieldList = subfield.GetFields(nameOfItems)
                daList = getattr(obj, subfield.klass)
                for each in fieldList:
                    daList.append(Extract(each))

            continue
        setattr(obj, subfield.klass, Extract(subfield))

    if hasattr(field, 'attributes'):
        setattr(obj, 'attributes', field.attributes)
    return obj


exports = {'naiveXML.Extract': Extract}

