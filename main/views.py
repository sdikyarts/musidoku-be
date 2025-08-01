from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import Artists, Categories, Puzzle, GameSubmission
from .serializers import (
    ArtistSerializer, CategorySerializer, PuzzleSerializer, 
    GameSubmissionSerializer, ValidateGuessSerializer
)

from .logic import GameValidator, PuzzleManager

# Helper functions to get row and column categories for a puzzle
def get_row_categories(puzzle):
    return [puzzle.category_row_1, puzzle.category_row_2, puzzle.category_row_3]

def get_column_categories(puzzle):
    return [puzzle.category_column_1, puzzle.category_column_2, puzzle.category_column_3]

# Create your views here.
class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artists.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Artists.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(debut_year__icontains=search) |
                Q(origin_country__icontains=search) |
                Q(spotify_primary_genre__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        artists = Artists.objects.filter(name__icontains=query)[:10]
        
        return Response(list(artists))

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class PuzzleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Puzzle.objects.all()
    serializer_class = PuzzleSerializer
    
    @action(detail=True, methods=['get'])
    def valid_artists(self, request, pk=None):
        puzzle = self.get_object()
        row = int(request.query_params.get('row', 1))
        column = int(request.query_params.get('column', 1))
        

        row_categories = get_row_categories(puzzle)
        column_categories = get_column_categories(puzzle)

        row_category = row_categories[row - 1]
        column_category = column_categories[column - 1]
        
        valid_artists = GameValidator.get_valid_artists_for_cell(row_category, column_category)
        serializer = ArtistSerializer(valid_artists, many=True)
        
        return Response({
            'row_category': CategorySerializer(row_category).data,
            'column_category': CategorySerializer(column_category).data,
            'valid_artists': serializer.data,
            'count': valid_artists.count()
        })
        
class TodayPuzzleView(APIView):
    def get(self, request):
        puzzle = PuzzleManager.get_today_puzzle()
        if not puzzle:
            return Response({'error': 'No puzzle available for today.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PuzzleSerializer(puzzle)
        return Response(serializer.data)

class ValidateGuessView(APIView):
    def post(self,request):
        serializer = ValidateGuessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_id = data['user_id']
        puzzle_id = data['puzzle_id']
        cell_index = data['cell_index']
        selected_artist_id = data['selected_artist_id']

        puzzle = get_object_or_404(Puzzle, id=puzzle_id, is_active=True)
        artist = get_object_or_404(Artists, id=selected_artist_id)
        
        row, col = map(int, cell_index.split(','))
        
        row_categories = get_row_categories(puzzle)
        column_categories = get_column_categories(puzzle)
        
        row_category = row_categories[row - 1]
        column_category = column_categories[col - 1]
        
        is_valid, reason = GameValidator.validate_artist_for_categories(artist, row_category, column_category)
        
        existing_submission = GameSubmission.objects.filter(
            user_id=user_id, puzzle=puzzle, selected_artist=artist
        ).first()
        
        if existing_submission:
            return Response({
                'is_valid': False,
                'reason': 'You have already submitted this artist for this puzzle.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        submission = GameSubmission.objects.create(
            user_id=user_id,
            puzzle=puzzle,
            cell_index=cell_index,
            selected_artist=artist,
            is_correct=is_valid
        )
        
        return Response({
            'is_valid': is_valid,
            'reason': reason,
            'artist': ArtistSerializer(artist).data,
            'submission_id': submission.id
        })
    
class UserSubmissionsView(APIView):
    def get(self, request, user_id, puzzle_id):
        submissions = GameSubmission.objects.filter(
            user_id=user_id, puzzle_id=puzzle_id).order_by('created_at')

        serializer = GameSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class GameSubmissionViewSet(viewsets.ModelViewSet):
    queryset = GameSubmission.objects.all()
    serializer_class = GameSubmissionSerializer
    
    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        puzzle_id = self.request.data.get('puzzle_id')
        cell_index = self.request.data.get('cell_index')
        selected_artist_id = self.request.data.get('selected_artist_id')

        puzzle = get_object_or_404(Puzzle, id=puzzle_id, is_active=True)
        artist = get_object_or_404(Artists, id=selected_artist_id)

        serializer.save(user_id=user_id, puzzle=puzzle, cell_index=cell_index, selected_artist=artist)