#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\optimizer.py
from jinja2 import nodes
from jinja2.visitor import NodeTransformer

def optimize(node, environment):
    optimizer = Optimizer(environment)
    return optimizer.visit(node)


class Optimizer(NodeTransformer):

    def __init__(self, environment):
        self.environment = environment

    def visit_If(self, node):
        if node.find(nodes.Block) is not None:
            return self.generic_visit(node)
        try:
            val = self.visit(node.test).as_const()
        except nodes.Impossible:
            return self.generic_visit(node)

        if val:
            body = node.body
        else:
            body = node.else_
        result = []
        for node in body:
            result.extend(self.visit_list(node))

        return result

    def fold(self, node):
        node = self.generic_visit(node)
        try:
            return nodes.Const.from_untrusted(node.as_const(), lineno=node.lineno, environment=self.environment)
        except nodes.Impossible:
            return node

    visit_Add = visit_Sub = visit_Mul = visit_Div = visit_FloorDiv = visit_Pow = visit_Mod = visit_And = visit_Or = visit_Pos = visit_Neg = visit_Not = visit_Compare = visit_Getitem = visit_Getattr = visit_Call = visit_Filter = visit_Test = visit_CondExpr = fold
    del fold