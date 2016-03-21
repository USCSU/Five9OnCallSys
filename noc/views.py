from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from manager.models import department,employee,onDuty
from noc.forms import NocOpsForm
from noc.models import log
from datetime import datetime
from sets import Set
import smtplib
from django.contrib.auth.decorators import login_required
from login.views import isAuth
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def logFormat():
	logs = []
	#take top 40 records in revser order 
	Oplogs = log.objects.all().order_by('-datetime')[:40]
	#title
	logs.append('{:>15}  {:>20} {:>20} {:>20}'.format('Time:','Ticket:','Actions:','Departments:'))
	listOfDepartments = department.objects.all()
	#take each log and update
	for singlelog in Oplogs:
		logtime = singlelog.datetime
		ticketnumber = singlelog.ticketnumber
		departlist = ""
		for item in singlelog.departments:
			departlist+=item
		if not singlelog.escalate:
			content = u"\u2022     "+ '{:<20}  {:<20} {:<20} {:>10}'.format(logtime,'ticket#'+ticketnumber,' sent to ',departlist)
		else:
			escalateList=singlelog.oncallUser
			content = u"\u2022     "+ '{:<20}  {:<20} {:<20} {:>10} '.format(logtime,'ticket#'+ticketnumber,' escalated to ',departlist)
		logs.append(content)
	#not log found
	if not logs:
		logs.append("No schedule for your team yet")
	return logs,listOfDepartments

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
		managerList.append(getManager(item).email)
	return managerList
'''
This funciton is mainly to retrieve employees who will take the duty for one department
'''
def getOnCallEmployee(depart_name):
	emaillist = []
	ondutylist = onDuty.objects.filter(department__name =depart_name) & onDuty.objects.filter(startDate__lte=datetime.now) &onDuty.objects.filter(endDate__gte=datetime.now)

	if not ondutylist: # if no employee is on duty, the ticket will be sent to corresponding manager
		manager = employee.objects.filter(department__name=depart_name) & employee.objects.filter(manager = True)
		emaillist.append(manager[0].email)
	else:
		for item in ondutylist:
			emaillist.append(item.employee.email)

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

def index(request):
	if not isAuth(request,'nocops'):
		return HttpResponseRedirect('/noc/login/')
	
	if request.method == 'POST':	 
		form = NocOpsForm(request.POST)
		escalate = [str(x) for x in request.POST.getlist('escalate')]
		departlist = [str(x) for x in request.POST.getlist('depart')]
		if form.is_valid() or not escalate and not departlist:
			#receive request's paramter from html
			escalateList =  Set(getManagers(escalate))
			oncallList = Set(getOnCallEmployees(departlist))
			ticket = form.cleaned_data['Ticket']
			#email sent
			#send_email("chris.sufive9@gmail.com", "Five9ossqa",list(oncallList), "Status : [Logged] This is a five9 local test: You've received a ticket from noc", "please reply to take request: ticket number"+ticket)
			#send_email("chris.sufive9@gmail.com", "Five9ossqa",list(escalateList), "Status : [Escalated] This is a five9 local test: You've received a ticket from noc", "please reply to take request: ticket number"+ticket)
			
			#update log of Noc operation
			record = log(datetime = datetime.now().strftime("%Y-%m-%d  %H:%M:%S"), ticketnumber = ticket, oncallUser = list(oncallList) , departments = list(departlist),escalate = False)
			record.save()
			record = log(datetime = datetime.now().strftime("%Y-%m-%d  %H:%M:%S"), ticketnumber = ticket, oncallUser = list(escalateList) , departments = list(escalate),escalate = True)
			record.save()
			return render(request,'noc/formsuccess.html');
		else:
			return render(request,'noc/no_data.html');
	else:
		form = NocOpsForm()
		logs,listOfDepartments = logFormat()
	 
	return render(request,'noc/index.html',{'form':form, 'log':logs, 'listOfDepartments':listOfDepartments})

