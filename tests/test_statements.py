from .conftest import interpret
from python_lox.exceptions import NameException
from python_lox.exceptions import RuntimeException
import pytest


def test_variables():
    assert (
        interpret(
            """
                     var x = 5;
                     var y = 30;
                     var t;
                     
                     // Swap the variables
                     t = x;
                     x = y;
                     y = t;
                     
                     x = x * x + 100;
                     y = y * y + 100;

                     print x;
                     print y;
                     
                     """
        )
        == "1000\n125\n"
    )

    with pytest.raises(NameException):
        interpret(
            """
                  var x = 30;
                  var z = x + y;
            """
        )

    with pytest.raises(NameException):
        interpret(
            """
                  var y;
                  var x = 30;
                  var z = x + y;
            """
        )

    assert (
        interpret(
            """
                  var y;
                  var x = 30;
                  y = 50;
                  var z = x + y;
                  print z;
            """
        )
        == "80\n"
    )


def test_const():
    assert (
        interpret(
            """
                    const x = 30;
                    const y = 100;
                    print x * y;
        """
        )
        == "3000\n"
    )

    with pytest.raises(NameException):
        assert interpret(
            """
                        const x = 50;
                        const y = 80;
                        x = 8000;
                         """
        )


def test_if_statement():
    assert (
        interpret(
            """
                if (true) {
                    print "This is true.";
                }
            """
        )
        == "This is true.\n"
    )

    assert (
        interpret(
            """
                if (false) {
                    print "This will not print.";
                }
            """
        )
        == ""
    )

    assert (
        interpret(
            """
                var x = 10;
                if (x > 5) {
                    print "x is greater than 5.";
                }
            """
        )
        == "x is greater than 5.\n"
    )

    assert (
        interpret(
            """
                var x = 3;
                if (x > 5) {
                    print "x is greater than 5.";
                }
            """
        )
        == ""
    )
    pass


def test_if_else_statement():
    assert (
        interpret(
            """
                if (true) {
                    print "This is true.";
                } else {
                    print "This is false.";
                }
            """
        )
        == "This is true.\n"
    )

    assert (
        interpret(
            """
                if (false) {
                    print "This will not print.";
                } else {
                    print "This will print.";
                }
            """
        )
        == "This will print.\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                if (x > 5) {
                    print "x is greater than 5.";
                } else {
                    print "x is not greater than 5.";
                }
            """
        )
        == "x is greater than 5.\n"
    )

    assert (
        interpret(
            """
                var x = 3;
                if (x > 5) {
                    print "x is greater than 5.";
                } else {
                    print "x is not greater than 5.";
                }
            """
        )
        == "x is not greater than 5.\n"
    )


def test_scopes():
    assert (
        interpret(
            """
                var x = 10;
                {
                    var x = 20;
                    print x;
                }
                print x;
            """
        )
        == "20\n10\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                {
                    var y = 20;
                    print y;
                }
                print x;
            """
        )
        == "20\n10\n"
    )

    with pytest.raises(NameException):
        interpret(
            """
                {
                    var y = 20;
                }
                print y;
            """
        )


def test_logical_operators():
    assert (
        interpret(
            """
                if (true or false) {
                    print "Logical OR works.";
                }
            """
        )
        == "Logical OR works.\n"
    )

    assert (
        interpret(
            """
                if (true and false) {
                    print "This will not print.";
                } else {
                    print "Logical AND works.";
                }
            """
        )
        == "Logical AND works.\n"
    )

    assert (
        interpret(
            """
                if (!false) {
                    print "Logical NOT works.";
                }
            """
        )
        == "Logical NOT works.\n"
    )


def test_typeof():
    assert (
        interpret(
            """
                var x = 10;
                print typeof x;
            """
        )
        == "number\n"
    )

    assert (
        interpret(
            """
                var x = "Hello";
                print typeof x;
            """
        )
        == "str\n"
    )

    assert (
        interpret(
            """
                var x = true;
                print typeof x;
            """
        )
        == "bool\n"
    )

    assert (
        interpret(
            """
                var x = nil;
                print typeof x;
            """
        )
        == "nil\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                var y = "Hello";
                var z = true;
                print typeof x;
                print typeof y;
                print typeof z;
            """
        )
        == "number\nstr\nbool\n"
    )


def test_assert():
    with pytest.raises(RuntimeException):
        interpret(
            """
                assert 3 == 2;
            """
        )

    with pytest.raises(RuntimeException):
        interpret(
            """
                assert 3 == 2, "3 is not equal to 2";
            """
        )

    # Assert with true condition
    assert (
        interpret(
            """
                assert 5 > 3;
                print "Assertion passed.";
            """
        )
        == "Assertion passed.\n"
    )

    # Assert with false condition
    with pytest.raises(RuntimeException):
        interpret(
            """
                assert 5 < 3;
            """
        )

    # Assert with true condition and custom message
    assert (
        interpret(
            """
                assert 10 == 10, "10 should be equal to 10";
                print "Assertion passed.";
            """
        )
        == "Assertion passed.\n"
    )

    # Assert with false condition and custom message
    with pytest.raises(RuntimeException):
        interpret(
            """
                assert 10 != 10, "10 should not be equal to 10";
            """
        )

    # Assert with logical AND
    assert (
        interpret(
            """
                assert true and true;
                print "Logical AND assertion passed.";
            """
        )
        == "Logical AND assertion passed.\n"
    )

    # Assert with logical OR
    assert (
        interpret(
            """
                assert true or false;
                print "Logical OR assertion passed.";
            """
        )
        == "Logical OR assertion passed.\n"
    )

    # Assert with logical NOT
    assert (
        interpret(
            """
                assert !false;
                print "Logical NOT assertion passed.";
            """
        )
        == "Logical NOT assertion passed.\n"
    )

    # Assert with variable comparison
    assert (
        interpret(
            """
                var x = 20;
                var y = 20;
                assert x == y;
                print "Variable comparison assertion passed.";
            """
        )
        == "Variable comparison assertion passed.\n"
    )

    # Assert with arithmetic expression
    assert (
        interpret(
            """
                assert (5 + 5) == 10;
                print "Arithmetic expression assertion passed.";
            """
        )
        == "Arithmetic expression assertion passed.\n"
    )

    # Assert with combined conditions
    assert (
        interpret(
            """
                var x = 10;
                var y = 20;
                assert (x < y) and (y > x);
                print "Combined condition assertion passed.";
            """
        )
        == "Combined condition assertion passed.\n"
    )
