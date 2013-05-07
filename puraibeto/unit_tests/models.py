from django.db import models
from puraibeto.fields import PrivateFileField


class Thing(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    @models.permalink
    def get_absolute_url(self):
        return ('thing-detail', (self.pk, ))
