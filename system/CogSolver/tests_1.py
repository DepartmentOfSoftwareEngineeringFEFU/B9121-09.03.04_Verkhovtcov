import datetime

from CogEditor.models import (
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
from CogSolver.models import Rule, RuleEngine
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse


class RuleModelTest(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        self.status1 = AgreedStatus.objects.create(
            status="Статус 1", n_stage=1
        )
        self.status2 = AgreedStatus.objects.create(
            status="Статус 2", n_stage=2
        )
        self.role1 = ParticipatoryRole.objects.create(role="Роль 1")
        self.role2 = ParticipatoryRole.objects.create(role="Роль 2")

        # Создаем тестовую заявку
        self.unit = StructuralUnit.objects.create(
            unit="Тестовое подразделение"
        )
        self.position = EmployeePosition.objects.create(
            position="Тестовая должность"
        )
        self.employee = Employee.objects.create(
            full_name="Тестовый сотрудник",
            position=self.position,
            structural_unit=self.unit,
        )
        self.source = Sources.objects.create(name="Тестовый источник")
        self.event_format = EventFormat.objects.create(name="Тестовый формат")

        # В setUp():
        self.schedule = Schedule.objects.create(
            start=datetime.datetime.now()
            + datetime.timedelta(days=1),  # Мероприятие через 1 день
            end=datetime.datetime.now() + datetime.timedelta(days=1, hours=2),
        )

        self.application = Application.objects.create(
            subm_date=datetime.datetime.now(),
            application_source=self.source,
            e_title="Тестовое мероприятие",
            e_description="Тестовое описание",
            e_format=self.event_format,
            organizer=self.unit,
            organizer_employee=self.employee,
            status=self.status1,
        )
        self.application.roles.add(self.role1)
        self.application.event_schedule.add(self.schedule)

    def test_date_compare_rule(self):
        rule = Rule.objects.create(
            name="Правило сравнения дат",
            condition_type="date_compare",
            days_threshold=2,
            new_status=self.status2,
            is_active=True,
        )
        self.assertTrue(rule.evaluate(self.application))

        # Тест с неактивным правилом
        rule.is_active = False
        self.assertFalse(rule.evaluate(self.application))

    def test_role_check_rule(self):
        rule = Rule.objects.create(
            name="Правило проверки роли",
            condition_type="role_check",
            new_status=self.status2,
            is_active=True,
        )
        rule.role_id.add(self.role1)
        self.assertTrue(rule.evaluate(self.application))

        rule.role_id.clear()
        rule.role_id.add(self.role2)
        self.assertFalse(rule.evaluate(self.application))

    def test_text_length_rule(self):
        rule = Rule.objects.create(
            name="Правило длины текста",
            condition_type="text_length",
            min_text_length=50,
            new_status=self.status2,
            is_active=True,
        )
        self.assertTrue(
            rule.evaluate(self.application)
        )  # Текст короче 50 символов

        self.application.e_description = "Очень длинное описание " * 10
        self.application.save()
        self.assertFalse(rule.evaluate(self.application))

    def test_combined_rule(self):
        rule = Rule.objects.create(
            name="Комбинированное правило",
            condition_type="combined",
            days_threshold=2,
            min_text_length=50,
            new_status=self.status2,
            is_active=True,
        )
        rule.role_id.add(self.role1)

        # Все условия выполняются
        self.assertTrue(rule.evaluate(self.application))

        # Нарушаем одно из условий
        rule.role_id.clear()
        rule.role_id.add(self.role2)
        self.assertFalse(rule.evaluate(self.application))

    def test_rule_clean_validation(self):
        # Проверка валидации для разных типов правил
        with self.assertRaises(ValidationError):
            rule = Rule(
                name="Некорректное правило дат",
                condition_type="date_compare",
                days_threshold=None,
                new_status=self.status1,
            )
            rule.full_clean()


class RuleEngineTest(TestCase):
    def setUp(self):
        # Используем данные из setUp предыдущего теста
        self.status1 = AgreedStatus.objects.create(
            status="Статус 1", n_stage=1
        )
        self.status2 = AgreedStatus.objects.create(
            status="Статус 2", n_stage=2
        )
        self.role1 = ParticipatoryRole.objects.create(role="Роль 1")

        self.unit = StructuralUnit.objects.create(
            unit="Тестовое подразделение"
        )
        self.position = EmployeePosition.objects.create(
            position="Тестовая должность"
        )
        self.employee = Employee.objects.create(
            full_name="Тестовый сотрудник",
            position=self.position,
            structural_unit=self.unit,
        )
        self.source = Sources.objects.create(name="Тестовый источник")
        self.event_format = EventFormat.objects.create(name="Тестовый формат")

        self.schedule = Schedule.objects.create(
            start=datetime.datetime.now() + datetime.timedelta(days=1),
            end=datetime.datetime.now() + datetime.timedelta(days=1, hours=2),
        )

        self.application = Application.objects.create(
            subm_date=datetime.datetime.now(),
            application_source=self.source,
            e_title="Тестовое мероприятие",
            e_description="Тестовое описание",
            e_format=self.event_format,
            organizer=self.unit,
            organizer_employee=self.employee,
            status=self.status1,
        )
        self.application.roles.add(self.role1)
        self.application.event_schedule.add(self.schedule)

    def test_apply_rules_to_application(self):
        # Создаем правило, которое должно сработать
        Rule.objects.create(
            name="Тестовое правило",
            condition_type="date_compare",
            days_threshold=2,
            new_status=self.status2,
            is_active=True,
            priority=1,
        )

        # Меняем дату мероприятия, чтобы правило сработало
        self.schedule.start = datetime.datetime.now() + datetime.timedelta(
            days=3
        )
        self.schedule.save()

        new_status = RuleEngine.apply_rules_to_application(self.application)
        self.assertEqual(new_status, self.status2)

        # Проверяем, что правило с более высоким приоритетом перекрывает другие
        Rule.objects.create(
            name="Правило с более высоким приоритетом",
            condition_type="date_compare",
            days_threshold=2,
            new_status=self.status1,  # Возвращаем исходный статус
            is_active=True,
            priority=2,  # Более высокий приоритет
        )

        new_status = RuleEngine.apply_rules_to_application(self.application)
        self.assertEqual(new_status, self.status1)

    def test_batch_apply_rules(self):
        Rule.objects.create(
            name="Тестовое правило",
            condition_type="date_compare",
            days_threshold=2,
            new_status=self.status2,
            is_active=True,
        )

        results = RuleEngine.batch_apply_rules()
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['status_changed'])
        self.assertEqual(results[0]['new_status'], self.status2)


class CogSolverViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.status = AgreedStatus.objects.create(
            status="Тестовый статус", n_stage=1
        )

    def test_rules_report_view(self):
        response = self.client.get(reverse("CogSolver:rules_report"))
        self.assertEqual(response.status_code, 200)
