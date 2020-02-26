from django.forms import ModelForm
from django.db import models
from django import forms
from .models import AddStudentqueue,studentgroup
from django.utils.translation import ugettext_lazy as _
class Addstudent(ModelForm):
    class Meta:
        sexchoice = (
            ('',''),
            ('女',"女"),
            ('男',"男"),
        )
        typechoice = (
            ('create','创建'),
            ('update','更新'),
        )
        model = AddStudentqueue
        fields = ['atype','stuNO','realName','sex','className','school','year','acID','cfID','vjID','ncID']
        widgets = {
            'sex' : forms.widgets.Select(attrs={'class':'form-control'},choices=sexchoice),
            'atype' : forms.widgets.Select(attrs={'class':'form-control','onchange':'typechange()'},choices=typechoice),
            'stuNO' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'realName' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'className' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'year' : forms.widgets.NumberInput(attrs={'class':'form-control'}),
            'acID' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'cfID' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'vjID' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'ncID' : forms.widgets.TextInput(attrs={'class':'form-control'}),
            'school' : forms.widgets.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'atype' :_('操作类型'),
            'sex' :_('性别'),
            'stuNO': _('学号'),
            'realName':_('姓名'),
            'className':_('班别'),
            'year':_('年级'),
            'acID':_('AtcoderID'),
            'cfID':_('CodeforcesID'),
            'vjID':_('VirtualJudgeID'),
            'ncID':_('牛客网ID'),
            'school' : _('学校'),
        }
        help_texts = {
            'cfID': _('codeforces网站ID，请注意不要有多余空格'),
            'ncID': _('nowcoder网站ID，请注意不是昵称，而是系统生成的数字'),
        }
        error_messages = {
            'realName': {
                'max_length': _("This writer's name is too long."),
            },
        }

class Addgroup(ModelForm):
    class Meta:
        model = studentgroup
        fields = ['groupstuID','remark']
        widgets = {
            'groupstuID' : forms.widgets.Textarea(attrs={'class':'form-control'}),
            'remark' : forms.widgets.TextInput(attrs={'class':'form-control'}), 
        }
        labels = {
            'groupstuID' : _('成员学生号'),
            'remark' : _('标识')
        }
        help_texts = {
            'groupstuID':_('请用,分割成员名,否则无法添加'+'\n'+'例:2019010101,2019010102,2019010103 \n（最大上限30人)')
        }
        error_messages = {
            'groupstuID': {
                'max_length': _("最大上限30人,如未超过30人请注意是否有多余分隔符"),
            }
        }

class addprize(forms.Form):
    contestchoice = (
        ("",""),
        ('ICPC国际大学生程序设计竞赛','ICPC国际大学生程序设计竞赛'),
        ('CCPC中国大学生程序竞赛','CCPC中国大学生程序竞赛'),
        ('CCPC-wFinal中国大学生程序设计竞赛女生专场','CCPC-wFinal中国大学生程序设计竞赛女生专场'),
        ('CCPC河北省大学生程序设计竞赛','CCPC河北省大学生程序设计竞赛'),
        ("蓝桥杯全国软件和信息技术专业人才大赛","蓝桥杯全国软件和信息技术专业人才大赛"),
        ('团体程序设计天梯赛','团体程序设计天梯赛'),
    )
    yearcholce = (
        (2019,'2019'),
        (2018,'2018'),
        (2017,'2017'),
        (2016,'2016'),
        (2015,'2015'),
    )
    monthchoice = (
        (12,"12"),
        (11,"11"),
        (10,"10"),
        (9,"9"),
        (8,"8"),
        (7,"7"),
        (6,"6"),
        (5,"5"),
        (4,"4"),
        (3,"3"),
        (2,"2"),
        (1,"1"),
    )
    levelchoice = (
        ('国际级','国际级'),
        ('国家级','国家级'),
        ('省部级','省部级'),
    )
    yearcho=('2019','2018','2017','2016','2015')
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}),label="姓名")
    classname = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}),label="班别")
    year = forms.IntegerField(widget=forms.Select(attrs={'class':'form-control'},choices=yearcholce),label="年级")
    stuNO = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}),label="学号")
    contestname = forms.CharField(max_length=100,widget=forms.Select(attrs={'class':'form-control','id':'cname','onchange':"getchange(this.id)"},choices=contestchoice),label="比赛")
    cyear = forms.IntegerField(widget=forms.Select(attrs={'class':'form-control'},choices=yearcholce),label="年份")
    prize = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}),label="奖项")
    level = forms.CharField(initial="国家级",widget=forms.Select(attrs={'class':'form-control','id':'level',},choices=levelchoice),label="比赛等级",disabled=True)
