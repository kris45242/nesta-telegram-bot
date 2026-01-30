import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram.utils.markdown import hbold
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID = 0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# DEBUG: временно выводим chat.id в логи
@dp.message()
async def debug(message: Message):
    print("CHAT ID:", message.chat.id)

# Клиент → менеджеры
@dp.message(F.chat.type == ChatType.PRIVATE)
async def from_client(message: Message):
    text = (
        f"👤 {hbold('Новый клиент')}\n"
        f"ID: {message.from_user.id}\n\n"
        f"{message.text}"
    )
    await bot.send_message(MANAGER_CHAT_ID, text)

# Менеджеры → клиент (reply)
@dp.message(F.chat.id == MANAGER_CHAT_ID, F.reply_to_message)
async def from_manager(message: Message):
    try:
        lines = message.reply_to_message.text.split("\n")
        user_id = int(lines[1].replace("ID: ", ""))
        await bot.send_message(user_id, message.text)
    except:
        await message.reply("❌ Ответьте reply на сообщение клиента")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
