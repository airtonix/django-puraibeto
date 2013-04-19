from django.db import models

class Thing(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField()

	@models.permalink
	def get_absolute_url(self):
		return ('thing-detail', (self.pk, ))