from .conftest import interpret


def test_while_loops():
    assert (
        interpret(
            """
                var x = 0;
                while (x < 5) {
                    print x;
                    x = x + 1;
                }
            """
        )
        == "0\n1\n2\n3\n4\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                while (x > 5) {
                    print x;
                    x = x - 1;
                }
            """
        )
        == "10\n9\n8\n7\n6\n"
    )

    assert (
        interpret(
            """
                var x = 1;
                while (x < 4) {
                    print x * 2;
                    x = x + 1;
                }
            """
        )
        == "2\n4\n6\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                var sum = 0;
                while (x <= 3) {
                    sum = sum + x;
                    x = x + 1;
                }
                print sum;
            """
        )
        == "6\n"
    )

    assert (
        interpret(
            """
                var x = 1;
                var factorial = 1;
                while (x <= 4) {
                    factorial = factorial * x;
                    x = x + 1;
                }
                print factorial;
            """
        )
        == "24\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                while (x < 3) {
                    print "Hello";
                    x = x + 1;
                }
            """
        )
        == "Hello\nHello\nHello\n"
    )

    assert (
        interpret(
            """
                var x = 5;
                while (x > 0) {
                    print x * x;
                    x = x - 1;
                }
            """
        )
        == "25\n16\n9\n4\n1\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                while (x < 2) {
                    var y = 0;
                    while (y < 2) {
                        print x + y;
                        y = y + 1;
                    }
                    x = x + 1;
                }
            """
        )
        == "0\n1\n1\n2\n"
    )

    assert (
        interpret(
            """
                var x = 10;
                while (x % 3 != 0) {
                    x = x - 1;
                }
                print x;
            """
        )
        == "9\n"
    )


def test_for_loop():
    assert (
        interpret(
            """
                var x;
                for x = 10; x % 3 != 0; x = x - 1 {
                }
                print x;
            """
        )
        == "9\n"
    )

    assert (
        interpret(
            """
                var sum = 0;
                for var x = 0; x <= 5; x = x + 1 {
                    sum = sum + x;
                }
                print sum;
            """
        )
        == "15\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 3; x = x + 1 {
                    print "Hello";
                }
            """
        )
        == "Hello\nHello\nHello\n"
    )

    assert (
        interpret(
            """
                for var x = 5; x > 0; x = x - 1 {
                    print x * x;
                }
            """
        )
        == "25\n16\n9\n4\n1\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 2; x = x + 1 {
                    for var y = 0; y < 2; y = y + 1 {
                        print x + y;
                    }
                }
            """
        )
        == "0\n1\n1\n2\n"
    )

    assert (
        interpret(
            """
                var factorial = 1;
                for var x = 1; x <= 4; x = x + 1 {
                    factorial = factorial * x;
                }
                print factorial;
            """
        )
        == "24\n"
    )

    assert (
        interpret(
            """
                var product = 1;
                for var x = 1; x <= 3; x = x + 1 {
                    product = product * x;
                }
                print product;
            """
        )
        == "6\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 5; x = x + 1 {
                    if (x % 2 == 0) {
                        print x;
                    }
                }
            """
        )
        == "0\n2\n4\n"
    )

    assert (
        interpret(
            """
                var sum = 0;
                for var x = 1; x <= 5; x = x + 1 {
                    if (x % 2 != 0) {
                        sum = sum + x;
                    }
                }
                print sum;
            """
        )
        == "9\n"
    )

    assert (
        interpret(
            """
                for var x = 10; x > 0; x = x - 2 {
                    print x;
                }
            """
        )
        == "10\n8\n6\n4\n2\n"
    )

    assert (
        interpret(
            """
                var count = 0;
                for var x = 0; x < 10; x = x + 1 {
                    if (x % 3 == 0) {
                        count = count + 1;
                    }
                }
                print count;
            """
        )
        == "4\n"
    )


def test_continue_and_break():
    assert (
        interpret(
            """
                for var x = 0; x < 5; x = x + 1 {
                    if (x == 2) {
                        continue;
                    }
                    print x;
                }
            """
        )
        == "0\n1\n3\n4\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 5; x = x + 1 {
                    if (x == 3) {
                        break;
                    }
                    print x;
                }
            """
        )
        == "0\n1\n2\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                while (x < 5) {
                    x = x + 1;
                    if (x % 2 == 0) {
                        continue;
                    }
                    print x;
                }
            """
        )
        == "1\n3\n5\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                while (x < 5) {
                    if (x == 3) {
                        break;
                    }
                    print x;
                    x = x + 1;
                }
            """
        )
        == "0\n1\n2\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 10; x = x + 1 {
                    if (x % 3 == 0) {
                        continue;
                    }
                    print x;
                }
            """
        )
        == "1\n2\n4\n5\n7\n8\n"
    )

    assert (
        interpret(
            """
                var sum = 0;
                for var x = 1; x <= 10; x = x + 1 {
                    if (x > 5) {
                        break;
                    }
                    sum = sum + x;
                }
                print sum;
            """
        )
        == "15\n"
    )

    assert (
        interpret(
            """
                var count = 0;
                for var x = 0; x < 10; x = x + 1 {
                    if (x % 2 == 0) {
                        continue;
                    }
                    count = count + 1;
                }
                print count;
            """
        )
        == "5\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                while (x < 10) {
                    if (x == 7) {
                        break;
                    }
                    if (x % 2 == 0) {
                        x = x + 1;
                        continue;
                    }
                    print x;
                    x = x + 1;
                }
            """
        )
        == "1\n3\n5\n"
    )

    assert (
        interpret(
            """
                for var x = 0; x < 10; x = x + 1 {
                    if (x % 2 != 0) {
                        continue;
                    }
                    if (x == 6) {
                        break;
                    }
                    print x;
                }
            """
        )
        == "0\n2\n4\n"
    )

    assert (
        interpret(
            """
                var x = 0;
                var sum = 0;
                while (x < 10) {
                    x = x + 1;
                    if (x % 3 == 0) {
                        continue;
                    }
                    if (x > 7) {
                        break;
                    }
                    sum = sum + x;
                }
                print sum;
            """
        )
        == "19\n"
    )
