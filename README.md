# python-lox

My implementation of Lox programming language from [Crafting interpreters](https://www.craftinginterpreters.com/contents.html) in Python.

## How to run

```sh
$ pdm install
$ source .venv/bin/activate
$ pylox
```

To generate ast files,

```sh
$ pdm run gen-ast src/python_lox/ast
```

## Screenshots

Visualization of AST for `5 * 6 / 3 - 2 / 5 * (6 + 8)`
![Visualization of AST](images/ast_visual.png)


## Additional features / modifications

1) Comma operator `,` - Evaluates to it's rightmost expression

For example,
```
var x = 5, 10, 20 * 30;
```
evaluates to 600

2) Ternary operators

For example,
```
print 5 > 3 ? "Greater" : "Lesser";
```

3) Accessing uninitialized variables is an error
```
var x;
print x * 20; // Error
```

4) Cannot redefine variables
```
var x = 20;
var x = 50; // Error (x is already defined)
x = 40;     // Assignment is supported
```

5) const variables
```
const name = "hello world";
name = "hello"; // Error: Assignment not permitted
var name = "hello"; // Error: redeclaration
```

6) typeof operator - Returns string representing the type of the given expression

```
const name = "hello";
const integer = 3;
const is_valid = true;
const value = nil;
print typeof(name); // str
print typeof(integer); // number
print typeof(is_valid); // bool
print typeof(value); // nil
```

7) `if` statement does not require parenthesis to enclose the condition. `if` and `else` statements require braced block after it, like Go and Rust. This also solves the dangling else problem.
```
if x > 3 { 
    // do something here
} else {
    // do something else
}
```

8) Similar to `if` statement, `while` statement does not require parenthesis, and requires a braced block
```
while x > 5 {
    // Statements
}
```

9) `for` loop statement does not require parenthesis
```
for var i = 0; i < 10; i = i + 1 {
    print i;
}
```

