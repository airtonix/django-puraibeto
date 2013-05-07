from __future__ import unicode_literals

import sys
import os
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.core.files.move import file_move_safe
from django.template.defaultfilters import slugify

from puraibeto.models import PrivateFile
from puraibeto.conf import settings


class Command(NoArgsCommand):
    """
    """
    help = "cleans up private filenames"

    option_list = NoArgsCommand.option_list + (
        make_option('--delete-orphans', '-o',
                    action='store_true',
                    dest='delete_orphans',
                    default=False,
                    help='Any PrivateFile instances without matching files will be deleted'),
        make_option('--blank-orphans', '-b',
                    action='store_true',
                    dest='blank_orphans',
                    default=False,
                    help='Any PrivateFile instances without matching files will be blanked'),
    )

    def handle_noargs(self, **options):
        processed = 0
        delete_orphans = options.get("delete_orphans", False)
        blank_orphans = options.get("blank_orphans", False)
        if blank_orphans and delete_orphans:
            raise Exception("Can't set both --blank-orphans and --delete-orphans")
            sys.exit()
        delete_orphans = not blank_orphans

        for item in PrivateFile.objects.all():
            if item.file is None:
                continue

            itempath = item.file.path

            if not os.path.exists(itempath):
                if delete_orphans:
                    item.delete()

                if blank_orphans:
                    print("Blanking {} {}".format(item.uuid, item.file))
                    item.file = ""
                    item.save()
                continue

            if " " in itempath:

                ext = None
                dirname = os.path.dirname(itempath)
                filename = os.path.basename(itempath)
                if "." in filename:
                    filename, ext = filename.split(".")
                    filename = ".".join([slugify(filename), ext])
                else:
                    filename = slugify(filename)
                new_path = os.sep.join([dirname, filename])
                file_move_safe(item.file.path, new_path)
                item.file = new_path.replace(settings.MEDIA_ROOT+"/", "")
                item.save()

                processed += 1

        if options['verbosity'] > 0:
            print("Cleaned up {} objects".format(processed))
