import os
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Contact
)
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

# ===== INIT =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== КНОПКА КОНТАКТА =====
contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="📞 Оставить номер телефона",
            request_contact=True
        )]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ===== /start =====
@dp.message(CommandStart(), ChatType.PRIVATE)
async def start(message: Message):
    await message.answer(
        "Если удобно, оставьте номер телефона — менеджер свяжется с вами напрямую 👇",
        reply_markup=contact_kb
    )

# ===== ПОЛУЧЕНИЕ КОНТАКТА =====
@dp.message(lambda m: m.contact is not None, ChatType.PRIVATE)
async def handle_contact(message: Message):
    contact: Contact = message.contact

    text = (
        "📞 <b>Клиент оставил контакт</b>\n"
        "━━━━━━━━━━━━\n"
        f"🆔 <code>{contact.user_id}</code>\n"
        f"👤 Имя: <b>{contact.first_name}</b>\n"
        f"📱 Телефон: <code>{contact.phone_number}</code>"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        parse_mode="HTML"
    )

    await message.answer(
        "✅ <b>Спасибо!</b>\n\n"
        "Менеджер получил ваш номер и свяжется с вами в ближайшее время 🙌",
        parse_mode="HTML",
        reply_markup=None
    )

# ===== СООБЩЕНИЯ ОТ КЛИЕНТА → МЕНЕДЖЕРАМ =====
@dp.message(ChatType.PRIVATE)
async def from_client(message: Message):
    text = (
        "👤 <b>Новый клиент</b>\n"
        "━━━━━━━━━━━━\n"
        f"🆔 <code>{message.from_user.id}</code>\n"
        f"👤 Имя: <b>{message.from_user.full_name}</b>\n\n"
        "💬 <b>Сообщение:</b>\n"
        f"{message.text}"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        parse_mode="HTML"
    )

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
