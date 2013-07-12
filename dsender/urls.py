from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dsender.settings import MEDIA_ROOT, DEBUG

admin.autodiscover()

if DEBUG:
    urlpatterns = patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': MEDIA_ROOT,
            'show_indexes': True
        }),
    )
    urlpatterns += staticfiles_urlpatterns()
else:
    urlpatterns = patterns('', )

urlpatterns += patterns('',
    url(r'^$', 'main.views.page_home', name='home'),
    url(r'^select_project/', 'main.views.page_select_project', name='select_project'),
    url(r'^select_group/', 'main.views.page_select_group', name='select_group'),
    url(r'^select_message/', 'main.views.page_select_message', name='select_message'),
    url(r'^confirm/', 'main.views.page_confirm', name='confirm'),
    url(r'^send/', 'main.views.page_send', name='send'),

    url(r'^logs/all/', 'main.views.page_logs', name='logs_view'),

    url(r'^project/list/', 'main.views.page_project_list', name='project_list'),
    url(r'^project/add/', 'main.views.page_project_add', name='project_add'),

    url(r'^group/list/', 'main.views.page_group_list', name='group_list'),
    url(r'^group/add/', 'main.views.page_group_add', name='group_add'),

    url(r'^message/list/', 'main.views.page_message_list', name='message_list'),
    url(r'^message/add/', 'main.views.page_message_add', name='message_add'),

    url(r'^client/list/', 'main.views.page_client_list', name='client_list'),
    url(r'^client/add/', 'main.views.page_client_add', name='client_add'),
    url(r'^client/(?P<client_id>\d+)/edit/$', 'main.views.page_client_edit', name='client_edit'),
    url(r'^client/(?P<client_id>\d+)/$', 'main.views.page_client_view', name='client_view'),

    url(r'^client/(?P<client_id>\d+)/unsubscribe/(?P<code>[a-f0-9]{32})/$', 'main.views.page_client_unsubscribe',
        name='client_unsubscribe'),
    url(r'^client/(?P<client_id>\d+)/unsubscribe/(?P<code>[a-f0-9]{32})/ok/$', 'main.views.page_client_unsubscribe_ok',
        name='client_unsubscribe_ok'),

    url(r'^accounts/', include('accounts.urls', namespace='accounts', app_name='accounts')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)