from django import forms
from manager.models import department
from manager.models import employee
class managerOpsForm(forms.Form):
	startDate = forms.DateField()
	endDate = forms.DateField()
	 