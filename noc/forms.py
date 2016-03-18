from django import forms
from manager.models import department
from manager.models import employee
class NocOpsForm(forms.Form):
	Ticket = forms.CharField()
