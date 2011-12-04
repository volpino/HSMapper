from django.conf.urls.defaults import patterns, include, url
from core.views.views import *
from core.views import api

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home),
    # url(r'^findmyspot/', include('findmyspot.foo.urls')),
    url(r'^api/get_hospitals', api.get_hospitals),
    url(r'^api/add_hospital', api.add_hospital),
    url(r'^api/delete_hospital', api.edit_hospital),
    url(r'^api/edit_hospital', api.edit_hospital),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
