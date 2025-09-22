from rest_framework import serializers
from .models import Categories, Puzzle, Artists, GameSubmission

class ArtistSerializer(serializers.ModelSerializer):
    normalized_genre = serializers.CharField(source='spotify_primary_genre', read_only=True)
    
    class Meta:
        model = Artists
        fields = ['id', 'roster_number', 'name', 'artist_type', 'origin_country', 'debut_year', 
                  'spotify_id', 'spotify_primary_genre', 'normalized_genre', 'image',
                  'uses_stage_name', 'has_grammy_win', 'has_hot100_entry', 'is_deceased', 'is_disbanded']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'code', 'display_name', 'description', 'category_type',
                  'validation_field', 'validation_value', 'validation_logic', 'is_active']

class PuzzleSerializer(serializers.ModelSerializer):
    categories= serializers.SerializerMethodField()
    
    class Meta:
        model = Puzzle
        fields = ['id', 'puzzle_date', 'categories', 'is_active']
        
    def get_categories(self, obj):
        return {
            'rows': [
                CategorySerializer(obj.category_row_1).data,
                CategorySerializer(obj.category_row_2).data,
                CategorySerializer(obj.category_row_3).data
            ],
            'columns': [
                CategorySerializer(obj.category_column_1).data,
                CategorySerializer(obj.category_column_2).data,
                CategorySerializer(obj.category_column_3).data
            ]
        }
        
class GameSubmissionSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='selected_artist.name', read_only=True)
    
    class Meta:
        model = GameSubmission
        fields = ['id', 'user_id', 'puzzle', 'cell_index', 'selected_artist',
                  'artist_name', 'is_correct', 'created_at', 'updated_at']
        
class ValidateGuessSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    puzzle_id = serializers.IntegerField()
    cell_index = serializers.IntegerField()
    artist_id = serializers.IntegerField()

    def validate_cell_index(self, value):
        if not value or ',' not in str(value):
            raise serializers.ValidationError("Cell index must be a valid string with comma-separated values.")
        
        try:
            row, col = value.split(',')
            row, col = int(row), int(col)
            if not (1 <= row <= 3 and 1 <= col <= 3):
                raise serializers.ValidationError("Cell index must be between 1,1 and 3,3.")
        except ValueError:
            raise serializers.ValidationError("Cell index must be a valid string with comma-separated integers.")
        return value