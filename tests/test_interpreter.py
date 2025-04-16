from python_lox.interpreter import Interpreter
from python_lox.lexer import Lexer
from python_lox.parser import Parser


def interpret(expression: str):
    lexer = Lexer(expression)
    parser = Parser(lexer.process())
    expr = parser.parse()
    if expr is None:
        raise RuntimeError()
    interpreter = Interpreter()
    return interpreter.interpret(expr)


def verify(expression: str):
    computed = interpret(expression)
    actual = eval(expression)
    if computed == "true" or computed == "false":
        return computed.capitalize() == actual
    if computed == "nil":
        return actual is None
    assert float(computed) == actual or int(computed) == actual


def test_expressions_simple():
    verify("5")
    verify("5 * 3")
    verify("5 + 3")
    verify("5 - 3")
    verify("5 / 3")
    verify("5 + 2 * 3")
    verify("5 / 2 * 3 + (6 - 8)")
    verify("88/3")
    verify("3 * 2 * 5")
    verify("3 * 2 / 5")
    verify("3 * 2 + 5")
    verify("3 * 2 - 5")
    verify("3 * 2 * 5")
    verify("3 + 2 * 5")
    verify("3 - 2 * 5")
    verify("3 / 2 * 5")
    verify("3 - 2 + 5")
    verify("3 / 2 + 5")


def test_expression_comparison():
    verify("3 > 5")
    verify("3 < 5")
    verify("3 >= 5")
    verify("3 == 5")
    verify("3 != 5")
    verify("not (3 == 5)")
    # Note: not has higher precedence than relational operators, and is hence evaluated first
    # In python, not has lower precedence than relational operators, and hence evaluates to a different result
    # So, use parenthesis to group the expression
    verify("not (3 == 5)")
    verify("not (3 != 5)")
    verify("not (3 > 5)")
    verify("not (3 < 5)")
    verify("not (3 <= 5)")
    verify("not (3 >= 5)")



def test_expressions_complex():
    verify("((((5*-12-10*(6*10+-11*-14))*3-16*13)*-8--16*-13)*7--2*18)*-12-9*-20")
    verify("8*0-13*((((-7*(-15*13+-14*16)-13*-4)*8-10*-7)*8-11*-20)*9--20*-4)")
    verify("(-2*((-8*-18-(15*-8+-2*-20)*-2)*17+4*7)-19*-20)*4+1*7")
    verify(
        "((18*((-20*((-13*18-20*3)*-8-8*-8)-2*-19)*16+-9*-20)+-13*20)*-3+-6*-2)*-9--17*1"
    )
    verify("-12*((6*((8*(6*-18--2*-19)--6*11)*13--7*20)-9*17)*12+-18*-9)+-12*-5")
    verify("((-6*-16+(-6*17+(-17*-7-15*1)*-10)*3)*3+10*16)*12+-10*3")
    verify("7*18-11*((1*-15+15*10)*((7*-4+-19*7)*1--6*0)+5*-10)")


def test_numbers_in_other_bases():
    verify("0b1 + 0b101 + 0b1100 + 0b11110000 + 0b1010101 + 0B111111111111")
    verify("0o1 + 0o2 + 0o3 + 0o4 + 0o5 + 0O6 + 0o7 + 0o7351")
    verify("0xab + 0xAB + 0xCD + 0xEF + 0x123 + 0X456 + 0x7890 + 32")
    verify("0b11111100101010101 + 0xabcdef + 0o12345")
    verify("0xabc")
    verify("0xa")
    verify("0o3")
    verify("0o357")
    verify("0b0")
    verify("0b1")
    verify("0b11101")