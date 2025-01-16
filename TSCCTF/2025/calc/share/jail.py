#!/usr/local/bin/python3

inp = input('> ')

if sum(1 for char in inp if char in set(__import__('string').ascii_letters)):
    raise NameError("just calc no evil(ascii).")

if '[' in inp or ']' in inp:
    raise NameError("just calc no evil([]).")

print(eval(inp, {"__builtins__": {}}, {}))
