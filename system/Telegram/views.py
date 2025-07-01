import logging

from colorama import Back, Fore, Style, init
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from Telegram.telegram_bot import handle_existing_user
from .models import TelegramChat
from Telegram.telegram_bot import send_verification_code


init()  # Инициализация colorama

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    f"{Fore.GREEN}%(asctime)s - {Fore.YELLOW}%(name)s - {Fore.BLUE}%(levelname)s -{Style.RESET_ALL} %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@require_POST
def check_phone(request):
    user_phone = request.POST.get('phone', '')

    # Нормализация номера (удаляем все нецифровые символы)
    user_phone = ''.join(c for c in user_phone if c.isdigit())

    if not user_phone.startswith('9') or len(user_phone) != 10:
        return JsonResponse(
            {
                'status': 'invalid',
                'message': 'Номер должен начинаться с 9 и содержать 10 цифр',
            },
            status=400,
        )

    try:
        chat = TelegramChat.objects.get(phone=f'+7{user_phone}')

        if chat is None:
            raise TelegramChat.DoesNotExist

        # Устанавливаем сессию и её время жизни (5 минута)
        request.session['verification_phone'] = chat.phone
        request.session.set_expiry(300)  # 60 секунд = 1 минута

        # Хоть Чусов один из лучших преподов ДВФУ, этот код был сгенерирован нейросетью)))
        # Создаем mock-объекты Update и Context для вызова handle_existing_user

        send_verification_code.delay(int(chat.telegram_chat))

        return JsonResponse(
            {'status': 'active', 'chat_id': chat.telegram_chat}
        )

    except TelegramChat.DoesNotExist:
        return JsonResponse(
            {
                'status': 'not_found',
                'message': 'Телефон не найден. Зарегистрируйтесь в боте',
                'bot_url': 'https://t.me/AutoBookingPlacesBot',
            },
            status=404,
        )

    except Exception as ex:
        logger.error(f"Error in check_phone: {ex}")
        return JsonResponse(
            {
                'status': 'error',
                'message': f'Произошла внутренняя ошибка сервера {ex}',
            },
            status=500,
        )


@require_POST
def check_code(request):
    phone = request.session.get('verification_phone')
    code = request.POST.get('code', '')

    if not phone or not code:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Необходимо сначала ввести телефон',
            },
            status=400,
        )
    code = int(code)
    cached_code = cache.get(f'verify_{phone}')

    logger.info(f"'verify_{phone}': {type(phone)}" f"'{code}': {type(code)}")

    if not cached_code:
        return JsonResponse(
            {'status': 'error', 'message': 'Код устарел. Запросите новый'},
            status=400,
        )

        # Код верный
    if code == cached_code:

        # Устанавливаем сессию и её время жизни (7 минута)
        request.session['phone_verified'] = True
        request.session.set_expiry(60 * 7)  # 60 секунд = 1 минута

        cache.delete(f'verify_{phone}')  # Удаляем использованный код

        return JsonResponse(
            {
                'status': 'success',
                'message': 'Телефон успешно подтвержден',
                'redirect_url': '/',  # Или любой другой URL
            }
        )
    else:
        return JsonResponse(
            {'status': 'error', 'message': 'Неверный код подтверждения'},
            status=400,
        )
