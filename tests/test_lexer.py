from python_lox.lexer import Lexer
from python_lox.token import TokenType

def test_lexer_empty_source():
    lexer = Lexer('')
    tokens = lexer.process()
    assert len(tokens) == 1
    assert tokens[0].token_type == TokenType.EOF

def test_single_letter_token():
    lexer = Lexer('{')
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].string_repr == "{"
    assert tokens[0].token_type == TokenType.LEFT_BRACE
    assert tokens[1].token_type == TokenType.EOF

def test_multiple_single_letter_tokens():
    lexer = Lexer('{}(),.-+;*')
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
