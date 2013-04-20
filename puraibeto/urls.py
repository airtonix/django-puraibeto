from django.conf.urls.defaults import patterns, include

from surlex import register_macro
from surlex.dj import surl

from . import views
from .conf import settings

register_macro('f', r"[^\s\/]+$")
register_macro('u', r'[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}')

urlpatterns = patterns('',

    surl(r'^$',
        views.PrivateFileListView.as_view(),
        name="puraibeto_files"),

    surl(r'^upload/$',
        views.PrivateFileCreateView.as_view(),
        name="puraibeto_upload"),

    surl(r'^<pk:#>/<uuid:u>/$',
        views.PrivateFileDetailView.as_view(),
        name="puraibeto_detail"),

    surl(r'^<pk:#>/<uuid:u>/edit/$',
        views.PrivateFileUpdateView.as_view(),
        name="puraibeto_update"),


    surl(r'^<pk:#>/download/<uuid:u>-<filename:f>$',
        views.PrivateFileDownloadView.as_view(),
        name="puraibeto_download"),
)

