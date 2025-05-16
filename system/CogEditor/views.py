from CogEditor.models import Application, Employee
from django.shortcuts import get_object_or_404
from django.views import generic


class IndexView(generic.ListView):
    template_name = "CogEditor/index.html"
    context_object_name = "latest_application_list"

    def get_queryset(self):
        """Возвращает 5 последних заявок"""
        return Application.objects.order_by("-subm_date")[:5]


class DetailView(generic.DetailView):
    model = Application
    template_name = "CogEditor/detail.html"


class ArchiveByYearMonthView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"

    def get_queryset(self):
        year = self.kwargs["year"]
        month = self.kwargs["month"]

        # Получаем заявки, у которых есть хотя бы одно событие
        # в указанном году и месяце
        return (
            Application.objects.filter(
                event_schedule__start__year=year,
                event_schedule__start__month=month,
            )
            .distinct()
            .order_by("subm_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["year"] = self.kwargs["year"]
        context["month"] = self.kwargs["month"]
        return context


class ArchiveByYearView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"

    def get_queryset(self):
        year = self.kwargs["year"]
        return (
            Application.objects.filter(event_schedule__start__year=year)
            .distinct()
            .order_by("subm_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["year"] = self.kwargs["year"]
        return context


class FullArchiveView(generic.ListView):
    template_name = "CogEditor/archive_list.html"
    context_object_name = "application_list"
    queryset = Application.objects.all().order_by("-subm_date")
    paginate_by = 20


class OrganizerEventsView(generic.ListView):
    template_name = "CogEditor/organizer_events.html"
    context_object_name = "application_list"

    def get_queryset(self):
        organizer = get_object_or_404(Employee, pk=self.kwargs["id"])
        return Application.objects.filter(organizer=organizer).order_by(
            "-subm_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organizer"] = get_object_or_404(
            Employee, pk=self.kwargs["id"]
        )
        return context
