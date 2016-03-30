from django.contrib import admin
from manager.models import employee
from .models import log
from manager.models import department

class departmentAdmin(admin.ModelAdmin):
	list_display=['name']

class employeeAdmin(admin.ModelAdmin):
	list_display = ['firstName','lastName','email','phone']

class logAdmin(admin.ModelAdmin):
	list_display = ['datetime','oncallUser']

admin.site.register(employee,employeeAdmin)
admin.site.register(log,logAdmin)
admin.site.register(department,departmentAdmin)
