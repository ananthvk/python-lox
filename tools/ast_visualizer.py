from python_lox.ast import expr as Expr
from python_lox.lexer import Lexer
from python_lox.parser import Parser
from typing import List, override

"""
Use graphviz to visualize the AST

Example online viewer: 
https://dreampuf.github.io/GraphvizOnline

Or if you have it installed locally
$ dot -Tpng dotf.gv -o graph.png
"""

statements: List[str] = []


class ASTExpressionVisualizer(Expr.Visitor[int]):

    def __init__(self) -> None:
        super().__init__()
        self.counter = 0

    def visualize(self, expr: Expr.Expr) -> int:
        return expr.accept(self)

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> int:
        self.counter += 1
        this_id = self.counter
        statements.append(f'node{this_id} [label="{expr.operator.string_repr}"];')

        left_id = expr.left.accept(self)
        right_id = expr.right.accept(self)

        statements.append(f"node{this_id} -> node{left_id};")
        statements.append(f"node{this_id} -> node{right_id};")
        return this_id

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> int:
        self.counter += 1
        this_id = self.counter

        statements.append(f'node{this_id} [label="()"];')

        group_id = expr.expression.accept(self)

        statements.append(f"node{this_id} -> node{group_id};")
        return this_id

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> int:
        self.counter += 1
        this_id = self.counter

        statements.append(f'node{this_id} [label="{expr.value}"];')

        # Literal do not have any children
        """
        if expr.value is None:
            return "nil"
        if isinstance(expr.value, bool):
            return str(expr.value).lower()
        return str(expr.value)
        """

        return this_id

    @override
    def visit_ternary_expr(self, expr: Expr.Ternary) -> int:
        self.counter += 1
        this_id = self.counter

        statements.append(f'node{this_id} [label="?:"];')

        cond_id = expr.condition.accept(self)
        if_id = expr.if_branch.accept(self)
        else_id = expr.else_branch.accept(self)

        statements.append(f"node{this_id} -> node{cond_id};")
        statements.append(f"node{this_id} -> node{if_id};")
        statements.append(f"node{this_id} -> node{else_id};")
        return this_id

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> int:
        self.counter += 1
        this_id = self.counter

        statements.append(f'node{this_id} [label="{expr.operator.string_repr}"];')

        expr_id = expr.right.accept(self)

        statements.append(f"node{this_id} -> node{expr_id};")
        return this_id


lexer = Lexer(input(""))
parser = Parser(lexer.process())
exp = parser.parse()
visualizer = ASTExpressionVisualizer()
visualizer.visualize(exp)

print("digraph G {")
for statement in statements:
    print(f"    {statement}")
print("}")
