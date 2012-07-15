#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\_markupsafe\_native.py
from jinja2._markupsafe import Markup

def escape(s):
    if hasattr(s, '__html__'):
        return s.__html__()
    return Markup(unicode(s).replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace("'", '&#39;').replace('"', '&#34;'))


def escape_silent(s):
    if s is None:
        return Markup()
    return escape(s)


def soft_unicode(s):
    if not isinstance(s, unicode):
        s = unicode(s)
    return s