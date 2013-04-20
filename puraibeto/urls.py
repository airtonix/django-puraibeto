from django.conf import settings
from django.conf.urls.defaults import patterns, include

from . import views
from surlex.dj import surl

register_macro('f', r"[^\s\/]+$")
register_macro('u', r'[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}')

urlpatterns = patterns('',
    surl(r'^download/<pk:#>/<uuid:u>/<filename:f>$',
        views.PrivateFileView.as_view(),
        name="puraibeto_download"),
)

