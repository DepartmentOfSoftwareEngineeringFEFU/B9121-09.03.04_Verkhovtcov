import datetime

from django.db import models
from django.utils import timezone


class StructuralUnit(models.Model):
    """Структурное подразделение"""
    unit = models.CharField(
        max_length=128,
        verbose_name="Наименование структурного подразделения"
    )

    def __str__(self):
        return f'<StructuralUnit: {self.unit}>'

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий наименование структурного подразделения на Рус. яз."""

        verbose_name = 'структурное подразделение'
        verbose_name_plural = 'Структурные подразделения'
        ordering = ['unit']


class EmployeePosition(models.Model):
    """Должность сотрудника"""
    position = models.CharField(
        max_length=32,
        verbose_name="Наименование должности",
    )

    def __str__(self):
        return f'<EmployeePosition: {self.position}>'

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий наименование должностей сотрудников на Рус. яз."""

        verbose_name = 'должность'
        verbose_name_plural = 'Должности'
        ordering = ['position']


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
        return f'<Employee: {self.full_name}>'

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий сотрудников ДВФУ на Рус. яз."""

        verbose_name = 'сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['full_name']


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
        return f'<ParticipatoryRole: {self.role}>'

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий роли участников мероприятий на Рус. яз."""

        verbose_name = 'роль участника'
        verbose_name_plural = 'Роли участников'
        ordering = ['role']


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

    def __str__(self):
        return f'<AgreedStatus: {self.status}>'

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий статусы согласования заявок на Рус. яз."""

        verbose_name = 'статус согласования'
        verbose_name_plural = 'Статусы согласования'
        ordering = ['status']


class Application(models.Model):
    """Заявка на мероприятие"""

    subm_date = models.DateTimeField(
        blank=False,
        verbose_name="Время регистрации заявки",
        auto_now_add=True,
    )

    e_title = models.TextField(
        max_length=256,
        verbose_name="Наименование мероприятия",
        default="Некоторое наименование мероприятия",
    )
    e_description = models.TextField(
        max_length=512,
        verbose_name="Описание мероприятия",
        default="Некоторое описание мероприятия",
    )

    e_start_time = models.DateTimeField(
        verbose_name="Дата и время начала мероприятия",
    )

    e_end_time = models.DateTimeField(
        verbose_name="Дата и время окончания мероприятия",
    )

    number_of_participants = models.IntegerField(
        verbose_name="Количество участников мероприятия",
        default=25,
    )

    role = models.ForeignKey(
        ParticipatoryRole,
        on_delete=models.CASCADE,
        verbose_name="Роль участника мероприятия",
        default=0,

    )

    organizer = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Организатор мероприятия",
    )

    status = models.ForeignKey(
        AgreedStatus,
        on_delete=models.CASCADE,
        verbose_name="Статус согласования мероприятия",

    )

    def __str__(self):
        return f'<Application: {self.e_title}>'

    def will_soon(self):
        return self.subm_date >= timezone.now() + datetime.timedelta(days=3)

    class Meta:
        """Зарещенный на територии РФ класс, \
        описывающий заявки на мероприятия на Рус. яз."""

        verbose_name = 'заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['subm_date']
