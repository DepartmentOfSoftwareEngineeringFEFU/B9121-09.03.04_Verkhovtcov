import datetime

from django.db import models
from django.utils import timezone


class StructuralUnit(models.Model):
    """Структурное подразделение"""

    unit = models.CharField(
        max_length=128, verbose_name="Наименование структурного подразделения"
    )

    def __str__(self):
        return self.unit

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий наименование структурного подразделения на Рус. яз."""

        verbose_name = "структурное подразделение"
        verbose_name_plural = "Структурные подразделения"
        ordering = ["unit"]


class EmployeePosition(models.Model):
    """Должность сотрудника"""

    position = models.CharField(
        max_length=32,
        verbose_name="Наименование должности",
    )

    def __str__(self):
        return self.position

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий наименование должностей сотрудников на Рус. яз."""

        verbose_name = "должность"
        verbose_name_plural = "Должности"
        ordering = ["position"]


class Employee(models.Model):
    """Сотрудник ДВФУ"""

    full_name = models.CharField(
        max_length=64,
        verbose_name="ФИО сотрудника",
    )

    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.CASCADE,
        verbose_name="Должность сотрудника",
    )

    structural_unit = models.ForeignKey(
        StructuralUnit,
        on_delete=models.CASCADE,
        verbose_name="Структурное подразделение",
    )

    def __str__(self):
        return self.full_name

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий сотрудников ДВФУ на Рус. яз."""

        verbose_name = "сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["full_name"]


class ParticipatoryRole(models.Model):
    """Роль участников мероприятия"""

    role = models.CharField(
        max_length=64,
        verbose_name="Роль участника мероприятия",
        default="Некоторая роль",
    )
    description = models.TextField(
        max_length=512,
        verbose_name="Описание роли участника",
    )

    def __str__(self):
        return self.role

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий роли участников мероприятий на Рус. яз."""

        verbose_name = "роль участника"
        verbose_name_plural = "Роли участников"
        ordering = ["role"]


class AgreedStatus(models.Model):
    """Статусы согласования мероприятий"""

    status = models.CharField(
        max_length=32,
        verbose_name="Наименование статуса согласования",
    )
    description = models.TextField(
        max_length=512,
        verbose_name="Описание статуса согласования",
    )
    n_stage = models.IntegerField(
        default=7,
        verbose_name="Номер этапа согласования",
    )

    def __str__(self):
        return f"{self.n_stage}. {self.status}"

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий статусы согласования заявок на Рус. яз."""

        verbose_name = "статус согласования"
        verbose_name_plural = "Статусы согласования"
        ordering = [
            "n_stage",
        ]


class Order(models.Model):
    """Приказ об организации мероприятия"""

    name = models.CharField(
        max_length=128,
        verbose_name="Наименование приказа",
    )
    date = models.DateField(
        verbose_name="Дата приказа",
    )
    number = models.CharField(
        max_length=10,
        verbose_name="Номер приказа",
    )

    def __str__(self):
        return f"Приказ от {self.date} № {self.number} «{self.name}»"

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий статусы согласования заявок на Рус. яз."""

        verbose_name = "приказ"
        verbose_name_plural = "Приказы"
        ordering = [
            "date",
        ]


class EventFormat(models.Model):
    """Перечень форматов мероприятия"""

    name = models.CharField(
        max_length=64,
        verbose_name="Наименование",
    )
    description = models.TextField(
        max_length=512,
        verbose_name="Описание",
    )

    def __str__(self):
        return self.name

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий статусы согласования заявок на Рус. яз."""

        verbose_name = "формат"
        verbose_name_plural = "Форматы"
        ordering = [
            "name",
        ]


class Schedule(models.Model):
    """Расписание мероприятия"""

    start = models.DateTimeField(
        verbose_name="Начало",
        blank=True,
        null=True,
    )

    end = models.DateTimeField(
        verbose_name="Окончание",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.start} – {self.end}"

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий статусы согласования заявок на Рус. яз."""

        verbose_name = "расписание"
        verbose_name_plural = "Расписания"
        ordering = [
            "start",
        ]


class Application(models.Model):
    """Заявка на мероприятие"""

    subm_date = models.DateTimeField(
        blank=False,
        verbose_name="Время регистрации заявки",
    )

    e_title = models.TextField(
        max_length=256,
        verbose_name="Наименование мероприятия",
    )
    e_description = models.TextField(
        max_length=512,
        verbose_name="Описание мероприятия",
        null=True,
    )

    e_format = models.ForeignKey(
        EventFormat,
        on_delete=models.CASCADE,
        verbose_name="Формат мероприятия",
        null=True,
    )

    installation_deinstallation = models.ForeignKey(
        Schedule,
        verbose_name="Время монтажа/демонтажа",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        # Уникальное имя для обратной связи
        related_name="installation_applications",
    )

    event_schedule = models.ManyToManyField(
        Schedule,
        verbose_name="Время бронирования",
        blank=True,
        # Уникальное имя для обратной связи
        related_name="event_applications",
    )

    number_of_participants = models.IntegerField(
        verbose_name="Количество участников мероприятия",
        default=25,
    )

    roles = models.ManyToManyField(
        ParticipatoryRole,
        verbose_name="Роль участника мероприятия",
    )

    organizer = models.ForeignKey(
        StructuralUnit, on_delete=models.CASCADE, verbose_name="Организатор"
    )

    organizer_employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Ответственный за организацию",
        null=True,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Приказ на мероприятие",
        null=True,
    )

    requires_technical_support = models.BooleanField(
        default=False, verbose_name="Требуется техническое сопровождение"
    )

    audio_training_date = models.DateField(
        null=True, blank=True, verbose_name="Дата обучения работе со звуком"
    )

    technical_requirements = models.TextField(
        blank=True, null=True, verbose_name="Технические требования"
    )

    status = models.ForeignKey(
        AgreedStatus,
        on_delete=models.CASCADE,
        verbose_name="Статус согласования мероприятия",
    )

    def __str__(self):
        return f"{self.subm_date.strftime('%Y.%m.%d')} - {self.e_title}"

    def will_soon(self):
        return self.subm_date >= timezone.now() + datetime.timedelta(days=3)

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий заявки на мероприятия на Рус. яз."""

        verbose_name = "заявка"
        verbose_name_plural = "Заявки"
        ordering = ["subm_date"]
