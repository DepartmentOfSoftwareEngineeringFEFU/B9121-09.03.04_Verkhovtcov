import datetime
import logging

from CogEditor.models import AgreedStatus, Application, ParticipatoryRole
from django.core.exceptions import ValidationError
from django.db import models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")
logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


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
    role_id = models.ManyToManyField(
        ParticipatoryRole,
        null=True,
        blank=True,
        verbose_name="Роли",
    )

    min_text_length = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Минимальная длина текста",
    )

    # Результирующий статус
    new_status = models.ForeignKey(
        AgreedStatus,
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
                logger.debug(f"{self.days_threshold=}")
                if self.days_threshold is None:
                    return False
                return (
                    application.subm_date
                    + datetime.timedelta(days=self.days_threshold)
                    >= application.e_start_time
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
                    + datetime.timedelta(days=self.days_threshold)
                    >= application.e_start_time

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
            logging.error("TypeError / ValueError", exc_info=True)
            logging.error("TypeError / ValueError", exc_info=True)
            return False

        return False

    def clean(self):
        if (
            self.condition_type == "date_compare"
            and self.days_threshold is None
        ):
            logging.error("ValidationError", exc_info=True)
            logging.error("ValidationError", exc_info=True)
            raise ValidationError(
                "Для сравнения дат необходимо указать порог дней"
            )

        if self.condition_type == "role_check" and self.role_id is None:
            logging.error("ValidationError", exc_info=True)
            logging.error("ValidationError", exc_info=True)
            raise ValidationError(
                "Для проверки роли необходимо указать ID роли"
            )
        if (
            self.condition_type == "text_length"
            and self.min_text_length is None
        ):
            logging.error("ValidationError", exc_info=True)
            logging.error("ValidationError", exc_info=True)
            raise ValidationError(
                "Для проверки длины текста необходимо указать минимальную"
                " длину"
            )

    class Meta:
        verbose_name = "правило"
        verbose_name_plural = "правила"
        ordering = ["-priority", "name"]


class RuleEngine:
    @staticmethod
    def apply_rules_to_application(
        application,
    ):
        """Применяет все активные правила к заявке"""
        rules = Rule.objects.filter(is_active=True).order_by("-priority")

        for rule in rules:
            try:
                if rule.evaluate(application):
                    return rule.new_status
            except Exception as e:
                # FIXME - не работает логирование
                logger.error(
                    f"Error evaluating rule {rule.id} for application "
                    f"{application.id}: {str(e)}"
                )
                continue

        # Возвращаем исходный статус при ошибках или если правила не сработали
        return application.status

    @staticmethod
    def batch_apply_rules():
        """Применяет правила ко всем заявкам и возвращает результаты"""
        results = []
        applications = Application.objects.all()

        for app in applications:
            new_status = RuleEngine.apply_rules_to_application(app)
            results.append(
                {
                    "application": app,
                    "current_status": app.status,
                    "new_status": new_status,
                    "status_changed": new_status != app.status,
                }
            )

        return results
