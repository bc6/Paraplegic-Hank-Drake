#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\yaml\scanner.py
__all__ = ['Scanner', 'ScannerError']
from error import MarkedYAMLError
from tokens import *

class ScannerError(MarkedYAMLError):
    pass


class SimpleKey(object):

    def __init__(self, token_number, required, index, line, column, mark):
        self.token_number = token_number
        self.required = required
        self.index = index
        self.line = line
        self.column = column
        self.mark = mark


class Scanner(object):

    def __init__(self):
        self.done = False
        self.flow_level = 0
        self.tokens = []
        self.fetch_stream_start()
        self.tokens_taken = 0
        self.indent = -1
        self.indents = []
        self.allow_simple_key = True
        self.possible_simple_keys = {}

    def check_token(self, *choices):
        while self.need_more_tokens():
            self.fetch_more_tokens()

        if self.tokens:
            if not choices:
                return True
            for choice in choices:
                if isinstance(self.tokens[0], choice):
                    return True

        return False

    def peek_token(self):
        while self.need_more_tokens():
            self.fetch_more_tokens()

        if self.tokens:
            return self.tokens[0]

    def get_token(self):
        while self.need_more_tokens():
            self.fetch_more_tokens()

        if self.tokens:
            self.tokens_taken += 1
            return self.tokens.pop(0)

    def need_more_tokens(self):
        if self.done:
            return False
        if not self.tokens:
            return True
        self.stale_possible_simple_keys()
        if self.next_possible_simple_key() == self.tokens_taken:
            return True

    def fetch_more_tokens(self):
        self.scan_to_next_token()
        self.stale_possible_simple_keys()
        self.unwind_indent(self.column)
        ch = self.peek()
        if ch == u'\x00':
            return self.fetch_stream_end()
        if ch == u'%' and self.check_directive():
            return self.fetch_directive()
        if ch == u'-' and self.check_document_start():
            return self.fetch_document_start()
        if ch == u'.' and self.check_document_end():
            return self.fetch_document_end()
        if ch == u'[':
            return self.fetch_flow_sequence_start()
        if ch == u'{':
            return self.fetch_flow_mapping_start()
        if ch == u']':
            return self.fetch_flow_sequence_end()
        if ch == u'}':
            return self.fetch_flow_mapping_end()
        if ch == u',':
            return self.fetch_flow_entry()
        if ch == u'-' and self.check_block_entry():
            return self.fetch_block_entry()
        if ch == u'?' and self.check_key():
            return self.fetch_key()
        if ch == u':' and self.check_value():
            return self.fetch_value()
        if ch == u'*':
            return self.fetch_alias()
        if ch == u'&':
            return self.fetch_anchor()
        if ch == u'!':
            return self.fetch_tag()
        if ch == u'|' and not self.flow_level:
            return self.fetch_literal()
        if ch == u'>' and not self.flow_level:
            return self.fetch_folded()
        if ch == u"'":
            return self.fetch_single()
        if ch == u'"':
            return self.fetch_double()
        if self.check_plain():
            return self.fetch_plain()
        raise ScannerError('while scanning for the next token', None, 'found character %r that cannot start any token' % ch.encode('utf-8'), self.get_mark())

    def next_possible_simple_key(self):
        min_token_number = None
        for level in self.possible_simple_keys:
            key = self.possible_simple_keys[level]
            if min_token_number is None or key.token_number < min_token_number:
                min_token_number = key.token_number

        return min_token_number

    def stale_possible_simple_keys(self):
        for level in self.possible_simple_keys.keys():
            key = self.possible_simple_keys[level]
            if key.line != self.line or self.index - key.index > 1024:
                if key.required:
                    raise ScannerError('while scanning a simple key', key.mark, "could not found expected ':'", self.get_mark())
                del self.possible_simple_keys[level]

    def save_possible_simple_key(self):
        required = not self.flow_level and self.indent == self.column
        if self.allow_simple_key:
            self.remove_possible_simple_key()
            token_number = self.tokens_taken + len(self.tokens)
            key = SimpleKey(token_number, required, self.index, self.line, self.column, self.get_mark())
            self.possible_simple_keys[self.flow_level] = key

    def remove_possible_simple_key(self):
        if self.flow_level in self.possible_simple_keys:
            key = self.possible_simple_keys[self.flow_level]
            if key.required:
                raise ScannerError('while scanning a simple key', key.mark, "could not found expected ':'", self.get_mark())
            del self.possible_simple_keys[self.flow_level]

    def unwind_indent(self, column):
        if self.flow_level:
            return
        while self.indent > column:
            mark = self.get_mark()
            self.indent = self.indents.pop()
            self.tokens.append(BlockEndToken(mark, mark))

    def add_indent(self, column):
        if self.indent < column:
            self.indents.append(self.indent)
            self.indent = column
            return True
        return False

    def fetch_stream_start(self):
        mark = self.get_mark()
        self.tokens.append(StreamStartToken(mark, mark, encoding=self.encoding))

    def fetch_stream_end(self):
        self.unwind_indent(-1)
        self.remove_possible_simple_key()
        self.allow_simple_key = False
        self.possible_simple_keys = {}
        mark = self.get_mark()
        self.tokens.append(StreamEndToken(mark, mark))
        self.done = True

    def fetch_directive(self):
        self.unwind_indent(-1)
        self.remove_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_directive())

    def fetch_document_start(self):
        self.fetch_document_indicator(DocumentStartToken)

    def fetch_document_end(self):
        self.fetch_document_indicator(DocumentEndToken)

    def fetch_document_indicator(self, TokenClass):
        self.unwind_indent(-1)
        self.remove_possible_simple_key()
        self.allow_simple_key = False
        start_mark = self.get_mark()
        self.forward(3)
        end_mark = self.get_mark()
        self.tokens.append(TokenClass(start_mark, end_mark))

    def fetch_flow_sequence_start(self):
        self.fetch_flow_collection_start(FlowSequenceStartToken)

    def fetch_flow_mapping_start(self):
        self.fetch_flow_collection_start(FlowMappingStartToken)

    def fetch_flow_collection_start(self, TokenClass):
        self.save_possible_simple_key()
        self.flow_level += 1
        self.allow_simple_key = True
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(TokenClass(start_mark, end_mark))

    def fetch_flow_sequence_end(self):
        self.fetch_flow_collection_end(FlowSequenceEndToken)

    def fetch_flow_mapping_end(self):
        self.fetch_flow_collection_end(FlowMappingEndToken)

    def fetch_flow_collection_end(self, TokenClass):
        self.remove_possible_simple_key()
        self.flow_level -= 1
        self.allow_simple_key = False
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(TokenClass(start_mark, end_mark))

    def fetch_flow_entry(self):
        self.allow_simple_key = True
        self.remove_possible_simple_key()
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(FlowEntryToken(start_mark, end_mark))

    def fetch_block_entry(self):
        if not self.flow_level:
            if not self.allow_simple_key:
                raise ScannerError(None, None, 'sequence entries are not allowed here', self.get_mark())
            if self.add_indent(self.column):
                mark = self.get_mark()
                self.tokens.append(BlockSequenceStartToken(mark, mark))
        self.allow_simple_key = True
        self.remove_possible_simple_key()
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(BlockEntryToken(start_mark, end_mark))

    def fetch_key(self):
        if not self.flow_level:
            if not self.allow_simple_key:
                raise ScannerError(None, None, 'mapping keys are not allowed here', self.get_mark())
            if self.add_indent(self.column):
                mark = self.get_mark()
                self.tokens.append(BlockMappingStartToken(mark, mark))
        self.allow_simple_key = not self.flow_level
        self.remove_possible_simple_key()
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(KeyToken(start_mark, end_mark))

    def fetch_value(self):
        if self.flow_level in self.possible_simple_keys:
            key = self.possible_simple_keys[self.flow_level]
            del self.possible_simple_keys[self.flow_level]
            self.tokens.insert(key.token_number - self.tokens_taken, KeyToken(key.mark, key.mark))
            if not self.flow_level:
                if self.add_indent(key.column):
                    self.tokens.insert(key.token_number - self.tokens_taken, BlockMappingStartToken(key.mark, key.mark))
            self.allow_simple_key = False
        else:
            if not self.flow_level:
                if not self.allow_simple_key:
                    raise ScannerError(None, None, 'mapping values are not allowed here', self.get_mark())
            if not self.flow_level:
                if self.add_indent(self.column):
                    mark = self.get_mark()
                    self.tokens.append(BlockMappingStartToken(mark, mark))
            self.allow_simple_key = not self.flow_level
            self.remove_possible_simple_key()
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(ValueToken(start_mark, end_mark))

    def fetch_alias(self):
        self.save_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_anchor(AliasToken))

    def fetch_anchor(self):
        self.save_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_anchor(AnchorToken))

    def fetch_tag(self):
        self.save_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_tag())

    def fetch_literal(self):
        self.fetch_block_scalar(style='|')

    def fetch_folded(self):
        self.fetch_block_scalar(style='>')

    def fetch_block_scalar(self, style):
        self.allow_simple_key = True
        self.remove_possible_simple_key()
        self.tokens.append(self.scan_block_scalar(style))

    def fetch_single(self):
        self.fetch_flow_scalar(style="'")

    def fetch_double(self):
        self.fetch_flow_scalar(style='"')

    def fetch_flow_scalar(self, style):
        self.save_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_flow_scalar(style))

    def fetch_plain(self):
        self.save_possible_simple_key()
        self.allow_simple_key = False
        self.tokens.append(self.scan_plain())

    def check_directive(self):
        if self.column == 0:
            return True

    def check_document_start(self):
        if self.column == 0 and self.prefix(3) == u'---':
            if self.peek(3) in u'\x00 \t\r\n\x85\u2028\u2029':
                return True

    def check_document_end(self):
        if self.column == 0 and self.prefix(3) == u'...':
            if self.peek(3) in u'\x00 \t\r\n\x85\u2028\u2029':
                return True

    def check_block_entry(self):
        return self.peek(1) in u'\x00 \t\r\n\x85\u2028\u2029'

    def check_key(self):
        if self.flow_level:
            return True
        else:
            return self.peek(1) in u'\x00 \t\r\n\x85\u2028\u2029'

    def check_value(self):
        if self.flow_level:
            return True
        else:
            return self.peek(1) in u'\x00 \t\r\n\x85\u2028\u2029'

    def check_plain(self):
        ch = self.peek()
        return ch not in u'\x00 \t\r\n\x85\u2028\u2029-?:,[]{}#&*!|>\'"%@`' or self.peek(1) not in u'\x00 \t\r\n\x85\u2028\u2029' and (ch == u'-' or not self.flow_level and ch in u'?:')

    def scan_to_next_token(self):
        if self.index == 0 and self.peek() == u'\ufeff':
            self.forward()
        found = False
        while not found:
            while self.peek() == u' ':
                self.forward()

            if self.peek() == u'#':
                while self.peek() not in u'\x00\r\n\x85\u2028\u2029':
                    self.forward()

            if self.scan_line_break():
                if not self.flow_level:
                    self.allow_simple_key = True
            else:
                found = True

    def scan_directive(self):
        start_mark = self.get_mark()
        self.forward()
        name = self.scan_directive_name(start_mark)
        value = None
        if name == u'YAML':
            value = self.scan_yaml_directive_value(start_mark)
            end_mark = self.get_mark()
        elif name == u'TAG':
            value = self.scan_tag_directive_value(start_mark)
            end_mark = self.get_mark()
        else:
            end_mark = self.get_mark()
            while self.peek() not in u'\x00\r\n\x85\u2028\u2029':
                self.forward()

        self.scan_directive_ignored_line(start_mark)
        return DirectiveToken(name, value, start_mark, end_mark)

    def scan_directive_name(self, start_mark):
        length = 0
        ch = self.peek(length)
        while u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u'-_':
            length += 1
            ch = self.peek(length)

        if not length:
            raise ScannerError('while scanning a directive', start_mark, 'expected alphabetic or numeric character, but found %r' % ch.encode('utf-8'), self.get_mark())
        value = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch not in u'\x00 \r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a directive', start_mark, 'expected alphabetic or numeric character, but found %r' % ch.encode('utf-8'), self.get_mark())
        return value

    def scan_yaml_directive_value(self, start_mark):
        while self.peek() == u' ':
            self.forward()

        major = self.scan_yaml_directive_number(start_mark)
        if self.peek() != '.':
            raise ScannerError('while scanning a directive', start_mark, "expected a digit or '.', but found %r" % self.peek().encode('utf-8'), self.get_mark())
        self.forward()
        minor = self.scan_yaml_directive_number(start_mark)
        if self.peek() not in u'\x00 \r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a directive', start_mark, "expected a digit or ' ', but found %r" % self.peek().encode('utf-8'), self.get_mark())
        return (major, minor)

    def scan_yaml_directive_number(self, start_mark):
        ch = self.peek()
        if not u'0' <= ch <= u'9':
            raise ScannerError('while scanning a directive', start_mark, 'expected a digit, but found %r' % ch.encode('utf-8'), self.get_mark())
        length = 0
        while u'0' <= self.peek(length) <= u'9':
            length += 1

        value = int(self.prefix(length))
        self.forward(length)
        return value

    def scan_tag_directive_value(self, start_mark):
        while self.peek() == u' ':
            self.forward()

        handle = self.scan_tag_directive_handle(start_mark)
        while self.peek() == u' ':
            self.forward()

        prefix = self.scan_tag_directive_prefix(start_mark)
        return (handle, prefix)

    def scan_tag_directive_handle(self, start_mark):
        value = self.scan_tag_handle('directive', start_mark)
        ch = self.peek()
        if ch != u' ':
            raise ScannerError('while scanning a directive', start_mark, "expected ' ', but found %r" % ch.encode('utf-8'), self.get_mark())
        return value

    def scan_tag_directive_prefix(self, start_mark):
        value = self.scan_tag_uri('directive', start_mark)
        ch = self.peek()
        if ch not in u'\x00 \r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a directive', start_mark, "expected ' ', but found %r" % ch.encode('utf-8'), self.get_mark())
        return value

    def scan_directive_ignored_line(self, start_mark):
        while self.peek() == u' ':
            self.forward()

        if self.peek() == u'#':
            while self.peek() not in u'\x00\r\n\x85\u2028\u2029':
                self.forward()

        ch = self.peek()
        if ch not in u'\x00\r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a directive', start_mark, 'expected a comment or a line break, but found %r' % ch.encode('utf-8'), self.get_mark())
        self.scan_line_break()

    def scan_anchor(self, TokenClass):
        start_mark = self.get_mark()
        indicator = self.peek()
        if indicator == u'*':
            name = 'alias'
        else:
            name = 'anchor'
        self.forward()
        length = 0
        ch = self.peek(length)
        while u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u'-_':
            length += 1
            ch = self.peek(length)

        if not length:
            raise ScannerError('while scanning an %s' % name, start_mark, 'expected alphabetic or numeric character, but found %r' % ch.encode('utf-8'), self.get_mark())
        value = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch not in u'\x00 \t\r\n\x85\u2028\u2029?:,]}%@`':
            raise ScannerError('while scanning an %s' % name, start_mark, 'expected alphabetic or numeric character, but found %r' % ch.encode('utf-8'), self.get_mark())
        end_mark = self.get_mark()
        return TokenClass(value, start_mark, end_mark)

    def scan_tag(self):
        start_mark = self.get_mark()
        ch = self.peek(1)
        if ch == u'<':
            handle = None
            self.forward(2)
            suffix = self.scan_tag_uri('tag', start_mark)
            if self.peek() != u'>':
                raise ScannerError('while parsing a tag', start_mark, "expected '>', but found %r" % self.peek().encode('utf-8'), self.get_mark())
            self.forward()
        elif ch in u'\x00 \t\r\n\x85\u2028\u2029':
            handle = None
            suffix = u'!'
            self.forward()
        else:
            length = 1
            use_handle = False
            while ch not in u'\x00 \r\n\x85\u2028\u2029':
                if ch == u'!':
                    use_handle = True
                    break
                length += 1
                ch = self.peek(length)

            handle = u'!'
            if use_handle:
                handle = self.scan_tag_handle('tag', start_mark)
            else:
                handle = u'!'
                self.forward()
            suffix = self.scan_tag_uri('tag', start_mark)
        ch = self.peek()
        if ch not in u'\x00 \r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a tag', start_mark, "expected ' ', but found %r" % ch.encode('utf-8'), self.get_mark())
        value = (handle, suffix)
        end_mark = self.get_mark()
        return TagToken(value, start_mark, end_mark)

    def scan_block_scalar(self, style):
        if style == '>':
            folded = True
        else:
            folded = False
        chunks = []
        start_mark = self.get_mark()
        self.forward()
        chomping, increment = self.scan_block_scalar_indicators(start_mark)
        self.scan_block_scalar_ignored_line(start_mark)
        min_indent = self.indent + 1
        if min_indent < 1:
            min_indent = 1
        if increment is None:
            breaks, max_indent, end_mark = self.scan_block_scalar_indentation()
            indent = max(min_indent, max_indent)
        else:
            indent = min_indent + increment - 1
            breaks, end_mark = self.scan_block_scalar_breaks(indent)
        line_break = u''
        while self.column == indent and self.peek() != u'\x00':
            chunks.extend(breaks)
            leading_non_space = self.peek() not in u' \t'
            length = 0
            while self.peek(length) not in u'\x00\r\n\x85\u2028\u2029':
                length += 1

            chunks.append(self.prefix(length))
            self.forward(length)
            line_break = self.scan_line_break()
            breaks, end_mark = self.scan_block_scalar_breaks(indent)
            if self.column == indent and self.peek() != u'\x00':
                if folded and line_break == u'\n' and leading_non_space and self.peek() not in u' \t':
                    if not breaks:
                        chunks.append(u' ')
                else:
                    chunks.append(line_break)
            else:
                break

        if chomping is not False:
            chunks.append(line_break)
        if chomping is True:
            chunks.extend(breaks)
        return ScalarToken(u''.join(chunks), False, start_mark, end_mark, style)

    def scan_block_scalar_indicators(self, start_mark):
        chomping = None
        increment = None
        ch = self.peek()
        if ch in u'+-':
            if ch == '+':
                chomping = True
            else:
                chomping = False
            self.forward()
            ch = self.peek()
            if ch in u'0123456789':
                increment = int(ch)
                if increment == 0:
                    raise ScannerError('while scanning a block scalar', start_mark, 'expected indentation indicator in the range 1-9, but found 0', self.get_mark())
                self.forward()
        elif ch in u'0123456789':
            increment = int(ch)
            if increment == 0:
                raise ScannerError('while scanning a block scalar', start_mark, 'expected indentation indicator in the range 1-9, but found 0', self.get_mark())
            self.forward()
            ch = self.peek()
            if ch in u'+-':
                if ch == '+':
                    chomping = True
                else:
                    chomping = False
                self.forward()
        ch = self.peek()
        if ch not in u'\x00 \r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a block scalar', start_mark, 'expected chomping or indentation indicators, but found %r' % ch.encode('utf-8'), self.get_mark())
        return (chomping, increment)

    def scan_block_scalar_ignored_line(self, start_mark):
        while self.peek() == u' ':
            self.forward()

        if self.peek() == u'#':
            while self.peek() not in u'\x00\r\n\x85\u2028\u2029':
                self.forward()

        ch = self.peek()
        if ch not in u'\x00\r\n\x85\u2028\u2029':
            raise ScannerError('while scanning a block scalar', start_mark, 'expected a comment or a line break, but found %r' % ch.encode('utf-8'), self.get_mark())
        self.scan_line_break()

    def scan_block_scalar_indentation(self):
        chunks = []
        max_indent = 0
        end_mark = self.get_mark()
        while self.peek() in u' \r\n\x85\u2028\u2029':
            if self.peek() != u' ':
                chunks.append(self.scan_line_break())
                end_mark = self.get_mark()
            else:
                self.forward()
                if self.column > max_indent:
                    max_indent = self.column

        return (chunks, max_indent, end_mark)

    def scan_block_scalar_breaks(self, indent):
        chunks = []
        end_mark = self.get_mark()
        while self.column < indent and self.peek() == u' ':
            self.forward()

        while self.peek() in u'\r\n\x85\u2028\u2029':
            chunks.append(self.scan_line_break())
            end_mark = self.get_mark()
            while self.column < indent and self.peek() == u' ':
                self.forward()

        return (chunks, end_mark)

    def scan_flow_scalar(self, style):
        if style == '"':
            double = True
        else:
            double = False
        chunks = []
        start_mark = self.get_mark()
        quote = self.peek()
        self.forward()
        chunks.extend(self.scan_flow_scalar_non_spaces(double, start_mark))
        while self.peek() != quote:
            chunks.extend(self.scan_flow_scalar_spaces(double, start_mark))
            chunks.extend(self.scan_flow_scalar_non_spaces(double, start_mark))

        self.forward()
        end_mark = self.get_mark()
        return ScalarToken(u''.join(chunks), False, start_mark, end_mark, style)

    ESCAPE_REPLACEMENTS = {u'0': u'\x00',
     u'a': u'\x07',
     u'b': u'\x08',
     u't': u'\t',
     u'\t': u'\t',
     u'n': u'\n',
     u'v': u'\x0b',
     u'f': u'\x0c',
     u'r': u'\r',
     u'e': u'\x1b',
     u' ': u' ',
     u'"': u'"',
     u'\\': u'\\',
     u'N': u'\x85',
     u'_': u'\xa0',
     u'L': u'\u2028',
     u'P': u'\u2029'}
    ESCAPE_CODES = {u'x': 2,
     u'u': 4,
     u'U': 8}

    def scan_flow_scalar_non_spaces(self, double, start_mark):
        chunks = []
        while True:
            length = 0
            while self.peek(length) not in u'\'"\\\x00 \t\r\n\x85\u2028\u2029':
                length += 1

            if length:
                chunks.append(self.prefix(length))
                self.forward(length)
            ch = self.peek()
            if not double and ch == u"'" and self.peek(1) == u"'":
                chunks.append(u"'")
                self.forward(2)
            elif double and ch == u"'" or not double and ch in u'"\\':
                chunks.append(ch)
                self.forward()
            elif double and ch == u'\\':
                self.forward()
                ch = self.peek()
                if ch in self.ESCAPE_REPLACEMENTS:
                    chunks.append(self.ESCAPE_REPLACEMENTS[ch])
                    self.forward()
                elif ch in self.ESCAPE_CODES:
                    length = self.ESCAPE_CODES[ch]
                    self.forward()
                    for k in range(length):
                        if self.peek(k) not in u'0123456789ABCDEFabcdef':
                            raise ScannerError('while scanning a double-quoted scalar', start_mark, 'expected escape sequence of %d hexdecimal numbers, but found %r' % (length, self.peek(k).encode('utf-8')), self.get_mark())

                    code = int(self.prefix(length), 16)
                    chunks.append(unichr(code))
                    self.forward(length)
                elif ch in u'\r\n\x85\u2028\u2029':
                    self.scan_line_break()
                    chunks.extend(self.scan_flow_scalar_breaks(double, start_mark))
                else:
                    raise ScannerError('while scanning a double-quoted scalar', start_mark, 'found unknown escape character %r' % ch.encode('utf-8'), self.get_mark())
            else:
                return chunks

    def scan_flow_scalar_spaces(self, double, start_mark):
        chunks = []
        length = 0
        while self.peek(length) in u' \t':
            length += 1

        whitespaces = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch == u'\x00':
            raise ScannerError('while scanning a quoted scalar', start_mark, 'found unexpected end of stream', self.get_mark())
        elif ch in u'\r\n\x85\u2028\u2029':
            line_break = self.scan_line_break()
            breaks = self.scan_flow_scalar_breaks(double, start_mark)
            if line_break != u'\n':
                chunks.append(line_break)
            elif not breaks:
                chunks.append(u' ')
            chunks.extend(breaks)
        else:
            chunks.append(whitespaces)
        return chunks

    def scan_flow_scalar_breaks(self, double, start_mark):
        chunks = []
        while True:
            prefix = self.prefix(3)
            if (prefix == u'---' or prefix == u'...') and self.peek(3) in u'\x00 \t\r\n\x85\u2028\u2029':
                raise ScannerError('while scanning a quoted scalar', start_mark, 'found unexpected document separator', self.get_mark())
            while self.peek() in u' \t':
                self.forward()

            if self.peek() in u'\r\n\x85\u2028\u2029':
                chunks.append(self.scan_line_break())
            else:
                return chunks

    def scan_plain(self):
        chunks = []
        start_mark = self.get_mark()
        end_mark = start_mark
        indent = self.indent + 1
        spaces = []
        while True:
            length = 0
            if self.peek() == u'#':
                break
            while True:
                ch = self.peek(length)
                if ch in u'\x00 \t\r\n\x85\u2028\u2029' or not self.flow_level and ch == u':' and self.peek(length + 1) in u'\x00 \t\r\n\x85\u2028\u2029' or self.flow_level and ch in u',:?[]{}':
                    break
                length += 1

            if self.flow_level and ch == u':' and self.peek(length + 1) not in u'\x00 \t\r\n\x85\u2028\u2029,[]{}':
                self.forward(length)
                raise ScannerError('while scanning a plain scalar', start_mark, "found unexpected ':'", self.get_mark(), 'Please check http://pyyaml.org/wiki/YAMLColonInFlowContext for details.')
            if length == 0:
                break
            self.allow_simple_key = False
            chunks.extend(spaces)
            chunks.append(self.prefix(length))
            self.forward(length)
            end_mark = self.get_mark()
            spaces = self.scan_plain_spaces(indent, start_mark)
            if not spaces or self.peek() == u'#' or not self.flow_level and self.column < indent:
                break

        return ScalarToken(u''.join(chunks), True, start_mark, end_mark)

    def scan_plain_spaces(self, indent, start_mark):
        chunks = []
        length = 0
        while self.peek(length) in u' ':
            length += 1

        whitespaces = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch in u'\r\n\x85\u2028\u2029':
            line_break = self.scan_line_break()
            self.allow_simple_key = True
            prefix = self.prefix(3)
            if (prefix == u'---' or prefix == u'...') and self.peek(3) in u'\x00 \t\r\n\x85\u2028\u2029':
                return
            breaks = []
            while self.peek() in u' \r\n\x85\u2028\u2029':
                if self.peek() == ' ':
                    self.forward()
                else:
                    breaks.append(self.scan_line_break())
                    prefix = self.prefix(3)
                    if (prefix == u'---' or prefix == u'...') and self.peek(3) in u'\x00 \t\r\n\x85\u2028\u2029':
                        return

            if line_break != u'\n':
                chunks.append(line_break)
            elif not breaks:
                chunks.append(u' ')
            chunks.extend(breaks)
        elif whitespaces:
            chunks.append(whitespaces)
        return chunks

    def scan_tag_handle(self, name, start_mark):
        ch = self.peek()
        if ch != u'!':
            raise ScannerError('while scanning a %s' % name, start_mark, "expected '!', but found %r" % ch.encode('utf-8'), self.get_mark())
        length = 1
        ch = self.peek(length)
        if ch != u' ':
            while u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u'-_':
                length += 1
                ch = self.peek(length)

            if ch != u'!':
                self.forward(length)
                raise ScannerError('while scanning a %s' % name, start_mark, "expected '!', but found %r" % ch.encode('utf-8'), self.get_mark())
            length += 1
        value = self.prefix(length)
        self.forward(length)
        return value

    def scan_tag_uri(self, name, start_mark):
        chunks = []
        length = 0
        ch = self.peek(length)
        while u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u"-;/?:@&=+$,_.!~*'()[]%":
            if ch == u'%':
                chunks.append(self.prefix(length))
                self.forward(length)
                length = 0
                chunks.append(self.scan_uri_escapes(name, start_mark))
            else:
                length += 1
            ch = self.peek(length)

        if length:
            chunks.append(self.prefix(length))
            self.forward(length)
            length = 0
        if not chunks:
            raise ScannerError('while parsing a %s' % name, start_mark, 'expected URI, but found %r' % ch.encode('utf-8'), self.get_mark())
        return u''.join(chunks)

    def scan_uri_escapes(self, name, start_mark):
        bytes = []
        mark = self.get_mark()
        while self.peek() == u'%':
            self.forward()
            for k in range(2):
                if self.peek(k) not in u'0123456789ABCDEFabcdef':
                    raise ScannerError('while scanning a %s' % name, start_mark, 'expected URI escape sequence of 2 hexdecimal numbers, but found %r' % self.peek(k).encode('utf-8'), self.get_mark())

            bytes.append(chr(int(self.prefix(2), 16)))
            self.forward(2)

        try:
            value = unicode(''.join(bytes), 'utf-8')
        except UnicodeDecodeError as exc:
            raise ScannerError('while scanning a %s' % name, start_mark, str(exc), mark)

        return value

    def scan_line_break(self):
        ch = self.peek()
        if ch in u'\r\n\x85':
            if self.prefix(2) == u'\r\n':
                self.forward(2)
            else:
                self.forward()
            return u'\n'
        if ch in u'\u2028\u2029':
            self.forward()
            return ch
        return u''