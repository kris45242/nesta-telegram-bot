import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ChatType
from aiogram.utils.markdown import hbold
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# временное хранилище: manager_id -> client_id
WAITING_REPLY = {}


# ---------- КЛИЕНТ → МЕНЕДЖЕРЫ ----------
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    client_id = message.from_user.id
    name = message.from_user.full_name

    text = (
        f"👤 <b>Новый клиент</b>\n"
        f"🆔 ID: <code>{client_id}</code>\n"
        f"👤 Имя: {name}\n\n"
        f"💬 <b>Сообщение:</b>\n{message.text}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍️ Ответить клиенту",
                    callback_data=f"reply:{client_id}"
                )
            ]
        ]
    )

    await bot.send_message(
        MANAGER_CHAT_ID,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ---------- НАЖАТИЕ КНОПКИ ----------
@dp.callback_query(F.data.startswith("reply:"))
async def start_reply(callback: CallbackQuery):
    client_id = int(callback.data.split(":")[1])
    manager_id = callback.from_user.id

    WAITING_REPLY[manager_id] = client_id

    await callback.answer()

    await bot.send_message(
        manager_id,
        f"✍️ Напишите ответ клиенту\n"
        f"🆔 ID: <code>{client_id}</code>",
        parse_mode="HTML"
    )


# ---------- СООБЩЕНИЕ МЕНЕДЖЕРА → КЛИЕНТ ----------
@dp.message()
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


# ---------- START ----------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Здравствуйте!\n"
        "Напишите ваш вопрос — менеджер ответит вам 💬"
    )


if __name__ == "__main__":
    dp.run_polling(bot)
