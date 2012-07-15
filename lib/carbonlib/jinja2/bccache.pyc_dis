#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\bccache.py
from os import path, listdir
import sys
import marshal
import tempfile
import cPickle as pickle
import fnmatch
try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

from jinja2.utils import open_if_exists
if sys.version_info > (3, 0):
    from io import BytesIO
    marshal_dump = marshal.dump
    marshal_load = marshal.load
else:
    from cStringIO import StringIO as BytesIO

    def marshal_dump(code, f):
        if isinstance(f, file):
            marshal.dump(code, f)
        else:
            f.write(marshal.dumps(code))


    def marshal_load(f):
        if isinstance(f, file):
            return marshal.load(f)
        return marshal.loads(f.read())


bc_version = 2
bc_magic = 'j2'.encode('ascii') + pickle.dumps(bc_version, 2) + pickle.dumps(sys.version_info[0] << 24 | sys.version_info[1])

class Bucket(object):

    def __init__(self, environment, key, checksum):
        self.environment = environment
        self.key = key
        self.checksum = checksum
        self.reset()

    def reset(self):
        self.code = None

    def load_bytecode(self, f):
        magic = f.read(len(bc_magic))
        if magic != bc_magic:
            self.reset()
            return
        checksum = pickle.load(f)
        if self.checksum != checksum:
            self.reset()
            return
        self.code = marshal_load(f)

    def write_bytecode(self, f):
        if self.code is None:
            raise TypeError("can't write empty bucket")
        f.write(bc_magic)
        pickle.dump(self.checksum, f, 2)
        marshal_dump(self.code, f)

    def bytecode_from_string(self, string):
        self.load_bytecode(BytesIO(string))

    def bytecode_to_string(self):
        out = BytesIO()
        self.write_bytecode(out)
        return out.getvalue()


class BytecodeCache(object):

    def load_bytecode(self, bucket):
        raise NotImplementedError()

    def dump_bytecode(self, bucket):
        raise NotImplementedError()

    def clear(self):
        pass

    def get_cache_key(self, name, filename = None):
        hash = sha1(name.encode('utf-8'))
        if filename is not None:
            filename = '|' + filename
            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
            hash.update(filename)
        return hash.hexdigest()

    def get_source_checksum(self, source):
        return sha1(source.encode('utf-8')).hexdigest()

    def get_bucket(self, environment, name, filename, source):
        key = self.get_cache_key(name, filename)
        checksum = self.get_source_checksum(source)
        bucket = Bucket(environment, key, checksum)
        self.load_bytecode(bucket)
        return bucket

    def set_bucket(self, bucket):
        self.dump_bytecode(bucket)


class FileSystemBytecodeCache(BytecodeCache):

    def __init__(self, directory = None, pattern = '__jinja2_%s.cache'):
        if directory is None:
            directory = tempfile.gettempdir()
        self.directory = directory
        self.pattern = pattern

    def _get_cache_filename(self, bucket):
        return path.join(self.directory, self.pattern % bucket.key)

    def load_bytecode(self, bucket):
        f = open_if_exists(self._get_cache_filename(bucket), 'rb')
        if f is not None:
            try:
                bucket.load_bytecode(f)
            finally:
                f.close()

    def dump_bytecode(self, bucket):
        f = open(self._get_cache_filename(bucket), 'wb')
        try:
            bucket.write_bytecode(f)
        finally:
            f.close()

    def clear(self):
        from os import remove
        files = fnmatch.filter(listdir(self.directory), self.pattern % '*')
        for filename in files:
            try:
                remove(path.join(self.directory, filename))
            except OSError:
                pass


class MemcachedBytecodeCache(BytecodeCache):

    def __init__(self, client, prefix = 'jinja2/bytecode/', timeout = None):
        self.client = client
        self.prefix = prefix
        self.timeout = timeout

    def load_bytecode(self, bucket):
        code = self.client.get(self.prefix + bucket.key)
        if code is not None:
            bucket.bytecode_from_string(code)

    def dump_bytecode(self, bucket):
        args = (self.prefix + bucket.key, bucket.bytecode_to_string())
        if self.timeout is not None:
            args += (self.timeout,)
        self.client.set(*args)