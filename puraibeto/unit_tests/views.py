from django.views.generic import ListView, DetailView

from . import models


class ThingListView(ListView):
	model = models.Thing

class ThingDetailView(DetailView):
	model = models.Thing
