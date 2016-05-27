import smtplib
import json
import pytz
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from manager.models import department,employee,onDuty
from noc.forms import NocOpsForm
from noc.models import log,bridge
from datetime import datetime
from sets import Set
from django.contrib.auth.decorators import login_required
from login.views import isAuth
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from pytz import timezone
from dateutil import parser
from django.core.urlresolvers import reverse
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
		temp.append(singlelog.bridge)
		lists=json.decoder.JSONDecoder().decode(singlelog.departments)
		departlist =[]
		for item in lists:
			departlist.append(filterDepartmentName(item)) #need to improve
		temp.append("Logged") if not singlelog.escalate else temp.append("Escalated");
		temp.append(departlist)
		temp.append(singlelog.nocEmp)
		logs.append(temp)
	return logs#,listOfDepartments

def send_email(user, pwd, sender,recipient, subject, body):
    gmail_user = user
    gmail_pwd = pwd
    FROM = sender
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        server = smtplib.SMTP("webmail.five9.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    # except:
    #     print "failed to send mail"
    except BaseException as e:
	    print 'Failed to send email: ' + str(e)

'''
this function is mainly to retrieve manager's name  with input from form submission
'''
def getManager(depart_name): 
	managerItem = (employee.objects.filter(department__name = depart_name).filter(manager='true'))
	return managerItem

def getManagers(listOfDepartments):
	managerList = []
	for item in listOfDepartments:
		manager = getManager(item)
		for item in manager:
			managerList.append(item.phone)
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
		for item in manager:
			emaillist.append(item.phone)
	else:
		for item in ondutylist:
			if item:
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
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/')
	if request.method == 'POST':	 
		form = NocOpsForm(request.POST)
		escalate = [str(x) for x in request.POST.getlist('escalate')]
		departlist = [str(x) for x in request.POST.getlist('depart')]
		superescalate = [str(x) for x in request.POST.getlist('superescalate')]
 		 
		if form.is_valid() or not escalate and not departlist and not superescalate:
			#receive request's paramter from html
			escalateList =  Set(getManagers(escalate))
			superescalateList =  Set(getManagers(superescalate))
			oncallList = Set(getOnCallEmployees(departlist))

			bridgeNumber = request.POST.get('bridge')
			 
			print escalateList
			print superescalateList
			print oncallList

			# receiverList = []
			# receiverList.extend(escalateList)
			# receiverList.extend(oncallList)
			# receiverList.extend(superescalateList)

			ticket = form.cleaned_data['Ticket']#list(oncallList)
			subject = request.POST.get('subject')
			# data base flag to save on the log
			# dbFlag = False
			# extraList = 
			# if bool(escalateList) or bool(superescalateList) or bool(oncallList):
			# 	extraList = ['chris.su@five9.com','Dhaval.vora@five9.com']
			# 	# ,'Dhaval.Vora@five9.com','Katherine.McCall@five9.com']
			# 	receiverList.extend(extraList)
			# 	dbFlag = True
			# 	send_email("NocTextAlert@five9.com", "Five9321!",'NocTextAlert@five9.com',receiverList, subject," Outrage bridge#:"+ bridgeNumber+"\nOutage/Service Alert #: "+ticket+" \n-Alert sent by "+request.user.username) 	

			oncallFlag = False
			escalateFlag= False
			extraList = ['chris.su@five9.com','Dhaval.vora@five9.com','Katherine.McCall@five9.com']
			#email sent
			if bool(oncallList):
				oncallExtraList=list(oncallList)
				oncallExtraList.extend(extraList)
				# send_email("chris.sufive9@gmail.com", "Five9ossqa",list(oncallList), subject," Outrage bridge#:"+ bridgeNumber+"\nOutage/Service Alert #: "+ticket) 
				send_email("NocTextAlert@five9.com", "Five9321!",'NocTextAlert@five9.com',oncallExtraList, subject," Outrage bridge#:"+ bridgeNumber+"\nOutage/Service Alert #: "+ticket+" \n-Alert sent by "+request.user.username) 
				oncallFlag = True
			if bool(escalateList):	
				escalateExtraList = list(escalateList)
				escalateExtraList.extend(extraList)
				send_email("NocTextAlert@five9.com", "Five9321!",'NocTextAlert@five9.com',escalateExtraList, subject," Outrage bridge#:"+ bridgeNumber+"\nOutage/Service Alert #: "+ticket+" \n-Alert sent by "+request.user.username)
				escalateFlag = True
			
			if bool(superescalateList):
				superExtraList = list(superescalateList)
				superExtraList.extend(extraList)
				send_email("NocTextAlert@five9.com", "Five9321!",'NocTextAlert@five9.com',superExtraList, subject," Outrage bridge#:"+ bridgeNumber+"\nOutage/Service Alert #: "+ticket+" \n-Alert sent by "+request.user.username)
			#update log of Noc operation
			 
			if bool(oncallList) and oncallFlag:
				record = log(datetime = getcurrentPST(), ticketnumber = ticket, oncallUser = list(oncallList) , departments = json.dumps(departlist),escalate = False, bridge = bridgeNumber, management = json.dumps(superescalate), nocEmp = request.user)
				record.save()
			if bool(escalateList) and escalateFlag:	
				record = log(datetime = getcurrentPST(), ticketnumber = ticket, oncallUser = list(escalateList) , departments = json.dumps(escalate),escalate = True, bridge = bridgeNumber, management = json.dumps(superescalate),nocEmp = request.user)
				record.save()
			return HttpResponseRedirect('/noc');
		else:
			return render(request,'noc/no_data.html');
	else:
		form = NocOpsForm()
		alldepartment = department.objects.filter(highRank =0)
		allsuperdepartment = department.objects.filter(highRank = 1)
		listOfDepartments,departNoExist = getNoEmpList(alldepartment)
		listOfSuperDepartments,superdepartNoExist=getNoEmpList(allsuperdepartment)

		bridgeSet = bridge.objects.all()
		if bridgeSet:
			oldNumber = bridge.objects.all()[:1][0].number	
		else:
			oldNumber =''
		print listOfDepartments
		print departNoExist
		print listOfSuperDepartments
		print superdepartNoExist
	return render(request,'noc/addTicket.html',{'form':form,  'listOfDepartments':listOfDepartments,'departNoExist':departNoExist,'superdepartNoExist':superdepartNoExist,'listOfSuperDepartments':listOfSuperDepartments,'number':oldNumber})
def getNoEmpList(listOfDepartment):
	exist = []
	noexist =[]
	for item in listOfDepartment:
		temp = employee.objects.filter(department__name = item)
		if temp:
			exist.append(item)
		else:
			noexist.append(item)
	return exist,noexist
def index(request):
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/')
	bridgeSet = bridge.objects.all()
	if bridgeSet:
		oldNumber = bridgeSet[:1][0].number	
	else:
		oldNumber =''

	logs = logFormat()
	return render(request,'noc/index.html',{ 'log':logs,'number':oldNumber})

def filterDepartmentName(team):
	result = team
	if 'IT' in team:
		result = 'IT' 
	if 'Security' in team:
		result = 'Security' 
	if 'Center' in team:
		result = 'DCNTER' 
	if 'Sys'  in team:
		result = 'SYS' 
	if 'Network' in team:
		result = 'Network' 
	if 'NOC' in team:
		result = 'NOC' 
	if 'Data' in team:
		result = 'DB' 
	if 'PSTN' in team:
		result = 'PSTN'
	if 'Sustain' in team:
		result = 'Sustain'
	if 'Infrastructure_team' in team:
		result = 'Infra'
	if 'NICE' in team:
		result = 'NICE'
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
		return HttpResponseRedirect('/')
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
		return HttpResponseRedirect('/')
	next24 = getNext24PST() # next 24 hour end time
	current = getcurrentPST()
	departlist = [item['name'] for item in department.objects.values('name')]
	logs = []
	for depart in departlist:
	 	temp = getOnDutyByDeparment(depart,next24,current)
	 	if temp:
			logs.extend(temp)
	return render(request,'noc/checkSMETable.html',{'logs':logs});
def setBridge(request):
	#avoid cross visit
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/')
	if request.method == 'POST':
		#take request from html page
		bridgeNum= request.POST.get('bridge')
		bridgeSet = bridge.objects.all()
		# //if no data in db ,insert
		if not bridgeSet:
			item = bridge(number = bridgeNum)
			item.save()
		# orelse, update 
		else:
			oldNumber = bridgeSet[:1][0].number
			bridge.objects.filter(number=oldNumber).update(number = bridgeNum)
		return HttpResponseRedirect(reverse('nocindex'))
	else:#get method
		 return HttpResponse("Wrong way,Turn back")
def setBridgeTicket(request):
	#avoid cross visit
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/')
	if request.method == 'POST':
		#take request from html page
		bridgeNum= request.POST.get('bridge')
		bridgeSet = bridge.objects.all()
		# //if no data in db ,insert
		if not bridgeSet:
			item = bridge(number = bridgeNum)
			item.save()
		# orelse, update 
		else:
			oldNumber = bridge.objects.all()[:1][0].number
			bridge.objects.filter(number=oldNumber).update(number = bridgeNum)
		return HttpResponseRedirect(reverse('nocaddticket'))
	else:#get method
		 return HttpResponse("Wrong way,Turn back")