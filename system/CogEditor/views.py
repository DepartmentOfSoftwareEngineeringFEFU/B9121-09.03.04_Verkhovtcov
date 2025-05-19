from CogEditor.models import Application, Employee, StructuralUnit
from django.shortcuts import get_object_or_404
from django.views import generic


class IndexView(generic.ListView):
    template_name = "CogEditor/index.html"
    context_object_name = "latest_application_list"
    paginate_by = 10

    def get_queryset(self):
        """Возвращает 5 последних заявок"""
        return Application.objects.order_by("-subm_date")[:5]


class DetailView(generic.DetailView):
    model = Application
    template_name = "CogEditor/detail.html"


class ArchiveByYearView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"
    paginate_by = 10

    def get_queryset(self):
        year = self.kwargs["year"]
        return (
            Application.objects.filter(event_schedule__start__year=year)
            .distinct()
            .order_by("-subm_date")
            .prefetch_related("event_schedule")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["year"] = self.kwargs["year"]
        context["archive_type"] = "year"
        return context


class ArchiveByYearMonthView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"
    paginate_by = 10

    def get_queryset(self):
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        return (
            Application.objects.filter(
                event_schedule__start__year=year,
                event_schedule__start__month=month,
            )
            .distinct()
            .order_by("-subm_date")
            .prefetch_related("event_schedule")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["year"] = self.kwargs["year"]
        context["month"] = self.kwargs["month"]
        context["archive_type"] = "month"
        return context


class OrganizerEventsView(generic.ListView):
    template_name = "CogEditor/organizer_events.html"
    context_object_name = "application_list"
    paginate_by = 10

    def get_queryset(self):
        organizer_id = self.kwargs["id"]
        return (
            Application.objects.filter(organizer_id=organizer_id)
            .order_by("-subm_date")
            .prefetch_related("event_schedule")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organizer"] = StructuralUnit.objects.get(pk=self.kwargs["id"])
        return context


class FullArchiveView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"
    queryset = Application.objects.all().order_by("-subm_date")
    paginate_by = 10
