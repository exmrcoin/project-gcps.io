import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.store.models import StoreCategory


class Command(BaseCommand):
    help = 'Create the default categories of store'

    def handle(self, *args, **options):
        for cat in StoreCategory.objects.all():
            try:
                filename = cat.slug + '.svg'
                file = File(open(os.path.join(settings.PROJECT_PATH, 'apps', 'store', 'management',
                                              'commands', 'category_images', filename), 'rb'))
            except FileNotFoundError as e:
                self.stdout.write(self.style.SUCCESS(e))
                continue
            else:
                self.stdout.write(self.style.SUCCESS(
                    os.path.join(settings.PROJECT_PATH, 'apps', 'store', 'management', 'commands', 'category_images',
                                 filename)))
                cat.image.save(filename, file, save=True)
                self.stdout.write(self.style.SUCCESS('Upload image for %s"' % cat.name))
