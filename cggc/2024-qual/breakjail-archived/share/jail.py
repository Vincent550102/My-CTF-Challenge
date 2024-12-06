#!/usr/local/bin/python3
print(open(__file__).read())

inp = __import__("unicodedata").normalize("NFKC", input(">>> "))

if any([x in "._." for x in inp]):
    print('bad hacker')
elif inp == '?':
    print(open('GoodPdb.py').read(), __import__('sys').version_info)
else:
    exec(inp, {"__builtins__": {}}, {'breakpoint':__import__('GoodPdb').good_breakpoint})
