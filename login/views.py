from django.shortcuts import render,render_to_response,redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.views import logout
from .forms import LoginForm
from django.core.urlresolvers import reverse
from manager.models import department
 
def getSessionTeamInfo(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
    depart = department.objects.filter(employee__email=username)
    return depart

def isAuth(request,group):
    return request.user.groups.filter(name= group).exists();
 
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username,password = password)
        if request.POST.has_key('remember'):
            print "has key of session"
            request.session.set_expiry(1209600)
        if user is not None:
            if user.is_active:
                login(request,user)
                if request.user.groups.filter(name = 'nocops'):
                    return HttpResponseRedirect('/noc')
                elif request.user.groups.filter(name = 'managerops'):
                    # return HttpResponseRedirect('/manager')
                    team = getSessionTeamInfo(request)
                    if not team:
                        return render(request,'registration/noactive.html')
                    else:
                        return HttpResponseRedirect(reverse('managerindex', args=[team[0].name]))
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
def logout(request):
    logout(request, *args, **kwargs)
    HttpResponseRedirect("logout")
def test(request):
    return render(request,'registration/test.html')
def checkbox(request):
    return render(request,'registration/checkbox.html')
def table(request):
    return render(request,'registration/table.html')