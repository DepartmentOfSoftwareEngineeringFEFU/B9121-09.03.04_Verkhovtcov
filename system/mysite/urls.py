from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("editor/", include("CogEditor.urls")),
    path("solver/", include("CogSolver.urls")),
    path("neural/", include("CogNeural.urls")),

    path("admin/", admin.site.urls),
]
