#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/dhtmlxwriters.py
import macho
import xmlwriter

class DHtmlXElement:
    __guid__ = 'xmlwriter.DHtmlXElement'

    def __init__(self):
        self.hasChild = False


class DHtmlXData_Default:
    __guid__ = 'xmlwriter.DHtmlXData_Default'

    def __init__(self):
        pass

    @staticmethod
    def DataToStr(val):
        try:
            ret = unicode(val)
            equalSign = ret.startswith('= ')
            if equalSign:
                ret = ret[2:]
            ret = float(ret)
            ret = ('%.13f' % ret).rstrip('0')
            if ret.endswith('.'):
                ret = ret[:-1]
            if equalSign:
                ret = '= ' + ret
        except ValueError:
            ret = unicode(val)

        return ret

    def WriteHead(self, id):
        return '<%s id="%s">' % ('data', id)

    def WriteTail(self, id):
        return '</data>'

    def WriteElement(self, element):
        ret = '<element '
        for key in element.__dict__.keys():
            ret = ret + '%s="%s" ' % (self.FormatString(key), self.FormatString(self.DataToStr(element.__dict__[key])))

        ret = ret + ' />'
        return ret

    def FormatString(self, string):
        string = unicode(string)
        string = string.replace('&', '&amp;')
        string = string.replace('<', '&lt;')
        string = string.replace('>', '&gt;')
        string = string.replace("'", '&apos;')
        string = string.replace('"', '&quot;')
        return string


class DHtmlXData_Tree(DHtmlXData_Default):
    __guid__ = 'xmlwriter.DHtmlXData_Tree'

    def WriteHead(self, id):
        return '<%s id="%s">' % ('tree', self.FormatString(id))

    def WriteTail(self, id):
        return '</tree>'

    def WriteElement(self, element):
        if element.hasChild == True:
            element.child = 1
        ret = '<item '
        for key in element.__dict__.keys():
            ret = ret + '%s="%s" ' % (self.FormatString(key), self.FormatString(self.DataToStr(element.__dict__[key])))

        ret = ret + ' />'
        return ret


class DHtmlXData_Grid(DHtmlXData_Default):
    __guid__ = 'xmlwriter.DHtmlXData_Grid'

    def WriteHead(self, id):
        return '<%s id="%s">' % ('rows', self.FormatString(id))

    def WriteTail(self, id):
        return '</rows>'

    def WriteElement(self, element):
        if element.hasChild:
            ret = '<row id="%s" xmlkids="1">' % self.FormatString(element.id)
        else:
            ret = '<row id="%s">' % self.FormatString(element.id)
        for key in element.__dict__.keys():
            ret = ret + '<%s>%s</%s>' % (self.FormatString(key), self.FormatString(self.DataToStr(element.__dict__[key])), key)

        ret = ret + '</row>'
        return ret


class DHtmlXData_TreeGrid(DHtmlXData_Default):
    __guid__ = 'xmlwriter.DHtmlXData_TreeGrid'

    def WriteHead(self, id):
        return '<rows parent="%s">' % self.FormatString(id)

    def WriteTail(self, id):
        return '</rows>'

    def WriteElement(self, element):
        if element.hasChild:
            ret = '<row id="%s" xmlkids="1">' % self.FormatString(element.id)
        else:
            ret = '<row id="%s">' % self.FormatString(element.id)
        for key in element.__dict__.keys():
            ret = ret + '<%s>%s</%s>' % (self.FormatString(key), self.FormatString(self.DataToStr(element.__dict__[key])), self.FormatString(key))

        ret = ret + '</row>'
        return ret


class DHtmlXDataWriter(xmlwriter.XmlWriter):
    __guid__ = 'xmlwriter.DHtmlXDataWriter'

    def __init__(self):
        xmlwriter.XmlWriter.__init__(self)
        self.DHtmlXData = DHtmlXData_Default()

    def WriteHead(self, id):
        self.Write(self.DHtmlXData.WriteHead(id))

    def WriteTail(self, id):
        self.Write(self.DHtmlXData.WriteTail(id))

    def WriteElement(self, element):
        self.Write(self.DHtmlXData.WriteElement(element))

    def SetControlType(self, controlType):
        if controlType.lower() == 'tree':
            self.DHtmlXData = xmlwriter.DHtmlXData_Tree()
        elif controlType.lower() == 'grid':
            self.DHtmlXData = xmlwriter.DHtmlXData_Grid()
        elif controlType.lower() == 'treegrid':
            self.DHtmlXData = xmlwriter.DHtmlXData_TreeGrid()