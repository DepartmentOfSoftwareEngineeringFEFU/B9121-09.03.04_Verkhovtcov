from django.urls import path

from . import views

app_name = "CogSolver"

urlpatterns = [
    path(
        "application_classifier/",
        views.ApplicationCreateView.as_view(),
        name="application_classifier",
    ),
    path("", views.rules_report, name="rules_report"),
]
