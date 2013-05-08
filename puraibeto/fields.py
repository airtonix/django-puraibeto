from django.db.models.fields.files import FileField, FieldFile


class PrivateFieldFile(FieldFile):

    @property
    def url(self):
        self._require_file()
        return self.instance.get_download_url(self.field.name)

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


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^puraibeto\.fields\.PrivateFileField"])
