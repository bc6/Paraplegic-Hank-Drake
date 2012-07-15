#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\launcherapi.py
import log
import json
import mmap
import os
NULL = chr(0)

class MemoryOverflow(Exception):
    pass


class UpdateFailedWrongDataType(Exception):
    pass


class BaseSharedMemory(object):

    def __init__(self, size, name):
        self.size = size
        self.name = name
        self.memory = mmap.mmap(-1, size, name)
        self.EMPTY = self.size * NULL

    def Read(self):
        self.memory.seek(0)
        return self.memory.readline()

    def Write(self, what):
        self.memory.seek(0)
        self.memory.write(str(what))

    def Wipe(self):
        self.memory.seek(0)
        for i in xrange(self.size):
            self.memory.write(NULL)

    def IsEmpty(self):
        data = self.Read()
        return data == self.EMPTY


class JsonMemory(BaseSharedMemory):
    size = 1024

    def Read(self):
        response = super(JsonMemory, self).Read()
        try:
            data = json.loads(response.strip())
        except ValueError:
            data = response.strip()

        return data

    def Write(self, what):
        data = json.dumps(what) + '\n'
        if len(data) > self.size:
            raise MemoryOverflow('Data is of length {} whilst the memory will only hold {}'.format(len(data), self.size))
        super(JsonMemory, self).Write(data)

    def Update(self, key, value):
        state = self.Read()
        if self.IsEmpty():
            state = {}
        if not isinstance(state, dict):
            raise UpdateFailedWrongDataType('Data in memory is of type {!r}'.format(type(state)))
        state[key] = value
        self.Write(state)


class ClientBootManager(JsonMemory):

    def __init__(self):
        self.name = 'exefile{}'.format(os.getpid())
        super(ClientBootManager, self).__init__(self.size, self.name)
        log.GetChannel('sharedMemory')
        self.log = log.GetChannel('sharedMemory').Log

    def SetPercentage(self, percentage):
        self.log('Client boot progress: %s' % percentage)
        self.Update('clientBoot', percentage)