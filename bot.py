import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🧠 храним связь: message_id в группе → client_id
MESSAGE_CLIENT_MAP = {}


# ===== КНОПКА ОТПРАВКИ ТЕЛЕФОНА =====
phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Оставить номер", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)


# ===== START =====
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Здравствуйте 👋\n"
        "Напишите ваш вопрос — менеджер скоро ответит.\n\n"
        "Если удобно, оставьте номер телефона 👇",
        reply_markup=phone_kb
    )


# ===== ПОЛУЧЕНИЕ КОНТАКТА =====
@dp.message(F.contact)
async def contact_handler(message: Message):
    contact = message.contact
    await bot.send_message(
        MANAGER_CHAT_ID,
        f"📞 <b>Контакт клиента</b>\n"
        f"🆔 <code>{message.from_user.id}</code>\n"
        f"👤 {contact.first_name}\n"
        f"📱 {contact.phone_number}",
        parse_mode="HTML"
    )
    await message.answer("Спасибо! Менеджер свяжется с вами 🙌")


# ===== КЛИЕНТ → МЕНЕДЖЕРЫ =====
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    text = (
        f"👤 <b>Новый клиент</b>\n"
        f"🆔 <code>{message.from_user.id}</code>\n"
        f"Имя: {message.from_user.full_name}\n\n"
        f"{message.text}"
    )

    sent = await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        parse_mode="HTML"
    )

    # сохраняем связь message_id → client_id
    MESSAGE_CLIENT_MAP[sent.message_id] = message.from_user.id


# ===== МЕНЕДЖЕР → КЛИЕНТ (REPLY) =====
@dp.message(F.chat.id == MANAGER_CHAT_ID, F.reply_to_message)
async def reply_from_manager(message: Message):
    replied_id = message.reply_to_message.message_id

    if replied_id not in MESSAGE_CLIENT_MAP:
        await message.reply("❌ Ответьте реплаем на сообщение клиента.")
        return

    client_id = MESSAGE_CLIENT_MAP[replied_id]

    try:
        await bot.send_message(
            client_id,
            f"💬 <b>Ответ менеджера:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
    except Exception:
        await message.reply("❌ Клиент недоступен или заблокировал бота.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
