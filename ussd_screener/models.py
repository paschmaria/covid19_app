import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from accounts.models import USSDUser


class Survey(models.Model):
    """
    Record of USSD Surveys
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(_("survey name"), max_length=100)
    service_code = models.CharField(max_length=50, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Session(models.Model):
    """
    Keep track of each USSD respondents session
    """

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(USSDUser, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, related_name="sessions", on_delete=models.CASCADE)
    session_id = models.CharField(_("Session ID"), max_length=100, db_index=True)

    def __str__(self):
        return self.session_id


class Page(models.Model):
    """
    Keep track of each survey page and the one before it
    """

    created = models.DateTimeField(auto_now_add=True)
    page_num = models.CharField(_("number"), max_length=50, db_index=True)
    text = models.CharField(max_length=225)
    parent = models.ForeignKey(
                        "self", related_name=_("previous_page"),
                        blank=True, null=True,
                        on_delete=models.CASCADE
                    )
    survey = models.ForeignKey(Survey, related_name="pages", on_delete=models.CASCADE)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ('-page_num',)
        get_latest_by = ('-created',)

    def __str__(self):
        return self.text[:50]


class Option(models.Model):
    """
    Keep track of the options for each survey page
    """

    created = models.DateTimeField(auto_now_add=True)
    number = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=225)
    page = models.ForeignKey(Page, related_name="options", on_delete=models.CASCADE)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ('-page', 'number')
        get_latest_by = ('-created',)

    def __str__(self):
        return f"{self.number}. {self.text}"
