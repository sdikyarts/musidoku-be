from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Artists(models.Model):
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
    spotify_primary_genre = models.CharField(max_length=100)
    image = models.URLField(blank=True, null=True)
    uses_stage_name = models.BooleanField(blank=True, null=True)
    has_grammy_win = models.BooleanField(default=False)
    has_hot100_entry = models.BooleanField(default=False)
    is_deceased = models.BooleanField(blank=True, null=True)
    is_disbanded = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Artist"
        verbose_name_plural = "Artists"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
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
    name = models.CharField(max_length=255, unique=True)
    parent_company = models.CharField(max_length=255, blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    is_major = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ArtistLabels(models.Model):
    artist = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name='label_relationships')
    label = models.ForeignKey(Labels, on_delete=models.CASCADE, related_name='artist_relationships')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['artist', 'label']
    
        
class Albums(models.Model):
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

    def __str__(self):
        return self.title
    
class AlbumCollabs(models.Model):
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name='collabs')
    collab_artist_id = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name='collab_albums')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['album', 'collab_artist_id']


class Categories(models.Model):
    CATEGORY_TYPES = [
        ("geographic", "Geographic"),
        ("temporal", "Temporal"),
        ("genre", "Genre"),
        ("achievement", "Achievement"),
        ("attribute", "Attribute"),
        ("label", "Label"),
        ("other", "Other"),
    ]
    
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
    
    def __str__(self):
        return f"Puzzle for {self.puzzle_date}"
    
class GameSubmission(models.Model):
    user_id = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name='submissions')
    cell_index = models.CharField(max_length=10)  # '1,1', '1,2', etc.
    selected_artist = models.ForeignKey(Artists, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_id', 'puzzle', 'selected_artist']  # Prevent repetition
    
    def __str__(self):
        return f"{self.user_id} - {self.puzzle.puzzle_date} - {self.cell_index}"