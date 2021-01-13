from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#a-full-example
class UserProfile(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    email: str = models.EmailField(blank=False, db_index=True, unique=True)

    is_staff: bool = models.BooleanField(default=False)
    is_active: bool = models.BooleanField(default=True)
    is_admin: bool = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class MessageConfig(models.Model):
    # https://developers.google.com/gmail/api/guides/labels#types_of_labels
    POSSIBLE_LABELS = [
        'INBOX',
        'SPAM',
        'TRASH',
        'UNREAD',
        'STARRED',
        'IMPORTANT',
        'SENT', # cannot be manually applied.
        'DRAFT', # cannot be manually applied.
        'CATEGORY_PERSONAL',
        'CATEGORY_SOCIAL',
        'CATEGORY_PROMOTIONS',
        'CATEGORY_UPDATES',
        'CATEGORY_FORUMS'
    ]

    id: int = models.AutoField(primary_key=True)

    inbox: bool = models.BooleanField(default=False)
    spam: bool = models.BooleanField(default=False)
    trash: bool = models.BooleanField(default=False)
    unread: bool = models.BooleanField(default=False)
    starred: bool = models.BooleanField(default=False)
    important: bool = models.BooleanField(default=False)
    sent: bool = models.BooleanField(default=False)
    draft: bool = models.BooleanField(default=False)
    category_personal: bool = models.BooleanField(default=False)
    category_social: bool = models.BooleanField(default=False)
    category_promotions: bool = models.BooleanField(default=False)
    category_updates: bool = models.BooleanField(default=False)
    category_forums: bool = models.BooleanField(default=False)


class Message(models.Model):
    id: str = models.CharField(primary_key=True, unique=True, max_length=100)

    sender: UserProfile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='senders')
    receiver: UserProfile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receivers')
    content: str = models.TextField()
    date_sent = models.DateTimeField('date sent')
    config: MessageConfig = models.ForeignKey(MessageConfig, on_delete=models.CASCADE, related_name='labels')

    def __str__(self) -> str:
        return f"<Message: {self.id} -> {self.content[:30] + '...'}>"
