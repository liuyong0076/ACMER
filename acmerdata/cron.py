from acmerdata import bsdata, datautils,jsk,atcoder
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

def getACData():    #atcoder信息更新
    studentlist = Student.objects.all()
    str = "AC Data, successed list:"
    logger = logging.getLogger('log')
    for stu in studentlist:
        logger.info(stu.realName + "start ac data")
        atcoder.saveACDataIncrementally(stu)
        str += stu.realName + ","
        logger.info(stu.realName + "end ac data")
    atcoder.resetACContestSolveAll()
    datautils.setContestJoinNumbers()
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    context = {'str': str}

def getNCData():    #newcoder信息更新
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

def updateforecastlist():   #比赛预告信息更新
    ntime = time.time()
    strs = ''
    Contestforecast.objects.filter(starttime__lte=ntime).delete()
    logger = logging.getLogger('log')
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
    logger.info(strs + "forecastdata")
    print("\n"+strs + '\n' + time.strftime("%Y-%m-%d %H:%M:%S",(time.localtime(int(contest['starttime'])))))

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
                datautils.saveCFstatu(stu.stuNO,stu.realName,data['cid'],
                contest.cname,data['time'],data['tags'],data['statu'],data['index'],data['subid'],data['language'])
        for stu in students:
            try:
                datautils.cfsolvereset(stuNO,cid)
            except:
                pass
        strs += contest.cname + ':' + str(len(datalist)) +'\n'
    datautils.cfstatureset()
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['cfAfterContestSubmitUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))
    context = {'str': strs }

def updateCFDataByContest(): #codeforces比赛更新
    logger = logging.getLogger('log')
    str = "CF Data, successed list:"
    str += datautils.saveCFDataByContest()
    datautils.cftimesreset()#供测试阶段调试使用，正式上线请将cftimes调整至准确再使用递增方法
    logger.info(str)
    context = {'str': str}
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['cfContestUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w"))

def updataweightratingstatistics():      #更新权重
    students = Student.objects.all()
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
        count = stu.cfRating + div1 * 30 + div2 * 20 + div3 * 10 +stu.correct_cf_aftersolve * 5 + stu.acRating
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

def jskdataupdate(): #计蒜客数据更新
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
    logger.info(strs)
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['jskUpdatTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w")) 
    
def updateACSubmit():
    logger = logging.getLogger("log")
    logger.info("start updateACSubmit")
    atcoder.UpdateACAfterSolve()
    atcoder.resetACContestSolveAll()
    logger.info("end updateACSubmit")
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acAfterContestSubmitUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w")) 

def updateACCode():
    logger = logging.getLogger("log")
    logger.info("start updateACCode")
    atcoder.getCodeUpdate()
    logger.info("end updateACCode")
    timelist  = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"r"))
    timelist['acCodeUpdateTime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    json.dump(timelist,open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"updatetime.json"),"w")) 