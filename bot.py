import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- ХРАНЕНИЕ СТАТУСОВ ----------------
client_status = {}  # client_id -> status

def get_status(client_id: int) -> str:
    return client_status.get(client_id, "🟡 В работе")

# ---------------- /start ----------------
@dp.message(Command("start"))
async def start(message: Message):
    text = (
        "👋 Привет!\n\n"
        "Напишите ваше сообщение — менеджер скоро ответит.\n\n"
        "📞 Если удобно, оставьте номер телефона — мы свяжемся напрямую 👇"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Оставить номер",
            request_contact=True
        )]
    ])

    await message.answer(text, reply_markup=keyboard)

# ---------------- КЛИЕНТ → МЕНЕДЖЕРЫ ----------------
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    client_id = message.from_user.id
    client_name = message.from_user.full_name
    text = message.text or ""

    if client_id not in client_status:
        client_status[client_id] = "🟡 В работе"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✍️ Ответить",
                switch_inline_query_current_chat=f"/answer {client_id} "
            )
        ],
        [
            InlineKeyboardButton(
                text="🟡 В работе",
                callback_data=f"work:{client_id}"
            ),
            InlineKeyboardButton(
                text="✅ Закрыт",
                callback_data=f"done:{client_id}"
            )
        ]
    ])

    msg = (
        f"👤 *Новый клиент*\n"
        f"🆔 `{client_id}`\n"
        f"👤 Имя: {client_name}\n"
        f"📌 Статус: *{get_status(client_id)}*\n\n"
        f"💬 Сообщение:\n{text}"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        msg,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ---------------- СТАТУСЫ ----------------
@dp.callback_query(F.data.startswith(("work:", "done:")))
async def change_status(callback):
    action, client_id = callback.data.split(":")
    client_id = int(client_id)

    client_status[client_id] = (
        "🟡 В работе" if action == "work" else "✅ Закрыт"
    )

    await callback.answer(f"Статус: {client_status[client_id]}")

# ---------------- ОТВЕТ МЕНЕДЖЕРА ----------------
@dp.message(Command("answer"), F.chat.id == MANAGER_CHAT_ID)
async def answer_from_manager(message: Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply("❌ Формат: /answer <ID> <сообщение>")
        return

    client_id = int(parts[1])
    answer_text = parts[2]

    await bot.send_message(client_id, answer_text)
    await message.reply("✅ Ответ отправлен клиенту")

# ---------------- ЗАПУСК ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
