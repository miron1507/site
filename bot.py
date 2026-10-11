import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN="8722765598:AAF8U0FFYbf5EEjpx9Fzxzh1155zP-EKJyU"        # токен от @BotFather
OWNER_ID = 8525192816                      # твой Telegram ID (@encluziv)

URGENCY = {
    "urgent": "🔴 Срочно (нужен ответ сейчас)",
    "today": "🟡 Сегодня (в течение дня)",
    "later": "🟢 Не срочно (когда будет время)",
}


def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data=key)] for key, text in URGENCY.items()]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("urgency", None)
    await update.message.reply_text(
        "Здравствуйте! Насколько срочный у вас вопрос?", reply_markup=keyboard()
    )


async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    if key not in URGENCY:
        return
    context.user_data["urgency"] = key
    await query.edit_message_text(
        f"Выбрано: {URGENCY[key]}\n\nТеперь напишите ваше сообщение одним текстом."
    )


async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("urgency")
    if not key:
        await update.message.reply_text(
            "Сначала выберите срочность:", reply_markup=keyboard()
        )
        return

    user = update.effective_user
    # юзернейм определяется автоматически; если его нет — имя со ссылкой на профиль
    if user.username:
        who = f"@{user.username}"
    else:
        who = f"{user.full_name} (tg://user?id={user.id})"

    text = update.message.text or update.message.caption or "[вложение без текста]"
    await context.bot.send_message(
        OWNER_ID,
        f"{URGENCY[key]}\nОт: {who}\nID: {user.id}\n\n{text}",
    )
    # если прислали фото/файл/голосовое — пересылаем и само вложение
    if not update.message.text:
        await update.message.copy(chat_id=OWNER_ID)

    context.user_data.pop("urgency", None)
    await update.message.reply_text(
        "Спасибо! Сообщение передано. Чтобы отправить ещё одно — нажмите /start"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, receive))
    app.run_polling()


if __name__ == "__main__":
    main()
