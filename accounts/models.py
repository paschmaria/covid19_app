from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from .managers import UserManager


class User(AbstractUser):
    """
    Default User model
    """

    username = None
    email_confirmed = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True,
                            error_messages={
                                'unique': "A user with that email address already exists.",
                            })

    objects = UserManager()
    
    """Set email as username field and remove username from required fields"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ('-date_joined',)
        get_latest_by = ('-date_joined',)

    def __str__(self):
        return self.email


class USSDUser(models.Model):
    """
    Users of the USSD Service
    """

    phone_number = PhoneNumberField(unique=True)
    language = models.CharField(
                            _("default language"),
                            max_length=50,
                            blank=True,
                            default=''
                        )
    state = models.CharField(max_length=50, blank=True, default='')
    lga = models.CharField(max_length=100, blank=True, default='')
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("USSD User")

    def __str__(self):
        return self.phone_number
