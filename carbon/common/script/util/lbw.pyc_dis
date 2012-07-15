#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/lbw.py
import sys
import struct
import time
import re
import ctypes
import datetime
_c_counter_frequency = ctypes.c_int64()
ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(_c_counter_frequency))
COUNTER_FREQUENCY = _c_counter_frequency.value
DELPHI_DATE_TIME_EPOCH = datetime.datetime(1899, 12, 30, 0, 0, 0)
LGINFO = 1
LGNOTICE = 32
LGWARN = 2
LGERR = 4
severity_name = {LGINFO: 'info',
 LGNOTICE: 'notice',
 LGWARN: 'warn',
 LGERR: 'error'}
epoch_diff = 11644473600000L / 1000.0
P_BYTE = 2
P_DWORD = 3
P_INT = 4
P_LONGLONG = 8
P_SHORT_STRING = 6
P_LONG_STRING = 12
P_REAL = 17
P_SINGLE = None

def Read_BYTE(f):
    return ord(f.read(1))


def Read_SBYTE(f):
    return struct.unpack('b', f.read(1))[0]


def Read_DWORD(f):
    return struct.unpack('h', f.read(2))[0]


def Read_INT(f):
    return struct.unpack('i', f.read(4))[0]


def Read_SHORT_STRING(f):
    return f.read(Read_BYTE(f))


def Read_LONG_STRING(f):
    return f.read(Read_INT(f))


def Read_REAL(f):
    return struct.unpack('d', f.read(8))[0]


def Read_SINGLE(f):
    return struct.unpack('f', f.read(4))[0]


def Read_LONGLONG(f):
    return struct.unpack('q', f.read(8))[0]


def Write_BYTE(f, b):
    f.write(chr(b))


def Write_SBYTE(f, b):
    f.write(struct.pack('b', b))


def Write_DWORD(f, dw):
    f.write(struct.pack('h', dw))


def Write_INT(f, i):
    f.write(struct.pack('i', i))


def Write_UINT(f, i):
    f.write(struct.pack('I', i))


def Write_SHORT_STRING(f, s):
    Write_BYTE(f, len(s))
    f.write(s)


def Write_LONG_STRING(f, s):
    Write_INT(f, len(s))
    f.write(s)


def Write_REAL(f, r):
    f.write(struct.pack('d', r))


def Write_SINGLE(f, s):
    f.write(struct.pack('f', s))


def Write_LONGLONG(f, ll):
    f.write(struct.pack('q', ll))


dispatchInt = {P_BYTE: Read_SBYTE,
 P_DWORD: Read_DWORD,
 P_INT: Read_INT,
 P_LONGLONG: Read_LONGLONG}
dispatchStr = {P_SHORT_STRING: Read_SHORT_STRING,
 P_LONG_STRING: Read_LONG_STRING}
dispatchFlt = {P_REAL: Read_REAL,
 P_SINGLE: Read_SINGLE}

def ReadInteger(f):
    return dispatchInt[Read_BYTE(f)](f)


def ReadString(f):
    return dispatchStr[Read_BYTE(f)](f).rstrip('\x00')


def ReadFloat(f):
    return dispatchFlt[Read_BYTE(f)](f)


def ReadBoolean(f):
    b = Read_BYTE(f)
    if b ^ 8:
        return True
    return False


def ReadHandle(f):
    Read_BYTE(f)
    return struct.unpack('I', f.read(4))[0]


def WriteInteger(f, i):
    if i >= -128 and i < 128:
        Write_BYTE(f, P_BYTE)
        Write_SBYTE(f, i)
    elif i >= -32768 and i < 32768:
        Write_BYTE(f, P_DWORD)
        Write_DWORD(f, i)
    elif i >= -0x80000000 and i < 2147483648L:
        Write_BYTE(f, P_INT)
        Write_INT(f, i)
    else:
        Write_BYTE(f, P_LONGLONG)
        Write_LONGLONG(f, i)


def WriteHandle(f, i):
    Write_BYTE(f, P_INT)
    Write_UINT(f, i)


def WriteString(f, s):
    if len(s) < 256:
        Write_BYTE(f, P_SHORT_STRING)
        Write_SHORT_STRING(f, s)
    else:
        Write_BYTE(f, P_LONG_STRING)
        Write_LONG_STRING(f, s)


def WriteFloat(f, fl):
    Write_BYTE(f, P_REAL)
    Write_REAL(f, fl)
    return
    s = struct.pack('f', fl)
    if struct.unpack('f', s) == fl:
        Write_BYTE(f, P_SINGLE)
        f.write(s)
    else:
        Write_BYTE(f, P_REAL)
        Write_REAL(f, fl)


def WriteBoolean(f, b):
    Write_BYTE(f, 9 if b else 8)


def FixStr(s):
    idx = s.find('\x00')
    if idx < 0:
        return s
    return s[:idx]


def FiletimeToUnix(t):
    return t * 1e-07 - epoch_diff


def UnixToFiletime(t):
    return int((t + epoch_diff) * 10000000.0)


class Header(object):

    @classmethod
    def Read(self, f):
        h = self()
        h.label = ReadString(f)
        h.description = ReadString(f)
        h.created = ReadFloat(f)
        h.modified = ReadFloat(f)
        return h

    def Write(self, f):
        WriteString(f, self.label)
        WriteString(f, self.description)
        WriteFloat(f, self.created)
        WriteFloat(f, self.modified)

    def __repr__(self):
        return '<%s %r %r %r %r>' % (self.__class__.__name__,
         self.label,
         self.description,
         self.created,
         self.modified)


class InitData(object):

    def __init__(self, f):
        if f is None:
            return
        self.computer = ReadString(f)
        self.processname = ReadString(f)
        self.pid = ReadInteger(f)
        self.module = ReadHandle(f)
        self.modulename = ReadString(f)
        self.timestamp = Read_LONGLONG(f)

    def Write(self, f):
        WriteString(f, self.computer)
        WriteString(f, self.processname)
        WriteInteger(f, self.pid)
        WriteHandle(f, self.module)
        WriteString(f, self.modulename)
        Write_LONGLONG(f, self.timestamp)

    def __repr__(self):
        return '<%s %r,%r,%r>' % (self.computer,
         self.processname,
         self.pid,
         self.modulename)


class Channel(object):

    def __init__(self, f):
        if f is not None:
            self.ReadChannelInfo(f)

    infoFmt = 'qq33s33sii0q'

    def ReadChannelInfo(self, f):
        fmt = self.infoFmt
        t = struct.unpack(fmt, f.read(struct.calcsize(fmt)))
        self.facilityHash = t[0]
        self.objectHash = t[1]
        self.facility = FixStr(t[2])
        self.objectdesc = FixStr(t[3])
        self.suppressed = t[4]
        self.flagSuppress = t[5]

    def WriteChannelInfo(self, f):
        f.write(struct.pack(self.infoFmt, self.facilityHash, self.objectHash, self.facility, self.objectdesc, self.suppressed, self.flagSuppress))

    def ReadHeader(self, f):
        self.header = Header.Read(f)

    def WriteHeader(self, f):
        self.header.Write(f)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, '::'.join((self.facility, self.objectdesc)))

    def __str__(self):
        return '::'.join((self.facility, self.objectdesc))


class LBW(object):

    def __init__(self, f = None):
        if f:
            self.Read(f)

    def ReadDevices(self, f):
        n = ReadInteger(f)
        return [ self.ReadDevice(f) for d in xrange(n) ]

    def ReadDevice(self, f):
        device = {'header': Header.Read(f),
         'devId': Read_LONGLONG(f),
         'mapFileName': ReadString(f),
         'pollInterval': ReadInteger(f),
         'capacity': ReadInteger(f),
         'channels': self.ReadChannels(f),
         'start': ReadBoolean(f)}
        return device

    def WriteDevices(self, f, devices):
        WriteInteger(f, len(devices))
        for d in devices:
            self.WriteDevice(f, d)

    def WriteDevice(self, f, d):
        d['header'].Write(f)
        Write_LONGLONG(f, d['devId'])
        WriteString(f, d['mapFileName'])
        WriteInteger(f, d['pollInterval'])
        WriteInteger(f, d['capacity'])
        self.WriteChannels(f, d['channels'], d['devId'])
        WriteBoolean(f, d['start'])

    def ReadChannels(self, f):
        devId = Read_LONGLONG(f)
        counter = ReadInteger(f)
        numChannels = ReadInteger(f)
        channels = [ Channel(f) for c in xrange(numChannels) ]
        for channel in channels:
            channel.ReadHeader(f)
            initCounter = ReadInteger(f)
            initData = {}
            for i in xrange(initCounter):
                sourceId = Read_INT(f)
                initData[sourceId] = InitData(f)

            channel.initData = initData

        return channels

    def WriteChannels(self, f, channels, devId):
        Write_LONGLONG(f, devId)
        nInits = sum([ len(chan.initData) for chan in channels ])
        WriteInteger(f, nInits)
        WriteInteger(f, len(channels))
        for c in channels:
            c.WriteChannelInfo(f)

        for c in channels:
            c.WriteHeader(f)
            WriteInteger(f, len(c.initData))
            for id, data in c.initData.iteritems():
                Write_INT(f, id)
                data.Write(f)

    def ReadLogs(self, f):
        self.createLogBase = ReadBoolean(f)
        self.startPerformanceCounters = {}
        result = [ self.ReadLogStorage(f) for i in xrange(ReadInteger(f)) ]
        return result

    def WriteLogs(self, f, logs):
        WriteBoolean(f, self.createLogBase)
        WriteInteger(f, len(logs))
        for l in logs:
            self.WriteLogStorage(f, l)

    def ReadLogStorage(self, f):
        header = Header.Read(f)
        logId = Read_LONGLONG(f)
        initialCap = ReadInteger(f)
        incrCap = ReadInteger(f)
        clearOnNewPid = ReadBoolean(f)
        filterChannels = ReadBoolean(f)
        fileTime = Read_LONGLONG(f)
        flags = [ReadInteger(f)]
        while flags[-1] != -1:
            flags.append(ReadInteger(f))

        filterFlags = ReadBoolean(f)
        filterFlagsMask = ReadInteger(f)
        keepLogs = ReadBoolean(f)
        if keepLogs:
            numberOfLogs = ReadInteger(f)
            numberOfOverlap = ReadInteger(f)
            logs = [ self.ReadLogLine(f) for i in xrange(numberOfLogs + numberOfOverlap) ]
        else:
            logs = []
        return {'header': header,
         'logId': logId,
         'initialCap': initialCap,
         'incrCap': incrCap,
         'clearOnNewPid': clearOnNewPid,
         'filterChannels': filterChannels,
         'fileTime': fileTime,
         'filterFlags': filterFlags,
         'filterFlagsMask': filterFlagsMask,
         'keepLogs': keepLogs,
         'flags': flags,
         'logs': logs}

    def WriteLogStorage(self, f, s):
        s['header'].Write(f)
        Write_LONGLONG(f, s['logId'])
        WriteInteger(f, s['initialCap'])
        WriteInteger(f, s['incrCap'])
        WriteBoolean(f, s['clearOnNewPid'])
        WriteBoolean(f, s['filterChannels'])
        Write_LONGLONG(f, s['fileTime'])
        for i in s['flags']:
            WriteInteger(f, i)

        WriteBoolean(f, s['filterFlags'])
        WriteInteger(f, s['filterFlagsMask'])
        WriteBoolean(f, s['keepLogs'])
        if s['keepLogs']:
            WriteInteger(f, len(s['logs']))
            WriteInteger(f, 0)
            for line in s['logs']:
                self.WriteLogLine(f, line)

    def ReadLogLine(self, f):
        return [Read_DWORD(f),
         Read_INT(f),
         Read_LONGLONG(f),
         Read_INT(f),
         Read_LONG_STRING(f).rstrip('\x00'),
         Read_INT(f),
         Read_INT(f)]

    def WriteLogLine(self, f, line):
        Write_DWORD(f, line[0])
        Write_INT(f, line[1])
        Write_LONGLONG(f, line[2])
        Write_INT(f, line[3])
        Write_LONG_STRING(f, line[4] + '\x00')
        Write_INT(f, line[5])
        Write_INT(f, line[6])

    def BuildIndices(self):
        self.channels = [None]
        for dev in self.devices:
            self.channels.extend(dev['channels'])

    def Read(self, f):
        self.version = ReadInteger(f)
        self.header = Header.Read(f)
        self.filename = ReadString(f)
        self.devices = self.ReadDevices(f)
        self.logStores = self.ReadLogs(f)
        self.numLayouts = ReadInteger(f)
        self.layoutHeaders = []
        for i in range(self.numLayouts):
            self.layoutHeaders.append(Header.Read(f))

        self.lbwTrailer = f.read()
        self.BuildIndices()

    def Write(self, f):
        WriteInteger(f, self.version)
        self.header.Write(f)
        WriteString(f, self.filename)
        self.WriteDevices(f, self.devices)
        self.WriteLogs(f, self.logStores)
        WriteInteger(f, self.numLayouts)
        for header in self.layoutHeaders:
            header.Write(f)

        if not hasattr(self, 'lbwTrailer'):
            self.lbwTrailer = '\x02\x00\x02\xff'
        f.write(self.lbwTrailer)

    def Normalize(self):
        used = {}
        for store in self.logStores:
            for line in store['logs']:
                idx = line[0]
                try:
                    used[idx].add(line[6])
                except KeyError:
                    used[idx] = set((line[6],))

        i, j = (1, 1)
        remap = {}
        for d in self.devices:
            chns = d['channels']
            for ci in xrange(len(chns)):
                if i in used:
                    remap[i] = j
                    j += 1
                    c = chns[ci]
                    ids = used[i]
                    c.initData = dict([ (k, c.initData[k]) for k in ids ])
                else:
                    chns[ci] = None
                i += 1

        for d in self.devices:
            chns = d['channels']
            chns = [ c for c in chns if c ]
            d['channels'] = chns

        for store in self.logStores:
            lines = store['logs']
            for line in lines:
                line[0] = remap[line[0]]

        self.devices = [ d for d in self.devices if d['channels'] ]
        self.BuildIndices()

    def ChunkLines(self, logStore):
        timediff = 0.0001
        i = iter(logStore['logs'])
        chunk = [i.next()]
        head = LogLine(chunk[0], self.channels)
        for l in i:
            this = LogLine(l, self.channels)
            if this.severity != head.severity or this.channel != head.channel or this.threadId != head.threadId or this.timestamp - head.timestamp >= timediff:
                yield chunk
                chunk = [l]
                head = this
            else:
                chunk.append(l)

        yield chunk

    def Filter(self, chunk = False, pid = None, regex = None):
        if regex is not None:
            regex = re.compile(regex)
        for store in self.logStores:
            if chunk:
                chunks = self.ChunkLines(store)
            else:
                chunks = [ [l] for l in store['logs'] ]

            def acceptchunk(c):
                for line in c:
                    if pid is not None and line[5] == pid:
                        return True
                    if regex and regex.search(line[4]):
                        return True

                return False

            chunks = [ c for c in chunks if acceptchunk(c) ]
            lines = []
            for c in chunks:
                lines.extend(c)

            store['logs'] = lines

        self.Normalize()

    def Lines(self, logStore = 0):
        s = self.logStores[0]
        for line in s['logs']:
            yield LogLine(line, self.channels)

    def SetupNewWorkspace(self):
        self._SetVersion(9)
        self._SetHeader('Workspace', '')
        self._SetFileName('defaultFileName')
        self.devices = []
        self.AddDevice('defaultDevice', '', 1L)
        self.createLogBase = False
        self.logStores = []
        self.startPerformanceCounters = {}
        self.AddLogStorage('Default storage', '')
        self.numLayouts = 0
        self.layoutHeaders = []
        self.AddLayout('Default layout', '')

    def _CreateNewHeader(self, label, description):
        newHeader = Header()
        newHeader.label = label
        newHeader.description = description
        newHeader.created = self._GetCurrentTimeInDelphiFormat()
        newHeader.modified = self._GetCurrentTimeInDelphiFormat()
        return newHeader

    def _SetVersion(self, version):
        self.version = version

    def _SetHeader(self, label, description):
        self.header = self._CreateNewHeader(label, description)

    def _SetFileName(self, fileName):
        self.filename = fileName

    def AddDevice(self, deviceLabel, deviceDescription, deviceID, pollInterval = 500, capacity = 5000):
        deviceHeader = self._CreateNewHeader(deviceLabel, deviceDescription)
        device = {'header': deviceHeader,
         'devId': deviceID,
         'mapFileName': deviceLabel,
         'pollInterval': pollInterval,
         'capacity': capacity,
         'channels': [],
         'start': True}
        self.devices.append(device)

    def AddLogStorage(self, label, description, initialCapacity = 1000, incrementalCapacity = 1000, clearOnNewPid = False, filterFlags = False, filterFlagsMask = 0):
        storageHeader = self._CreateNewHeader(label, description)
        devID = self.devices[0]['devId']
        logStorage = {'header': storageHeader,
         'logId': devID,
         'initialCap': initialCapacity,
         'incrCap': incrementalCapacity,
         'clearOnNewPid': clearOnNewPid,
         'filterChannels': False,
         'fileTime': 0L,
         'filterFlags': filterFlags,
         'filterFlagsMask': filterFlagsMask,
         'keepLogs': True,
         'flags': [-1],
         'logs': []}
        self.logStores.append(logStorage)

    def AddLayout(self, label, description):
        self.numLayouts += 1
        layoutHeader = self._CreateNewHeader(label, description)
        self.layoutHeaders.append(layoutHeader)

    def _GetCurrentTimeInDelphiFormat(self):
        curTime = datetime.datetime.utcnow() - DELPHI_DATE_TIME_EPOCH
        return curTime.days + curTime.seconds / 86400.0

    def AddChannel(self, facilityHash, objectHash, facilityName, objectDescription, sourceID, computerName, processName, processID, module, moduleName, timestamp):
        channel = None
        for chan in self.devices[0]['channels']:
            if chan.facilityHash == facilityHash and chan.objectHash == objectHash and chan.facility == facilityName and chan.objectdesc == objectDescription:
                channel = chan
                break

        if channel is None:
            channel = Channel(None)
            channel.facilityHash = facilityHash
            channel.objectHash = objectHash
            channel.facility = facilityName
            channel.objectdesc = objectDescription
            channel.suppressed = 0
            channel.flagSuppress = 0
            channel.header = self._CreateNewHeader(objectDescription, '')
            channel.initData = {}
            self.devices[0]['channels'].append(channel)
        channelInitData = InitData(None)
        channelInitData.computer = computerName
        channelInitData.processname = processName
        channelInitData.pid = processID
        channelInitData.module = module
        channelInitData.modulename = moduleName
        channelInitData.timestamp = timestamp
        channel.initData[sourceID] = channelInitData
        self.BuildIndices()

    def AddLogLine(self, channelIndex, threadID, performanceCounter, flag, message, processID, sourceID):
        for idx, store in enumerate(self.logStores):
            if not store['filterFlags'] or flag & store['filterFlagsMask']:
                if len(store['logs']) == 0:
                    store['fileTime'] = UnixToFiletime(time.time())
                if idx not in self.startPerformanceCounters or self.startPerformanceCounters[idx] == 0:
                    self.startPerformanceCounters[idx] = performanceCounter
                timestamp = long((performanceCounter - self.startPerformanceCounters[idx]) * 10000000.0 / COUNTER_FREQUENCY)
                timestamp += store['fileTime']
                logLine = [channelIndex,
                 threadID,
                 timestamp,
                 flag,
                 message,
                 processID,
                 sourceID]
                store['logs'].append(logLine)


class LogLine(object):
    __slots__ = ['channel',
     'threadId',
     '_timestamp',
     'severity',
     'msg',
     'pid',
     'initData']

    def __init__(self, t, channels):
        self.channel = channels[t[0]]
        self.threadId = t[1]
        self._timestamp = t[2]
        self.severity = t[3]
        self.msg = t[4]
        self.pid = t[5]
        self.initData = self.channel.initData[t[6]]

    @property
    def message(self):
        try:
            return self.msg.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return self.msg.decode('cp1252')
            except UnicodeDecodeError:
                return self.msg

    @property
    def timestamp(self):
        return FiletimeToUnix(self._timestamp)

    @property
    def facility(self):
        return self.channel.facility

    @property
    def object(self):
        return self.channel.objectdesc

    @property
    def computer(self):
        return self.initData.computer

    @property
    def process(self):
        return self.initData.processname

    @property
    def module(self):
        return self.initData.modulename

    @property
    def severitystr(self):
        return severity_name[self.severity]

    def ShortTime(self):
        ts = self.timestamp
        ms = int(ts * 1000.0) % 1000
        return time.strftime('%H:%M:%S', time.gmtime(ts)) + '.%.3i' % ms

    def LongTime(self):
        ts = self.timestamp
        ms = int(ts * 1000.0) % 1000
        return time.strftime('%Y.%m.%d::%H:%M:%S', time.gmtime(ts)) + '.%.3i' % ms

    def __repr__(self):
        '<%s %r>' % (self.__class__.__name__, self.message[:20])

    def __str__(self):
        ts = self.timestamp
        ms = int(ts * 1000.0) % 1000
        return '%s:%s:%s:%r' % (self.ShortTime(),
         self.facility,
         self.object,
         self.message)


def ChunkLines(lines):
    lineIter = iter(lines)
    chunk = [lineIter.next()]
    last = chunk[0]
    regex = re.compile('\\n- *')
    timediff = 0.0001
    for l in lineIter:
        if l.severity != last.severity or l.channel != last.channel or l.threadId != last.threadId or l.timestamp - last.timestamp >= timediff:
            last.msg = '\n'.join([ line.msg for line in chunk ])
            last.msg = regex.sub('', last.msg)
            yield last
            chunk = [l]
            last = l
        else:
            chunk.append(l)


def Filter(lines, severity = 0, pid = 0, text = None):
    lineIter = iter(lines)
    if text:
        import re
        re = re.compile(text)
    else:
        re = None
    for l in lineIter:
        if re and not re.search(l.message):
            continue
        if severity and not l.severity & severity:
            continue
        if pid and pid != l.pid:
            continue
        yield l


def FilterFiles(files, severity = None, text = None):
    sev = dict(info=1, warn=2, error=4, fatal=8)
    sev = sev[severity] if severity else 0
    for fn in files:
        if not hasattr(fn, 'read'):
            f = file(fn, 'rb')
        else:
            f = fn
        logs = LBW(f)
        for l in Filter(ChunkLines(logs.Lines()), severity=sev, text=text):
            print l.ShortTime(), '%6i' % l.pid, '%5s' % l.severitystr, '%20s' % l.channel, repr(l.message)


def FilterExceptions(files):
    regex = re.compile('\\b.+Error: .+')
    for fn in files:
        if not hasattr(fn, 'read'):
            f = file(fn, 'rb')
        else:
            f = fn
        logs = LBW(f)
        for l in ChunkLines(logs.Lines()):
            msg = l.message
            m = regex.search(msg)
            if m:
                print l.ShortTime(), '%6i' % l.pid, '%5s' % l.severitystr, '%20s' % l.channel, repr(m.group(0)), repr(msg)


def FilterFile(infile, outfile, chunk = False, pid = None, regex = None):
    logs = LBW(open(infile, 'rb'))
    logs.Filter(chunk=chunk, pid=pid, regex=regex)
    logs.Write(open(outfile, 'wb'))


def main(args = None):
    import glob
    if args is None:
        args = sys.argv[1:]
    if not args or args[0] not in ('-l', '-s', '-t', '-e', '-f'):
        Usage()
    if args[0] == '-l':
        if len(args) == 1:
            Usage()
        for f in args[1:]:
            FilterFiles(glob.glob(f))

    if args[0] == '-s':
        if len(args) < 3:
            Usage()
        severity = args[1]
        for f in args[2:]:
            FilterFiles(glob.glob(f), severity=severity)

    if args[0] == '-t':
        if len(args) < 3:
            Usage()
        text = args[1]
        for f in args[2:]:
            FilterFiles(glob.glob(f), text=text)

    if args[0] == '-e':
        if len(args) < 2:
            Usage()
        for f in args[1:]:
            FilterExceptions(glob.glob(f))

    if args[0] == '-f':
        args.pop(0)
        try:
            outfile = args.pop(-1)
            infile = args.pop(-1)
            pid = None
            regex = None
            chunk = False
            while args:
                if args[0] == '-p':
                    args.pop(0)
                    pid = int(args.pop(0))
                elif args[0] == '-c':
                    args.pop(0)
                    chunk = True
                elif args[0] == '-r':
                    args.pop(0)
                    regex = args.pop(0)
                else:
                    Usage()

        except IndexError:
            Usage()

        FilterFile(infile, outfile, pid=pid, chunk=chunk, regex=regex)


def Usage():
    import textwrap
    print textwrap.dedent('        Usage:\n            lbw.py -l files ... \n            lbw.py -s severity files  \n            lbw.py -e files   # Exceptions\n            lbw.py -f [-c] [-r regex][-p pid] infile outfile #filter file\n        ')
    sys.exit(1)


import util
exports = util.AutoExports('lbw', globals())