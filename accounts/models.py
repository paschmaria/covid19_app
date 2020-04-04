from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from .managers import UserManager


class BaseClass(models.Model):
    """
    Base class for models
    """
    created = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


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


class HealthStatus(BaseClass):
    """
    USSD User's health status
    """

    fever = models.BooleanField(default=False)
    cough = models.BooleanField(default=False)
    tiredness = models.BooleanField(default=False)
    difficult_breath = models.BooleanField(default=False)
    sore_throat = models.BooleanField(default=False)
    primary_contact = models.BooleanField(default=False)    
    secondary_contact = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Health Status")

    def __str__(self):
        return self.risk_level 

    @property
    def risk_level(self):
        if (
            self.fever and
            self.cough and
            self.tiredness and
            self.difficult_breath
        ):
            if (
                self.primary_contact or
                self.secondary_contact
            ):
                return "very high"
            elif self.sore_throat:
                return "very high"
            else:
                return "high"
        elif (
            self.primary_contact or
            self.secondary_contact
        ):
            if (
                (self.fever and self.cough) or
                (self.cough and self.tiredness) or
                (self.fever and self.tiredness) or
                (self.fever and self.cough and self.tiredness)
            ):
                return "medium"

        return "low"


class USSDUser(BaseClass):
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
    health_status = models.ForeignKey(
                            HealthStatus, 
                            related_name="respondent",
                            on_delete=models.PROTECT
                        )

    class Meta:
        verbose_name = _("USSD User")

    def __str__(self):
        return str(self.phone_number)

    def save(self, *args, **kwargs):
        if not self.health_status_id:
            health_status = HealthStatus()
            health_status.save()
            self.health_status = health_status
        return super().save(*args, **kwargs)
