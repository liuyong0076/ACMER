from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import loader
from acmerdata import bsdata, datautils ,jsk,atcoder,CodeforcesQuestion
from acmerdata import CodeforcesQuestion as CQ
from django.views.decorators.cache import cache_page
import logging
import lxml
from .models import Student, Contest, StudentContest,AddStudentqueue,studentgroup,CFContest,Contestforecast,AddContestprize,ACContest,CodeforcesQuestion
from .forms import Addstudent,Addgroup,addprize
import time,datetime,json
import re
import random
import markdown
from django.db.models import Max
import operator
import os


# Create your views here.
#数据展示模块
def spider(request):    #spider页面接口
    context = {} #{'studentlist': studentlist}
    return render(request, 'spider.html', context)

def contact(request):   #contact页面接口
    context = {} #{'studentlist': studentlist}
    return render(request, 'contact.html', context)

def fixbug(request):
    # fix the diff is 0 of ac data
    studentlist = Student.objects.all()
    str = ""
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data")
        datautils.saveACData_fixbug(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data")
    datautils.setContestJoinNumbers()
    context = {'str': str}
    return render(request, 'fixbug.html', context)

@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def index(request):   #入口页面
    studentlist = Student.objects.order_by("-cfRating").all()
    retire = []
    data = []
    active = []
    for stu in studentlist:
        data.append({
            'stuNO':stu.stuNO,
            'realName':stu.realName,
            'className':stu.className,
            'year':stu.year,
            'cfRating':stu.cfRating,
            'cfTimes':stu.cfTimes,
            'CFafter':str(stu.correct_cf_aftersolve) + '/' + str(stu.all_cf_aftersolve),
            'ACafter':str(stu.correct_ac_aftersolve) + '/' + str(stu.all_ac_aftersolve),
            'acRating':stu.acRating,
            'acTimes':stu.acTimes,
            'ncTimes':stu.ncTimes,
            'ncRating':stu.ncRating,
            'jskTimes':stu.jskTimes,
            'school':stu.school,
            'sex':stu.sex,
        })
        if stu.isActive == 1:
            active.append({
            'stuNO':stu.stuNO,
            'realName':stu.realName,
            'className':stu.className,
            'year':stu.year,
            'cfRating':stu.cfRating,
            'cfTimes':stu.cfTimes,
            'CFafter':str(stu.correct_cf_aftersolve) + '/' + str(stu.all_cf_aftersolve),
            'ACafter':str(stu.correct_ac_aftersolve) + '/' + str(stu.all_ac_aftersolve),
            'acRating':stu.acRating,
            'acTimes':stu.acTimes,
            'ncTimes':stu.ncTimes,
            'ncRating':stu.ncRating,
            'jskTimes':stu.jskTimes,
            'school':stu.school,
            'sex':stu.sex,
            })
        if stu.isActive == 0:
            retire.append({
                'stuNO':stu.stuNO,
                'realName':stu.realName,
                'className':stu.className,
                'year':stu.year,
                'cfRating':stu.cfRating,
                'cfTimes':stu.cfTimes,
                'CFafter':str(stu.correct_cf_aftersolve) + '/' + str(stu.all_cf_aftersolve),
                'ACafter':str(stu.correct_ac_aftersolve) + '/' + str(stu.all_ac_aftersolve),
                'acRating':stu.acRating,
                'acTimes':stu.acTimes,
                'ncTimes':stu.ncTimes,
                'ncRating':stu.ncRating,
                'jskTimes':stu.jskTimes,
                'school':stu.school,
                'sex':stu.sex,
            })
    context = {'studentlist': data,"active":active,"retire":retire}
    return render(request, 'students.html', context)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def contests(request):  #比赛页面
    contestlist = Contest.objects.order_by('-cdate').all()
    for c in contestlist:
        c.cdate = c.cdate[0:16]
        if len(c.cname) > 50:
            c.cname = c.cname[0:50] + "..."
    times = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    context = {'contestlist': contestlist,"time":times}
    return render(request, 'contests.html', context)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def contest(request, contest_id=-1,studentcontest_id=-1):   #比赛详情,分别从学生页面与比赛页面进入
    if contest_id > 0:
        ct = Contest.objects.filter(id=contest_id)  
    else:
        ct = StudentContest.objects.filter(id=studentcontest_id)  
    logging.info("len(ct)"+str(len(ct)))
    list = []
    if len(ct)>0:
        #list = StudentContest.objects.order_by('rank').filter(cname=ct[0].cname)
        if ct[0].ctype == 'cf' or ct[0].ctype == 'jsk':
            cid = ct[0].cid
            list = datautils.contestdatasolve(cname=ct[0].cname,cid=ct[0].cid)
        else:
            list = datautils.contestdatasolve(cname=ct[0].cname)
            cid = ''
    context = {'list': list,"cname":ct[0].cname,"cdate":ct[0].cdate,'cid':cid,'nickName':ct[0].nickName}
    return render(request, 'contest.html', context)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def student(request, stuNO):
    #list = StudentContest.objects.order_by('-cdate').filter(stuNO=stuNO)
    data = datautils.contestdatasolve(stuNO=stuNO)
    stu = Student.objects.get(stuNO=stuNO)
    classname, realname= '',''
    classname,realname,cfID,acID,ncID,jskID = stu.className, stu.realName, stu.cfID, stu.acID, stu.ncID,stu.jskID
    context = {'list': data,'classname':classname, 'realname':realname,'cfID':cfID,'acID':acID,'ncID':ncID,'jskID':jskID}

    return render(request, 'student.html', context)
#end数据展示模块
#数据爬取模块
# update cf data by contest, start from not zero
def updateCFDataByContest(request):
    str = "CF Data, successed list:"
    str += datautils.saveCFDataByContest()
    datautils.cftimesreset()#供测试阶段调试使用，正式上线请将cftimes调整至准确再使用递增方法
    context = {'str': str}
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['cfContestUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    return render(request, 'spiderResults.html', context)   

# update cf data by all user, start from zero
def updateACDataByContest(request):
    studentlist = Student.objects.all()
    str = "AC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data Incrementally")
        atcoder.saveACDataIncrementally(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data Incrementally")
    datautils.setContestJoinNumbers()
    context = {'str': str}
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    return render(request, 'spiderResults.html', context)

def getCFData(request):     #全量抓取codeforce数据；注意根据网络情况可能极慢！！！
    studentlist = Student.objects.all()
    str = "CF Data, successed list:"
    log = logging.getLogger("log")
    log.info("getCFData start")
    count = 0
    for stu in studentlist:
        count += 1
        text = "getCFData start %d/%d: %s" % (count,len(studentlist),stu.realName)
        log.info(text)
        datautils.saveCFdataByUser(stu)
        str += stu.realName + ","
        log.info("getCFData end:" + stu.realName)
    context = {'str': str}
    strs=datautils.cftimeStandard()
    datautils.setContestJoinNumbers()
    contests = Contest.objects.filter(ctype='cf')
    for contest in contests:
        datautils.setcontestsolve(contest.cid)
    return render(request, 'spiderResults.html', context)

def getACCode(request,utype):
    if utype == 'fixbug':
        count = atcoder.getCodeFixBug()
    elif utype == 'update':
        count = atcoder.getCodeUpdate()
    else:
        return render(request, 'spiderResults.html', {'str': "Unknown Update Type"})
    message = "get code success num :"+ str(count)
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acCodeUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    return render(request, 'spiderResults.html', {'str': message})
def getACData(request):    #手动抓取atcoder数据
    studentlist = Student.objects.all()
    str = "AC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data")
        atcoder.saveACDataAll(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data")
    datautils.setContestJoinNumbers()
    context = {'str': str}
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    return render(request, 'spiderResults.html', context)

def updateACData(request):
    studentlist = Student.objects.all()
    str = "AC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data")
        atcoder.saveACDataIncrementally(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data")
    datautils.setContestJoinNumbers()
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    context = {'str': str}
    return render(request, 'spiderResults.html', context)


def getNCData(request):    #手动抓取newcoder数据；受工具限制较慢
    studentlist = Student.objects.all()
    str = "NC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start nc data")
        datautils.saveNCData(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end nc data")
    context = {'str': str}
    datautils.setContestJoinNumbers()
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['ncUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    return render(request, 'spiderResults.html', context)
#end数据爬取模块
#学生信息修改模块
def Addstudentdata(request):
    massage =""
    if request.method == 'POST':
        formt = Addstudent(request.POST)
        if formt.is_valid():
            print(formt.clean())
            c = formt.clean()
            if c['atype']=='update':
                exist = Student.objects.filter(stuNO=c['stuNO'])
                if len(exist) == 0:
                    massage = "无此学号,请检查"
                    return render(request,'addstudent.html',{'form': formt,'massage':massage})
            acck=bsdata.cheakacID(str(c['acID']))
            cfck=bsdata.cheakcfID(str(c['cfID']))
            AddStudentqueue.objects.create(atype=c['atype'],stuNO=c['stuNO'],realName=c['realName'],sex=c['sex'],className=c['className'],school=c['school'],year=c['year'],jskID=c['jskID'],
            acID=c['acID'],accheck=acck,cfID=c['cfID'],cfcheck=cfck,vjID=c['vjID'],ncID=c['ncID'],execution_statu=False,request_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            formt=Addstudent()
            massage = "申请成功，请等待审核"
            return render(request,'addstudent.html',{'form': formt,'massage':massage})
    else:
        formt = Addstudent()
    return render(request,'addstudent.html',{'form': formt,'massage':massage})

def updatestudentlist(request):     #更新学生名单函数,对后台审核操作为accept的学生进行添加,同时具有更新功能,用if分支来进行判断
    students = []
    for s in AddStudentqueue.objects.all():
        if s.execution_statu == False and str(s.execution) != "None":       #判断该操作是否以及执行以及是否已经通过审核
            if s.execution == True:     #判断是否通过
                if s.atype == 'update':     #判断是否为更新
                    a = Student.objects.get(stuNO=s.stuNO)
                    if s.acID!='':
                        a.acID=s.acID
                        atcoder.saveACDataAll(a)
                        atcoder.resetACContestSolveStu(a)
                    if s.cfID!='':
                        a.cfID=s.cfID
                        datautils.saveCFdataByUser(a)
                        students.append(a)
                    if s.ncID!='':
                        a.ncID=s.ncID
                        datautils.saveNCData(a)
                    if s.vjID!='':
                        a.vjID=s.vjID
                    if s.jskID!='':
                        a.jskID = s.jskID
                    if s.realName!='':
                        a.realName=s.realName
                    if s.className!='':
                        a.className=s.className
                    if s.school != '':
                        a.school=s.school
                    if s.year != '':
                        a.year=int(s.year)
                    if s.sex != '':
                        a.sex = s.sex
                    a.save()
                elif s.atype=='create':     #判断是否为创建
                    if Student.objects.filter(stuNO=s.stuNO,realName=s.realName).count()!=0:
                        context = {"str":"已有重复数据:"+s.stuNO+"-"+s.realName+"-"+s.className+"-"+s.school}
                        return render(request,'spiderResults.html',context)
                    Student.objects.create(
                    stuNO=s.stuNO,realName=s.realName,className=s.className,school=s.school,sex=s.sex,
                    year=int(s.year),acID=s.acID,cfID=s.cfID,vjID=s.vjID,ncID=s.ncID,jskID = s.jskID
                    )
                    a = Student.objects.get(stuNO=s.stuNO,realName=s.realName,className=s.className,school=s.school)
                    datautils.saveCFdataByUser(a)
                    atcoder.saveACDataAll(a)
                    datautils.saveNCData(a)
                    jsk.getjskdata(a)
                    students.append(a)
            s.execution_statu=True      #设置
            s.execution_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            s.save()
    contests = Contest.objects.filter(ctype='cf')       #重置cf比赛解题数
    for contest in contests:
        datautils.setcontestsolve(contest.cid)
    for stu in students:
        datautils.setaftersolve(stu)       #重置补题人数
    datautils.setContestJoinNumbers()   #重置比赛人数
    studentlist = AddStudentqueue.objects.order_by("-request_time").all()
    context = {'studentlist': studentlist}
    return render(request, 'addstudentslist.html', context)
#end学生信息修改模块
def addstatu(request):      #添加详情页面函数
    studentlist = AddStudentqueue.objects.order_by("-request_time").all()
    context = {'studentlist': studentlist}
    return render(request, 'addstudentslist.html', context)

#end比较组展示模块
#代码及解题数模块
def cfcontestsubmit(request,cid):   #比赛提交记录视图函数,传入cf比赛id进行查询
    contest = Contest.objects.get(cid=cid)
    cname = contest.cname
    cdate = contest.cdate
    list = CFContest.objects.order_by("-subid").filter(cid=cid)
    data=[]
    for submit in list:
        data.append({
            'stuNO':submit.stuNO,
            'realName':submit.realName,
            'subid':submit.subid,
            'index':submit.index,
            'tag':submit.tag,
            'statu':submit.statu,
            'language':submit.language,
            'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
        })
    context = {
        'cname':cname,
        'cdate':cdate,
        'list':data,
    }
    return render(request,"cfcontestsubmit.html",context)

def acContestSubmit(request,nickName):
    contest = Contest.objects.get(nickName=nickName)
    cname = contest.cname
    cdate = contest.cdate
    list = ACContest.objects.order_by("-subid").filter(nickName=nickName)
    data=[]
    for submit in list:
        data.append({
            'stuNO':submit.stuNO,
            'realName':submit.realName,
            'subid':submit.subid,
            'task':submit.task,
            'language':submit.language,
            'statu':submit.statu,
            'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
        })
    context = {
        'cname':cname,
        'cdate':cdate,
        'list':data,
        'nickName':nickName,
    }
    return render(request,"acContestSubmit.html",context)

def viewACCode(request,submitID):
    acct = ACContest.objects.get(subid=submitID)
    name = acct.realName
    statu = acct.statu
    task = acct.task
    subid = acct.subid
    language = "c++"
    if "Py" in acct.language:
        language="python"
    elif "Java" in acct.language:
        language="java"
    code = "```"+language+"\n"+ acct.code +"\n```"
    print(code)
    code = markdown.markdown(code,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    context={
        'code':code,
        'name':name,
        'index':task,
        'subid':subid,
        'statu':statu,
    }
    return render(request,"codeshow.html",context)
    
def afterSolveAC(request,stuNO):
    op=[]
    StuACcontests = ACContest.objects.filter(stuNO=stuNO)
    for ACcontest in StuACcontests:
        if ACcontest.nickName not in op :
            op.append(ACcontest.nickName)
    data = []
    for contest in op:
        con = Contest.objects.get(nickName=contest,ctype='ac')
        submits = ACContest.objects.filter(nickName=contest,stuNO=stuNO,ctime__gt=con.endtimestamp)
        for submit in submits:
            data.append({
                'stuNO':submit.stuNO,
                'realName':submit.realName,
                'contestname':con.cname,
                'subid':submit.subid,
                'index':submit.task,
                'language':submit.language,
                'statu':submit.statu,
                'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
            })
    context = {
        'name':Student.objects.get(stuNO=stuNO).realName,
        'list':data,
    }
    return render(request,"ACaftersubmit.html",context)
def viewcode(request,submitid):     #代码展示视图函数,传入cf提交代码展示学生代码页面
    cfct = CFContest.objects.get(subid=submitid)
    name = cfct.realName
    statu = cfct.statu
    index = cfct.index
    subid = cfct.subid
    language = "c++"
    if "Py" in cfct.language:
        language="python"
    elif "Java" in cfct.language:
        language="java"
    code = "```"+language+"\n"+ cfct.code +"\n```"
    code = markdown.markdown(code,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    context={
        'code':code,
        'name':name,
        'index':index,
        'subid':subid,
        'statu':statu,
    }
    return render(request,"codeshow.html",context)
    
def fixcodeerrorforinternetproblem(request):    #此视图函数用于补正由于网络问题出现的get error代码，已成功实现
    list = CFContest.objects.filter(code='get error')
    for i in list:
        print(str(i.subid))
        try:
            code = bsdata.submitdetail(i.cid,i.subid)
            i.code=code
            i.save()
            continue
        except:
            print('error')
    context = {'str': 'str'}
    return render(request, 'spiderResults.html', context)

def fixcodeerrorforlanguageerror(request): #此视图函数用于尝试修复cf乱码问题，但没有成功
    list = CFContest.objects.filter(code='get error')
    for i in list:
        print(str(i.subid))
        try:
            code = bsdata.submitdetail(i.cid,i.subid)
            code = str(code.encode('UTF-8'))
            Ruler = "(\/\*(\s|.)*?\*\/)|(\/\/.*)"
            code = re.sub(Ruler,'',code)
            i.code=code
            i.save()
            continue
        except:
            print('error')
    context = {'str': 'str'}
    return render(request, 'spiderResults.html', context)  

def cfcontestsubmitupdatebycontest(request): #此视图函数用于更新codeforce补题数
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
                datautils.saveCFstatu(stu.stuNO,stu.realName,data['cid'],
                contest.cname,data['time'],data['tags'],data['statu'],data['index'],data['subid'])        
        strs += contest.cname + ':' + str(len(datalist)) +'\n'
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def updateforecastlist(request):    #此视图函数用于增量更新比赛预告,过期预告会自动删除,但官方主动删除的比赛会保留
    ntime = time.time()
    ttime = ntime - 172800
    strs = ''
    passCons = Contestforecast.objects.filter(starttime__lte=ntime,ctype = "cf")
    for passcon in passCons:
        passcon.link = "https://codeforces.com/api/contest.ratingChanges?contestId=" + str(passcon.cid)
        passcon.save()
    Contestforecast.objects.filter(starttime__lte=ttime).delete()
    cfdatalist = bsdata.cfforecastget()
    ncdatelist = bsdata.ncforecastget()
    acdatalist = bsdata.acforecastget()
    for data in cfdatalist:
        strs += data['contestname'] +','
        datautils.addforecastlist(data['starttime'],data['contestname'],data['during'],'','cf',data['cid'])
    for data in acdatalist:
        strs += data['contestname'] +','
        datautils.addforecastlist(data['starttime'],data['contestname'],data['during'],data['link'],'ac')
    for data in ncdatelist:
        strs += data['contestname'] +','
        datautils.addforecastlist(data['starttime'],data['contestname'],data['during'],data['link'],'nc')
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def contestforecast(request):       #用于提供比赛预告
    ac = Contestforecast.objects.filter(ctype='ac').order_by("starttime")
    nc = Contestforecast.objects.filter(ctype='nc').order_by("starttime")
    cf = Contestforecast.objects.filter(ctype='cf').order_by("starttime")
    cflist=[]
    nclist=[]
    aclist=[]
    for contest in nc:
        nclist.append({
            'cname':contest.cname,
            'starttime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(contest.starttime)),
            'link':contest.link,
            'during':datautils.timestamptotime(int(contest.during)),
        })
    for contest in cf:
        cflist.append({
            'cname':contest.cname,
            'starttime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(contest.starttime)),
            'during':datautils.timestamptotime(int(contest.during)),
            'link':contest.link,
        })
    for contest in ac:
        aclist.append({
            'cname':contest.cname,
            'starttime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(contest.starttime)),
            'during':contest.during,
            'link':contest.link,
        })
    context = {'aclist': aclist,'nclist':nclist,'cflist':cflist }
    return render(request,'forecast.html',context)

def Standardizecftime(request):     #用于手动标准化cf比赛时间
    strs = datautils.cftimeStandard()
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def setallcontestsolve(request):    #用于手动标准化cf解题数量
    contests = Contest.objects.filter(ctype='cf')
    strs = ''
    for contest in contests:
        strs += contest.cname +' \ '
        datautils.setcontestsolve(contest.cid)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def aftersolve(request,stuNO):      #展示学生补题数
    op=[]
    StuCFcontests = CFContest.objects.filter(stuNO=stuNO)
    for CFcontest in StuCFcontests:
        if CFcontest.cid not in op :
            op.append(CFcontest.cid)
    data = []
    for contest in op:
        con = Contest.objects.get(cid=contest,ctype='cf')
        submits = CFContest.objects.filter(cid=contest,stuNO=stuNO,ctime__gt=con.endtimestamp)
        for submit in submits:
            data.append({
                'stuNO':submit.stuNO,
                'realName':submit.realName,
                'contestname':con.cname,
                'subid':submit.subid,
                'index':submit.index,
                'tag':submit.tag,
                'statu':submit.statu,
                'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
            })
    context = {
        'name':Student.objects.get(stuNO=stuNO).realName,
        'list':data,
    }
    return render(request,"aftersubmit.html",context)

def setallaftersolve(request):      #手动更新解题数
    students = Student.objects.all()
    strs = ''
    for stu in students:
        strs += stu.realName + ','
        datautils.setaftersolve(stu)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)
#end代码及解题数模块

def addprizet(request):     #比赛获奖记录功能,此模块尚未开发完毕
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


#月排名模块
@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def monthlyrating(request,year='0',month='0'):
    currYear = datetime.datetime.now().year
    yearlist = [currYear,currYear-1,currYear-2,currYear-3,currYear-4,currYear-5,currYear-6,currYear-7,currYear-8,currYear-9,currYear-10,'ALL']
    if year == '0':
        year = str(currYear)
        month = datetime.datetime.now().month
        if month<10:
            month = ('0%d') % (month)
    if month == 'S1':   #第一季度
        starttime = ("%s-0%s-01 00:00:00") % (year, 1)
        endtime = ("%s-0%s-31 23:59:59") % (year, 3)
    elif month == 'S2':
        starttime = ("%s-0%s-01 00:00:00") % (year, 4)
        endtime = ("%s-0%s-31 23:59:59") % (year, 6)
    elif month == 'S3':
        starttime = ("%s-0%s-01 00:00:00") % (year, 7)
        endtime = ("%s-0%s-31 23:59:59") % (year, 9)
    elif month == 'S4':
        starttime = ("%s-%s-01 00:00:00") % (year, 10)
        endtime = ("%s-%s-31 23:59:59") % (year, 12)
    elif month == 'H1': #上半年
        starttime = ("%s-0%s-01 00:00:00") % (year, 1)
        endtime = ("%s-0%s-31 23:59:59") % (year, 6)
    elif month == 'H2':
        starttime = ("%s-0%s-01 00:00:00") % (year, 7)
        endtime = ("%s-%s-31 23:59:59") % (year, 12)
    elif month == 'ALL':    #全年
        starttime = ("%s-0%s-01 00:00:00") % (year, 1)
        endtime = ("%s-%s-31 23:59:59") % (year, 12)
    else:
        starttime = ("%s-%s-01 00:00:00") % (year, month)
        endtime = ("%s-%s-31 23:59:59") % (year, month)

    if year == "ALL":        
        starttime = "2014-01-01 00:00:00"
        endtime = ("%s-%s-31 23:59:59") % (currYear, 12)

    datalist = StudentContest.objects.filter(cdate__range=(starttime,endtime))
    studentlist = []
    for d in datalist:
        isFind = False        
        for stu in studentlist:
            if stu['stuNO'] == d.stuNO:
                isFind = True
                break
        if not isFind:            
            studentlist.append({
                'stuNO':d.stuNO,
                'className':d.className,
                'realName':d.realName,
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
            })
            stu = studentlist[-1]
        if d.ctype == 'cf':
            stu['cf'] += 1
            stu['cfp'] += int(d.solve)
            stu['cfpp'] += int(d.aftersolve)
            stu['cfdiff'] += int(d.diff)
        elif d.ctype == 'ac':
            stu['ac'] += 1
            stu['acp'] += int(d.solve)
            stu['acpp'] += int(d.aftersolve)
            try:
                stu['acdiff'] += int(d.diff)
            except:
                pass
        elif d.ctype == 'jsk':
            stu['jsk'] += 1
            stu['jskp'] += int(d.solve)
        elif d.ctype == 'nc':
            stu['nc'] += 1
            stu['ncp'] += int(d.solve.split('/')[0])
    
    if year == 'ALL':
        datalist_cfpp = datautils.getbigaftersolve(2014,1,currYear,12,source='cf')
        datalist_acpp = datautils.getbigaftersolve(2014,1,currYear,12,source='ac')
    elif month == 'S1':   #第一季度
        datalist_cfpp = datautils.getbigaftersolve(int(year),1,int(year),4,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),1,int(year),4,source='ac')
    elif month == 'S2':
        datalist_cfpp = datautils.getbigaftersolve(int(year),4,int(year),7,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),4,int(year),7,source='ac')
    elif month == 'S3':
        datalist_cfpp = datautils.getbigaftersolve(int(year),7,int(year),10,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),7,int(year),10,source='ac')
    elif month == 'S4':
        datalist_cfpp = datautils.getbigaftersolve(int(year),10,int(year)+1,1,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),10,int(year)+1,1,source='ac')
    elif month == 'H1': #上半年
        datalist_cfpp = datautils.getbigaftersolve(int(year),1,int(year),7,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),1,int(year),7,source='ac')
    elif month == 'H2':
        datalist_cfpp = datautils.getbigaftersolve(int(year),7,int(year)+1,1,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),7,int(year)+1,1,source='ac')
    elif month == 'ALL':    #全年
        datalist_cfpp = datautils.getbigaftersolve(int(year),1,int(year)+1,1,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),1,int(year)+1,1,source='ac')
    else:
        datalist_cfpp = datautils.getbigaftersolve(int(year),int(month),int(year),int(month)+1,source='cf')
        datalist_acpp = datautils.getbigaftersolve(int(year),int(month),int(year),int(month)+1,source='ac')
    for s in studentlist:
        if s['stuNO'] in datalist_cfpp:
            s['cfpp']=datalist_cfpp[s['stuNO']]-s['cfp']
        else:
            s['cfpp']=0
        if s['stuNO'] in datalist_acpp:
            s['acpp']=datalist_acpp[s['stuNO']]-s['acp']
        else:
            s['acpp']=0
        s["score"] = (s['cf']+s['ac']+s['jsk']+s['nc']) * 20 + (s['cfp']+s['cfpp']+s['jskp']+s['ncp']+s['acp']+s['acpp']) * 5 + (s['cfdiff']+s['acdiff'])

    studentlist = sorted(studentlist, reverse=True, key=lambda x: x['score'])
    monthlist = ["01","02","03","04","05","06","07","08","09","10","11","12","S1","S2","S3","S4","H1","H2","ALL"]
    context = {'studentlist': studentlist ,"year":year, "month":month,"yearlist":yearlist, "monthlist":monthlist}
    return render(request, 'monthlyrating.html', context)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def studentmonthlys(request,stuNO):
    thisyear = datetime.datetime.now().year
    thismon = datetime.datetime.now().month
    years = [thisyear,thisyear-1,thisyear-2,thisyear-3]
    stu = Student.objects.get(stuNO=stuNO)
    classname,realname,cfID,acID,ncID,jskID = stu.className, stu.realName, stu.cfID, stu.acID, stu.ncID,stu.jskID
    monthlist={}
    """for year in years:
        if year not in monthlist:
            monthlist[year]=[]
        if year >= stu.year:
            if year == thisyear:
                for month in range(thismon,0,-1):
                    monthlist[year].append(month)
            elif year == stu.year:
                for month in range(12,8,-1):
                    monthlist[year].append(month)
            else:
                for month in range(12,0,-1):
                    monthlist[year].append(month)"""
    datalist = datautils.getbigstudentmonth(stu,stu.year-2,9,thisyear,thismon+1)
    """lent= len(datalist)
    lists = []
    for ids,data in enumerate(datalist):
        if  (str(data['year']) + str(data['month'])) not in lists:
            if data['month'] == '03' :
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'S1'))
            elif data['month'] == '06':
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'S2'))
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'H1'))
            elif data['month'] == '09':
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'S3'))
            elif data['month'] == '12':
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'S4'))
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'H2'))
                datalist.insert(ids,datautils.spmonth(datalist,data['year'],'ALL'))
            lists.append((str(data['year']) + str(data['month'])))"""#季度年度显示
    datalist.reverse()
    poplist = []
    for idx,data in enumerate(datalist):
        if data['cf']==0 and data['cfpp']==0 and data['ac']==0 and data['jsk']==0 and data['nc']==0 and data['score']==0:
            poplist.append(idx)
        else:
            break
    poplist.reverse()
    for idx in poplist:
        datalist.pop(idx)
    datalist.reverse()
    context = {'list': datalist,'classname':classname, 'realname':realname,'cfID':cfID,'acID':acID,'ncID':ncID,'jskID':jskID}
    return render(request, 'studentmonthlys.html',context)

def monthlysub(request,type,stuNO,year,month):
    contest = Contest.objects.filter(ctype="cf")
    end = {}
    names = {}
    for con in contest:
        end[con.cid]=con.endtimestamp
        names[con.cid] = con.cname
    if month == 's1':
        starttime = time.mktime(time.strptime(("%s-01-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-04-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 's2':
        starttime = time.mktime(time.strptime(("%s-04-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-07-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 's3':
        starttime = time.mktime(time.strptime(("%s-07-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-10-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 's4':
        starttime = time.mktime(time.strptime(("%s-10-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-12-31 23:59:59") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 'h1':
        starttime = time.mktime(time.strptime(("%s-01-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-07-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 'h2':
        starttime = time.mktime(time.strptime(("%s-07-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-12-31 23:59:59") % (year),"%Y-%m-%d %H:%M:%S"))
    elif month == 'all':
        starttime = time.mktime(time.strptime(("%s-01-01 00:00:00") % (year),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%s-12-31 23:59:59") % (year),"%Y-%m-%d %H:%M:%S"))
    else:
        if month == '12':
            eyear = int(year) + 1
            emonth = 1
        else:
            eyear = int(year)
            emonth = int(month) + 1
        starttime = time.mktime(time.strptime(("%s-%s-01 00:00:00") % (year,month),"%Y-%m-%d %H:%M:%S"))
        endtime = time.mktime(time.strptime(("%d-%02d-01 00:00:00") % (eyear,emonth),"%Y-%m-%d %H:%M:%S"))
    datalist = []
    cfcons = CFContest.objects.filter(stuNO=stuNO,ctime__range=(starttime,endtime))
    if type=='after':
        for submit in cfcons:
            if submit.ctime > end[submit.cid]:
                datalist.append({
            'stuNO':submit.stuNO,
            'contestname':names[submit.cid],
            'subid':submit.subid,
            'index':submit.index,
            'tag':submit.tag,
            'statu':submit.statu,
            'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
        })
    if type == 'before':
        for submit in cfcons:
            if submit.ctime <= end[submit.cid]:
                datalist.append({
                'stuNO':submit.stuNO,
                'contestname':names[submit.cid],
                'subid':submit.subid,
                'index':submit.index,
                'tag':submit.tag,
                'statu':submit.statu,
                'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
                })
    content = {'list':datalist,'name':Student.objects.get(stuNO=stuNO).realName}
    return render(request,"monthlysubmit.html",content)
    
#end月排名



def jskdataupdate(request): #计蒜客数据更新
    students = Student.objects.all()
    suc = ''
    fail = ''
    strs = ''
    logger = logging.getLogger('log')
    for stu in students:
        if stu.jskID:
            logger.info(stu.realName + "start jsk dataget")
            p = jsk.getjskdata(stu)
            if p :
                suc += stu.realName + '、'
            else:
                fail += stu.realName + '、'
            logger.info(stu.realName + "end jsk dataget")
    datautils.setContestJoinNumbers()
    strs = "successlist:\n" + suc + "\nerrorlist:\n" + fail
    context = {'str': strs }
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['jskUpdatTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w")) 
    return render(request, 'spiderResults.html', context)

def fixacdiff(request):
    contest = StudentContest.objects.all()
    strs = ''
    for con in contest:
        if con.diff == '-':
            strs += con.realName + ' & '
            con.diff = con.newRating
            con.save()
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def updateCodeforcesQuestion(request):
    strs = CQ.updateContestQuestion()
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)
@cache_page(24*60*60) #一天

@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def CodeforcesQuestionsview(request,cid,index):
    que = CodeforcesQuestion.objects.get(cid=cid,index = index)
    acsub = CFContest.objects.filter(cid=cid,index=index,statu = "OK")
    acnum = acsub.count()
    failnum = CFContest.objects.filter(cid=cid,index=index).count()-acnum
    data = []
    for submit in acsub:
        data.append({
            'realName':submit.realName,
            'subid':submit.subid,
            'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
        })
    text = que.mdtext
    text = markdown.markdown(text,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.latex',
    ])
    content = {
        "cid":cid,
        "index":index,
        "cname":que.cname,
        "name":que.name,
        "text":text,
        "acsub":data,
        "acnum":acnum,
        "failnum":failnum,
    }
    return render(request,"CoderforcesQuestion.html",content)
@cache_page(60*60) #1小时

@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def Problemset(request,tag):
    if tag == "ALL":
        qus = CodeforcesQuestion.objects.defer("mdtext").all().order_by("-cid")
    else:
        qus = CodeforcesQuestion.objects.defer("mdtext").order_by("-difficulty").filter(tags__contains = tag)
        print(qus)
    tags = ['brute force', 'greedy', 'math', 'sortings', 'implementation', 'binary search', 'ternary search', 'number theory', 'dp', 'strings', 'data structures', 'two pointers', 'constructive algorithms', 'combinatorics', 'flows', 'bitmasks', 'dfs and similar', 'expression parsing', 'shortest paths', 'geometry', 'meet-in-the-middle', 'divide and conquer', 'trees', 'graphs', 'games', 'dsu', 'interactive','hashing', 'matrices', 'string suffix structures', 'chinese remainder theorem', 'probabilities', '2-sat', 'graph matchings', 'fft']
    tags.insert(0,"ALL")
    content = {
        "problems": qus,
        "tags": tags,
        "tag" :tag,
        
    }
    return render(request,"Problemset.html",content)

