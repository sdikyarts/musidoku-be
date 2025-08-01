from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'puzzles', PuzzleViewSet)
router.register(r'game-submissions', GameSubmissionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/today-puzzle/', TodayPuzzleView.as_view(), name='today-puzzle'),
    path('api/validate-guess/', ValidateGuessView.as_view(), name='validate-guess'),
    path('api/user-submissions/<int:user_id>/<int:puzzle_id>/', UserSubmissionsView.as_view(), name='user-submissions'),
]