from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^theiggy_com/', include('theiggy_com.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^blog/', include('theiggy_com.blog.urls')),
    (r'^mail/', include('theiggy_com.mail.urls')),
    #(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media', 'show_indexes': True}),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media/'}),
)
