__author__ = 'delin'

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login/$', 'accounts.views.page_login', name='login'),
    url(r'^logout/$', 'accounts.views.page_logout', name='logout'),
)