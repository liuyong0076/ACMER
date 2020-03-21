from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import loader
from acmerdata import bsdata, datautils ,jsk,atcoder
from django.views.decorators.cache import cache_page
import logging
import lxml
from .models import Student, Contest, StudentContest,AddStudentqueue,studentgroup,CFContest,Contestforecast,AddContestprize,ACContest
from .forms import Addstudent,Addgroup,addprize
import time,datetime,json
import re
import random
import markdown
from django.db.models import Max,Min
import operator
import os


@cache_page(60 * 60 * 24) # 单位：秒，这里表示缓存一天
def timeline(request):  #时间线页面接口
    studentlist = Student.objects.filter(school='北京化工大学')
    StuContestList = StudentContest.objects.all().filter(ctype='cf').order_by('cdate')
    dic = {'name':'name',"value":"v","date":"d"}
    datalist = []
    str = ""
    logger = logging.getLogger('log')
    yearlist = ['2015','2016','2017','2018','2019','2020']
    
    yeartemp = 2020
    currYear = datetime.datetime.now().year
    while yeartemp < currYear:
        yearlist.append(str(yeartemp))
        yeartemp += 1

    monthlist = ['01','02','03','04','05','06','07','08','09','10','11','12']

    stuRatingList = {}
    for year in yearlist:
        for month in monthlist:
            isChange = 0            
            for stu in studentlist:
                date = year+'-'+month
                # name = stu.realName
                # value = datautils.getLatestCFRating(stu.stuNO,date)
                value = datautils.getLatestCFRating_fasterVersion(StuContestList,stu.stuNO,date)
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
    context = {'str': json.dumps(datalist)}
    return render(request, 'VisualData/timeline.html', context)

#比较组展示模块
def group(request):     #组页面函数,提供未被删除的组进行浏览,同时使用POST进行增加组
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
            return render(request,"VisualData/group.html",{'form':form,'massage':massage,'grouplist':grouplist})            
    else:
        form=Addgroup()
    return render(request,"VisualData/group.html",{'form':form,'massage':massage,'grouplist':grouplist})

def groupdel(request,groupid):      #组删除视图函数,传入组id,但此删除为伪删除,删除之后此比较组不可用,但仍能在数据库中查询到相关信息
    qs = studentgroup.objects.get(id=groupid)
    massage = "您已删除id为" + str(qs.id) +"的组" 
    qs.enable = False
    qs.save()
    return render(request,"VisualData/groupdeleteresult.html",{'massage':massage})

@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def groupRatingLine(request,groupid):   #队时间线页面接口 groupid可以是整数，也可以是学号列表
    if len(groupid)>6:
        stuNOList = groupid.split(",")
    else:
        group = studentgroup.objects.get(id=groupid)
        pattern = re.compile(r'\d+')
        s = pattern.findall(str(group.groupstuID))
        stuNOList = []
        for sid in s:
            stuNOList.append(int(sid))

    logger = logging.getLogger('log')

    stuList = Student.objects.filter(stuNO__in = stuNOList)
    StuContestList = StudentContest.objects.filter(stuNO__in = stuNOList)
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
                value = datautils.getLatestCFRating_fasterVersion(StuContestList,stuNO,date)
                if value == 0 and len(dic_stuNO_rating[stuNO])>0:
                    value = dic_stuNO_rating[stuNO][-1]
                logger.info(date + ":" + str(value))
                dic_stuNO_rating[stuNO].append(value)
    context = {
        "lineX":json.dumps(lineX),
        "names":json.dumps(names),
        "stuNOList":json.dumps(stuNOList),
        "dic_stuNO_rating":json.dumps(dic_stuNO_rating),
        "color":json.dumps(color)
    } 
    return render(request, 'VisualData/groupRatingLine.html', context)

def groupdata(request,groupid):   #队数据
    group = studentgroup.objects.get(id=groupid)
    StuContestList = StudentContest.objects.all().filter(ctype='cf').order_by('cdate')
    pattern = re.compile(r'\d+')
    s = pattern.findall(str(group.groupstuID))
    stuNOList = []
    for sid in s:
        stuNOList.append(int(sid))
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
                value = datautils.getLatestCFRating_fasterVersion(StuContestList,stuNO,date,)
                if value == 0 and len(dic_stuNO_rating[stuNO])>0:
                    value = dic_stuNO_rating[stuNO][-1]
                logger.info(date + ":" + str(value))
                dic_stuNO_rating[stuNO].append(value)
    grouplist = studentgroup.objects.filter(enable=True)

    cons = Contest.objects.filter(ctype = "cf")
    endtime = {}
    for con in cons:
        endtime[con.cid] = con.endtimestamp
    cfContest = CFContest.objects.all()
    datalist = {}
    names = []
    tags = ['brute force', 'greedy', 'math', 'sortings', 'implementation', 'binary search', 'ternary search', 'number theory', 'dp', 'strings', 'data structures', 'two pointers', 'constructive algorithms', 'combinatorics', 'flows', 'bitmasks', 'dfs and similar', 'expression parsing', 'shortest paths', 'geometry', 'meet-in-the-middle', 'divide and conquer', 'trees', 'graphs', 'games', 'dsu', 'interactive','hashing', 'matrices', 'string suffix structures', 'chinese remainder theorem', 'probabilities', '2-sat', 'graph matchings', 'fft']
    allcount = [0]*len(tags)
    for stuNO in stuNOList:
        names.append(stuList.get(stuNO=stuNO).realName)
        slist=[]
        clist = []
        for ids,tag in enumerate(tags):
            clist = []
            solve = 0
            contests = cfContest.filter(stuNO=stuNO,realName=names[-1],statu="OK",tag__contains=tag)
            for con in contests:
                if str(con.cid) + con.index not in clist:
                    if endtime[con.cid] > con.ctime:
                        clist.append(str(con.cid) + con.index)
                        solve = solve + 1
            slist.append(solve)
            allcount[ids] += solve
        datalist[names[-1]] = slist
    # logger.info(lineX)
    # logger.info(names)
    # logger.info(dic_stuNO_rating)

    context = {
        "lineX":json.dumps(lineX),
        "names":json.dumps(names),
        "stuNOList":json.dumps(stuNOList),
        "dic_stuNO_rating":json.dumps(dic_stuNO_rating),
        "grouplist":grouplist,
        "students":stuList,
        "groupid":groupid,
        'tags':json.dumps(tags),
        'datalist':json.dumps(datalist),
        'namesforit':names,
        'names':json.dumps(names),
        'colors':json.dumps(color),
        'allcount':json.dumps(allcount),
    } 
    return render(request, 'VisualData/groupdata.html', context)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def teamMembersCount(request):
    y=[]
    number = []
    cycle= []
    bar = []
    bar1 = []
    cnt = []
    for year in range(2014,2020):
        cycle.append(0)
        bar.append(100)
        bar1.append(99.5)
        cnt.append(Student.objects.filter(school = "北京化工大学",year = year,cfTimes__gte=5).count())
        y.append(year)
        number.append(Student.objects.filter(school = "北京化工大学",year = year,cfTimes__gte=5).count())
    return render(request,'VisualData/TeamMembersCount.html',{'year':y,'number':number,"cycle":cycle,'bar':bar,"bar1":bar1,"cnt":cnt})


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def topCompare(request):
    stu = Student.objects.filter(school = '北京化工大学')
    years = {}
    content = {}
    content['year'] = []
    for year in range(2014,2020):
        rank = stu.filter(year = year).order_by("-cfRating")
        yt1 = 0
        yt3 = 0
        n3 =0
        yt5 = 0
        n5=0
        yt10 = 0
        n10 = 0
        for i,s in enumerate(rank):
            if i<1:
                yt1 += s.cfRating
            if i<3:
                yt3 += s.cfRating
                n3 +=1
            if i<5:
                yt5 += s.cfRating
                n5 +=1
            if i<10:
                yt10 += s.cfRating
                n10 +=1
        if year not in content:
            content['year'].append(year)
            content[str(year)+'年'] = []
        content[str(year)+'年'].append(yt1)
        content[str(year)+'年'].append(int(yt3/3))
        content[str(year)+'年'].append(yt5/5)
        content[str(year)+'年'].append(yt10/10)
    
    return render(request,"VisualData/TopCompare.html",content)


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def contestCount(request):
    allcount = []
    account = []
    cfcount = []
    nccount = []
    thisyear = time.localtime(time.time()).tm_year
    thismonth = time.localtime(time.time()).tm_mon
    contest = Contest.objects.all()
    mintimestamp = Contest.objects.filter(endtimestamp__gt = 0).order_by("endtimestamp")[0].endtimestamp
    date = time.localtime(mintimestamp)
    xdata = []
    for year in range(date.tm_year,thisyear+1):
        if year == thisyear:
            for month in range(1,thismonth+1):
                xdata.append("%d-%02d" % (year,month))
        elif year == date.tm_year:
            for month in range(date.tm_mon,12):
                xdata.append("%d-%02d" % (year,month))
        else:
            for month in range(1,13):
                xdata.append("%d-%02d" % (year,month))
    for x in xdata:
        year = int(x.split("-")[0])
        month = int(x.split("-")[1])
        starttime = ("%d-%02d-01 00:00:00"%(year,month))
        if month == 12:
            endtime = ("%d-01-01 00:00:00"%(year+1))
        else:
            endtime = ("%d-%02d-01 00:00:00"%(year,month + 1))
        actime = contest.filter(cdate__range = (starttime,endtime),ctype="ac").count()
        cftime = contest.filter(cdate__range = (starttime,endtime),ctype="cf").count()
        nctime = contest.filter(cdate__range = (starttime,endtime),ctype="nc").count()
        allcount.append(actime+cftime+nctime)
        account.append(actime)
        cfcount.append(cftime)
        nccount.append(nctime)
    return render(request,"VisualData/contestCount.html",{'xdata':json.dumps(xdata),'account':account,'cfcount':cfcount,'allcount':allcount,'nccount':nccount})


@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def groupTagCompare(request,groupid): #groupid可以是整数，也可以是学号列表
    if len(groupid)>6:
        stuNOList = groupid.split(",")
    else:
        group = studentgroup.objects.get(id=groupid)
        pattern = re.compile(r'\d+')
        s = pattern.findall(str(group.groupstuID))
        stuNOList = []
        for sid in s:
            stuNOList.append(int(sid))

    cons = Contest.objects.filter(ctype = "cf")
    endtime = {}
    for con in cons:
        endtime[con.cid] = con.endtimestamp
    cfContest = CFContest.objects.all()
    stuList = Student.objects.all()
    datalist = {}
    names = []
    colors = datautils.ncolors(len(stuNOList))
    tags = ['brute force', 'greedy', 'math', 'sortings', 'implementation', 'binary search', 'ternary search', 'number theory', 'dp', 'strings', 'data structures', 'two pointers', 'constructive algorithms', 'combinatorics', 'flows', 'bitmasks', 'dfs and similar', 'expression parsing', 'shortest paths', 'geometry', 'meet-in-the-middle', 'divide and conquer', 'trees', 'graphs', 'games', 'dsu', 'interactive','hashing', 'matrices', 'string suffix structures', 'chinese remainder theorem', 'probabilities', '2-sat', 'graph matchings', 'fft']
    allcount = [0]*len(tags)
    for stuNO in stuNOList:
        names.append(stuList.get(stuNO=stuNO).realName)
        slist=[]
        clist = []
        for ids,tag in enumerate(tags):
            clist = []
            solve = 0
            contests = cfContest.filter(stuNO=stuNO,realName=names[-1],statu="OK",tag__contains=tag)
            for con in contests:
                if str(con.cid) + con.index not in clist:
                    if endtime[con.cid] > con.ctime:
                        clist.append(str(con.cid) + con.index)
                        solve = solve + 1
            slist.append(solve)
            allcount[ids] += solve
        datalist[names[-1]] = slist
    content = {
        'tags':json.dumps(tags),
        'datalist':json.dumps(datalist),
        'namesforit':names,
        'names':json.dumps(names),
        'colors':json.dumps(colors),
        'allcount':json.dumps(allcount),
    }
    return render(request,"VisualData/TagCompare.html",content)

@cache_page(60 * 15) # 单位：秒，这里表示15分钟
def groupTagPolor(request,groupid):
    if len(groupid)>6:
        stuNOList = groupid.split(",")
    else:
        group = studentgroup.objects.get(id=groupid)
        pattern = re.compile(r'\d+')
        s = pattern.findall(str(group.groupstuID))
        stuNOList = []
        for sid in s:
            stuNOList.append(int(sid))
    cons = Contest.objects.filter(ctype = "cf")
    endtime = {}
    for con in cons:
        endtime[con.cid] = con.endtimestamp
    cfContest = CFContest.objects.all()
    stuList = Student.objects.all()
    datalist = {}
    names = []
    colors = datautils.ncolors(len(stuNOList))
    tags = ['brute force', 'greedy', 'math', 'sortings', 'implementation', 'binary search', 'ternary search', 'number theory', 'dp', 'strings', 'data structures', 'two pointers', 'constructive algorithms', 'combinatorics', 'flows', 'bitmasks', 'dfs and similar', 'expression parsing', 'shortest paths', 'geometry', 'meet-in-the-middle', 'divide and conquer', 'trees', 'graphs', 'games', 'dsu', 'interactive','hashing', 'matrices', 'string suffix structures', 'chinese remainder theorem', 'probabilities', '2-sat', 'graph matchings', 'fft']
    for stuNO in stuNOList:
        names.append(stuList.get(stuNO=stuNO).realName)
        slist=[]
        clist = []
        for tag in tags:
            clist = []
            solve = 0
            contests = cfContest.filter(stuNO=stuNO,realName=names[-1],statu="OK",tag__contains=tag)
            for con in contests:
                if str(con.cid) + con.index not in clist:
                    if endtime[con.cid] > con.ctime:
                        clist.append(str(con.cid) + con.index)
                        solve = solve + 1
            slist.append(solve)
        datalist[names[-1]] = slist
    tags.append(tags[0])
    content = {
        'tags':json.dumps(tags),
        'datalist':json.dumps(datalist),
        'namesforit':names,
        'names':json.dumps(names),
        'colors':json.dumps(colors),
    }
    return render(request,"VisualData/polorCompare.html",content)