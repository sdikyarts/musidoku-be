import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_spotify_client():
    """
    Create and return a Spotify client using client credentials flow
    (no user authentication required for public data)
    """
    try:
        from django.conf import settings
        
        # Check if settings are available
        if not hasattr(settings, 'SPOTIPY_CLIENT_ID') or not hasattr(settings, 'SPOTIPY_CLIENT_SECRET'):
            logger.error("Spotify credentials not found in settings")
            return None
            
        if not settings.SPOTIPY_CLIENT_ID or not settings.SPOTIPY_CLIENT_SECRET:
            logger.error("Spotify credentials are empty")
            return None
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    except ImportError as e:
        logger.error(f"Failed to import Spotify modules: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to create Spotify client: {e}")
        return None

def fetch_artist_image_from_spotify(spotify_id):
    """
    Fetch the primary image URL for an artist from Spotify API
    
    Args:
        spotify_id (str): The Spotify ID of the artist
    
    Returns:
        str or None: The image URL if found, None otherwise
    """
    if not spotify_id:
        return None
    
    sp = get_spotify_client()
    if not sp:
        return None
    
    try:
        # Get artist information from Spotify
        artist = sp.artist(spotify_id)
        images = artist.get('images', [])
        
        # Return the first (usually highest quality) image URL
        if images:
            return images[0]['url']
        
        logger.info(f"No images found for artist with Spotify ID: {spotify_id}")
        return None
        
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error for artist {spotify_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching image for artist {spotify_id}: {e}")
        return None

def update_artist_image(artist):
    """
    Update an artist's cached image from Spotify
    
    Args:
        artist: Artist model instance
    
    Returns:
        bool: True if image was updated, False otherwise
    """
    if not artist.spotify_id:
        logger.warning(f"Artist {artist.name} has no Spotify ID")
        return False
    
    new_image_url = fetch_artist_image_from_spotify(artist.spotify_id)
    
    if new_image_url and new_image_url != artist.cached_image_url:
        from django.utils import timezone
        artist.cached_image_url = new_image_url
        artist.image_last_updated = timezone.now()
        artist.save(update_fields=['cached_image_url', 'image_last_updated'])
        logger.info(f"Updated cached image for artist: {artist.name}")
        return True
    
    return False