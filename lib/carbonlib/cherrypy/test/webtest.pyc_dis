#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\webtest.py
import os
import pprint
import re
import socket
import sys
import time
import traceback
import types
from unittest import *
from unittest import _TextTestResult
from cherrypy._cpcompat import basestring, HTTPConnection, HTTPSConnection, unicodestr

def interface(host):
    if host == '0.0.0.0':
        return '127.0.0.1'
    if host == '::':
        return '::1'
    return host


class TerseTestResult(_TextTestResult):

    def printErrors(self):
        if self.errors or self.failures:
            if self.dots or self.showAll:
                self.stream.writeln()
            self.printErrorList('ERROR', self.errors)
            self.printErrorList('FAIL', self.failures)


class TerseTestRunner(TextTestRunner):

    def _makeResult(self):
        return TerseTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        result = self._makeResult()
        test(result)
        result.printErrors()
        if not result.wasSuccessful():
            self.stream.write('FAILED (')
            failed, errored = list(map(len, (result.failures, result.errors)))
            if failed:
                self.stream.write('failures=%d' % failed)
            if errored:
                if failed:
                    self.stream.write(', ')
                self.stream.write('errors=%d' % errored)
            self.stream.writeln(')')
        return result


class ReloadingTestLoader(TestLoader):

    def loadTestsFromName(self, name, module = None):
        parts = name.split('.')
        unused_parts = []
        if module is None:
            if not parts:
                raise ValueError('incomplete test name: %s' % name)
            else:
                parts_copy = parts[:]
                while parts_copy:
                    target = '.'.join(parts_copy)
                    if target in sys.modules:
                        module = reload(sys.modules[target])
                        parts = unused_parts
                        break
                    else:
                        try:
                            module = __import__(target)
                            parts = unused_parts
                            break
                        except ImportError:
                            unused_parts.insert(0, parts_copy[-1])
                            del parts_copy[-1]
                            if not parts_copy:
                                raise 

                parts = parts[1:]
        obj = module
        for part in parts:
            obj = getattr(obj, part)

        if type(obj) == types.ModuleType:
            return self.loadTestsFromModule(obj)
        if isinstance(obj, (type, types.ClassType)) and issubclass(obj, TestCase):
            return self.loadTestsFromTestCase(obj)
        if type(obj) == types.UnboundMethodType:
            return obj.im_class(obj.__name__)
        if hasattr(obj, '__call__'):
            test = obj()
            if not isinstance(test, TestCase) and not isinstance(test, TestSuite):
                raise ValueError('calling %s returned %s, not a test' % (obj, test))
            return test
        raise ValueError('do not know how to make test from: %s' % obj)


try:
    if sys.platform[:4] == 'java':

        def getchar():
            return sys.stdin.read(1)


    else:
        import msvcrt

        def getchar():
            return msvcrt.getch()


except ImportError:
    import tty, termios

    def getchar():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


class WebCase(TestCase):
    HOST = '127.0.0.1'
    PORT = 8000
    HTTP_CONN = HTTPConnection
    PROTOCOL = 'HTTP/1.1'
    scheme = 'http'
    url = None
    status = None
    headers = None
    body = None
    encoding = 'utf-8'
    time = None

    def get_conn(self, auto_open = False):
        if self.scheme == 'https':
            cls = HTTPSConnection
        else:
            cls = HTTPConnection
        conn = cls(self.interface(), self.PORT)
        conn.auto_open = auto_open
        conn.connect()
        return conn

    def set_persistent(self, on = True, auto_open = False):
        try:
            self.HTTP_CONN.close()
        except (TypeError, AttributeError):
            pass

        if on:
            self.HTTP_CONN = self.get_conn(auto_open=auto_open)
        elif self.scheme == 'https':
            self.HTTP_CONN = HTTPSConnection
        else:
            self.HTTP_CONN = HTTPConnection

    def _get_persistent(self):
        return hasattr(self.HTTP_CONN, '__class__')

    def _set_persistent(self, on):
        self.set_persistent(on)

    persistent = property(_get_persistent, _set_persistent)

    def interface(self):
        return interface(self.HOST)

    def getPage(self, url, headers = None, method = 'GET', body = None, protocol = None):
        ServerError.on = False
        if isinstance(url, unicodestr):
            url = url.encode('utf-8')
        if isinstance(body, unicodestr):
            body = body.encode('utf-8')
        self.url = url
        self.time = None
        start = time.time()
        result = openURL(url, headers, method, body, self.HOST, self.PORT, self.HTTP_CONN, protocol or self.PROTOCOL)
        self.time = time.time() - start
        self.status, self.headers, self.body = result
        self.cookies = [ ('Cookie', v) for k, v in self.headers if k.lower() == 'set-cookie' ]
        if ServerError.on:
            raise ServerError()
        return result

    interactive = True
    console_height = 30

    def _handlewebError(self, msg):
        print ''
        print '    ERROR: %s' % msg
        if not self.interactive:
            raise self.failureException(msg)
        p = '    Show: [B]ody [H]eaders [S]tatus [U]RL; [I]gnore, [R]aise, or sys.e[X]it >> '
        sys.stdout.write(p)
        sys.stdout.flush()
        while True:
            i = getchar().upper()
            if i not in 'BHSUIRX':
                continue
            print i.upper()
            if i == 'B':
                for x, line in enumerate(self.body.splitlines()):
                    if (x + 1) % self.console_height == 0:
                        sys.stdout.write('<-- More -->\r')
                        m = getchar().lower()
                        sys.stdout.write('            \r')
                        if m == 'q':
                            break
                    print line

            elif i == 'H':
                pprint.pprint(self.headers)
            elif i == 'S':
                print self.status
            elif i == 'U':
                print self.url
            else:
                if i == 'I':
                    return
                if i == 'R':
                    raise self.failureException(msg)
                elif i == 'X':
                    self.exit()
            sys.stdout.write(p)
            sys.stdout.flush()

    def exit(self):
        sys.exit()

    def assertStatus(self, status, msg = None):
        if isinstance(status, basestring):
            if not self.status == status:
                if msg is None:
                    msg = 'Status (%r) != %r' % (self.status, status)
                self._handlewebError(msg)
        elif isinstance(status, int):
            code = int(self.status[:3])
            if code != status:
                if msg is None:
                    msg = 'Status (%r) != %r' % (self.status, status)
                self._handlewebError(msg)
        else:
            match = False
            for s in status:
                if isinstance(s, basestring):
                    if self.status == s:
                        match = True
                        break
                elif int(self.status[:3]) == s:
                    match = True
                    break

            if not match:
                if msg is None:
                    msg = 'Status (%r) not in %r' % (self.status, status)
                self._handlewebError(msg)

    def assertHeader(self, key, value = None, msg = None):
        lowkey = key.lower()
        for k, v in self.headers:
            if k.lower() == lowkey:
                if value is None or str(value) == v:
                    return v

        if msg is None:
            if value is None:
                msg = '%r not in headers' % key
            else:
                msg = '%r:%r not in headers' % (key, value)
        self._handlewebError(msg)

    def assertHeaderItemValue(self, key, value, msg = None):
        actual_value = self.assertHeader(key, msg=msg)
        header_values = map(str.strip, actual_value.split(','))
        if value in header_values:
            return value
        if msg is None:
            msg = '%r not in %r' % (value, header_values)
        self._handlewebError(msg)

    def assertNoHeader(self, key, msg = None):
        lowkey = key.lower()
        matches = [ k for k, v in self.headers if k.lower() == lowkey ]
        if matches:
            if msg is None:
                msg = '%r in headers' % key
            self._handlewebError(msg)

    def assertBody(self, value, msg = None):
        if value != self.body:
            if msg is None:
                msg = 'expected body:\n%r\n\nactual body:\n%r' % (value, self.body)
            self._handlewebError(msg)

    def assertInBody(self, value, msg = None):
        if value not in self.body:
            if msg is None:
                msg = '%r not in body: %s' % (value, self.body)
            self._handlewebError(msg)

    def assertNotInBody(self, value, msg = None):
        if value in self.body:
            if msg is None:
                msg = '%r found in body' % value
            self._handlewebError(msg)

    def assertMatchesBody(self, pattern, msg = None, flags = 0):
        if re.search(pattern, self.body, flags) is None:
            if msg is None:
                msg = 'No match for %r in body' % pattern
            self._handlewebError(msg)


methods_with_bodies = ('POST', 'PUT')

def cleanHeaders(headers, method, body, host, port):
    if headers is None:
        headers = []
    found = False
    for k, v in headers:
        if k.lower() == 'host':
            found = True
            break

    if not found:
        if port == 80:
            headers.append(('Host', host))
        else:
            headers.append(('Host', '%s:%s' % (host, port)))
    if method in methods_with_bodies:
        found = False
        for k, v in headers:
            if k.lower() == 'content-type':
                found = True
                break

        if not found:
            headers.append(('Content-Type', 'application/x-www-form-urlencoded'))
            headers.append(('Content-Length', str(len(body or ''))))
    return headers


def shb(response):
    h = []
    key, value = (None, None)
    for line in response.msg.headers:
        if line:
            if line[0] in ' \t':
                value += line.strip()
            else:
                if key and value:
                    h.append((key, value))
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

    if key and value:
        h.append((key, value))
    return ('%s %s' % (response.status, response.reason), h, response.read())


def openURL(url, headers = None, method = 'GET', body = None, host = '127.0.0.1', port = 8000, http_conn = HTTPConnection, protocol = 'HTTP/1.1'):
    headers = cleanHeaders(headers, method, body, host, port)
    for trial in range(10):
        try:
            if hasattr(http_conn, 'host'):
                conn = http_conn
            else:
                conn = http_conn(interface(host), port)
            conn._http_vsn_str = protocol
            conn._http_vsn = int(''.join([ x for x in protocol if x.isdigit() ]))
            if sys.version_info < (2, 4):

                def putheader(self, header, value):
                    if header == 'Accept-Encoding' and value == 'identity':
                        return
                    self.__class__.putheader(self, header, value)

                import new
                conn.putheader = new.instancemethod(putheader, conn, conn.__class__)
                conn.putrequest(method.upper(), url, skip_host=True)
            else:
                conn.putrequest(method.upper(), url, skip_host=True, skip_accept_encoding=True)
            for key, value in headers:
                conn.putheader(key, value)

            conn.endheaders()
            if body is not None:
                conn.send(body)
            response = conn.getresponse()
            s, h, b = shb(response)
            if not hasattr(http_conn, 'host'):
                conn.close()
            return (s, h, b)
        except socket.error:
            time.sleep(0.5)

    raise 


ignored_exceptions = []
ignore_all = False

class ServerError(Exception):
    on = False


def server_error(exc = None):
    if exc is None:
        exc = sys.exc_info()
    if ignore_all or exc[0] in ignored_exceptions:
        return False
    else:
        ServerError.on = True
        print ''
        print ''.join(traceback.format_exception(*exc))
        return True