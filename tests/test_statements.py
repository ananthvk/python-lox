import pytest

from python_lox.exceptions import NameException, RuntimeException

from .conftest import interpret


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

                     println x;
                     println y;
                     
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
                  println z;
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
                    println x * y;
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
                    println "This is true.";
                }
            """
        )
        == "This is true.\n"
    )

    assert (
        interpret(
            """
                if (false) {
                    println "This will not println.";
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
                    println "x is greater than 5.";
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
                    println "x is greater than 5.";
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
                    println "This is true.";
                } else {
                    println "This is false.";
                }
            """
        )
        == "This is true.\n"
    )

    assert (
        interpret(
            """
                if (false) {
                    println "This will not println.";
                } else {
                    println "This will println.";
                }
            """
        )
        == "This will println.\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                if (x > 5) {
                    println "x is greater than 5.";
                } else {
                    println "x is not greater than 5.";
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
                    println "x is greater than 5.";
                } else {
                    println "x is not greater than 5.";
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
                    println x;
                }
                println x;
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
                    println y;
                }
                println x;
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
                println y;
            """
        )


def test_logical_operators():
    assert (
        interpret(
            """
                if (true or false) {
                    println "Logical OR works.";
                }
            """
        )
        == "Logical OR works.\n"
    )

    assert (
        interpret(
            """
                if (true and false) {
                    println "This will not println.";
                } else {
                    println "Logical AND works.";
                }
            """
        )
        == "Logical AND works.\n"
    )

    assert (
        interpret(
            """
                if (!false) {
                    println "Logical NOT works.";
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
                println typeof x;
            """
        )
        == "number\n"
    )

    assert (
        interpret(
            """
                var x = "Hello";
                println typeof x;
            """
        )
        == "str\n"
    )

    assert (
        interpret(
            """
                var x = true;
                println typeof x;
            """
        )
        == "bool\n"
    )

    assert (
        interpret(
            """
                var x = nil;
                println typeof x;
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
                println typeof x;
                println typeof y;
                println typeof z;
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
                println "Assertion passed.";
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
                println "Assertion passed.";
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
                println "Logical AND assertion passed.";
            """
        )
        == "Logical AND assertion passed.\n"
    )

    # Assert with logical OR
    assert (
        interpret(
            """
                assert true or false;
                println "Logical OR assertion passed.";
            """
        )
        == "Logical OR assertion passed.\n"
    )

    # Assert with logical NOT
    assert (
        interpret(
            """
                assert !false;
                println "Logical NOT assertion passed.";
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
                println "Variable comparison assertion passed.";
            """
        )
        == "Variable comparison assertion passed.\n"
    )

    # Assert with arithmetic expression
    assert (
        interpret(
            """
                assert (5 + 5) == 10;
                println "Arithmetic expression assertion passed.";
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
                println "Combined condition assertion passed.";
            """
        )
        == "Combined condition assertion passed.\n"
    )
