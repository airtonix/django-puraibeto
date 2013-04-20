from django.dispatch import Signal
from .conf import settings

pre_download = Signal(providing_args=["instance", "request"])
