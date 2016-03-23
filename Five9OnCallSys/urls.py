from django.conf.urls import include, url
from django.contrib import admin
from manager import views as manager
from login import views as login
from noc import views as noc

urlpatterns = [
	url(r'^$', login.index,name ='homepage'),

	# url(r'^manager/$', manager.home,name ='managerhome'),
	url(r'^team/(?P<team>\w+)/add_schdule$', manager.addSchedule,name ='managerschdule'),
	
	url(r'^team/(?P<name>\w+)/$', manager.index,name ='managerindex'),
	
	url(r'^noc/$', noc.index,name ='nocindex'),

	url(r'^noc/Add_Ticket$', noc.addTicket,name ='nocaddticket'),

    url(r'^logout/$','django.contrib.auth.views.logout',{'next_page': '/'}),
    
    url(r'test/$',login.test,name='test'),
    
    url(r'^admin/', include(admin.site.urls)), #defual one: means any admin/ will be redirected into admin url rule.
]
