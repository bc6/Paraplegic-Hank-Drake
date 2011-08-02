from string import digits
from cStringIO import StringIO
from tokenize import generate_tokens, NL
_consts = {'None': None,
 'False': False,
 'True': True}

def SimpleEval(source):
    itertokens = generate_tokens(StringIO(source).readline)
    next = (token[1] for token in itertokens if token[0] is not NL).next
    res = atom(next, next())
    if next():
        raise SyntaxError('bogus data after expression')
    return res



def atom(next, token):

    def _iter_sequence(end):
        token = next()
        while token != end:
            yield atom(next, token)
            token = next()
            if token == ',':
                token = next()



    firstchar = token[0]
    if token in _consts:
        return _consts[token]
    if token[-1] == 'L':
        return long(token)
    if firstchar in digits:
        if '.' in token:
            return float(token)
        return int(token)
    if firstchar in '"\'':
        return token[1:-1].decode('string-escape')
    if firstchar == 'u':
        return token[2:-1].decode('unicode-escape')
    if token == '-':
        return -atom(next, next())
    if token == '(':
        return tuple(_iter_sequence(')'))
    if token == '[':
        return list(_iter_sequence(']'))
    if token == '{':
        out = {}
        token = next()
        while token != '}':
            key = atom(next, token)
            next()
            token = next()
            out[key] = atom(next, token)
            token = next()
            if token == ',':
                token = next()

        return out
    raise SyntaxError('malformed expression (%r)' % token)


exports = {'util.SimpleEval': SimpleEval}

