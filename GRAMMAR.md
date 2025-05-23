program              = declaration* EOF
declaration          = const_declaration 
                      | variable_declaration 
                      | function_declaration
                      | class_declaration
                      | statement
class_declaration    = "class" IDENTIFIER (":" IDENTIFIER)? "{" method* "}" 
method               = function
                      | "static" function
                      | IDENTIFIER block
function_declaration = "fun" function
function             = IDENTIFIER "(" parameters? ")" block
parameters           = IDENTIFIER ( "," IDENTIFIER ) * 
variable_declaration = "var" IDENTIFIER ( "=" expression )? ";"
const_declaration    = "const" IDENTIFIER "=" expression ";"
statement            = expression_statement
                      | print_statement
                      | println_statement
                      | block
                      | if_statement
                      | while_statement
                      | for_statement
                      | break_statement
                      | continue_statement
                      | assert_statement
                      | return_statement
return_statement     = "return" expression? ";"
assert_statement     = "assert" logical_or ("," expression)? ";"
break_statement      = "break" ";"
continue_statement   = "continue" ";"
for_statement        = "for" variable_declaration? ";" 
                             expression? ";"
                             expression? 
                             block
while_statement      = "while" expression block
if_statement         = "if" expression block ("else" block)? 
block                = "{" declaration* "}"
print_statement      = "print" expression ";"
println_statement      = "println" expression ";"
expression_statement = expression ";"
expression           = comma
comma                = assignment ( "," assignment )*
assignment           = (call ".")? IDENTIFIER assignment_operator assignment | ternary
asssignment_operator = "=" | "*=" | "+=" | "-=" | "/=" | "%="
ternary              = logical_or | logical_or "?" expression ":" ternary
logical_or           = logical_and ("or" logical_and)*
logical_and          = equality ("and" equality)*
equality             = comparison ( ("==" | "!=") comparison)*
comparison           = term | ( (">" | ">=" | "<" | "<=") term)*
term                 = factor | ( ("+" | "-") factor)*
factor               = unary | ( ("*" | "/" | "%") unary)*
unary                = (("!" | "-" | "not") unary) | call
call                 = primary ( "(" arguments? ")" | "." IDENTIFIER)*
arguments            = assignment ("," assignment)*
primary              = "false" | "true" | "nil"
                      | NUMBER | STRING | "(" expression ")"
                      | IDENTIFIER
                      | arrow_function
arrow_function   = "(" parameters? ")" "=>" (block | expression)
