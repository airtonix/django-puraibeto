from django.dispatch import Signal
from .conf import settings

pre_download = Signal(providing_args=["instance", "request"])
model_saved = Signal(providing_args=["instance", "request"])
