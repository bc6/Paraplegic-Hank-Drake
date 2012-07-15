#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\useragents.py
import re

class UserAgentParser(object):
    platforms = (('iphone', 'iphone'),
     ('darwin|mac|os\\s*x', 'macos'),
     ('win', 'windows'),
     ('android', 'android'),
     ('x11|lin(\\b|ux)?', 'linux'),
     ('(sun|i86)os', 'solaris'),
     ('nintendo\\s+wii', 'wii'),
     ('irix', 'irix'),
     ('hp-?ux', 'hpux'),
     ('aix', 'aix'),
     ('sco|unix_sv', 'sco'),
     ('bsd', 'bsd'),
     ('amiga', 'amiga'))
    browsers = (('googlebot', 'google'),
     ('msnbot', 'msn'),
     ('yahoo', 'yahoo'),
     ('ask jeeves', 'ask'),
     ('aol|america\\s+online\\s+browser', 'aol'),
     ('opera', 'opera'),
     ('chrome', 'chrome'),
     ('firefox|firebird|phoenix|iceweasel', 'firefox'),
     ('galeon', 'galeon'),
     ('safari', 'safari'),
     ('webkit', 'webkit'),
     ('camino', 'camino'),
     ('konqueror', 'konqueror'),
     ('k-meleon', 'kmeleon'),
     ('netscape', 'netscape'),
     ('msie|microsoft\\s+internet\\s+explorer', 'msie'),
     ('lynx', 'lynx'),
     ('links', 'links'),
     ('seamonkey|mozilla', 'seamonkey'))
    _browser_version_re = '(?:%s)[/\\sa-z(]*(\\d+[.\\da-z]+)?(?i)'
    _language_re = re.compile('(?:;\\s*|\\s+)(\\b\\w{2}\\b(?:-\\b\\w{2}\\b)?)\\s*;|(?:\\(|\\[|;)\\s*(\\b\\w{2}\\b(?:-\\b\\w{2}\\b)?)\\s*(?:\\]|\\)|;)')

    def __init__(self):
        self.platforms = [ (b, re.compile(a, re.I)) for a, b in self.platforms ]
        self.browsers = [ (b, re.compile(self._browser_version_re % a)) for a, b in self.browsers ]

    def __call__(self, user_agent):
        for platform, regex in self.platforms:
            match = regex.search(user_agent)
            if match is not None:
                break
        else:
            platform = None

        for browser, regex in self.browsers:
            match = regex.search(user_agent)
            if match is not None:
                version = match.group(1)
                break
        else:
            browser = version = None

        match = self._language_re.search(user_agent)
        if match is not None:
            language = match.group(1) or match.group(2)
        else:
            language = None
        return (platform,
         browser,
         version,
         language)


class UserAgent(object):
    _parser = UserAgentParser()

    def __init__(self, environ_or_string):
        if isinstance(environ_or_string, dict):
            environ_or_string = environ_or_string.get('HTTP_USER_AGENT', '')
        self.string = environ_or_string
        self.platform, self.browser, self.version, self.language = self._parser(environ_or_string)

    def to_header(self):
        return self.string

    def __str__(self):
        return self.string

    def __nonzero__(self):
        return bool(self.browser)

    def __repr__(self):
        return '<%s %r/%s>' % (self.__class__.__name__, self.browser, self.version)


from werkzeug.wrappers import UserAgentMixin