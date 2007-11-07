from django.conf.urls.defaults import *

urlpatterns = patterns('mail.views',
    (r'^$', 'index'),
    (r'main/$', 'main'),
    (r'msglist/(?P<folder_name>.*?)/$', 'msglist'),
    (r'viewmsg/(?P<server>\d+)/(?P<folder>.*?)/(?P<uid>.*?)/$', 'viewmsg'),
    (r'newmail/', 'newmail'),
    (r'send/$', 'send'),
    (r'config/(?P<action>.*?)/$', 'config'),
    (r'json/(?P<action>.*?)/$', 'json'),
    (r'action/(?P<action>.*?)/$', 'action'),

)
