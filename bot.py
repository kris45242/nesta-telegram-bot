import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ChatType
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== ХРАНИЛИЩА =====
TICKETS = {}        # client_id -> {status, manager_id}
WAITING_REPLY = {} # manager_id -> client_id


# ===== КНОПКИ =====
def ticket_keyboard(client_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍️ Ответить",
                    callback_data=f"reply:{client_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 В работе",
                    callback_data=f"work:{client_id}"
                ),
                InlineKeyboardButton(
                    text="✅ Закрыть",
                    callback_data=f"close:{client_id}"
                )
            ]
        ]
    )


# ===== START КЛИЕНТА =====
@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start(message: Message):
    await message.answer(
        "Здравствуйте 👋\n"
        "Напишите ваш вопрос — менеджер ответит вам."
    )


# ===== КЛИЕНТ → ГРУППА =====
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    client_id = message.from_user.id

    if client_id not in TICKETS:
        TICKETS[client_id] = {
            "status": "new",
            "manager_id": None
        }

    text = (
        "👤 <b>Новый клиент</b>\n"
        f"🆔 <code>{client_id}</code>\n"
        f"👤 {message.from_user.full_name}\n"
        f"📌 Статус: <b>{TICKETS[client_id]['status']}</b>\n\n"
        f"💬 {message.text}"
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        reply_markup=ticket_keyboard(client_id),
        parse_mode="HTML"
    )


# ===== КНОПКА «В РАБОТЕ» =====
@dp.callback_query(F.data.startswith("work:"))
async def take_to_work(callback: CallbackQuery):
    client_id = int(callback.data.split(":")[1])

    TICKETS[client_id]["status"] = "in_progress"
    TICKETS[client_id]["manager_id"] = callback.from_user.id

    await callback.answer("Вы взяли диалог в работу")
    await callback.message.reply(
        f"🔄 Диалог с клиентом <code>{client_id}</code> взят в работу",
        parse_mode="HTML"
    )


# ===== КНОПКА «ЗАКРЫТЬ» =====
@dp.callback_query(F.data.startswith("close:"))
async def close_ticket(callback: CallbackQuery):
    client_id = int(callback.data.split(":")[1])

    TICKETS[client_id]["status"] = "closed"

    await callback.answer("Диалог закрыт")
    await callback.message.reply(
        f"✅ Диалог с клиентом <code>{client_id}</code> закрыт",
        parse_mode="HTML"
    )


# ===== КНОПКА «ОТВЕТИТЬ» =====
@dp.callback_query(F.data.startswith("reply:"))
async def start_reply(callback: CallbackQuery):
    client_id = int(callback.data.split(":")[1])
    manager_id = callback.from_user.id

    # если диалог уже в работе — проверяем владельца
    owner = TICKETS[client_id]["manager_id"]
    if owner and owner != manager_id:
        await callback.answer("Диалог уже в работе у другого менеджера", show_alert=True)
        return

    WAITING_REPLY[manager_id] = client_id
    await callback.answer()

    await bot.send_message(
        manager_id,
        f"✍️ Напишите ответ клиенту\n"
        f"🆔 <code>{client_id}</code>",
        parse_mode="HTML"
    )


# ===== СООБЩЕНИЕ МЕНЕДЖЕРА → КЛИЕНТ =====
@dp.message(F.chat.type == ChatType.PRIVATE)
async def manager_reply(message: Message):
    manager_id = message.from_user.id

    if manager_id not in WAITING_REPLY:
        return

    client_id = WAITING_REPLY.pop(manager_id)

    await bot.send_message(
        client_id,
        f"💬 <b>Ответ менеджера:</b>\n\n{message.text}",
        parse_mode="HTML"
    )

    await message.answer("✅ Ответ отправлен клиенту")


if __name__ == "__main__":
    dp.run_polling(bot)
