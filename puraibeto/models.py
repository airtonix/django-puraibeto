import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

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
        ext = None
        if "." in filename:
            filename, ext = filename.split(".")

        if " " in filename:
            filename = slugify(filename)

        filename = filename.lower()

        if not ext is None:
            filename = filename+"."+ext

        return "private/{content_type}/{contenttype_pk}/{object_id}/{uuid}-{filename}".format(
            content_type=instance.content_type.name.lower(),
            contenttype_pk=instance.content_type_id,
            object_id=instance.object_id,
            uuid=instance.uuid,
            filename=filename
        )

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
        return self.file

    def get_download_url(self, *args, **kwargs):
        return reverse('puraibeto_download', kwargs={
            "contenttype_pk": self.content_type_id,
            "object_pk": self.object_id,
            "pk": self.id,
            # "uuid": self.uuid,
            "filename": self.filename()
        })
        #     surl(r'^download/<contenttype_pk:#>/<object_pk:#>/<pk:#>/<uuid:uuid>-<filename:f>$',

    def save(self, *args, **kwargs):
        if not self.pk:
            super(AttachedFileBase, self).save(*args, **kwargs)

        if not self.name or len(self.name) <= 0:
            self.name = " ".join(self.filename().split(".")[:-1])
            super(AttachedFileBase, self).save(*args, **kwargs)

        signals.model_saved.send(sender=self)

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
