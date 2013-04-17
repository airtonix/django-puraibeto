import os
import mimetypes

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotModified
from django.views.static import was_modified_since
from django.utils.http import http_date, parse_http_date
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied, ImproperlyConfigured

from . import signals



class PrivateFileResponseBase(HttpResponse): pass

	def __init__(self, *args, **kwargs):
		field_file  = kwargs.pop('file')

		mimetype, encoding = mimetypes.guess_type(field_file.path)
		mimetype = mimetype or 'application/octet-stream'
		statobj = os.stat(field_file.path)

		if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
		                          statobj.st_mtime, statobj.st_size):
		    return HttpResponseNotModified(mimetype=mimetype)

		basename = os.path.basename(field_file.path)
		field_file.open()
		response = HttpResponse(field_file.file.read(), mimetype=mimetype)
		response["Last-Modified"] = http_date(statobj.st_mtime)
		response["Content-Length"] = statobj.st_size
		if field_file.attachment:
		    response['Content-Disposition'] = 'attachment; filename=%s'%basename
		if encoding:
		    response["Content-Encoding"] = encoding
		field_file.close()
		return response


class NginxResponse(PrivateFileResponseBase): pass
class ApacheResponse(PrivateFileResponseBase): pass
class LightHttpResponse(PrivateFileResponseBase): pass
