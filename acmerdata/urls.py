from django.urls import path

from . import views,viewsVisualData

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

    path('monthlyrating/<str:year>/<str:month>',views.monthlyrating,name="monthlyrating"),
    path('monthlyrating',views.monthlyrating,name="monthlyrating"),
    path('studentmonthlys/<str:stuNO>',views.studentmonthlys,name='studentmonthlys'),
    path('monthlysub/<str:type>/<str:stuNO>/<str:year>/<str:month>',views.monthlysub,name='monthlysub'),
    path('ac/<str:nickName>',views.acContestSubmit,name='acContestSubmit'),
    path('acsubmit/<int:submitID>',views.viewACCode,name='viewACCode'),
    path('afterac/<str:stuNO>',views.afterSolveAC,name='afterSolveAC'),
    path('CodeforcesQuestionsview/<int:cid>/<str:index>',views.CodeforcesQuestionsview,name="CodeforcesQuestionsview"),
    path('Problemset/<str:tag>',views.Problemset,name="Problemset"),
    #group
    path('group',viewsVisualData.group,name='group'),
    path('group/del/<int:groupid>',viewsVisualData.groupdel,name='groupdel'),
    path('group/data/<int:groupid>',viewsVisualData.groupdata,name='groupdata'),
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
    path('updateCodeforcesQuestion',views.updateCodeforcesQuestion,name="updateCodeforcesQuestion"),
    path('jskdataupdate',views.jskdataupdate,name='jskdataupdate'),
    path('fixacdiff',views.fixacdiff,name='fixacdiff'),
    path('getaccode/<str:utype>',views.getACCode,name="getACCode"),
    path('updateACDataByContest',views.updateACDataByContest,name='updateACDataByContest'),
    
    # data visualization
    path('group/ratingline/<str:groupid>',viewsVisualData.groupRatingLine,name='groupdata'),
    path('groupRatingLine', viewsVisualData.groupRatingLine, name='groupRatingLine'),
    path('timeline', viewsVisualData.timeline, name='timeline'),
    path('teamMembersCount',viewsVisualData.teamMembersCount,name="teamMembersCount"),
    path('topCompare',viewsVisualData.topCompare,name="topCompare"),
    path('contestCount',viewsVisualData.contestCount,name="contestCount"),
    path('groupTagLine/<str:groupid>',viewsVisualData.groupTagCompare,name="groupTagCompare"),
    path('groupTagPolor/<str:groupid>',viewsVisualData.groupTagPolor,name="groupTagPolor"),
    #etc
    path('contact', views.contact, name='contact'),
    path('fixbug', views.fixbug, name='fixbug'),
]