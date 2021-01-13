from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#a-full-example
class UserProfile(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    email: str = models.EmailField(blank=False, db_index=True, unique=True,)

    is_staff: bool = models.BooleanField(default=False)
    is_active: bool = models.BooleanField(default=True)
    is_admin: bool = models.BooleanField(default=False)

    objects = UserManager()

    ### Super User
    # email: admin@example.com
    # password: password

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Message(models.Model):
    id: int = models.AutoField(auto_created=True, primary_key=True, verbose_name='ID')

    sender: UserProfile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='senders')
    receiver: UserProfile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receivers')
    content: str = models.TextField()
    date_sent = models.DateTimeField('date sent')