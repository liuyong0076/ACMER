from bs4 import BeautifulSoup
import requests
from acmerdata import bsdata
from .models import Student, Contest, StudentContest,AddStudentqueue,CFContest,Contestforecast,ACContest
import logging
import time
import datetime
def getUrlText(url):
    while True:
        try:
            html = requests.get(url)
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

def getACUserData(acID):    #根据acID获取比赛记录,返回一个字典列表,里面存储此学生的比赛记录
    print("getACUserData---"+acID)
    url = "https://atcoder.jp/users/"+acID.strip()+"/history"
    html = getUrlText(url)
    soup = BeautifulSoup(html, features="lxml")
    table = soup.select('#history')
    if len(table) > 0:
        t = table[0]
    else:
        return []

    data_list = []  

    for idx, tr in enumerate(t.select('tr')):
        if idx != 0:
            tds = tr.select('td')
            timestamp = acTimefix(tds[0].select('time')[0].text)
            contest = tds[1].select('a')[0].text
            nickName = tds[1].select('a')[0]['href'].split("/")[2]
            rank = tds[2].select('a')[0].text
            if len(tds[4].select('span')) > 0:
                newRating = tds[4].select('span')[0].text
            else:
                newRating = tds[4].text
            diff = tds[5].contents[0]
            if str(newRating).isdigit() == False:
                newRating = 0
            if str(diff) == '-':
                diff = newRating
            # print(date,contest,rank,newRating,diff)
            data_list.append({
                'date': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp)),
                'contestID': -1,
                'contest': contest, 
                'rank': rank,
                'newRating': newRating,
                'diff':diff,
                'nickName':nickName,
                'endtimestamp':timestamp
            })

    return data_list

def getACSubmitData(acID,acNickName):
    datalist = []
    for page in range(1,10):
        url = 'https://atcoder.jp/contests/'+str(acNickName)+'/submissions?f.Task=&f.Language=&f.Status=&f.User=' + str(acID) + '&page='+str(page)
        html = getUrlText(url)
        soup = BeautifulSoup(html,"lxml")
        table = soup.select(".panel-submission")[0].select("tbody")
        if len(table) == 0:
            return datalist
        trs = table[0].select("tr")
        for ids,tr in enumerate(trs):
            tds = tr.select('td')
            subtime = acTimefix(tds[0].text)
            task = tds[1].text
            language = tds[3].text
            statu = tds[6].text
            if len(tds)>8:
                subid = tds[9].select('a')[0]['href'].split('/')[4]
            else:
                subid = tds[7].select('a')[0]['href'].split('/')[4]
            datalist.append({
                'ctime':subtime,
                'task':task,
                'language':language,
                'statu':statu,
                'subid':subid,
            })

def contestCodeGet(nickName,subid):
    url = 'https://atcoder.jp/contests/'+str(nickName)+'/submissions/'+str(subid)
    html = getUrlText(url)
    soup = BeautifulSoup(html,"lxml")
    code = soup.select("#submission-code")[0].text
    return code

def saveACDataAll(stu):    #   根据学生对象全部获取atcoder数据
    if stu.acID:
        dataList = getACUserData(stu.acID)
        stu.acTimes = len(dataList)
        if(stu.acTimes > 0):
            stu.acRating = dataList[-1]["newRating"]
            for data in dataList:
                subList = getACSubmitData(stu.acID,data['nickName'])
                task = []
                solve = 0
                after = 0
                for submit in subList:
                    if submit['statu']=='AC':
                        if submit['task'] not in task:
                            task.append(submit['task'])
                            if submit['ctime'] > data['endtimestamp']:
                                after = after + 1
                            else:
                                solve = solve + 1
                    if ACContest.objects.filter(stuNO=stu.stuNO,subid=submit['subid'],nickName=data['nickName']).count() == 0:
                        ACContest.objects.create(stuNO=stu.stuNO,realName=stu.realName,ctime=submit['ctime'],nickName=data['nickName'],cname=data["contest"],
                            subid=submit['subid'],code="wating to get",task=submit['task'],statu=submit['statu'],language=submit['language'])
                if Contest.objects.filter(cname = data['contest'],nickName=data['nickName']).count()==0:
                    Contest.objects.create(cid=data['contestID'],cname=data['contest'],cdate=data['date'],cdiv=0,ctype='ac',cnumber=0,endtimestamp=data['endtimestamp'],nickName=data['nickName'],starttimestamp=0)
                addStudentContestForAC(stu.stuNO,stu.realName,stu.className,data["contestID"],data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"ac",str(solve),str(after),data['nickName'])
        else:
            stu.acRating = 0
    else:
        stu.acTimes = 0
        stu.acRating = 0
    stu.save()

def saveACDataIncrementally(stu):    #   根据学生对象增量获取atcoder数据
    if stu.acID:
        dataList = getACUserData(stu.acID)
        dataList.reverse()
        stu.acTimes = len(dataList)
        if(stu.acTimes > 0):
            stu.acRating = dataList[0]["newRating"]
            for data in dataList:
                if StudentContest.objects.filter(nickName=data['nickName'],ctype='ac',stuNO=stu.stuNO).count() !=0:
                    break
                subList = getACSubmitData(stu.acID,data['nickName'])
                task = []
                solve = 0
                after = 0
                for submit in subList:
                    if submit['statu']=='AC':
                        if submit['task'] not in task:
                            task.append(submit['task'])
                            if submit['ctime'] > data['endtimestamp']:
                                after = after + 1
                            else:
                                solve = solve + 1
                    if ACContest.objects.filter(stuNO=stu.stuNO,subid=submit['subid'],nickName=data['nickName']).count() == 0:
                        ACContest.objects.create(stuNO=stu.stuNO,realName=stu.realName,ctime=submit['ctime'],nickName=data['nickName'],cname=data["contest"],
                            subid=submit['subid'],code="wating to get",task=submit['task'],statu=submit['statu'],language=submit['language'])
                if Contest.objects.filter(cname = data['contest'],nickName=data['nickName']).count()==0:
                    Contest.objects.create(cid=data['contestID'],cname=data['contest'],cdate=data['date'],cdiv=0,ctype='ac',cnumber=0,endtimestamp=data['endtimestamp'],nickName=data['nickName'],starttimestamp=0)
                addStudentContestForAC(stu.stuNO,stu.realName,stu.className,data["contestID"],data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"ac",str(solve),str(after),data['nickName'])
        else:
            stu.acRating = 0
    else:
        stu.acTimes = 0
        stu.acRating = 0
    stu.save()

def addStudentContestForAC(stuNO,realname,classname,cid,cname,cdate,rank,newRating,diff,ctype,solve,aftersolve,nickName):    #添加学生比赛记录
    sc = StudentContest.objects.filter(stuNO=stuNO,cid=cid,cname=cname,ctype=ctype)
    if len(sc) == 0:
        StudentContest.objects.create(stuNO=stuNO,realName=realname,className=classname,
            cid=cid,cname=cname,cdate=cdate,cdiv=0,rank=rank,newRating=newRating,diff=diff,ctype=ctype,solve=solve,aftersolve=aftersolve,nickName=nickName)
    else:
        sc[0].newRating = newRating
        sc[0].diff = diff  # for fix bug
        sc[0].save()

def getCodeUpdate():
    log = logging.getLogger("log")
    log.info("Begin accode Updata")
    count = 0
    submits = ACContest.objects.filter(code = "wating to get")
    for submit in submits:
        try:
            code = contestCodeGet(submit.nickName,submit.subid)
            log.info("get:"+ str(submit.subid))
            submit.code = code
            count += 1
        except:
            log.error("get error:"+str(subid))
            submit.code = "get error"
        submit.save()
    return count

def getCodeFixBug():
    log = logging.getLogger("log")
    log.info("Begin accode fixbug")
    count = 0
    submits = ACContest.objects.filter(code = "get error")
    for submit in submits:
        code = contestCodeGet(submit.nickName,submit.subid)
        submit.save()
        count +=1
    return count

def acTimefix(acTime):
    actime = acTime.split("+")[0]
    zone = acTime.split("+")[1]
    timestamp = time.mktime(time.strptime(actime,"%Y-%m-%d %H:%M:%S"))
    if zone=="0900":
        timestamp -= 3600
    return timestamp

def UpdateACAfterSolve():
    students = Student.objects.all()
    acIDs = []
    stuDic = {}
    for stu in students:
        if stu.acID:
            acIDs.append(stu.acID)
            stuDic[stu.acID]=stu
    contests = Contest.objects.order_by("-cdate").filter(ctype="ac")
    for ids,con in enumerate(contests):
        if ids>=10:
            break
        print(con.nickName)
        for acID in acIDs:
            datalist = getUpdateSubmitStatu(con.nickName,acID)
            for submit in datalist:
                if ACContest.objects.filter(stuNO=stuDic[acID].stuNO,subid=submit['subid'],nickName=data['nickName']).count() == 0:
                    ACContest.objects.create(stuNO=stuDic[acID].stuNO,realName=stuDic[acID].realName,ctime=submit['ctime'],nickName=data['nickName'],cname=data["contest"],
                        subid=submit['subid'],code="wating to get",task=submit['task'],statu=submit['statu'],language=submit['language'])

def getUpdateSubmitStatu(acNickName,acID):
    datalist = []
    for page in range(1,10):
        url = 'https://atcoder.jp/contests/'+str(acNickName)+'/submissions?f.Task=&f.Language=&f.Status=&f.User=' + str(acID) + '&page='+str(page)
        html = getUrlText(url)
        soup = BeautifulSoup(html,"lxml")
        table = soup.select(".panel-submission")[0].select("tbody")
        if len(table) == 0:
            return datalist
        trs = table[0].select("tr")
        for ids,tr in enumerate(trs):
            tds = tr.select('td')
            subtime = acTimefix(tds[0].text)
            task = tds[1].text
            language = tds[3].text
            statu = tds[6].text
            if len(tds)>8:
                subid = tds[9].select('a')[0]['href'].split('/')[4]
            else:
                subid = tds[7].select('a')[0]['href'].split('/')[4]
            if ACContest.objects.filter(subid=subid,nickName=acNickName).count()!=0:
                return datalist
            datalist.append({
                'ctime':subtime,
                'task':task,
                'language':language,
                'statu':statu,
                'subid':subid,
            })

def resetACContestSolveAll():
    students = Student.objects.all()
    contests = Contest.objects.filter(ctype="ac")
    after = {}
    allafter = {}
    acIDs=[]
    stuDic={}
    for stu in students:
        if stu.acID:
            acIDs.append(stu.acID)
            stuDic[stu.stuNO]=stu
            after[stu.stuNO]=0
            allafter[stu.stuNO]=0
    for con in contests:
        submits = ACContest.objects.filter(nickName=con.nickName)
        thisafter = {}
        thissolve = {}
        index = {}
        for submit in submits:
            if submit.stuNO not in thisafter:
                thisafter[submit.stuNO]=0
            if submit.stuNO not in thissolve:
                thissolve[submit.stuNO]=0
            if submit.stuNO not in index:
                index[submit.stuNO]=[]
            if submit.statu == "AC":
                if submit.task not in index[submit.stuNO]:
                    index[submit.stuNO].append(submit.task)
                    if submit.ctime > con.endtimestamp:
                        thisafter[submit.stuNO] = thisafter[submit.stuNO] + 1
                        after[submit.stuNO] = after[submit.stuNO] + 1
                    else:
                        thissolve[submit.stuNO] = thissolve[submit.stuNO] + 1
            if submit.ctime > con.endtimestamp:
                allafter[submit.stuNO] = allafter[submit.stuNO] + 1
        for stuNO in thisafter.keys():
            sc = StudentContest.objects.filter(stuNO=stuNO,nickName=con.nickName,ctype="ac")
            if len(sc)!=0:
                con = sc[0]
                con.solve = thissolve[stuNO]
                con.after = thisafter[stuNO]
                con.save()
    for stuNO in after.keys():
        sc = Student.objects.filter(stuNO=stuNO)
        if len(sc)!=0:
            stu = sc[0]
            stu.all_ac_aftersolve = allafter[stuNO]
            stu.correct_ac_aftersolve = after[stuNO]
            stu.save()

def resetACContestSolveStu(stu):
    contests = ACContest.objects.filter()
    after = 0
    allafter = 0
    endtime = {}
    cons = Contest.objects.filter(ctype="ac")
    for con in cons:
        endtime[con.nickName]= con.endtimestamp
    index ={}
    for contest in contests:
        if contest.nickName not in index:
            index[contest.nickName] = []
        if contest.task not in index[contest.nickName]:
            index[contest.nickName].append(contest.task)
            if contest.ctime > endtime[contest.nickName]:
                after = after + 1
        if contest.ctime > endtime[contest.nickName]:
            allafter = allafter + 1
    stu.all_ac_aftersolve = allafter
    stu.correct_ac_aftersolve = after
    stu.save()
        
            