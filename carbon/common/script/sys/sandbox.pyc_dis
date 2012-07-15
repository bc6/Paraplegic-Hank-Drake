#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/sys/sandbox.py
import dis

def _get_opcodes(codeobj):
    i = 0
    opcodes = {}
    s = codeobj.co_code
    while i < len(s):
        code = ord(s[i])
        opcodes[code] = True
        if code >= dis.HAVE_ARGUMENT:
            i += 3
        else:
            i += 1

    return opcodes.keys()


def fingerprint(*args):
    allCodes = {}
    for expr in args:
        try:
            c = compile(expr, '', 'eval')
        except:
            raise ValueError, '%s is not a valid expression' % strx(expr)

        for code in _get_opcodes(c):
            allCodes[code] = True

    return allCodes.keys()


constant_codes = fingerprint('+1', '-1L', "'asdf'", "u'asdf'", '(1,2)', '[1,2]')
expression_codes = fingerprint('+1', '-1L', "'asdf'", "u'asdf'", '(1,2)', '[1,2]', '(1)', '1+1', '1-1', '2*2', '2/2', '2%2', '2**2', '~2', '1<<1', '1>>1', '1&1', '1|1', '1 or 1', '1 and 1', 'not 1')

def test_expr(expr, allowed_codes):
    try:
        c = compile(expr, '', 'eval')
    except:
        raise ValueError, '%s is not a valid expression' % strx(expr)

    codes = _get_opcodes(c)
    for code in codes:
        if code not in allowed_codes:
            raise ValueError, 'opcode %s not allowed' % dis.opname[code]

    return c


def eval_fingerprinted(expr, fingerprint, g = None, l = None):
    c = test_expr(expr, fingerprint)
    if l is not None:
        return eval(c, g, l)
    if g is not None:
        return eval(c, g)
    return eval(c)


def eval_constant(expr, g = None, l = None):
    return eval_fingerprinted(expr, constant_codes, g, l)


def eval_expression(expr, g = None, l = None):
    return eval_fingerprinted(expr, expression_codes, g, l)


exports = {'sandbox.eval_constant': eval_constant,
 'sandbox.eval_expression': eval_expression,
 'sandbox.fingerprint': fingerprint,
 'sandbox.eval': eval_fingerprinted}