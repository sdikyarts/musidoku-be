from django.contrib import admin
from .models import Artists, Labels, Albums, ArtistLabels, AlbumCollabs, Categories, Puzzle, GameSubmission

# Register your models here.
@admin.register(Artists)
class ArtistsAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist_type', 'origin_country', 'debut_year', 'spotify_id','spotify_primary_genre', 'image', 'uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
    list_filter = ['artist_type', 'origin_country', 'debut_year', 'spotify_id', 'spotify_primary_genre', 'uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
    search_fields = ['name', 'origin_country', 'spotify_primary_genre']
    list_editable = ['uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'artist_type', 'origin_country', 'debut_year', 'spotify_id', 'spotify_primary_genre', 'image')
        }),
        ('Attribute', {
            'fields': ('uses_stage_name',)
        }),
        ('Achievements', {
            'fields': ('has_grammy_win', 'has_hot100_entry')
        }),
        ('Status', {
            'fields': ('is_deceased', 'is_disbanded')
        })
    )

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