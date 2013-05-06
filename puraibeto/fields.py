import os

from django.db.models.fields.files import FileField, FieldFile
from django.core.urlresolvers import reverse


class PrivateFieldFile(FieldFile):

    @property
    def url(self):
        self._require_file()
        filename = os.path.basename(self.path)
        return reverse('puraibeto_download', kwargs={
            "contenttype_pk": self.instance.content_type_id,
            "object_pk": self.instance.object_id,
            "pk": self.instance.pk,
            "uuid": self.instance.uuid,
            "filename": filename})

    @property
    def contidion(self):
        return self.field.condition

    @property
    def attachment(self):
        return self.field.attachment


def is_user_authenticated(request, instance):
    return (not request.user.is_anonymous()) and request.user.is_authenticated


class PrivateFileField(FileField):
    attr_class = PrivateFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, condition=is_user_authenticated, attachment=True, **kwargs):
        super(PrivateFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)
        self.condition = condition
        self.attachment = attachment
