from django.shortcuts import render,render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from .forms import LoginForm
from django.contrib.auth.decorators import login_required

def isAuth(request,group):
    print group
    return request.user.groups.filter(name= group).exists();

def index(request):
	 return render(request,'registration/index.html')

@login_required(redirect_field_name='homepage')
def manager(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username,password = password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/manager')
            else:
                return HttpResponseRedirect('login/loginfail.html')
        else:
            return render(request,'registration/loginfail.html')
        
    else:
        form = LoginForm()
         
    return render(request,'registration/managerlogin.html',{'form':form})

@login_required(redirect_field_name='homepage')
def noc(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username,password = password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/noc')
            else:
                return HttpResponseRedirect('login/loginfail.html')
        else:
            return render(request,'registration/loginfail.html')
        
    else:
        form = LoginForm()
         
    return render(request,'registration/noclogin.html',{'form':form})