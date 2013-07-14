from django.conf import settings
from django.conf.urls.defaults import *
from main.feeds import pat_feed
from settings import MEDIA_ROOT, STATIC_ROOT

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r"^$", "main.views.home"),
    (r"^photo/(?P<jslug>[\-\d\w]+)/$", "main.views.view"),
    (r"^category/(?P<jcat>[\-\d\w]+)/$", "main.views.category"),
    (r"^about", "main.views.about"),
    (r"^feed", pat_feed()),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += patterns('',
url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    'document_root': MEDIA_ROOT,
    }),
url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT, 'show_indexes':True}),
)
