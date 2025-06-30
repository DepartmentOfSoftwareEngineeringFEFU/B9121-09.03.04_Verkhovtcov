from django.urls import path

from . import views

app_name = "Telegram"

urlpatterns = [
    path("check_phone/", views.check_phone, name="check_phone"),
    path("check_code/", views.check_code, name="check_code"),
]
