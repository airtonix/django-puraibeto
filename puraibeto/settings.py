from django.conf import settings

BACKEND = getattr(settings, 'PURAIBETO_BACKEND', 'basic')