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
