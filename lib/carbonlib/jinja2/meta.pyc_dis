#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\meta.py
from jinja2 import nodes
from jinja2.compiler import CodeGenerator

class TrackingCodeGenerator(CodeGenerator):

    def __init__(self, environment):
        CodeGenerator.__init__(self, environment, '<introspection>', '<introspection>')
        self.undeclared_identifiers = set()

    def write(self, x):
        pass

    def pull_locals(self, frame):
        self.undeclared_identifiers.update(frame.identifiers.undeclared)


def find_undeclared_variables(ast):
    codegen = TrackingCodeGenerator(ast.environment)
    codegen.visit(ast)
    return codegen.undeclared_identifiers


def find_referenced_templates(ast):
    for node in ast.find_all((nodes.Extends,
     nodes.FromImport,
     nodes.Import,
     nodes.Include)):
        if not isinstance(node.template, nodes.Const):
            if isinstance(node.template, (nodes.Tuple, nodes.List)):
                for template_name in node.template.items:
                    if isinstance(template_name, nodes.Const):
                        if isinstance(template_name.value, basestring):
                            yield template_name.value
                    else:
                        yield

            else:
                yield
            continue
        if isinstance(node.template.value, basestring):
            yield node.template.value
        elif isinstance(node, nodes.Include) and isinstance(node.template.value, (tuple, list)):
            for template_name in node.template.value:
                if isinstance(template_name, basestring):
                    yield template_name

        else:
            yield