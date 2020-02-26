from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import loader
from acmerdata import bsdata, datautils
import logging
import lxml
from .models import Student, Contest, StudentContest,AddStudentqueue,studentgroup,CFContest,Contestforecast,AddContestprize,Weightrating
from .forms import Addstudent,Addgroup,addprize
import time,datetime,json
import re
import random
import markdown
from django.db.models import Max
import operator

# Create your views here.
def spider(request):
    context = {} #{'studentlist': studentlist}
    return render(request, 'spider.html', context)

def contact(request):
    context = {} #{'studentlist': studentlist}
    return render(request, 'contact.html', context)

def timeline(request):
    context = {} #{'studentlist': studentlist}
    return render(request, 'timeline.html', context)

def groupRatingLine(request,groupid):
    group = studentgroup.objects.get(id=groupid)
    pattern = re.compile(r'\d+')
    s = pattern.findall(str(group.groupstuID))
    stuNOList = []
    for sid in s:
        stuNOList.append(int(sid))
    # stuNOList = [ 2016014323]
    logger = logging.getLogger('log')

    stuList = Student.objects.filter(stuNO__in = stuNOList)
    color = datautils.ncolors(len(stuList))
    stuNOList = []
    lineX = []
    names = []
    dic_stuNO_rating = {}
    dic_stuNO_year = {}
    for stu in stuList:
        stuNOList.append(stu.stuNO)
        names.append(stu.realName)
        dic_stuNO_rating[stu.stuNO] = []   
        dic_stuNO_year[stu.stuNO] = stu.year     
    yearlist = ['Freshman','Sophomore','Junior']
    monthlist = ['09','10','11','12','01','02','03','04','05','06','07','08']
    dic_year_gap = {'Freshman':0,'Sophomore':1,'Junior':2}
    dic_month_gap = {'09':0,'10':0,'11':0,'12':0,'01':1,'02':1,'03':1,'04':1,'05':1,'06':1,'07':1,'08':1}
    for year in yearlist:
        for month in monthlist:
            if month == '09':
                lineX.append(year+month)
            else:
                lineX.append(month)
            for stuNO in stuNOList:
                date = str(dic_stuNO_year[stuNO] + dic_year_gap[year] + dic_month_gap[month]) + "-" + month
                value = datautils.getLatestCFRating(stuNO,date)
                if value == 0 and len(dic_stuNO_rating[stuNO])>0:
                    value = dic_stuNO_rating[stuNO][-1]
                logger.info(date + ":" + str(value))
                dic_stuNO_rating[stuNO].append(value)

    
    # logger.info(lineX)
    # logger.info(names)
    # logger.info(dic_stuNO_rating)

    context = {
        "lineX":json.dumps(lineX),
        "names":json.dumps(names),
        "stuNOList":json.dumps(stuNOList),
        "dic_stuNO_rating":json.dumps(dic_stuNO_rating),
        "color":json.dumps(color)
    } 
    return render(request, 'groupRatingLine.html', context)

def groupdata(request,groupid):
    group = studentgroup.objects.get(id=groupid)
    pattern = re.compile(r'\d+')
    s = pattern.findall(str(group.groupstuID))
    stuNOList = []
    for sid in s:
        stuNOList.append(int(sid))
    # stuNOList = [ 2016014323]
    logger = logging.getLogger('log')

    stuList = Student.objects.filter(stuNO__in = stuNOList)
    color = datautils.ncolors(len(stuList))
    stuNOList = []
    lineX = []
    names = []
    dic_stuNO_rating = {}
    dic_stuNO_year = {}
    for stu in stuList:
        stuNOList.append(stu.stuNO)
        names.append(stu.realName)
        dic_stuNO_rating[stu.stuNO] = []   
        dic_stuNO_year[stu.stuNO] = stu.year     
    yearlist = ['Freshman','Sophomore','Junior']
    monthlist = ['09','10','11','12','01','02','03','04','05','06','07','08']
    dic_year_gap = {'Freshman':0,'Sophomore':1,'Junior':2}
    dic_month_gap = {'09':0,'10':0,'11':0,'12':0,'01':1,'02':1,'03':1,'04':1,'05':1,'06':1,'07':1,'08':1}
    for year in yearlist:
        for month in monthlist:
            if month == '09':
                lineX.append(year+month)
            else:
                lineX.append(month)
            for stuNO in stuNOList:
                date = str(dic_stuNO_year[stuNO] + dic_year_gap[year] + dic_month_gap[month]) + "-" + month
                value = datautils.getLatestCFRating(stuNO,date)
                if value == 0 and len(dic_stuNO_rating[stuNO])>0:
                    value = dic_stuNO_rating[stuNO][-1]
                logger.info(date + ":" + str(value))
                dic_stuNO_rating[stuNO].append(value)
    grouplist = studentgroup.objects.filter(enable=True)

    
    # logger.info(lineX)
    # logger.info(names)
    # logger.info(dic_stuNO_rating)

    context = {
        "lineX":json.dumps(lineX),
        "names":json.dumps(names),
        "stuNOList":json.dumps(stuNOList),
        "dic_stuNO_rating":json.dumps(dic_stuNO_rating),
        "color":json.dumps(color),
        "grouplist":grouplist,
        "students":stuList,
        "groupid":groupid,
    } 
    return render(request, 'groupdata.html', context)

def cftimeline(request):
    # fix the diff is 0 of ac data
    studentlist = Student.objects.all()
    dic = {'name':'name',"value":"v","date":"d"}
    datalist = []
    str = ""
    logger = logging.getLogger('log')
    yearlist = ['2015','2016','2017','2018','2019','2020']
    monthlist = ['01','02','03','04','05','06','07','08','09','10','11','12']
    stuRatingList = {}
    for year in yearlist:
        for month in monthlist:
            isChange = 0            
            for stu in studentlist:
                date = year+'-'+month
                name = stu.realName
                value = datautils.getLatestCFRating(stu.stuNO,date)
                if value > 0:
                    isChange = 1
                    stuRatingList[stu.realName] = value
            if isChange == 1:
                newList = sorted(stuRatingList.items(), key=lambda item:item[1], reverse=True)
                for k in newList:
                    if int(k[1]) > 0:
                        datalist.append({
                            'name':k[0],"value":k[1],"date":year+month
                        })
    context = {'str': datalist}
    return render(request, 'cftimeline.html', context)

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

def index(request):
    studentlist = Student.objects.order_by("-cfRating").all()
    data=[]
    for stu in studentlist:
        data.append({
            'stuNO':stu.stuNO,
            'realName':stu.realName,
            'className':stu.className,
            'year':stu.year,
            'cfRating':stu.cfRating,
            'cfTimes':stu.cfTimes,
            'after':str(stu.correct_cf_aftersolve) + '/' + str(stu.all_cf_aftersolve),
            'acRating':stu.acRating,
            'acTimes':stu.acTimes,
            'ncTimes':stu.ncTimes,
            'ncRating':stu.ncRating,
            'school':stu.school,
        })
    context = {'studentlist': data}
    return render(request, 'students.html', context)

def contests(request):
    contestlist = Contest.objects.order_by('-cdate').all()
    for c in contestlist:
        c.cdate = c.cdate[0:16]
        if len(c.cname) > 50:
            c.cname = c.cname[0:50] + "..."
    context = {'contestlist': contestlist}
    return render(request, 'contests.html', context)

def contest(request, contest_id=-1,studentcontest_id=-1):
    if contest_id > 0:
        ct = Contest.objects.filter(id=contest_id)  
    else:
        ct = StudentContest.objects.filter(id=studentcontest_id)  
    logging.info("len(ct)"+str(len(ct)))
    list = []
    if len(ct)>0:
        #list = StudentContest.objects.order_by('rank').filter(cname=ct[0].cname)
        list = datautils.contestdatasolve(cname=ct[0].cname)
        if ct[0].ctype == 'cf':
            cid = ct[0].cid
        else:
            cid = ''
    context = {'list': list,"cname":ct[0].cname,"cdate":ct[0].cdate,'cid':cid}
    return render(request, 'contest.html', context)

def student(request, stuNO):
    #list = StudentContest.objects.order_by('-cdate').filter(stuNO=stuNO)
    data = datautils.contestdatasolve(stuNO=stuNO)
    stu = Student.objects.get(stuNO=stuNO)
    classname, realname= '',''
    if len(data)>0:
        classname,realname,cfID,acID,ncID = stu.className, stu.realName, stu.cfID, stu.acID, stu.ncID

    context = {'list': data,'classname':classname, 'realname':realname,'cfID':cfID,'acID':acID,'ncID':ncID}
    return render(request, 'student.html', context)

# update cf data by contest, start from not zero
def updateCFDataByContest(request):
    str = "CF Data, successed list:"
    str += datautils.saveCFDataByContest()
    datautils.cftimesreset()#供测试阶段调试使用，正式上线请将cftimes调整至准确再使用递增方法
    context = {'str': str}
    return render(request, 'spiderResults.html', context)   

# update cf data by all user, start from zero
def getCFData(request):
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

def getACData(request):    
    studentlist = Student.objects.all()
    # studentlist = Student.objects.filter(realName='张世东')
    str = "AC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data")
        datautils.saveACData(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data")
    datautils.setContestJoinNumbers()
    context = {'str': str}
    return render(request, 'spiderResults.html', context)

def getNCData(request):    
    studentlist = Student.objects.all()
    # studentlist = Student.objects.filter(realName='张世东')
    str = "NC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start nc data")
        datautils.saveNCData(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end nc data")
    context = {'str': str}
    datautils.setContestJoinNumbers()
    return render(request, 'spiderResults.html', context)

def Addstudentdata(request):
    if request.method == 'POST':
        formt = Addstudent(request.POST)
        if formt.is_valid():
            print(formt.clean())
            c = formt.clean()
            acck=bsdata.cheakacID(str(c['acID']))
            cfck=bsdata.cheakcfID(str(c['cfID']))
            AddStudentqueue.objects.create(stuNO=c['stuNO'],realName=c['realName'],className=c['className'],school=c['school'],year=c['year'],
            acID=c['acID'],accheck=acck,cfID=c['cfID'],cfcheck=cfck,vjID=c['vjID'],ncID=c['ncID'],execution_statu=False,request_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            formt=Addstudent()
            massage = "添加成功，请等待审核"
            return render(request,'addstudent.html',{'form': formt,'massage':massage})
    else:
        formt = Addstudent()
        massage =""
    return render(request,'addstudent.html',{'form': formt,'massage':massage})

def updatestudentlist(request):
    students = []
    for s in AddStudentqueue.objects.all():
        if s.execution_statu == False and str(s.execution) != "None":
            if s.execution == True:
                sc = Student.objects.filter(stuNO=s.stuNO,realName=s.realName,className=s.className)
                if len(sc)==0:
                    Student.objects.create(
                    stuNO=s.stuNO,realName=s.realName,className=s.className,school=s.school,
                    year=s.year,acID=s.acID,cfID=s.cfID,vjID=s.vjID,ncID=s.ncID,
                    )
                    a = Student.objects.get(stuNO=s.stuNO,realName=s.realName,className=s.className,school=s.school)
                else:
                    """sc.update(
                    stuNO=s.stuNO,realName=s.realName,className=s.className,school=s.school,
                    year=s.year,acID=s.acID,cfID=s.cfID,vjID=s.vjID,ncID=s.ncID,
                    )"""#全量修改
                    a = Student.objects.get(stuNO=s.stuNO)
                    if s.acID!='':
                        a.acID=s.acID
                    if s.cfID!='':
                        a.cfID=s.cfID
                    if s.ncID!='':
                        a.ncID=s.ncID
                    if s.vjID!='':
                        a.vjID=s.vjID
                datautils.saveCFdataByUser(a)
                datautils.saveACData(a)
                datautils.saveNCData(a)
                students.append(a)
            s.execution_statu=True
            s.execution_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            s.save()
    contests = Contest.objects.filter(ctype='cf')
    for contest in contests:
        datautils.setcontestsolve(contest.cid)
    for stu in students:
        datautils.setaftersolve(stu)
    datautils.setContestJoinNumbers()
    studentlist = AddStudentqueue.objects.order_by("-request_time").all()
    context = {'studentlist': studentlist}
    return render(request, 'addstudentslist.html', context)


def addstatu(request):
    studentlist = AddStudentqueue.objects.order_by("-request_time").all()
    context = {'studentlist': studentlist}
    return render(request, 'addstudentslist.html', context)

def group(request):
    massage = ''
    grouplist = studentgroup.objects.filter(enable=True)
    if request.method == "POST":
        form = Addgroup(request.POST)
        if form.is_valid():
            name = ''
            c = form.clean()
            pattern = re.compile(r'\d+')
            s = pattern.findall(c['groupstuID'])
            try:
                for sid in s:
                    print(str(sid))
                    student = Student.objects.get(stuNO=str(sid))
                    if name == '':
                        name = ''.join([name,str(student.realName)])
                    else :
                        name="&".join([name,str(student.realName)])
                studentgroup.objects.create(groupstuID=c['groupstuID'],remark = c['remark'],studentNames = name)
                form=Addgroup()
                massage = "Add success"
            except:
                massage = "Error:no student-" + str(sid)
            grouplist = studentgroup.objects.filter(enable=True)
            return render(request,"group.html",{'form':form,'massage':massage,'grouplist':grouplist})            
    else:
        form=Addgroup()
    return render(request,"group.html",{'form':form,'massage':massage,'grouplist':grouplist})

def groupdel(request,groupid):
    qs = studentgroup.objects.get(id=groupid)
    massage = "您已删除id为" + str(qs.id) +"的组" 
    qs.enable = False
    qs.save()
    return render(request,"groupdeleteresult.html",{'massage':massage})

def cfcontestsubmit(request,cid):
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
            'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
        })
    context = {
        'cname':cname,
        'cdate':cdate,
        'list':data,
    }
    return render(request,"cfcontestsubmit.html",context)

def viewcode(request,submitid):
    cfct = CFContest.objects.get(subid=submitid)
    name = cfct.realName
    statu = cfct.statu
    index = cfct.index
    subid = cfct.subid
    code = "```c++\n"+ cfct.code +"\n```"
    print(code)
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
    
def fixcodeerrorforinternetproblem(request):
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
def fixcodeerrorforlanguageerror(request):
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

def cfcontestsubmitupdatebycontest(request):
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

def updateforecastlist(request):
    ntime = time.time()
    strs = ''
    Contestforecast.objects.filter(starttime__lte=ntime).delete()
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

def contestforecast(request):
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
            'during':datautils.timestamptotime(int(contest.during))
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

def Standardizecftime(request):
    strs = datautils.cftimeStandard()
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def setallcontestsolve(request):
    contests = Contest.objects.filter(ctype='cf')
    strs = ''
    for contest in contests:
        strs += contest.cname +' \ '
        datautils.setcontestsolve(contest.cid)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def aftersolve(request,stuNO):
    cfcontests = StudentContest.objects.filter(ctype='cf',stuNO=stuNO)
    data = []
    for contest in cfcontests:
        con = Contest.objects.get(cid=contest.cid)
        submits = CFContest.objects.filter(cid=contest.cid,stuNO=stuNO,ctime__gt=con.endtimestamp)
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

def setallaftersolve(request):
    students = Student.objects.all()
    strs = ''
    for stu in students:
        strs += stu.realName + ','
        datautils.setaftersolve(stu)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def addprizet(request):
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

def updataweightratingstatistics(request):
    students = Student.objects.filter(school="北京化工大学")
    strs=''
    tngap = time.time() - 8035200
    for stu in students:
        strs += stu.realName +"、"
        div2 = 0
        div1 = 0
        div3 = 0 
        contests = StudentContest.objects.filter(stuNO = stu.stuNO,ctype='cf')
        for contest in contests :
            if Contest.objects.get(cid=contest.cid).starttimestamp >= tngap:
                if contest.cdiv == '2':
                    div2=div2+1
                elif contest.cdiv == '1':
                    div1=div1+1
                elif contest.cdiv == '3':
                    div3=div3+1
        count = stu.cfRating + div1 * 30 + div2 * 20 + div1 * 10 +stu.correct_cf_aftersolve * 5 + stu.acRating
        datalist={
            'div1':div1,
            'div2':div2,
            'div3':div3,
            'stuNO':stu.stuNO,
            'realName':stu.realName,
            'className':stu.className,
            'year':stu.year,
            'after':str(stu.correct_cf_aftersolve) + '/' + str(stu.all_cf_aftersolve),
            'count':count,
            'cfRating':stu.cfRating,
            'acRating':stu.acRating,
        }
        Weightrating.objects.update_or_create(datalist,stuNO=stu.stuNO)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)
def weightratingstatistic(request):
    list = Weightrating.objects.order_by("-count").all()
    return render(request,'weightrating.html',{'studentlist': list})