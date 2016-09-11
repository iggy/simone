# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'simone'

urlpatterns = [
    url(r'^$', views.index),
    #url(r'main/$', 'main'),
    #url(r'msglist/(?P<folder_name>.*?)/$', 'msglist'),
    url(r'msglist/(?P<server>\d+)/(?P<folder>.*?)/(?P<page>.*?)/(?P<perpage>.*?)/(?P<sortc>.*?)/(?P<sortdir>.*?)/(?P<search>.*?)/$', views.msglist),
    url(r'viewmsg/(?P<server>\d+)/(?P<folder>.*?)/(?P<uid>\d+)/$', views.viewmsg),
    url(r'newmail/', views.newmail),
    url(r'send/$', views.send),
    url(r'config/(?P<action>.*?)/$', views.config, name='config'),
    url(r'json/(?P<action>.*?)/$', views.jsonview),
    url(r'action/(?P<action>.*?)/$', views.action),
    url(r'prefs/$', views.prefs),
]

urlpatterns += [
    url(
        regex="^ImapServer/~create/$",
        view=views.ImapServerCreateView.as_view(),
        name='ImapServer_create',
    ),
    url(
        regex="^ImapServer/(?P<pk>\d+)/~delete/$",
        view=views.ImapServerDeleteView.as_view(),
        name='ImapServer_delete',
    ),
    url(
        regex="^ImapServer/(?P<pk>\d+)/$",
        view=views.ImapServerDetailView.as_view(),
        name='ImapServer_detail',
    ),
    url(
        regex="^ImapServer/(?P<pk>\d+)/~update/$",
        view=views.ImapServerUpdateView.as_view(),
        name='ImapServer_update',
    ),
    url(
        regex="^ImapServer/$",
        view=views.ImapServerListView.as_view(),
        name='ImapServer_list',
    ),
	url(
        regex="^SmtpServer/~create/$",
        view=views.SmtpServerCreateView.as_view(),
        name='SmtpServer_create',
    ),
    url(
        regex="^SmtpServer/(?P<pk>\d+)/~delete/$",
        view=views.SmtpServerDeleteView.as_view(),
        name='SmtpServer_delete',
    ),
    url(
        regex="^SmtpServer/(?P<pk>\d+)/$",
        view=views.SmtpServerDetailView.as_view(),
        name='SmtpServer_detail',
    ),
    url(
        regex="^SmtpServer/(?P<pk>\d+)/~update/$",
        view=views.SmtpServerUpdateView.as_view(),
        name='SmtpServer_update',
    ),
    url(
        regex="^SmtpServer/$",
        view=views.SmtpServerListView.as_view(),
        name='SmtpServer_list',
    ),
	]
