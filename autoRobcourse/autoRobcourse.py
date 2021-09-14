#import code
import re
import pickle
import getpass
#import sys
import numpy as np
import requests
import random
import time
import os
from functools import cmp_to_key
from prettytable import PrettyTable as pt
import getPass
import time
from requests.adapters import HTTPAdapter
import sys

def geTime():
  return time.strftime("%Y-%m-%d  %H:%M:%S",time.localtime())

def glb():
  glb.nl=[]#needList
  glb.nsl=set()#needSelectList
  glb.imf : map

def rd(name):
  path="cache\\"+name+".pkl"
  if not os.path.exists(path):
    return None
  with open(path,'rb') as file:
    rq  = pickle.loads(file.read())
  return rq

def readToInit():
  if os.path.exists("cache\\imf.pkl"):
    imf=rd("imf")
    if imf['stuNo']==glb.imf['stuNo'] and glb.imf['turn']==glb.imf['turn']:
      glb.cc=rd('cc')
      glb.ncc=rd('ncc')
      glb.all=rd('all')
      glb.allimf=rd('allimf')
      glb.got=rd('got')
      glb.table=rd('table')
      return 1
  glb.cc={}#ChoosenCourse
  glb.ncc={}#NoChoosenCourse
  glb.all={}#allCourses
  glb.allimf={}#allCourseInf
  glb.got={}
  glb.table=classTable()
  return 0

def readAll():
  if rd('nl')==None:
    return
  glb.nl=rd('nl')
  glb.nsl=rd('nsl')

def saveAll():
  wr(glb.nl,'nl')
  wr(glb.nsl,'nsl')

def wr(things,name):
  path="cache\\"+name+".pkl"
  if not os.path.exists(path):
    open(path, 'w').close()
  output_hal = open(path, 'wb')
  str = pickle.dumps(things)
  output_hal.write(str)
  output_hal.close()

def save():
  wr(glb.cc,"cc")
  wr(glb.ncc,"ncc")
  wr(glb.all,"all")
  wr(glb.allimf,"allimf")
  wr(glb.got,"got")
  wr(glb.imf,"imf")
  wr(glb.table,'table')

req=requests.session()
req.mount('http://', requests.adapters.HTTPAdapter(max_retries=10))
req.mount('https://', requests.adapters.HTTPAdapter(max_retries=10))

class t:#单节课的单个时间
  def __init__(self,ls):
    super().__init__()
    self.week,self.st,self.ed,self.ws,self.we=ls[0],ls[1],ls[2],ls[3],ls[4]

  def getdoc(self):
    return "\t{}-{}周\t周{}\t第{}-{}节\n\t".format(self.ws+1,self.we,self.week+1,self.st+1,self.ed)

class courseImfor:#某节课的信息

  @staticmethod
  def _getTime(s):
    week=re.findall("(?<=周).",s)[0]
    ls=re.findall("\d+",s)
    st,ed=int(ls[0]),int(ls[-1])
    if week=="一":
      week=0
    elif week=="二":
      week=1
    elif week=="三":
      week=2
    elif week=="四":
      week=3
    elif week=="五":
      week=4
    return [week,st-1,ed]

  @staticmethod
  def _getWeek(s):
    a=re.findall("\d+",s)
    return [int(a[0])-1,int(a[-1])]

  def __init__(self,map,got=0):
    super().__init__()
    self.got=got
    if got==0:
      self.id=str(map['cttId'])
      self.Tname=map['techName']
      self.name=map['crName']
      self.enroll=map['enrollCnt']
      self.max=map['maxCnt']
    else:
      self.id=str(map['courseCode'])
      self.Tname=map['teachName']
      self.name=map['courseName']
    self.t=[]
    ct,uw='classTime','useWeek'
    for k in range(1,5):
      if map[ct+str(k)]==None:
        break
      self.t.append(t(courseImfor._getTime(map[ct+str(k)])+courseImfor._getWeek(map[uw+str(k)])))
    glb.allimf[self.id]=self

  def getTime(self):
    return t

  def getdoc(self):
    s=''
    for each in self.t:
      s+=each.getdoc()
    if s=='':
      s+='无'
    if self.got==0:
      return "\t课程id：{}\t教师：{}\t录取情况：{}/{}\n\t时间：{}\n".format(self.id,self.Tname,self.enroll,self.max,s)
    else:
      return "\t课程id：{}\t教师：{}\t\n时间：{}\n".format(self.id,self.Tname,s)

  def getLdoc(self):
    s=''
    for each in self.t:
      s+=each.getdoc()
    return "\t课程名：{}\t课程id：{}\t教师：{}\t录取情况：{}/{}\n\t时间：{}\n".format(self.name,self.id,self.Tname,self.enroll,self.max,s)

class course:#某种课的信息
  def __init__(self,name,turn,code,got,imf=None):
    super().__init__()
    self.imf=[]
    self.turn=turn
    self.got=got
    self.code=code
    self.name=name
    if imf==None:
      self.getable=self._getInf()
    else:
      self.imf.append(courseImfor(imf,1))
      self.getable=0
  
  def getTime(self):#only
    s=[]
    for each in self.imf:
      s+=each.getTime()
    return s
  
  def getdoc(self):
    s='\t课程: {}\n\t建议修读学期: {}\n\t已选: {}\n\t课程代码: {}\n'.format(self.name,self.turn,self.got,self.code)
    if self.getable==0 and self.got==0:
      s+='\t未开放选课\n'
    elif self.getable==0 and self.got==1:
      s+='\t已选\n'
    else:
      for each in self.imf:
        s+=each.getdoc()
    return s
  
  def _getInf(self):
    data={'courseCode':self.code}
    url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/accessJudge',headers=glb.headers,data=data,cookies=req.cookies.get_dict(),timeout=15)
    if url.json()['success']==0:
      return 0
    data={'sEcho':'1&iColumns=10&sColumns=&iDisplayStart=0&iDisplayLength=-1&mDataProp_0=cttId&mDataProp_1=classNo&mDataProp_2=maxCnt&mDataProp_3=applyCnt&mDataProp_4=enrollCnt&mDataProp_5=priorMajors&mDataProp_6=techName&mDataProp_7=cttId&mDataProp_8=cttId&mDataProp_9=cttId&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&bSortable_0=false&bSortable_1=false&bSortable_2=false&bSortable_3=false&bSortable_4=false&bSortable_5=false&bSortable_6=false&bSortable_7=false&bSortable_8=false&bSortable_9=false','courseCode':self.code}
    url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/initACC',headers=glb.headers,data=data,cookies=req.cookies.get_dict(),timeout=15)
    courseList=url.json()['aaData']
    for each in courseList:
      if each['priorMajors'].count('延安')==0:#####
        self.imf.append(courseImfor(each))
    return 1

class classTable:#dfs操作台
  def __init__(self):
    super().__init__()
    self.ct=np.full((13,5,18),0,dtype=bool)
  
  def set1_f(self,ci):
    for i in ci:
      for week in range(i.ws,i.we):
        for time in range(i.st,i.ed):
          self.ct[time][i.week][week]=1
  
  def set1(self,ci):#ci:courseimfor
    for i in ci:
      for week in range(i.ws,i.we):
        for time in range(i.st,i.ed):
          if self.ct[time][i.week][week]==1:
            return 0
    for i in ci:
      for week in range(i.ws,i.we):
        for time in range(i.st,i.ed):
          self.ct[time][i.week][week]=1
    return 1
  
  def set0(self,ci):
    for i in ci:
      for week in range(i.ws,i.we):
        for time in range(i.st,i.ed):
          self.ct[time][i.week][week]=0
  
  def _getrow(self,row):
    r=[]
    for day in range(0,5):
      s=''
      for week in range(0,18):
        if self.ct[row][day][week]==1:
          s+='#'
        else:
          s+='-'
      r.append(s)
    return r
  
  def getdoc(self):
    t=['8:15-9:00','9:00-9:45','10:05-10:50','10:50-11:35','13:00-13:45','13:45-14:30','14:50-15:35','15:35-16:20','16:20-17:05','18:00-18:45','18:45-19:30','19:50-20:35','20:35-21:20']
    s=pt()
    s.field_names=['','时间','周一','周二','周三','周四','周五']
    for i in range(0,13):
      w=self._getrow(i)
      w.insert(0,t[i])
      w.insert(0,i+1)
      s.add_row(w)
    return "'-'代表空闲，'#'代表有安排。\n{}".format(s)

def getSalt():#找到藏着的密钥
  headers={
    'Host':'cas.dhu.edu.cn',
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0',
    'sec-ch-ua':'"Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile':'?0',
    'DNT':'1',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site':'cross-site',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-User':'?1',
    'Sec-Fetch-Dest':'document',
    'Referer':'http://jwgl.dhu.edu.cn/',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
  }
  url=req.get('https://cas.dhu.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.dhu.edu.cn%2Fdhu%2FcasLogin',headers=headers,timeout=15)
  glb.salt=re.findall('(?<=pwdDefaultEncryptSalt = ").+?(?=")',url.text)[0]
  glb.lt=re.findall('(?<=name="lt" value=").+?(?=")',url.text)[0]
  glb.dllt=re.findall('(?<=name="dllt" value=").+?(?=")',url.text)[0]
  glb.execution=re.findall('(?<=name="execution" value=").+?(?=")',url.text)[0]
  glb._eventId=re.findall('(?<=name="_eventId" value=").+?(?=")',url.text)[0]
  glb.rmShown=re.findall('(?<=name="rmShown" value=").+?(?=")',url.text)[0]
  getCookie()

def getCookie():
  headers={
    'Host':'cas.dhu.edu.cn',
    'Connection':'keep-alive',
    'Content-Length':'275',
    'Cache-Control':'max-age=0',
    'sec-ch-ua':'" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile':'?0',
    'Origin':'https://cas.dhu.edu.cn',
    'Upgrade-Insecure-Requests':'1',
    'DNT':'1',
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-User':'?1',
    'Sec-Fetch-Dest':'document',
    'Referer':'https://cas.dhu.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.dhu.edu.cn%2Fdhu%2FcasLogin',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
  }
  data={
    'username':glb.sNo,
    'password':getPass.getCryptPass(glb.sSec,glb.salt),
    'lt':glb.lt,
    'dllt':glb.dllt,
    'execution':glb.execution,
    '_eventId':glb._eventId,
    'rmShown':glb.rmShown
  }
  url=req.post('https://cas.dhu.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.dhu.edu.cn%2Fdhu%2FcasLogin',headers=headers,data=data,timeout=15)

def GetUserImf():#获取用户信息，生成请求头，得到cookie
  glb.sNo=input("请输入您的学号: ")
  glb.sSec=getpass.getpass('请输入您的密码: ')
  glb.seme=input('输入选课学期（例如：20212022a 代表2021-2022学年 第1学期）: ')
  glb.headers={
    'Host':'jwgl.dhu.edu.cn',
    'Connection':'keep-alive',
    'Content-Length':'37',
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'DNT':'1',
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67',
    'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin':'http://jwgl.dhu.edu.cn',
    'Referer':'http://jwgl.dhu.edu.cn/dhu/selectcourse/toSH',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  }
  print("登录中")
  getSalt()
  getCookie()
  glb.imf={
    "stuNo":glb.sNo,
    "turn":glb.seme
  }

def GetCourseText():#获取选课列表
  data={
    'studNo':glb.sNo,
    'scSemester':glb.seme
  }
  url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/initTSCourses',headers=glb.headers,data=data,cookies=req.cookies.get_dict(),timeout=15)
  print(url.status_code)
  if url.status_code != requests.codes.ok:
    ans=input("与教务处链接错误，请再试一次吧(是/否)")
    if ans!='是':
      url=GetCourseText()
    else:
      exit(0)
  elif url.json()['success']==0:
    print('错误(大概)')
    url=GetCourseText()
  else:
    print('已获取课程列表')
  return url

def GetCourseList(list):#完善课程信息并进行分类
  def getCourseClass(list):
    map=list["tsCourseMapNoCagegory"]
    categorys=list['courseCategory']
    for category in categorys:
      url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/initSCC',headers=glb.headers,data={'smallSort':category},cookies=req.cookies.get_dict(),timeout=15)
      map[category]=url.json()['sccs']
    return map
  map=getCourseClass(list)
  got=list["crScores"]
  tmp=0
  maxx=0
  for key in map:
    for c in map[key]:
      maxx+=1
  for key in map:
    if key.count("必修")==0:
      for c in map[key]:
        tmp+=1
        glb.cc[c['courseCode']]=course(c['courseName'],c['yearTerm'] if 'yearTerm' in c else "无推荐选修时间",c['courseCode'],c['courseCode'] in got)
        print('\r爬取课程信息中({}/{})'.format(tmp,maxx),end='')
    else :
      for c in map[key]:
        tmp+=1
        glb.ncc[c['courseCode']]=course(c['courseName'],c['yearTerm'],c['courseCode'],c['courseCode'] in got)
        print('\r爬取课程信息中({}/{})'.format(tmp,maxx),end='')
  glb.all=dict(**glb.ncc,**glb.cc)

def GetSelectedList():#得到此学期目前的课表
  headers=glb.headers.copy()
  print('获取已选课程中……')
  headers['Referer']='http://jwgl.dhu.edu.cn/dhu/selectcourse/toSSC'
  url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/initSelCourses',headers=headers,cookies=req.cookies.get_dict(),timeout=15)
  print('分析中……')
  list=url.json()['enrollCourses']+url.json()['selectedCourses']
  for c in list:
    glb.got[c['courseCode']]=course(c['courseName'],'本学期',c['courseCode'],True,c)
  for a,each in glb.got.items():
    for qwq in each.imf:
      glb.table.set1(qwq.t)

def PrintCourseList(IgnoreGetable):#输出课程列表
  print('\n\n\n必修：')
  for a,each in glb.ncc.items():
    if IgnoreGetable==0 or each.getable==1:
      print(each.getdoc())
  print('\n\n\n选修：')
  for a,each in glb.cc.items():
    if IgnoreGetable==0 or each.getable==1:
      print(each.getdoc())

def PrintSelectesList():#输出已选列表
  for a,each in glb.got.items():
    print(each.getdoc())

def PrintNeed():
  for i in glb.nl:
    print(glb.all[i].getdoc())

def ChangeNeed():
  while 1:
    id=input('请输入您要取反的课程代码（注意不要与id混淆--代码是一种课程，id是比它小的某一节具体的科），退出输入exit：')
    if id=='exit':
      break
    if id not in glb.all:
      print('没有检索到该课程')
    else:
      print(glb.all[id])
    if id in glb.nl:
      glb.nl.remove(id)
      print('已删除代码为{}的课程'.format(id))
    else :
      glb.nl.append(id)
      print('已添加代码为{}的课程'.format(id))

def ChangeSelNeed():
  while 1:
    id=input('请输入您要取反的课程id（注意不要与代码混淆--代码是一种课程，id是比它小的某一节具体的课），退出输入exit：')
    if id=='exit':
      break
    if id in glb.nsl:
      glb.nsl.remove(id)
      print('已删除id为{}的课程'.format(id))
    else :
      glb.nsl.add(id)
      print('已添加id为{}的课程'.format(id))

def autoSelect():
  s=input('请输入必修课的学期（例如：2S）')
  for a,each in glb.ncc.items():
    if each.turn==s and each.got==0:
      glb.nl.append(a)
  print('以下是要选的课：')
  PrintNeed()

def _cmp(a,b):
  return len(glb.all[a].imf)<len(glb.all[b].imf)

def printNsl():
  print('得到可行的选课方案：')
  for id in glb.nsl:
    print(glb.allimf[id].getLdoc())
  print(glb.table.getdoc())
  a=input('输入0则选用此方案，继续搜索请输入1：')
  if a=='0':
    return 1
  else:
    return 0

def autoArrange():
  def dfs(_now,siz):
    if _now==siz:
      return printNsl()
    now=glb.all[glb.nl[_now]]
    for eachimf in now.imf:
      if glb.table.set1(eachimf.t)==1:
        glb.nsl.add(eachimf.id)
        if dfs(_now+1,siz)==1:
          return 1
        glb.nsl.remove(eachimf.id)
        glb.table.set0(eachimf.t)
      else:
        return 0
  sorted(glb.nl,key=cmp_to_key(_cmp))
  dfs(0,len(glb.nl))
  print('搜索完毕')

def SetBusyTime():
  while 1:
    ip=input('请输入时间（输入exit退出）\n格式：增加还是删除（增加为1，删除为0） 星期几 从第几节课开始 到第几节课结束 从第几周开始 到第几周结束）\n例如：1 2 3 4 5 6代表：增加不想上课时间 —— 5-6周 周二的3-4节课\n')
    if ip=='exit':
      break
    s=re.findall('\d+',ip)
    for i in range(0,6):
      s[i]=int(s[i])
    s[1]-=1
    s[2]-=1
    s[4]-=1
    if s[0]==1:
      glb.table.set1_f([t(s[1:6])])
    else:
      glb.table.set0([t(s[1:6])])

def autoRob():
  print(glb.nsl)
  print('60s抢一轮（抢的快了应该会出来验证码）')
  nsl=list(glb.nsl)
  while 1:
    for id in nsl:
      data={
        'cttId':id,
        'needMaterial':'false'
      }
      url=req.post('http://jwgl.dhu.edu.cn/dhu/selectcourse/scSubmit',headers=glb.headers,data=data,cookies=req.cookies.get_dict(),timeout=15)
      print(geTime(),end='   ')
      if {'success':True} == url.json():
        nsl.remove(id)
        print('抢到了,id:{}\n还有：{}\n{}'.format(id,nsl,url.json()))
      else:
        print('id {} : {}'.format(id,url.json()))
    if len(nsl)==0:
      print('全部抢完了')
      break
    time.sleep(60)
def menu():
  choose=input("""
       目录
  
  1.输出可选课程。
  2.输出所有课程。
  3.输出已选课程。
  4.查看待排课程名单。
  5.修改待排课程。
  6.自动选择必修课。
  7.设置不上课时间。
  8.自动排课。
  9.自动抢课。
  10.保存排课选课数据。
  11.输出安排时间表。
  12.修改待选名单。
  13.获取排课选课数据。
  >>>""")
  if choose=='1':
    PrintCourseList(1)
  elif choose=='2':
    PrintCourseList(0)
  elif choose=='3':
    PrintSelectesList()
  elif choose=='4':
    PrintNeed()
  elif choose=='5':
    ChangeNeed()
  elif choose=='6':
    autoSelect()
  elif choose=='7':
    SetBusyTime()
  elif choose=='8':
    autoArrange()
  elif choose=='9':
    #print('因政策原因，本功能暂不开放')
    autoRob()
  elif choose=='10':
    saveAll()
  elif choose=='11':
    print(glb.table.getdoc())
  elif choose=='12':
    ChangeSelNeed()
  elif choose=='13':
    readAll()
    print(glb.nl)
    print(glb.nsl)
  else:
    print('输入错误，请重新输入。')

def main():
  print('温馨提示：请挂上vpn。本程序没有鲁棒性，不合法（或合法）的输入极易导致崩溃，请慎重输入。（如果报错了可以多试几遍，如果登录部分一直报错但链接是200，那么可能是需要输入验证码，登上学校官网再退出即可）')
  GetUserImf()
  if readToInit()==0:
    print('爬取信息中……')
    url=GetCourseText()
    GetCourseList(url.json()["tsCourses"])
    GetSelectedList()
    save()
    print("已自动保存信息")
  else :
    print("已从文件中获取到选课信息")
  while 1:
    menu()

if __name__=="__main__":
  glb()
  main()
  
  #code.InteractiveConsole(globals()).interact("")
