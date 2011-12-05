from django.core.management.base import NoArgsCommand
from main.models import *
import glob
import os

class Command(NoArgsCommand):
    help = "Recreates Thumbnails for Photos"

    def handle_noargs(self, **options):
        self.stdout.write('Removing items from Photo Cache.')
        for each in glob.glob(settings.MEDIA_ROOT+'thumb/*.jpg'):
            os.unlink(each)
        for each in glob.glob(settings.MEDIA_ROOT+'display/*.jpg'):
            os.unlink(each)

        self.stdout.write('\nRe-creating Photo Cache.\n')
        for photo in Photo.objects.all():
            print ('Generating thumbnails for %s' % photo.name)
            photo.create_sizes()    

