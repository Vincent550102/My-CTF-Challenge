#!/usr/local/bin/python3
print(open(__file__).read())

flag = open('flag').read()
flag = "Got eaten by the cookie monster QQ"

inp = __import__("unicodedata").normalize("NFKC", input(">>> "))

if any([x in "._." for x in inp]) or inp.__len__() > 55:
    print('bad hacker')
else:
    eval(inp, {"__builtins__": {}}, {
         'breakpoint': __import__('GoodPdb').good_breakpoint})

print(flag)
