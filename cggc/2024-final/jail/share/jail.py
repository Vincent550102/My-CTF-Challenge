#!/usr/local/bin/python3

import re

expr = input("Enter code: ")

if len(re.findall(r"\([^)]+\)", expr)) > 1:
    raise NameError("only one (blablabla) %r" % expr)

if "[" in expr or "]" in expr:
    raise NameError("no [] %r" % expr)

code_obj = compile(expr, "<sandbox>", "eval")
for name in code_obj.co_names:
    if "__" in name:
        raise NameError("no dunder %r (%r)" % (name, expr))

print(eval(code_obj, {"__builtins__": {}}, {}))
