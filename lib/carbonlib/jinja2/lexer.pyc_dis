#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\lexer.py
import re
from operator import itemgetter
from collections import deque
from jinja2.exceptions import TemplateSyntaxError
from jinja2.utils import LRUCache, next
_lexer_cache = LRUCache(50)
whitespace_re = re.compile('\\s+', re.U)
string_re = re.compile('(\'([^\'\\\\]*(?:\\\\.[^\'\\\\]*)*)\'|"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)")', re.S)
integer_re = re.compile('\\d+')
try:
    compile('f\xc3\xb6\xc3\xb6', '<unknown>', 'eval')
except SyntaxError:
    name_re = re.compile('\\b[a-zA-Z_][a-zA-Z0-9_]*\\b')
else:
    from jinja2 import _stringdefs
    name_re = re.compile('[%s][%s]*' % (_stringdefs.xid_start, _stringdefs.xid_continue))

float_re = re.compile('(?<!\\.)\\d+\\.\\d+')
newline_re = re.compile('(\\r\\n|\\r|\\n)')
TOKEN_ADD = intern('add')
TOKEN_ASSIGN = intern('assign')
TOKEN_COLON = intern('colon')
TOKEN_COMMA = intern('comma')
TOKEN_DIV = intern('div')
TOKEN_DOT = intern('dot')
TOKEN_EQ = intern('eq')
TOKEN_FLOORDIV = intern('floordiv')
TOKEN_GT = intern('gt')
TOKEN_GTEQ = intern('gteq')
TOKEN_LBRACE = intern('lbrace')
TOKEN_LBRACKET = intern('lbracket')
TOKEN_LPAREN = intern('lparen')
TOKEN_LT = intern('lt')
TOKEN_LTEQ = intern('lteq')
TOKEN_MOD = intern('mod')
TOKEN_MUL = intern('mul')
TOKEN_NE = intern('ne')
TOKEN_PIPE = intern('pipe')
TOKEN_POW = intern('pow')
TOKEN_RBRACE = intern('rbrace')
TOKEN_RBRACKET = intern('rbracket')
TOKEN_RPAREN = intern('rparen')
TOKEN_SEMICOLON = intern('semicolon')
TOKEN_SUB = intern('sub')
TOKEN_TILDE = intern('tilde')
TOKEN_WHITESPACE = intern('whitespace')
TOKEN_FLOAT = intern('float')
TOKEN_INTEGER = intern('integer')
TOKEN_NAME = intern('name')
TOKEN_STRING = intern('string')
TOKEN_OPERATOR = intern('operator')
TOKEN_BLOCK_BEGIN = intern('block_begin')
TOKEN_BLOCK_END = intern('block_end')
TOKEN_VARIABLE_BEGIN = intern('variable_begin')
TOKEN_VARIABLE_END = intern('variable_end')
TOKEN_RAW_BEGIN = intern('raw_begin')
TOKEN_RAW_END = intern('raw_end')
TOKEN_COMMENT_BEGIN = intern('comment_begin')
TOKEN_COMMENT_END = intern('comment_end')
TOKEN_COMMENT = intern('comment')
TOKEN_LINESTATEMENT_BEGIN = intern('linestatement_begin')
TOKEN_LINESTATEMENT_END = intern('linestatement_end')
TOKEN_LINECOMMENT_BEGIN = intern('linecomment_begin')
TOKEN_LINECOMMENT_END = intern('linecomment_end')
TOKEN_LINECOMMENT = intern('linecomment')
TOKEN_DATA = intern('data')
TOKEN_INITIAL = intern('initial')
TOKEN_EOF = intern('eof')
operators = {'+': TOKEN_ADD,
 '-': TOKEN_SUB,
 '/': TOKEN_DIV,
 '//': TOKEN_FLOORDIV,
 '*': TOKEN_MUL,
 '%': TOKEN_MOD,
 '**': TOKEN_POW,
 '~': TOKEN_TILDE,
 '[': TOKEN_LBRACKET,
 ']': TOKEN_RBRACKET,
 '(': TOKEN_LPAREN,
 ')': TOKEN_RPAREN,
 '{': TOKEN_LBRACE,
 '}': TOKEN_RBRACE,
 '==': TOKEN_EQ,
 '!=': TOKEN_NE,
 '>': TOKEN_GT,
 '>=': TOKEN_GTEQ,
 '<': TOKEN_LT,
 '<=': TOKEN_LTEQ,
 '=': TOKEN_ASSIGN,
 '.': TOKEN_DOT,
 ':': TOKEN_COLON,
 '|': TOKEN_PIPE,
 ',': TOKEN_COMMA,
 ';': TOKEN_SEMICOLON}
reverse_operators = dict([ (v, k) for k, v in operators.iteritems() ])
operator_re = re.compile('(%s)' % '|'.join((re.escape(x) for x in sorted(operators, key=lambda x: -len(x)))))
ignored_tokens = frozenset([TOKEN_COMMENT_BEGIN,
 TOKEN_COMMENT,
 TOKEN_COMMENT_END,
 TOKEN_WHITESPACE,
 TOKEN_WHITESPACE,
 TOKEN_LINECOMMENT_BEGIN,
 TOKEN_LINECOMMENT_END,
 TOKEN_LINECOMMENT])
ignore_if_empty = frozenset([TOKEN_WHITESPACE,
 TOKEN_DATA,
 TOKEN_COMMENT,
 TOKEN_LINECOMMENT])

def _describe_token_type(token_type):
    if token_type in reverse_operators:
        return reverse_operators[token_type]
    return {TOKEN_COMMENT_BEGIN: 'begin of comment',
     TOKEN_COMMENT_END: 'end of comment',
     TOKEN_COMMENT: 'comment',
     TOKEN_LINECOMMENT: 'comment',
     TOKEN_BLOCK_BEGIN: 'begin of statement block',
     TOKEN_BLOCK_END: 'end of statement block',
     TOKEN_VARIABLE_BEGIN: 'begin of print statement',
     TOKEN_VARIABLE_END: 'end of print statement',
     TOKEN_LINESTATEMENT_BEGIN: 'begin of line statement',
     TOKEN_LINESTATEMENT_END: 'end of line statement',
     TOKEN_DATA: 'template data / text',
     TOKEN_EOF: 'end of template'}.get(token_type, token_type)


def describe_token(token):
    if token.type == 'name':
        return token.value
    return _describe_token_type(token.type)


def describe_token_expr(expr):
    if ':' in expr:
        type, value = expr.split(':', 1)
        if type == 'name':
            return value
    else:
        type = expr
    return _describe_token_type(type)


def count_newlines(value):
    return len(newline_re.findall(value))


def compile_rules(environment):
    e = re.escape
    rules = [(len(environment.comment_start_string), 'comment', e(environment.comment_start_string)), (len(environment.block_start_string), 'block', e(environment.block_start_string)), (len(environment.variable_start_string), 'variable', e(environment.variable_start_string))]
    if environment.line_statement_prefix is not None:
        rules.append((len(environment.line_statement_prefix), 'linestatement', '^\\s*' + e(environment.line_statement_prefix)))
    if environment.line_comment_prefix is not None:
        rules.append((len(environment.line_comment_prefix), 'linecomment', '(?:^|(?<=\\S))[^\\S\\r\\n]*' + e(environment.line_comment_prefix)))
    return [ x[1:] for x in sorted(rules, reverse=True) ]


class Failure(object):

    def __init__(self, message, cls = TemplateSyntaxError):
        self.message = message
        self.error_class = cls

    def __call__(self, lineno, filename):
        raise self.error_class(self.message, lineno, filename)


class Token(tuple):
    __slots__ = ()
    lineno, type, value = (property(itemgetter(x)) for x in range(3))

    def __new__(cls, lineno, type, value):
        return tuple.__new__(cls, (lineno, intern(str(type)), value))

    def __str__(self):
        if self.type in reverse_operators:
            return reverse_operators[self.type]
        if self.type == 'name':
            return self.value
        return self.type

    def test(self, expr):
        if self.type == expr:
            return True
        if ':' in expr:
            return expr.split(':', 1) == [self.type, self.value]
        return False

    def test_any(self, *iterable):
        for expr in iterable:
            if self.test(expr):
                return True

        return False

    def __repr__(self):
        return 'Token(%r, %r, %r)' % (self.lineno, self.type, self.value)


class TokenStreamIterator(object):

    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        return self

    def next(self):
        token = self.stream.current
        if token.type is TOKEN_EOF:
            self.stream.close()
            raise StopIteration()
        next(self.stream)
        return token


class TokenStream(object):

    def __init__(self, generator, name, filename):
        self._next = iter(generator).next
        self._pushed = deque()
        self.name = name
        self.filename = filename
        self.closed = False
        self.current = Token(1, TOKEN_INITIAL, '')
        next(self)

    def __iter__(self):
        return TokenStreamIterator(self)

    def __nonzero__(self):
        return bool(self._pushed) or self.current.type is not TOKEN_EOF

    eos = property(lambda x: not x, doc='Are we at the end of the stream?')

    def push(self, token):
        self._pushed.append(token)

    def look(self):
        old_token = next(self)
        result = self.current
        self.push(result)
        self.current = old_token
        return result

    def skip(self, n = 1):
        for x in xrange(n):
            next(self)

    def next_if(self, expr):
        if self.current.test(expr):
            return next(self)

    def skip_if(self, expr):
        return self.next_if(expr) is not None

    def next(self):
        rv = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        elif self.current.type is not TOKEN_EOF:
            try:
                self.current = self._next()
            except StopIteration:
                self.close()

        return rv

    def close(self):
        self.current = Token(self.current.lineno, TOKEN_EOF, '')
        self._next = None
        self.closed = True

    def expect(self, expr):
        if not self.current.test(expr):
            expr = describe_token_expr(expr)
            if self.current.type is TOKEN_EOF:
                raise TemplateSyntaxError('unexpected end of template, expected %r.' % expr, self.current.lineno, self.name, self.filename)
            raise TemplateSyntaxError('expected token %r, got %r' % (expr, describe_token(self.current)), self.current.lineno, self.name, self.filename)
        try:
            return self.current
        finally:
            next(self)


def get_lexer(environment):
    key = (environment.block_start_string,
     environment.block_end_string,
     environment.variable_start_string,
     environment.variable_end_string,
     environment.comment_start_string,
     environment.comment_end_string,
     environment.line_statement_prefix,
     environment.line_comment_prefix,
     environment.trim_blocks,
     environment.newline_sequence)
    lexer = _lexer_cache.get(key)
    if lexer is None:
        lexer = Lexer(environment)
        _lexer_cache[key] = lexer
    return lexer


class Lexer(object):

    def __init__(self, environment):
        c = lambda x: re.compile(x, re.M | re.S)
        e = re.escape
        tag_rules = [(whitespace_re, TOKEN_WHITESPACE, None),
         (float_re, TOKEN_FLOAT, None),
         (integer_re, TOKEN_INTEGER, None),
         (name_re, TOKEN_NAME, None),
         (string_re, TOKEN_STRING, None),
         (operator_re, TOKEN_OPERATOR, None)]
        root_tag_rules = compile_rules(environment)
        block_suffix_re = environment.trim_blocks and '\\n?' or ''
        self.newline_sequence = environment.newline_sequence
        self.rules = {'root': [(c('(.*?)(?:%s)' % '|'.join(['(?P<raw_begin>(?:\\s*%s\\-|%s)\\s*raw\\s*(?:\\-%s\\s*|%s))' % (e(environment.block_start_string),
                     e(environment.block_start_string),
                     e(environment.block_end_string),
                     e(environment.block_end_string))] + [ '(?P<%s_begin>\\s*%s\\-|%s)' % (n, r, r) for n, r in root_tag_rules ])), (TOKEN_DATA, '#bygroup'), '#bygroup'), (c('.+'), TOKEN_DATA, None)],
         TOKEN_COMMENT_BEGIN: [(c('(.*?)((?:\\-%s\\s*|%s)%s)' % (e(environment.comment_end_string), e(environment.comment_end_string), block_suffix_re)), (TOKEN_COMMENT, TOKEN_COMMENT_END), '#pop'), (c('(.)'), (Failure('Missing end of comment tag'),), None)],
         TOKEN_BLOCK_BEGIN: [(c('(?:\\-%s\\s*|%s)%s' % (e(environment.block_end_string), e(environment.block_end_string), block_suffix_re)), TOKEN_BLOCK_END, '#pop')] + tag_rules,
         TOKEN_VARIABLE_BEGIN: [(c('\\-%s\\s*|%s' % (e(environment.variable_end_string), e(environment.variable_end_string))), TOKEN_VARIABLE_END, '#pop')] + tag_rules,
         TOKEN_RAW_BEGIN: [(c('(.*?)((?:\\s*%s\\-|%s)\\s*endraw\\s*(?:\\-%s\\s*|%s%s))' % (e(environment.block_start_string),
                             e(environment.block_start_string),
                             e(environment.block_end_string),
                             e(environment.block_end_string),
                             block_suffix_re)), (TOKEN_DATA, TOKEN_RAW_END), '#pop'), (c('(.)'), (Failure('Missing end of raw directive'),), None)],
         TOKEN_LINESTATEMENT_BEGIN: [(c('\\s*(\\n|$)'), TOKEN_LINESTATEMENT_END, '#pop')] + tag_rules,
         TOKEN_LINECOMMENT_BEGIN: [(c('(.*?)()(?=\\n|$)'), (TOKEN_LINECOMMENT, TOKEN_LINECOMMENT_END), '#pop')]}

    def _normalize_newlines(self, value):
        return newline_re.sub(self.newline_sequence, value)

    def tokenize(self, source, name = None, filename = None, state = None):
        stream = self.tokeniter(source, name, filename, state)
        return TokenStream(self.wrap(stream, name, filename), name, filename)

    def wrap(self, stream, name = None, filename = None):
        for lineno, token, value in stream:
            if token in ignored_tokens:
                continue
            elif token == 'linestatement_begin':
                token = 'block_begin'
            elif token == 'linestatement_end':
                token = 'block_end'
            elif token in ('raw_begin', 'raw_end'):
                continue
            elif token == 'data':
                value = self._normalize_newlines(value)
            elif token == 'keyword':
                token = value
            elif token == 'name':
                value = str(value)
            elif token == 'string':
                try:
                    value = self._normalize_newlines(value[1:-1]).encode('ascii', 'backslashreplace').decode('unicode-escape')
                except Exception as e:
                    msg = str(e).split(':')[-1].strip()
                    raise TemplateSyntaxError(msg, lineno, name, filename)

                try:
                    value = str(value)
                except UnicodeError:
                    pass

            elif token == 'integer':
                value = int(value)
            elif token == 'float':
                value = float(value)
            elif token == 'operator':
                token = operators[value]
            yield Token(lineno, token, value)

    def tokeniter(self, source, name, filename = None, state = None):
        source = '\n'.join(unicode(source).splitlines())
        pos = 0
        lineno = 1
        stack = ['root']
        if state is not None and state != 'root':
            stack.append(state + '_begin')
        else:
            state = 'root'
        statetokens = self.rules[stack[-1]]
        source_length = len(source)
        balancing_stack = []
        while 1:
            for regex, tokens, new_state in statetokens:
                m = regex.match(source, pos)
                if m is None:
                    continue
                if balancing_stack and tokens in ('variable_end', 'block_end', 'linestatement_end'):
                    continue
                if isinstance(tokens, tuple):
                    for idx, token in enumerate(tokens):
                        if token.__class__ is Failure:
                            raise token(lineno, filename)
                        elif token == '#bygroup':
                            for key, value in m.groupdict().iteritems():
                                if value is not None:
                                    yield (lineno, key, value)
                                    lineno += value.count('\n')
                                    break
                            else:
                                raise RuntimeError('%r wanted to resolve the token dynamically but no group matched' % regex)

                        else:
                            data = m.group(idx + 1)
                            if data or token not in ignore_if_empty:
                                yield (lineno, token, data)
                            lineno += data.count('\n')

                else:
                    data = m.group()
                    if tokens == 'operator':
                        if data == '{':
                            balancing_stack.append('}')
                        elif data == '(':
                            balancing_stack.append(')')
                        elif data == '[':
                            balancing_stack.append(']')
                        elif data in ('}', ')', ']'):
                            if not balancing_stack:
                                raise TemplateSyntaxError("unexpected '%s'" % data, lineno, name, filename)
                            expected_op = balancing_stack.pop()
                            if expected_op != data:
                                raise TemplateSyntaxError("unexpected '%s', expected '%s'" % (data, expected_op), lineno, name, filename)
                    if data or tokens not in ignore_if_empty:
                        yield (lineno, tokens, data)
                    lineno += data.count('\n')
                pos2 = m.end()
                if new_state is not None:
                    if new_state == '#pop':
                        stack.pop()
                    elif new_state == '#bygroup':
                        for key, value in m.groupdict().iteritems():
                            if value is not None:
                                stack.append(key)
                                break
                        else:
                            raise RuntimeError('%r wanted to resolve the new state dynamically but no group matched' % regex)

                    else:
                        stack.append(new_state)
                    statetokens = self.rules[stack[-1]]
                elif pos2 == pos:
                    raise RuntimeError('%r yielded empty string without stack change' % regex)
                pos = pos2
                break
            else:
                if pos >= source_length:
                    return
                raise TemplateSyntaxError('unexpected char %r at %d' % (source[pos], pos), lineno, name, filename)