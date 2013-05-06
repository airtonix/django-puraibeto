import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _


from . import fields
from . import signals
from .conf import settings


if settings.PURAIBETO_CHECK_PERMISSIONS:
    if not "guardian" in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("PURAIBETO_CHECK_PERMISSIONS = True requires that you have django-guardian installed. ")
    if not "guardian.backends.ObjectPermissionBackend" in settings.AUTHENTICATION_BACKENDS:
        raise ImproperlyConfigured("PURAIBETO_CHECK_PERMISSIONS = True requires that you have 'guardian.backends.ObjectPermissionBackend' listed in settings.AUTHENTICATION_BACKENDS.")


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

    def can_user_view(self, user=None):
        if settings.PURAIBETO_CHECK_PERMISSIONS:
            if not isinstance(user, User):
                return False
            return user.has_perm(settings.PURAIBETO_PERMISSION_CANVIEW, user_or_group=user, obj=self)

    def can_user_download(self, user=None):
        if settings.PURAIBETO_CHECK_PERMISSIONS:
            if not isinstance(user, User):
                return False
            return user.has_perm(settings.PURAIBETO_PERMISSION_CANDOWNLOAD, user_or_group=user, obj=self)


class PrivateFile(AttachedFileBase):
    pass
