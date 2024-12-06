#!/usr/local/bin/python3
import unicodedata

print(open(__file__).read())
fg = open("/flag").read()

inp = unicodedata.normalize("NFKC", input(">>> "))
blacklist = "0123456789abdefgijklmnopqstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'*,-./:;<>?@[\]^_`{|}~"
if not sum(bad in inp.lower() for bad in blacklist):
    print(eval(f"locals()[{inp}]"))
else:
    print("bad boyQQ")
