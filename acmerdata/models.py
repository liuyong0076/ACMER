from django.db import models
import time

# cd E:\刘勇团队文件\项目相关\程序代码\PY-2020-ACM\mycode\acmer
# python manage.py makemigrations acmerdata
# python manage.py sqlmigrate acmerdata 0001
# python manage.py migrate
# python manage.py runserver
# python manage.py shell  

# Create your models here.

class Student(models.Model):
    stuNO = models.CharField(max_length=100, default='')
    realName = models.CharField(max_length=100, default='')
    className = models.CharField(max_length=100, default='')
    year = models.IntegerField(default='0')
    acID = models.CharField(max_length=100, default='')
    cfID = models.CharField(max_length=100, default='')
    vjID = models.CharField(max_length=100, default='')
    ncID = models.CharField(max_length=100, default='')
    acRating = models.IntegerField(default=0)
    cfRating = models.IntegerField(default=0)
    ncRating = models.IntegerField(default=0)
    acTimes = models.IntegerField(default=0)
    cfTimes = models.IntegerField(default=0)
    ncTimes = models.IntegerField(default=0)
    all_cf_aftersolve = models.IntegerField(default=0)
    correct_cf_aftersolve = models.IntegerField(default=0)
    isActive = models.IntegerField(default=1)
    school = models.CharField(default='北京化工大学',max_length=100)

    def __str__(self):
        return self.className + self.realName

class Contest(models.Model):
    cid = models.IntegerField(default=0)
    cname = models.CharField(max_length=1000,default='')
    cdate = models.CharField(max_length=100,default='')
    cdiv = models.CharField(max_length=100,default=0)
    ctype = models.CharField(max_length=100,default='')
    cnumber = models.IntegerField(default=-1)
    starttimestamp = models.IntegerField(default=0)
    endtimestamp = models.IntegerField(default=0)
    
    def __str__(self):
        return self.cdate + self.cname

class StudentContest(models.Model):
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
    def __str__(self):
        return self.stuNO + self.cname

class CFContest(models.Model):
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
    def __str__(self):
        return self.stuNO + self.cname + self.index +self.statu



class AddStudentqueue(models.Model):
    stuNO = models.CharField(max_length=100, default='')
    realName = models.CharField(max_length=100, default='')
    className = models.CharField(max_length=100, default='')
    school = models.CharField(default='北京化工大学',max_length=100)
    year = models.IntegerField(default='2019')
    acID = models.CharField(max_length=100, default='',blank=True)
    accheck = models.BooleanField()
    cfID = models.CharField(max_length=100, default='')
    cfcheck = models.BooleanField()
    vjID = models.CharField(max_length=100, default='',blank=True)
    ncID = models.CharField(max_length=100, default='',blank=True)
    execution= models.NullBooleanField()
    execution_statu = models.BooleanField()
    execution_time = models.CharField(max_length=100, default='',blank=True)
    request_time = models.CharField(max_length=100, default='')


    def __str__(self):
        return self.realName + "execution:" + str(self.execution) + "statu:" + str(self.execution_statu)

class studentgroup(models.Model):
    groupstuID = models.TextField(default='',max_length=330)
    remark = models.CharField(default='',max_length=100)
    studentNames = models.TextField(default='')
    enable = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id) + '.' +self.studentNames

class Contestforecast(models.Model):
    ctype = models.CharField(default='',max_length=100)
    cid = models.IntegerField(default=0)
    cname = models.CharField(default='',max_length=100)
    starttime = models.IntegerField(default=0)
    link = models.CharField(default='',max_length=1000)
    during = models.CharField(default='',max_length=100)
    def __str__(self):
        return self.cname + 'start:' + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.starttime))

class AddContestprize(models.Model):
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

class Weightrating(models.Model):
    stuNO = models.CharField(max_length=100, default='')
    realName = models.CharField(max_length=100, default='')
    className = models.CharField(max_length=100, default='')
    div1 = models.IntegerField(default=0)
    div2 = models.IntegerField(default=0)
    div3 = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    cfRating = models.IntegerField(default=0)
    acRating = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    after = models.CharField(default='',max_length=100)