import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    AgreedStatus,
    Application,
    Employee,
    EmployeePosition,
    EventFormat,
    ParticipatoryRole,
    Schedule,
    Sources,
    StructuralUnit,
)


class ApplicationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Создание тестовых данных
        self.unit = StructuralUnit.objects.create(unit="Test Unit")
        self.position = EmployeePosition.objects.create(
            position="Test Position"
        )
        self.employee = Employee.objects.create(
            full_name="Test Employee",
            position=self.position,
            structural_unit=self.unit,
        )
        self.status = AgreedStatus.objects.create(
            status="Test Status", description="Test Description", n_stage=1
        )
        self.role = ParticipatoryRole.objects.create(
            role="Test Role", description="Test Role Description"
        )
        self.event_format = EventFormat.objects.create(
            name="Test Format", description="Test Format Description"
        )
        self.source = Sources.objects.create(name="Test Source")

        # Создание расписания для мероприятия
        self.schedule = Schedule.objects.create(
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=2),
            all_day=False,
        )

        # Создание тестовой заявки
        self.application = Application.objects.create(
            subm_date=timezone.now(),
            application_source=self.source,
            e_title="Test Event",
            e_description="Test Description",
            e_format=self.event_format,
            number_of_participants=10,
            organizer=self.unit,
            organizer_employee=self.employee,
            status=self.status,
            requires_technical_support=False,
        )
        self.application.roles.add(self.role)
        self.application.event_schedule.add(self.schedule)

    # 1. Тест главной страницы
    def test_home_page(self):
        response = self.client.get(reverse("CogEditor:index"))
        self.assertEqual(response.status_code, 200)

    # 2. Тест архива за месяц
    def test_archive_month(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        response = self.client.get(
            reverse("CogEditor:archive_by_year_month", args=[year, month])
        )
        self.assertEqual(response.status_code, 200)

    # 3. Тест архива за год
    def test_archive_year(self):
        year = datetime.datetime.now().year
        response = self.client.get(
            reverse("CogEditor:archive_by_year", args=[year])
        )
        self.assertEqual(response.status_code, 200)

    # 4. Тест полного архива
    def test_archive_all(self):
        response = self.client.get(reverse("CogEditor:archive"))
        self.assertEqual(response.status_code, 200)

    # 5. Тест получения заявки по ID
    def test_detail(self):
        response = self.client.get(
            reverse("CogEditor:detail", args=[self.application.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.application.e_title)

    # 6. Тест мероприятий организатора
    def test_organizer_events(self):
        response = self.client.get(
            reverse('CogEditor:organizer_events', args=[self.employee.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.application.e_title)
