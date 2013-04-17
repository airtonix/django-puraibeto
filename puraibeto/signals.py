from django.dispatch import Signal

pre_download = Signal(providing_args=["instance", "request"])
