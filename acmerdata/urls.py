from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #data show
    path('contests', views.contests, name='contests'),
    path('contestforecast',views.contestforecast,name='contestforecast'),
    path('contest/<int:contest_id>', views.contest, name='contest'),
    path('cf/<int:cid>',views.cfcontestsubmit,name='cfcontest'),
    path('cfsubmit/<int:submitid>',views.viewcode,name='viewcode'),
    path('contestFromStudent/<int:studentcontest_id>', views.contest, name='contest'),
    path('student/<str:stuNO>', views.student, name='student'),
    path('addstudent',views.Addstudentdata,name='add'),
    path('addstudentslist',views.addstatu,name='addstatu'),
    path('aftercf/<str:stuNO>',views.aftersolve,name='aftersolve'),
    path('addprizet',views.addprizet,name='addprize'),
    path('weightratingstatistic',views.weightratingstatistic,name="weightratingstatistics"),
    path('monthlyrating/<str:year>/<str:month>',views.monthlyrating,name="monthlyrating"),
    path('monthlyrating',views.monthlyrating,name="monthlyrating"),
    #group
    path('group',views.group,name='group'),
    path('group/del/<int:groupid>',views.groupdel,name='groupdel'),
    path('group/ratingline/<int:groupid>',views.groupRatingLine,name='groupdata'),
    path('group/data/<int:groupid>',views.groupdata,name='groupdata'),
    #bsdata
    path('fixcodeerrorforinternetproblem',views.fixcodeerrorforinternetproblem,name='fixcodeerror'),
    path('fixcodeerrorforlanguageerror',views.fixcodeerrorforlanguageerror,name='fixcodeerror'),
    path('cfcontestsubmitupdatebycontest',views.cfcontestsubmitupdatebycontest,name='cfcontestsubmitupdatebycontest'),
    path('updateforecastlist',views.updateforecastlist,name='updateforecastlist'),
    path('spider', views.spider, name='spider'),
    path('updateStudentlist',views.updatestudentlist,name='updatelist'),
    path('getNCData', views.getNCData,name='getNCData'),
    path('getCFData', views.getCFData, name='getCFData'),
    path('updateCFDataByContest', views.updateCFDataByContest, name='updateCFDataByContest'),
    path('getACData', views.getACData, name='getACData'),
    path('standardizecftime',views.Standardizecftime,name='Standardizecftime'),
    path('setallcontestsolve',views.setallcontestsolve,name='setallcontestsolve'),
    path('setallaftersolve',views.setallaftersolve,name='setallaftersolve'),
    path('updataweightratingstatistics',views.updataweightratingstatistics,name="updatacfstatistics"),
    path('jskdataupdate',views.jskdataupdate,name='jskdataupdate'),
    
    # data visualization
    path('cftimeline', views.cftimeline, name='cftimeline'),
    path('groupRatingLine', views.groupRatingLine, name='groupRatingLine'),
    path('timeline', views.timeline, name='timeline'),
    #etc
    path('contact', views.contact, name='contact'),
    path('fixbug', views.fixbug, name='fixbug'),
]