import logging

from django.db import models

logger = logging.getLogger(__name__)


class Rule(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Наименование правила",
    )
    description = models.TextField(verbose_name="Описание правила")
    priority = models.IntegerField(
        default=0,
        verbose_name="Приоритет выполнения",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
    )

    # Параметры условия
    condition_type = models.CharField(
        max_length=20,
        choices=[
            (
                "date_compare",
                "Сравнение дат",
            ),
            (
                "role_check",
                "Проверка роли",
            ),
            (
                "text_length",
                "Длина текста",
            ),
            (
                "combined",
                "Комбинированное условие",
            ),
        ],
        verbose_name="Тип условия",
    )

    # Параметры для разных типов условий
    days_threshold = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Порог дней",
    )
    role_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID роли",
    )
    min_text_length = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Минимальная длина текста",
    )

    # Результирующий статус
    new_status = models.ForeignKey(
        "CogEditor.AgreedStatus",
        on_delete=models.CASCADE,
        verbose_name="Новый статус",
    )
