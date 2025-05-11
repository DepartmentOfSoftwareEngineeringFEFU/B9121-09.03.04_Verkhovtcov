from CogEditor.models import Application, Employee
from django.http import HttpResponse
from django.utils import timezone


def index(request):
    latest_application_list = Application.objects.filter(
        event_schedule__start__gt=timezone.now()
    ).distinct()

    output = ", ".join([q.e_title for q in latest_application_list])
    return HttpResponse(output)


def archive_by_year_month(request, year, month):

    # start.year <= year <= end.year
    archive_application_list = Application.objects.filter(
        e_start_time__year__lte=year,
        e_end_time__year__gte=year,
        e_start_time__month__lte=month,
        e_end_time__month__gte=month,
    )

    output = ", ".join([q.e_title for q in archive_application_list])
    return HttpResponse(output)


def archive_by_year(request, year):

    # start.year <= year <= end.year
    archive_application_list = Application.objects.filter(
        e_start_time__year__lte=year,
        e_end_time__year__gte=year,
    )

    output = ", ".join([q.e_title for q in archive_application_list])
    return HttpResponse(output)


def full_archive(request):
    archive_application_list = Application.objects.all()
    output = ", ".join([q.e_title for q in archive_application_list])
    return HttpResponse(output)


def application_detail(request, id):
    application = Application.objects.get(pk=id)
    output = application.e_title
    return HttpResponse(output)


def organizer_events(request, id):
    employee = Employee.objects.get(pk=id)
    application_list = Application.objects.filter(organizer=employee)
    output = ", ".join([q.e_title for q in application_list])
    return HttpResponse(output)
