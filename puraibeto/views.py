import os
import mimetypes

from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.static import was_modified_since
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotModified
from django.utils.http import http_date, parse_http_date
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied, ImproperlyConfigured

from . import signals
from . import models
from .conf import settings


class PrivateFileMixin(object):
    check_modified = True
    parentpk_kwarg = 'attachedto_pk'
    model = models.PrivateFile

    def get_queryset(self):
        return models.PrivateFile.objects.filter(object_id=self.kwargs.get(self.parentpk_kwarg))


class BasePrivateFileView(PrivateFileMixin, SingleObjectMixin, View):

    def get_object(self, queryset=None):
        obj = super(BasePrivateFileView, self).get_object(queryset)

        field_file = getattr(obj, 'file', None)

        if not field_file:
            raise Http404("File not available yet.")

        mimetype, encoding = mimetypes.guess_type(field_file.path)
        self.mimetype = mimetype or 'application/octet-stream'
        self.encoding = encoding or 'utf-8'
        self.statobj = os.stat(field_file.path)
        self.basename = os.path.basename(field_file.path)


    def set_headers(self):
        field_file = self.object.file
        self.response["Last-Modified"] = http_date(self.statobj.st_mtime)
        self.response["Content-Length"] = self.statobj.st_size

        attachment = getattr(field_file, 'attachment', False)

        if attachment:
            response['Content-Disposition'] = 'attachment; filename={}'.format(self.basename)

        if self.encoding:
            response["Content-Encoding"] = self.encoding

    def get_response(self):
        field_file.open()
        self.response = HttpResponse(field_file.file.read(), mimetype=self.mimetype)
        field_file.close()

        return self.response

    def render_to_response(self, *args, **kwargs):
        field_file = self.object.file

        condition = getattr(field_file, condition, None)

        if condition != None and not condition(self.request, self.object):
            raise PermissionDenied()

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

        return response


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
