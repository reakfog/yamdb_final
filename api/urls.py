from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    TokenView,
    UsersViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet)


v1_router = DefaultRouter()
v1_router.register('users', UsersViewSet)
v1_router.register('titles', TitleViewSet, basename='titles_api')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='review')
comments_url = r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments'
v1_router.register(comments_url, CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/email/', RegisterView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(v1_router.urls))
]
