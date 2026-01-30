from aiogram import Bot, Dispatcher, executor, types
import os

# Берём данные из переменных окружения (Railway)
TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Клиент → чат менеджеров
@dp.message_handler(lambda m: m.chat.type == "private")
async def from_client(message: types.Message):
    text = (
        f"👤 Новый клиент\n"
        f"ID: {message.from_user.id}\n\n"
        f"{message.text}"
    )
    await bot.send_message(MANAGER_CHAT_ID, text)

# Менеджеры → клиент (ответ через Reply)
@dp.message_handler(lambda m: m.chat.id == MANAGER_CHAT_ID and m.reply_to_message)
async def from_manager(message: types.Message):
    try:
        lines = message.reply_to_message.text.split("\n")
        user_id = int(lines[1].replace("ID: ", ""))
        await bot.send_message(user_id, message.text)
    except:
        await message.reply("❌ Ответьте через reply на сообщение клиента")

if __name__ == "__main__":
    executor.start_polling(dp)
