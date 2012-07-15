#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\testtools.py
from werkzeug import Response, cached_property, import_string

class ContentAccessors(object):

    def xml(self):
        if 'xml' not in self.mimetype:
            raise AttributeError('Not a XML response (Content-Type: %s)' % self.mimetype)
        for module in ['xml.etree.ElementTree', 'ElementTree', 'elementtree.ElementTree']:
            etree = import_string(module, silent=True)
            if etree is not None:
                return etree.XML(self.body)

        raise RuntimeError('You must have ElementTree installed to use TestResponse.xml')

    xml = cached_property(xml)

    def lxml(self):
        if 'html' not in self.mimetype and 'xml' not in self.mimetype:
            raise AttributeError('Not an HTML/XML response')
        from lxml import etree
        try:
            from lxml.html import fromstring
        except ImportError:
            fromstring = etree.HTML

        if self.mimetype == 'text/html':
            return fromstring(self.data)
        return etree.XML(self.data)

    lxml = cached_property(lxml)

    def json(self):
        if 'json' not in self.mimetype:
            raise AttributeError('Not a JSON response')
        try:
            from simplejson import loads
        except:
            from json import loads

        return loads(self.data)

    json = cached_property(json)


class TestResponse(Response, ContentAccessors):
    pass