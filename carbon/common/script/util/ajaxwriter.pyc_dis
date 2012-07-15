#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/ajaxwriter.py
import htmlwriter
import types
import datetime
import util

class AjaxWriter(htmlwriter.HtmlWriter):
    __guid__ = 'htmlwriter.AjaxWriter'
    __dependencies__ = []

    def __init__(self, ajaxfilter, neededRoles, session):
        htmlwriter.HtmlWriter.__init__(self, template='script:/wwwroot/lib/template/empty.html')
        self.ajaxfilter = ajaxfilter
        self.neededRoles = neededRoles
        self.session = session
        try:
            self.DB2 = sm.services['DB2']
        except:
            pass

    def WriteJsonGridList(self, columns, data, pageNumber, numberOfPages):
        colFunc = lambda row: '{"id":"%(id)s","cell":%(cell)s}' % {'id': unicode(getattr(row, columns[0], None)()),
         'cell': unicode([ unicode(getattr(row, c1, None)()) for c1 in columns ]).replace("'", '"')}
        self.Write('{"page":"%(page)s","total":%(total)s,"records":"%(records)s","rows":[%(rows)s]}' % {'page': str(pageNumber),
         'total': str(numberOfPages),
         'records': str(len(data)),
         'rows': str(','.join(map(colFunc, data)))})

    def WriteJsonList(self, valueId, captionId, data):
        self.Write(self.ToJsonList(self.PrepJson(valueId, captionId, data)))

    def PrepJson(self, valueId, captionId, data):
        res = []
        for d in data:
            try:
                yield res + [self.ToJson(str(getattr(d, valueId, None)()), str(getattr(d, captionId, None)()))]
            except:
                yield res + [self.ToJson(str(getattr(d, valueId, None)), str(getattr(d, captionId, None)))]

    def ToJson(self, kpart, labelpart):
        return '{"id":"%s","label":"%s"}' % (str(kpart), str(labelpart).replace("'", '').replace('\xb4', ''))

    def ToJsonList(self, gen):
        return str(map(''.join, gen)).replace("'", '')

    def HasAccess(self):
        return session.userid and session.role & self.neededRoles

    def Lookup(self, table, key_field, value_field):
        if not self.HasAccess:
            return self.Write('[]')
        rs = self.DB2.GetSchema('zsystem').Lookup(table, key_field, value_field, None, None, None, util.EscapeSQL(unicode(self.ajaxfilter)), 0)
        return self.WriteJsonList(key_field, value_field, rs)

    def MediaTypeBin(self):
        self.response.contentType = 'application/octet-stream'

    def MediaTypeJson(self):
        self.response.contentType = 'application/json; charset=utf-8'

    def MediaTypeXml(self):
        self.response.contentType = 'application/xhtml+xml'

    def MediaTypeAtom(self):
        self.response.contentType = 'application/atom+xml'

    def HandleAction(self, action, request, response):
        self.request = request
        self.response = response
        argstuple = self.GetActionArgs(request, action)
        if argstuple:
            args, kwargs = argstuple
            try:
                getattr(self, action)(*args, **kwargs)
            except TypeError as e:
                sm.services['http'].LogError('Bad params (', kwargs, ') sent to ', action, ', resulting in exception: ', e)
                raise 

        else:
            self.Write('[]')