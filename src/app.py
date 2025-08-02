import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import settings
from src.log import logger

from .api.db.database import Base, engine
from .routes.tasks import register_task_handlers


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # /start and /menu handler
    @dp.message(Command(commands=["start", "menu"]))
    async def cmd_start(message: types.Message) -> None:
        # Main menu keyboard
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Задачи"), KeyboardButton(text="⏲️ Трекер времени")],
                [KeyboardButton(text="📆 События"), KeyboardButton(text="📄 Документы")],
                [KeyboardButton(text="⚙️ Настройки")],
            ],
            resize_keyboard=True,
        )
        await message.answer("Выберите раздел:", reply_markup=main_kb)

    # Register feature modules
    register_task_handlers(dp)

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
