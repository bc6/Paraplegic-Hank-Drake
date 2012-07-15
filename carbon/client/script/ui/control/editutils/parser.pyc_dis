#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/editutils/parser.py
import hparser
import _weakref
import htmlentitydefs
import types
import sys
import re
supportedTags = ['area',
 'a',
 'b',
 'blockquote',
 'br',
 'body',
 'em',
 'form',
 'h1',
 'h2',
 'h3',
 'h4',
 'h5',
 'h6',
 'hr',
 'i',
 'img',
 'input',
 'li',
 'link',
 'map',
 'ol',
 'option',
 'p',
 'select',
 'strong',
 'textarea',
 'title',
 'u',
 'ul',
 'table',
 'colgroup',
 'col',
 'tr',
 'td',
 'th',
 'font',
 'div',
 'span',
 'pre',
 'meta']
ignoredTags = ['html', 'head']
autoClose = {'body': ('p', 'a', 'u', 'i', 'b', 'strong', 'em', 'table', 'div', 'ul', 'ol'),
 'p': ('a', 'u', 'i', 'b', 'strong', 'em'),
 'table': ('tr', 'td', 'th', 'colgroup', 'div'),
 'tr': ('td', 'th'),
 'td': ('td', 'th'),
 'th': ('td', 'th'),
 'div': ('p', 'table', 'a', 'u', 'i', 'b'),
 'ul': 'li',
 'ol': 'li',
 'a': ('b', 'u', 'i'),
 'option': 'option',
 'select': 'option'}
optionalClose = {'option': 'option',
 'td': ('td', 'th'),
 'th': ('td', 'th'),
 'tr': ('td', 'th', 'tr')}
colors = {'Black': '#000000',
 'Green': '#008000',
 'Silver': '#C0C0C0',
 'Lime': '#00FF00',
 'Gray': '#808080',
 'Olive': '#808000',
 'White': '#FFFFFF',
 'Yellow': '#FFFF00',
 'Maroon': '#800000',
 'Navy': '#000080',
 'Red': '#FF0000',
 'Blue': '#0000FF',
 'Purple': '#800080',
 'Teal': '#008080',
 'Fuchsia': '#FF00FF',
 'Aqua': '#00FFFF'}
entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')

class Parser(hparser.HtmlScraper):
    __guid__ = 'parser.Html'

    def __init__(self, handler):
        self.__handler = _weakref.proxy(handler)

    def handletag(self, tag, attrs, thetag):
        tag = tag.lower()
        d = {}
        for name, val in attrs:
            d[str(name)] = val

        attrs = globals().get('Tag_%s' % tag, Tag)(**d)
        if self.__handler.destroyed:
            return
        self.__handler.OnStartTag(tag, attrs)
        return ''

    def emptytag(self, tag):
        self.handletag(tag, [], tag)

    def endtag(self, tag):
        tag = tag.lower()
        tag = tag[1:]
        if self.__handler.destroyed:
            return
        self.__handler.OnEndTag(tag)
        return ''

    def pdata(self, data):
        if hasattr(self.__handler, 'OnData'):
            self.__handler.OnData(self.decode_string(data))
        return ''

    def pdecl(self, tag):
        return ''

    def decode_string(self, data):
        if type(data) == types.StringType:
            data = data.decode(self.__handler.charset, 'replace')
        i = 0
        s = data.split(u'&')
        ndata = [s[0]]
        for chunk in s[1:]:
            name = None
            k = 0
            match = charref.match(u'&' + chunk, 0)
            if match:
                name = match.group()[2:-1]
            else:
                match = entityref.match(u'&' + chunk, 0)
                if match:
                    name = match.group(1)
            if name:
                t = self.handle_charref(name)
                k = match.end()
                if not chunk.startswith(u';', k - 1):
                    k = k - 1
                ndata.append(t)
            else:
                ndata.append(u'&')
            ndata.append(chunk[k:])

        return u''.join(ndata)

    def handle_charref(self, name):
        code = htmlentitydefs.name2codepoint.get(name, None)
        if code:
            return unichr(code)
        if name.startswith('x'):
            try:
                return unichr(int('0' + name, 16))
            except:
                sys.exc_clear()

        elif name.isdigit():
            try:
                return unichr(int(name))
            except:
                sys.exc_clear()

        return name

    handle_entityref = handle_charref


class Tag:

    def __init__(self, **attrs):
        self.__dict__.update(attrs)

    def SetDefault(self, *attrs):
        for name in attrs:
            setattr(self, name, getattr(self, name, None))

    def SetBoolean(self, *attrs):
        for each in attrs:
            setattr(self, each, hasattr(self, each))

    def Get(self, attr, default):
        return self.__dict__.get(attr, default)


class Tag_img(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.src = getattr(self, 'src', None)
        self.SetDefault('alt', 'align', 'width', 'height', 'border', 'bordercolor', 'hspace', 'vspace', 'usemap')
        if hasattr(self, 'size'):
            self.size = int(self.size)


class Tag_a(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('href', 'alt')


class Tag_body(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('background', 'bgcolor', 'text', 'link', 'vlink', 'alink', 'style')


class Tag_form(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('method', 'action')
        if self.method is None:
            self.method = 'get'


class Tag_input(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.size = int(getattr(self, 'size', None) or 0)
        self.SetDefault('type', 'name', 'value', 'valign')


class Tag_textarea(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        try:
            self.rows = int(getattr(self, 'rows', None) or 0)
            self.cols = int(getattr(self, 'cols', None) or 0)
        except ValueError:
            raise RuntimeError('ParsingError', {'what': 'TextArea %s has uninitialized or bad rows or cols.' % getattr(self, 'name', '[Unnamed]')})

        self.SetDefault('name', 'value')


class Tag_div(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align', 'height', 'width', 'border', 'bordercolor', 'background', 'bgcolor')


class Tag_select(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('name')


class Tag_option(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetBoolean('selected')
        self.SetDefault('value')


class Tag_hr(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('size', 'color', 'width', 'align')


class Tag_table(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align', 'width', 'height', 'border', 'bordercolor', 'background', 'bgcolor', 'cellspacing', 'cellpadding', 'vspace', 'hspace')


class Tag_colgroup(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('width', 'span')


class Tag_col(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('width', 'span')


class Tag_td(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align', 'valign', 'width', 'rowspan', 'colspan', 'nowrap', 'background', 'bgcolor')


class Tag_th(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align', 'valign', 'width', 'rowspan', 'colspan', 'nowrap', 'background', 'bgcolor')


class Tag_tr(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align', 'valign', 'height', 'background', 'bgcolor')


class Tag_h1(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_h2(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_h3(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_h4(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_h5(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_h6(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('align')


class Tag_font(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('size', 'color', 'style')


class Tag_span(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('style')


class Tag_link(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('rel', 'type', 'href')


class Tag_map(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('name')


class Tag_area(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('shape', 'coords', 'href')


class Tag_meta(Tag):

    def __init__(self, **attrs):
        Tag.__init__(self, **attrs)
        self.SetDefault('content')


parseErrorMsg = '\n    <html><body>\n    <h1>Unsupported Format</h1>\n    <p>This page is not suitable for displaying.</p>\n    <p>%s.</p>\n    <p>line %s, offset %s.</p>\n    </body></html>\n    '
exports = {'parser.HtmlSupportedTags': supportedTags,
 'parser.HtmlIgnoredTags': ignoredTags,
 'parser.HtmlAutoClose': autoClose,
 'parser.HtmlOptionalClose': optionalClose,
 'parser.HtmlColors': colors,
 'parser.ErrorMsg': parseErrorMsg,
 'html.ALIGNBASELINE': 0,
 'html.ALIGNTOP': 1,
 'html.ALIGNMIDDLE': 2,
 'html.ALIGNBOTTOM': 3,
 'html.ALIGNSUB': 4,
 'html.ALIGNSUPER': 5,
 'html.BG_TILED': 0,
 'html.BG_SCROLL': 1,
 'html.BG_FIXED': 2}