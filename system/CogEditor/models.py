from django.db import models


class StructuralUnit(models.Model):
    """Структурное подразделение"""
    unit = models.CharField(max_length=128)


class EmployeePosition(models.Model):
    """Должность сотрудника"""
    position = models.CharField(max_length=32)


class Employee(models.Model):
    """Сотрудник ДВФУ"""
    full_name = models.CharField(max_length=64)

    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.SET_NULL,
    )

    structural_unit = models.ForeignKey(
        StructuralUnit,
        on_delete=models.SET_NULL,
    )


class ParticipatoryRole(models.Model):
    """Роль участников мероприятия"""
    role = models.CharField(max_length=64)
    description = models.CharField(max_length=512)


class Contingent(models.Model):
    """Контингент мероприятия"""
    number_of_participants = models.IntegerField()
    role = models.ForeignKey(
        ParticipatoryRole,
        on_delete=models.SET_NULL,
    )


class AgreedStatus(models.Model):
    """Статусы согласования мероприятий"""
    status = models.CharField(max_length=32)
    description = models.CharField(max_length=512)


class Application(models.Model):
    """Заявка на мероприятие"""
    subm_date = models.DateTimeField("submission date")
    e_start_time = models.DateTimeField("Event start time")
    e_end_time = models.DateTimeField("Event end time")

    organizer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
    )

    status = models.ForeignKey(
        AgreedStatus,
        on_delete=models.SET_NULL,
    )
