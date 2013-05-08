import logging

from django.contrib.auth.models import User
from django.template import RequestContext, Library, loader as template_loader, TemplateDoesNotExist, defaultfilters
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from classytags.core import Options, Tag
from classytags.arguments import Argument, MultiKeywordArgument, IntegerArgument
from classytags.helpers import AsTag, InclusionTag

from ..conf import settings
from . import models
from ..lib import sizify

logger = logging.getLogger(__name__)
register = Library()


class PrivateFileBaseTag(InclusionTag):

    def render_tag(self, context, user_obj=None, file_obj=None, yes_can=None, no_cant=None):
        request = context.get('request', None)
        content = None

        if not user_obj or not isinstance(user_obj, User):
            if not hasattr(request, 'user'):
                content = u"Missing or invalid user"

        if not file_obj or not isinstance(file_obj, models.PrivateFile):
            content = u"Missing or invalid file"

        if content is None:
            if self.permission_code and user_obj.has_perm(self.permission_code, user_obj):
                return yes_can
            return no_cant

        return content


@register.tag
class PrivateFileDownloadTag(PrivateFileBaseTag):
    name = "can_download_privatefile"
    permission_code = settings.PURAIBETO_PERMISSION_CANDOWNLOAD
    options = Options(
        Argument('user_obj', resolve=True, required=True),
        Argument('file_obj', resolve=False, required=True),
        blocks=[
            ('else',                'yes_can'),
            ('end{0}'.format(name), 'no_cant'),
        ],
    )


@register.tag
class PrivateFileViewTag(PrivateFileBaseTag):
    name = "can_view_privatefile"
    permission_code = settings.PURAIBETO_PERMISSION_CANVIEW
    options = Options(
        Argument('user_obj', resolve=True, required=True),
        Argument('file_obj', resolve=False, required=True),
        blocks=[
            ('else',                'yes_can'),
            ('end{0}'.format(name), 'no_cant'),
        ],
    )


register.filter(sizify)
