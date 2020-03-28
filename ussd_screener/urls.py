from django.urls import path

from .views import ussd_callback


urlpatterns = [
    path("ussd-screener-callback/", ussd_callback, name="ussd-screener-callback")
]
