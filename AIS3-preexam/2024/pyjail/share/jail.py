#!/usr/local/bin/python3

from safe_eval import safe_eval
from inspect import getdoc


class Desc:
    """
    Welcome to my 🐍 ⛓️
    """

    def __get__(self, objname, obj):
        return __import__("conf").flag

    def desc_helper(self, name):
        origin = getattr(type, name)
        if origin == type.__getattribute__:
            raise NameError(
                "Access to forbidden name %r (%r)" % (name, "__getattribute__")
            )
        self.helper = origin


class Test:
    desc = Desc()


test = Test()
test.desc = "flag{fakeflag}"


# Just a tricky way to print a welcome message, or maybe a hint :/
# You can just `print(getdoc(Desc))`
# This is not part of the challenge, but if you can get the flag through here, please contact @Vincent55.
welcome_msg = """
desctmp := Desc()
desctmp.desc_helper("__base__")
Obj := desctmp.helper
desctmp := Desc()
desctmp.desc_helper("__subclasses__")
print(getdoc(desctmp.helper(Obj)[-2]))
""".strip().replace("\n", ",")
welcome_msg = f"({welcome_msg})"

safe_eval(
    welcome_msg,
    {"__builtins__": {}},
    {"Desc": Desc, "print": print, "getdoc": getdoc},
)


# Your challenge begin here!
payload = input("✏️: ")

safe_eval(
    payload,
    {"__builtins__": {}},
    {"Desc": Desc},
)

# print(f"test.__dict__: {test.__dict__}")
print(f"🚩: {test.desc}")
