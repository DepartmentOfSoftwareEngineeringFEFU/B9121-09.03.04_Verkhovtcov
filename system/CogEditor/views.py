from CogEditor.forms import ApplicationForm
from CogEditor.models import Application, StructuralUnit
from django.views import generic
from django.views.generic.edit import CreateView


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


class ApplicationCreateView(CreateView):

    model = Application
    form_class = ApplicationForm
    template_name = 'CogEditor/application_classifier.html'
    success_url = '/solver/'

    def get_form_kwargs(self):
        """Добавляем default значения в форму"""
        kwargs = super().get_form_kwargs()

        from CogEditor.models import AgreedStatus, Sources

        # Получаем или создаем default значения
        default_status = AgreedStatus.objects.filter(n_stage=4).first()
        if default_status is None:
            default_status = AgreedStatus.objects.create(
                status="Предварительное согласование", n_stage=4
            )

        default_source = Sources.objects.filter(name="Сайт").first()
        if default_source is None:
            default_source = Sources.objects.create(name="Сайт")

        kwargs.update(
            {
                'default_status': default_status,
                'default_source': default_source,
            }
        )
        return kwargs
