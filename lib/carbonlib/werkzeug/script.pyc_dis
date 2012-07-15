#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\script.py
import sys
import inspect
import getopt
from os.path import basename
argument_types = {bool: 'boolean',
 str: 'string',
 int: 'integer',
 float: 'float'}
converters = {'boolean': lambda x: x.lower() in ('1', 'true', 'yes', 'on'),
 'string': str,
 'integer': int,
 'float': float}

def run(namespace = None, action_prefix = 'action_', args = None):
    if namespace is None:
        namespace = sys._getframe(1).f_locals
    actions = find_actions(namespace, action_prefix)
    if args is None:
        args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        return print_usage(actions)
    if args[0] not in actions:
        fail("Unknown action '%s'" % args[0])
    arguments = {}
    types = {}
    key_to_arg = {}
    long_options = []
    formatstring = ''
    func, doc, arg_def = actions[args.pop(0)]
    for idx, (arg, shortcut, default, option_type) in enumerate(arg_def):
        real_arg = arg.replace('-', '_')
        if shortcut:
            formatstring += shortcut
            if not isinstance(default, bool):
                formatstring += ':'
            key_to_arg['-' + shortcut] = real_arg
        long_options.append(isinstance(default, bool) and arg or arg + '=')
        key_to_arg['--' + arg] = real_arg
        key_to_arg[idx] = real_arg
        types[real_arg] = option_type
        arguments[real_arg] = default

    try:
        optlist, posargs = getopt.gnu_getopt(args, formatstring, long_options)
    except getopt.GetoptError as e:
        fail(str(e))

    specified_arguments = set()
    for key, value in enumerate(posargs):
        try:
            arg = key_to_arg[key]
        except IndexError:
            fail('Too many parameters')

        specified_arguments.add(arg)
        try:
            arguments[arg] = converters[types[arg]](value)
        except ValueError:
            fail('Invalid value for argument %s (%s): %s' % (key, arg, value))

    for key, value in optlist:
        arg = key_to_arg[key]
        if arg in specified_arguments:
            fail("Argument '%s' is specified twice" % arg)
        if types[arg] == 'boolean':
            if arg.startswith('no_'):
                value = 'no'
            else:
                value = 'yes'
        try:
            arguments[arg] = converters[types[arg]](value)
        except ValueError:
            fail("Invalid value for '%s': %s" % (key, value))

    newargs = {}
    for k, v in arguments.iteritems():
        newargs[k.startswith('no_') and k[3:] or k] = v

    arguments = newargs
    return func(**arguments)


def fail(message, code = -1):
    print >> sys.stderr, 'Error:', message
    sys.exit(code)


def find_actions(namespace, action_prefix):
    actions = {}
    for key, value in namespace.iteritems():
        if key.startswith(action_prefix):
            actions[key[len(action_prefix):]] = analyse_action(value)

    return actions


def print_usage(actions):
    actions = actions.items()
    actions.sort()
    print 'usage: %s <action> [<options>]' % basename(sys.argv[0])
    print '       %s --help' % basename(sys.argv[0])
    print
    print 'actions:'
    for name, (func, doc, arguments) in actions:
        print '  %s:' % name
        for line in doc.splitlines():
            print '    %s' % line

        if arguments:
            print
        for arg, shortcut, default, argtype in arguments:
            if isinstance(default, bool):
                print '    %s' % ((shortcut and '-%s, ' % shortcut or '') + '--' + arg)
            else:
                print '    %-30s%-10s%s' % ((shortcut and '-%s, ' % shortcut or '') + '--' + arg, argtype, default)

        print


def analyse_action(func):
    description = inspect.getdoc(func) or 'undocumented action'
    arguments = []
    args, varargs, kwargs, defaults = inspect.getargspec(func)
    if varargs or kwargs:
        raise TypeError('variable length arguments for action not allowed.')
    if len(args) != len(defaults or ()):
        raise TypeError('not all arguments have proper definitions')
    for idx, (arg, definition) in enumerate(zip(args, defaults or ())):
        if arg.startswith('_'):
            raise TypeError('arguments may not start with an underscore')
        if not isinstance(definition, tuple):
            shortcut = None
            default = definition
        else:
            shortcut, default = definition
        argument_type = argument_types[type(default)]
        if isinstance(default, bool) and default is True:
            arg = 'no-' + arg
        arguments.append((arg.replace('_', '-'),
         shortcut,
         default,
         argument_type))

    return (func, description, arguments)


def make_shell(init_func = None, banner = None, use_ipython = True):
    if banner is None:
        banner = 'Interactive Werkzeug Shell'
    if init_func is None:
        init_func = dict

    def action(ipython = use_ipython):
        namespace = init_func()
        if ipython:
            try:
                import IPython
            except ImportError:
                pass
            else:
                sh = IPython.Shell.IPShellEmbed(banner=banner)
                sh(global_ns={}, local_ns=namespace)
                return

        from code import interact
        interact(banner, local=namespace)

    return action


def make_runserver(app_factory, hostname = 'localhost', port = 5000, use_reloader = False, use_debugger = False, use_evalex = True, threaded = False, processes = 1, static_files = None, extra_files = None, ssl_context = None):

    def action(hostname = ('h', hostname), port = ('p', port), reloader = use_reloader, debugger = use_debugger, evalex = use_evalex, threaded = threaded, processes = processes):
        from werkzeug.serving import run_simple
        app = app_factory()
        run_simple(hostname, port, app, reloader, debugger, evalex, extra_files, 1, threaded, processes, static_files=static_files, ssl_context=ssl_context)

    return action