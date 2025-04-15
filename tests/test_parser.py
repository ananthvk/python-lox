from python_lox.lexer import Lexer
from python_lox.token import TokenType
from python_lox.parser import Parser

def test_basic_operations():
    lexer = Lexer('3 + 5')
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