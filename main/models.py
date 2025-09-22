from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid, re

# Create your models here.
class Artists(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ARTIST_TYPES = [
        ("Solo", "Solo"),
        ("Group", "Group"),
    ]
    
    GENRE_MAPPING = {
        'Rap': 'Hip-Hop',
        'Pop': 'Pop',
        'Reggaeton': 'Latin',
        'Soft Pop': 'Pop',
        'Hip Hop': 'Hip-Hop',
        'Alternative': 'Alternative',
        'K-pop': ['K-Pop', 'Pop'],
        'Melodic Rap': 'Hip-Hop',
        'Hip-hop': 'Hip-Hop',
        'R&b': 'R&B',
        'Emo Rap': 'Hip-Hop',
        'Edm': 'Electronic',
        'R&B': 'R&B',
        'Art Pop': 'Pop',
        'Classic Rock': 'Rock',
        'Latin Pop': 'Latin',
        'Nu Metal': 'Rock',
        'Trap Soul': 'R&B',
        'Hindi Pop': 'Bollywood',
        'Corrido': 'Latin',
        'Indie': 'Alternative',
        'Country': 'Country',
        'Electronic': 'Electronic',
        'Bollywood': 'Bollywood',
        'Rage Rap': 'Hip-Hop',
        'Corridos Tumbados': 'Latin',
        'G-funk': 'Hip-Hop',
        'Tropical House': 'Electronic',
        'Funk Rock': 'Rock',
        'East Coast Hip Hop': 'Hip-Hop',
        'Rock': 'Rock',
        'Bachata': 'Latin',
        'Brooklyn Drill': 'Hip-Hop',
        'Metal': 'Metal',
        'Moombahton': 'Electronic',
        'Trap': 'Hip-Hop',
        'French House': 'Electronic',
        'Dancehall': 'Reggae',
        'Mariachi': 'Latin',
        'Chicago Drill': 'Hip-Hop',
        'Southern Hip Hop': 'Hip-Hop',
        'Argentine Trap': 'Latin',
        'Sertanejo': 'Latin',
        'Emo': 'Rock',
        'Banda': 'Latin',
        'Brazilian Pop': 'Latin',
        'Colombian Pop': 'Latin',
        'Singer-songwriter': 'Alternative',
        'Soul / Motown R&B': 'R&B',
        'Christian Hip Hop': 'Hip-Hop',
        'Old School Hip Hop': 'Hip-Hop',
        'Christmas': 'Pop',
        'French Rap': 'Hip-Hop',
        'Tamil Pop': 'Bollywood',
        'Grunge': 'Rock',
        'Punk': 'Rock',
        'Hyperpop': 'Pop',
        'Neo-psychedelic': 'Alternative',
        'Dubstep': 'Electronic',
        'Art Rock': 'Rock',
        'Progressive Rock': 'Rock',
        'Urbano Latino': 'Latin',
        'Cumbia Norteña': 'Latin',
        'Rockabilly': 'Rock',
        'Latin': 'Latin',
        'Dream Pop': 'Alternative',
    }
    
    name = models.CharField(max_length=255)
    artist_type = models.CharField(max_length=10, choices=ARTIST_TYPES)
    origin_country = models.CharField(max_length=2)
    debut_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    spotify_id = models.CharField(max_length=22)
    spotify_primary_genre = models.CharField(max_length=100)
    # Removed manual image field - now using automatic Spotify fetching
    cached_image_url = models.URLField(blank=True, null=True, help_text="Cached image URL from Spotify")
    image_last_updated = models.DateTimeField(blank=True, null=True, help_text="When the image was last fetched")
    roster_number = models.PositiveIntegerField(unique=True, null=True, blank=True, 
                                              help_text="Sequential number based on when artist was added (1st added = #1)")
    uses_stage_name = models.BooleanField(blank=True, null=True)
    has_grammy_win = models.BooleanField(default=False)
    has_hot100_entry = models.BooleanField(default=False)
    is_deceased = models.BooleanField(blank=True, null=True)
    is_disbanded = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False, blank=True, null=True)
    
    class Meta:
        verbose_name = "Artist"
        verbose_name_plural = "Artists"
        ordering = ['roster_number']  # Order by roster number (chronological order)
    
    def __str__(self):
        return f"#{self.roster_number} - {self.name}" if self.roster_number else self.name
    
    def clean_slug(self, name):
        name = re.sub(r'[^\w\s-]', '', name)
        return slugify(name)

    def get_disambiguator(self):
        return self.origin_country or str(self.debut_year)

    def save(self, *args, **kwargs):
        # Handle slug generation
        if not self.slug or self.name != Artists.objects.filter(pk=self.pk).first().name if self.pk else None:
            base_slug = self.clean_slug(self.name)
            slug = base_slug
            counter = 1
            while Artists.objects.filter(slug__iexact=slug).exclude(pk=self.pk).exists():
                # For LISA vs LiSA, append disambiguator (country, etc.)
                disambiguator = self.get_disambiguator()
                slug = f"{base_slug}-{disambiguator.lower()}"
                if Artists.objects.filter(slug__iexact=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{disambiguator.lower()}-{counter}"
                    counter += 1
            self.slug = slug
        
        # Auto-assign roster number for new artists
        if not self.roster_number and not self.pk:
            # Get the highest existing roster number and add 1
            max_roster = Artists.objects.aggregate(
                max_roster=models.Max('roster_number')
            )['max_roster']
            self.roster_number = (max_roster or 0) + 1
        
        # Check if we should update the image from Spotify
        should_fetch_image = (
            self.spotify_id and  # Has Spotify ID
            (not self.cached_image_url or  # No cached image
             not self.pk or     # New artist being created
             kwargs.get('force_image_update', False))  # Force update flag
        )
        
        # Save first to ensure the object exists
        super().save(*args, **kwargs)
        
        # Fetch image from Spotify if needed
        if should_fetch_image:
            from .utils import fetch_artist_image_from_spotify
            from django.utils import timezone
            try:
                new_image_url = fetch_artist_image_from_spotify(self.spotify_id)
                if new_image_url and new_image_url != self.cached_image_url:
                    # Update cached image without triggering another save cycle
                    Artists.objects.filter(pk=self.pk).update(
                        cached_image_url=new_image_url,
                        image_last_updated=timezone.now()
                    )
                    self.cached_image_url = new_image_url
                    self.image_last_updated = timezone.now()
            except Exception as e:
                # Log error but don't fail the save operation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to fetch image for artist {self.name}: {e}")
    
    @property
    def image(self):
        """
        Automatically fetch and cache image from Spotify
        Returns cached image if available and recent, otherwise fetches fresh
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # If we have a cached image that's less than 24 hours old, use it
        if (self.cached_image_url and self.image_last_updated and 
            timezone.now() - self.image_last_updated < timedelta(hours=24)):
            return self.cached_image_url
        
        # If we have a Spotify ID, try to fetch fresh image
        if self.spotify_id:
            from .utils import fetch_artist_image_from_spotify
            try:
                new_image_url = fetch_artist_image_from_spotify(self.spotify_id)
                if new_image_url:
                    # Update the cache
                    Artists.objects.filter(pk=self.pk).update(
                        cached_image_url=new_image_url,
                        image_last_updated=timezone.now()
                    )
                    self.cached_image_url = new_image_url
                    self.image_last_updated = timezone.now()
                    return new_image_url
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to fetch fresh image for artist {self.name}: {e}")
        
        # Fallback to cached image or None
        return self.cached_image_url
    
    
    @property
    def normalized_genre(self):
        genre = self.spotify_primary_genre
        if genre in self.GENRE_MAPPING:
            mapped_genre = self.GENRE_MAPPING[genre]
            if isinstance(mapped_genre, list):
                return mapped_genre[0]
            return mapped_genre
        return genre

class Labels(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    parent_company = models.CharField(max_length=255, blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    is_major = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
    
    def __str__(self):
        return self.name
    
class ArtistLabels(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name='label_relationships')
    label = models.ForeignKey(Labels, on_delete=models.CASCADE, related_name='artist_relationships')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['artist', 'label']
    
        
class Albums(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    primary_artist = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    peak_chart_pos = models.IntegerField(blank=True, null=True)
    has_number_one = models.BooleanField(default=False)
    is_collab = models.BooleanField(default=False)
    spotify_id = models.CharField(max_length=22, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def __str__(self):
        return self.title
    
class AlbumCollabs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name='collabs')
    collab_artist_id = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name='collab_albums')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['album', 'collab_artist_id']


class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CATEGORY_TYPES = [
        ("geographic", "Geographic"),
        ("temporal", "Temporal"),
        ("genre", "Genre"),
        ("achievement", "Achievement"),
        ("attribute", "Attribute"),
        ("label", "Label"),
        ("other", "Other"),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    validation_field = models.CharField(max_length=50)
    validation_value = models.CharField(max_length=100, blank=True, null=True)
    validation_logic = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.display_name

class Puzzle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    puzzle_date = models.DateField(unique=True)
    category_row_1 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='row1_puzzles')
    category_row_2 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='row2_puzzles')
    category_row_3 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='row3_puzzles')
    category_col_1 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='col1_puzzles')
    category_col_2 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='col2_puzzles')
    category_col_3 = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='col3_puzzles')

    # Creator picks for each cell (optional)
    creator_pick_1_1 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_1_1')
    creator_pick_1_2 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_1_2')
    creator_pick_1_3 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_1_3')
    creator_pick_2_1 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_2_1')
    creator_pick_2_2 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_2_2')
    creator_pick_2_3 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_2_3')
    creator_pick_3_1 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_3_1')
    creator_pick_3_2 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_3_2')
    creator_pick_3_3 = models.ForeignKey(Artists, on_delete=models.SET_NULL, null=True, blank=True, related_name='pick_3_3')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Puzzle"
        verbose_name_plural = "Puzzles"
    
    def __str__(self):
        return f"Puzzle for {self.puzzle_date}"
    
class GameSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name='submissions')
    cell_index = models.CharField(max_length=10)  # '1,1', '1,2', etc.
    selected_artist = models.ForeignKey(Artists, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_id', 'puzzle', 'selected_artist']  # Prevent repetition
        verbose_name = "Game Submission"
        verbose_name_plural = "Game Submissions"
    
    def __str__(self):
        return f"{self.user_id} - {self.puzzle.puzzle_date} - {self.cell_index}"