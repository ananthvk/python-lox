from .exceptions import ParserException
from .token import Token, TokenType
from .ast import stmt
from typing import List, Final
from .ast import expr
from copy import copy
from .error_reporter import ErrorReporter

MAX_ARGUMENTS: Final = 255


class Parser:
    def __init__(
        self, tokens: List[Token], error_reporter: ErrorReporter | None = None
    ) -> None:
        self.tokens = tokens
        self.error_reporter = error_reporter
        self.loop_depth = 0

        # Next token to be processed
        self.current = 0

    def match(self, token_types: List[TokenType]) -> bool:
        """
        Checks if the current token type is same as any of the passed token types
        Args:
            token_types: List of token types that needs to be matched
        Returns:
            bool: True if the current token matches any of the passed token type, this method also calls advance(). False otherwise
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_types: List[TokenType], message: str) -> None:
        """
        Similar to match, but throws an exception if the token type does not match
        """
        if not self.match(token_types):
            token = self.previous()
            raise ParserException(message, token)

    def check(self, token_type: TokenType) -> bool:
        """
        Args:
            token_type: Type of token to be checked
        Returns:
            bool: True if the type of the current token is equal to token_type, False otherwise
        """

        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        token = self.tokens[self.current]
        if not self.is_at_end():
            self.current += 1
        return token

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    # Code for recursive descent parser

    def expression(self) -> expr.Expr:
        return self.comma()

    def comma(self) -> expr.Expr:
        """
        The comma operator has the lowest precedence among all operators, and it evaluates to it's rightmost expression
        It can be of the form comma ("," comma)*
        """
        exp = self.assign()
        while self.match([TokenType.COMMA]):
            operator = self.previous()
            right = self.assign()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def assign(self) -> expr.Expr:
        exp = self.ternary()
        if self.match(
            [
                TokenType.EQUAL,
                TokenType.PLUS_EQUAL,
                TokenType.STAR_EQUAL,
                TokenType.SLASH_EQUAL,
                TokenType.PERCENTAGE_EQUAL,
                TokenType.MINUS_EQUAL,
            ]
        ):
            # Since assignment is right associative
            operator = self.previous()
            value = self.assign()

            if isinstance(exp, expr.Variable):
                name = exp.name
                # Desugar to get binary + assignment
                op: Token = copy(operator)
                match operator.token_type:
                    case TokenType.PLUS_EQUAL:
                        op.token_type = TokenType.PLUS
                        op.string_repr = "+"
                    case TokenType.MINUS_EQUAL:
                        op.token_type = TokenType.MINUS
                        op.string_repr = "-"
                    case TokenType.STAR_EQUAL:
                        op.token_type = TokenType.STAR
                        op.string_repr = "*"
                    case TokenType.SLASH_EQUAL:
                        op.token_type = TokenType.SLASH
                        op.string_repr = "/"
                    case TokenType.PERCENTAGE_EQUAL:
                        op.token_type = TokenType.PERCENTAGE
                        op.string_repr = "%"
                    case TokenType.EQUAL:
                        pass
                    case _:
                        raise SystemExit("Logic error")

                if op.token_type == TokenType.EQUAL:
                    # Simple assignment
                    return expr.Assign(name=name, value=value)
                else:
                    return expr.Assign(
                        name=name,
                        value=expr.Binary(
                            left=expr.Variable(name), operator=op, right=value
                        ),
                    )

            if self.error_reporter is not None:
                self.error_reporter.report(
                    "error", "Invalid assignment", token=operator
                )
            else:
                raise ParserException("Invalid assignment", token=operator)

        return exp

    def ternary(self) -> expr.Expr:
        """
        https://en.cppreference.com/w/c/language/operator_precedence
        In precedence chart, ternery operator's precedence > comma, but is less than equality
        """
        # A ternary expression is of the form: equality?equality:ternary
        exp = self.logical_or()

        # Look for a ?
        if self.match([TokenType.QUESTION_MARK]):
            # It is a ternary expression
            if_branch = self.expression()

            # There should be a mandatory :
            self.consume(
                [TokenType.COLON], "Expected : after if branch in ternary expression"
            )

            # Recursively parse the else branch, since it can contain another ternery (right associative)
            else_branch = self.ternary()
            exp = expr.Ternary(
                condition=exp, if_branch=if_branch, else_branch=else_branch
            )
        return exp

    def logical_or(self) -> expr.Expr:
        exp = self.logical_and()
        while self.match([TokenType.OR]):
            operator = self.previous()
            right = self.logical_and()
            exp = expr.Logical(left=exp, operator=operator, right=right)
        return exp

    def logical_and(self) -> expr.Expr:
        exp = self.equality()
        while self.match([TokenType.AND]):
            operator = self.previous()
            right = self.equality()
            exp = expr.Logical(left=exp, operator=operator, right=right)
        return exp

    def equality(self) -> expr.Expr:
        exp = self.comparison()
        # A equality is of the following form: comparison (("!=" | "==") comparison) *
        while self.match([TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def comparison(self) -> expr.Expr:
        exp = self.term()
        while self.match(
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ]
        ):
            operator = self.previous()
            right = self.term()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def term(self) -> expr.Expr:
        exp = self.factor()
        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def factor(self) -> expr.Expr:
        exp = self.unary()
        while self.match([TokenType.STAR, TokenType.SLASH, TokenType.PERCENTAGE]):
            operator = self.previous()
            right = self.unary()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def unary(self) -> expr.Expr:
        if self.match(
            [TokenType.BANG, TokenType.NOT, TokenType.MINUS, TokenType.TYPEOF]
        ):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator=operator, right=right)

        return self.call()

    def call(self) -> expr.Expr:
        # A function call can be chained if one call returns another function
        # For example: foo()(3, 2)(5, 6) ...
        exp = self.primary()

        while True:
            if self.match([TokenType.LEFT_PAREN]):
                args = self.function_args()
                paren = self.previous()
                exp = expr.Call(callee=exp, paren=paren, args=args)
            else:
                break
        return exp

    def function_args(self) -> List[expr.Expr]:
        # Parses function args, assumes that LEFT_PAREN "(" has already been consumed
        # Returns a list of expressions, that denote the function arguments / parameters
        arguments: List[expr.Expr] = []
        if self.match([TokenType.RIGHT_PAREN]):
            # There are no args
            return arguments

        while True:
            if len(arguments) >= MAX_ARGUMENTS:
                if self.error_reporter is not None:
                    self.error_reporter.report(
                        "error",
                        f"Cannot have more than {MAX_ARGUMENTS} arguments",
                        token=self.peek(),
                    )
                else:
                    raise ParserException(
                        f"Cannot have more than ${MAX_ARGUMENTS} arguments",
                        token=self.peek(),
                    )
            argument = self.assign()
            arguments.append(argument)
            # If there are no more commas, break
            if not self.match([TokenType.COMMA]):
                break

        self.consume([TokenType.RIGHT_PAREN], message='Expected ")" after arguments')
        return arguments

    def function(self, kind: str) -> stmt.Function:
        self.consume([TokenType.IDENTIFIER], f"Expected {kind} name")
        name = self.previous()
        self.consume([TokenType.LEFT_PAREN], f'Expected "(" after {kind} name')

        parameters: List[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= MAX_ARGUMENTS:
                    if self.error_reporter is not None:
                        self.error_reporter.report(
                            "error",
                            f"Cannot have more than {MAX_ARGUMENTS} parameters",
                            token=self.peek(),
                        )
                    else:
                        raise ParserException(
                            f"Cannot have more than ${MAX_ARGUMENTS} parameters",
                            token=self.peek(),
                        )
                self.consume([TokenType.IDENTIFIER], "Expected parameter name")
                parameter = self.previous()
                parameters.append(parameter)
                # If there are no more commas, break
                if not self.match([TokenType.COMMA]):
                    break
        self.consume([TokenType.RIGHT_PAREN], message='Expected ")" after parameters')
        self.consume(
            [TokenType.LEFT_BRACE],
            message='Expected "{" block after function declaration',
        )
        body = self.block_statement().statements
        return stmt.Function(name=name, params=parameters, body=body)

    def primary(self) -> expr.Expr:
        if self.match([TokenType.IDENTIFIER]):
            return expr.Variable(name=self.previous())

        if self.match([TokenType.FALSE]):
            return expr.Literal(value=False)

        if self.match([TokenType.TRUE]):
            return expr.Literal(value=True)

        if self.match([TokenType.NIL]):
            return expr.Literal(value=None)

        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return expr.Literal(value=self.previous().literal)

        if self.match([TokenType.LEFT_PAREN]):
            exp = self.expression()
            # If right parenthesis is not found, it's an error
            self.consume(
                [TokenType.RIGHT_PAREN], "Could not find closing ')' after expression"
            )
            return expr.Grouping(exp)

        # Add error productions here to handle missing left hand operands

        if self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            err_token = self.previous()
            self.equality()
            raise ParserException("Left hand operand missing", token=err_token)

        if self.match(
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ]
        ):
            err_token = self.previous()
            self.comparison()
            raise ParserException("Left hand operand missing", token=err_token)

        if self.match([TokenType.PLUS]):
            err_token = self.previous()
            self.term()
            raise ParserException("Left hand operand missing", token=err_token)

        if self.match([TokenType.STAR, TokenType.SLASH]):
            err_token = self.previous()
            self.factor()
            raise ParserException("Left hand operand missing", token=err_token)

        raise ParserException("Expected expression", token=self.previous())

    def synchronize(self) -> None:
        """
        This method is called when a ParserException is thrown, and the parser state needs to be synchronized.
        This function moves the parser to the next statement
        """
        self.advance()
        while not self.is_at_end():
            # We check previous because the current token (not yet consumed) is part of another statement
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            if self.peek().token_type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self.advance()

    def print_statement(self) -> stmt.Print:
        expression = self.expression()
        statement = stmt.Print(expression)
        self.consume([TokenType.SEMICOLON], 'Expected ";" at end of print statement')
        return statement

    def println_statement(self) -> stmt.Println:
        expression = self.expression()
        statement = stmt.Println(expression)
        self.consume([TokenType.SEMICOLON], 'Expected ";" at end of println statement')
        return statement

    def expression_statement(self) -> stmt.Expression:
        expression = self.expression()
        statement = stmt.Expression(expression)
        self.consume([TokenType.SEMICOLON], 'Expected ";" at end of statement')
        return statement

    def if_statement(self) -> stmt.If:
        # "if" has been matched, match an expression and a block
        try:
            expression = self.expression()
        except ParserException as e:
            if str(e) == "Expected expression":
                raise ParserException(
                    "Expected valid expression after if", token=self.previous()
                )
            else:
                raise e

        self.consume([TokenType.LEFT_BRACE], 'Expected "{" block after "if"')

        if_branch = self.block_statement()

        if self.match([TokenType.ELSE]):
            self.consume([TokenType.LEFT_BRACE], 'Expected "{" block after "else"')
            else_branch = self.block_statement()
            return stmt.If(
                condition=expression, if_branch=if_branch, else_branch=else_branch
            )

        return stmt.If(condition=expression, if_branch=if_branch)

    def while_statement(self) -> stmt.Stmt:
        try:
            expression = self.expression()
        except ParserException as e:
            if str(e) == "Expected expression":
                raise ParserException(
                    "Expected valid expression after while", token=self.previous()
                )
            else:
                raise e

        self.consume([TokenType.LEFT_BRACE], 'Expected "{" block after "while"')

        try:
            self.loop_depth += 1
            body = self.block_statement()
            return stmt.While(condition=expression, body=body)
        finally:
            self.loop_depth -= 1

    def for_statement(self) -> stmt.For:

        # For loop is of the form for initializer ; condition; update {}

        # Parse the initializer, here we only restrict to
        # variable_declaration and expression_statement, since other types of statements are not allowed
        initializer: stmt.Stmt | None = None
        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        expression: expr.Expr | None = None
        if self.match([TokenType.SEMICOLON]):
            expression = None
        else:
            expression = self.expression()
            self.consume(
                [TokenType.SEMICOLON],
                'Expected ";" after for loop condition expression',
            )

        update: expr.Expr | None = None
        if self.check(TokenType.LEFT_BRACE):
            # There is no update expression
            update = None
        else:
            update = self.expression()

        self.consume([TokenType.LEFT_BRACE], 'Expected "{" block after "for"')
        try:
            self.loop_depth += 1
            body: stmt.Block = self.block_statement()
        finally:
            self.loop_depth -= 1

        return stmt.For(
            initializer=initializer, body=body, condition=expression, update=update
        )

    def break_statement(self) -> stmt.Break:
        if self.loop_depth > 0:
            self.consume(
                [TokenType.SEMICOLON],
                'Expected ";" after break statement',
            )
            return stmt.Break()

        raise ParserException('"break" outside loop', token=self.previous())

    def continue_statement(self) -> stmt.Continue:
        if self.loop_depth > 0:
            self.consume(
                [TokenType.SEMICOLON],
                'Expected ";" after continue statement',
            )
            return stmt.Continue()

        raise ParserException('"continue" outside loop', token=self.previous())

    def assert_statement(self) -> stmt.Assert:
        exp = self.logical_or()
        message_expression = None

        if self.match([TokenType.COMMA]):
            message_expression = self.expression()

        self.consume(
            [TokenType.SEMICOLON],
            'Expected ";" after statement',
        )
        return stmt.Assert(exp, message_expression=message_expression)

    def statement(self) -> stmt.Stmt:
        if self.match([TokenType.FUN]):
            return self.function("function")
        if self.match([TokenType.PRINT]):
            return self.print_statement()
        if self.match([TokenType.PRINTLN]):
            return self.println_statement()
        if self.match([TokenType.LEFT_BRACE]):
            return self.block_statement()
        if self.match([TokenType.IF]):
            return self.if_statement()
        if self.match([TokenType.WHILE]):
            return self.while_statement()
        if self.match([TokenType.FOR]):
            return self.for_statement()
        if self.match([TokenType.BREAK]):
            return self.break_statement()
        if self.match([TokenType.CONTINUE]):
            return self.continue_statement()
        if self.match([TokenType.ASSERT]):
            return self.assert_statement()
        return self.expression_statement()

    def block_statement(self) -> stmt.Block:
        statements: List[stmt.Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume([TokenType.RIGHT_BRACE], 'Expected "}" after block')
        return stmt.Block(statements=statements)

    def variable_declaration(self) -> stmt.Var:
        if self.peek().token_type != TokenType.IDENTIFIER:
            token = self.peek()
            if token.token_type == TokenType.EOF:
                token = self.previous()
            raise ParserException("Expected variable name after var", token=token)

        name = self.advance()

        initializer = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()

        self.consume(
            [TokenType.SEMICOLON], message='Expected ";" after variable declaration'
        )
        return stmt.Var(name, initializer=initializer)

    def const_declaration(self) -> stmt.Const:
        if self.peek().token_type != TokenType.IDENTIFIER:
            token = self.peek()
            if token.token_type == TokenType.EOF:
                token = self.previous()
            raise ParserException("Expected variable name after const", token=token)

        name = self.advance()

        self.consume(
            [TokenType.EQUAL], message="Expected initializer after const declaration"
        )

        initializer = self.expression()

        self.consume(
            [TokenType.SEMICOLON], message='Expected ";" after const declaration'
        )
        return stmt.Const(name, initializer=initializer)

    def declaration(self) -> stmt.Stmt:
        if self.match([TokenType.VAR]):
            return self.variable_declaration()
        if self.match([TokenType.CONST]):
            return self.const_declaration()
        return self.statement()

    def parse(self, repl: bool = False) -> List[stmt.Stmt] | None:
        statements: List[stmt.Stmt] = []
        # TODO: Fix double error message in REPL

        while not self.is_at_end():
            prev_current = self.current
            try:
                statements.append(self.declaration())
            except ParserException as e:
                if not repl:
                    if self.error_reporter is None:
                        raise e
                    self.error_reporter.report("error", f"{str(e)}", token=e.token)
                    self.synchronize()

                # If we are running in REPL, also try to parse an expression
                # Then make it into a println statement (desugaring)
                self.current = prev_current
                # Try parsing an expression
                try:
                    exp = self.expression()
                    statement = stmt.Println(expression=exp)
                    statements.append(statement)
                except ParserException as e:
                    if self.error_reporter is None:
                        raise e
                    self.error_reporter.report("error", f"{str(e)}", token=e.token)
                    self.synchronize()

        if self.error_reporter and self.error_reporter.is_error:
            return None

        return statements
