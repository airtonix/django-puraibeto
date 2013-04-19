from django.conf import settings
from django.conf.urls.defaults import patterns, include

from surlex import register_macro
from surlex.dj import surl

from . import views

register_macro('f',r"[^\s\/]+$")

urlpatterns = patterns('',
    surl(r'^/$', views.PrivateFileListView.as_view(), name="puraibeto_files"),
    surl(r'^download/<pk:#>/<filename:f>$', views.PrivateFileView.as_view(), name="puraibeto_download"),
)

