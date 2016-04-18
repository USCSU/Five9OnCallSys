from django.db import models


class log(models.Model):
	datetime = models.CharField(max_length = 100)
	ticketnumber = models.CharField(max_length=50)
	oncallUser = models.TextField(max_length = 255)
	departments = models.TextField(max_length=255)
	escalate = models.BooleanField()
	management = models.TextField(max_length = 255)
	bridge = models.CharField(max_length=20)
	nocEmp = models.CharField(max_length = 30)
class bridge(models.Model):
	number = models.CharField(max_length=25)