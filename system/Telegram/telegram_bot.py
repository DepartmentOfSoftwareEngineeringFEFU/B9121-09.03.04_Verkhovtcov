import logging
from random import randint
from celery import shared_task
from celery.utils.log import get_task_logger
from telegram import Bot
from telegram.error import TelegramError


from asgiref.sync import sync_to_async
from colorama import Back, Fore, Style, init
from django.core.cache import cache
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from Telegram.models import TelegramChat

init()  # Инициализация colorama

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    f"{Fore.GREEN}%(asctime)s - {Fore.YELLOW}%(name)s - {Fore.BLUE}%(levelname)s -{Style.RESET_ALL} %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    try:
        # Используем sync_to_async для выполнения синхронного запроса к БД
        chat = await sync_to_async(TelegramChat.objects.get)(
            telegram_chat=str(user_id)
        )
        if chat is not None:
            await handle_existing_user(update, context)

    except TelegramChat.DoesNotExist:
        await request_phone_number(update)

    except Exception as ex:
        logger.error(
            f"Error when user_id:{user_id} start @AutoBookingPlacesBot\n"
            f"Error message: {str(ex)}"
        )


@shared_task(bind=True, max_retries=3)
def send_verification_code(self, telegram_chat_id):
    try:
        # Получаем чат (синхронный запрос в асинхронной задаче)
        chat = TelegramChat.objects.get(telegram_chat=str(telegram_chat_id))

        # Генерируем код
        code = randint(1000, 9999)

        # Отправляем сообщение через бота
        bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

        # Используем sync_to_async для асинхронной отправки
        sync_to_async(bot.send_message)(
            chat_id=telegram_chat_id,
            text=f"Ваш код подтверждения: {code}\n"
            "Введите его на сайте для отправки заявки на бронирование.",
        )

        # Сохраняем код в кеш (5 минут)
        from django.core.cache import cache

        cache.set(f'verify_{chat.phone}', code, timeout=300)

        logger.info(f"Sent verification code {code} to {telegram_chat_id}")

    except TelegramChat.DoesNotExist as ex:
        logger.error(f"Chat {telegram_chat_id} not found: {str(ex)}")
        raise self.retry(exc=ex, countdown=60)

    except TelegramError as ex:
        logger.error(f"Telegram error: {str(ex)}")
        raise self.retry(exc=ex, countdown=60)

    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}")
        raise self.retry(exc=ex, countdown=60)


async def handle_existing_user(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обработка существующего пользователя"""

    user_id = update.effective_user.id

    code = randint(1000, 9999)

    await update.message.reply_text(
        f"Ваш код подтверждения: {code}\n"
        "Введите его на сайте для отправки заявки на бронирование.",
        reply_markup=ReplyKeyboardRemove(),
    )

    print(user_id)

    chat = await sync_to_async(TelegramChat.objects.get)(
        telegram_chat=str(user_id)
    )

    await sync_to_async(cache.set)(f'verify_{chat.phone}', code, timeout=60)

    cached_code = cache.get(f'verify_{chat.phone}')

    logger.info(
        f"'verify_{chat.phone}': {type(chat.phone)}"
        f"'{cached_code}': {type(cached_code)}"
    )

    logger.info(
        f"Django API call: update form for user {user_id} with code {code}. "
        f"Cache: verify_{chat.phone}"
    )


async def handle_contact(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обработка полученного контакта"""
    user = update.effective_user
    contact = update.effective_message.contact

    if not contact or not contact.phone_number:
        await update.message.reply_text("Не удалось получить номер телефона")
        return

    phone = contact.phone_number

    await sync_to_async(TelegramChat.objects.update_or_create)(
        phone=str(phone), telegram_chat=str(user.id)
    )

    await handle_existing_user(update, context)


async def request_phone_number(update: Update) -> None:
    """Запрашивает номер телефона у нового пользователя"""
    await update.message.reply_text(
        "Для регистрации поделитесь номером телефона",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


def main():
    token = os.getenv("TOKEN_TELEGRAM_BOT")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    application.run_polling()


if __name__ == '__main__':
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django

    django.setup()
    main()
