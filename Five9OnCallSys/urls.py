from django.conf.urls import include, url
from django.contrib import admin
from manager import views as manager
from login import views as login
from noc import views as noc

urlpatterns = [
	# url(r'^login/', login.index,name ='loginindex'),
	url(r'^$', login.index,name ='homepage'),

	url(r'^noc/login/$', login.noc, name = 'noclogin'),
    url(r'^manager/login/$', login.manager,name ='managerlogin'),
	 
	url(r'^manager/$', manager.home,name ='managerhome'),
	
	url(r'^team/(?P<name>\w+)/', manager.index,name ='managerindex'),
	
	url(r'^noc/$', noc.index,name ='nocindex'),
    
    
    url(r'^admin/', include(admin.site.urls)), #defual one: means any admin/ will be redirected into admin url rule.
]
