from python_lox.lexer import Lexer
from python_lox.extras import astprint
from python_lox.token import TokenType
from python_lox.parser import Parser


def test_basic_operations():
    lexer = Lexer("3 + 5")
    parser = Parser(lexer.process())

    assert parser.peek().token_type == TokenType.NUMBER
    assert parser.peek().literal == 3
    assert parser.is_at_end() == False

    token = parser.advance()
    assert token.literal == 3
    assert token.token_type == TokenType.NUMBER

    assert parser.peek().token_type == TokenType.PLUS
    assert parser.is_at_end() == False

    assert not parser.match([TokenType.STAR, TokenType.MINUS, TokenType.BANG])
    assert parser.match([TokenType.SLASH, TokenType.MINUS, TokenType.PLUS])
    token = parser.previous()
    assert token.token_type == TokenType.PLUS
    assert parser.previous().token_type == TokenType.PLUS

    assert parser.peek().token_type == TokenType.NUMBER
    assert parser.peek().literal == 5
    assert parser.is_at_end() == False

    token = parser.advance()
    assert token.literal == 5
    assert token.token_type == TokenType.NUMBER

    assert parser.is_at_end()
    assert parser.previous().token_type == TokenType.NUMBER
    assert parser.peek().token_type == TokenType.EOF

    token = parser.advance()
    assert token.token_type == TokenType.EOF

    token = parser.advance()
    assert token.token_type == TokenType.EOF

    assert parser.peek().token_type == TokenType.EOF


"""
Test if parsing worked correctly by checking the output of printing the AST
"""


def test_simple_expressions():
    assert astprint("3") == "3"
    assert astprint("3 == 2") == "(== 3 2)"
    assert astprint("3 != 2") == "(!= 3 2)"
    assert astprint("3 > 2") == "(> 3 2)"
    assert astprint("3 >= 2") == "(>= 3 2)"
    assert astprint("3 < 2") == "(< 3 2)"
    assert astprint("3 <= 2") == "(<= 3 2)"
    assert astprint("3 - 2") == "(- 3 2)"
    assert astprint("3 + 2") == "(+ 3 2)"
    assert astprint("3 / 2") == "(/ 3 2)"
    assert astprint("3 * 2") == "(* 3 2)"
    assert astprint("-3") == "(- 3)"
    assert astprint("!true") == "(! true)"
    assert astprint("false") == "false"
    assert astprint("nil") == "nil"
    assert astprint('"Some string"') == "Some string"


def test_associativity_precedence():
    assert astprint("1 + 2 + 3") == "(+ (+ 1 2) 3)"
    assert astprint("1 + 2 * 3") == "(+ 1 (* 2 3))"
    assert astprint("1 * 2 + 3") == "(+ (* 1 2) 3)"
    assert astprint("-3 * 2") == "(* (- 3) 2)"


def test_grouping():
    assert astprint("(1 + 2) * 3") == "(* (group (+ 1 2)) 3)"
    assert astprint("!(false == true)") == "(! (group (== false true)))"
    assert astprint("((3))") == "(group (group 3))"


def test_multiple_unary():
    assert astprint("!!true") == "(! (! true))"
    assert astprint("---3") == "(- (- (- 3)))"


def test_multiple():
    assert astprint("3 + 2 + 5 + 4 + 6") == "(+ (+ (+ (+ 3 2) 5) 4) 6)"
    assert astprint("3 == 2 == 5 == 4 == 6") == "(== (== (== (== 3 2) 5) 4) 6)"


def test_comparisons():
    assert astprint("3 - 2 > 5 - 4") == "(> (- 3 2) (- 5 4))"


def test_ternary_expression():
    assert astprint("2 > 3 ? 5 : 7") == "(?: (> 2 3) 5 7)"
    assert (
        astprint("true ? false ? 1 : 2 : true ? 3 : 4")
        == "(?: true (?: false 1 2) (?: true 3 4))"
    )

    assert astprint("2 > 3 ? 5 == 2 : 6 - 3") == "(?: (> 2 3) (== 5 2) (- 6 3))"
