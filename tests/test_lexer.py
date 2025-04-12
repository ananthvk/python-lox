from python_lox.lexer import Lexer
from python_lox.token import TokenType


def test_lexer_empty_source():
    lexer = Lexer("")
    tokens = lexer.process()
    assert len(tokens) == 1
    assert tokens[0].token_type == TokenType.EOF


def test_single_letter_token():
    lexer = Lexer("{")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].string_repr == "{"
    assert tokens[0].token_type == TokenType.LEFT_BRACE
    assert tokens[1].token_type == TokenType.EOF


def test_multiple_single_letter_tokens():
    lexer = Lexer("{}(),.-+;*")
    tokens = lexer.process()
    assert len(tokens) == 11
    assert tokens[0].token_type == TokenType.LEFT_BRACE
    assert tokens[1].token_type == TokenType.RIGHT_BRACE
    assert tokens[2].token_type == TokenType.LEFT_PAREN
    assert tokens[3].token_type == TokenType.RIGHT_PAREN
    assert tokens[4].token_type == TokenType.COMMA
    assert tokens[5].token_type == TokenType.DOT
    assert tokens[6].token_type == TokenType.MINUS
    assert tokens[7].token_type == TokenType.PLUS
    assert tokens[8].token_type == TokenType.SEMICOLON
    assert tokens[9].token_type == TokenType.STAR
    assert tokens[10].token_type == TokenType.EOF


def test_operators_with_multiple_characters_single():
    lexer = Lexer(">=")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.GREATER_EQUAL
    assert tokens[0].literal == None
    assert tokens[0].string_repr == ">="


def test_operators_with_multiple_characters_multiple():
    lexer = Lexer(">=<===!=><!")
    tokens = lexer.process()
    assert len(tokens) == 8

    assert tokens[0].token_type == TokenType.GREATER_EQUAL
    assert tokens[0].literal == None
    assert tokens[0].string_repr == ">="

    assert tokens[1].token_type == TokenType.LESS_EQUAL
    assert tokens[1].literal == None
    assert tokens[1].string_repr == "<="

    assert tokens[2].token_type == TokenType.EQUAL_EQUAL
    assert tokens[2].literal == None
    assert tokens[2].string_repr == "=="

    assert tokens[3].token_type == TokenType.BANG_EQUAL
    assert tokens[3].literal == None
    assert tokens[3].string_repr == "!="

    assert tokens[4].token_type == TokenType.GREATER
    assert tokens[4].literal == None
    assert tokens[4].string_repr == ">"

    assert tokens[5].token_type == TokenType.LESS
    assert tokens[5].literal == None
    assert tokens[5].string_repr == "<"

    assert tokens[6].token_type == TokenType.BANG
    assert tokens[6].literal == None
    assert tokens[6].string_repr == "!"

    assert tokens[7].token_type == TokenType.EOF


def test_single_line_comments_division():
    lexer = Lexer("/")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.SLASH

    lexer = Lexer("// This line should be ignored since this is a comment\n\n/")
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.SLASH
    assert tokens[1].token_type == TokenType.EOF


def test_newline_whitespace():
    lexer = Lexer("*     \n\n\t\r + -")
    tokens = lexer.process()
    assert len(tokens) == 4
    assert tokens[0].token_type == TokenType.STAR
    assert tokens[1].token_type == TokenType.PLUS
    assert tokens[2].token_type == TokenType.MINUS
    assert tokens[3].token_type == TokenType.EOF


def test_small_example():
    lexer = Lexer(
        """({ }) // This is another comment
                    -+ // Here is an inline comment
                    // A line comment
                    
                    /"""
    )
    tokens = lexer.process()
    assert len(tokens) == 8
    assert tokens[0].token_type == TokenType.LEFT_PAREN
    assert tokens[0].line == 1
    assert tokens[1].token_type == TokenType.LEFT_BRACE
    assert tokens[1].line == 1
    assert tokens[2].token_type == TokenType.RIGHT_BRACE
    assert tokens[2].line == 1
    assert tokens[3].token_type == TokenType.RIGHT_PAREN
    assert tokens[3].line == 1
    assert tokens[4].token_type == TokenType.MINUS
    assert tokens[4].line == 2
    assert tokens[5].token_type == TokenType.PLUS
    assert tokens[5].line == 2
    assert tokens[6].token_type == TokenType.SLASH
    assert tokens[6].line == 5
    assert tokens[7].token_type == TokenType.EOF


def test_string_literals():
    # Empty string
    lexer = Lexer('""')
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.STRING
    assert tokens[0].literal == ""
    assert tokens[0].string_repr == '""'
    assert tokens[1].token_type == TokenType.EOF

    # String with one character
    lexer = Lexer('"h"')
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.STRING
    assert tokens[0].literal == "h"
    assert tokens[0].string_repr == '"h"'
    assert tokens[1].token_type == TokenType.EOF

    # String with multiple characters
    lexer = Lexer(
        '// Hello world comment \n"hello world, this is lox programming language\n\n//This comment is inside the string...." // This comment is outside'
    )
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.STRING
    assert (
        tokens[0].literal
        == "hello world, this is lox programming language\n\n//This comment is inside the string...."
    )
    assert (
        tokens[0].string_repr
        == '"hello world, this is lox programming language\n\n//This comment is inside the string...."'
    )
    assert tokens[1].token_type == TokenType.EOF

    # Multiple strings
    lexer = Lexer('"h""ello""world"')
    tokens = lexer.process()
    assert len(tokens) == 4
    assert tokens[0].token_type == TokenType.STRING
    assert tokens[0].literal == "h"
    assert tokens[0].string_repr == '"h"'
    assert tokens[1].token_type == TokenType.STRING
    assert tokens[1].literal == "ello"
    assert tokens[1].string_repr == '"ello"'
    assert tokens[2].token_type == TokenType.STRING
    assert tokens[2].literal == "world"
    assert tokens[2].string_repr == '"world"'
    assert tokens[3].token_type == TokenType.EOF


def test_numbers():
    lexer = Lexer("3125")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert isinstance(tokens[0].literal, float) or isinstance(tokens[0].literal, int)
    assert abs(tokens[0].literal - 3125) < 10e-5

    lexer = Lexer("0")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert isinstance(tokens[0].literal, float) or isinstance(tokens[0].literal, int)
    assert abs(tokens[0].literal - 0) < 10e-5

    lexer = Lexer("3.1415")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert isinstance(tokens[0].literal, float) or isinstance(tokens[0].literal, int)
    assert abs(tokens[0].literal - 3.1415) < 10e-5

    lexer = Lexer("122213.1415")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert isinstance(tokens[0].literal, float) or isinstance(tokens[0].literal, int)
    assert abs(tokens[0].literal - 122213.1415) < 10e-5

    lexer = Lexer("3.8815 + 561112 / 2 - 3.06")
    tokens = lexer.process()
    tokens = [i for i in tokens if i.token_type == TokenType.NUMBER]
    assert len(tokens) == 4
    assert isinstance(tokens[0].literal, float) or isinstance(tokens[0].literal, int)
    assert abs(tokens[0].literal - 3.8815) < 10e-5

    assert isinstance(tokens[1].literal, float) or isinstance(tokens[1].literal, int)
    assert abs(tokens[1].literal - 561112) < 10e-5

    assert isinstance(tokens[2].literal, float) or isinstance(tokens[2].literal, int)
    assert abs(tokens[2].literal - 2) < 10e-5

    assert isinstance(tokens[3].literal, float) or isinstance(tokens[3].literal, int)
    assert abs(tokens[3].literal - 3.06) < 10e-5

def test_identifiers():
    lexer = Lexer("abc")
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.IDENTIFIER
    assert tokens[0].literal == "abc"

def test_keywords():
    lexer = Lexer("and or not false true nil if else class fun for while print return super this var")
    tokens = lexer.process()
    tokens = [i for i in tokens if i.token_type != TokenType.IDENTIFIER]
    assert len(tokens) == 18
    assert tokens[0].token_type == TokenType.AND
    assert tokens[1].token_type == TokenType.OR
    assert tokens[2].token_type == TokenType.NOT
    assert tokens[3].token_type == TokenType.FALSE
    assert tokens[4].token_type == TokenType.TRUE
    assert tokens[5].token_type == TokenType.NIL
    assert tokens[6].token_type == TokenType.IF
    assert tokens[7].token_type == TokenType.ELSE
    assert tokens[8].token_type == TokenType.CLASS
    assert tokens[9].token_type == TokenType.FUN
    assert tokens[10].token_type == TokenType.FOR
    assert tokens[11].token_type == TokenType.WHILE
    assert tokens[12].token_type == TokenType.PRINT
    assert tokens[13].token_type == TokenType.RETURN
    assert tokens[14].token_type == TokenType.SUPER
    assert tokens[15].token_type == TokenType.THIS
    assert tokens[16].token_type == TokenType.VAR
    assert tokens[17].token_type == TokenType.EOF
