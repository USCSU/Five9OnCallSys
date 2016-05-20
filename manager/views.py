from django.shortcuts import render,render_to_response,redirect
import json,pytz
from pytz import timezone
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
import csv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings

def getSessionTeamInfo(request):
	username = None
	if request.user.is_authenticated():
		username = request.user.username
	depart = department.objects.filter(employee__email=username)
	return depart

def logSave(name,person,start,end):
	managerObj = employee.objects.filter(department__name = name)& employee.objects.filter(manager=True)
	managername = managerObj[0].firstName + " " + managerObj[0].lastName
	managerlog = log(department = name,manager = managername, startdate=parser.parse(start).strftime("%Y-%m-%d %H:%M"),enddate= parser.parse(end).strftime("%Y-%m-%d %H:%M"),oncallUser = person,logtime=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
	managerlog.save()

def onDutySave(departName,start,end,id):
	depart =  department.objects.get(name = departName)
	emp= employee.objects.get(employeeid =id)
 	duty = onDuty(department = depart,startDate = datetime.strptime(start, "%Y/%m/%d %H:%M %p"),endDate= datetime.strptime(end, "%Y/%m/%d %H:%M %p"), employee= emp )
 	duty.save()

 

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def logformat(opLog):
	logs = []
	for singlelog in opLog:
		row = {}
		row['id'] = singlelog.id
		row['name']='%s %s' %(singlelog.employee.firstName,singlelog.employee.lastName)
		row['startdate'] = singlelog.startDate
		row['enddate'] = singlelog.endDate
		logs.append(row)
	return logs

def index(request,name):
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	team = getSessionTeamInfo(request)
	if not team:
		return render(request,'registration/noactive.html')
	
	currentTeam = team[0].name
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
		
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))

	else:#get method
		emp = employee.objects.filter(department__name =name)
		opLog = onDuty.objects.filter(department__name = name).order_by('-endDate')
		 
		return render(request,'manager/index.html',{'emp':emp,'team':name,  'logs':json.dumps(logformat(opLog),default = json_serial)})

def addSchedule(request,team):
	#avoid cross visit
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	temp = getSessionTeamInfo(request)
	if not temp:
		return render(request,'registration/noactive.html')
	
	currentTeam = temp[0].name
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
		return render(request,'manager/setschedule.html',{'emp':emp,'team':team, 'log':logformat(opLog),'logs':json.dumps(logformat(opLog),default = json_serial)})
def updateSchedule(request,team):
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	temp = getSessionTeamInfo(request)
	if not temp:
		return render(request,'registration/noactive.html')
	
	currentTeam = temp[0].name
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method=='POST':
		start= request.POST.get('startdate')
		end =request.POST.get('enddate')
		logid = request.POST.get('log_id')
		user = onDuty.objects.filter(id=logid)[0].employee
		# user = request.POST.get('user')

		onDuty.objects.filter(id=logid).update(startDate = parser.parse(start).strftime("%Y-%m-%d %H:%M"), endDate = parser.parse(end).strftime("%Y-%m-%d %H:%M"), employee_id = user)

		return HttpResponseRedirect(reverse('managerschdule', args=[team]))
	else:
		return HttpResponse("fail!")

def deleteSchedule(request,team):
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	 
	temp = getSessionTeamInfo(request)
	if not temp:
		return render(request,'registration/noactive.html')
	
	currentTeam = temp[0].name
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method=='POST':
		logid = request.POST.get('log_id')
		onDuty.objects.filter(id=logid).delete()
		return HttpResponseRedirect(reverse('managerschdule', args=[team]))
	else:
		return HttpResponse("fail!")

def readCSV(data):
	
    path = default_storage.save('tmp/' + str(data), ContentFile(data.read()))
    # get all employee id and name pair

    with open(path, 'rb') as csvfile:
    	temp = [row for row in csv.reader(csvfile.read().splitlines())]
    data = []
    for row in temp:
    	if len(row) < 3:
    		continue
    	elif len(row[0].strip()) ==0 or len(row[1].strip())==0 or len(row[2].strip())==0:
    		continue
    	else:
    		data.append(row)
    return data

def employeeIdPair(team):
	emailpair={}
	namepair = {}
	departid = department.objects.get(name = team).departmentid
	employeelist = employee.objects.filter(department_id=departid) #queryset
	for item in employeelist:
		namepair[(item.firstName+''+item.lastName).strip()] = item.employeeid
		emailpair[item.email] = item.employeeid
	return emailpair,namepair,departid

def uploadSchedule(request,team):
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	 
	temp = getSessionTeamInfo(request)
	if not temp:
		return render(request,'registration/noactive.html')
	currentTeam = temp[0].name
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))


	if request.method =='POST':
		# try:
			fileObj = request.FILES['files']
			data = readCSV(fileObj) #current file data
			if not data:
				return render(request,'manager/errorUpload.html',{'team':team})
			emailEmp,nameEmp,departId= employeeIdPair(team) # all current employee list by name and email
			wrongName,wrongFormat,wrongDate,insertionVal,employeeid = examinedata(data,emailEmp,nameEmp,departId)
			if len(wrongDate) ==0 and len(wrongFormat)==0 and len(wrongName) ==0:
				print insertionVal
				#everything is ok, insert into data base
				for record in insertionVal:
					case = onDuty(startDate = parser.parse(record[1]).strftime("%Y-%m-%d %H:%M"),endDate = parser.parse(record[2]).strftime("%Y-%m-%d %H:%M"),department_id=departId,employee_id = employeeid)
					case.save()
				return HttpResponseRedirect(reverse('managerschdule', args=[team]))
			else:
				
				return render(request,'manager/errorDetail.html',{'team':team,'wrongDate':wrongDate,'wrongFormat':wrongFormat,'wrongName':wrongName})
		# except:
			 # return render(request,'manager/errorUpload.html',{'team':team})

def examinedata(data,emailEmp,nameEmp,id):
	wrongName=[]
	wrongDate=[]
	wrongFormat= []
	insertionVal =[] #startdate enddate employee_id department_id
	employeeid=""
	try:
		for row in data:
			# if len(row)<3:
			# 	wrongFormat.append(row)
			# 	continue
			if ((row[0].strip() not in emailEmp) and (row[0].strip() not in nameEmp)):
				wrongName.append(row)
				continue
			elif row[2] and row[1]: #enddate
				tagEndTime = parser.parse(row[2]).strftime("%Y-%m-%d %H:%M")
				tagStartTime = parser.parse(row[1]).strftime("%Y-%m-%d %H:%M")
				current = str(datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific')))
				if tagEndTime < current or tagEndTime < tagStartTime:
					wrongDate.append(row)
				else:
					key = row[0]
					if key in emailEmp:
						employeeid = emailEmp.get(key)
					elif key in nameEmp:
						employeeid = nameEmp.get(key);
					insertionVal.append(row)
				continue
			else:
				wrongFormat.append(row)
	except:
		wrongFormat.append(row)
	return wrongName,wrongFormat,wrongDate,insertionVal,employeeid

def deleteAllSchedule(request,team):
	if not isAuth(request,'managerops') and not isAuth(request,'SME'):
		return HttpResponseRedirect('/')
	 
	temp = getSessionTeamInfo(request)
	if not temp:
		return render(request,'registration/noactive.html')
	
	currentTeam = temp[0].name
	if team != currentTeam:
		return HttpResponseRedirect(reverse('managerindex', args=[currentTeam]))
	if request.method=='POST':
		onDuty.objects.filter(department__name=team).delete()
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
	
