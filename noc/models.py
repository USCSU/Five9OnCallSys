from django.db import models


class log(models.Model):
	datetime = models.CharField(max_length = 100)
	ticketnumber = models.CharField(max_length=50)
	oncallUser = models.CharField(max_length = 255)
	departments = models.CharField(max_length=100)
	escalate = models.BooleanField()