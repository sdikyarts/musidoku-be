from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Artists
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Artists)
def update_artist_image_on_save(sender, instance, created, **kwargs):
    """
    Update artist image when an artist is saved
    Only for new artists or when spotify_id changes
    """
    if created and instance.spotify_id and not instance.cached_image_url:
        # For new artists, try to fetch image synchronously but with timeout protection
        try:
            from .utils import fetch_artist_image_from_spotify
            from django.utils import timezone
            
            new_image_url = fetch_artist_image_from_spotify(instance.spotify_id)
            if new_image_url:
                # Update the cache directly in the database
                Artists.objects.filter(pk=instance.pk).update(
                    cached_image_url=new_image_url,
                    image_last_updated=timezone.now()
                )
                logger.info(f"Updated image for new artist: {instance.name}")
                
        except Exception as e:
            logger.warning(f"Could not fetch image for new artist {instance.name}: {e}")
            # Don't fail the save operation if image fetch fails