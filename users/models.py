from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager
from .utils import generate_confirmation_code


class ConstUserRoles(models.TextChoices):
    USER = 'user', _('user')
    MODERATOR = 'moderator', _('moderator')
    ADMIN = 'admin', _('admin')


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name=_('email address'))
    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_('user name'))
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('bio'))
    role = models.CharField(
        max_length=9,
        choices=ConstUserRoles.choices,
        default='user',
        verbose_name=_('user role'))
    confirmation_code = models.CharField(
        null=True,
        max_length=10,
        default=generate_confirmation_code(),
        verbose_name=_('confirmation code'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = CustomUserManager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == ConstUserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == ConstUserRoles.MODERATOR
