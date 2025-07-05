#!/usr/local/bin/python3
import unicodedata

print(open(__file__).read())

expr = unicodedata.normalize("NFKC", input("> "))

if "._" in expr:
    raise NameError("no __ %r" % expr)

if "breakpoint" in expr:
    raise NameError("no breakpoint %r" % expr)

if any([x in "([ ])" for x in expr]):
    raise NameError("no ([ ]) %r" % expr)

# baby version: response for free OUO
result = eval(expr)
print(result)
