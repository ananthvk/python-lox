from .conftest import interpret


def verify(expression: str):
    computed = interpret(expression).strip()
    actual = eval(expression.replace("print", "").replace(";", ""))
    if computed == "true" or computed == "false":
        return computed.capitalize() == actual
    if computed == "nil":
        return actual is None
    assert float(computed) == actual or int(computed) == actual


def test_expressions_simple():
    verify("print 5;")
    verify("print 5 * 3;")
    verify("print 5 + 3;")
    verify("print 5 - 3;")
    verify("print 5 / 3;")
    verify("print 5 + 2 * 3;")
    verify("print 5 / 2 * 3 + (6 - 8);")
    verify("print 88/3;")
    verify("print 3 * 2 * 5;")
    verify("print 3 * 2 / 5;")
    verify("print 3 * 2 + 5;")
    verify("print 3 * 2 - 5;")
    verify("print 3 * 2 * 5;")
    verify("print 3 + 2 * 5;")
    verify("print 3 - 2 * 5;")
    verify("print 3 / 2 * 5;")
    verify("print 3 - 2 + 5;")
    verify("print 3 / 2 + 5;")


def test_expression_comparison():
    verify("print 3 > 5;")
    verify("print 3 < 5;")
    verify("print 3 >= 5;")
    verify("print 3 == 5;")
    verify("print 3 != 5;")
    verify("print not (3 == 5);")
    # Note: not has higher precedence than relational operators, and is hence evaluated first
    # In python, not has lower precedence than relational operators, and hence evaluates to a different result
    # So, use parenthesis to group the expression
    verify("print not (3 == 5);")
    verify("print not (3 != 5);")
    verify("print not (3 > 5);")
    verify("print not (3 < 5);")
    verify("print not (3 <= 5);")
    verify("print not (3 >= 5);")


def test_expressions_complex():
    verify(
        "print ((((5*-12-10*(6*10+-11*-14))*3-16*13)*-8--16*-13)*7--2*18)*-12-9*-20;"
    )
    verify("print 8*0-13*((((-7*(-15*13+-14*16)-13*-4)*8-10*-7)*8-11*-20)*9--20*-4);")
    verify("print (-2*((-8*-18-(15*-8+-2*-20)*-2)*17+4*7)-19*-20)*4+1*7;")
    verify(
        "print ((18*((-20*((-13*18-20*3)*-8-8*-8)-2*-19)*16+-9*-20)+-13*20)*-3+-6*-2)*-9--17*1;"
    )
    verify("print -12*((6*((8*(6*-18--2*-19)--6*11)*13--7*20)-9*17)*12+-18*-9)+-12*-5;")
    verify("print ((-6*-16+(-6*17+(-17*-7-15*1)*-10)*3)*3+10*16)*12+-10*3;")
    verify("print 7*18-11*((1*-15+15*10)*((7*-4+-19*7)*1--6*0)+5*-10);")


def test_numbers_in_other_bases():
    verify("print 0b1 + 0b101 + 0b1100 + 0b11110000 + 0b1010101 + 0B111111111111;")
    verify("print 0o1 + 0o2 + 0o3 + 0o4 + 0o5 + 0O6 + 0o7 + 0o7351;")
    verify("print 0xab + 0xAB + 0xCD + 0xEF + 0x123 + 0X456 + 0x7890 + 32;")
    verify("print 0b11111100101010101 + 0xabcdef + 0o12345;")
    verify("print 0xabc;")
    verify("print 0xa;")
    verify("print 0o3;")
    verify("print 0o357;")
    verify("print 0b0;")
    verify("print 0b1;")
    verify("print 0b11101;")
    verify("print (5 + 3) * 2;")
    verify("print 7 - (3 + 2);")
    verify("print 10 / (2 + 3);")
    verify("print (8 - 3) * (2 + 4);")
    verify("print (10 - 3) / (2 + 1);")
    verify("print (5 + 2) * (3 - 1) / 2;")


def test_variables():
    assert (
        interpret(
            """
                var z = 30;
                var y = 20;
                var x = 10;
                print x * y + z;
              """
        )
        == "230\n"
    )
