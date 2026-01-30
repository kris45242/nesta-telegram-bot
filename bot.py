import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ─────────────────────────────
# /start для клиента
# ─────────────────────────────
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "👋 Здравствуйте!\n\n"
        "Вы можете написать нам сообщение — менеджер скоро ответит."
    )


# ─────────────────────────────
# Клиент → группа менеджеров
# ─────────────────────────────
@dp.message(F.chat.type == "private")
async def from_client(message: Message):
    text = (
        "👤 <b>Новый клиент</b>\n"
        f"🆔 <b>ID:</b> {message.from_user.id}\n"
        f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
        "🟡 <b>Статус:</b> В работе\n\n"
        "💬 <b>Сообщение:</b>\n"
        f"{message.text}"
    )

    await bot.send_message(
        chat_id=MANAGER_CHAT_ID,
        text=text,
        parse_mode="HTML"
    )


# ─────────────────────────────
# Менеджер → клиент (/answer)
# ─────────────────────────────
@dp.message(Command("answer"), F.chat.id == MANAGER_CHAT_ID)
async def answer_from_manager(message: Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply(
            "❌ Формат команды:\n"
            "<code>/answer ID текст_ответа</code>",
            parse_mode="HTML"
        )
        return

    try:
        client_id = int(parts[1])
    except ValueError:
        await message.reply("❌ ID должен быть числом")
        return

    answer_text = parts[2]

    await bot.send_message(
        chat_id=client_id,
        text=answer_text
    )

    await message.reply("✅ Ответ отправлен клиенту")


# ─────────────────────────────
# Запуск
# ─────────────────────────────
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
