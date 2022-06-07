import HackRequests
import json
import time
idList=[???]

header='''
???
'''

if idList.__len__()==0:
    break
  for id in idList:
    js=json.loads(HackRequests.http('https://webproxy.dhu.edu.cn/http/77726476706e69737468656265737421fae0469069346045300d8db9d6562d/dhu/selectcourse/scSubmit?vpn-12-o1-jwgl.dhu.edu.cn', headers=header, post={'cttId':id,'needMaterial':False, 'capCode':'fgee'}).text())
    js['id']=id
    if js['success']==True:
      print(f'抢到了{id}')
      idList.remove(id)
      break
    print(js, end='                \r')
    time.sleep(5)
