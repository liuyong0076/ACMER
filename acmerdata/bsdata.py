# pip install BeautifulSoup4
from .models import Student, Contest, StudentContest,AddStudentqueue,CFContest
from bs4 import BeautifulSoup
import requests
import json, time, datetime
import operator
from selenium import webdriver
from selenium.webdriver.common.by import By

def getUrlText(url):
    while True:
        try:
            html = requests.get(url,timeout=60)
            html = html.text
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3)    
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)
    return html

# codeforces get one user's data
def getCFUserData(cfID):
    url = "https://codeforces.com/api/user.rating?handle=" + cfID.strip()
    html = getUrlText(url)    
    js = json.loads(html)    
    if 'result' not in js.keys():
        return []
    results = json.loads(html)['result']
    datalist = []
    for d in results:
        date = d["ratingUpdateTimeSeconds"]
        date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(date)))
        contestID = d["contestId"]
        contest = d["contestName"]
        rank = d["rank"]
        newRating = d["newRating"]
        diff = int(newRating) - int(d["oldRating"])
        datalist.append({
                'date': date,
                'contestID': contestID,
                'contest': contest, 
                'rank': rank, 
                'newRating': newRating,
                'diff':diff
            })
    # print(datalist['result'])
    return datalist

# atcoder get one user's data
def getACUserData(acID):
    print("getACUserData---"+acID)
    url = "https://atcoder.jp/users/"+acID.strip()+"/history"
    html = getUrlText(url)
    soup = BeautifulSoup(html, features="lxml")
    table = soup.select('#history')
    if len(table) > 0:
        t = table[0]
    else:
        return []

    # [dict1, dict2, ...]
    # dict:{'date': date, 'contest': contest, 'rank': rank, 'newRating': newRanking, 'diff':diff}
    data_list = []  

    for idx, tr in enumerate(t.select('tr')):
        if idx != 0:
            tds = tr.select('td')
            date = tds[0].select('time')[0].text
            contest = tds[1].select('a')[0].text
            rank = tds[2].select('a')[0].text
            if len(tds[4].select('span')) > 0:
                newRating = tds[4].select('span')[0].text
            else:
                newRating = tds[4].text
            diff = tds[5].contents[0]
            if str(newRating).isdigit() == False:
                newRating = 0
            # print(date,contest,rank,newRating,diff)
            data_list.append({
                'date': date,
                'contestID': -1,
                'contest': contest, 
                'rank': rank, 
                'newRating': newRating, 
                'diff':diff
            })

    return data_list

def getCFContestList(max_timestamp):
    url = "https://codeforces.com/api/contest.list?gym=false"
    html = getUrlText(url)
    js = json.loads(html)    
    if 'result' not in js.keys():
        return []
    results = json.loads(html)['result']
    datalist = []
    for d in results:
        if int(d["startTimeSeconds"])>int(max_timestamp):
            datalist.append({
                "cid":d["id"],
                "cname":d["name"],
                "cdate":time.strftime("%Y-%m-%d %H:%M:%S",(time.localtime(int(d["startTimeSeconds"])))),
                "starttime":int(d["startTimeSeconds"]),
                "endtime":d["startTimeSeconds"]+d["durationSeconds"],
            })
        datalist.sort(key=operator.itemgetter('starttime'))
    return datalist

def getCFContestRankingChange(contestID,existCFIDList):
    url = "https://codeforces.com/api/contest.ratingChanges?contestId=" + str(contestID)  #566
    html = getUrlText(url)
    js = json.loads(html)    
    if 'result' not in js.keys():
        return []
    results = json.loads(html)['result']
    datalist = []
    for d in results:
        if d["handle"] in existCFIDList:
            datalist.append({
                "cfID":d['handle'],
                "rank":d['rank'],
                "newRating":d["newRating"],
                "diff":int(d["newRating"])-int(d["oldRating"])
            })
    return datalist

def cheakcfID(cfID):
    url = "https://codeforces.com/api/user.rating?handle=" + cfID.strip()
    html = getUrlText(url)    
    js = json.loads(html)
    statu = js['status']
    if statu == 'OK':
        return True
    else:
        return False

def cheakacID(acID):
    if acID =='':
        return False
    url = "https://atcoder.jp/users/"+acID.strip()+"/history"
    html = getUrlText(url)
    soup = BeautifulSoup(html, features="lxml")
    table = soup.select('#user-nav-tabs')
    if len(table)==0:
        return False
    else:
        return True
def getNCUserData(ncID):
    url = "https://ac.nowcoder.com/acm/contest/profile/" + ncID
    driver = webdriver.PhantomJS()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source)
    page_s = soup.select(".js-contest-list")
    p=page_s[0]
    datalist = []
    li=p.select("ul")
    if len(li)<2:
        return datalist
    else:
        li=li[1]
    l=li.select("li")
    if len(l)==0:
        pages=1
    else:
        pages = len(l)-4
    while pages:
        bs = BeautifulSoup(driver.page_source)
        f=bs.select(".compete-list")[0]
        contest = f.select("li")
        for s,li in enumerate(contest):
            name = li.select(".compete-item-name")[0].text
            date = li.select(".item-cont")[0].text[0:16]
            state = li.select(".state-num")
            if state[0].select('span')[0].text.isdigit()==False:
                newrating = 0
            else:
                newrating = int(state[0].select('span')[0].text)
            if state[0].text !="不计":
                diff = state[0].text.split("(")[1].replace(")","")
            else:
                diff = "0"
            rank = exeNCrank(state[1].text)
            acnum = state[2].text
            datalist.append({'contest':name,'contestID':-1,'date':date,'rank':rank,'acnum':acnum,'newrating':newrating,'diff':diff})
        pages = pages - 1
        if pages:
            while True:
                    print(pages)
                    driver.find_element(By.LINK_TEXT,"下一页").click()
                    time.sleep(3)
                    break
    driver.close()
    return datalist

def exeNCrank(rank):
    p=rank.replace(" ","")
    l=p.split("/" , 1)
    return int(l[0])

def getsubmitdata(cid,cfID):
    url = 'https://codeforces.com/api/contest.status?contestId='+str(cid)+'&handle='+cfID
    html = getUrlText(url)
    datalist = []
    data = json.loads(html)['result']
    for submit in data:
        t=0
        while True:
            try:
                t=t+1
                sc = CFContest.objects.filter(subid=submit['id'])
                if len(sc)==0 or sc.code=='get error':
                    code = submitdetail(cid,submit['id'])
                else:
                    code = sc[0].code
                break
            except:
                if t>5 :
                    code='get error'
                    break
        tags=''
        for tag in submit['problem']['tags']:
            if tags == '' :
                tags += tag
            else:
                tags = tags + "," + tag
        print(submit['id'])
        datalist.append(
            {
                'time':submit['creationTimeSeconds'],
                'subid':int(submit['id']),
                'index':submit['problem']['index'],
                'code':code,
                'tags':tags,
                'statu':submit['verdict'],
            }
        )
    return datalist

"""def getcfsolve(cid,cfID):
    url = 'https://codeforces.com/api/contest.status?contestId='+str(cid)+'&handle='+cfID
    html = getUrlText(url)
    solve = 0
    indexs = ''
    data = json.loads(html)['result']
    for submit in data:
        if submit['verdict']=='OK':
            if indexs.find(submit['problem']['index']) == -1 :
                solve = solve + 1
                indexs += submit['problem']['index']
    return solve"""
#旧solve获取，已废弃
def submitdetail(cid,subID):
    code = ''
    url = 'https://codeforces.com/contest/'+str(cid)+'/submission/'+str(subID)
    html = getUrlText(url)
    soup = BeautifulSoup(html,features="lxml")
    o = soup.select(".linenums")[0]
    p = o.select("li")
    code = o.text
    #print(code)
    return code

def contestsubmitgetupdate(cid,cfidlist,maxsubid):
    url = 'https://codeforces.com/api/contest.status?contestId=' +str(cid)
    source = getUrlText(url)
    submits = json.loads(source)['result']
    datalist = []
    t=0
    for submit in submits:
        mem=submit['author']['members']
        t=t+1
        """print(t)
        if t == 849 or submit['id']==71268945:
            print("mark")
            pass"""
        for p in mem:
            if p['handle'] in cfidlist and int(submit['id'])>maxsubid:
                print(submit['id'])
                tags=''
                for tag in submit['problem']['tags']:
                    if tags == '' :
                        tags += tag
                    else:
                        tags = tags + "," + tag
                datalist.append({
                    'subid':int(submit['id']),
                    'cfid':p['handle'],
                    'cid':cid,
                    'index':submit['problem']['index'],
                    'tags':tags,
                    'statu':submit['verdict'],
                    'time':submit['creationTimeSeconds'],
                })
                break
    return datalist

def cfforecastget():
    url = 'https://codeforces.com/api/contest.list?gym=false'
    html = getUrlText(url)
    text = json.loads(html)['result']
    ntime=time.time()
    datalist=[]
    for contest in text:
        if contest['startTimeSeconds']>ntime:
            datalist.append({
                'during':contest['durationSeconds'],
                'starttime':contest['startTimeSeconds'],
                'contestname':contest['name'],
                'cid':contest['id'],
            })
    return datalist
def acforecastget():
    url = 'https://atcoder.jp/contests/'
    html = getUrlText(url)
    soup = BeautifulSoup(html,'lxml')
    upcome = soup.select("#contest-table-upcoming")[0]
    trs = upcome.select('tr')
    datalist = []
    for tid,tr in enumerate(trs):
        if tid !=0:
            td = tr.select('td')
            ta = time.strptime(td[0].text[0:19],"%Y-%m-%d %H:%M:%S")
            starttime = int(time.mktime(ta))-3600
            name = str(td[1].text).replace("\n","").replace("◉","")
            during = td[2].text
            link =  'https://atcoder.jp'+td[1].select('a')[0]['href']
            datalist.append({
                'starttime':starttime,
                'contestname':name,
                'during':during,
                'link':link,
            })
    return datalist

def ncforecastget():
    url = 'https://ac.nowcoder.com/acm/contest/vip-index'
    html = getUrlText(url)
    bs = BeautifulSoup(html,"lxml")
    current = bs.select(".js-current")[0].select(".js-item")
    datalist = []
    for contest in current:
        link = "https://ac.nowcoder.com" + contest.select(".platform-item-cont")[0].select("a")[0]['href']
        jsondata = str(contest['data-json']).replace("&quot;","\"")
        data = json.loads(jsondata)
        starttime = int(str(data['contestStartTime'])[:-3])
        during = str(data['contestDuration'])[:-3]
        name = data['contestName']
        datalist.append({
                'starttime':starttime,
                'contestname':name,
                'during':during,
                'link':link,
        })
    return datalist

def getcftimestamp(cflist):
    url = "https://codeforces.com/api/contest.list?gym=false"
    html = getUrlText(url)
    li = json.loads(html)['result']
    timelist = []
    for contest in li:
        if contest['id'] in cflist:
            timelist.append({
                'starttime' : contest['startTimeSeconds'],
                'endtime' : contest['startTimeSeconds'] + contest['durationSeconds'],
                'cid' : contest['id'],
            })
    return timelist
