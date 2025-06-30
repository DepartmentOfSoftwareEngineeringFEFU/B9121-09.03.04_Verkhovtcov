#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Инициализация Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

    import django

    django.setup()

    # Теперь можно импортировать модели
    from Telegram.models import TelegramChat
    from Telegram.telegram_bot import main

    # Запуск бота
    main()
