from .token import Token, TokenType
from .ast import stmt
from typing import List, cast
from .ast import expr
from .error_reporter import ErrorReporter


class ParserException(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    def __init__(
        self, tokens: List[Token], error_reporter: ErrorReporter | None = None
    ) -> None:
        self.tokens = tokens
        self.error_reporter = error_reporter

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
        if self.match([TokenType.EQUAL]):
            # Since assignment is right associative
            equal = self.previous()
            value = self.assign()

            if isinstance(exp, expr.Variable):
                name = exp.name
                return expr.Assign(name=name, value=value)

            if self.error_reporter is not None:
                self.error_reporter.report(
                    "error", "Syntax Error: Invalid assignment", token=equal
                )
            else:
                raise ParserException("Syntax Error: Invalid assignment", token=equal)

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

        return self.primary()

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

        body = self.block_statement()
        return stmt.While(condition=expression, body=body)

    def for_statement(self) -> stmt.Stmt:

        # For loop is of the form for initializer ; condition; update {}

        # Parse the initializer, here we only restrict to
        # variable_declaration and expression_statement, since other types of statements are not allowed
        initializer = None
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
        body = self.block_statement()

        if update is not None:
            body = stmt.Block(
                statements=[body, cast(stmt.Stmt, stmt.Expression(expression=update))]
            )

        if expression is None:
            expression = expr.Literal(value=True)

        body = stmt.While(condition=expression, body=body)

        if initializer is not None:
            body = stmt.Block(statements=[initializer, body])

        return body

    def statement(self) -> stmt.Stmt:
        """
        Parses a statement
        statement -> print_statement | expression_statement
        print_statement -> "print" expression ";"
        expression_statement -> expression ";"
        """
        if self.match([TokenType.PRINT]):
            return self.print_statement()
        if self.match([TokenType.LEFT_BRACE]):
            return self.block_statement()
        if self.match([TokenType.IF]):
            return self.if_statement()
        if self.match([TokenType.WHILE]):
            return self.while_statement()
        if self.match([TokenType.FOR]):
            return self.for_statement()
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

    def parse(self) -> List[stmt.Stmt] | None:
        statements: List[stmt.Stmt] = []

        while not self.is_at_end():
            try:
                statements.append(self.declaration())
            except ParserException as e:
                if self.error_reporter is None:
                    raise e
                self.error_reporter.report("error", f"{str(e)}", token=e.token)
                self.synchronize()

        if self.error_reporter and self.error_reporter.is_error:
            return None

        return statements
