from django.urls import path

from . import views

app_name = "CogNeural"

urlpatterns = [
    path("", views.index, name="index"),
]
