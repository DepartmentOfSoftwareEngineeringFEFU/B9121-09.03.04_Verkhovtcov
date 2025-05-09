from django.urls import path

from . import views

urlpatterns = [
    path("", views.rules_report, name="rules_report"),
]
