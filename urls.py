from photologue.models import *
from django.conf import settings
from django.conf.urls.defaults import *
#from main.feeds import patfeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pat_prod.views.home', name='home'),
    #url(r'^pat_prod/', include('pat_prod.main.urls')),
    (r"^$", "main.views.home"),
   (r"^photo/(?P<jslug>[\-\d\w]+)/$", "main.views.view"),
   (r'^admin_tools/', include('admin_tools.urls')),
    (r"^photo/(?P<jslug>[\-\d\w]+)/details", "main.views.details"),
    (r"^photo/(?P<jslug>[\-\d\w]+)/full", "main.views.full"),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
