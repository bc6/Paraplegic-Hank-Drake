#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\compiler.py
from cStringIO import StringIO
from itertools import chain
from copy import deepcopy
from jinja2 import nodes
from jinja2.nodes import EvalContext
from jinja2.visitor import NodeVisitor
from jinja2.exceptions import TemplateAssertionError
from jinja2.utils import Markup, concat, escape, is_python_keyword, next
operators = {'eq': '==',
 'ne': '!=',
 'gt': '>',
 'gteq': '>=',
 'lt': '<',
 'lteq': '<=',
 'in': 'in',
 'notin': 'not in'}
try:
    exec '(0 if 0 else 0)'
except SyntaxError:
    have_condexpr = False
else:
    have_condexpr = True

if hasattr(dict, 'iteritems'):
    dict_item_iter = 'iteritems'
else:
    dict_item_iter = 'items'

def unoptimize_before_dead_code():
    x = 42

    def f():
        pass

    return f


unoptimize_before_dead_code = bool(unoptimize_before_dead_code().func_closure)

def generate(node, environment, name, filename, stream = None, defer_init = False):
    if not isinstance(node, nodes.Template):
        raise TypeError("Can't compile non template nodes")
    generator = CodeGenerator(environment, name, filename, stream, defer_init)
    generator.visit(node)
    if stream is None:
        return generator.stream.getvalue()


def has_safe_repr(value):
    if value is None or value is NotImplemented or value is Ellipsis:
        return True
    if isinstance(value, (bool,
     int,
     long,
     float,
     complex,
     basestring,
     xrange,
     Markup)):
        return True
    if isinstance(value, (tuple,
     list,
     set,
     frozenset)):
        for item in value:
            if not has_safe_repr(item):
                return False

        return True
    if isinstance(value, dict):
        for key, value in value.iteritems():
            if not has_safe_repr(key):
                return False
            if not has_safe_repr(value):
                return False

        return True
    return False


def find_undeclared(nodes, names):
    visitor = UndeclaredNameVisitor(names)
    try:
        for node in nodes:
            visitor.visit(node)

    except VisitorExit:
        pass

    return visitor.undeclared


class Identifiers(object):

    def __init__(self):
        self.declared = set()
        self.outer_undeclared = set()
        self.undeclared = set()
        self.declared_locally = set()
        self.declared_parameter = set()

    def add_special(self, name):
        self.undeclared.discard(name)
        self.declared.add(name)

    def is_declared(self, name):
        if name in self.declared_locally or name in self.declared_parameter:
            return True
        return name in self.declared

    def copy(self):
        return deepcopy(self)


class Frame(object):

    def __init__(self, eval_ctx, parent = None):
        self.eval_ctx = eval_ctx
        self.identifiers = Identifiers()
        self.toplevel = False
        self.rootlevel = False
        self.require_output_check = parent and parent.require_output_check
        self.buffer = None
        self.block = parent and parent.block or None
        self.assigned_names = set()
        self.parent = parent
        if parent is not None:
            self.identifiers.declared.update(parent.identifiers.declared | parent.identifiers.declared_parameter | parent.assigned_names)
            self.identifiers.outer_undeclared.update(parent.identifiers.undeclared - self.identifiers.declared)
            self.buffer = parent.buffer

    def copy(self):
        rv = object.__new__(self.__class__)
        rv.__dict__.update(self.__dict__)
        rv.identifiers = object.__new__(self.identifiers.__class__)
        rv.identifiers.__dict__.update(self.identifiers.__dict__)
        return rv

    def inspect(self, nodes):
        visitor = FrameIdentifierVisitor(self.identifiers)
        for node in nodes:
            visitor.visit(node)

    def find_shadowed(self, extra = ()):
        i = self.identifiers
        return (i.declared | i.outer_undeclared) & (i.declared_locally | i.declared_parameter) | set((x for x in extra if i.is_declared(x)))

    def inner(self):
        return Frame(self.eval_ctx, self)

    def soft(self):
        rv = self.copy()
        rv.rootlevel = False
        return rv

    __copy__ = copy


class VisitorExit(RuntimeError):
    pass


class DependencyFinderVisitor(NodeVisitor):

    def __init__(self):
        self.filters = set()
        self.tests = set()

    def visit_Filter(self, node):
        self.generic_visit(node)
        self.filters.add(node.name)

    def visit_Test(self, node):
        self.generic_visit(node)
        self.tests.add(node.name)

    def visit_Block(self, node):
        pass


class UndeclaredNameVisitor(NodeVisitor):

    def __init__(self, names):
        self.names = set(names)
        self.undeclared = set()

    def visit_Name(self, node):
        if node.ctx == 'load' and node.name in self.names:
            self.undeclared.add(node.name)
            if self.undeclared == self.names:
                raise VisitorExit()
        else:
            self.names.discard(node.name)

    def visit_Block(self, node):
        pass


class FrameIdentifierVisitor(NodeVisitor):

    def __init__(self, identifiers):
        self.identifiers = identifiers

    def visit_Name(self, node):
        if node.ctx == 'store':
            self.identifiers.declared_locally.add(node.name)
        elif node.ctx == 'param':
            self.identifiers.declared_parameter.add(node.name)
        elif node.ctx == 'load' and not self.identifiers.is_declared(node.name):
            self.identifiers.undeclared.add(node.name)

    def visit_If(self, node):
        self.visit(node.test)
        real_identifiers = self.identifiers
        old_names = real_identifiers.declared_locally | real_identifiers.declared_parameter

        def inner_visit(nodes):
            if not nodes:
                return set()
            self.identifiers = real_identifiers.copy()
            for subnode in nodes:
                self.visit(subnode)

            rv = self.identifiers.declared_locally - old_names
            real_identifiers.undeclared.update(self.identifiers.undeclared)
            self.identifiers = real_identifiers
            return rv

        body = inner_visit(node.body)
        else_ = inner_visit(node.else_ or ())
        real_identifiers.undeclared.update(body.symmetric_difference(else_) - real_identifiers.declared)
        real_identifiers.declared_locally.update(body | else_)

    def visit_Macro(self, node):
        self.identifiers.declared_locally.add(node.name)

    def visit_Import(self, node):
        self.generic_visit(node)
        self.identifiers.declared_locally.add(node.target)

    def visit_FromImport(self, node):
        self.generic_visit(node)
        for name in node.names:
            if isinstance(name, tuple):
                self.identifiers.declared_locally.add(name[1])
            else:
                self.identifiers.declared_locally.add(name)

    def visit_Assign(self, node):
        self.visit(node.node)
        self.visit(node.target)

    def visit_For(self, node):
        self.visit(node.iter)

    def visit_CallBlock(self, node):
        self.visit(node.call)

    def visit_FilterBlock(self, node):
        self.visit(node.filter)

    def visit_Scope(self, node):
        pass

    def visit_Block(self, node):
        pass


class CompilerExit(Exception):
    pass


class CodeGenerator(NodeVisitor):

    def __init__(self, environment, name, filename, stream = None, defer_init = False):
        if stream is None:
            stream = StringIO()
        self.environment = environment
        self.name = name
        self.filename = filename
        self.stream = stream
        self.created_block_context = False
        self.defer_init = defer_init
        self.import_aliases = {}
        self.blocks = {}
        self.extends_so_far = 0
        self.has_known_extends = False
        self.code_lineno = 1
        self.tests = {}
        self.filters = {}
        self.debug_info = []
        self._write_debug_info = None
        self._new_lines = 0
        self._last_line = 0
        self._first_write = True
        self._last_identifier = 0
        self._indentation = 0

    def fail(self, msg, lineno):
        raise TemplateAssertionError(msg, lineno, self.name, self.filename)

    def temporary_identifier(self):
        self._last_identifier += 1
        return 't_%d' % self._last_identifier

    def buffer(self, frame):
        frame.buffer = self.temporary_identifier()
        self.writeline('%s = []' % frame.buffer)

    def return_buffer_contents(self, frame):
        if frame.eval_ctx.volatile:
            self.writeline('if context.eval_ctx.autoescape:')
            self.indent()
            self.writeline('return Markup(concat(%s))' % frame.buffer)
            self.outdent()
            self.writeline('else:')
            self.indent()
            self.writeline('return concat(%s)' % frame.buffer)
            self.outdent()
        elif frame.eval_ctx.autoescape:
            self.writeline('return Markup(concat(%s))' % frame.buffer)
        else:
            self.writeline('return concat(%s)' % frame.buffer)

    def indent(self):
        self._indentation += 1

    def outdent(self, step = 1):
        self._indentation -= step

    def start_write(self, frame, node = None):
        if frame.buffer is None:
            self.writeline('yield ', node)
        else:
            self.writeline('%s.append(' % frame.buffer, node)

    def end_write(self, frame):
        if frame.buffer is not None:
            self.write(')')

    def simple_write(self, s, frame, node = None):
        self.start_write(frame, node)
        self.write(s)
        self.end_write(frame)

    def blockvisit(self, nodes, frame):
        if frame.buffer is None:
            self.writeline('if 0: yield None')
        else:
            self.writeline('pass')
        try:
            for node in nodes:
                self.visit(node, frame)

        except CompilerExit:
            pass

    def write(self, x):
        if self._new_lines:
            if not self._first_write:
                self.stream.write('\n' * self._new_lines)
                self.code_lineno += self._new_lines
                if self._write_debug_info is not None:
                    self.debug_info.append((self._write_debug_info, self.code_lineno))
                    self._write_debug_info = None
            self._first_write = False
            self.stream.write('    ' * self._indentation)
            self._new_lines = 0
        self.stream.write(x)

    def writeline(self, x, node = None, extra = 0):
        self.newline(node, extra)
        self.write(x)

    def newline(self, node = None, extra = 0):
        self._new_lines = max(self._new_lines, 1 + extra)
        if node is not None and node.lineno != self._last_line:
            self._write_debug_info = node.lineno
            self._last_line = node.lineno

    def signature(self, node, frame, extra_kwargs = None):
        kwarg_workaround = False
        for kwarg in chain((x.key for x in node.kwargs), extra_kwargs or ()):
            if is_python_keyword(kwarg):
                kwarg_workaround = True
                break

        for arg in node.args:
            self.write(', ')
            self.visit(arg, frame)

        if not kwarg_workaround:
            for kwarg in node.kwargs:
                self.write(', ')
                self.visit(kwarg, frame)

            if extra_kwargs is not None:
                for key, value in extra_kwargs.iteritems():
                    self.write(', %s=%s' % (key, value))

        if node.dyn_args:
            self.write(', *')
            self.visit(node.dyn_args, frame)
        if kwarg_workaround:
            if node.dyn_kwargs is not None:
                self.write(', **dict({')
            else:
                self.write(', **{')
            for kwarg in node.kwargs:
                self.write('%r: ' % kwarg.key)
                self.visit(kwarg.value, frame)
                self.write(', ')

            if extra_kwargs is not None:
                for key, value in extra_kwargs.iteritems():
                    self.write('%r: %s, ' % (key, value))

            if node.dyn_kwargs is not None:
                self.write('}, **')
                self.visit(node.dyn_kwargs, frame)
                self.write(')')
            else:
                self.write('}')
        elif node.dyn_kwargs is not None:
            self.write(', **')
            self.visit(node.dyn_kwargs, frame)

    def pull_locals(self, frame):
        for name in frame.identifiers.undeclared:
            self.writeline('l_%s = context.resolve(%r)' % (name, name))

    def pull_dependencies(self, nodes):
        visitor = DependencyFinderVisitor()
        for node in nodes:
            visitor.visit(node)

        for dependency in ('filters', 'tests'):
            mapping = getattr(self, dependency)
            for name in getattr(visitor, dependency):
                if name not in mapping:
                    mapping[name] = self.temporary_identifier()
                self.writeline('%s = environment.%s[%r]' % (mapping[name], dependency, name))

    def unoptimize_scope(self, frame):
        if frame.identifiers.declared:
            self.writeline('%sdummy(%s)' % (unoptimize_before_dead_code and 'if 0: ' or '', ', '.join(('l_' + name for name in frame.identifiers.declared))))

    def push_scope(self, frame, extra_vars = ()):
        aliases = {}
        for name in frame.find_shadowed(extra_vars):
            aliases[name] = ident = self.temporary_identifier()
            self.writeline('%s = l_%s' % (ident, name))

        to_declare = set()
        for name in frame.identifiers.declared_locally:
            if name not in aliases:
                to_declare.add('l_' + name)

        if to_declare:
            self.writeline(' = '.join(to_declare) + ' = missing')
        return aliases

    def pop_scope(self, aliases, frame):
        for name, alias in aliases.iteritems():
            self.writeline('l_%s = %s' % (name, alias))

        to_delete = set()
        for name in frame.identifiers.declared_locally:
            if name not in aliases:
                to_delete.add('l_' + name)

        if to_delete:
            self.writeline(' = '.join(to_delete) + ' = missing')

    def function_scoping(self, node, frame, children = None, find_special = True):
        if children is None:
            children = node.iter_child_nodes()
        children = list(children)
        func_frame = frame.inner()
        func_frame.inspect(children)
        overriden_closure_vars = func_frame.identifiers.undeclared & func_frame.identifiers.declared & (func_frame.identifiers.declared_locally | func_frame.identifiers.declared_parameter)
        if overriden_closure_vars:
            self.fail("It's not possible to set and access variables derived from an outer scope! (affects: %s)" % ', '.join(sorted(overriden_closure_vars)), node.lineno)
        func_frame.identifiers.undeclared -= func_frame.identifiers.undeclared & func_frame.identifiers.declared
        if not find_special:
            return func_frame
        func_frame.accesses_kwargs = False
        func_frame.accesses_varargs = False
        func_frame.accesses_caller = False
        func_frame.arguments = args = [ 'l_' + x.name for x in node.args ]
        undeclared = find_undeclared(children, ('caller', 'kwargs', 'varargs'))
        if 'caller' in undeclared:
            func_frame.accesses_caller = True
            func_frame.identifiers.add_special('caller')
            args.append('l_caller')
        if 'kwargs' in undeclared:
            func_frame.accesses_kwargs = True
            func_frame.identifiers.add_special('kwargs')
            args.append('l_kwargs')
        if 'varargs' in undeclared:
            func_frame.accesses_varargs = True
            func_frame.identifiers.add_special('varargs')
            args.append('l_varargs')
        return func_frame

    def macro_body(self, node, frame, children = None):
        frame = self.function_scoping(node, frame, children)
        frame.require_output_check = False
        args = frame.arguments
        if 'loop' in frame.identifiers.declared:
            args = args + ['l_loop=l_loop']
        self.writeline('def macro(%s):' % ', '.join(args), node)
        self.indent()
        self.buffer(frame)
        self.pull_locals(frame)
        self.blockvisit(node.body, frame)
        self.return_buffer_contents(frame)
        self.outdent()
        return frame

    def macro_def(self, node, frame):
        arg_tuple = ', '.join((repr(x.name) for x in node.args))
        name = getattr(node, 'name', None)
        if len(node.args) == 1:
            arg_tuple += ','
        self.write('Macro(environment, macro, %r, (%s), (' % (name, arg_tuple))
        for arg in node.defaults:
            self.visit(arg, frame)
            self.write(', ')

        self.write('), %r, %r, %r)' % (bool(frame.accesses_kwargs), bool(frame.accesses_varargs), bool(frame.accesses_caller)))

    def position(self, node):
        rv = 'line %d' % node.lineno
        if self.name is not None:
            rv += ' in ' + repr(self.name)
        return rv

    def visit_Template(self, node, frame = None):
        eval_ctx = EvalContext(self.environment, self.name)
        from jinja2.runtime import __all__ as exported
        self.writeline('from __future__ import division')
        self.writeline('from jinja2.runtime import ' + ', '.join(exported))
        if not unoptimize_before_dead_code:
            self.writeline('dummy = lambda *x: None')
        envenv = not self.defer_init and ', environment=environment' or ''
        have_extends = node.find(nodes.Extends) is not None
        for block in node.find_all(nodes.Block):
            if block.name in self.blocks:
                self.fail('block %r defined twice' % block.name, block.lineno)
            self.blocks[block.name] = block

        for import_ in node.find_all(nodes.ImportedName):
            if import_.importname not in self.import_aliases:
                imp = import_.importname
                self.import_aliases[imp] = alias = self.temporary_identifier()
                if '.' in imp:
                    module, obj = imp.rsplit('.', 1)
                    self.writeline('from %s import %s as %s' % (module, obj, alias))
                else:
                    self.writeline('import %s as %s' % (imp, alias))

        self.writeline('name = %r' % self.name)
        self.writeline('def root(context%s):' % envenv, extra=1)
        frame = Frame(eval_ctx)
        frame.inspect(node.body)
        frame.toplevel = frame.rootlevel = True
        frame.require_output_check = have_extends and not self.has_known_extends
        self.indent()
        if have_extends:
            self.writeline('parent_template = None')
        if 'self' in find_undeclared(node.body, ('self',)):
            frame.identifiers.add_special('self')
            self.writeline('l_self = TemplateReference(context)')
        self.pull_locals(frame)
        self.pull_dependencies(node.body)
        self.blockvisit(node.body, frame)
        self.outdent()
        if have_extends:
            if not self.has_known_extends:
                self.indent()
                self.writeline('if parent_template is not None:')
            self.indent()
            self.writeline('for event in parent_template.root_render_func(context):')
            self.indent()
            self.writeline('yield event')
            self.outdent(2 + (not self.has_known_extends))
        for name, block in self.blocks.iteritems():
            block_frame = Frame(eval_ctx)
            block_frame.inspect(block.body)
            block_frame.block = name
            self.writeline('def block_%s(context%s):' % (name, envenv), block, 1)
            self.indent()
            undeclared = find_undeclared(block.body, ('self', 'super'))
            if 'self' in undeclared:
                block_frame.identifiers.add_special('self')
                self.writeline('l_self = TemplateReference(context)')
            if 'super' in undeclared:
                block_frame.identifiers.add_special('super')
                self.writeline('l_super = context.super(%r, block_%s)' % (name, name))
            self.pull_locals(block_frame)
            self.pull_dependencies(block.body)
            self.blockvisit(block.body, block_frame)
            self.outdent()

        self.writeline('blocks = {%s}' % ', '.join(('%r: block_%s' % (x, x) for x in self.blocks)), extra=1)
        self.writeline('debug_info = %r' % '&'.join(('%s=%s' % x for x in self.debug_info)))

    def visit_Block(self, node, frame):
        level = 1
        if frame.toplevel:
            if self.has_known_extends:
                return
            if self.extends_so_far > 0:
                self.writeline('if parent_template is None:')
                self.indent()
                level += 1
        context = node.scoped and 'context.derived(locals())' or 'context'
        self.writeline('for event in context.blocks[%r][0](%s):' % (node.name, context), node)
        self.indent()
        self.simple_write('event', frame)
        self.outdent(level)

    def visit_Extends(self, node, frame):
        if not frame.toplevel:
            self.fail('cannot use extend from a non top-level scope', node.lineno)
        if self.extends_so_far > 0:
            if not self.has_known_extends:
                self.writeline('if parent_template is not None:')
                self.indent()
            self.writeline('raise TemplateRuntimeError(%r)' % 'extended multiple times')
            self.outdent()
            if self.has_known_extends:
                raise CompilerExit()
        self.writeline('parent_template = environment.get_template(', node)
        self.visit(node.template, frame)
        self.write(', %r)' % self.name)
        self.writeline('for name, parent_block in parent_template.blocks.%s():' % dict_item_iter)
        self.indent()
        self.writeline('context.blocks.setdefault(name, []).append(parent_block)')
        self.outdent()
        if frame.rootlevel:
            self.has_known_extends = True
        self.extends_so_far += 1

    def visit_Include(self, node, frame):
        if node.with_context:
            self.unoptimize_scope(frame)
        if node.ignore_missing:
            self.writeline('try:')
            self.indent()
        func_name = 'get_or_select_template'
        if isinstance(node.template, nodes.Const):
            if isinstance(node.template.value, basestring):
                func_name = 'get_template'
            elif isinstance(node.template.value, (tuple, list)):
                func_name = 'select_template'
        elif isinstance(node.template, (nodes.Tuple, nodes.List)):
            func_name = 'select_template'
        self.writeline('template = environment.%s(' % func_name, node)
        self.visit(node.template, frame)
        self.write(', %r)' % self.name)
        if node.ignore_missing:
            self.outdent()
            self.writeline('except TemplateNotFound:')
            self.indent()
            self.writeline('pass')
            self.outdent()
            self.writeline('else:')
            self.indent()
        if node.with_context:
            self.writeline('for event in template.root_render_func(template.new_context(context.parent, True, locals())):')
        else:
            self.writeline('for event in template.module._body_stream:')
        self.indent()
        self.simple_write('event', frame)
        self.outdent()
        if node.ignore_missing:
            self.outdent()

    def visit_Import(self, node, frame):
        if node.with_context:
            self.unoptimize_scope(frame)
        self.writeline('l_%s = ' % node.target, node)
        if frame.toplevel:
            self.write('context.vars[%r] = ' % node.target)
        self.write('environment.get_template(')
        self.visit(node.template, frame)
        self.write(', %r).' % self.name)
        if node.with_context:
            self.write('make_module(context.parent, True, locals())')
        else:
            self.write('module')
        if frame.toplevel and not node.target.startswith('_'):
            self.writeline('context.exported_vars.discard(%r)' % node.target)
        frame.assigned_names.add(node.target)

    def visit_FromImport(self, node, frame):
        self.newline(node)
        self.write('included_template = environment.get_template(')
        self.visit(node.template, frame)
        self.write(', %r).' % self.name)
        if node.with_context:
            self.write('make_module(context.parent, True)')
        else:
            self.write('module')
        var_names = []
        discarded_names = []
        for name in node.names:
            if isinstance(name, tuple):
                name, alias = name
            else:
                alias = name
            self.writeline('l_%s = getattr(included_template, %r, missing)' % (alias, name))
            self.writeline('if l_%s is missing:' % alias)
            self.indent()
            self.writeline('l_%s = environment.undefined(%r %% included_template.__name__, name=%r)' % (alias, 'the template %%r (imported on %s) does not export the requested name %s' % (self.position(node), repr(name)), name))
            self.outdent()
            if frame.toplevel:
                var_names.append(alias)
                if not alias.startswith('_'):
                    discarded_names.append(alias)
            frame.assigned_names.add(alias)

        if var_names:
            if len(var_names) == 1:
                name = var_names[0]
                self.writeline('context.vars[%r] = l_%s' % (name, name))
            else:
                self.writeline('context.vars.update({%s})' % ', '.join(('%r: l_%s' % (name, name) for name in var_names)))
        if discarded_names:
            if len(discarded_names) == 1:
                self.writeline('context.exported_vars.discard(%r)' % discarded_names[0])
            else:
                self.writeline('context.exported_vars.difference_update((%s))' % ', '.join(map(repr, discarded_names)))

    def visit_For(self, node, frame):
        children = node.iter_child_nodes(exclude=('iter',))
        if node.recursive:
            loop_frame = self.function_scoping(node, frame, children, find_special=False)
        else:
            loop_frame = frame.inner()
            loop_frame.inspect(children)
        extended_loop = node.recursive or 'loop' in find_undeclared(node.iter_child_nodes(only=('body',)), ('loop',))
        if not node.recursive:
            aliases = self.push_scope(loop_frame, ('loop',))
        else:
            self.writeline('def loop(reciter, loop_render_func):', node)
            self.indent()
            self.buffer(loop_frame)
            aliases = {}
        if extended_loop:
            loop_frame.identifiers.add_special('loop')
        for name in node.find_all(nodes.Name):
            if name.ctx == 'store' and name.name == 'loop':
                self.fail("Can't assign to special loop variable in for-loop target", name.lineno)

        self.pull_locals(loop_frame)
        if node.else_:
            iteration_indicator = self.temporary_identifier()
            self.writeline('%s = 1' % iteration_indicator)
        if 'loop' not in aliases and 'loop' in find_undeclared(node.iter_child_nodes(only=('else_', 'test')), ('loop',)):
            self.writeline("l_loop = environment.undefined(%r, name='loop')" % ("'loop' is undefined. the filter section of a loop as well as the else block don't have access to the special 'loop' variable of the current loop.  Because there is no parent loop it's undefined.  Happened in loop on %s" % self.position(node)))
        self.writeline('for ', node)
        self.visit(node.target, loop_frame)
        self.write(extended_loop and ', l_loop in LoopContext(' or ' in ')
        if extended_loop and node.test is not None:
            self.write('(')
            self.visit(node.target, loop_frame)
            self.write(' for ')
            self.visit(node.target, loop_frame)
            self.write(' in ')
            if node.recursive:
                self.write('reciter')
            else:
                self.visit(node.iter, loop_frame)
            self.write(' if (')
            test_frame = loop_frame.copy()
            self.visit(node.test, test_frame)
            self.write('))')
        elif node.recursive:
            self.write('reciter')
        else:
            self.visit(node.iter, loop_frame)
        if node.recursive:
            self.write(', recurse=loop_render_func):')
        else:
            self.write(extended_loop and '):' or ':')
        if not extended_loop and node.test is not None:
            self.indent()
            self.writeline('if not ')
            self.visit(node.test, loop_frame)
            self.write(':')
            self.indent()
            self.writeline('continue')
            self.outdent(2)
        self.indent()
        self.blockvisit(node.body, loop_frame)
        if node.else_:
            self.writeline('%s = 0' % iteration_indicator)
        self.outdent()
        if node.else_:
            self.writeline('if %s:' % iteration_indicator)
            self.indent()
            self.blockvisit(node.else_, loop_frame)
            self.outdent()
        if not node.recursive:
            self.pop_scope(aliases, loop_frame)
        if node.recursive:
            self.return_buffer_contents(loop_frame)
            self.outdent()
            self.start_write(frame, node)
            self.write('loop(')
            self.visit(node.iter, frame)
            self.write(', loop)')
            self.end_write(frame)

    def visit_If(self, node, frame):
        if_frame = frame.soft()
        self.writeline('if ', node)
        self.visit(node.test, if_frame)
        self.write(':')
        self.indent()
        self.blockvisit(node.body, if_frame)
        self.outdent()
        if node.else_:
            self.writeline('else:')
            self.indent()
            self.blockvisit(node.else_, if_frame)
            self.outdent()

    def visit_Macro(self, node, frame):
        macro_frame = self.macro_body(node, frame)
        self.newline()
        if frame.toplevel:
            if not node.name.startswith('_'):
                self.write('context.exported_vars.add(%r)' % node.name)
            self.writeline('context.vars[%r] = ' % node.name)
        self.write('l_%s = ' % node.name)
        self.macro_def(node, macro_frame)
        frame.assigned_names.add(node.name)

    def visit_CallBlock(self, node, frame):
        children = node.iter_child_nodes(exclude=('call',))
        call_frame = self.macro_body(node, frame, children)
        self.writeline('caller = ')
        self.macro_def(node, call_frame)
        self.start_write(frame, node)
        self.visit_Call(node.call, call_frame, forward_caller=True)
        self.end_write(frame)

    def visit_FilterBlock(self, node, frame):
        filter_frame = frame.inner()
        filter_frame.inspect(node.iter_child_nodes())
        aliases = self.push_scope(filter_frame)
        self.pull_locals(filter_frame)
        self.buffer(filter_frame)
        self.blockvisit(node.body, filter_frame)
        self.start_write(frame, node)
        self.visit_Filter(node.filter, filter_frame)
        self.end_write(frame)
        self.pop_scope(aliases, filter_frame)

    def visit_ExprStmt(self, node, frame):
        self.newline(node)
        self.visit(node.node, frame)

    def visit_Output(self, node, frame):
        if self.has_known_extends and frame.require_output_check:
            return
        if self.environment.finalize:
            finalize = lambda x: unicode(self.environment.finalize(x))
        else:
            finalize = unicode
        outdent_later = False
        if frame.require_output_check:
            self.writeline('if parent_template is None:')
            self.indent()
            outdent_later = True
        body = []
        for child in node.nodes:
            try:
                const = child.as_const(frame.eval_ctx)
            except nodes.Impossible:
                body.append(child)
                continue

            try:
                if frame.eval_ctx.autoescape:
                    if hasattr(const, '__html__'):
                        const = const.__html__()
                    else:
                        const = escape(const)
                const = finalize(const)
            except Exception:
                body.append(child)
                continue

            if body and isinstance(body[-1], list):
                body[-1].append(const)
            else:
                body.append([const])

        if len(body) < 3 or frame.buffer is not None:
            if frame.buffer is not None:
                if len(body) == 1:
                    self.writeline('%s.append(' % frame.buffer)
                else:
                    self.writeline('%s.extend((' % frame.buffer)
                self.indent()
            for item in body:
                if isinstance(item, list):
                    val = repr(concat(item))
                    if frame.buffer is None:
                        self.writeline('yield ' + val)
                    else:
                        self.writeline(val + ', ')
                else:
                    if frame.buffer is None:
                        self.writeline('yield ', item)
                    else:
                        self.newline(item)
                    close = 1
                    if frame.eval_ctx.volatile:
                        self.write('(context.eval_ctx.autoescape and escape or to_string)(')
                    elif frame.eval_ctx.autoescape:
                        self.write('escape(')
                    else:
                        self.write('to_string(')
                    if self.environment.finalize is not None:
                        self.write('environment.finalize(')
                        close += 1
                    self.visit(item, frame)
                    self.write(')' * close)
                    if frame.buffer is not None:
                        self.write(', ')

            if frame.buffer is not None:
                self.outdent()
                self.writeline(len(body) == 1 and ')' or '))')
        else:
            format = []
            arguments = []
            for item in body:
                if isinstance(item, list):
                    format.append(concat(item).replace('%', '%%'))
                else:
                    format.append('%s')
                    arguments.append(item)

            self.writeline('yield ')
            self.write(repr(concat(format)) + ' % (')
            idx = -1
            self.indent()
            for argument in arguments:
                self.newline(argument)
                close = 0
                if frame.eval_ctx.volatile:
                    self.write('(context.eval_ctx.autoescape and escape or to_string)(')
                    close += 1
                elif frame.eval_ctx.autoescape:
                    self.write('escape(')
                    close += 1
                if self.environment.finalize is not None:
                    self.write('environment.finalize(')
                    close += 1
                self.visit(argument, frame)
                self.write(')' * close + ', ')

            self.outdent()
            self.writeline(')')
        if outdent_later:
            self.outdent()

    def visit_Assign(self, node, frame):
        self.newline(node)
        if frame.toplevel:
            assignment_frame = frame.copy()
            assignment_frame.toplevel_assignments = set()
        else:
            assignment_frame = frame
        self.visit(node.target, assignment_frame)
        self.write(' = ')
        self.visit(node.node, frame)
        if frame.toplevel:
            public_names = [ x for x in assignment_frame.toplevel_assignments if not x.startswith('_') ]
            if len(assignment_frame.toplevel_assignments) == 1:
                name = next(iter(assignment_frame.toplevel_assignments))
                self.writeline('context.vars[%r] = l_%s' % (name, name))
            else:
                self.writeline('context.vars.update({')
                for idx, name in enumerate(assignment_frame.toplevel_assignments):
                    if idx:
                        self.write(', ')
                    self.write('%r: l_%s' % (name, name))

                self.write('})')
            if public_names:
                if len(public_names) == 1:
                    self.writeline('context.exported_vars.add(%r)' % public_names[0])
                else:
                    self.writeline('context.exported_vars.update((%s))' % ', '.join(map(repr, public_names)))

    def visit_Name(self, node, frame):
        if node.ctx == 'store' and frame.toplevel:
            frame.toplevel_assignments.add(node.name)
        self.write('l_' + node.name)
        frame.assigned_names.add(node.name)

    def visit_Const(self, node, frame):
        val = node.value
        if isinstance(val, float):
            self.write(str(val))
        else:
            self.write(repr(val))

    def visit_TemplateData(self, node, frame):
        try:
            self.write(repr(node.as_const(frame.eval_ctx)))
        except nodes.Impossible:
            self.write('(context.eval_ctx.autoescape and Markup or identity)(%r)' % node.data)

    def visit_Tuple(self, node, frame):
        self.write('(')
        idx = -1
        for idx, item in enumerate(node.items):
            if idx:
                self.write(', ')
            self.visit(item, frame)

        self.write(idx == 0 and ',)' or ')')

    def visit_List(self, node, frame):
        self.write('[')
        for idx, item in enumerate(node.items):
            if idx:
                self.write(', ')
            self.visit(item, frame)

        self.write(']')

    def visit_Dict(self, node, frame):
        self.write('{')
        for idx, item in enumerate(node.items):
            if idx:
                self.write(', ')
            self.visit(item.key, frame)
            self.write(': ')
            self.visit(item.value, frame)

        self.write('}')

    def binop(operator, interceptable = True):

        def visitor(self, node, frame):
            if self.environment.sandboxed and operator in self.environment.intercepted_binops:
                self.write('environment.call_binop(context, %r, ' % operator)
                self.visit(node.left, frame)
                self.write(', ')
                self.visit(node.right, frame)
            else:
                self.write('(')
                self.visit(node.left, frame)
                self.write(' %s ' % operator)
                self.visit(node.right, frame)
            self.write(')')

        return visitor

    def uaop(operator, interceptable = True):

        def visitor(self, node, frame):
            if self.environment.sandboxed and operator in self.environment.intercepted_unops:
                self.write('environment.call_unop(context, %r, ' % operator)
                self.visit(node.node, frame)
            else:
                self.write('(' + operator)
                self.visit(node.node, frame)
            self.write(')')

        return visitor

    visit_Add = binop('+')
    visit_Sub = binop('-')
    visit_Mul = binop('*')
    visit_Div = binop('/')
    visit_FloorDiv = binop('//')
    visit_Pow = binop('**')
    visit_Mod = binop('%')
    visit_And = binop('and', interceptable=False)
    visit_Or = binop('or', interceptable=False)
    visit_Pos = uaop('+')
    visit_Neg = uaop('-')
    visit_Not = uaop('not ', interceptable=False)
    del binop
    del uaop

    def visit_Concat(self, node, frame):
        if frame.eval_ctx.volatile:
            func_name = '(context.eval_ctx.volatile and markup_join or unicode_join)'
        elif frame.eval_ctx.autoescape:
            func_name = 'markup_join'
        else:
            func_name = 'unicode_join'
        self.write('%s((' % func_name)
        for arg in node.nodes:
            self.visit(arg, frame)
            self.write(', ')

        self.write('))')

    def visit_Compare(self, node, frame):
        self.visit(node.expr, frame)
        for op in node.ops:
            self.visit(op, frame)

    def visit_Operand(self, node, frame):
        self.write(' %s ' % operators[node.op])
        self.visit(node.expr, frame)

    def visit_Getattr(self, node, frame):
        self.write('environment.getattr(')
        self.visit(node.node, frame)
        self.write(', %r)' % node.attr)

    def visit_Getitem(self, node, frame):
        if isinstance(node.arg, nodes.Slice):
            self.visit(node.node, frame)
            self.write('[')
            self.visit(node.arg, frame)
            self.write(']')
        else:
            self.write('environment.getitem(')
            self.visit(node.node, frame)
            self.write(', ')
            self.visit(node.arg, frame)
            self.write(')')

    def visit_Slice(self, node, frame):
        if node.start is not None:
            self.visit(node.start, frame)
        self.write(':')
        if node.stop is not None:
            self.visit(node.stop, frame)
        if node.step is not None:
            self.write(':')
            self.visit(node.step, frame)

    def visit_Filter(self, node, frame):
        self.write(self.filters[node.name] + '(')
        func = self.environment.filters.get(node.name)
        if func is None:
            self.fail('no filter named %r' % node.name, node.lineno)
        if getattr(func, 'contextfilter', False):
            self.write('context, ')
        elif getattr(func, 'evalcontextfilter', False):
            self.write('context.eval_ctx, ')
        elif getattr(func, 'environmentfilter', False):
            self.write('environment, ')
        if node.node is not None:
            self.visit(node.node, frame)
        elif frame.eval_ctx.volatile:
            self.write('(context.eval_ctx.autoescape and Markup(concat(%s)) or concat(%s))' % (frame.buffer, frame.buffer))
        elif frame.eval_ctx.autoescape:
            self.write('Markup(concat(%s))' % frame.buffer)
        else:
            self.write('concat(%s)' % frame.buffer)
        self.signature(node, frame)
        self.write(')')

    def visit_Test(self, node, frame):
        self.write(self.tests[node.name] + '(')
        if node.name not in self.environment.tests:
            self.fail('no test named %r' % node.name, node.lineno)
        self.visit(node.node, frame)
        self.signature(node, frame)
        self.write(')')

    def visit_CondExpr(self, node, frame):

        def write_expr2():
            if node.expr2 is not None:
                return self.visit(node.expr2, frame)
            self.write('environment.undefined(%r)' % ('the inline if-expression on %s evaluated to false and no else section was defined.' % self.position(node)))

        if not have_condexpr:
            self.write('((')
            self.visit(node.test, frame)
            self.write(') and (')
            self.visit(node.expr1, frame)
            self.write(',) or (')
            write_expr2()
            self.write(',))[0]')
        else:
            self.write('(')
            self.visit(node.expr1, frame)
            self.write(' if ')
            self.visit(node.test, frame)
            self.write(' else ')
            write_expr2()
            self.write(')')

    def visit_Call(self, node, frame, forward_caller = False):
        if self.environment.sandboxed:
            self.write('environment.call(context, ')
        else:
            self.write('context.call(')
        self.visit(node.node, frame)
        extra_kwargs = forward_caller and {'caller': 'caller'} or None
        self.signature(node, frame, extra_kwargs)
        self.write(')')

    def visit_Keyword(self, node, frame):
        self.write(node.key + '=')
        self.visit(node.value, frame)

    def visit_MarkSafe(self, node, frame):
        self.write('Markup(')
        self.visit(node.expr, frame)
        self.write(')')

    def visit_MarkSafeIfAutoescape(self, node, frame):
        self.write('(context.eval_ctx.autoescape and Markup or identity)(')
        self.visit(node.expr, frame)
        self.write(')')

    def visit_EnvironmentAttribute(self, node, frame):
        self.write('environment.' + node.name)

    def visit_ExtensionAttribute(self, node, frame):
        self.write('environment.extensions[%r].%s' % (node.identifier, node.name))

    def visit_ImportedName(self, node, frame):
        self.write(self.import_aliases[node.importname])

    def visit_InternalName(self, node, frame):
        self.write(node.name)

    def visit_ContextReference(self, node, frame):
        self.write('context')

    def visit_Continue(self, node, frame):
        self.writeline('continue', node)

    def visit_Break(self, node, frame):
        self.writeline('break', node)

    def visit_Scope(self, node, frame):
        scope_frame = frame.inner()
        scope_frame.inspect(node.iter_child_nodes())
        aliases = self.push_scope(scope_frame)
        self.pull_locals(scope_frame)
        self.blockvisit(node.body, scope_frame)
        self.pop_scope(aliases, scope_frame)

    def visit_EvalContextModifier(self, node, frame):
        for keyword in node.options:
            self.writeline('context.eval_ctx.%s = ' % keyword.key)
            self.visit(keyword.value, frame)
            try:
                val = keyword.value.as_const(frame.eval_ctx)
            except nodes.Impossible:
                frame.eval_ctx.volatile = True
            else:
                setattr(frame.eval_ctx, keyword.key, val)

    def visit_ScopedEvalContextModifier(self, node, frame):
        old_ctx_name = self.temporary_identifier()
        safed_ctx = frame.eval_ctx.save()
        self.writeline('%s = context.eval_ctx.save()' % old_ctx_name)
        self.visit_EvalContextModifier(node, frame)
        for child in node.body:
            self.visit(child, frame)

        frame.eval_ctx.revert(safed_ctx)
        self.writeline('context.eval_ctx.revert(%s)' % old_ctx_name)