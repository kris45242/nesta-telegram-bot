import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простая память (можно потом заменить на БД)
clients_with_phone = set()


# ─────────────────────────────
# Кнопка "Оставить номер"
# ─────────────────────────────
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Оставить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# ─────────────────────────────
# /start
# ─────────────────────────────
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Здравствуйте!\n\n"
        "Напишите ваш вопрос — менеджер скоро ответит.\n\n"
        "Если удобно, вы можете оставить номер телефона 👇",
        reply_markup=contact_keyboard
    )


# ─────────────────────────────
# Получение контакта
# ─────────────────────────────
@dp.message(F.contact)
async def contact_handler(message: Message):
    clients_with_phone.add(message.from_user.id)

    phone = message.contact.phone_number
    name = message.from_user.full_name

    await bot.send_message(
        MANAGER_CHAT_ID,
        (
            "📞 <b>Контакт клиента</b>\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"👤 Имя: {name}\n"
            f"📱 Телефон: {phone}"
        ),
        parse_mode="HTML"
    )

    await message.answer(
        "✅ Спасибо! Менеджер свяжется с вами напрямую.",
        reply_markup=ReplyKeyboardRemove()
    )


# ─────────────────────────────
# Клиент → менеджеры
# ─────────────────────────────
@dp.message(F.chat.type == "private")
async def from_client(message: Message):
    if message.contact:
        return

    text = (
        "👤 <b>Новый клиент</b>\n"
        f"🆔 <b>ID:</b> {message.from_user.id}\n"
        f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
        "🟡 <b>Статус:</b> В работе\n\n"
        "💬 <b>Сообщение:</b>\n"
        f"{message.text}"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        parse_mode="HTML"
    )

    # если номер ещё не оставлял — покажем кнопку
    if message.from_user.id not in clients_with_phone:
        await message.answer(
            "Если удобно, оставьте номер телефона 👇",
            reply_markup=contact_keyboard
        )


# ─────────────────────────────
# Ответ менеджера клиенту
# /answer ID текст
# ─────────────────────────────
@dp.message(Command("answer"), F.chat.id == MANAGER_CHAT_ID)
async def answer_manager(message: Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply(
            "❌ Формат:\n<code>/answer ID текст</code>",
            parse_mode="HTML"
        )
        return

    try:
        client_id = int(parts[1])
    except ValueError:
        await message.reply("❌ ID должен быть числом")
        return

    await bot.send_message(
        chat_id=client_id,
        text=f"💬 Ответ менеджера:\n\n{parts[2]}"
    )

    await message.reply("✅ Ответ отправлен клиенту")


# ─────────────────────────────
# Запуск
# ─────────────────────────────
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
