from uuid import uuid4

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from . import fields
from .conf import settings


class AttachedFileBase(models.Model):
    def get_uploadpath(instance, filename):
        klassname = instance.attached_to.__class__.__name__.lower()
        filename = "private/{file_uuid}/{filename}".format(
            file_uuid=instance.uuid,
            filename=filename)

        if hasattr(instance.attached_to, 'get_uploadpath'):
            return instance.attached_to.get_uploadpath(instance, filename)

        return "{klass}/{klass_id}/".format(
            klass=klassname,
            klass_id=instance.object_id,
            filename=filename)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    attached_to = generic.GenericForeignKey('content_type', 'object_id')

    file = fields.PrivateFileField(verbose_name=_('File'), upload_to=get_uploadpath)
    uuid = models.CharField(verbose_name=_('UUID'),
                            blank=True, null=True,
                            max_length=256, unique=True,
                            default=lambda: str(uuid4()))

    name = models.CharField(verbose_name=_('Name'),
        blank=True, null=True, max_length=255)
    description = models.TextField(verbose_name=("Description"),
        blank=True, null=True, max_length=255)

    class Meta:
        abstract = True
        permissions = (
            ('can_view', 'Can see file in lists'),
            ('can_download', 'Can download file'),
            ('can_remove', 'Can remove file'),
        )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        # for now we'll assume you're attaching your urlpatterns under a
        # route that uses 'attached_pk' as a url argument
        return ('puraibeto_download', (), {
            'attached_pk': self.object_id,
            'pk': self.pk,
        })


class PrivateFile(AttachedFileBase): pass