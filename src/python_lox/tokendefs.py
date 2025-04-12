from .token import TokenType

keywords = {
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "true": TokenType.TRUE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "class": TokenType.CLASS,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "var": TokenType.VAR,
}

token_type_map_single_char = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    "-": TokenType.MINUS,
    "+": TokenType.PLUS,
    ";": TokenType.SEMICOLON,
    "*": TokenType.STAR,
    "!": TokenType.BANG,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    "=": TokenType.EQUAL,
}

token_type_map_double_char = {
    "!=": TokenType.BANG_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
}
