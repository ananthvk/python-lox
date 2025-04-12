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

def test_operators_with_multiple_characters_single():
    lexer = Lexer('>=')
    tokens = lexer.process()
    assert len(tokens) == 2
    assert tokens[0].token_type == TokenType.GREATER_EQUAL
    assert tokens[0].literal == None
    assert tokens[0].string_repr == '>='

def test_operators_with_multiple_characters_multiple():
    lexer = Lexer('>=<===!=><!')
    tokens = lexer.process()
    assert len(tokens) == 8

    assert tokens[0].token_type == TokenType.GREATER_EQUAL
    assert tokens[0].literal == None
    assert tokens[0].string_repr == '>='

    assert tokens[1].token_type == TokenType.LESS_EQUAL
    assert tokens[1].literal == None
    assert tokens[1].string_repr == '<='

    assert tokens[2].token_type == TokenType.EQUAL_EQUAL
    assert tokens[2].literal == None
    assert tokens[2].string_repr == '=='

    assert tokens[3].token_type == TokenType.BANG_EQUAL
    assert tokens[3].literal == None
    assert tokens[3].string_repr == '!='

    assert tokens[4].token_type == TokenType.GREATER
    assert tokens[4].literal == None
    assert tokens[4].string_repr == '>'

    assert tokens[5].token_type == TokenType.LESS
    assert tokens[5].literal == None
    assert tokens[5].string_repr == '<'

    assert tokens[6].token_type == TokenType.BANG
    assert tokens[6].literal == None
    assert tokens[6].string_repr == '!'

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
    lexer = Lexer("""({ }) // This is another comment
                    -+ // Here is an inline comment
                    // A line comment
                    
                    /""")
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