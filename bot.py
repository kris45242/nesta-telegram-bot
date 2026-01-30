import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ---------- START КЛИЕНТА ----------
@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start(message: Message):
    await message.answer(
        "Здравствуйте 👋\n"
        "Напишите ваш вопрос — менеджер ответит вам."
    )


# ---------- КЛИЕНТ → ГРУППА ----------
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    client_id = message.from_user.id

    text = (
        "👤 <b>Новый клиент</b>\n"
        f"🆔 ID: <code>{client_id}</code>\n"
        f"👤 {message.from_user.full_name}\n\n"
        f"💬 <b>Сообщение:</b>\n{message.text}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍️ Ответить",
                    # 👇 ЭТО ГЛАВНОЕ
                    switch_inline_query_current_chat=f"/answer {client_id} "
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


# ---------- /answer В ГРУППЕ ----------
@dp.message(
    F.chat.id == MANAGER_CHAT_ID,
    Command("answer")
)
async def answer_from_group(message: Message):
    if not message.text:
        return

    # формат: /answer ID текст
    match = re.match(r"/answer\s+(\d+)\s+(.+)", message.text, re.S)

    if not match:
        await message.reply(
            "❌ Неверный формат\n"
            "Используйте:\n"
            "<code>/answer ID текст ответа</code>",
            parse_mode="HTML"
        )
        return

    client_id = int(match.group(1))
    reply_text = match.group(2)

    try:
        await bot.send_message(
            client_id,
            f"💬 <b>Ответ менеджера:</b>\n\n{reply_text}",
            parse_mode="HTML"
        )
    except Exception:
        await message.reply("❌ Не удалось отправить сообщение клиенту")
        return

    await message.reply("✅ Ответ отправлен клиенту")


if __name__ == "__main__":
    dp.run_polling(bot)
