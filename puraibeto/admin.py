from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from . import models
from .conf import settings

if settings.PURAIBETO_REGISTER_ADMIN:
    class PrivateFileAdmin(GuardedModelAdmin):
        list_display = ['name', 'file', 'attached_to']
    admin.site.register(models.PrivateFile, PrivateFileAdmin)
