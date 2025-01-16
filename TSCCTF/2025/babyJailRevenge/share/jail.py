#!/usr/local/bin/python3

inp = __import__("unicodedata").normalize("NFKC", input("> "))
if "__" in inp:
    raise NameError("no dunder")

if ',' in inp:
    raise NameError("no ,")

if sum(1 for c in inp if c == '(') > 2:
    raise NameError("no (")

print(eval(inp, {"__builtins__": {}}, None))
