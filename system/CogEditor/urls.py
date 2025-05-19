from django.urls import path

from . import views

app_name = "CogEditor"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path(
        "application/archive/<int:year>/<int:month>/",
        views.ArchiveByYearMonthView.as_view(),
        name="archive_by_year_month",
    ),
    path(
        "application/archive/<int:year>/",
        views.ArchiveByYearView.as_view(),
        name="archive_by_year",
    ),
    path(
        "application/archive/", views.FullArchiveView.as_view(), name="archive"
    ),
    path(
        "organizer/<int:id>/events/",
        views.OrganizerEventsView.as_view(),
        name="organizer_events",
    ),
    path(
        "application_classifier/",
        views.ApplicationCreateView.as_view(),
        name="application_classifier",
    ),
]
