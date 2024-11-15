from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Clears all Django caches configured in settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--wait',
            type=int,
            default=0,
            help='Wait specified seconds between clearing each cache'
        )

    def handle(self, *args, **kwargs):
        wait_time = kwargs['wait']
        
        # Get all configured caches
        if hasattr(settings, 'CACHES'):
            caches = settings.CACHES.keys()
        else:
            caches = ['default']
            
        for cache_name in caches:
            try:
                self.stdout.write(f'Clearing cache: {cache_name}')
                cache.caches[cache_name].clear()
                self.stdout.write(self.style.SUCCESS(f'Successfully cleared cache: {cache_name}'))
                
                if wait_time and cache_name != list(caches)[-1]:
                    self.stdout.write(f'Waiting {wait_time} seconds...')
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error clearing cache {cache_name}: {str(e)}')
                )