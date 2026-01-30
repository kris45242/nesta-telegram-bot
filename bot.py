import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Contact
)
from aiogram.filters import CommandStart

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

# ===== INIT =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== КНОПКА КОНТАКТА =====
contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📞 Оставить номер телефона",
                request_contact=True
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ===== /start =====
@dp.message(CommandStart(), F.chat.type == "private")
async def start(message: Message):
    await message.answer(
        "Если удобно, оставьте номер телефона — менеджер свяжется с вами напрямую 👇",
        reply_markup=contact_kb
    )

# ===== КОНТАКТ ОТ КЛИЕНТА =====
@dp.message(F.contact, F.chat.type == "private")
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

# ===== СООБЩЕНИЯ КЛИЕНТА → МЕНЕДЖЕРАМ =====
@dp.message(F.chat.type == "private")
async def from_client(message: Message):
    if message.contact:
        return  # контакт уже обработан выше

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

# ===== START =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
# ===== ОТВЕТ МЕНЕДЖЕРА КЛИЕНТУ (через Reply) =====
@dp.message(F.chat.id == MANAGER_CHAT_ID, F.reply_to_message)
async def reply_from_manager(message: Message):
    original_text = message.reply_to_message.text or ""

    # ищем ID клиента в сообщении
    import re
    match = re.search(r"🆔\s*<code>(\d+)</code>", original_text)

    if not match:
        await message.reply("❌ Не удалось определить клиента. Ответьте реплаем на сообщение клиента.")
        return

    client_id = int(match.group(1))

    try:
        await bot.send_message(
            client_id,
            f"💬 <b>Ответ менеджера:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply("❌ Не удалось отправить сообщение клиенту (он мог заблокировать бота).")
