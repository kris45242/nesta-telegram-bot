import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FContext # Для управления состояниями

# Состояния для менеджера
class AdminStates(StatesGroup):
    waiting_for_answer = State()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client_status = {}

def get_status(client_id: int) -> str:
    return client_status.get(client_id, "🟡 В работе")

# ---------------- /start ----------------
@dp.message(Command("start"))
async def start(message: Message):
    text = "👋 Привет!\nНапишите ваше сообщение — менеджер скоро ответит."
    # Исправлено: request_contact работает ТОЛЬКО в ReplyKeyboard (обычные кнопки), 
    # в InlineKeyboard (под сообщением) его использовать нельзя.
    await message.answer(text)

# ---------------- КЛИЕНТ → МЕНЕДЖЕРЫ ----------------
@dp.message(F.chat.type == ChatType.PRIVATE, F.chat.id != MANAGER_CHAT_ID)
async def from_client(message: Message):
    client_id = message.from_user.id
    client_name = message.from_user.full_name
    text = message.text or "[Медиа-сообщение]"

    if client_id not in client_status:
        client_status[client_id] = "🟡 В работе"

    # ИСПОЛЬЗУЕМ callback_data вместо switch_inline
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ответить", callback_data=f"ask_reply:{client_id}")],
        [
            InlineKeyboardButton(text="🟡 В работе", callback_data=f"work:{client_id}"),
            InlineKeyboardButton(text="✅ Закрыт", callback_data=f"done:{client_id}")
        ]
    ])

    msg = (
        f"👤 *Новый клиент*\n🆔 `{client_id}`\n👤 Имя: {client_name}\n"
        f"📌 Статус: *{get_status(client_id)}*\n\n💬 Сообщение:\n{text}"
    )

    await bot.send_message(MANAGER_CHAT_ID, msg, reply_markup=keyboard, parse_mode="Markdown")

# ---------------- ЛОГИКА ОТВЕТА (FSM) ----------------

# 1. Менеджер нажал кнопку "Ответить"
@dp.callback_query(F.data.startswith("ask_reply:"))
async def prepare_answer(callback: CallbackQuery, state: FContext):
    client_id = callback.data.split(":")[1]
    await state.update_data(target_client_id=client_id) # Запоминаем ID
    await state.set_state(AdminStates.waiting_for_answer) # Включаем режим ожидания текста
    
    await callback.message.answer(f"📝 Введите ответ для клиента `{client_id}`:", parse_mode="Markdown")
    await callback.answer()

# 2. Менеджер прислал текст ответа
@dp.message(AdminStates.waiting_for_answer, F.chat.id == MANAGER_CHAT_ID)
async def send_answer_to_client(message: Message, state: FContext):
    data = await state.get_data()
    client_id = data.get("target_client_id")
    
    try:
        await bot.send_message(client_id, f"<b>Ответ менеджера:</b>\n\n{message.text}", parse_mode="HTML")
        await message.answer("✅ Отправлено клиенту!")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки: {e}")
    
    await state.clear() # Выходим из режима ответа

# ---------------- СТАТУСЫ ----------------
@dp.callback_query(F.data.startswith(("work:", "done:")))
async def change_status(callback: CallbackQuery):
    action, client_id = callback.data.split(":")
    client_id = int(client_id)
    client_status[client_id] = "🟡 В работе" if action == "work" else "✅ Закрыт"
    
    await callback.answer(f"Статус обновлен: {client_status[client_id]}")
    # Можно обновить текст сообщения у менеджера, чтобы статус поменялся и там
    await callback.message.edit_text(f"{callback.message.text}\n\n(Обновлено: {client_status[client_id]})")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
