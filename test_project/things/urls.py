from django.conf.urls import patterns, include, url
from django.contrib import admin

from surlex.dj import surl

from . import views

admin.autodiscover()
urlpatterns = patterns('',
	surl(r'^/$', views.ThingListView.as_view(), name="thing-list")
	surl(r'^<pk:#>/$', views.ThingDetailView.as_view(), name="thing-detail")
	surl(r'^<pk:#>/files/$', include('puraibeto.urls'))
)
