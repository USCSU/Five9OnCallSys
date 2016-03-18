from django.shortcuts import render,render_to_response
from manager.models import department
from manager.models import employee
from manager.models import log
from manager.models import onDuty
from dateutil import parser
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from login.views import isAuth
 

def index(request,name):
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')

	if request.method == 'POST':
	#take request from html page
		start= request.POST.get('startdate')
		end =request.POST.get('enddate')
		idlist = request.POST.getlist('employee')
		depart =  department.objects.get(name = name)
		employeelist = []
		for item in idlist:
		 	emp= employee.objects.get(employeeid =item)
		 	employeelist.append(emp)
		 	duty = onDuty(department = depart,startDate = parser.parse(start).strftime("%Y-%m-%d"),endDate= parser.parse(end).strftime("%Y-%m-%d"), employee= emp )
		 	duty.save()
		print employeelist

		#update log file 
		
		managerObj = employee.objects.filter(department__name = name)& employee.objects.filter(manager=True)
		managername = managerObj[0].firstName + " " + managerObj[0].lastName
		for person in employeelist:
			managerlog = log(department = depart,manager = managername, startdate=parser.parse(start).strftime("%Y-%m-%d"),enddate= parser.parse(end).strftime("%Y-%m-%d"),oncallUser = person,logtime=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
		  	managerlog.save()
		return render(request,'manager/success.html');

	else:
		emp = employee.objects.filter(department__name =name)
		opLog = onDuty.objects.filter(department__name = name).order_by('-endDate')
		
		logs = []
		logs.append('{:<10}  {:<9} {:<10} {:<10}'.format('FirstName:', 'LastName:','','Schedule:'))

		for singlelog in opLog:
			worker = singlelog.employee 
			workername = '{:<10}  {:<9} '.format(worker.firstName, worker.lastName)
			content = workername +" will be on scheudle from " + str(singlelog.startDate) + " to " +str(singlelog.endDate)
			logs.append(content)
		if not logs:
			logs.append("No schedule for your team yet")
		return render(request,'manager/index.html',{'emp':emp,'team':name,'log':logs})

@login_required(redirect_field_name='homepage')
def home(request):
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')

	items = department.objects.all()
	return render(request,'manager/home.html',{
		 'items':items,
		 })

