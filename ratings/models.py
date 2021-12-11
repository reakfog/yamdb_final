from django.db import models
from users.models import CustomUser as User
from django.core.validators import MinValueValidator, MaxValueValidator
import textwrap


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.id}, {self.name}, {self.slug}'


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    year = models.SmallIntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        db_index=False,)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,)
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True, null=True,
        help_text='Добавить описание произведения')

    def __str__(self):
        name = textwrap.shorten(self.name, 50, placeholder="")
        return f'{self.category}, {self.genre}, {name}, {self.year}'

    class Meta:
        ordering = ['id', ]


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Автор",)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)])
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Произведение",)

    class Meta:
        ordering = ['-id']


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор",)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Отзыв",)

    class Meta:
        ordering = ['-id']
