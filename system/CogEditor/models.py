import datetime

from django.db import models
from django.utils import timezone


class StructuralUnit(models.Model):
    """Структурное подразделение"""
    unit = models.CharField(max_length=128)

    def __str__(self):
        return f'<StructuralUnit: {self.unit}>'


class EmployeePosition(models.Model):
    """Должность сотрудника"""
    position = models.CharField(max_length=32)

    def __str__(self):
        return f'<EmployeePosition: {self.position}>'


class Employee(models.Model):
    """Сотрудник ДВФУ"""
    full_name = models.CharField(max_length=64)

    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.CASCADE,
    )

    structural_unit = models.ForeignKey(
        StructuralUnit,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'<Employee: {self.full_name}>'


class ParticipatoryRole(models.Model):
    """Роль участников мероприятия"""
    role = models.CharField(max_length=64)
    description = models.CharField(max_length=512)

    def __str__(self):
        return f'<ParticipatoryRole: {self.role}>'


class Contingent(models.Model):
    """Контингент мероприятия"""
    number_of_participants = models.IntegerField()
    role = models.ForeignKey(
        ParticipatoryRole,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'<Contingent: {self.number_of_participants}, {self.role}>'


class AgreedStatus(models.Model):
    """Статусы согласования мероприятий"""
    status = models.CharField(max_length=32)
    description = models.CharField(max_length=512)

    def __str__(self):
        return f'<AgreedStatus: {self.status}>'


class Application(models.Model):
    """Заявка на мероприятие"""

    subm_date = models.DateTimeField("submission date")

    e_title = models.CharField(max_length=256)
    e_description = models.CharField(max_length=512)

    e_start_time = models.DateTimeField("Event start time")
    e_end_time = models.DateTimeField("Event end time")

    organizer = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
    )

    status = models.ForeignKey(
        AgreedStatus,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'<Application: {self.e_title}>'

    def will_soon(self):
        return self.subm_date >= timezone.now() + datetime.timedelta(days=3)
