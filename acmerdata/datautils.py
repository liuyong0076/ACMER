# commonly used functions to write data into database

from acmerdata import bsdata
from .models import Student, Contest, StudentContest,AddStudentqueue,CFContest,Contestforecast,ACContest
from django.db.models import Max
import logging
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import colorsys,random
import json

def setContestJoinNumbers():    #重置参赛人数
    list = Contest.objects.all()
    for l in list:
        if l.ctype=='cf' or l.ctype == 'jsk':
            sc = StudentContest.objects.filter(cname=l.cname,cid=l.cid)
        else:
            sc = StudentContest.objects.filter(cname=l.cname)
        l.cnumber = len(sc)
        l.save()

def getDivByName(contestname):  #获取div等级
    div = 0
    dic = {"Div. 1":1, "Div. 2":2, "Div. 3":3, 'Grand ':1, 'Regular':2, 'Beginner':3}
    for k,v in dic.items():
        if contestname.find(k)>=0:
            div = v
            break
    return div

def addContest(contestID,date,contest,ctype,cnumber=0,starttime=0,endtime=0):   #添加比赛
    if contestID and int(contestID)>0:
        ct = Contest.objects.filter(cid=contestID,ctype=ctype)
    else:
        ct = Contest.objects.filter(cname=contest,ctype=ctype)
    if len(ct) == 0:
        div = getDivByName(contest)
        Contest.objects.create(cid=contestID,cname=contest,cdate=date,cdiv=div,ctype=ctype,cnumber=cnumber,starttimestamp=starttime,endtimestamp=endtime)

def addStudentContest(stuNO,realname,classname,cid,cname,cdate,rank,newRating,diff,ctype,solve="no data"):    #添加学生比赛记录
    sc = StudentContest.objects.filter(stuNO=stuNO,cid=cid,cname=cname,ctype=ctype)
    if len(sc) == 0:
        cdiv = getDivByName(cname)
        StudentContest.objects.create(stuNO=stuNO,realName=realname,className=classname,
            cid=cid,cname=cname,cdate=cdate,cdiv=cdiv,rank=rank,newRating=newRating,diff=diff,ctype=ctype,solve=solve)
    else:
        sc[0].newRating = newRating
        sc[0].diff = diff  # for fix bug
        sc[0].save()

def addCFStatu(stuNO,realname,cid,cname,cfID):      #添加学生提交代码
    datalist = bsdata.getsubmitdata(cid,cfID)
    for data in datalist:
        sc = CFContest.objects.filter(subid=data['subid'])
        if len(sc) == 0 :
            cdiv = cdiv = getDivByName(cname)
            try:
                CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=data['subid'],index=data['index'],
                    cdiv = cdiv,code = data['code'],tag = data['tags'],statu = data['statu'],ctime=data['time'],language=data['language'])
            except:
                CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=data['subid'],index=data['index'],
                cdiv = cdiv,code = 'get error',tag = data['tags'],statu = data['statu'],ctime=data['time'],language=data['language'])
        elif sc[0].code == 'get error':
            op = CFContest.objects.get(subid=data['subid'])
            op.code = data['code']
            op.save()

def saveCFDataByContest():  #更新cf比赛
    students = Student.objects.all()
    cfIDList = []
    stuInfoDic = {}
    for stu in students:
        cfIDList.append(stu.cfID)
        stuInfoDic[stu.cfID] = stu
    log = logging.getLogger("log")
    max_timestamp=0
    for d in Contest.objects.filter():
        t=d.ctype
        dt=d.cdate 
        if(d.ctype=="cf"):
            timestamp=int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S") )) 
            if(max_timestamp<timestamp):
                max_timestamp=timestamp
            
    # print(existMaxCFID)
    log.info(max_timestamp)
    str = ""
    contestList = bsdata.getCFContestList(max_timestamp)
    if len(contestList) != 0:
        cfcontestsubmitupdatebycontest()
    for c in contestList:
        rankChangingList = bsdata.getCFContestRankingChange(c["cid"],cfIDList)
        if len(rankChangingList)>0:
            str += c["cname"] + ","
            addContest(c["cid"],c["cdate"],c["cname"],"cf",len(rankChangingList),c["starttime"],c["endtime"])
            for r in rankChangingList:
                stu = stuInfoDic[r["cfID"]]
                log.info("addStudentContest" + stu.realName)
                addStudentContest(stu.stuNO,stu.realName,stu.className,c["cid"],
                                    c["cname"],c["cdate"],r["rank"],r["newRating"],r["diff"],"cf")
                addCFStatu(stu.stuNO,stu.realName,c["cid"],c["cname"],r["cfID"])
                p = Student.objects.get(cfID=r["cfID"])
                p.cfRating=r["newRating"]
                k = int(p.cfTimes) + 1
                p.cfTimes = k
                p.save()
            setcontestsolve(c["cid"])
    return str

def cfcontestsubmitupdatebycontest():       #codeforces补题更新
    maxsubid = CFContest.objects.all().aggregate(Max('subid'))['subid__max']
    students = Student.objects.all()
    cfIDList = []
    strs = ''
    stuInfoDic = {}
    logger = logging.getLogger('log')
    for stu in students:
        cfIDList.append(stu.cfID)
        stuInfoDic[stu.cfID] = stu
    contestlist = Contest.objects.filter(ctype='cf').order_by("-cdate")
    lencontest = 10
    for contest in contestlist:
        if lencontest == 0:
            break
        else:
            lencontest = lencontest - 1
        logger.info(contest.cid)
        datalist = bsdata.contestsubmitgetupdate(contest.cid,cfIDList,maxsubid)
        if len(datalist)>0:
            for data in datalist:
                stu = stuInfoDic[data['cfid']]
                saveCFstatu(stu.stuNO,stu.realName,data['cid'],
                contest.cname,data['time'],data['tags'],data['statu'],data['index'],data['subid'],data['language'])        
        strs += contest.cname + ':' + str(len(datalist)) +'\n'
    context = {'str': strs }

def saveCFdataByUser(stu):  #   根据学生对象获取cf数据
    if stu.cfID:
        dataList = bsdata.getCFUserData(stu.cfID)
        stu.cfTimes = len(dataList)
        if(stu.cfTimes > 0):
            stu.cfRating = dataList[-1]["newRating"]
            for data in dataList:
                addContest(data["contestID"],data["date"],data["contest"],"cf")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data["contestID"],
                    data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"cf")
                addCFStatu(stu.stuNO,stu.realName,data["contestID"],data["contest"],stu.cfID)
        else:
            stu.cfRating = 0
    else:
        stu.cfTimes = 0
        stu.cfRating = 0
    stu.save()

def saveACData_fixbug(stu):
    pass

def getLatestCFRating_fasterVersion(StuContestList,stuNO,date):
    # sclist = StudentContest.objects.filter(cdate__startswith=date,stuNO=stuNO,ctype='cf')        
    rating = 0
    for c in StuContestList:
        if c.stuNO == stuNO and c.cdate.startswith(date) and c.ctype == 'cf':
            rating = c.newRating
    return rating

def saveACData(stu):    #   根据学生对象获取atcoder数据
    if stu.acID:
        dataList = bsdata.getACUserData(stu.acID)
        stu.acTimes = len(dataList)
        if(stu.acTimes > 0):
            for data in dataList:
                stu.acRating = dataList[-1]["newRating"]
                addContest(data["contestID"],data["date"],data["contest"],"ac")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data["contestID"],data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"ac")
        else:
            stu.acRating = 0
    else:
        stu.acTimes = 0
        stu.acRating = 0
    stu.save()

def saveNCData(stu):    #   根据学生对象获取newcoder数据
    if stu.ncID:
        dataList=bsdata.getNCUserData(stu.ncID)
        stu.ncTimes = len(dataList)
        if stu.ncTimes > 0 :
            nrk = True
            for data in dataList:
                if nrk:
                    if data['newrating'] != 0:
                        stu.ncRating = data['newrating']
                        nrk=False
                addContest(data['contestID'],data["date"],data["contest"],"nc")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data['contestID'],data["contest"],data["date"],data["rank"],data["newrating"],data["diff"],"nc",data["acnum"])
        else:
            stu.ncRating = 0
    else:
        stu.ncTimes=0
    stu.save()

def contestdatasolve(cname=0,stuNO=0,cid=-1):      #比赛数据展示规范函数,用于过滤数据并输出字典列表供展示
    if(cname):
        if cid !=-1:
            list = StudentContest.objects.order_by('rank').filter(cname=cname,cid=cid)
        else:
            list = StudentContest.objects.order_by('rank').filter(cname=cname)
    if(stuNO):
        list = StudentContest.objects.order_by('-cdate').filter(stuNO=stuNO)
    data =[]
    for i in list:
        if i.diff[0] != '-':
            difftype = 1
            if i.diff[0]!='+':
                diff = ''.join(['+',i.diff])
            else:
                diff = i.diff
        else:
            difftype = 0
            diff = i.diff
        data.append({
            'id':i.id,
            'cname':i.cname,
            'cdate':i.cdate,
            'stuNO':i.stuNO,
            'className':i.className,
            'rank':i.rank,
            'realname':i.realName,
            'newRating':i.newRating,
            'diff':diff,
            'solve':i.solve,
            'difftype':difftype,
            'type':i.ctype,
            'after':i.aftersolve,
        })
    return data

def saveCFstatu(stuNO,realname,cid,cname,time,tags,statu,index,subid,language):      #添加提交记录
    print(subid)
    t=0
    while True:
        try:
            t=t+1
            sc = CFContest.objects.filter(subid=subid)
            if len(sc)==0 or sc.code=='get error':
                code = bsdata.submitdetail(cid,subid)
                break
            else:
                code = sc[0].code
                break
        except:
            if t>5 :
                code='get error'
                break
    cdiv = cdiv = getDivByName(cname)
    if CFContest.objects.filter(subid=subid).count()==0:
        try:
            CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=subid,index=index,
                cdiv = cdiv,code = code,tag = tags,statu = statu,ctime=time,language=language)
        except:
            CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=subid,index=index,
                cdiv = cdiv,code = 'get error',tag = tags,statu = statu,ctime=time,language=language)

def cfsolvereset(stuNO,cid):    #重置解题数量
    submits = CFContest.objects.filter(stuNO=stuNO,cid=cid)
    endtime = Contest.objects.get(cid=cid,ctype='cf')
    ok = []
    solve = 0
    aftersolve= 0 
    for submit in submits:
        if submit.statu == 'OK' and ok.count(submit.index)==0 :
            if submit.ctime > endtime:
                aftersolve=aftersolve+1
            else:
                solve = solve + 1
            ok.append(submit.index)
    contest = StudentContest.objects.get(stuNO=stuNO,cid=cid,ctype='cf')
    contest.solve = str(solve)
    contest.aftersolve = str(aftersolve)
    contest.save()

def cftimesreset(): #重置参赛次数
    students = Student.objects.all()
    for stu in students:
        contests = StudentContest.objects.filter(ctype='cf',stuNO=stu.stuNO)
        stu.cfTimes = len(contests)
        stu.save()

def addforecastlist(starttime,cname,during,link,ctype,cid=0):   #添加比赛预告
    if ctype == 'cf':
        sc = Contestforecast.objects.filter(cid=cid)
    else:
        sc = Contestforecast.objects.filter(cname=cname)
    if len(sc)==0:
        Contestforecast.objects.create(ctype=ctype,link=link,cname=cname,starttime=starttime,during=during,cid=cid)
    else:
        a=sc[0]
        a.ctype=ctype
        a.link=link
        a.cname=cname
        a.starttime=starttime
        a.during=during
        a.save()
    
def timestamptotime(ts):    #时间戳转换时间间隔
    hour = ts/3600
    minute = (ts%3600)/60
    time = '%02d:%02d' % (hour,minute)
    return time

def cftimeStandard():   #cf时间标准化
    cfcontest = Contest.objects.filter(ctype='cf')
    cflist=[]
    strs=''
    for contest in cfcontest:
        cflist.append(contest.cid)
    timelist = bsdata.getcftimestamp(cflist)
    for contest in timelist:
        strs += str(contest['cid']) +'  &  '
        con = Contest.objects.get(cid = contest['cid'])
        con.starttimestamp = contest['starttime']
        con.cdate = time.strftime("%Y-%m-%d %H:%M:%S",(time.localtime(int(contest['starttime']))))
        con.endtimestamp = contest['endtime']
        con.save()
    return strs

def setcontestsolve(cid):       #比赛解题数重置
    stucons = StudentContest.objects.filter(cid=cid,ctype='cf')
    for stucon in stucons:
        submits = CFContest.objects.filter(cid=cid,stuNO=stucon.stuNO)
        contest = Contest.objects.get(cid=cid,ctype='cf')
        solve = 0
        after = 0
        index = []
        for submit in submits:
            if submit.statu=='OK' and submit.index not in index :
                if submit.ctime > contest.endtimestamp:
                    after = after + 1
                else:
                    solve = solve + 1
                index.append(submit.index)
        stucon.solve = str(solve)
        stucon.aftersolve = str(after)
        stucon.save()

def setaftersolve(stu):     #补题数重置
    allsub = 0
    correctsub = 0
    op=[]
    StuCFcontests = CFContest.objects.filter(stuNO=stu.stuNO)
    for CFcontest in StuCFcontests:
        if CFcontest.cid not in op :
            op.append(CFcontest.cid)
    for con in op:
        cont = Contest.objects.get(cid = con,ctype='cf')
        submitlen = len(CFContest.objects.filter(cid=con,stuNO=stu.stuNO,ctime__gt=cont.endtimestamp))
        correctlen = correctanslen(stu,con)
        allsub += int(submitlen)
        correctsub += int(correctlen)
    stu.all_cf_aftersolve= allsub
    stu.correct_cf_aftersolve = correctsub
    stu.save()

def correctanslen(stu,con):
    ind=[]
    solve=0
    cont = Contest.objects.get(cid = con,ctype='cf')
    submits = CFContest.objects.filter(cid=con,stuNO=stu.stuNO,ctime__gt=cont.endtimestamp,statu='OK')
    for submit in submits:
        if submit.index not in ind:
            ind.append(submit.index)
            solve=solve+1
    return solve

def addprizet(request):     #添加比赛获奖记录，未完全开发
    if request.method=="POST":
        formt = addprize(request.POST)
        if formt.is_valid():
            form = formt.clean()
            AddContestprize.objects.create(name = form['name'],className=form['classname'],stuyear=form['year'],
            stuNO=form['stuNO'],cname=form['contestname'],cyear=form['cyear'],clevel=form['level'],prize=form['prize'],exe=False)
            forms = addprize(initial={"name":form['name'],'classname':form['classname'],'year':form['year'],'stuNO':form['stuNO']})
            return render(request,'addprize.html',{'form': forms})
    else:
        formt = addprize()
    return render(request,'addprize.html',{'form': formt})

def getstumonthly(stu,year,month):      #按月获取学生数据,效率过低暂时弃用
    starttime = ("%d-%02d-01 00:00:00") % (year, month)
    endtime = ("%d-%02d-31 23:59:59") % (year, month)
    contests = StudentContest.objects.filter(cdate__range=(starttime,endtime),stuNO=stu.stuNO)
    monthdata = {
                'year':year,
                'month':"%02d" % (month),
                'cf':0,
                'cfdiff':0,
                'cfp':0,
                'cfpp':0,
                'ac':0,
                'acdiff':0,
                'jsk':0,
                'jskp':0,
                'nc':0,
                'ncp':0,
                'score':0  # 比赛场次*20 + 解题数*5 + rating diff
            }
    for con in contests:
        if con.ctype == 'cf':
            monthdata['cf'] += 1
            monthdata['cfp'] += int(con.solve)
            monthdata['cfdiff'] += int(con.diff)
        elif con.ctype == 'ac':
            monthdata['ac'] += 1
            try:
                monthdata['acdiff'] += int(con.diff)
            except:
                pass
        elif con.ctype == 'jsk':
            monthdata['jsk'] += 1
            monthdata['jskp'] += int(con.solve)
        elif con.ctype == 'nc':
            monthdata['nc'] += 1
            monthdata['ncp'] += int(con.solve.split('/')[0])
    monthdata['cfpp']=getstudentmonthsolve(stu,year,month)
    monthdata['score'] = (monthdata['cf']+monthdata['ac']+monthdata['jsk']+monthdata['nc']) * 20 + (monthdata['cfp']+monthdata['cfpp']+monthdata['jskp']+monthdata['ncp']) * 5 + (monthdata['cfdiff']+monthdata['acdiff'])
    return monthdata

def spmonth(datalist,year,mtype):       #特殊时间段获取,暂时无使用
    monthdata = {
                'year':year,
                'month':mtype,
                'cf':0,
                'cfdiff':0,
                'cfp':0,
                'cfpp':0,
                'ac':0,
                'acdiff':0,
                'jsk':0,
                'jskp':0,
                'nc':0,
                'ncp':0,
                'score':0  # 比赛场次*20 + 解题数*5 + rating diff
            }
    ls = []
    if mtype == 'S1':
        rgs = 1
        rge = 4
    elif mtype == 'S2':
        rgs = 4
        rge = 7
    elif mtype == 'S3':
        rgs = 7
        rge = 10
    elif mtype == 'S4':
        rgs = 10
        rge = 13
    elif mtype == 'H1':
        rgs = 1
        rge = 7
    elif mtype == 'H2':
        rgs = 7
        rge = 13
    elif mtype == 'ALL':
        rgs = 1
        rge = 13
    for data in datalist:
        try:
            if data['year'] == year and int(data['month']) in range(rgs,rge):
                ls.append(data)
        except:
            pass
    for data in ls:
        monthdata['cf'] += data['cf']
        monthdata['cfdiff'] += data['cfdiff']
        monthdata['cfp'] += data['cfp']
        monthdata['cfpp'] += data['cfpp']
        monthdata['ac'] += data['ac']
        monthdata['acdiff'] += data['acdiff']
        monthdata['jsk'] += data['jsk']
        monthdata['jskp'] += data['jskp']
        monthdata['nc'] += data['nc']
        monthdata['ncp'] += data['ncp']
        monthdata['score'] += data['score']
    return monthdata

def getstudentmonthsolve(stu,year,month):       #按月获取学生补题数据,效率过低暂时弃用
    starttime = time.mktime(time.strptime(("%d-%02d-01 00:00:00") % (year, month),"%Y-%m-%d %H:%M:%S"))
    if month == 12:
        endtime = time.mktime(time.strptime(("%d-01-01 00:00:00") % (year+1),"%Y-%m-%d %H:%M:%S"))
    else:
        endtime = time.mktime(time.strptime(("%d-%02d-01 00:00:00") % (year, month+1),"%Y-%m-%d %H:%M:%S"))
    contests = CFContest.objects.filter(stuNO = stu.stuNO,statu='OK',ctime__range=(starttime,endtime))
    end = {}
    index = {}
    aftersolve = 0
    for contest in contests:
        if not contest.cid in index :
            index[contest.cid]=[]
            end[contest.cid]=Contest.objects.get(cid=contest.cid,ctype='cf').endtimestamp
        if contest.index not in index[contest.cid] and contest.ctime>end[contest.cid]:
            index[contest.cid].append(contest.index)
            aftersolve=aftersolve+1
    return aftersolve

def getbigaftersolve(y1,m1,y2,m2,source='cf'):      #大范围获取全部学生月补题数据，返回一个字典,对应学生号和解题数
    if m2==13:
        m2=1
        y2=y2+1
    starttime = time.mktime(time.strptime(("%d-%02d-01 00:00:00") % (y1, m1),"%Y-%m-%d %H:%M:%S"))
    endtime = time.mktime(time.strptime(("%d-%02d-01 00:00:00") % (y2, m2),"%Y-%m-%d %H:%M:%S"))
    endt = {}
    if source =='cf':
        contests = CFContest.objects.filter(statu='OK',ctime__range=(starttime,endtime))
    elif source == 'ac':
        contests = ACContest.objects.filter(statu='AC',ctime__range=(starttime,endtime))

    # logger = logging.getLogger('log')
    # logger.info("source=%s, size of contests=%d" % (source,len(contests)))


    aftersolve={}
    end = {}
    index = {}
    if source == 'cf':
        for contest in contests:
            if not contest.stuNO in aftersolve:
                aftersolve[contest.stuNO]=0
            if not contest.cid in index :
                index[contest.cid]={}
            if not contest.stuNO in index[contest.cid]:
                index[contest.cid][contest.stuNO] = []
            if contest.index not in index[contest.cid][contest.stuNO]:
                index[contest.cid][contest.stuNO].append(contest.index)
                aftersolve[contest.stuNO] = aftersolve[contest.stuNO] + 1
    elif source == 'ac':
        for contest in contests:
            if not contest.stuNO in aftersolve:
                aftersolve[contest.stuNO]=0
            if not contest.cname in index :
                index[contest.cname]={}
            if not contest.stuNO in index[contest.cname]:
                index[contest.cname][contest.stuNO] = []
            if contest.task not in index[contest.cname][contest.stuNO]:
                index[contest.cname][contest.stuNO].append(contest.task)
                aftersolve[contest.stuNO] = aftersolve[contest.stuNO] + 1

    # if source == 'ac':
    #     logger.info(aftersolve)
    
    return aftersolve

def getbigstudentmonth(stu,y1,m1,y2,m2):    #大范围获取学生数据(y1,m1)代表数据起始年月,(y2,m2)代表截止年月,返回记录着学生从起始到截止年月的每月数据的字典列表
    if m2==13:
        m2=1
        y2=y2+1
    starttime = ("%d-%02d-01 00:00:00") % (y1, m1)
    endtime = ("%d-%02d-01 00:00:00") % (y2, m2)
    datas = StudentContest.objects.filter(stuNO=stu.stuNO,cdate__range=(starttime,endtime))
    s={}
    for con in datas:
        date = con.cdate[0:7]
        year = date.split("-")[0]
        month = date.split("-")[1]
        if year not in s:
            s[year]={}
        if month not in s[year]:
            s[year][month]={
                'year':year,
                'month':month,
                'date':year+'-'+month,
                'cf':0,
                'cfdiff':0,
                'cfp':0,
                'cfpp':0,
                'ac':0,
                'acp':0,
                'acpp':0,
                'acdiff':0,
                'jsk':0,
                'jskp':0,
                'nc':0,
                'ncp':0,
                'score':0  # 比赛场次*20 + 解题数*5 + rating diff
            }
        if con.ctype == 'cf':
            s[year][month]['cf'] += 1
            s[year][month]['cfp'] += int(con.solve)
            s[year][month]['cfdiff'] += int(con.diff)
        elif con.ctype == 'ac':
            s[year][month]['ac'] += 1
            s[year][month]['acp'] += int(con.solve)
            try:
                s[year][month]['acdiff'] += int(con.diff)
            except:
                pass
        elif con.ctype == 'jsk':
            s[year][month]['jsk'] += 1
            s[year][month]['jskp'] += int(con.solve)
        elif con.ctype == 'nc':
            s[year][month]['nc'] += 1
            s[year][month]['ncp'] += int(con.solve.split('/')[0])
    start=time.mktime(time.strptime(starttime,"%Y-%m-%d %H:%M:%S"))
    end = time.mktime(time.strptime(endtime,"%Y-%m-%d %H:%M:%S"))
    sc = CFContest.objects.filter(stuNO=stu.stuNO,ctime__range=(start,end),statu='OK')
    asc = ACContest.objects.filter(stuNO=stu.stuNO,ctime__range=(start,end),statu='AC')
    index = {}
    for data in sc:
        date=time.localtime(data.ctime)
        year = date.tm_year
        month = date.tm_mon
        if data.cid not in index:
            index[data.cid]=[]
        if data.index not in index[data.cid]:
            s[str(year)][("%02d")%(month)]['cfpp'] += 1
            index[data.cid].append(data.index)
    index = {}
    for data in asc:
        date=time.localtime(data.ctime)
        year = date.tm_year
        month = date.tm_mon
        if data.nickName not in index:
            index[data.nickName]=[]
        if data.task not in index[data.nickName]:
            s[str(year)][("%02d")%(month)]['acpp'] += 1
            index[data.nickName].append(data.task)
    datalist = []
    for ykey in s.keys():
        for mkey in s[ykey].keys():
            s[ykey][mkey]['cfpp']=s[ykey][mkey]['cfpp']-s[ykey][mkey]['cfp']
            s[ykey][mkey]['acpp']=s[ykey][mkey]['acpp']-s[ykey][mkey]['acp']
            s[ykey][mkey]['score'] = (s[ykey][mkey]['cf']+s[ykey][mkey]['ac']+s[ykey][mkey]['jsk']+s[ykey][mkey]['nc']) * 20 + (s[ykey][mkey]['cfp']+s[ykey][mkey]['cfpp']+s[ykey][mkey]['jskp']+s[ykey][mkey]['ncp']+s[ykey][mkey]['acp']+s[ykey][mkey]['acpp']) * 5 + (s[ykey][mkey]['cfdiff']+s[ykey][mkey]['acdiff'])
            datalist.append(s[ykey][mkey])
    datalist.sort(key=lambda x: x['date'],reverse=True)
    return datalist

def cfstatureset():
    datas = CFContest.objects.all()
    sub = []
    dells = []
    for data in datas:
        if data.subid not in sub:
            sub.append(data.subid)
        else:
            dells.append(data.id)
    for idtd in dells:
        CFContest.objects.filter(id = idtd).delete()


#color
def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step
 
    return hls_colors
 
def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append("rgba("+str(r)+','+str(g)+","+str(b))
    return rgb_colors
#colorend