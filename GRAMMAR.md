program              = declaration* EOF
declaration          = variable_declaration | statement
variable_declaration = "var" IDENTIFER ( "=" expression )? ";"
statement            = expression_statement
                      | print_statement
                      | block
block                = "{" declaration* "}"
print_statement      = "print" expression ";"
expression_statement = expression ";"
expression           = assignment
assignment           = IDENTIFIER "=" assignment | comma
comma                = ternary ( "," ternary )*
ternary              = equality | equality "?" expression ":" ternary
equality             = comparison ( ("==" | "!=") comparison)*
comparison           = term | ( (">" | ">=" | "<" | "<=") term)*
term                 = factor | ( ("+" | "-") factor)*
factor               = unary | ( ("*" | "/") unary)*
unary                = (("!" | "-" | "not") unary) | primary
primary              = "false" | "true" | "nil"
                      | NUMBER | STRING | "(" expression ")"
                      | IDENTIFIER
