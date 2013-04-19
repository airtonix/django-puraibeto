from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy

from guardian.admin import GuardedModelAdmin

from . import models


class PrivateFileAdmin(GuardedModelAdmin):

    list_display = [ 'name', 'file', 'attached_to' ]

admin.site.register(models.PrivateFile, PrivateFileAdmin)