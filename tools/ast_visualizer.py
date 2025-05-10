import sys
from typing import List, override

from python_lox.ast import expr as Expr
from python_lox.ast import stmt as Stmt
from python_lox.lexer import Lexer
from python_lox.parser import Parser

"""
Use graphviz to visualize the AST

Example online viewer: 
https://dreampuf.github.io/GraphvizOnline

Or if you have it installed locally
$ dot -Tpng dotf.gv -o graph.png
"""

graphviz_statements: List[str] = []


class AstVisualizer(Expr.Visitor[int], Stmt.Visitor[int]):
    def __init__(self) -> None:
        super().__init__()
        self.counter = 0

    def visualize(
        self,
        obj: Expr.Expr | Stmt.Stmt | List[Stmt.Stmt],
        statements_label: str | None = None,
    ) -> int:
        if isinstance(obj, Expr.Expr) or isinstance(obj, Stmt.Stmt):
            return obj.accept(self)
        else:
            self.counter += 1
            this_id = self.counter
            graphviz_statements.append(f'node{this_id} [label="{statements_label}"];')
            for stmt in obj:
                stmt_id = stmt.accept(self)
                graphviz_statements.append(f"node{this_id} -> node{stmt_id};")
            return this_id

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(
            f'node{this_id} [label="{expr.operator.string_repr}"];'
        )

        left_id = expr.left.accept(self)
        right_id = expr.right.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{left_id};")
        graphviz_statements.append(f"node{this_id} -> node{right_id};")
        return this_id

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="()"];')

        group_id = expr.expression.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{group_id};")
        return this_id

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="{expr.value}"];')

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

        graphviz_statements.append(f'node{this_id} [label="?:"];')

        cond_id = expr.condition.accept(self)
        if_id = expr.if_branch.accept(self)
        else_id = expr.else_branch.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{cond_id};")
        graphviz_statements.append(f"node{this_id} -> node{if_id};")
        graphviz_statements.append(f"node{this_id} -> node{else_id};")
        return this_id

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(
            f'node{this_id} [label="{expr.operator.string_repr}"];'
        )

        expr_id = expr.right.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_arrow_expr(self, expr: Expr.Arrow) -> int:
        self.counter += 1
        this_id = self.counter

        params = ",".join([i.string_repr for i in expr.params])
        graphviz_statements.append(f'node{this_id} [label="arrow_function({params})"];')

        expr_id = self.visualize(expr.body, statements_label="block")

        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_assert_stmt(self, stmt: Stmt.Assert) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="assert"];')

        expr_id = stmt.expression.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_assign_expr(self, expr: Expr.Assign) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="assign_expression"];')

        self.counter += 1
        lvalue = self.counter
        graphviz_statements.append(f'node{lvalue} [label="{expr.name.string_repr}"];')
        graphviz_statements.append(f'node{this_id} -> node{lvalue} [label="lvalue"];')

        expr_id = expr.value.accept(self)

        graphviz_statements.append(f'node{this_id} -> node{expr_id} [label="rvalue"];')
        return this_id

    @override
    def visit_block_stmt(self, stmt: Stmt.Block) -> int:
        expr_id = self.visualize(stmt.statements, statements_label="block")
        return expr_id

    @override
    def visit_break_stmt(self, stmt: Stmt.Break) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="break"];')
        return this_id

    @override
    def visit_call_expr(self, expr: Expr.Call) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="call"];')

        expr_id = expr.callee.accept(self)
        graphviz_statements.append(f'node{this_id} -> node{expr_id} [label="callee"];')

        self.counter += 1
        args_id = self.counter
        graphviz_statements.append(f'node{args_id} [label="args"];')
        graphviz_statements.append(f"node{this_id} -> node{args_id};")

        for arg in expr.args:
            exp_id = arg.accept(self)
            graphviz_statements.append(f"node{args_id} -> node{exp_id};")
        return this_id

    @override
    def visit_const_stmt(self, stmt: Stmt.Const) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="const"];')

        self.counter += 1
        var_name_id = self.counter

        graphviz_statements.append(
            f'node{var_name_id} [label="{stmt.name.string_repr}"];'
        )
        graphviz_statements.append(f"node{this_id} -> node{var_name_id};")

        if stmt.initializer:
            expr_id = stmt.initializer.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{expr_id} [label="initializer"];'
            )

        return this_id

    @override
    def visit_continue_stmt(self, stmt: Stmt.Continue) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="continue"];')
        return this_id

    @override
    def visit_expression_stmt(self, stmt: Stmt.Expression) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="expression_statement"];')

        expr_id = stmt.expression.accept(self)

        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_for_stmt(self, stmt: Stmt.For) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="for"];')

        if stmt.initializer:
            initialize_id = stmt.initializer.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{initialize_id} [label="initializer"];'
            )
        if stmt.condition:
            condition_id = stmt.condition.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{condition_id} [label="condition"];'
            )
        if stmt.update:
            update_id = stmt.update.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{update_id} [label="update"];'
            )

        body_id = stmt.body.accept(self)
        graphviz_statements.append(f"node{this_id} -> node{body_id};")

        return this_id

    @override
    def visit_print_stmt(self, stmt: Stmt.Print) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="print"];')
        expr_id = stmt.expression.accept(self)
        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_println_stmt(self, stmt: Stmt.Println) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="println"];')
        expr_id = stmt.expression.accept(self)
        graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_return_stmt(self, stmt: Stmt.Return) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="return"];')
        if stmt.value:
            expr_id = stmt.value.accept(self)
            graphviz_statements.append(f"node{this_id} -> node{expr_id};")
        return this_id

    @override
    def visit_super_expr(self, expr: Expr.Super) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="super"];')
        return this_id

    @override
    def visit_this_expr(self, expr: Expr.This) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="this"];')
        return this_id

    @override
    def visit_var_stmt(self, stmt: Stmt.Var) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="var"];')

        self.counter += 1
        var_name_id = self.counter

        graphviz_statements.append(
            f'node{var_name_id} [label="{stmt.name.string_repr}"];'
        )
        graphviz_statements.append(f"node{this_id} -> node{var_name_id};")

        if stmt.initializer:
            expr_id = stmt.initializer.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{expr_id} [label="initializer"];'
            )

        return this_id

    @override
    def visit_while_stmt(self, stmt: Stmt.While) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="while"];')

        if stmt.condition:
            condition_id = stmt.condition.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{condition_id} [label="condition"];'
            )

        body_id = stmt.body.accept(self)
        graphviz_statements.append(f"node{this_id} -> node{body_id};")
        return this_id

    @override
    def visit_variable_expr(self, expr: Expr.Variable) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="{expr.name.string_repr}"];')
        return this_id

    @override
    def visit_if_stmt(self, stmt: Stmt.If) -> int:
        self.counter += 1
        this_id = self.counter
        graphviz_statements.append(f'node{this_id} [label="if-else"];')

        expr_id = stmt.condition.accept(self)
        graphviz_statements.append(
            f'node{this_id} -> node{expr_id} [label="condition"];'
        )

        if_body = stmt.if_branch.accept(self)
        graphviz_statements.append(f'node{this_id} -> node{if_body} [label="if"];')

        if stmt.else_branch:
            else_body = stmt.else_branch.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{else_body} [label="else"];'
            )

        return this_id

    @override
    def visit_function_stmt(self, stmt: Stmt.Function) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(
            f'node{this_id} [label="function {stmt.name.string_repr}"];'
        )

        self.counter += 1
        params_id = self.counter

        params = ", ".join([param.string_repr for param in stmt.params])
        graphviz_statements.append(f'node{params_id} [label="params({params})"];')
        graphviz_statements.append(f"node{this_id} -> node{params_id};")

        body_id = self.visualize(stmt.body, statements_label="block")
        graphviz_statements.append(f"node{this_id} -> node{body_id};")

        return this_id

    @override
    def visit_class_stmt(self, stmt: Stmt.Class) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(
            f'node{this_id} [label="class {stmt.name.string_repr}"];'
        )

        if stmt.base_class:
            baseclass_id = stmt.base_class.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{baseclass_id} [label="base_class"];'
            )

        for method in stmt.methods:
            method_id = method.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{method_id} [label="method"];'
            )

        for static_method in stmt.static_methods:
            static_method_id = static_method.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{static_method_id} [label="static method"];'
            )

        for getter in stmt.getters:
            getter_id = getter.accept(self)
            graphviz_statements.append(
                f'node{this_id} -> node{getter_id} [label="getter"];'
            )

        return this_id

    @override
    def visit_set_expr(self, expr: Expr.Set) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="set"];')

        object_id = expr.obj.accept(self)
        graphviz_statements.append(
            f'node{this_id} -> node{object_id} [label="object"];'
        )

        self.counter += 1
        property_id = self.counter
        graphviz_statements.append(
            f'node{property_id} [label="{expr.name.string_repr}"];'
        )
        graphviz_statements.append(
            f'node{this_id} -> node{property_id} [label="property"];'
        )

        value_id = expr.value.accept(self)
        graphviz_statements.append(f'node{this_id} -> node{value_id} [label="value"];')

        return this_id

    @override
    def visit_get_expr(self, expr: Expr.Get) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(f'node{this_id} [label="get"];')

        object_id = expr.obj.accept(self)
        graphviz_statements.append(
            f'node{this_id} -> node{object_id} [label="object"];'
        )

        self.counter += 1
        property_id = self.counter
        graphviz_statements.append(
            f'node{property_id} [label="{expr.name.string_repr}"];'
        )
        graphviz_statements.append(
            f'node{this_id} -> node{property_id} [label="property"];'
        )

        return this_id

    @override
    def visit_logical_expr(self, expr: Expr.Logical) -> int:
        self.counter += 1
        this_id = self.counter

        graphviz_statements.append(
            f'node{this_id} [label="{expr.operator.string_repr}"];'
        )

        left_id = expr.left.accept(self)
        right_id = expr.right.accept(self)

        graphviz_statements.append(f'node{this_id} -> node{left_id} [label="left"];')
        graphviz_statements.append(f'node{this_id} -> node{right_id} [label="right"];')
        return this_id


lexer = Lexer(sys.stdin.read())
parser = Parser(lexer.process())
statements = parser.parse()
if statements is None:
    print("Parse error")
    exit()
visualizer = AstVisualizer()
visualizer.visualize(statements, statements_label="program")

print("digraph G {")
for statement in graphviz_statements:
    print(f"    {statement}")
print("}")
