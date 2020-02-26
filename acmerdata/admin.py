from django.contrib import admin

# Register your models here.

from .models import Student, Contest, StudentContest,AddStudentqueue,studentgroup,Contestforecast

def execute_execution_reject(odeladmin, request, queryset):
    queryset.update(execution=False)
def execute_execution_accept(odeladmin, request, queryset):
    queryset.update(execution=True)
execute_execution_accept.short_description = "Accept Student"
execute_execution_reject.short_description = "Reject Student"
class AddAdmin(admin.ModelAdmin):
    list_display = ('stuNO', 'realName','className','sex','year','acID','accheck','cfID','cfcheck',
    'vjID','ncID','execution','request_time','execution_statu','execution_time'
    )
    actions = [execute_execution_reject,execute_execution_accept]



admin.site.register(Student)
admin.site.register(Contest)
admin.site.register(StudentContest)
admin.site.register(AddStudentqueue,AddAdmin)
admin.site.register(studentgroup)
admin.site.register(Contestforecast)
