from django.db import models


class TelegramChat(models.Model):
    phone = models.CharField(
        verbose_name="Номер телефона",
        blank=None,
        null=None,
        unique=True,
    )

    telegram_chat = models.CharField(
        verbose_name="ID чата telegram",
        blank=None,
        null=None,
    )
