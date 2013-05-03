from django.conf import settings
from appconf import AppConf


class PuraibetoConf(AppConf):
    BACKEND = "basic"
    PERMISSION_CANDOWNLOAD = 'download_privatefile'
    PERMISSION_CANCREATE = 'add_privatefile'
    PERMISSION_CANVIEW = 'view_privatefile'
    PERMISSION_CANDELETE = 'delete_privatefile'
    PERMISSION_CANCHANGE = 'change_privatefile'
    REGISTER_ADMIN = False
