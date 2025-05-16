from django.urls import path

from . import views

app_name = "CogSolver"

urlpatterns = [
    path("", views.rules_report, name="rules_report"),
]
