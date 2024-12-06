#!/usr/local/bin/python3
import unicodedata

print(open(__file__).read())

inp = unicodedata.normalize("NFKC", input(">>> "))
blacklist = "0123456789cdfghjlmqsuvwxyz!\"#$%&'*+,-./:;<=>?@[\]^_`{|}~"
if not sum(bad in inp.lower() for bad in blacklist):
    print(eval(inp))
else:
    print("bad boyQQ")
