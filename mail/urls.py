from django.conf.urls.defaults import *

urlpatterns = patterns('theiggy_com.mail.views',
    (r'^$', 'index'),
    (r'msglist/(?P<folder_name>.*?)/$', 'msglist'),
    (r'viewmsg/(?P<folder>.*?)/(?P<uid>.*?)/$', 'viewmsg'),
)