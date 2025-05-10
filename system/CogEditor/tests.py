import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (AgreedStatus, Application, Employee, EmployeePosition,
                     ParticipatoryRole, StructuralUnit)


class ApplicationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

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

        self.application = Application.objects.create(
            e_title="Test Event",
            e_description="Test Description",
            e_start_time=timezone.now() + datetime.timedelta(days=1),
            e_end_time=timezone.now() + datetime.timedelta(days=2),
            number_of_participants=10,
            organizer=self.employee,
            status=self.status,
            subm_date=timezone.now(),  # Добавлено
        )
        self.application.roles.add(self.role)

    # 1. Тест главной страницы
    def test_home_page(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    # 2. Тест архива за месяц
    def test_archive_month(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        response = self.client.get(
            reverse("archive_by_year_month", args=[year, month])
        )
        self.assertEqual(response.status_code, 200)

    # 3. Тест архива за год
    def test_archive_year(self):
        year = datetime.datetime.now().year
        response = self.client.get(reverse("archive_by_year", args=[year]))
        self.assertEqual(response.status_code, 200)

    # 4. Тест полного архива
    def test_archive_all(self):
        response = self.client.get(reverse("archive"))
        self.assertEqual(response.status_code, 200)

    # 5. Тест получения заявки по ID
    def test_application_detail(self):
        response = self.client.get(
            reverse("application_detail", args=[self.application.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.application.e_title)

    # 6. Тест мероприятий организатора
    def test_organizer_events(self):
        response = self.client.get(
            reverse('organizer_events', args=[self.employee.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.application.e_title)
