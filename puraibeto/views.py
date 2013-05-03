import os
import mimetypes

from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.static import was_modified_since
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotModified
from django.utils.http import http_date, parse_http_date
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType

from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm, get_perms

from . import signals
from . import models
from .conf import settings



class PrivateFileMixin(object):
    check_modified = True
    model = models.PrivateFile
    pk_kwarg = "pk"
    contenttype_kwarg = 'contenttype'
    contenttypepk_kwarg = "contenttype_pk"
    objectpk_kwarg = "object_pk"

    def get_queryset(self):
        contenttype = self.kwargs.get(self.contenttype_kwarg)
        contenttype_pk = self.kwargs.get(self.contenttypepk_kwarg)
        object_pk = self.kwargs.get(self.objectpk_kwarg)

        queryset = models.PrivateFile.objects.filter(
            content_type_id=contenttype_pk,
            object_id=object_pk,
        )
        return queryset

    def get_object(self, queryset):
        self.object = queryset.get(**{self.pk_kwarg: self.kwargs.get(self.pk_kwarg)})



class BasePrivateFileView(PrivateFileMixin, SingleObjectMixin, View):

    def dispatch(self, request, *args, **kwargs):
        return super(PrivateFileMixin, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.object = self.get_object(self.get_queryset())
        return self.render_to_response()

    def get_object(self, queryset):
        super(BasePrivateFileView, self).get_object(queryset)

        field_file = getattr(self.object, 'file', None)
        if not settings.PURAIBETO_PERMISSION_CANDOWNLOAD in get_perms(self.request.user, self.object):
            raise PermissionDenied

        if not field_file:
            raise Http404("File not available yet.")

        mimetype, encoding = mimetypes.guess_type(field_file.path)
        self.mimetype = mimetype or 'application/octet-stream'
        self.encoding = encoding or 'utf-8'
        self.statobj = os.stat(field_file.path)
        self.basename = os.path.basename(field_file.path)
        return self.object


    def set_headers(self):
        field_file = self.object.file
        self.response["Last-Modified"] = http_date(self.statobj.st_mtime)
        self.response["Content-Length"] = self.statobj.st_size

        attachment = getattr(field_file, 'attachment', False)
        if attachment:
            self.response['Content-Disposition'] = 'attachment; filename={}'.format(self.basename)
        if self.encoding:
            self.response["Content-Encoding"] = self.encoding

    def get_response(self):
        file_obj = self.object.file
        file_obj.open()
        self.response = HttpResponse(file_obj.file.read(), mimetype=self.mimetype)
        file_obj.close()
        return self.response

    def render_to_response(self, *args, **kwargs):
        condition = getattr(self.object.file, 'condition', None)

        if self.check_modified and not was_modified_since(
                self.request.META.get('HTTP_IF_MODIFIED_SINCE'),
                self.statobj.st_mtime,
                self.statobj.st_size):
            return HttpResponseNotModified(mimetype=self.mimetype)

        self.get_response()
        self.set_headers()

        signals.pre_download.send(
            sender = self.model,
            instance = self.object,
            request = self.request)

        return self.response


class NginxPrivateFileView(BasePrivateFileView):

    def set_headers(self, *args, **kwargs):
        super(NginxPrivateFileView, self).set_headers(*args, **kwargs)
        self.response['Content-Type'] = self.mimetype
        # This is the Nginx Specific header that performs the magic.
        self.response["X-Accel-Redirect"] = "/{}".format(unicode(self.object.file))

    def get_response(self, *args, **kwargs):
        self.response = HttpResponse()
        return self.response


class XSendPrivateFileView(BasePrivateFileView):

    def set_headers(self, *args, **kwargs):
        super(NginxPrivateFileView, self).set_headers(*args, **kwargs)
        self.response['Content-Type'] = self.mimetype
        # This is the X-Send Specific header that performs the magic.
        self.response["X-Sendfile"] = self.object.file.path

    def get_response(self, *args, **kwargs):
        self.response = HttpResponse()
        return self.response


Backends = {
    'nginx' : NginxPrivateFileView,
    'xsend' : XSendPrivateFileView,
    'basic' : BasePrivateFileView,
}

PrivateFileDownloadView = Backends.get(settings.PURAIBETO_BACKEND)

class PrivateFileListView(PrivateFileMixin, ListView): pass
class PrivateFileCreateView(PrivateFileMixin, CreateView): pass
class PrivateFileDetailView(PrivateFileMixin, DetailView): pass
class PrivateFileUpdateView(PrivateFileMixin, UpdateView): pass
