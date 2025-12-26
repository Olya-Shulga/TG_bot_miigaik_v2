import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from content import SECTIONS, SUBSECTION_TEXTS


# Настройка логгера (используется из content.py)
logger = logging.getLogger(__name__)


# Загрузка токена из .env-файла
load_dotenv()
TELEGRAM_TOKEN_BOT = os.getenv('TELEGRAM_TOKEN_BOT')


# Константы
MAIN_MENU = "main_menu"
BACK_TO_SECTION_PREFIX = "back_to_"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start — показывает главное меню."""
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    """Отображает главное меню с разделами 1–6."""
    keyboard = [
        [InlineKeyboardButton("Учёба", callback_data="1")],
        [InlineKeyboardButton("Документы и административные вопросы", callback_data="2")],
        [InlineKeyboardButton("Техническая поддержка", callback_data="3")],
        [InlineKeyboardButton("Финансовые и социальные вопросы", callback_data="4")],
        [InlineKeyboardButton("Университеты-партнёры", callback_data="5")],
        [InlineKeyboardButton("Контакты и команда", callback_data="6")],
        [InlineKeyboardButton("Часто задаваемые вопросы", callback_data="7")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Выберите интересующий раздел:"

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        # Приветствие
        await update.message.reply_text("Добро пожаловать в бот Сетевой магистратуры МИИГАиК!")
        await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode="HTML")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основной обработчик всех нажатий inline-кнопок."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # Главное меню
    if data == MAIN_MENU:
        await show_main_menu(update, context, edit=True)
        return

    # Проверка: это раздел (1–7)?
    if data in SECTIONS:
        section = SECTIONS[data]
        # Генерация кнопок подразделов
        sub_buttons = [
            [InlineKeyboardButton(title, callback_data=subkey)]
            for subkey, title in section["subsections"].items()
        ]
        sub_buttons.append([InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)])
        reply_markup = InlineKeyboardMarkup(sub_buttons)

        await query.edit_message_text(
            text=f"{section['text']}\n\nВыберите подраздел:",
            reply_markup=reply_markup,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
        return

    # Проверка: это подраздел (например, 1.1, 2.3, 5.2 и т.д.)?
    if data in SUBSECTION_TEXTS:
        text = SUBSECTION_TEXTS[data]
        # Определяем родительский раздел: "1.1" -> "1"
        section_key = data.split('.')[0]

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "↩️ Назад к разделу", callback_data=section_key
                ),
                InlineKeyboardButton(
                    "🏠 Главное меню", callback_data=MAIN_MENU
                )
            ]
        ])

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
        return

    # Непредвиденный callback_data
    logger.warning(f"Неизвестный callback_data: {data}")
    await query.edit_message_text(
        text="⚠️ Произошла ошибка. Вернитесь в главное меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
        ])
    )


# --- Запуск бота ---
def main():
    token = os.getenv("TELEGRAM_TOKEN_BOT")
    if not token:
        raise ValueError("Переменная окружения TELEGRAM_TOKEN_BOT не установлена!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Бот запущен и ожидает сообщения...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()