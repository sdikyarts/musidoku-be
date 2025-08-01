from .models import Artists, Puzzle, GameSubmission
from django.utils import timezone
import json

class GameValidator:
    @staticmethod
    def validate_artist_for_categories(artist, row_category, column_category):
        """
        Validate if the artist is associated with the given row and column categories.
        """
        row_valid, row_reason = GameValidator._validate_artist_category(artist, row_category)
        if not row_valid:
            return False, row_reason
        
        column_valid, column_reason = GameValidator._validate_artist_category(artist, column_category)
        if not column_valid:
            return False, column_reason
        
        return True, "Artist is valid for both row and column categories."
    
    @staticmethod
    def _validate_artist_category(artist, category):
        if category.validation_logic:
            try:
                logic = json.loads(category.validation_logic)
                field = logic["field"]
                lookup = logic["lookup"]
                value = logic["value"]
                filter_expr = {f"{field}__{lookup}": value}
                if Artists.objects.filter(pk=artist.pk, **filter_expr).exists():
                    return True, "Artist matches validation logic"
                else:
                    return False, f"Artist does not match logic: {filter_expr}"
            except Exception as e:
                return False, f"Invalid validation_logic: {e}"

        field = category.validation_field
        value = category.validation_value

        # Get the value from the artist dynamically
        artist_value = getattr(artist, field, None)
        if artist_value is None:
            return False, f"Artist does not have field {field}"

        # For boolean fields
        if isinstance(artist_value, bool):
            expected = value.lower() == "true"
            return artist_value == expected, f"Expected {expected}, got {artist_value}"

        # For other types (string, int, etc.)
        return str(artist_value) == str(value), f"Expected {value}, got {artist_value}"
    
    @staticmethod
    def get_valid_artists_for_cell(row_category, column_category):
        """
        Get all artists that are valid for both row and column categories.
        """
        artists = Artists.objects.all()
        valid_artists = []

        for artist in artists:
            is_valid, reason = GameValidator.validate_artist_for_categories(artist, row_category, column_category)
            if is_valid:
                valid_artists.append(artist.id)

        return Artists.objects.filter(id__in=valid_artists)

    @staticmethod
    def calculate_uniq_score(user_submissions, puzzle):
        """
        Calculate the unique score for a user based on their submissions.
        """
        total_score = 0
        total_cells = 0
        
        for submission in user_submissions:
            same_picks = GameSubmission.objects.filter(
                puzzle=puzzle,
                cell_index=submission.cell_index,
                selected_artist=submission.selected_artist
            ).count()

            cell_score = max(1, 100 - (same_picks * 5))
            total_score += cell_score
            total_cells += 1

        return round(total_score / total_cells, 2) if total_cells > 0 else 0
    
class PuzzleManager:
    @staticmethod
    def get_today_puzzle():
        """
        Get the puzzle for today. Assumes puzzles are being reset daily on Midnight UTC.
        """
        now_utc = timezone.now()
        today_utc = now_utc.date()
        try:
            return Puzzle.objects.get(created_at__date=today_utc)
        except Puzzle.DoesNotExist:
            return None
        
    @staticmethod
    def get_puzzle_grid_data(puzzle):
        """
        Returns structured data for puzzle grid
        """
        return {
            'puzzle_id': puzzle.puzzle_id,
            'date': puzzle.puzzle_date,
            'categories': {
                'rows': [
                    {
                        'id': puzzle.category_row_1.id,
                        'code': puzzle.category_row_1.code,
                        'name': puzzle.category_row_1.display_name,
                        'description': puzzle.category_row_1.description,
                        'category_type': puzzle.category_row_1.category_type,
                    },
                    {
                        'id': puzzle.category_row_2.id,
                        'code': puzzle.category_row_2.code,
                        'name': puzzle.category_row_2.display_name,
                        'description': puzzle.category_row_2.description,
                        'category_type': puzzle.category_row_2.category_type,
                    },
                    {
                        'id': puzzle.category_row_3.id,
                        'code': puzzle.category_row_3.code,
                        'name': puzzle.category_row_3.display_name,
                        'description': puzzle.category_row_3.description,
                        'category_type': puzzle.category_row_3.category_type,
                    }
                ],
                'columns': [
                    {
                        'id': puzzle.category_column_1.id,
                        'code': puzzle.category_column_1.code,
                        'name': puzzle.category_column_1.display_name,
                        'description': puzzle.category_column_1.description,
                        'category_type': puzzle.category_column_1.category_type,
                    },
                    {
                        'id': puzzle.category_column_2.id,
                        'code': puzzle.category_column_2.code,
                        'name': puzzle.category_column_2.display_name,
                        'description': puzzle.category_column_2.description,
                        'category_type': puzzle.category_column_2.category_type,
                    },
                    {
                        'id': puzzle.category_column_3.id,
                        'code': puzzle.category_column_3.code,
                        'name': puzzle.category_column_3.display_name,
                        'description': puzzle.category_column_3.description,
                        'category_type': puzzle.category_column_3.category_type,
                    }
                ]
            }
        }