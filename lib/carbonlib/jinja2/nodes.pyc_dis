#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\nodes.py
import operator
from itertools import chain, izip
from collections import deque
from jinja2.utils import Markup, MethodType, FunctionType
_context_function_types = (FunctionType, MethodType)
_binop_to_func = {'*': operator.mul,
 '/': operator.truediv,
 '//': operator.floordiv,
 '**': operator.pow,
 '%': operator.mod,
 '+': operator.add,
 '-': operator.sub}
_uaop_to_func = {'not': operator.not_,
 '+': operator.pos,
 '-': operator.neg}
_cmpop_to_func = {'eq': operator.eq,
 'ne': operator.ne,
 'gt': operator.gt,
 'gteq': operator.ge,
 'lt': operator.lt,
 'lteq': operator.le,
 'in': lambda a, b: a in b,
 'notin': lambda a, b: a not in b}

class Impossible(Exception):
    pass


class NodeType(type):

    def __new__(cls, name, bases, d):
        for attr in ('fields', 'attributes'):
            storage = []
            storage.extend(getattr(bases[0], attr, ()))
            storage.extend(d.get(attr, ()))
            d[attr] = tuple(storage)

        d.setdefault('abstract', False)
        return type.__new__(cls, name, bases, d)


class EvalContext(object):

    def __init__(self, environment, template_name = None):
        self.environment = environment
        if callable(environment.autoescape):
            self.autoescape = environment.autoescape(template_name)
        else:
            self.autoescape = environment.autoescape
        self.volatile = False

    def save(self):
        return self.__dict__.copy()

    def revert(self, old):
        self.__dict__.clear()
        self.__dict__.update(old)


def get_eval_context(node, ctx):
    if ctx is None:
        if node.environment is None:
            raise RuntimeError('if no eval context is passed, the node must have an attached environment.')
        return EvalContext(node.environment)
    return ctx


class Node(object):
    __metaclass__ = NodeType
    fields = ()
    attributes = ('lineno', 'environment')
    abstract = True

    def __init__(self, *fields, **attributes):
        if self.abstract:
            raise TypeError('abstract nodes are not instanciable')
        if fields:
            if len(fields) != len(self.fields):
                if not self.fields:
                    raise TypeError('%r takes 0 arguments' % self.__class__.__name__)
                raise TypeError('%r takes 0 or %d argument%s' % (self.__class__.__name__, len(self.fields), len(self.fields) != 1 and 's' or ''))
            for name, arg in izip(self.fields, fields):
                setattr(self, name, arg)

        for attr in self.attributes:
            setattr(self, attr, attributes.pop(attr, None))

        if attributes:
            raise TypeError('unknown attribute %r' % iter(attributes).next())

    def iter_fields(self, exclude = None, only = None):
        for name in self.fields:
            if exclude is only is None or exclude is not None and name not in exclude or only is not None and name in only:
                try:
                    yield (name, getattr(self, name))
                except AttributeError:
                    pass

    def iter_child_nodes(self, exclude = None, only = None):
        for field, item in self.iter_fields(exclude, only):
            if isinstance(item, list):
                for n in item:
                    if isinstance(n, Node):
                        yield n

            elif isinstance(item, Node):
                yield item

    def find(self, node_type):
        for result in self.find_all(node_type):
            return result

    def find_all(self, node_type):
        for child in self.iter_child_nodes():
            if isinstance(child, node_type):
                yield child
            for result in child.find_all(node_type):
                yield result

    def set_ctx(self, ctx):
        todo = deque([self])
        while todo:
            node = todo.popleft()
            if 'ctx' in node.fields:
                node.ctx = ctx
            todo.extend(node.iter_child_nodes())

        return self

    def set_lineno(self, lineno, override = False):
        todo = deque([self])
        while todo:
            node = todo.popleft()
            if 'lineno' in node.attributes:
                if node.lineno is None or override:
                    node.lineno = lineno
            todo.extend(node.iter_child_nodes())

        return self

    def set_environment(self, environment):
        todo = deque([self])
        while todo:
            node = todo.popleft()
            node.environment = environment
            todo.extend(node.iter_child_nodes())

        return self

    def __eq__(self, other):
        return type(self) is type(other) and tuple(self.iter_fields()) == tuple(other.iter_fields())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(('%s=%r' % (arg, getattr(self, arg, None)) for arg in self.fields)))


class Stmt(Node):
    abstract = True


class Helper(Node):
    abstract = True


class Template(Node):
    fields = ('body',)


class Output(Stmt):
    fields = ('nodes',)


class Extends(Stmt):
    fields = ('template',)


class For(Stmt):
    fields = ('target', 'iter', 'body', 'else_', 'test', 'recursive')


class If(Stmt):
    fields = ('test', 'body', 'else_')


class Macro(Stmt):
    fields = ('name', 'args', 'defaults', 'body')


class CallBlock(Stmt):
    fields = ('call', 'args', 'defaults', 'body')


class FilterBlock(Stmt):
    fields = ('body', 'filter')


class Block(Stmt):
    fields = ('name', 'body', 'scoped')


class Include(Stmt):
    fields = ('template', 'with_context', 'ignore_missing')


class Import(Stmt):
    fields = ('template', 'target', 'with_context')


class FromImport(Stmt):
    fields = ('template', 'names', 'with_context')


class ExprStmt(Stmt):
    fields = ('node',)


class Assign(Stmt):
    fields = ('target', 'node')


class Expr(Node):
    abstract = True

    def as_const(self, eval_ctx = None):
        raise Impossible()

    def can_assign(self):
        return False


class BinExpr(Expr):
    fields = ('left', 'right')
    operator = None
    abstract = True

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if self.environment.sandboxed and self.operator in self.environment.intercepted_binops:
            raise Impossible()
        f = _binop_to_func[self.operator]
        try:
            return f(self.left.as_const(eval_ctx), self.right.as_const(eval_ctx))
        except Exception:
            raise Impossible()


class UnaryExpr(Expr):
    fields = ('node',)
    operator = None
    abstract = True

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if self.environment.sandboxed and self.operator in self.environment.intercepted_unops:
            raise Impossible()
        f = _uaop_to_func[self.operator]
        try:
            return f(self.node.as_const(eval_ctx))
        except Exception:
            raise Impossible()


class Name(Expr):
    fields = ('name', 'ctx')

    def can_assign(self):
        return self.name not in ('true', 'false', 'none', 'True', 'False', 'None')


class Literal(Expr):
    abstract = True


class Const(Literal):
    fields = ('value',)

    def as_const(self, eval_ctx = None):
        return self.value

    @classmethod
    def from_untrusted(cls, value, lineno = None, environment = None):
        from compiler import has_safe_repr
        if not has_safe_repr(value):
            raise Impossible()
        return cls(value, lineno=lineno, environment=environment)


class TemplateData(Literal):
    fields = ('data',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile:
            raise Impossible()
        if eval_ctx.autoescape:
            return Markup(self.data)
        return self.data


class Tuple(Literal):
    fields = ('items', 'ctx')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return tuple((x.as_const(eval_ctx) for x in self.items))

    def can_assign(self):
        for item in self.items:
            if not item.can_assign():
                return False

        return True


class List(Literal):
    fields = ('items',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return [ x.as_const(eval_ctx) for x in self.items ]


class Dict(Literal):
    fields = ('items',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return dict((x.as_const(eval_ctx) for x in self.items))


class Pair(Helper):
    fields = ('key', 'value')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return (self.key.as_const(eval_ctx), self.value.as_const(eval_ctx))


class Keyword(Helper):
    fields = ('key', 'value')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return (self.key, self.value.as_const(eval_ctx))


class CondExpr(Expr):
    fields = ('test', 'expr1', 'expr2')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if self.test.as_const(eval_ctx):
            return self.expr1.as_const(eval_ctx)
        if self.expr2 is None:
            raise Impossible()
        return self.expr2.as_const(eval_ctx)


class Filter(Expr):
    fields = ('node', 'name', 'args', 'kwargs', 'dyn_args', 'dyn_kwargs')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile or self.node is None:
            raise Impossible()
        filter_ = self.environment.filters.get(self.name)
        if filter_ is None or getattr(filter_, 'contextfilter', False):
            raise Impossible()
        obj = self.node.as_const(eval_ctx)
        args = [ x.as_const(eval_ctx) for x in self.args ]
        if getattr(filter_, 'evalcontextfilter', False):
            args.insert(0, eval_ctx)
        elif getattr(filter_, 'environmentfilter', False):
            args.insert(0, self.environment)
        kwargs = dict((x.as_const(eval_ctx) for x in self.kwargs))
        if self.dyn_args is not None:
            try:
                args.extend(self.dyn_args.as_const(eval_ctx))
            except Exception:
                raise Impossible()

        if self.dyn_kwargs is not None:
            try:
                kwargs.update(self.dyn_kwargs.as_const(eval_ctx))
            except Exception:
                raise Impossible()

        try:
            return filter_(obj, *args, **kwargs)
        except Exception:
            raise Impossible()


class Test(Expr):
    fields = ('node', 'name', 'args', 'kwargs', 'dyn_args', 'dyn_kwargs')


class Call(Expr):
    fields = ('node', 'args', 'kwargs', 'dyn_args', 'dyn_kwargs')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile:
            raise Impossible()
        obj = self.node.as_const(eval_ctx)
        args = [ x.as_const(eval_ctx) for x in self.args ]
        if isinstance(obj, _context_function_types):
            if getattr(obj, 'contextfunction', False):
                raise Impossible()
            elif getattr(obj, 'evalcontextfunction', False):
                args.insert(0, eval_ctx)
            elif getattr(obj, 'environmentfunction', False):
                args.insert(0, self.environment)
        kwargs = dict((x.as_const(eval_ctx) for x in self.kwargs))
        if self.dyn_args is not None:
            try:
                args.extend(self.dyn_args.as_const(eval_ctx))
            except Exception:
                raise Impossible()

        if self.dyn_kwargs is not None:
            try:
                kwargs.update(self.dyn_kwargs.as_const(eval_ctx))
            except Exception:
                raise Impossible()

        try:
            return obj(*args, **kwargs)
        except Exception:
            raise Impossible()


class Getitem(Expr):
    fields = ('node', 'arg', 'ctx')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if self.ctx != 'load':
            raise Impossible()
        try:
            return self.environment.getitem(self.node.as_const(eval_ctx), self.arg.as_const(eval_ctx))
        except Exception:
            raise Impossible()

    def can_assign(self):
        return False


class Getattr(Expr):
    fields = ('node', 'attr', 'ctx')

    def as_const(self, eval_ctx = None):
        if self.ctx != 'load':
            raise Impossible()
        try:
            eval_ctx = get_eval_context(self, eval_ctx)
            return self.environment.getattr(self.node.as_const(eval_ctx), self.attr)
        except Exception:
            raise Impossible()

    def can_assign(self):
        return False


class Slice(Expr):
    fields = ('start', 'stop', 'step')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)

        def const(obj):
            if obj is None:
                return
            return obj.as_const(eval_ctx)

        return slice(const(self.start), const(self.stop), const(self.step))


class Concat(Expr):
    fields = ('nodes',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return ''.join((unicode(x.as_const(eval_ctx)) for x in self.nodes))


class Compare(Expr):
    fields = ('expr', 'ops')

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        result = value = self.expr.as_const(eval_ctx)
        try:
            for op in self.ops:
                new_value = op.expr.as_const(eval_ctx)
                result = _cmpop_to_func[op.op](value, new_value)
                value = new_value

        except Exception:
            raise Impossible()

        return result


class Operand(Helper):
    fields = ('op', 'expr')


class Mul(BinExpr):
    operator = '*'


class Div(BinExpr):
    operator = '/'


class FloorDiv(BinExpr):
    operator = '//'


class Add(BinExpr):
    operator = '+'


class Sub(BinExpr):
    operator = '-'


class Mod(BinExpr):
    operator = '%'


class Pow(BinExpr):
    operator = '**'


class And(BinExpr):
    operator = 'and'

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.left.as_const(eval_ctx) and self.right.as_const(eval_ctx)


class Or(BinExpr):
    operator = 'or'

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.left.as_const(eval_ctx) or self.right.as_const(eval_ctx)


class Not(UnaryExpr):
    operator = 'not'


class Neg(UnaryExpr):
    operator = '-'


class Pos(UnaryExpr):
    operator = '+'


class EnvironmentAttribute(Expr):
    fields = ('name',)


class ExtensionAttribute(Expr):
    fields = ('identifier', 'name')


class ImportedName(Expr):
    fields = ('importname',)


class InternalName(Expr):
    fields = ('name',)

    def __init__(self):
        raise TypeError("Can't create internal names.  Use the `free_identifier` method on a parser.")


class MarkSafe(Expr):
    fields = ('expr',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        return Markup(self.expr.as_const(eval_ctx))


class MarkSafeIfAutoescape(Expr):
    fields = ('expr',)

    def as_const(self, eval_ctx = None):
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile:
            raise Impossible()
        expr = self.expr.as_const(eval_ctx)
        if eval_ctx.autoescape:
            return Markup(expr)
        return expr


class ContextReference(Expr):
    pass


class Continue(Stmt):
    pass


class Break(Stmt):
    pass


class Scope(Stmt):
    fields = ('body',)


class EvalContextModifier(Stmt):
    fields = ('options',)


class ScopedEvalContextModifier(EvalContextModifier):
    fields = ('body',)


def _failing_new(*args, **kwargs):
    raise TypeError("can't create custom node types")


NodeType.__new__ = staticmethod(_failing_new)
del _failing_new