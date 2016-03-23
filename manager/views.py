from django.shortcuts import render,render_to_response,redirect
import json
from django.core.urlresolvers import reverse
from manager.models import department
from manager.models import employee
from manager.models import log
from manager.models import onDuty
from dateutil import parser
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from login.views import isAuth
from .forms import managerOpsForm

def getSessionTeamInfo(request):
	username = None
	if request.user.is_authenticated():
		username = request.user.username
	depart = department.objects.filter(employee__email=username)[0]
	return depart.name

def logSave(name,employeelist,start,end):
	managerObj = employee.objects.filter(department__name = name)& employee.objects.filter(manager=True)
	managername = managerObj[0].firstName + " " + managerObj[0].lastName
	for person in employeelist:
		managerlog = log(department = name,manager = managername, startdate=parser.parse(start).strftime("%Y-%m-%d"),enddate= parser.parse(end).strftime("%Y-%m-%d"),oncallUser = person,logtime=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
		managerlog.save()

def onDutySave(departName,start,end,idlist):
	depart =  department.objects.get(name = departName)
	employeelist = []
	for item in idlist:
	 	emp= employee.objects.get(employeeid =item)
	 	employeelist.append(emp)
	 	duty = onDuty(department = depart,startDate = parser.parse(start).strftime("%Y-%m-%d"),endDate= parser.parse(end).strftime("%Y-%m-%d"), employee= emp )
	 	duty.save()
	return employeelist

def logFormat1(opLog):
	logs = []
	logs.append('{:<10}  {:<9} {:<10} {:<10}'.format('FirstName:', 'LastName:','','Schedule:'))

	for singlelog in opLog:
		worker = singlelog.employee 
		workername = '{:<10}  {:<9} '.format(worker.firstName, worker.lastName)
		content = workername +" will be on scheudle from " + str(singlelog.startDate) + " to " +str(singlelog.endDate)
		logs.append(content)
	if not logs:
		logs.append("No schedule for your team yet")
	return logs
def logformat(opLog):
	logs = []
	for singlelog in opLog:
		row = {}
		row['name']='%s %s' %(singlelog.employee.firstName,singlelog.employee.lastName)
		row['startdate'] = str(singlelog.startDate)
		row['enddate'] = str(singlelog.endDate)
		logs.append(row)
	return logs

def index(request,name):
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')
	currentTeam = getSessionTeamInfo(request)
	if name != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))

	if request.method == 'POST':
		#take request from html page
		start= request.POST.get('startdate')
		end =request.POST.get('enddate')
		idlist = request.POST.getlist('employee')
	
		#onduty log file
		employeelist = onDutySave(name, start,end,idlist)
		
		#update log file 
		logSave(name,employeelist,start,end)
		
		return HttpResponseRedirect(reverse('managerindex', args=[getSessionTeamInfo(request)]))

	else:#get method
		emp = employee.objects.filter(department__name =name)
		opLog = onDuty.objects.filter(department__name = name).order_by('-endDate')
		 

		return render(request,'manager/index.html',{'emp':emp,'team':name,  'logs':json.dumps(logformat(opLog))})

def addSchedule(request,team):
	#avoid cross visit
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')
	currentTeam = getSessionTeamInfo(request)
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method == 'POST':
		#take request from html page
		start= request.POST.get('startdate')
		end =request.POST.get('enddate')
		idlist = request.POST.getlist('employee')

		#onduty log file
		employeelist = onDutySave(name, start,end,idlist)
		
		#update log file 
		logSave(name,employeelist,start,end)
		
		return HttpResponseRedirect(reverse('managerindex', args=[getSessionTeamInfo(request)]))
	else:#get method
		emp = employee.objects.filter(department__name =team)
		opLog = onDuty.objects.filter(department__name = team).order_by('-endDate')
		 

		return render(request,'manager/setschedule.html',{'emp':emp,'team':team,  'logs':json.dumps(logformat(opLog))})
	 
# def home(request):
# 	if not isAuth(request,'managerops'):
# 		return HttpResponseRedirect('/manager/login/')
# 	# return index(request,depart.name)
# 	return HttpResponseRedirect(reverse('managerindex', args=[getSessionTeamInfo(request)]))
	 
