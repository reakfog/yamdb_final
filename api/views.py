from django.db.models import Max, Avg
from django.shortcuts import get_object_or_404
from rest_framework import (
    status,
    permissions,
    viewsets,
    views,
    filters,
    serializers)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from .utils import send_mail_to_user, generate_confirmation_code
from .viewsets import CatGenViewSet
from .filterset import TitleFilter
from ratings.models import (
    User,
    Category,
    Genre,
    Title,
    Review,
    Comment)
from .serializers import (
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer)
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsSuperuser,
    IsAuthorOrAdminOrModerator)


BASE_USERNAME = 'User'


class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        if len(user) > 0:
            confirmation_code = user[0].confirmation_code
        else:
            confirmation_code = generate_confirmation_code()
            max_id = User.objects.aggregate(Max('id'))['id__max'] + 1
            data = {
                'email': email,
                'confirmation_code': confirmation_code,
                'username': f'{BASE_USERNAME}{max_id}'}
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        send_mail_to_user(email, confirmation_code)
        return Response({'email': email})


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def post(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            response = {'confirmation_code': 'Неверный код для данного email'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {'token': self.get_token(user)}
        return Response(response, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsSuperuser | IsAdmin,)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', 'patch'],
        url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(
                request.user,
                many=False)
            return Response(serializer.data)


class CategoryViewSet(CatGenViewSet):
    """View-класс категорий"""
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]


class GenreViewSet(CatGenViewSet):
    """View-класс жанров"""
    permission_classes = [IsAdminOrReadOnly]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]


class TitleViewSet(viewsets.ModelViewSet):
    """View-класс произведений"""
    permission_classes = [IsAdminOrReadOnly]
    queryset = Title.objects.all().order_by('-id')
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        return Review.objects.filter(title__id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.request.user
        if Review.objects.filter(title=title, author=author).count() > 0:
            raise serializers.ValidationError('You already reviewed the title')
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        return Comment.objects.filter(review__id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
