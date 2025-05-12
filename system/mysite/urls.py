from django.contrib import admin
from django.urls import include, path

urlpatterns = [

    path("neural/", include("CogNeural.urls")),
    path("editor/", include("CogEditor.urls")),
    path("solver/", include("CogSolver.urls")),
    path("", include("CogEditor.urls")),

    path("admin/", admin.site.urls),
]
