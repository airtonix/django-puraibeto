import os

from django.db.models.fields.files import FileField, ImageField, ImageFieldFile, FieldFile
from django.core.urlresolvers import reverse


class PrivateFieldFile(FieldFile):

    @property
    def url(self):
        self._require_file()
        app_label = self.instance._meta.app_label
        model_name  = self.instance._meta.object_name.lower()
        field_name = self.field.name
        filename = os.path.basename(self.path)

        return reverse('puraibeto_download', args=[
            self.intsance.attached_to.pk, self.instance.uuid, filename])

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

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, condition = is_user_authenticated, attachment = True, **kwargs):
        super(PrivateFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)
        self.condition = condition
        self.attachment = attachment