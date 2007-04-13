from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^blog/', include('blog.urls')),
    (r'^mail/', include('mail.urls')),
    #(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media', 'show_indexes': True}),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media/'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
)
