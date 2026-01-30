import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= КНОПКА КОНТАКТА =================

contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Передать номер менеджеру", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ================= КЛИЕНТ → МЕНЕДЖЕРЫ =================

@dp.message()
async def from_client(message: Message):
    # игнорируем сообщения от бота
    if message.from_user.is_bot:
        return

    # работаем ТОЛЬКО с личкой
    if message.chat.type != "private":
        return

    text = (
        "👤 Новый клиент\n"
        f"ID: {message.from_user.id}\n"
        f"Имя: {message.from_user.full_name}\n\n"
        f"{message.text}"
    )

    # отправляем в группу менеджеров
    await bot.send_message(MANAGER_CHAT_ID, text)

    # предлагаем оставить контакт
    await message.answer(
        "Если удобно, оставьте номер телефона — менеджер свяжется с вами напрямую 👇",
        reply_markup=contact_kb
    )

# ================= ПРИЁМ КОНТАКТА =================

@dp.message()
async def handle_contact(message: Message):
    if not message.contact:
        return

    text = (
        "📞 Клиент отправил контакт\n"
        f"Имя: {message.contact.first_name}\n"
        f"Телефон: {message.contact.phone_number}\n"
        f"User ID: {message.from_user.id}"
    )

    await bot.send_message(MANAGER_CHAT_ID, text)

    await message.answer(
        "Спасибо! Менеджер скоро свяжется с вами 🙌",
        reply_markup=None
    )

# ================= МЕНЕДЖЕР → КЛИЕНТ (REPLY) =================

@dp.message()
async def from_manager(message: Message):
    # игнорируем сообщения от бота
    if message.from_user.is_bot:
        return

    # работаем ТОЛЬКО в группе менеджеров
    if message.chat.id != MANAGER_CHAT_ID:
        return

    # ответ ТОЛЬКО через Reply
    if not message.reply_to_message:
        return

    try:
        original_text = message.reply_to_message.text or ""
        client_id = None

        for line in original_text.split("\n"):
            if line.startswith("ID:"):
                client_id = int(line.replace("ID:", "").strip())
                break

        if not client_id:
            return

        await bot.send_message(
            client_id,
            f"💬 Ответ менеджера:\n{message.text}"
        )

    except Exception:
        await message.reply("❌ Ответьте через Reply на сообщение клиента")

# ================= ЗАПУСК =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
