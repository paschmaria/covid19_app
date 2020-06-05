from django.urls import path

from .views.aft_views import ussd_callback as aft
from .views.htg_views import ussd_callback as htg

urlpatterns = [
    path(
        "ussd-screener-callback/",
        htg,
        name="ussd-screener-callback"
    ),
    path(
        "aft-ussd-callback/",
        aft,
        name="aft-ussd-callback"
    )
]
