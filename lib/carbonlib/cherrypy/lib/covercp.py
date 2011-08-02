import re
import sys
import cgi
from urllib import quote_plus
import os
import os.path
localFile = os.path.join(os.path.dirname(__file__), 'coverage.cache')
try:
    from coverage import the_coverage as coverage

    def start():
        coverage.start()


except ImportError:
    coverage = None
    import warnings
    warnings.warn('No code coverage will be performed; coverage.py could not be imported.')

    def start():
        pass


start.priority = 20
TEMPLATE_MENU = '<html>\n<head>\n    <title>CherryPy Coverage Menu</title>\n    <style>\n        body {font: 9pt Arial, serif;}\n        #tree {\n            font-size: 8pt;\n            font-family: Andale Mono, monospace;\n            white-space: pre;\n            }\n        #tree a:active, a:focus {\n            background-color: black;\n            padding: 1px;\n            color: white;\n            border: 0px solid #9999FF;\n            -moz-outline-style: none;\n            }\n        .fail { color: red;}\n        .pass { color: #888;}\n        #pct { text-align: right;}\n        h3 {\n            font-size: small;\n            font-weight: bold;\n            font-style: italic;\n            margin-top: 5px; \n            }\n        input { border: 1px solid #ccc; padding: 2px; }\n        .directory {\n            color: #933;\n            font-style: italic;\n            font-weight: bold;\n            font-size: 10pt;\n            }\n        .file {\n            color: #400;\n            }\n        a { text-decoration: none; }\n        #crumbs {\n            color: white;\n            font-size: 8pt;\n            font-family: Andale Mono, monospace;\n            width: 100%;\n            background-color: black;\n            }\n        #crumbs a {\n            color: #f88;\n            }\n        #options {\n            line-height: 2.3em;\n            border: 1px solid black;\n            background-color: #eee;\n            padding: 4px;\n            }\n        #exclude {\n            width: 100%;\n            margin-bottom: 3px;\n            border: 1px solid #999;\n            }\n        #submit {\n            background-color: black;\n            color: white;\n            border: 0;\n            margin-bottom: -9px;\n            }\n    </style>\n</head>\n<body>\n<h2>CherryPy Coverage</h2>'
TEMPLATE_FORM = '\n<div id="options">\n<form action=\'menu\' method=GET>\n    <input type=\'hidden\' name=\'base\' value=\'%(base)s\' />\n    Show percentages <input type=\'checkbox\' %(showpct)s name=\'showpct\' value=\'checked\' /><br />\n    Hide files over <input type=\'text\' id=\'pct\' name=\'pct\' value=\'%(pct)s\' size=\'3\' />%%<br />\n    Exclude files matching<br />\n    <input type=\'text\' id=\'exclude\' name=\'exclude\' value=\'%(exclude)s\' size=\'20\' />\n    <br />\n\n    <input type=\'submit\' value=\'Change view\' id="submit"/>\n</form>\n</div>'
TEMPLATE_FRAMESET = "<html>\n<head><title>CherryPy coverage data</title></head>\n<frameset cols='250, 1*'>\n    <frame src='menu?base=%s' />\n    <frame name='main' src='' />\n</frameset>\n</html>\n"
TEMPLATE_COVERAGE = '<html>\n<head>\n    <title>Coverage for %(name)s</title>\n    <style>\n        h2 { margin-bottom: .25em; }\n        p { margin: .25em; }\n        .covered { color: #000; background-color: #fff; }\n        .notcovered { color: #fee; background-color: #500; }\n        .excluded { color: #00f; background-color: #fff; }\n         table .covered, table .notcovered, table .excluded\n             { font-family: Andale Mono, monospace;\n               font-size: 10pt; white-space: pre; }\n\n         .lineno { background-color: #eee;}\n         .notcovered .lineno { background-color: #000;}\n         table { border-collapse: collapse;\n    </style>\n</head>\n<body>\n<h2>%(name)s</h2>\n<p>%(fullpath)s</p>\n<p>Coverage: %(pc)s%%</p>'
TEMPLATE_LOC_COVERED = '<tr class="covered">\n    <td class="lineno">%s&nbsp;</td>\n    <td>%s</td>\n</tr>\n'
TEMPLATE_LOC_NOT_COVERED = '<tr class="notcovered">\n    <td class="lineno">%s&nbsp;</td>\n    <td>%s</td>\n</tr>\n'
TEMPLATE_LOC_EXCLUDED = '<tr class="excluded">\n    <td class="lineno">%s&nbsp;</td>\n    <td>%s</td>\n</tr>\n'
TEMPLATE_ITEM = "%s%s<a class='file' href='report?name=%s' target='main'>%s</a>\n"

def _percent(statements, missing):
    s = len(statements)
    e = s - len(missing)
    if s > 0:
        return int(round(100.0 * e / s))
    return 0



def _show_branch(root, base, path, pct = 0, showpct = False, exclude = ''):
    dirs = [ k for (k, v,) in root.items() if v ]
    dirs.sort()
    for name in dirs:
        newpath = os.path.join(path, name)
        if newpath.lower().startswith(base):
            relpath = newpath[len(base):]
            yield '| ' * relpath.count(os.sep)
            yield "<a class='directory' href='menu?base=%s&exclude=%s'>%s</a>\n" % (newpath, quote_plus(exclude), name)
        for chunk in _show_branch(root[name], base, newpath, pct, showpct, exclude):
            yield chunk


    if path.lower().startswith(base):
        relpath = path[len(base):]
        files = [ k for (k, v,) in root.items() if not v ]
        files.sort()
        for name in files:
            newpath = os.path.join(path, name)
            pc_str = ''
            if showpct:
                try:
                    (_, statements, _, missing, _,) = coverage.analysis2(newpath)
                except:
                    pass
                else:
                    pc = _percent(statements, missing)
                    pc_str = ('%3d%% ' % pc).replace(' ', '&nbsp;')
                    if pc < float(pct) or pc == -1:
                        pc_str = "<span class='fail'>%s</span>" % pc_str
                    else:
                        pc_str = "<span class='pass'>%s</span>" % pc_str
            yield TEMPLATE_ITEM % ('| ' * (relpath.count(os.sep) + 1),
             pc_str,
             newpath,
             name)




def _skip_file(path, exclude):
    if exclude:
        return bool(re.search(exclude, path))



def _graft(path, tree):
    d = tree
    p = path
    atoms = []
    while True:
        (p, tail,) = os.path.split(p)
        if not tail:
            break
        atoms.append(tail)

    atoms.append(p)
    if p != '/':
        atoms.append('/')
    atoms.reverse()
    for node in atoms:
        if node:
            d = d.setdefault(node, {})




def get_tree(base, exclude):
    tree = {}
    coverage.get_ready()
    runs = list(coverage.cexecuted.keys())
    if runs:
        for path in runs:
            if not _skip_file(path, exclude) and not os.path.isdir(path):
                _graft(path, tree)

    return tree



class CoverStats(object):

    def __init__(self, root = None):
        if root is None:
            import cherrypy
            root = os.path.dirname(cherrypy.__file__)
        self.root = root



    def index(self):
        return TEMPLATE_FRAMESET % self.root.lower()


    index.exposed = True

    def menu(self, base = '/', pct = '50', showpct = '', exclude = 'python\\d\\.\\d|test|tut\\d|tutorial'):
        base = base.lower().rstrip(os.sep)
        yield TEMPLATE_MENU
        yield TEMPLATE_FORM % locals()
        yield "<div id='crumbs'>"
        path = ''
        atoms = base.split(os.sep)
        atoms.pop()
        for atom in atoms:
            path += atom + os.sep
            yield "<a href='menu?base=%s&exclude=%s'>%s</a> %s" % (path,
             quote_plus(exclude),
             atom,
             os.sep)

        yield '</div>'
        yield "<div id='tree'>"
        tree = get_tree(base, exclude)
        if not tree:
            yield '<p>No modules covered.</p>'
        else:
            for chunk in _show_branch(tree, base, '/', pct, showpct == 'checked', exclude):
                yield chunk

        yield '</div>'
        yield '</body></html>'


    menu.exposed = True

    def annotated_file(self, filename, statements, excluded, missing):
        source = open(filename, 'r')
        buffer = []
        for (lineno, line,) in enumerate(source.readlines()):
            lineno += 1
            line = line.strip('\n\r')
            empty_the_buffer = True
            if lineno in excluded:
                template = TEMPLATE_LOC_EXCLUDED
            elif lineno in missing:
                template = TEMPLATE_LOC_NOT_COVERED
            elif lineno in statements:
                template = TEMPLATE_LOC_COVERED
            else:
                empty_the_buffer = False
                buffer.append((lineno, line))
            if empty_the_buffer:
                for (lno, pastline,) in buffer:
                    yield template % (lno, cgi.escape(pastline))

                buffer = []
                yield template % (lineno, cgi.escape(line))




    def report(self, name):
        coverage.get_ready()
        (filename, statements, excluded, missing, _,) = coverage.analysis2(name)
        pc = _percent(statements, missing)
        yield TEMPLATE_COVERAGE % dict(name=os.path.basename(name), fullpath=name, pc=pc)
        yield '<table>\n'
        for line in self.annotated_file(filename, statements, excluded, missing):
            yield line

        yield '</table>'
        yield '</body>'
        yield '</html>'


    report.exposed = True


def serve(path = localFile, port = 8080, root = None):
    if coverage is None:
        raise ImportError('The coverage module could not be imported.')
    coverage.cache_default = path
    import cherrypy
    cherrypy.config.update({'server.socket_port': int(port),
     'server.thread_pool': 10,
     'environment': 'production'})
    cherrypy.quickstart(CoverStats(root))


if __name__ == '__main__':
    serve(*tuple(sys.argv[1:]))

