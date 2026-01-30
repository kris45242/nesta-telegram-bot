import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# старт
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Здравствуйте! Напишите ваше сообщение, и мы передадим его менеджеру.")

# клиент → менеджеры
@dp.message()
async def from_client(message: Message):
    text = (
        "👤 Новый клиент\n"
        f"ID: {message.from_user.id}\n"
        f"Имя: {message.from_user.full_name}\n\n"
        f"{message.text}"
    )
    await bot.send_message(MANAGER_CHAT_ID, text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
from aiogram import F

# менеджер → клиент (ответ через Reply)
@dp.message(F.chat.id == MANAGER_CHAT_ID, F.reply_to_message)
async def from_manager(message: Message):
    try:
        # достаём ID клиента из текста сообщения
        lines = message.reply_to_message.text.split("\n")
        client_id_line = [line for line in lines if line.startswith("ID:")][0]
        client_id = int(client_id_line.replace("ID:", "").strip())

        await bot.send_message(
            client_id,
            f"💬 Ответ менеджера:\n{message.text}"
        )

    except Exception as e:
        await message.reply("❌ Ответьте через Reply на сообщение клиента")
