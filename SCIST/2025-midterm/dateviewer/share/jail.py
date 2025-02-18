#!/usr/local/bin/python3

import unicodedata
import datetime

inp = unicodedata.normalize("NFKC", input("ex: datetime.datetime.now()\n>>> "))

if "_" in inp:
    raise NameError("no _ %r" % inp)


print(eval(inp, {"__builtins__": {"datetime": datetime}}, {}))
