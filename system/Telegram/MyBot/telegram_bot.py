import logging
import random
from datetime import datetime

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import requests
from Telegram.models import TelegramChat

logger = logging.getLogger(__name__)


def is_chat_active(chat_id):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    params = {'chat_id': chat_id}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return True  # Чат активен
        return False  # Чат не найден или бот заблокирован
    except Exception as e:
        logger.error(f"Error checking chat status: {e}")
        return False


class TelegramAuthHandler:
    """Обработчик авторизации через Telegram"""

    @csrf_exempt
    def check_phone(self, request):
        if request.method == 'POST':
            phone = request.POST.get('phone', '')

            try:
                chat = TelegramChat.objects.get(phone_number=phone)

                if not self._is_chat_active(chat.telegram_id):
                    return JsonResponse(
                        {
                            'status': 'inactive',
                            'message': 'Чат с ботом неактивен. Пожалуйста,'
                            'запустите бот.',
                        }
                    )

                return JsonResponse({'status': 'active'})

            except TelegramChat.DoesNotExist:
                return JsonResponse(
                    {
                        'status': 'not_found',
                        'message': 'Телефон не найден. Пожалуйста,'
                        'зарегистрируйтесь в боте.',
                    }
                )

        return JsonResponse({'error': 'Invalid request'}, status=400)

    @csrf_exempt
    def send_code(self, request):
        if request.method == 'POST':
            phone = request.POST.get('phone', '')

            try:
                chat = TelegramChat.objects.get(phone_number=phone)
                code = str(random.randint(1000, 9999))

                self._send_telegram_message(
                    chat.telegram_id, f"Ваш код подтверждения: {code}"
                )

                request.session['verification_code'] = code
                request.session['verification_phone'] = phone
                request.session.save()

                return JsonResponse({'success': True})
            except TelegramChat.DoesNotExist:
                return JsonResponse({'error': 'Чат не найден'}, status=400)

        return JsonResponse({'error': 'Invalid request'}, status=400)

    def _is_chat_active(self, chat_id):
        """Проверяет, активен ли чат с пользователем"""
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getChat"
        try:
            response = requests.get(
                url, params={'chat_id': chat_id}, timeout=5
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Telegram API error: {e}")
            return False

    @csrf_exempt
    def verify_code(self, request):
        if request.method == 'POST':
            code = request.POST.get('code', '')
            saved_code = request.session.get('verification_code', '')
            phone = request.session.get('verification_phone', '')

            if code == saved_code:
                request.session['phone_verified'] = True
                request.session.save()

                self._notify_user(phone)
                return JsonResponse({'success': True})

            return JsonResponse({'error': 'Неверный код'}, status=400)

        return JsonResponse({'error': 'Invalid request'}, status=400)

    def _send_telegram_message(self, chat_id, text):
        """Отправка сообщения через Telegram API"""
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={'chat_id': chat_id, 'text': text})

    def _notify_user(self, phone):
        """Уведомление пользователя об успешной отправке заявки"""
        try:
            chat = TelegramChat.objects.get(phone_number=phone)
            now = datetime.now().strftime("%H:%M %d %B %Y")
            self._send_telegram_message(
                chat.telegram_id,
                f"Заявка на бронирование направлена на рассмотрение администратору.\n\n"
                f"№ заявки: {self._generate_application_number()}\n"
                f"Дата подачи: {now}",
            )
        except TelegramChat.DoesNotExist:
            pass

    def _generate_application_number(self):
        """Генерация номера заявки"""
        now = datetime.now()
        return (
            f"{now.year % 100}-{now.month}-{now.day}/{random.randint(1, 100)}"
        )


class TelegramBot:
    """Класс для работы с Telegram ботом"""

    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(
            CommandHandler("start", self._start_handler)
        )
        self.application.add_handler(
            MessageHandler(filters.CONTACT, self._contact_handler)
        )

    async def _start_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Добро пожаловать! Для работы с системой бронирования, пожалуйста, поделитесь своим номером телефона.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Отправить номер", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )

    async def _contact_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработчик получения контакта"""
        user = update.effective_user
        contact = update.effective_message.contact

        if contact and contact.phone_number:
            phone = contact.phone_number.lstrip('+')  # Удаляем + для хранения

            TelegramChat.objects.update_or_create(
                telegram_id=user.id, defaults={'phone_number': phone}
            )

            await update.message.reply_text(
                "Спасибо! Теперь вы можете подтверждать заявки на бронирование через этого бота."
            )
        else:
            await update.message.reply_text(
                "Не удалось получить номер телефона."
            )

    def run(self):
        """Запуск бота"""
        self.application.run_polling()


# Создание экземпляров классов для использования
telegram_auth = TelegramAuthHandler()
telegram_bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
