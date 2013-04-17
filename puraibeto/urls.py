from django.conf import settings
from django.conf.urls.defaults import patterns, include

from . import views
from surlex.dj import url

register_macro('f',r"[^\s\/]+$")

urlpatterns = patterns('',
    url('^download/<pk:#>/<filename:f>$',
        views.PrivateFileView.as_view(),
        name = "puraibeto_download"),
)

