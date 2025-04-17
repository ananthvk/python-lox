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


## Additional features

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