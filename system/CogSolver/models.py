import datetime
import logging

from django.core.exceptions import ValidationError
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

    def evaluate(self, application):
        """Применяет правило к заявке и возвращает True, если условие
        выполнено"""
        if not self.is_active:
            return False

        try:
            if self.condition_type == "date_compare":
                if self.days_threshold is None:
                    return False
                return (
                    application.subm_date
                    > application.e_start_time
                    + datetime.timedelta(days=self.days_threshold)
                )

            elif self.condition_type == "role_check":
                if self.role_id is None:
                    return False
                return application.roles.filter(id=self.role_id).exists()

            elif self.condition_type == "text_length":
                if self.min_text_length is None:
                    return False
                return len(application.e_description) > self.min_text_length

            elif self.condition_type == "combined":
                date_ok = (
                    self.days_threshold is not None
                    and application.subm_date
                    > application.e_start_time
                    + datetime.timedelta(days=self.days_threshold)
                )
                role_ok = (
                    self.role_id is not None
                    and application.roles.filter(id=self.role_id).exists()
                )
                text_ok = (
                    self.min_text_length is not None
                    and len(application.e_description) > self.min_text_length
                )
                return date_ok and role_ok and text_ok

        except (TypeError, ValueError):
            return False

        return False

    def clean(self):
        if (
            self.condition_type == "date_compare"
            and self.days_threshold is None
        ):
            raise ValidationError(
                "Для сравнения дат необходимо указать порог дней"
            )
        if self.condition_type == "role_check" and self.role_id is None:
            raise ValidationError(
                "Для проверки роли необходимо указать ID роли"
            )
        if (
            self.condition_type == "text_length"
            and self.min_text_length is None
        ):
            raise ValidationError(
                "Для проверки длины текста необходимо указать минимальную"
                " длину"
            )
