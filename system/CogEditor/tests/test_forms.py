from CogEditor.models import (
    AgreedStatus,
    Employee,
    EmployeePosition,
    EventFormat,
    Sources,
    StructuralUnit,
)
from django.test import TestCase


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
