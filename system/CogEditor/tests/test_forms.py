import datetime

from CogEditor.forms import ApplicationForm
from CogEditor.models import (
    AgreedStatus,
    Employee,
    EmployeePosition,
    EventFormat,
    Sources,
    StructuralUnit,
)
from django.test import TestCase
from django.utils import timezone


class ApplicationFormTest(TestCase):
    def setUp(self):
        self.status = AgreedStatus.objects.create(status="Тест", n_stage=5)
        self.source = Sources.objects.create(name="Сайт")
        self.unit = StructuralUnit.objects.create(
            unit="Тестовое подразделение"
        )
        self.position = EmployeePosition.objects.create(position="Тест")
        self.employee = Employee.objects.create(
            full_name="Тест", position=self.position, structural_unit=self.unit
        )
        self.event_format = EventFormat.objects.create(name="Тест")

    def test_valid_form(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        form_data = {
            'e_title': 'Тестовое мероприятие',
            'e_description': 'Тестовое описание',
            'organizer_employee_name': 'Тестовый сотрудник',
            'event_date': tomorrow.date(),
            'event_time_start': datetime.time(10, 0),
            'event_time_end': datetime.time(12, 0),
            'organizer': self.unit.id,
            'e_format': self.event_format.id,
            'number_of_participants': 10,
        }
        form = ApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
