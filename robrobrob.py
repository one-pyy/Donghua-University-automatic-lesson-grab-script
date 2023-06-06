import requests
import json
import time
import random
from typing import *
import traceback
from objprint import op

# 考虑某节课选了某老师不满意, 想要换老师但怕退了不能选上的情况
# 可以在发现有空余时再退课并选课
#course_code, tc_code, del_tc_code(可以是None)
id_list = [('039661', '265177', None)]
#https://webproxy.dhu.edu.cn/http/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu/captcha/code

url = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Cookie': input("cookie meow, give me cookie thanks meow: "),
    'Origin': 'https://webproxy.dhu.edu.cn',
    'Referer': 'https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu/selectcourse/toSCC',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

cource_list_data = {
  'sEcho': '1',
  'iColumns': '10',
  'sColumns': '',
  'iDisplayStart': '0',
  'iDisplayLength': '-1',
  'mDataProp_0': 'cttId',
  'mDataProp_1': 'classNo',
  'mDataProp_2': 'maxCnt',
  'mDataProp_3': 'applyCnt',
  'mDataProp_4': 'enrollCnt',
  'mDataProp_5': 'priorMajors',
  'mDataProp_6': 'techName',
  'mDataProp_7': 'cttId',
  'mDataProp_8': 'cttId',
  'mDataProp_9': 'cttId',
  'iSortCol_0': '0',
  'sSortDir_0': 'asc',
  'iSortingCols': '1',
  'bSortable_0': 'false',
  'bSortable_1': 'false',
  'bSortable_2': 'false',
  'bSortable_3': 'false',
  'bSortable_4': 'false',
  'bSortable_5': 'false',
  'bSortable_6': 'false',
  'bSortable_7': 'false',
  'bSortable_8': 'false',
  'bSortable_9': 'false',
}

def get_space_num(course_code: str, tc_code: str) -> int:
  while True:
    response = None
    try:
      response = requests.post( 
        f'{url}/selectcourse/initACC?vpn-12-o1-jwgl.dhu.edu.cn',
        headers=dict(headers, Referer=f'{url}/selectcourse/toSH'),
        data=dict(cource_list_data, courseCode=course_code),
      )
      js: List[Dict[str, Any]] = json.loads(response.text)['aaData']
      target = filter(lambda x: str(x['cttId']) == tc_code, js).__next__()
      remaining_quota = target['maxCnt']-target['enrollCnt']
      return remaining_quota
    except (KeyboardInterrupt, requests.exceptions.SSLError):
      raise
    except:
      if response is not None:
        op(response.json())
      traceback.print_exc()

def del_cource(tc_code: Union[None, str]):
  if not tc_code:
    return
  data = {
    'courseCode': tc_code,
    'classNo': '3',
    'cancelType': '1',
  }
  try:
    response = requests.post(
      f'{url}/selectcourse/cancelSC?vpn-12-o1-jwgl.dhu.edu.cn',
      headers=headers,
      data=data,
    )
  except: 
    traceback.print_exc()
  else:
    print(f"退课<{tc_code}>:", response.text)

def enroll(tc_code: str):
  data = {
    'cttId': tc_code,
    'needMaterial': False, 
    'capCode': 'e8xn'
  }
  while True:
    response = None
    try:
      response = requests.post(
        f'{url}/selectcourse/scSubmit?vpn-12-o1-jwgl.dhu.edu.cn',
        headers=dict(headers, Referer=f'{url}/selectcourse/toSH'),
        data=data,
      )
      js=json.loads(response.text)
      if js['success']==True and "msg" not in js:
        print(f'\n抢到了{tc_code}'+' '*70)
        return
    except:
      if response is not None:
        print(response.text)
      traceback.print_exc()

def try_enroll(course_code: str, tc_code: str, del_tc_code: Union[str, None]) -> bool:
  print(f'\r试抢{tc_code}'+f'  {random.random()}                  ', end='')
  if get_space_num(course_code, tc_code) > 0:
    del_cource(del_tc_code)
    enroll(tc_code)
    return True
  else:
    return False

if __name__=='__main__':
  while True:
    if id_list.__len__()==0:
      break
    
    for course_code, tc_code, del_tc_code in id_list[:]:
      try:
        if try_enroll(course_code, tc_code, del_tc_code):
          id_list.remove((course_code, tc_code, del_tc_code))
      except:
        pass
      time.sleep(3)
