from .conftest import interpret


def test_function_no_params():
    assert (
        interpret(
            """
            fun hello(){
                return "Hello, this is a simple program";
            }
            print hello();
            """
        )
        == "Hello, this is a simple program"
    )

    assert (
        interpret(
            """
            fun hello(){
            }
            print hello();
            """
        )
        == "nil"
    )


def test_functions_simple():
    assert (
        interpret(
            """
            fun sum(a, b) {
                return a + b;
            }
            print sum(3, 8);
            """
        )
        == "11"
    )


def test_function_calls_another_function():
    assert (
        interpret(
            """
            fun sum(a, b) {
                return a + b;
            }
            
            fun operation(a, b, c) {
                var x = sum(a, b);
                var y = sum(b, c);
                return x * y;
            }
            print operation(3, 4, 5);
            """
        )
        == "63"
    )


def test_function_shadowing():
    assert (
        interpret(
            """
            fun say_hello(){
                return "hello, there";
            }
            // Define a new block
            {
                fun say_hello(){
                    fun say_hello(name) {
                        return "hello, " + name;
                    }
                    return say_hello("world");
                }
                
                println say_hello();
            }
            println say_hello();
            """
        )
        == "hello, world\nhello, there\n"
    )


def test_closures():
    assert (
        interpret(
            """
            fun makeCounter() {
                var i = 0;
                fun count() {
                    i = i + 1;
                    print i;
                }

                return count;
            }

            const counter1 = makeCounter();
            counter1();
            counter1();
            counter1();
            println "";

            const counter2 = makeCounter();
            counter2();
            counter2();
            counter2();
            counter2();
            println "";
            
            counter1();
            counter2();
            """
        )
        == "123\n1234\n45"
    )
