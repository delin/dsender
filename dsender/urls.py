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

    url(r'^accounts/', include('accounts.urls', namespace='accounts', app_name='accounts')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)