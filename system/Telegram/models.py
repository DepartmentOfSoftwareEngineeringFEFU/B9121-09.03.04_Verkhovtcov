from django.db import models


class TelegramChat(models.Model):
    phone = models.CharField(
        verbose_name="Номер телефона",
        blank=None,
        null=None,
    )

    telegram_chat_id = models.CharField(
        verbose_name="ID чата telegram",
        blank=None,
        null=None,
    )
