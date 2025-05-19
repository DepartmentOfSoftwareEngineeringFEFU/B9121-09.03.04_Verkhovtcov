from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("CogEditor.urls")),
    path("neural/", include("CogNeural.urls")),
    path("solver/", include("CogSolver.urls")),
    path("admin/", admin.site.urls),
]
