from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Artists
from main.utils import update_artist_image
import time

class Command(BaseCommand):
    help = 'Update artist images from Spotify for all artists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of artists to process in each batch (default: 50)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.1,
            help='Delay between API calls in seconds (default: 0.1)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update images even if they already exist'
        )
        parser.add_argument(
            '--missing-only',
            action='store_true',
            help='Only update artists that currently have no image'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        delay = options['delay']
        force_update = options['force']
        missing_only = options['missing_only']

        # Build queryset based on options
        queryset = Artists.objects.exclude(spotify_id__isnull=True).exclude(spotify_id='')
        
        if missing_only:
            queryset = queryset.filter(cached_image_url__isnull=True)
            self.stdout.write(f"Processing artists with missing cached images only...")
        elif not force_update:
            queryset = queryset.filter(cached_image_url__isnull=True)
            self.stdout.write(f"Processing artists with missing cached images (use --force to update all)...")
        else:
            self.stdout.write(f"Processing all artists with Spotify IDs...")

        total_artists = queryset.count()
        self.stdout.write(f"Found {total_artists} artists to process")

        if total_artists == 0:
            self.stdout.write("No artists to process.")
            return

        updated_count = 0
        error_count = 0
        processed_count = 0

        # Process in batches
        for i in range(0, total_artists, batch_size):
            batch = queryset[i:i + batch_size]
            
            self.stdout.write(f"Processing batch {i//batch_size + 1}/{(total_artists-1)//batch_size + 1}")
            
            for artist in batch:
                processed_count += 1
                
                try:
                    # Show progress
                    if processed_count % 10 == 0:
                        self.stdout.write(f"Processed {processed_count}/{total_artists} artists...")
                    
                    # Update the image
                    if update_artist_image(artist):
                        updated_count += 1
                        self.stdout.write(f"✓ Updated image for: {artist.name}")
                    
                    # Add delay to respect API rate limits
                    if delay > 0:
                        time.sleep(delay)
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error updating {artist.name}: {e}")
                    )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Processed {processed_count} artists, "
                f"updated {updated_count} images, {error_count} errors."
            )
        )