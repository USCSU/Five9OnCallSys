from django.db import models
class department(models.Model):
	name = models.CharField(max_length=50) 
	departmentid = models.IntegerField(primary_key = True)
	def __unicode__(self):
		return self.name
class employee(models.Model):
	firstName = models.CharField(max_length = 50) #char
	lastName = models.CharField(max_length = 50) #char
	number = models.IntegerField(blank = True,null = True)
	address =  models.CharField(max_length = 100) #text
	city = models.CharField(max_length=20, blank = True, null = True)
	state = models.CharField(max_length = 10, blank = True,null = True)
	zipcode = models.IntegerField(blank = True, null = True)
	email = models.EmailField() #email
	mobile = models.CharField(max_length=20) #char
	employeeid = models.IntegerField(primary_key = True)
	manager = models.BooleanField()
	department = models.ForeignKey(department)
	def __unicode__(self):
		# return self.firstName
		return "%s %s" %(self.firstName, self.lastName)

class onDuty(models.Model):
	startDate = models.DateField()
	endDate = models.DateField()
	employee = models.ForeignKey(employee)
	department = models.ForeignKey(department)

class log(models.Model):
	department = models.CharField(max_length = 20)
	manager = models.CharField(max_length = 20)
	startdate = models.DateField()
	enddate = models.DateField()
	oncallUser = models.CharField(max_length = 255)
	logtime = models.CharField(max_length = 100)
		 