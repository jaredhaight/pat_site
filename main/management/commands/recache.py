from django.core.management.base import NoArgsCommand
from main.models import *
import glob
import os

class Command(NoArgsCommand):
    help = "Recreates Thumbnails for Photos"

    def handle_noargs(self, **options):
        self.stdout.write('Removing items from Photo Cache.')
        for photo in Photo.objects.all():
            print ('Removing thumbnails for %s' % photo.name)
            photo.clear_photos()


        self.stdout.write('\nRe-creating Photo Cache.\n')
        for photo in Photo.objects.all():
            print ('Generating thumbnails for %s' % photo.name)
            photo.create_sizes()    

