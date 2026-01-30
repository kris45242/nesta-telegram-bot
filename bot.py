import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ---------- ХРАНЕНИЕ СТАТУСОВ ----------
client_status = {}  # client_id: "В работе" | "Закрыт"

def get_status(client_id: int) -> str:
    return client_status.get(client_id, "🟡 В работе")

# ---------- КЛИЕНТ → МЕНЕДЖЕРЫ ----------

@dp.message_handler(content_types=types.ContentTypes.TEXT, chat_type=types.ChatType.PRIVATE)
async def from_client(message: types.Message):
    client_id = message.from_user.id
    client_name = message.from_user.full_name
    text = message.text

    # статус по умолчанию
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
                callback_data=f"status_work:{client_id}"
            ),
            InlineKeyboardButton(
                text="✅ Закрыт",
                callback_data=f"status_done:{client_id}"
            )
        ]
    ])

    msg = (
        f"👤 *Клиент*\n"
        f"🆔 `{client_id}`\n"
        f"👤 Имя: {client_name}\n"
        f"📌 Статус: *{get_status(client_id)}*\n\n"
        f"💬 *Сообщение:*\n{text}"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        msg,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ---------- СТАТУСЫ ----------

@dp.callback_query_handler(lambda c: c.data.startswith("status_"))
async def change_status(callback: types.CallbackQuery):
    action, client_id = callback.data.split(":")
    client_id = int(client_id)

    if action == "status_work":
        client_status[client_id] = "🟡 В работе"
    elif action == "status_done":
        client_status[client_id] = "✅ Закрыт"

    await callback.answer(f"Статус обновлён: {client_status[client_id]}")

# ---------- МЕНЕДЖЕР → КЛИЕНТ ----------

@dp.message_handler(commands=["answer"], chat_id=MANAGER_CHAT_ID)
async def answer_from_manager(message: types.Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply("❌ Формат: /answer <client_id> <текст>")
        return

    client_id = int(parts[1])
    answer_text = parts[2]

    await bot.send_message(client_id, answer_text)
    await message.reply("✅ Сообщение отправлено клиенту")

if __name__ == "__main__":
    executor.start_polling(dp)
