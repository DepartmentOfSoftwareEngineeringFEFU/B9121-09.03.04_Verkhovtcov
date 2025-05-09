from django.urls import path

from . import views

urlpatterns = [
    path("",
         views.index,
         name="index"
         ),
    path("application/archive/<int:year>/<int:month>",
         views.archive_by_year_month,
         name="archive_by_year_month",
         ),
    path("application/archive/<int:year>/",
         views.archive_by_year,
         name="archive_by_year",
         ),
    path("application/archive/",
         views.full_archive,
         name="archive",
         ),
    path("application/<int:id>/",
         views.application_detail,
         name="application_detail",
         ),
    path("organizer/<int:id>/events/",
         views.organizer_events,
         name="organizer_events",
         ),
]
