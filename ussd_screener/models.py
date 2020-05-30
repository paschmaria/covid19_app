import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from accounts.models import USSDUser


class BaseClass(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Survey(BaseClass):
    """
    Record of USSD Surveys
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("survey name"), max_length=100)
    service_code = models.CharField(max_length=50, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Session(BaseClass):
    """
    Keep track of each USSD respondents session
    """

    user = models.ForeignKey(USSDUser, related_name="user_sessions", on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, related_name="survey_sessions", on_delete=models.CASCADE)
    session_id = models.CharField(_("Session ID"), max_length=100, db_index=True)
    prev_page_id = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.session_id


class SurveyResponse(BaseClass):
    """
    Keeps track of survey responses per session
    """

    session = models.ForeignKey(Session, related_name="survey_responses", on_delete=models.CASCADE)
    question_text = models.CharField(max_length=225)
    response = models.CharField(max_length=100)
    weight = models.CharField(_("weight of response"), max_length=50)

    def __str__(self):
        return self.question_text


class Page(BaseClass):
    """
    Keep track of each survey page
    """

    page_num = models.CharField(_("number"), max_length=50, db_index=True)
    text = models.CharField(max_length=225)
    extra_text = models.TextField(max_length=300, blank=True, default="")
    parent = models.ForeignKey(
                        "self", related_name="next_page",
                        blank=True, null=True,
                        on_delete=models.CASCADE
                    )
    survey = models.ForeignKey(Survey, related_name="pages", on_delete=models.CASCADE)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ('page_num',)
        get_latest_by = ('-created',)

    def __str__(self):
        return self.text[:50]


class Option(BaseClass):
    """
    Keep track of the options for each survey page
    """

    number = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=225)
    pages = models.ManyToManyField(Page, related_name="options", related_query_name="options")
    history = HistoricalRecords()
    
    class Meta:
        ordering = ('number',)
        get_latest_by = ('-created',)

    def __str__(self):
        return f"{self.number}.{self.text}"
