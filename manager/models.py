from django.db import models
class department(models.Model):
	name = models.CharField(max_length=50) 
	departmentid = models.IntegerField(primary_key = True)
	highRank = models.BooleanField()
	def __unicode__(self):
		return self.name
class employee(models.Model):
	firstName = models.CharField(max_length = 50) #char
	lastName = models.CharField(max_length = 50) #char
	email = models.EmailField() #email
	phone = models.EmailField(max_length=50)
	employeeid = models.IntegerField(primary_key = True)
	manager = models.BooleanField()
	department = models.ForeignKey(department)

	def __unicode__(self):
		# return self.firstName
		return "%s %s" %(self.firstName, self.lastName)

class onDuty(models.Model):
	startDate = models.DateTimeField()
	endDate = models.DateTimeField()
	employee = models.ForeignKey(employee)
	department = models.ForeignKey(department)

class log(models.Model):
	department = models.CharField(max_length = 20)
	manager = models.CharField(max_length = 20)
	startdate = models.DateTimeField()
	enddate = models.DateTimeField()
	oncallUser = models.CharField(max_length = 255)
	logtime = models.CharField(max_length = 100)
		 