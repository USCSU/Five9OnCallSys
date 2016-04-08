import smtplib
import json
import pytz
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from manager.models import department,employee,onDuty
from noc.forms import NocOpsForm
from noc.models import log
from datetime import datetime
from sets import Set
from django.contrib.auth.decorators import login_required
from login.views import isAuth
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from pytz import timezone
from dateutil import parser

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def getPSTDateTime():
	return datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific'))
def getcurrentPST():
	format = "%Y-%m-%d %H:%M"
	return getPSTDateTime().strftime(format)
def getNext24PST():
	format = "%Y-%m-%d %H:%M"
	current = getPSTDateTime()
	next24=current.replace(day = current.day+1)
	return next24.strftime(format)

def logFormat():
	logs=[]
	#take top 40 records in desc order
	Oplogs = log.objects.all().order_by('-datetime')[:40]
	#take list of departments
	# listOfDepartments = department.objects.all()
	for singlelog in Oplogs:
		temp = []
		temp.append(singlelog.datetime)
		temp.append(singlelog.ticketnumber)
		departlist=""
		for item in singlelog.departments:
			departlist+=item
		temp.append("Logged") if not singlelog.escalate else temp.append("Escalted");
		temp.append(departlist)
		logs.append(temp)
	return logs#,listOfDepartments

def send_email(user, pwd, recipient, subject, body):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        # server = smtplib.SMTP("intranetdev001.scl.five9.com", 25)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

'''
this function is mainly to retrieve manager's name  with input from form submission
'''
def getManager(depart_name): 
	managerItem = (employee.objects.filter(department__name = depart_name) & employee.objects.filter(manager='true'))[0]
	return managerItem

def getManagers(listOfDepartments):
	managerList = []
	for item in listOfDepartments:
		managerList.append(getManager(item).phone)
	return managerList
'''
This funciton is mainly to retrieve employees who will take the duty for one department
'''
def getOnCallEmployee(depart_name):
	emaillist = []
	currentTime = getcurrentPST() #get pst time
	ondutylist = onDuty.objects.filter(department__name =depart_name).filter(startDate__lte= currentTime).filter(endDate__gte=currentTime)
	print "onduty"
	print ondutylist
	if not ondutylist: # if no employee is on duty, the ticket will be sent to corresponding manager
		manager = employee.objects.filter(department__name=depart_name).filter(manager = True)
		emaillist.append(manager[0].phone)
	else:
		for item in ondutylist:
			emaillist.append(item.employee.phone)

	return emaillist
'''
The function takes list of departments as input, return all corresponding employees who should take oncall requests
'''
def getOnCallEmployees(listOfDepartments):
	oncalllist = []
	for item in listOfDepartments:
		oncalllist.extend(getOnCallEmployee(item))
	return oncalllist
'''
Index page of noc module
'''
def addTicket(request):
	if request.method == 'POST':	 
		form = NocOpsForm(request.POST)
		escalate = [str(x) for x in request.POST.getlist('escalate')]
		departlist = [str(x) for x in request.POST.getlist('depart')]
		print escalate
		print departlist
		if form.is_valid() or not escalate and not departlist:
			#receive request's paramter from html
			escalateList =  Set(getManagers(escalate))
			oncallList = Set(getOnCallEmployees(departlist))
			ticket = form.cleaned_data['Ticket']#list(oncallList)
			#email sent
			if bool(oncallList):
				send_email("chris.sufive9@gmail.com", "Five9ossqa",list(oncallList), " Outrage bridge#:925-201-2000", "Outage/Service Alert #: "+ticket) 
				# send_email("@five9.com", "Five9ossqa",list(oncallList), " Outrage bridge#:925-201-2000", "Outage/Service Alert #: "+ticket) 
			if bool(escalateList):	
				send_email("chris.sufive9@gmail.com", "Five9ossqa",list(escalateList), "Outrage bridge#:925-201-2000", "Outage/Service Alert #:"+ticket) 
			
			#update log of Noc operation
			print "---"
			print oncallList 
			print "+++"
			print escalateList
			if bool(oncallList):
				record = log(datetime = getcurrentPST(), ticketnumber = ticket, oncallUser = list(oncallList) , departments = list(departlist),escalate = False)
				record.save()
			if bool(escalateList):	
				record = log(datetime = getcurrentPST(), ticketnumber = ticket, oncallUser = list(escalateList) , departments = list(escalate),escalate = True)
				record.save()
			return HttpResponseRedirect('/noc');
		else:
			return render(request,'noc/no_data.html');
	else:
		form = NocOpsForm()
		listOfDepartments = department.objects.all()
	return render(request,'noc/addTicket.html',{'form':form,  'listOfDepartments':listOfDepartments})
def index(request):
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/noc/login/')
	
	logs = logFormat()
	return render(request,'noc/index.html',{ 'log':logs})

def filterDepartmentName(team):
	result = ""
	if 'IT' in team:
		result = 'IT' 
	if 'INFO' in team:
		result = 'INFO' 
	if 'Center' in team:
		result = 'DCNTER' 
	if 'SYS' in team:
		result = 'SYS' 
	if 'Network' in team:
		result = 'Network' 
	if 'NOC' in team:
		result = 'NOC' 
	if 'DB' in team:
		result = 'DB' 
	
	return result
'''format the query from database; list is db query set'''
def dutylistFormat():
	dutylist = []
	dbquery = onDuty.objects.all()
	for singlelog in dbquery:
		row = {}
		row['id'] = singlelog.id
		team = department.objects.filter(departmentid =singlelog.department_id)[0].name

		row['name']='%s:%s %s' %(filterDepartmentName(team),singlelog.employee.firstName,singlelog.employee.lastName)
		row['startdate'] = singlelog.startDate
		row['enddate'] = singlelog.endDate
		dutylist.append(row)
	return dutylist

''' check SME view page'''
def checkSME(request):
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/noc/login/')
	return render(request,'noc/checkSME.html',{'logs':json.dumps(dutylistFormat(),default = json_serial)});

def getOnDutyByDeparment(nameOfDepart,next24,current):
	log = []

	ondutyobjs  = onDuty.objects.filter(department__name=nameOfDepart).exclude(endDate__lte = current).exclude(startDate__gte=next24)
	for item in ondutyobjs:
		row = {}
		empid = item.employee_id
		emp = employee.objects.get(employeeid = empid)
		row['startdate'] = item.startDate.strftime("%m/%d %I:%M %p")
		row['enddate'] = item.endDate.strftime("%m/%d %I:%M %p")
		row['department'] = nameOfDepart
		row['employee'] =  '%s %s' %(emp.firstName, emp.lastName) 
		log.append(row)
	return log

'''check SME table view'''
def checkSMETable(request):
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/noc/login/')
	next24 = getNext24PST() # next 24 hour end time
	current = getcurrentPST()
	departlist = [item['name'] for item in department.objects.values('name')]
	print departlist
	logs = []
	for depart in departlist:
	 	temp = getOnDutyByDeparment(depart,next24,current)
	 	if temp:
			logs.extend(temp)
	print "!@#$!@#%@#&#%$"
	print logs
	return render(request,'noc/checkSMETable.html',{'logs':logs});

