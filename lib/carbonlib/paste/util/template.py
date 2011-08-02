import re
import sys
import cgi
import urllib
from paste.util.looper import looper
__all__ = ['TemplateError',
 'Template',
 'sub',
 'HTMLTemplate',
 'sub_html',
 'html',
 'bunch']
token_re = re.compile('\\{\\{|\\}\\}')
in_re = re.compile('\\s+in\\s+')
var_re = re.compile('^[a-z_][a-z0-9_]*$', re.I)

class TemplateError(Exception):

    def __init__(self, message, position, name = None):
        self.message = message
        self.position = position
        self.name = name



    def __str__(self):
        msg = '%s at line %s column %s' % (self.message, self.position[0], self.position[1])
        if self.name:
            msg += ' in %s' % self.name
        return msg




class _TemplateContinue(Exception):
    pass

class _TemplateBreak(Exception):
    pass

class Template(object):
    default_namespace = {'start_braces': '{{',
     'end_braces': '}}',
     'looper': looper}
    default_encoding = 'utf8'

    def __init__(self, content, name = None, namespace = None):
        self.content = content
        self._unicode = isinstance(content, unicode)
        self.name = name
        self._parsed = parse(content, name=name)
        if namespace is None:
            namespace = {}
        self.namespace = namespace



    def from_filename(cls, filename, namespace = None, encoding = None):
        f = open(filename, 'rb')
        c = f.read()
        f.close()
        if encoding:
            c = c.decode(encoding)
        return cls(content=c, name=filename, namespace=namespace)


    from_filename = classmethod(from_filename)

    def __repr__(self):
        return '<%s %s name=%r>' % (self.__class__.__name__, hex(id(self))[2:], self.name)



    def substitute(self, *args, **kw):
        if args:
            if kw:
                raise TypeError('You can only give positional *or* keyword arguments')
            if len(args) > 1:
                raise TypeError('You can only give on positional argument')
            kw = args[0]
        ns = self.default_namespace.copy()
        ns.update(self.namespace)
        ns.update(kw)
        result = self._interpret(ns)
        return result



    def _interpret(self, ns):
        __traceback_hide__ = True
        parts = []
        self._interpret_codes(self._parsed, ns, out=parts)
        return ''.join(parts)



    def _interpret_codes(self, codes, ns, out):
        __traceback_hide__ = True
        for item in codes:
            if isinstance(item, basestring):
                out.append(item)
            else:
                self._interpret_code(item, ns, out)




    def _interpret_code(self, code, ns, out):
        __traceback_hide__ = True
        (name, pos,) = (code[0], code[1])
        if name == 'py':
            self._exec(code[2], ns, pos)
        elif name == 'continue':
            raise _TemplateContinue()
        elif name == 'break':
            raise _TemplateBreak()
        elif name == 'for':
            (vars, expr, content,) = (code[2], code[3], code[4])
            expr = self._eval(expr, ns, pos)
            self._interpret_for(vars, expr, content, ns, out)
        elif name == 'cond':
            parts = code[2:]
            self._interpret_if(parts, ns, out)
        elif name == 'expr':
            parts = code[2].split('|')
            base = self._eval(parts[0], ns, pos)
            for part in parts[1:]:
                func = self._eval(part, ns, pos)
                base = func(base)

            out.append(self._repr(base, pos))
        elif name == 'default':
            (var, expr,) = (code[2], code[3])
            if var not in ns:
                result = self._eval(expr, ns, pos)
                ns[var] = result
        elif name == 'comment':
            return 



    def _interpret_for(self, vars, expr, content, ns, out):
        __traceback_hide__ = True
        for item in expr:
            if len(vars) == 1:
                ns[vars[0]] = item
            elif len(vars) != len(item):
                raise ValueError('Need %i items to unpack (got %i items)' % (len(vars), len(item)))
            for (name, value,) in zip(vars, item):
                ns[name] = value

            try:
                self._interpret_codes(content, ns, out)
            except _TemplateContinue:
                continue
            except _TemplateBreak:
                break




    def _interpret_if(self, parts, ns, out):
        __traceback_hide__ = True
        for part in parts:
            (name, pos,) = (part[0], part[1])
            if name == 'else':
                result = True
            else:
                result = self._eval(part[2], ns, pos)
            if result:
                self._interpret_codes(part[3], ns, out)
                break




    def _eval(self, code, ns, pos):
        __traceback_hide__ = True
        try:
            value = eval(code, ns)
            return value
        except:
            exc_info = sys.exc_info()
            e = exc_info[1]
            if getattr(e, 'args'):
                arg0 = e.args[0]
            else:
                arg0 = str(e)
            e.args = (self._add_line_info(arg0, pos),)
            raise exc_info[0], e, exc_info[2]



    def _exec(self, code, ns, pos):
        __traceback_hide__ = True
        try:
            exec code in ns
        except:
            exc_info = sys.exc_info()
            e = exc_info[1]
            e.args = (self._add_line_info(e.args[0], pos),)
            raise exc_info[0], e, exc_info[2]



    def _repr(self, value, pos):
        __traceback_hide__ = True
        try:
            if value is None:
                return ''
            if self._unicode:
                try:
                    value = unicode(value)
                except UnicodeDecodeError:
                    value = str(value)
            else:
                value = str(value)
        except:
            exc_info = sys.exc_info()
            e = exc_info[1]
            e.args = (self._add_line_info(e.args[0], pos),)
            raise exc_info[0], e, exc_info[2]
        else:
            if self._unicode and isinstance(value, str):
                if not self.decode_encoding:
                    raise UnicodeDecodeError('Cannot decode str value %r into unicode (no default_encoding provided)' % value)
                value = value.decode(self.default_encoding)
            elif not self._unicode and isinstance(value, unicode):
                if not self.decode_encoding:
                    raise UnicodeEncodeError('Cannot encode unicode value %r into str (no default_encoding provided)' % value)
                value = value.encode(self.default_encoding)
            return value



    def _add_line_info(self, msg, pos):
        msg = '%s at line %s column %s' % (msg, pos[0], pos[1])
        if self.name:
            msg += ' in file %s' % self.name
        return msg




def sub(content, **kw):
    name = kw.get('__name')
    tmpl = Template(content, name=name)
    return tmpl.substitute(kw)



def paste_script_template_renderer(content, vars, filename = None):
    tmpl = Template(content, name=filename)
    return tmpl.substitute(vars)



class bunch(dict):

    def __init__(self, **kw):
        for (name, value,) in kw.items():
            setattr(self, name, value)




    def __setattr__(self, name, value):
        self[name] = value



    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)



    def __getitem__(self, key):
        if 'default' in self:
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return dict.__getitem__(self, 'default')
        else:
            return dict.__getitem__(self, key)



    def __repr__(self):
        items = [ (k, v) for (k, v,) in self.items() ]
        items.sort()
        return '<%s %s>' % (self.__class__.__name__, ' '.join([ '%s=%r' % (k, v) for (k, v,) in items ]))




class html(object):

    def __init__(self, value):
        self.value = value



    def __str__(self):
        return self.value



    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.value)




def html_quote(value):
    if value is None:
        return ''
    if not isinstance(value, basestring):
        if hasattr(value, '__unicode__'):
            value = unicode(value)
        else:
            value = str(value)
    value = cgi.escape(value, 1)
    if isinstance(value, unicode):
        value = value.encode('ascii', 'xmlcharrefreplace')
    return value



def url(v):
    if not isinstance(v, basestring):
        if hasattr(v, '__unicode__'):
            v = unicode(v)
        else:
            v = str(v)
    if isinstance(v, unicode):
        v = v.encode('utf8')
    return urllib.quote(v)



def attr(**kw):
    kw = kw.items()
    kw.sort()
    parts = []
    for (name, value,) in kw:
        if value is None:
            continue
        if name.endswith('_'):
            name = name[:-1]
        parts.append('%s="%s"' % (html_quote(name), html_quote(value)))

    return html(' '.join(parts))



class HTMLTemplate(Template):
    default_namespace = Template.default_namespace.copy()
    default_namespace.update(dict(html=html, attr=attr, url=url))

    def _repr(self, value, pos):
        plain = Template._repr(self, value, pos)
        if isinstance(value, html):
            return plain
        else:
            return html_quote(plain)




def sub_html(content, **kw):
    name = kw.get('__name')
    tmpl = HTMLTemplate(content, name=name)
    return tmpl.substitute(kw)



def lex(s, name = None, trim_whitespace = True):
    in_expr = False
    chunks = []
    last = 0
    last_pos = (1, 1)
    for match in token_re.finditer(s):
        expr = match.group(0)
        pos = find_position(s, match.end())
        if expr == '{{' and in_expr:
            raise TemplateError('{{ inside expression', position=pos, name=name)
        elif expr == '}}' and not in_expr:
            raise TemplateError('}} outside expression', position=pos, name=name)
        if expr == '{{':
            part = s[last:match.start()]
            if part:
                chunks.append(part)
            in_expr = True
        else:
            chunks.append((s[last:match.start()], last_pos))
            in_expr = False
        last = match.end()
        last_pos = pos

    if in_expr:
        raise TemplateError('No }} to finish last expression', name=name, position=last_pos)
    part = s[last:]
    if part:
        chunks.append(part)
    if trim_whitespace:
        chunks = trim_lex(chunks)
    return chunks


statement_re = re.compile('^(?:if |elif |else |for |py:)')
single_statements = ['endif',
 'endfor',
 'continue',
 'break']
trail_whitespace_re = re.compile('\\n[\\t ]*$')
lead_whitespace_re = re.compile('^[\\t ]*\\n')

def trim_lex(tokens):
    for i in range(len(tokens)):
        current = tokens[i]
        if isinstance(tokens[i], basestring):
            continue
        item = current[0]
        if not statement_re.search(item) and item not in single_statements:
            continue
        if not i:
            prev = ''
        else:
            prev = tokens[(i - 1)]
        if i + 1 >= len(tokens):
            next = ''
        else:
            next = tokens[(i + 1)]
        if not isinstance(next, basestring) or not isinstance(prev, basestring):
            continue
        if (not prev or trail_whitespace_re.search(prev)) and (not next or lead_whitespace_re.search(next)):
            if prev:
                m = trail_whitespace_re.search(prev)
                prev = prev[:(m.start() + 1)]
                tokens[i - 1] = prev
            if next:
                m = lead_whitespace_re.search(next)
                next = next[m.end():]
                tokens[i + 1] = next

    return tokens



def find_position(string, index):
    leading = string[:index].splitlines()
    return (len(leading), len(leading[-1]) + 1)



def parse(s, name = None):
    tokens = lex(s, name=name)
    result = []
    while tokens:
        (next, tokens,) = parse_expr(tokens, name)
        result.append(next)

    return result



def parse_expr(tokens, name, context = ()):
    if isinstance(tokens[0], basestring):
        return (tokens[0], tokens[1:])
    (expr, pos,) = tokens[0]
    expr = expr.strip()
    if expr.startswith('py:'):
        expr = expr[3:].lstrip(' \t')
        if expr.startswith('\n'):
            expr = expr[1:]
        elif '\n' in expr:
            raise TemplateError('Multi-line py blocks must start with a newline', position=pos, name=name)
        return (('py', pos, expr), tokens[1:])
    if expr in ('continue', 'break'):
        if 'for' not in context:
            raise TemplateError('continue outside of for loop', position=pos, name=name)
        return ((expr, pos), tokens[1:])
    if expr.startswith('if '):
        return parse_cond(tokens, name, context)
    if expr.startswith('elif ') or expr == 'else':
        raise TemplateError('%s outside of an if block' % expr.split()[0], position=pos, name=name)
    elif expr in ('if', 'elif', 'for'):
        raise TemplateError('%s with no expression' % expr, position=pos, name=name)
    elif expr in ('endif', 'endfor'):
        raise TemplateError('Unexpected %s' % expr, position=pos, name=name)
    elif expr.startswith('for '):
        return parse_for(tokens, name, context)
    if expr.startswith('default '):
        return parse_default(tokens, name, context)
    if expr.startswith('#'):
        return (('comment', pos, tokens[0][0]), tokens[1:])
    return (('expr', pos, tokens[0][0]), tokens[1:])



def parse_cond(tokens, name, context):
    start = tokens[0][1]
    pieces = []
    context = context + ('if',)
    while 1:
        if not tokens:
            raise TemplateError('Missing {{endif}}', position=start, name=name)
        if isinstance(tokens[0], tuple) and tokens[0][0] == 'endif':
            return (('cond', start) + tuple(pieces), tokens[1:])
        (next, tokens,) = parse_one_cond(tokens, name, context)
        pieces.append(next)




def parse_one_cond(tokens, name, context):
    ((first, pos,), tokens,) = (tokens[0], tokens[1:])
    content = []
    if first.endswith(':'):
        first = first[:-1]
    if first.startswith('if '):
        part = ('if',
         pos,
         first[3:].lstrip(),
         content)
    elif first.startswith('elif '):
        part = ('elif',
         pos,
         first[5:].lstrip(),
         content)
    elif first == 'else':
        part = ('else',
         pos,
         None,
         content)
    while 1:
        if not tokens:
            raise TemplateError('No {{endif}}', position=pos, name=name)
        if isinstance(tokens[0], tuple) and (tokens[0][0] == 'endif' or tokens[0][0].startswith('elif ') or tokens[0][0] == 'else'):
            return (part, tokens)
        (next, tokens,) = parse_expr(tokens, name, context)
        content.append(next)




def parse_for(tokens, name, context):
    (first, pos,) = tokens[0]
    tokens = tokens[1:]
    context = ('for',) + context
    content = []
    if first.endswith(':'):
        first = first[:-1]
    first = first[3:].strip()
    match = in_re.search(first)
    if not match:
        raise TemplateError('Bad for (no "in") in %r' % first, position=pos, name=name)
    vars = first[:match.start()]
    if '(' in vars:
        raise TemplateError('You cannot have () in the variable section of a for loop (%r)' % vars, position=pos, name=name)
    vars = tuple([ v.strip() for v in first[:match.start()].split(',') if v.strip() ])
    expr = first[match.end():]
    while 1:
        if not tokens:
            raise TemplateError('No {{endfor}}', position=pos, name=name)
        if isinstance(tokens[0], tuple) and tokens[0][0] == 'endfor':
            return (('for',
              pos,
              vars,
              expr,
              content), tokens[1:])
        (next, tokens,) = parse_expr(tokens, name, context)
        content.append(next)




def parse_default(tokens, name, context):
    (first, pos,) = tokens[0]
    first = first.split(None, 1)[1]
    parts = first.split('=', 1)
    if len(parts) == 1:
        raise TemplateError('Expression must be {{default var=value}}; no = found in %r' % first, position=pos, name=name)
    var = parts[0].strip()
    if ',' in var:
        raise TemplateError('{{default x, y = ...}} is not supported', position=pos, name=name)
    if not var_re.search(var):
        raise TemplateError('Not a valid variable name for {{default}}: %r' % var, position=pos, name=name)
    expr = parts[1].strip()
    return (('default',
      pos,
      var,
      expr), tokens[1:])


_fill_command_usage = '%prog [OPTIONS] TEMPLATE arg=value\n\nUse py:arg=value to set a Python value; otherwise all values are\nstrings.\n'

def fill_command(args = None):
    import sys
    import optparse
    import pkg_resources
    import os
    if args is None:
        args = sys.argv[1:]
    dist = pkg_resources.get_distribution('Paste')
    parser = optparse.OptionParser(version=str(dist), usage=_fill_command_usage)
    parser.add_option('-o', '--output', dest='output', metavar='FILENAME', help='File to write output to (default stdout)')
    parser.add_option('--html', dest='use_html', action='store_true', help='Use HTML style filling (including automatic HTML quoting)')
    parser.add_option('--env', dest='use_env', action='store_true', help='Put the environment in as top-level variables')
    (options, args,) = parser.parse_args(args)
    if len(args) < 1:
        print 'You must give a template filename'
        print dir(parser)
    template_name = args[0]
    args = args[1:]
    vars = {}
    if options.use_env:
        vars.update(os.environ)
    for value in args:
        if '=' not in value:
            print 'Bad argument: %r' % value
            sys.exit(2)
        (name, value,) = value.split('=', 1)
        if name.startswith('py:'):
            name = name[:3]
            value = eval(value)
        vars[name] = value

    if template_name == '-':
        template_content = sys.stdin.read()
        template_name = '<stdin>'
    else:
        f = open(template_name, 'rb')
        template_content = f.read()
        f.close()
    if options.use_html:
        TemplateClass = HTMLTemplate
    else:
        TemplateClass = Template
    template = TemplateClass(template_content, name=template_name)
    result = template.substitute(vars)
    if options.output:
        f = open(options.output, 'wb')
        f.write(result)
        f.close()
    else:
        sys.stdout.write(result)


if __name__ == '__main__':
    from paste.util.template import fill_command
    fill_command()

