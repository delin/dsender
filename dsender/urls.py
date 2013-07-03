from django.conf.urls import patterns, include, url
from django.contrib import admin
from main.views import Home, StartMailing

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^mailing/', StartMailing.as_view(), name='start_mailing'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
