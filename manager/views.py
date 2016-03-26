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

def logSave(name,person,start,end):
	managerObj = employee.objects.filter(department__name = name)& employee.objects.filter(manager=True)
	managername = managerObj[0].firstName + " " + managerObj[0].lastName
	managerlog = log(department = name,manager = managername, startdate=parser.parse(start).strftime("%Y-%m-%d"),enddate= parser.parse(end).strftime("%Y-%m-%d"),oncallUser = person,logtime=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
	managerlog.save()

def onDutySave(departName,start,end,id):
	depart =  department.objects.get(name = departName)
	emp= employee.objects.get(employeeid =id)
 	duty = onDuty(department = depart,startDate = parser.parse(start).strftime("%Y-%m-%d"),endDate= parser.parse(end).strftime("%Y-%m-%d"), employee= emp )
 	duty.save()

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
		row['id'] = singlelog.id
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
		onDutySave(name, start,end,idlist)
		
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
		idlist = request.POST.get('user')
		 
		#onduty log file
		onDutySave(team, start,end,idlist)
		
		#update log file 
		logSave(team,idlist,start,end)
		
		return HttpResponseRedirect(reverse('managerschdule', args=[team]))
	else:#get method
		emp = employee.objects.filter(department__name =team)
		opLog = onDuty.objects.filter(department__name = team).order_by('-endDate')



		return render(request,'manager/setschedule.html',{'emp':emp,'team':team, 'log':logformat(opLog),'logs':json.dumps(logformat(opLog))})
def updateSchedule(request,team):
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')
	currentTeam = getSessionTeamInfo(request)
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method=='POST':
		start= request.POST.get('startdate')
		end =request.POST.get('enddate')
		user = request.POST.get('user')
		logid = request.POST.get('log_id')
		onDuty.objects.filter(id=logid).update(startDate = parser.parse(start).strftime("%Y-%m-%d"), endDate = parser.parse(end).strftime("%Y-%m-%d"), employee_id = user)

		return HttpResponseRedirect(reverse('managerschdule', args=[team]))
	else:
		return HttpResponse("fail!")

def deleteSchedule(request,team):
	if not isAuth(request,'managerops'):
		return HttpResponseRedirect('/manager/login/')
	currentTeam = getSessionTeamInfo(request)
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method=='POST':
		logid = request.POST.get('log_id')
		onDuty.objects.filter(id=logid).delete()
		return HttpResponseRedirect(reverse('managerschdule', args=[team]))
	else:
		return HttpResponse("fail!")

def deleteEntry(request, id):
	return HttpResponse("<p>The entry is deleted</p>")
# def home(request):
# 	if not isAuth(request,'managerops'):
# 		return HttpResponseRedirect('/manager/login/')
# 	# return index(request,depart.name)
# 	return HttpResponseRedirect(reverse('managerindex', args=[getSessionTeamInfo(request)]))
	 
