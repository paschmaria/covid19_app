from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Model manager for User model with no username field
    extending the default BaseUserManager
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Default method for creating and saving a User with given email and password
        """

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User
        """

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is False:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
