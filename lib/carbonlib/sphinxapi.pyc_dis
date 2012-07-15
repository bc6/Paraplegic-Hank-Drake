#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\sphinxapi.py
import sys
import socket
import re
import util
from struct import *
SEARCHD_COMMAND_SEARCH = 0
SEARCHD_COMMAND_EXCERPT = 1
SEARCHD_COMMAND_UPDATE = 2
SEARCHD_COMMAND_KEYWORDS = 3
SEARCHD_COMMAND_PERSIST = 4
SEARCHD_COMMAND_STATUS = 5
SEARCHD_COMMAND_FLUSHATTRS = 7
VER_COMMAND_SEARCH = 281
VER_COMMAND_EXCERPT = 260
VER_COMMAND_UPDATE = 258
VER_COMMAND_KEYWORDS = 256
VER_COMMAND_STATUS = 256
VER_COMMAND_FLUSHATTRS = 256
SEARCHD_OK = 0
SEARCHD_ERROR = 1
SEARCHD_RETRY = 2
SEARCHD_WARNING = 3
SPH_MATCH_ALL = 0
SPH_MATCH_ANY = 1
SPH_MATCH_PHRASE = 2
SPH_MATCH_BOOLEAN = 3
SPH_MATCH_EXTENDED = 4
SPH_MATCH_FULLSCAN = 5
SPH_MATCH_EXTENDED2 = 6
SPH_RANK_PROXIMITY_BM25 = 0
SPH_RANK_BM25 = 1
SPH_RANK_NONE = 2
SPH_RANK_WORDCOUNT = 3
SPH_RANK_PROXIMITY = 4
SPH_RANK_MATCHANY = 5
SPH_RANK_FIELDMASK = 6
SPH_RANK_SPH04 = 7
SPH_RANK_EXPR = 8
SPH_RANK_TOTAL = 9
SPH_SORT_RELEVANCE = 0
SPH_SORT_ATTR_DESC = 1
SPH_SORT_ATTR_ASC = 2
SPH_SORT_TIME_SEGMENTS = 3
SPH_SORT_EXTENDED = 4
SPH_SORT_EXPR = 5
SPH_FILTER_VALUES = 0
SPH_FILTER_RANGE = 1
SPH_FILTER_FLOATRANGE = 2
SPH_ATTR_NONE = 0
SPH_ATTR_INTEGER = 1
SPH_ATTR_TIMESTAMP = 2
SPH_ATTR_ORDINAL = 3
SPH_ATTR_BOOL = 4
SPH_ATTR_FLOAT = 5
SPH_ATTR_BIGINT = 6
SPH_ATTR_STRING = 7
SPH_ATTR_MULTI = 1073741825L
SPH_ATTR_MULTI64 = 1073741826L
SPH_ATTR_TYPES = (SPH_ATTR_NONE,
 SPH_ATTR_INTEGER,
 SPH_ATTR_TIMESTAMP,
 SPH_ATTR_ORDINAL,
 SPH_ATTR_BOOL,
 SPH_ATTR_FLOAT,
 SPH_ATTR_BIGINT,
 SPH_ATTR_STRING,
 SPH_ATTR_MULTI,
 SPH_ATTR_MULTI64)
SPH_GROUPBY_DAY = 0
SPH_GROUPBY_WEEK = 1
SPH_GROUPBY_MONTH = 2
SPH_GROUPBY_YEAR = 3
SPH_GROUPBY_ATTR = 4
SPH_GROUPBY_ATTRPAIR = 5

class SphinxClient():

    def __init__(self):
        self._host = 'localhost'
        self._port = 9312
        self._path = None
        self._socket = None
        self._offset = 0
        self._limit = 20
        self._mode = SPH_MATCH_EXTENDED2
        self._weights = []
        self._sort = SPH_SORT_RELEVANCE
        self._sortby = ''
        self._min_id = 0
        self._max_id = 0
        self._filters = []
        self._groupby = ''
        self._groupfunc = SPH_GROUPBY_DAY
        self._groupsort = '@group desc'
        self._groupdistinct = ''
        self._maxmatches = 100
        self._cutoff = 0
        self._retrycount = 0
        self._retrydelay = 0
        self._anchor = {}
        self._indexweights = {}
        self._ranker = SPH_RANK_PROXIMITY_BM25
        self._rankexpr = ''
        self._maxquerytime = 0
        self._timeout = 1.0
        self._fieldweights = {}
        self._overrides = {}
        self._select = '*'
        self._error = ''
        self._warning = ''
        self._reqs = []

    def __del__(self):
        if self._socket:
            self._socket.close()

    def GetLastError(self):
        return self._error

    def GetLastWarning(self):
        return self._warning

    def SetServer(self, host, port = None):
        if host.startswith('/'):
            self._path = host
            return
        if host.startswith('unix://'):
            self._path = host[7:]
            return
        self._host = host
        self._port = port
        self._path = None

    def SetConnectTimeout(self, timeout):
        self._timeout = max(0.001, timeout)

    def _Connect(self):
        if self._socket:
            self._socket.close()
            self._socket = None
        try:
            if self._path:
                af = socket.AF_UNIX
                addr = self._path
                desc = self._path
            else:
                af = socket.AF_INET
                addr = (self._host, self._port)
                desc = '%s;%s' % addr
            sock = socket.socket(af, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect(addr)
        except socket.error as msg:
            if sock:
                sock.close()
            self._error = 'connection to %s failed (%s)' % (desc, msg)
            return

        v = unpack('>L', sock.recv(4))
        if v < 1:
            sock.close()
            self._error = 'expected searchd protocol version, got %s' % v
            return
        sock.send(pack('>L', 1))
        return sock

    def _GetResponse(self, sock, client_ver):
        status, ver, length = unpack('>2HL', sock.recv(8))
        response = ''
        left = length
        while left > 0:
            chunk = sock.recv(left)
            if chunk:
                response += chunk
                left -= len(chunk)
            else:
                break

        if not self._socket:
            sock.close()
        read = len(response)
        if not response or read != length:
            if length:
                self._error = 'failed to read searchd response (status=%s, ver=%s, len=%s, read=%s)' % (status,
                 ver,
                 length,
                 read)
            else:
                self._error = 'received zero-sized searchd response'
            return None
        if status == SEARCHD_WARNING:
            wend = 4 + unpack('>L', response[0:4])[0]
            self._warning = response[4:wend]
            return response[wend:]
        if status == SEARCHD_ERROR:
            self._error = 'searchd error: ' + response[4:]
            return None
        if status == SEARCHD_RETRY:
            self._error = 'temporary searchd error: ' + response[4:]
            return None
        if status != SEARCHD_OK:
            self._error = 'unknown status code %d' % status
            return None
        if ver < client_ver:
            self._warning = "searchd command v.%d.%d older than client's v.%d.%d, some options might not work" % (ver >> 8,
             ver & 255,
             client_ver >> 8,
             client_ver & 255)
        return response

    def SetLimits(self, offset, limit, maxmatches = 0, cutoff = 0):
        self._offset = offset
        self._limit = limit
        if maxmatches > 0:
            self._maxmatches = maxmatches
        if cutoff >= 0:
            self._cutoff = cutoff

    def SetMaxQueryTime(self, maxquerytime):
        self._maxquerytime = maxquerytime

    def SetMatchMode(self, mode):
        self._mode = mode

    def SetRankingMode(self, ranker, rankexpr = ''):
        self._ranker = ranker
        self._rankexpr = rankexpr

    def SetSortMode(self, mode, clause = ''):
        self._sort = mode
        self._sortby = clause

    def SetWeights(self, weights):
        for w in weights:
            AssertUInt32(w)

        self._weights = weights

    def SetFieldWeights(self, weights):
        for key, val in weights.items():
            AssertUInt32(val)

        self._fieldweights = weights

    def SetIndexWeights(self, weights):
        for key, val in weights.items():
            AssertUInt32(val)

        self._indexweights = weights

    def SetIDRange(self, minid, maxid):
        self._min_id = minid
        self._max_id = maxid

    def SetFilter(self, attribute, values, exclude = 0):
        for value in values:
            AssertInt32(value)

        self._filters.append({'type': SPH_FILTER_VALUES,
         'attr': attribute,
         'exclude': exclude,
         'values': values})

    def SetFilterRange(self, attribute, min_, max_, exclude = 0):
        AssertInt32(min_)
        AssertInt32(max_)
        self._filters.append({'type': SPH_FILTER_RANGE,
         'attr': attribute,
         'exclude': exclude,
         'min': min_,
         'max': max_})

    def SetFilterFloatRange(self, attribute, min_, max_, exclude = 0):
        self._filters.append({'type': SPH_FILTER_FLOATRANGE,
         'attr': attribute,
         'exclude': exclude,
         'min': min_,
         'max': max_})

    def SetGeoAnchor(self, attrlat, attrlong, latitude, longitude):
        self._anchor['attrlat'] = attrlat
        self._anchor['attrlong'] = attrlong
        self._anchor['lat'] = latitude
        self._anchor['long'] = longitude

    def SetGroupBy(self, attribute, func, groupsort = '@group desc'):
        self._groupby = attribute
        self._groupfunc = func
        self._groupsort = groupsort

    def SetGroupDistinct(self, attribute):
        self._groupdistinct = attribute

    def SetRetries(self, count, delay = 0):
        self._retrycount = count
        self._retrydelay = delay

    def SetOverride(self, name, type, values):
        self._overrides[name] = {'name': name,
         'type': type,
         'values': values}

    def SetSelect(self, select):
        self._select = select

    def ResetOverrides(self):
        self._overrides = {}

    def ResetFilters(self):
        self._filters = []
        self._anchor = {}

    def ResetGroupBy(self):
        self._groupby = ''
        self._groupfunc = SPH_GROUPBY_DAY
        self._groupsort = '@group desc'
        self._groupdistinct = ''

    def Query(self, query, index = '*', comment = ''):
        self.AddQuery(query, index, comment)
        results = self.RunQueries()
        self._reqs = []
        if not results or len(results) == 0:
            return None
        self._error = results[0]['error']
        self._warning = results[0]['warning']
        if results[0]['status'] == SEARCHD_ERROR:
            return None
        return results[0]

    def AddQuery(self, query, index = '*', comment = ''):
        req = []
        req.append(pack('>4L', self._offset, self._limit, self._mode, self._ranker))
        if self._ranker == SPH_RANK_EXPR:
            req.append(pack('>L', len(self._rankexpr)))
            req.append(self._rankexpr)
        req.append(pack('>L', self._sort))
        req.append(pack('>L', len(self._sortby)))
        req.append(self._sortby)
        if isinstance(query, unicode):
            query = query.encode('utf-8')
        req.append(pack('>L', len(query)))
        req.append(query)
        req.append(pack('>L', len(self._weights)))
        for w in self._weights:
            req.append(pack('>L', w))

        req.append(pack('>L', len(index)))
        req.append(index)
        req.append(pack('>L', 1))
        req.append(pack('>Q', self._min_id))
        req.append(pack('>Q', self._max_id))
        req.append(pack('>L', len(self._filters)))
        for f in self._filters:
            req.append(pack('>L', len(f['attr'])) + f['attr'])
            filtertype = f['type']
            req.append(pack('>L', filtertype))
            if filtertype == SPH_FILTER_VALUES:
                req.append(pack('>L', len(f['values'])))
                for val in f['values']:
                    req.append(pack('>q', val))

            elif filtertype == SPH_FILTER_RANGE:
                req.append(pack('>2q', f['min'], f['max']))
            elif filtertype == SPH_FILTER_FLOATRANGE:
                req.append(pack('>2f', f['min'], f['max']))
            req.append(pack('>L', f['exclude']))

        req.append(pack('>2L', self._groupfunc, len(self._groupby)))
        req.append(self._groupby)
        req.append(pack('>2L', self._maxmatches, len(self._groupsort)))
        req.append(self._groupsort)
        req.append(pack('>LLL', self._cutoff, self._retrycount, self._retrydelay))
        req.append(pack('>L', len(self._groupdistinct)))
        req.append(self._groupdistinct)
        if len(self._anchor) == 0:
            req.append(pack('>L', 0))
        else:
            attrlat, attrlong = self._anchor['attrlat'], self._anchor['attrlong']
            latitude, longitude = self._anchor['lat'], self._anchor['long']
            req.append(pack('>L', 1))
            req.append(pack('>L', len(attrlat)) + attrlat)
            req.append(pack('>L', len(attrlong)) + attrlong)
            req.append(pack('>f', latitude) + pack('>f', longitude))
        req.append(pack('>L', len(self._indexweights)))
        for indx, weight in self._indexweights.items():
            req.append(pack('>L', len(indx)) + indx + pack('>L', weight))

        req.append(pack('>L', self._maxquerytime))
        req.append(pack('>L', len(self._fieldweights)))
        for field, weight in self._fieldweights.items():
            req.append(pack('>L', len(field)) + field + pack('>L', weight))

        req.append(pack('>L', len(comment)) + comment)
        req.append(pack('>L', len(self._overrides)))
        for v in self._overrides.values():
            req.extend((pack('>L', len(v['name'])), v['name']))
            req.append(pack('>LL', v['type'], len(v['values'])))
            for id, value in v['values'].iteritems():
                req.append(pack('>Q', id))
                if v['type'] == SPH_ATTR_FLOAT:
                    req.append(pack('>f', value))
                elif v['type'] == SPH_ATTR_BIGINT:
                    req.append(pack('>q', value))
                else:
                    req.append(pack('>l', value))

        req.append(pack('>L', len(self._select)))
        req.append(self._select)
        req = ''.join(req)
        self._reqs.append(req)

    def RunQueries(self):
        if len(self._reqs) == 0:
            self._error = 'no queries defined, issue AddQuery() first'
            return None
        sock = self._Connect()
        if not sock:
            return None
        req = ''.join(self._reqs)
        length = len(req) + 8
        req = pack('>HHLLL', SEARCHD_COMMAND_SEARCH, VER_COMMAND_SEARCH, length, 0, len(self._reqs)) + req
        sock.send(req)
        response = self._GetResponse(sock, VER_COMMAND_SEARCH)
        if not response:
            return None
        nreqs = len(self._reqs)
        max_ = len(response)
        p = 0
        results = []
        for i in range(0, nreqs, 1):
            result = {}
            results.append(result)
            result['error'] = ''
            result['warning'] = ''
            status = unpack('>L', response[p:p + 4])[0]
            p += 4
            result['status'] = status
            if status != SEARCHD_OK:
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                message = response[p:p + length]
                p += length
                if status == SEARCHD_WARNING:
                    result['warning'] = message
                else:
                    result['error'] = message
                    continue
            fields = []
            attrs = []
            nfields = unpack('>L', response[p:p + 4])[0]
            p += 4
            while nfields > 0 and p < max_:
                nfields -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                fields.append(response[p:p + length])
                p += length

            result['fields'] = fields
            nattrs = unpack('>L', response[p:p + 4])[0]
            p += 4
            while nattrs > 0 and p < max_:
                nattrs -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                attr = response[p:p + length]
                p += length
                type_ = unpack('>L', response[p:p + 4])[0]
                p += 4
                attrs.append([attr, type_])

            result['attrs'] = attrs
            count = unpack('>L', response[p:p + 4])[0]
            p += 4
            id64 = unpack('>L', response[p:p + 4])[0]
            p += 4
            result['matches'] = []
            while count > 0 and p < max_:
                count -= 1
                if id64:
                    doc, weight = unpack('>QL', response[p:p + 12])
                    p += 12
                else:
                    doc, weight = unpack('>2L', response[p:p + 8])
                    p += 8
                match = {'id': doc,
                 'weight': weight,
                 'attrs': {}}
                for i in range(len(attrs)):
                    if attrs[i][1] == SPH_ATTR_FLOAT:
                        match['attrs'][attrs[i][0]] = unpack('>f', response[p:p + 4])[0]
                    elif attrs[i][1] == SPH_ATTR_BIGINT:
                        match['attrs'][attrs[i][0]] = unpack('>q', response[p:p + 8])[0]
                        p += 4
                    elif attrs[i][1] == SPH_ATTR_STRING:
                        slen = unpack('>L', response[p:p + 4])[0]
                        p += 4
                        match['attrs'][attrs[i][0]] = ''
                        if slen > 0:
                            match['attrs'][attrs[i][0]] = response[p:p + slen]
                        p += slen - 4
                    elif attrs[i][1] == SPH_ATTR_MULTI:
                        match['attrs'][attrs[i][0]] = []
                        nvals = unpack('>L', response[p:p + 4])[0]
                        p += 4
                        for n in range(0, nvals, 1):
                            match['attrs'][attrs[i][0]].append(unpack('>L', response[p:p + 4])[0])
                            p += 4

                        p -= 4
                    elif attrs[i][1] == SPH_ATTR_MULTI64:
                        match['attrs'][attrs[i][0]] = []
                        nvals = unpack('>L', response[p:p + 4])[0]
                        nvals = nvals / 2
                        p += 4
                        for n in range(0, nvals, 1):
                            match['attrs'][attrs[i][0]].append(unpack('>q', response[p:p + 8])[0])
                            p += 8

                        p -= 4
                    else:
                        match['attrs'][attrs[i][0]] = unpack('>L', response[p:p + 4])[0]
                    p += 4

                result['matches'].append(match)

            result['total'], result['total_found'], result['time'], words = unpack('>4L', response[p:p + 16])
            result['time'] = '%.3f' % (result['time'] / 1000.0)
            p += 16
            result['words'] = []
            while words > 0:
                words -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                word = response[p:p + length]
                p += length
                docs, hits = unpack('>2L', response[p:p + 8])
                p += 8
                result['words'].append({'word': word,
                 'docs': docs,
                 'hits': hits})

        self._reqs = []
        return results

    def BuildExcerpts(self, docs, index, words, opts = None):
        if not opts:
            opts = {}
        if isinstance(words, unicode):
            words = words.encode('utf-8')
        sock = self._Connect()
        if not sock:
            return None
        opts.setdefault('before_match', '<b>')
        opts.setdefault('after_match', '</b>')
        opts.setdefault('chunk_separator', ' ... ')
        opts.setdefault('html_strip_mode', 'index')
        opts.setdefault('limit', 256)
        opts.setdefault('limit_passages', 0)
        opts.setdefault('limit_words', 0)
        opts.setdefault('around', 5)
        opts.setdefault('start_passage_id', 1)
        opts.setdefault('passage_boundary', 'none')
        flags = 1
        if opts.get('exact_phrase'):
            flags |= 2
        if opts.get('single_passage'):
            flags |= 4
        if opts.get('use_boundaries'):
            flags |= 8
        if opts.get('weight_order'):
            flags |= 16
        if opts.get('query_mode'):
            flags |= 32
        if opts.get('force_all_words'):
            flags |= 64
        if opts.get('load_files'):
            flags |= 128
        if opts.get('allow_empty'):
            flags |= 256
        if opts.get('emit_zones'):
            flags |= 512
        if opts.get('load_files_scattered'):
            flags |= 1024
        req = [pack('>2L', 0, flags)]
        req.append(pack('>L', len(index)))
        req.append(index)
        req.append(pack('>L', len(words)))
        req.append(words)
        req.append(pack('>L', len(opts['before_match'])))
        req.append(opts['before_match'])
        req.append(pack('>L', len(opts['after_match'])))
        req.append(opts['after_match'])
        req.append(pack('>L', len(opts['chunk_separator'])))
        req.append(opts['chunk_separator'])
        req.append(pack('>L', int(opts['limit'])))
        req.append(pack('>L', int(opts['around'])))
        req.append(pack('>L', int(opts['limit_passages'])))
        req.append(pack('>L', int(opts['limit_words'])))
        req.append(pack('>L', int(opts['start_passage_id'])))
        req.append(pack('>L', len(opts['html_strip_mode'])))
        req.append(opts['html_strip_mode'])
        req.append(pack('>L', len(opts['passage_boundary'])))
        req.append(opts['passage_boundary'])
        req.append(pack('>L', len(docs)))
        for doc in docs:
            if isinstance(doc, unicode):
                doc = doc.encode('utf-8')
            req.append(pack('>L', len(doc)))
            req.append(doc)

        req = ''.join(req)
        length = len(req)
        req = pack('>2HL', SEARCHD_COMMAND_EXCERPT, VER_COMMAND_EXCERPT, length) + req
        wrote = sock.send(req)
        response = self._GetResponse(sock, VER_COMMAND_EXCERPT)
        if not response:
            return []
        pos = 0
        res = []
        rlen = len(response)
        for i in range(len(docs)):
            length = unpack('>L', response[pos:pos + 4])[0]
            pos += 4
            if pos + length > rlen:
                self._error = 'incomplete reply'
                return []
            res.append(response[pos:pos + length])
            pos += length

        return res

    def UpdateAttributes(self, index, attrs, values, mva = False):
        for attr in attrs:
            pass

        for docid, entry in values.items():
            AssertUInt32(docid)
            for val in entry:
                if mva:
                    for vals in val:
                        AssertInt32(vals)

                else:
                    AssertInt32(val)

        req = [pack('>L', len(index)), index]
        req.append(pack('>L', len(attrs)))
        mva_attr = 0
        if mva:
            mva_attr = 1
        for attr in attrs:
            req.append(pack('>L', len(attr)) + attr)
            req.append(pack('>L', mva_attr))

        req.append(pack('>L', len(values)))
        for docid, entry in values.items():
            req.append(pack('>Q', docid))
            for val in entry:
                val_len = val
                if mva:
                    val_len = len(val)
                req.append(pack('>L', val_len))
                if mva:
                    for vals in val:
                        req.append(pack('>L', vals))

        sock = self._Connect()
        if not sock:
            return None
        req = ''.join(req)
        length = len(req)
        req = pack('>2HL', SEARCHD_COMMAND_UPDATE, VER_COMMAND_UPDATE, length) + req
        wrote = sock.send(req)
        response = self._GetResponse(sock, VER_COMMAND_UPDATE)
        if not response:
            return -1
        updated = unpack('>L', response[0:4])[0]
        return updated

    def BuildKeywords(self, query, index, hits):
        req = [pack('>L', len(query)) + query]
        req.append(pack('>L', len(index)) + index)
        req.append(pack('>L', hits))
        sock = self._Connect()
        if not sock:
            return None
        req = ''.join(req)
        length = len(req)
        req = pack('>2HL', SEARCHD_COMMAND_KEYWORDS, VER_COMMAND_KEYWORDS, length) + req
        wrote = sock.send(req)
        response = self._GetResponse(sock, VER_COMMAND_KEYWORDS)
        if not response:
            return None
        res = []
        nwords = unpack('>L', response[0:4])[0]
        p = 4
        max_ = len(response)
        while nwords > 0 and p < max_:
            nwords -= 1
            length = unpack('>L', response[p:p + 4])[0]
            p += 4
            tokenized = response[p:p + length]
            p += length
            length = unpack('>L', response[p:p + 4])[0]
            p += 4
            normalized = response[p:p + length]
            p += length
            entry = {'tokenized': tokenized,
             'normalized': normalized}
            if hits:
                entry['docs'], entry['hits'] = unpack('>2L', response[p:p + 8])
                p += 8
            res.append(entry)

        if nwords > 0 or p > max_:
            self._error = 'incomplete reply'
            return None
        return res

    def Status(self):
        sock = self._Connect()
        if not sock:
            return None
        req = pack('>2HLL', SEARCHD_COMMAND_STATUS, VER_COMMAND_STATUS, 4, 1)
        wrote = sock.send(req)
        response = self._GetResponse(sock, VER_COMMAND_STATUS)
        if not response:
            return None
        res = []
        p = 8
        max_ = len(response)
        while p < max_:
            length = unpack('>L', response[p:p + 4])[0]
            k = response[p + 4:p + length + 4]
            p += 4 + length
            length = unpack('>L', response[p:p + 4])[0]
            v = response[p + 4:p + length + 4]
            p += 4 + length
            res += [[k, v]]

        return res

    def Open(self):
        if self._socket:
            self._error = 'already connected'
            return None
        server = self._Connect()
        if not server:
            return None
        request = pack('>hhII', SEARCHD_COMMAND_PERSIST, 0, 4, 1)
        server.send(request)
        self._socket = server
        return True

    def Close(self):
        if not self._socket:
            self._error = 'not connected'
            return
        self._socket.close()
        self._socket = None

    def EscapeString(self, string):
        return re.sub('([=\\(\\)|\\-!@~\\"&/\\\\\\^\\$\\=])', '\\\\\\1', string)

    def FlushAttributes(self):
        sock = self._Connect()
        if not sock:
            return -1
        request = pack('>hhI', SEARCHD_COMMAND_FLUSHATTRS, VER_COMMAND_FLUSHATTRS, 0)
        sock.send(request)
        response = self._GetResponse(sock, VER_COMMAND_FLUSHATTRS)
        if not response or len(response) != 4:
            self._error = 'unexpected response length'
            return -1
        tag = unpack('>L', response[0:4])[0]
        return tag


def AssertInt32(value):
    pass


def AssertUInt32(value):
    pass