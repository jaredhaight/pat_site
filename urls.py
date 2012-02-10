from django.conf import settings
from django.conf.urls.defaults import *
#from main.feeds import patfeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r"^$", "main.views.home"),
    (r"^photo/(?P<jslug>[\-\d\w]+)/$", "main.views.view"),
    (r'^admin_tools/', include('admin_tools.urls')),
    (r"^photo/(?P<jslug>[\-\d\w]+)/details", "main.views.details"),
    (r"^photo/(?P<jslug>[\-\d\w]+)/full", "main.views.full"),
    (r"^photo/(?P<jslug>[\-\d\w]+)/download", "main.views.download"),    
    (r"^category/(?P<jcat>[\-\d\w]+)/$", "main.views.category"),
    (r"^about", "main.views.about"),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
    
