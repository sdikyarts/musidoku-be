from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Artists, Labels, Albums, ArtistLabels, AlbumCollabs, Categories, Puzzle, GameSubmission
from .utils import update_artist_image
from .constants import COUNTRY_CONTINENTS, COUNTRY_SUBREGIONS, GENRE_MAPPING


# Custom Admin Filters
class DecadeFilter(admin.SimpleListFilter):
    title = 'debut decade'
    parameter_name = 'debut_decade'

    def lookups(self, request, model_admin):
        return [
            ('1950s', '1950s (1950-1959)'),
            ('1960s', '1960s (1960-1969)'),
            ('1970s', '1970s (1970-1979)'),
            ('1980s', '1980s (1980-1989)'),
            ('1990s', '1990s (1990-1999)'),
            ('2000s', '2000s (2000-2009)'),
            ('2010s', '2010s (2010-2019)'),
            ('2020s', '2020s (2020-2029)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1950s':
            return queryset.filter(debut_year__gte=1950, debut_year__lte=1959)
        elif self.value() == '1960s':
            return queryset.filter(debut_year__gte=1960, debut_year__lte=1969)
        elif self.value() == '1970s':
            return queryset.filter(debut_year__gte=1970, debut_year__lte=1979)
        elif self.value() == '1980s':
            return queryset.filter(debut_year__gte=1980, debut_year__lte=1989)
        elif self.value() == '1990s':
            return queryset.filter(debut_year__gte=1990, debut_year__lte=1999)
        elif self.value() == '2000s':
            return queryset.filter(debut_year__gte=2000, debut_year__lte=2009)
        elif self.value() == '2010s':
            return queryset.filter(debut_year__gte=2010, debut_year__lte=2019)
        elif self.value() == '2020s':
            return queryset.filter(debut_year__gte=2020, debut_year__lte=2029)
        return queryset


class GenreCategoryFilter(admin.SimpleListFilter):
    title = 'genre category'
    parameter_name = 'genre_category'

    def lookups(self, request, model_admin):
        # Get unique genre categories from the GENRE_MAPPING
        genre_categories = set()
        for original_genre, mapped_genre in GENRE_MAPPING.items():
            if isinstance(mapped_genre, list):
                genre_categories.update(mapped_genre)
            else:
                genre_categories.add(mapped_genre)
        
        # Sort and return as choices
        return [(category, category) for category in sorted(genre_categories)]

    def queryset(self, request, queryset):
        if self.value():
            # Find all original genres that map to this category
            matching_genres = []
            for original_genre, mapped_genre in GENRE_MAPPING.items():
                if isinstance(mapped_genre, list):
                    if self.value() in mapped_genre:
                        matching_genres.append(original_genre)
                else:
                    if mapped_genre == self.value():
                        matching_genres.append(original_genre)
            
            return queryset.filter(spotify_primary_genre__in=matching_genres)
        return queryset


class ContinentFilter(admin.SimpleListFilter):
    title = 'continent'
    parameter_name = 'continent'

    def lookups(self, request, model_admin):
        return [
            ('North America', 'North America'),
            ('Central America & Caribbean', 'Central America & Caribbean'),
            ('South America', 'South America'),
            ('Europe', 'Europe'),
            ('Asia', 'Asia'),
            ('Africa', 'Africa'),
            ('Oceania', 'Oceania'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            # Find all countries that belong to this continent
            matching_countries = [
                country for country, continent in COUNTRY_CONTINENTS.items()
                if continent == self.value()
            ]
            return queryset.filter(origin_country__in=matching_countries)
        return queryset


class SubregionFilter(admin.SimpleListFilter):
    title = 'sub-region'
    parameter_name = 'subregion'

    def lookups(self, request, model_admin):
        return [
            # North America
            ('United States', 'United States'),
            ('Canada', 'Canada'),
            ('Mexico', 'Mexico'),
            
            # Europe
            ('Western Europe', 'Western Europe'),
            ('Northern Europe', 'Northern Europe'),
            ('Eastern Europe', 'Eastern Europe'),
            ('Southern Europe', 'Southern Europe'),
            
            # Asia
            ('East Asia', 'East Asia'),
            ('Southeast Asia', 'Southeast Asia'),
            ('South Asia', 'South Asia'),
            ('Central Asia', 'Central Asia'),
            ('Western Asia', 'Western Asia (Middle East)'),
            
            # Oceania
            ('Australia & New Zealand', 'Australia & New Zealand'),
            ('Pacific Islands', 'Pacific Islands'),
            
            # South America
            ('Brazil', 'Brazil'),
            ('Southern Cone', 'Southern Cone'),
            ('Northern Countries', 'Northern Countries'),
            ('Andean Countries', 'Andean Countries'),
            
            # Central America & Caribbean
            ('Central America', 'Central America'),
            ('Caribbean', 'Caribbean'),
            
            # Africa
            ('North Africa', 'North Africa'),
            ('West Africa', 'West Africa'),
            ('East Africa', 'East Africa'),
            ('Central Africa', 'Central Africa'),
            ('Southern Africa', 'Southern Africa'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            # Find all countries that belong to this sub-region
            matching_countries = [
                country for country, subregion in COUNTRY_SUBREGIONS.items()
                if subregion == self.value()
            ]
            return queryset.filter(origin_country__in=matching_countries)
        return queryset

# Register your models here.
@admin.register(Artists)
class ArtistsAdmin(admin.ModelAdmin):
    list_display = ['roster_number', 'name', 'artist_type', 'origin_country', 'debut_year', 'spotify_id','spotify_primary_genre', 'image_thumbnail', 'uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
    list_filter = [
        'artist_type', 
        ContinentFilter,           # Broad continent grouping
        SubregionFilter,           # More specific sub-region grouping
        'origin_country',          # Still keep individual countries
        DecadeFilter,              # Decade grouping with extended coverage
        GenreCategoryFilter,       # Genre categories instead of specific genres
        'uses_stage_name', 
        'has_grammy_win', 
        'has_hot100_entry', 
        'is_deceased', 
        'is_disbanded'
    ]
    search_fields = ['name', 'origin_country', 'spotify_primary_genre', 'roster_number']
    list_editable = ['uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
    readonly_fields = ['created_at', 'updated_at', 'image_preview', 'cached_image_url', 'image_last_updated', 'roster_number']
    actions = ['refresh_images_from_spotify']
    ordering = ['roster_number']  # Default order by roster number

    fieldsets = (
        ('Basic Information', {
            'fields': ('roster_number', 'name', 'artist_type', 'origin_country', 'debut_year', 'spotify_id', 'spotify_primary_genre')
        }),
        ('Auto-Generated Image (from Spotify)', {
            'fields': ('image_preview', 'cached_image_url', 'image_last_updated'),
            'description': 'Images are automatically fetched from Spotify using the Spotify ID. The image property will always return the latest image from Spotify.'
        }),
        ('Attribute', {
            'fields': ('uses_stage_name',)
        }),
        ('Achievements', {
            'fields': ('has_grammy_win', 'has_hot100_entry')
        }),
        ('Status', {
            'fields': ('is_deceased', 'is_disbanded')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def image_thumbnail(self, obj):
        """Display a small thumbnail of the artist image in the list view"""
        try:
            # Use cached image URL to avoid triggering API calls in list view
            image_url = obj.cached_image_url
            if image_url:
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                    image_url
                )
            return "No cached image"
        except Exception as e:
            return "Error loading image"
    image_thumbnail.short_description = "Image (Cached)"

    def image_preview(self, obj):
        """Display a larger preview of the artist image in the detail view"""
        try:
            # Try cached image first, fallback to live fetch for detail view only
            image_url = obj.cached_image_url
            if not image_url:
                # Only fetch live image in detail view, not list view
                try:
                    image_url = obj.image  # This will trigger automatic fetching
                except Exception:
                    pass
            
            if image_url:
                return format_html(
                    '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                    image_url
                )
            return "No image available"
        except Exception as e:
            return f"Error loading image: {str(e)}"
    image_preview.short_description = "Auto-Generated Image Preview"

    def refresh_images_from_spotify(self, request, queryset):
        """Admin action to force refresh images for selected artists"""
        updated_count = 0
        error_count = 0
        
        for artist in queryset:
            try:
                from .utils import update_artist_image
                if update_artist_image(artist):
                    updated_count += 1
            except Exception as e:
                error_count += 1
                
        if updated_count > 0:
            messages.success(
                request,
                f"Successfully refreshed images for {updated_count} artist(s)."
            )
        if error_count > 0:
            messages.error(
                request,
                f"Failed to refresh images for {error_count} artist(s)."
            )
        if updated_count == 0 and error_count == 0:
            messages.info(
                request,
                "No new images found or no updates needed."
            )
    
    refresh_images_from_spotify.short_description = "Force refresh images from Spotify"

class ArtistLabelsInline(admin.TabularInline):
    model = ArtistLabels
    extra = 1

@admin.register(Labels)
class LabelsAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_company', 'founded_year', 'country', 'is_major']
    list_filter = ['is_major', 'country']
    search_fields = ['name', 'parent_company']
    inlines = [ArtistLabelsInline]
    readonly_fields = ['created_at', 'updated_at']
    
class AlbumCollabsInline(admin.TabularInline):
    model = AlbumCollabs
    extra = 1

@admin.register(Albums)
class AlbumsAdmin(admin.ModelAdmin):
    list_display = ['title', 'primary_artist', 'release_date', 'spotify_id', 'peak_chart_pos', 'has_number_one', 'is_collab', 'image']
    list_filter = ['has_number_one', 'is_collab', 'release_date']
    search_fields = ['title', 'artist__name', 'spotify_id']
    inlines = [AlbumCollabsInline]
    readonly_fields = ['created_at', 'updated_at']
    
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'code', 'category_type', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['display_name', 'code']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ['puzzle_date', 'is_active', 'row_categories', 'col_categories']
    list_filter = ['is_active', 'puzzle_date']
    date_hierarchy = 'puzzle_date'
    
    fieldsets = (
        ('Puzzle Date', {
            'fields': ('puzzle_date', 'is_active')
        }),
        ('Row Categories', {
            'fields': ('category_row_1', 'category_row_2', 'category_row_3')
        }),
        ('Column Categories', {
            'fields': ('category_col_1', 'category_col_2', 'category_col_3')
        }),
        ('Creator Picks (Optional)', {
            'fields': (
                ('creator_pick_1_1', 'creator_pick_1_2', 'creator_pick_1_3'),
                ('creator_pick_2_1', 'creator_pick_2_2', 'creator_pick_2_3'),
                ('creator_pick_3_1', 'creator_pick_3_2', 'creator_pick_3_3'),
            ),
            'classes': ('collapse',)
        }),
    )
    
    def row_categories(self, obj):
        return f"{obj.category_row_1.display_name} | {obj.category_row_2.display_name} | {obj.category_row_3.display_name}"
    
    def col_categories(self, obj):
        return f"{obj.category_col_1.display_name} | {obj.category_col_2.display_name} | {obj.category_col_3.display_name}"

@admin.register(GameSubmission)
class GameSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'puzzle', 'cell_index', 'selected_artist', 'timestamp']
    list_filter = ['puzzle__puzzle_date', 'cell_index']
    search_fields = ['user_id', 'selected_artist__name']
    readonly_fields = ['timestamp']