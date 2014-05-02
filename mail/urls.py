from django.conf.urls import patterns, url

urlpatterns = patterns('simone.mail.views',
    url(r'^$', 'index'),
    #url(r'main/$', 'main'),
    #url(r'msglist/(?P<folder_name>.*?)/$', 'msglist'),
    url(r'msglist/(?P<server>\d+)/(?P<folder>.*?)/(?P<page>.*?)/(?P<perpage>.*?)/(?P<sortc>.*?)/(?P<sortdir>.*?)/(?P<search>.*?)/$', 'msglist'),
    url(r'viewmsg/(?P<server>\d+)/(?P<folder>.*?)/(?P<uid>\d+)/$', 'viewmsg'),
    url(r'newmail/', 'newmail'),
    url(r'send/$', 'send'),
    url(r'config/(?P<action>.*?)/$', 'config'),
    url(r'json/(?P<action>.*?)/$', 'json'),
    url(r'action/(?P<action>.*?)/$', 'action'),
    url(r'prefs/$', 'prefs'),
)
