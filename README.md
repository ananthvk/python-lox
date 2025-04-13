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