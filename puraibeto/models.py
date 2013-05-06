import os
from uuid import uuid4

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from guardian.shortcuts import assign_perm

from . import fields
from . import signals
from .conf import settings


class AttachedFileBase(models.Model):
    def get_uploadpath(instance, filename):
        return "private/{content_type}/{contenttype_pk}/{object_id}/{uuid}-{filename}".format(
            content_type=instance.content_type.name.lower(),
            contenttype_pk=instance.content_type_id,
            object_id=instance.object_id,
            uuid=instance.uuid,
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
            (settings.PURAIBETO_PERMISSION_CANVIEW, 'Can view'),
            (settings.PURAIBETO_PERMISSION_CANDOWNLOAD, 'Can download file'),
        )

    def __unicode__(self):
        return self.name

    def save(self):
        if not self.id:
            super(AttachedFileBase, self).save()
        signals.model_saved.send(sender=self)

    @models.permalink
    def get_download_url(self):
        return ('puraibeto_download', [
            self.content_type_id,
            self.object_id,
            self.pk,
            self.uuid,
            self.filename()])

    def filename(self):
        return str(os.path.basename(self.file.path))


class PrivateFile(AttachedFileBase):
    pass
