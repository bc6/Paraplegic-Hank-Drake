#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/cookieManager.py
import Cookie
import urlparse
import blue
import log
import re
ip = re.compile('[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+')

class CookieManager:
    __guid__ = 'corebrowserutil.CookieManager'

    def __init__(self):
        self.cookies = []

    def ProcessCookies(self, httpResponse):
        host, path = urlparse.urlsplit(httpResponse.url.encode('ascii'))[1:3]
        for each in httpResponse.info().headers:
            if not each.lower().startswith('set-cookie:'):
                continue
            raw = each[len('set-cookie:'):]
            cookie = Cookie.SimpleCookie(raw)
            for morsel in cookie.values():
                for oldmorsel in self.cookies[:]:
                    if morsel.key == oldmorsel.key and (morsel['domain'] or host == oldmorsel['domain'] or oldmorsel.__host) and morsel['path'] == oldmorsel['path']:
                        self.cookies.remove(oldmorsel)

                if morsel['max-age'] == '0':
                    continue
                if not morsel['path'] or not path.startswith(morsel['path']):
                    log.LogWarn('browser', 'No proper path; rejecting cookie:', morsel.output(header=''))
                    continue
                if morsel['domain']:
                    if not morsel['domain'].startswith('.'):
                        log.LogWarn('browser', "Domain doesn't begin with a dot; rejecting cookie:", morsel.output(header=''))
                        continue
                    if morsel['domain'][1:-1].find('.') == -1:
                        log.LogWarn('browser', 'Domain contains no embedded dots; rejecting cookie:', morsel.output(header=''))
                        continue
                    if not self.DomainMatches(host, morsel['domain']):
                        log.LogWarn('browser', "Response-host doesn't match domain; rejecting cookie:", morsel.output(header=''))
                        continue
                    if not ip.match(host) and host[:-len(morsel['domain'])].find('.') != -1:
                        log.LogWarn('browser', 'HD case; rejecting cookie:', morsel.output(header=''))
                        continue
                morsel.__host = host
                morsel.__time = blue.os.GetWallclockTime()
                self.cookies.append(morsel)

    def GetCookie(self, url):
        url = url.encode('ascii')
        morsels = []
        host, path = urlparse.urlsplit(url)[1:3]
        for morsel in self.cookies[:]:
            if morsel['max-age'] and blue.os.TimeDiffInMs(morsel.__time) / 1000 > morsel['max-age']:
                self.cookies.remove(morsel)
                continue
            if not self.DomainMatches(host, morsel['domain'] or morsel.__host):
                continue
            if not path.startswith(morsel['path']):
                continue
            morsels.append(morsel)

        morsels.sort(lambda a, b: cmp(len(a['path'] or ''), len(b['path'] or '')))
        morsels.reverse()
        parts = []
        for morsel in morsels:
            s = '%s=%s' % (morsel.key, morsel.coded_value)
            if morsel['path']:
                s = '%s;$Path=%s' % (s, morsel['path'])
            if morsel['domain']:
                s = '%s;$Domain=%s' % (s, morsel['domain'])
            parts.append(s)

        if parts:
            return '$Version=%s;%s' % (min([ each['version'] and int(each['version']) or 0 for each in morsels ]), ';'.join(parts))
        else:
            return None

    def DomainMatches(self, d1, d2):
        if d2.startswith('.'):
            return d1.endswith(d2) and d1 != d2
        else:
            return d1 == d2