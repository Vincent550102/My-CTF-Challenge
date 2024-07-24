def foo(x):
    result = "(chr==chr)+" * ord(x)
    return result.rstrip("+")


print(f"chr({foo('f')})+chr({foo('g')})")
