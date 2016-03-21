from django.shortcuts import render,render_to_response,redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from .forms import LoginForm

def isAuth(request,group):
    return request.user.groups.filter(name= group).exists();
 
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username,password = password)
        if user is not None:
            if user.is_active:
                login(request,user)
                if request.user.groups.filter(name = 'nocops'):
                    return HttpResponseRedirect('/noc')
                elif request.user.groups.filter(name = 'managerops'):
                    return HttpResponseRedirect('/manager')
                else:
                    return render(request,'registration/nogroup.html')
            else:
                print "not is_active"
                return render(request,'registration/noactive.html')
        else:
            print "user none"
            return render(request,'registration/loginfail.html')
        
    else:
        form = LoginForm()
         
    return render(request,'registration/login.html',{'form':form})

def test(request):
    return render(request,'registration/test.html')