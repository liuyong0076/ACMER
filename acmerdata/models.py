from django.db import models
import time
class Student(models.Model):    #学生模型
    stuNO = models.CharField(max_length=100, default='')
    realName = models.CharField(max_length=100, default='')
    className = models.CharField(max_length=100, default='')
    sex = models.CharField(max_length=100,default='男')
    year = models.IntegerField(default='0')
    acID = models.CharField(max_length=100, default='')
    cfID = models.CharField(max_length=100, default='')
    vjID = models.CharField(max_length=100, default='')
    ncID = models.CharField(max_length=100, default='')
    jskID = models.CharField(max_length=100,default='')
    acRating = models.IntegerField(default=0)
    cfRating = models.IntegerField(default=0)
    ncRating = models.IntegerField(default=0)
    jskRating = models.IntegerField(default=0)
    acTimes = models.IntegerField(default=0)
    cfTimes = models.IntegerField(default=0)
    ncTimes = models.IntegerField(default=0)
    jskTimes = models.IntegerField(default=0)
    all_cf_aftersolve = models.IntegerField(default=0)
    correct_cf_aftersolve = models.IntegerField(default=0)
    all_ac_aftersolve = models.IntegerField(default=0)
    correct_ac_aftersolve = models.IntegerField(default=0)
    isActive = models.IntegerField(default=1)
    school = models.CharField(default='',max_length=100)

    def __str__(self):
        return self.className + self.realName

class Contest(models.Model):    #比赛模型
    cid = models.IntegerField(default=0)
    cname = models.CharField(max_length=1000,default='')
    cdate = models.CharField(max_length=100,default='')
    cdiv = models.CharField(max_length=100,default=0)
    ctype = models.CharField(max_length=100,default='')
    cnumber = models.IntegerField(default=-1)
    starttimestamp = models.IntegerField(default=0)
    endtimestamp = models.IntegerField(default=0)
    nickName = models.CharField(default='',max_length=100,blank=True)
    questionnum = models.IntegerField(default=0)
    def __str__(self):
        return self.cdate + self.cname

class StudentContest(models.Model):     #学生参赛记录模型
    stuNO = models.CharField(max_length=100)
    realName = models.CharField(max_length=100, default='')
    className = models.CharField(max_length=100, default='')
    cid = models.IntegerField(default=0)
    cname = models.CharField(max_length=1000)
    cdate = models.CharField(max_length=100)
    cdiv = models.CharField(max_length=100)
    ctype = models.CharField(max_length=100,default='')
    rank = models.IntegerField()
    newRating = models.IntegerField()
    diff = models.CharField(max_length=100,default=0) # you should use char to save diff like '+20' or '-20'
    solve = models.CharField(max_length=100,default="no data")#牛客数据与cf数据不相同，故用char进行存储
    aftersolve = models.CharField(max_length=100,default="no data")
    nickName = models.CharField(default='',max_length=100,blank=True)
    def __str__(self):
        return self.stuNO + self.cname

class CFContest(models.Model):  #codeforce提交代码模型
    stuNO = models.CharField(max_length=100)
    realName = models.CharField(max_length=100, default='')
    ctime = models.IntegerField(default=0)
    cid = models.IntegerField(default=0)
    cname = models.CharField(max_length=1000)
    cdiv = models.CharField(max_length=100)
    subid = models.IntegerField(default=0)
    code = models.TextField(default='')
    tag = models.CharField(default='',max_length=200)
    index = models.CharField(default='',max_length=200)
    statu = models.CharField(default='',max_length=100)
    language = models.CharField(default='',max_length=100)
    def __str__(self):
        return self.stuNO + self.cname + self.index +self.statu

class ACContest(models.Model):
    stuNO = models.CharField(max_length=100)
    realName = models.CharField(max_length=100, default='')
    ctime = models.IntegerField(default=0)
    nickName = models.CharField(default='',max_length=100)
    cname = models.CharField(max_length=1000)
    subid = models.IntegerField(default=0)
    code = models.TextField(default='')
    task = models.CharField(default='',max_length=200)
    statu = models.CharField(default='',max_length=100)
    language = models.CharField(default='',max_length=100)
    def __str__(self):
        return self.stuNO + self.cname + self.index +self.statu

class AddStudentqueue(models.Model):    #添加学生缓冲队列
    stuNO = models.CharField(max_length=100, default='')
    realName = models.CharField(max_length=100, default='',blank=True)
    sex = models.CharField(max_length=2,default="",blank=True)
    className = models.CharField(max_length=100, default='',blank=True)
    school = models.CharField(default='',max_length=100,blank=True)
    year = models.CharField(default='',blank=True,max_length=5)
    acID = models.CharField(max_length=100, default='',blank=True)
    accheck = models.BooleanField()
    cfID = models.CharField(max_length=100, default='',blank=True)
    cfcheck = models.BooleanField()
    vjID = models.CharField(max_length=100, default='',blank=True)
    ncID = models.CharField(max_length=100, default='',blank=True)
    jskID = models.CharField(max_length=100, default='',blank=True)
    execution= models.NullBooleanField()
    execution_statu = models.BooleanField()
    execution_time = models.CharField(max_length=100, default='',blank=True)
    request_time = models.CharField(max_length=100, default='')
    atype = models.CharField(max_length=100,default="")

    def __str__(self):
        return self.realName + "execution:" + str(self.execution) + "statu:" + str(self.execution_statu)

class studentgroup(models.Model):   #比较组模型
    groupstuID = models.TextField(default='',max_length=330)
    remark = models.CharField(default='',max_length=100)
    studentNames = models.TextField(default='')
    enable = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id) + '.' +self.studentNames

class Contestforecast(models.Model):    #比赛预报模型
    ctype = models.CharField(default='',max_length=100)
    cid = models.IntegerField(default=0)
    cname = models.CharField(default='',max_length=100)
    starttime = models.IntegerField(default=0)
    link = models.CharField(default='',max_length=1000)
    during = models.CharField(default='',max_length=100)
    def __str__(self):
        return self.cname + 'start:' + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.starttime))

class AddContestprize(models.Model):    #比赛奖项模型,未完全开发
    name = models.CharField(default='',max_length=100)
    className = models.CharField(default='',max_length=100)
    stuNO = models.IntegerField(default=0)
    stuyear = models.IntegerField(default=0)
    cname = models.CharField(default='',max_length=100)
    cyear = models.IntegerField(default=0)
    clevel = models.CharField(default='',max_length=100)
    prize = models.CharField(default='',max_length=100)
    exe = models.BooleanField(default=False)
    def __str__(self):
        return self.cname +'-'+self.name

class CodeforcesQuestion(models.Model):
    name = models.CharField(default="",max_length=100)
    cid = models.IntegerField(default=0)
    cname = models.CharField(default="",max_length=300)
    index = models.CharField(default="",max_length=100)
    tags = models.CharField(default="",max_length=200)
    mdtext = models.TextField(default="")
    difficulty = models.IntegerField(default=0)
