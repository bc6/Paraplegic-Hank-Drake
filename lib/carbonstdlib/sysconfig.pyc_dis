#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\sysconfig.py
import sys
import os
from os.path import pardir, realpath
_INSTALL_SCHEMES = {'posix_prefix': {'stdlib': '{base}/lib/python{py_version_short}',
                  'platstdlib': '{platbase}/lib/python{py_version_short}',
                  'purelib': '{base}/lib/python{py_version_short}/site-packages',
                  'platlib': '{platbase}/lib/python{py_version_short}/site-packages',
                  'include': '{base}/include/python{py_version_short}',
                  'platinclude': '{platbase}/include/python{py_version_short}',
                  'scripts': '{base}/bin',
                  'data': '{base}'},
 'posix_home': {'stdlib': '{base}/lib/python',
                'platstdlib': '{base}/lib/python',
                'purelib': '{base}/lib/python',
                'platlib': '{base}/lib/python',
                'include': '{base}/include/python',
                'platinclude': '{base}/include/python',
                'scripts': '{base}/bin',
                'data': '{base}'},
 'nt': {'stdlib': '{base}/Lib',
        'platstdlib': '{base}/Lib',
        'purelib': '{base}/Lib/site-packages',
        'platlib': '{base}/Lib/site-packages',
        'include': '{base}/Include',
        'platinclude': '{base}/Include',
        'scripts': '{base}/Scripts',
        'data': '{base}'},
 'os2': {'stdlib': '{base}/Lib',
         'platstdlib': '{base}/Lib',
         'purelib': '{base}/Lib/site-packages',
         'platlib': '{base}/Lib/site-packages',
         'include': '{base}/Include',
         'platinclude': '{base}/Include',
         'scripts': '{base}/Scripts',
         'data': '{base}'},
 'os2_home': {'stdlib': '{userbase}/lib/python{py_version_short}',
              'platstdlib': '{userbase}/lib/python{py_version_short}',
              'purelib': '{userbase}/lib/python{py_version_short}/site-packages',
              'platlib': '{userbase}/lib/python{py_version_short}/site-packages',
              'include': '{userbase}/include/python{py_version_short}',
              'scripts': '{userbase}/bin',
              'data': '{userbase}'},
 'nt_user': {'stdlib': '{userbase}/Python{py_version_nodot}',
             'platstdlib': '{userbase}/Python{py_version_nodot}',
             'purelib': '{userbase}/Python{py_version_nodot}/site-packages',
             'platlib': '{userbase}/Python{py_version_nodot}/site-packages',
             'include': '{userbase}/Python{py_version_nodot}/Include',
             'scripts': '{userbase}/Scripts',
             'data': '{userbase}'},
 'posix_user': {'stdlib': '{userbase}/lib/python{py_version_short}',
                'platstdlib': '{userbase}/lib/python{py_version_short}',
                'purelib': '{userbase}/lib/python{py_version_short}/site-packages',
                'platlib': '{userbase}/lib/python{py_version_short}/site-packages',
                'include': '{userbase}/include/python{py_version_short}',
                'scripts': '{userbase}/bin',
                'data': '{userbase}'},
 'osx_framework_user': {'stdlib': '{userbase}/lib/python',
                        'platstdlib': '{userbase}/lib/python',
                        'purelib': '{userbase}/lib/python/site-packages',
                        'platlib': '{userbase}/lib/python/site-packages',
                        'include': '{userbase}/include',
                        'scripts': '{userbase}/bin',
                        'data': '{userbase}'}}
_SCHEME_KEYS = ('stdlib', 'platstdlib', 'purelib', 'platlib', 'include', 'scripts', 'data')
_PY_VERSION = sys.version.split()[0]
_PY_VERSION_SHORT = sys.version[:3]
_PY_VERSION_SHORT_NO_DOT = _PY_VERSION[0] + _PY_VERSION[2]
_PREFIX = os.path.normpath(sys.prefix)
_EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
_CONFIG_VARS = None
_USER_BASE = None

def _safe_realpath(path):
    try:
        return realpath(path)
    except OSError:
        return path


if sys.executable:
    _PROJECT_BASE = os.path.dirname(_safe_realpath(sys.executable))
else:
    _PROJECT_BASE = _safe_realpath(os.getcwd())
if os.name == 'nt' and 'pcbuild' in _PROJECT_BASE[-8:].lower():
    _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir))
if os.name == 'nt' and '\\pc\\v' in _PROJECT_BASE[-10:].lower():
    _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir, pardir))
if os.name == 'nt' and '\\pcbuild\\amd64' in _PROJECT_BASE[-14:].lower():
    _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir, pardir))

def is_python_build():
    for fn in ('Setup.dist', 'Setup.local'):
        if os.path.isfile(os.path.join(_PROJECT_BASE, 'Modules', fn)):
            return True

    return False


_PYTHON_BUILD = is_python_build()
if _PYTHON_BUILD:
    for scheme in ('posix_prefix', 'posix_home'):
        _INSTALL_SCHEMES[scheme]['include'] = '{projectbase}/Include'
        _INSTALL_SCHEMES[scheme]['platinclude'] = '{srcdir}'

def _subst_vars(s, local_vars):
    try:
        return s.format(**local_vars)
    except KeyError:
        try:
            return s.format(**os.environ)
        except KeyError as var:
            raise AttributeError('{%s}' % var)


def _extend_dict(target_dict, other_dict):
    target_keys = target_dict.keys()
    for key, value in other_dict.items():
        if key in target_keys:
            continue
        target_dict[key] = value


def _expand_vars(scheme, vars):
    res = {}
    if vars is None:
        vars = {}
    _extend_dict(vars, get_config_vars())
    for key, value in _INSTALL_SCHEMES[scheme].items():
        if os.name in ('posix', 'nt'):
            value = os.path.expanduser(value)
        res[key] = os.path.normpath(_subst_vars(value, vars))

    return res


def _get_default_scheme():
    if os.name == 'posix':
        return 'posix_prefix'
    return os.name


def _getuserbase():
    env_base = os.environ.get('PYTHONUSERBASE', None)

    def joinuser(*args):
        return os.path.expanduser(os.path.join(*args))

    if os.name == 'nt':
        base = os.environ.get('APPDATA') or '~'
        if env_base:
            return env_base
        return joinuser(base, 'Python')
    if sys.platform == 'darwin':
        framework = get_config_var('PYTHONFRAMEWORK')
        if framework:
            return joinuser('~', 'Library', framework, '%d.%d' % sys.version_info[:2])
    if env_base:
        return env_base
    return joinuser('~', '.local')


def _parse_makefile(filename, vars = None):
    import re
    _variable_rx = re.compile('([a-zA-Z][a-zA-Z0-9_]+)\\s*=\\s*(.*)')
    _findvar1_rx = re.compile('\\$\\(([A-Za-z][A-Za-z0-9_]*)\\)')
    _findvar2_rx = re.compile('\\${([A-Za-z][A-Za-z0-9_]*)}')
    if vars is None:
        vars = {}
    done = {}
    notdone = {}
    with open(filename) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            continue
        m = _variable_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            v = v.strip()
            tmpv = v.replace('$$', '')
            if '$' in tmpv:
                notdone[n] = v
            else:
                try:
                    v = int(v)
                except ValueError:
                    done[n] = v.replace('$$', '$')
                else:
                    done[n] = v

    while notdone:
        for name in notdone.keys():
            value = notdone[name]
            m = _findvar1_rx.search(value) or _findvar2_rx.search(value)
            if m:
                n = m.group(1)
                found = True
                if n in done:
                    item = str(done[n])
                elif n in notdone:
                    found = False
                elif n in os.environ:
                    item = os.environ[n]
                else:
                    done[n] = item = ''
                if found:
                    after = value[m.end():]
                    value = value[:m.start()] + item + after
                    if '$' in after:
                        notdone[name] = value
                    else:
                        try:
                            value = int(value)
                        except ValueError:
                            done[name] = value.strip()
                        else:
                            done[name] = value

                        del notdone[name]
            else:
                del notdone[name]

    for k, v in done.items():
        if isinstance(v, str):
            done[k] = v.strip()

    vars.update(done)
    return vars


def _get_makefile_filename():
    if _PYTHON_BUILD:
        return os.path.join(_PROJECT_BASE, 'Makefile')
    return os.path.join(get_path('stdlib'), 'config', 'Makefile')


def _init_posix(vars):
    makefile = _get_makefile_filename()
    try:
        _parse_makefile(makefile, vars)
    except IOError as e:
        msg = 'invalid Python installation: unable to open %s' % makefile
        if hasattr(e, 'strerror'):
            msg = msg + ' (%s)' % e.strerror
        raise IOError(msg)

    config_h = get_config_h_filename()
    try:
        with open(config_h) as f:
            parse_config_h(f, vars)
    except IOError as e:
        msg = 'invalid Python installation: unable to open %s' % config_h
        if hasattr(e, 'strerror'):
            msg = msg + ' (%s)' % e.strerror
        raise IOError(msg)

    if sys.platform == 'darwin' and 'MACOSX_DEPLOYMENT_TARGET' in vars:
        cfg_target = vars['MACOSX_DEPLOYMENT_TARGET']
        cur_target = os.getenv('MACOSX_DEPLOYMENT_TARGET', '')
        if cur_target == '':
            cur_target = cfg_target
            os.putenv('MACOSX_DEPLOYMENT_TARGET', cfg_target)
        elif map(int, cfg_target.split('.')) > map(int, cur_target.split('.')):
            msg = '$MACOSX_DEPLOYMENT_TARGET mismatch: now "%s" but "%s" during configure' % (cur_target, cfg_target)
            raise IOError(msg)
    if _PYTHON_BUILD:
        vars['LDSHARED'] = vars['BLDSHARED']


def _init_non_posix(vars):
    vars['LIBDEST'] = get_path('stdlib')
    vars['BINLIBDEST'] = get_path('platstdlib')
    vars['INCLUDEPY'] = get_path('include')
    vars['SO'] = '.pyd'
    vars['EXE'] = '.exe'
    vars['VERSION'] = _PY_VERSION_SHORT_NO_DOT
    vars['BINDIR'] = os.path.dirname(_safe_realpath(sys.executable))


def parse_config_h(fp, vars = None):
    import re
    if vars is None:
        vars = {}
    define_rx = re.compile('#define ([A-Z][A-Za-z0-9_]+) (.*)\n')
    undef_rx = re.compile('/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n')
    while True:
        line = fp.readline()
        if not line:
            break
        m = define_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            try:
                v = int(v)
            except ValueError:
                pass

            vars[n] = v
        else:
            m = undef_rx.match(line)
            if m:
                vars[m.group(1)] = 0

    return vars


def get_config_h_filename():
    if _PYTHON_BUILD:
        if os.name == 'nt':
            inc_dir = os.path.join(_PROJECT_BASE, 'PC')
        else:
            inc_dir = _PROJECT_BASE
    else:
        inc_dir = get_path('platinclude')
    return os.path.join(inc_dir, 'pyconfig.h')


def get_scheme_names():
    schemes = _INSTALL_SCHEMES.keys()
    schemes.sort()
    return tuple(schemes)


def get_path_names():
    return _SCHEME_KEYS


def get_paths(scheme = _get_default_scheme(), vars = None, expand = True):
    if expand:
        return _expand_vars(scheme, vars)
    else:
        return _INSTALL_SCHEMES[scheme]


def get_path(name, scheme = _get_default_scheme(), vars = None, expand = True):
    return get_paths(scheme, vars, expand)[name]


def get_config_vars(*args):
    global _CONFIG_VARS
    import re
    if _CONFIG_VARS is None:
        _CONFIG_VARS = {}
        _CONFIG_VARS['prefix'] = _PREFIX
        _CONFIG_VARS['exec_prefix'] = _EXEC_PREFIX
        _CONFIG_VARS['py_version'] = _PY_VERSION
        _CONFIG_VARS['py_version_short'] = _PY_VERSION_SHORT
        _CONFIG_VARS['py_version_nodot'] = _PY_VERSION[0] + _PY_VERSION[2]
        _CONFIG_VARS['base'] = _PREFIX
        _CONFIG_VARS['platbase'] = _EXEC_PREFIX
        _CONFIG_VARS['projectbase'] = _PROJECT_BASE
        if os.name in ('nt', 'os2'):
            _init_non_posix(_CONFIG_VARS)
        if os.name == 'posix':
            _init_posix(_CONFIG_VARS)
        _CONFIG_VARS['userbase'] = _getuserbase()
        if 'srcdir' not in _CONFIG_VARS:
            _CONFIG_VARS['srcdir'] = _PROJECT_BASE
        if _PYTHON_BUILD and os.name == 'posix':
            base = _PROJECT_BASE
            try:
                cwd = os.getcwd()
            except OSError:
                cwd = None

            if not os.path.isabs(_CONFIG_VARS['srcdir']) and base != cwd:
                srcdir = os.path.join(base, _CONFIG_VARS['srcdir'])
                _CONFIG_VARS['srcdir'] = os.path.normpath(srcdir)
        if sys.platform == 'darwin':
            kernel_version = os.uname()[2]
            major_version = int(kernel_version.split('.')[0])
            if major_version < 8:
                for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                    flags = _CONFIG_VARS[key]
                    flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
                    flags = re.sub('-isysroot [^ \t]*', ' ', flags)
                    _CONFIG_VARS[key] = flags

            else:
                if 'ARCHFLAGS' in os.environ:
                    arch = os.environ['ARCHFLAGS']
                    for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                        flags = _CONFIG_VARS[key]
                        flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
                        flags = flags + ' ' + arch
                        _CONFIG_VARS[key] = flags

                CFLAGS = _CONFIG_VARS.get('CFLAGS', '')
                m = re.search('-isysroot\\s+(\\S+)', CFLAGS)
                if m is not None:
                    sdk = m.group(1)
                    if not os.path.exists(sdk):
                        for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                            flags = _CONFIG_VARS[key]
                            flags = re.sub('-isysroot\\s+\\S+(\\s|$)', ' ', flags)
                            _CONFIG_VARS[key] = flags

    if args:
        vals = []
        for name in args:
            vals.append(_CONFIG_VARS.get(name))

        return vals
    else:
        return _CONFIG_VARS


def get_config_var(name):
    return get_config_vars().get(name)


def get_platform():
    import re
    if os.name == 'nt':
        prefix = ' bit ('
        i = sys.version.find(prefix)
        if i == -1:
            return sys.platform
        j = sys.version.find(')', i)
        look = sys.version[i + len(prefix):j].lower()
        if look == 'amd64':
            return 'win-amd64'
        if look == 'itanium':
            return 'win-ia64'
        return sys.platform
    if os.name != 'posix' or not hasattr(os, 'uname'):
        return sys.platform
    osname, host, release, version, machine = os.uname()
    osname = osname.lower().replace('/', '')
    machine = machine.replace(' ', '_')
    machine = machine.replace('/', '-')
    if osname[:5] == 'linux':
        return '%s-%s' % (osname, machine)
    if osname[:5] == 'sunos':
        if release[0] >= '5':
            osname = 'solaris'
            release = '%d.%s' % (int(release[0]) - 3, release[2:])
    else:
        if osname[:4] == 'irix':
            return '%s-%s' % (osname, release)
        if osname[:3] == 'aix':
            return '%s-%s.%s' % (osname, version, release)
        if osname[:6] == 'cygwin':
            osname = 'cygwin'
            rel_re = re.compile('[\\d.]+')
            m = rel_re.match(release)
            if m:
                release = m.group()
        elif osname[:6] == 'darwin':
            cfgvars = get_config_vars()
            macver = os.environ.get('MACOSX_DEPLOYMENT_TARGET')
            if not macver:
                macver = cfgvars.get('MACOSX_DEPLOYMENT_TARGET')
            macrelease = macver
            try:
                f = open('/System/Library/CoreServices/SystemVersion.plist')
            except IOError:
                pass
            else:
                try:
                    m = re.search('<key>ProductUserVisibleVersion</key>\\s*' + '<string>(.*?)</string>', f.read())
                    f.close()
                    if m is not None:
                        macrelease = '.'.join(m.group(1).split('.')[:2])
                finally:
                    f.close()

            if not macver:
                macver = macrelease
            if macver:
                release = macver
                osname = 'macosx'
                if macrelease + '.' >= '10.4.' and '-arch' in get_config_vars().get('CFLAGS', '').strip():
                    machine = 'fat'
                    cflags = get_config_vars().get('CFLAGS')
                    archs = re.findall('-arch\\s+(\\S+)', cflags)
                    archs = tuple(sorted(set(archs)))
                    if len(archs) == 1:
                        machine = archs[0]
                    elif archs == ('i386', 'ppc'):
                        machine = 'fat'
                    elif archs == ('i386', 'x86_64'):
                        machine = 'intel'
                    elif archs == ('i386', 'ppc', 'x86_64'):
                        machine = 'fat3'
                    elif archs == ('ppc64', 'x86_64'):
                        machine = 'fat64'
                    elif archs == ('i386', 'ppc', 'ppc64', 'x86_64'):
                        machine = 'universal'
                    else:
                        raise ValueError("Don't know machine value for archs=%r" % (archs,))
                elif machine == 'i386':
                    if sys.maxint >= 4294967296L:
                        machine = 'x86_64'
                elif machine in ('PowerPC', 'Power_Macintosh'):
                    if sys.maxint >= 4294967296L:
                        machine = 'ppc64'
                    else:
                        machine = 'ppc'
    return '%s-%s-%s' % (osname, release, machine)


def get_python_version():
    return _PY_VERSION_SHORT