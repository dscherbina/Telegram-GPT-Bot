"""Точка входу: запуск Telegram-бота."""
import asyncio
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from handlers import routers

TIME_ZONE = ZoneInfo("Europe/Kyiv")

class TzFormatter(logging.Formatter):
    """ Форматер логів, в заданій таймзоні"""
    def formatTime(self, record: logging.LogRecord, datefmt : str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=TIME_ZONE)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def setup_logging() -> None:
    """Налаштовує вивід логів у консоль та файл — вимога ТЗ."""
    formatter = TzFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    #     handlers=[
    #         logging.StreamHandler(sys.stdout),
    #         logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    #     ],
    # )
    # logging.getLogger("aiogram.event").setLevel(logging.WARNING)


async def main() -> None:
    """Створює бота, підключає роутери і запускає polling."""
    setup_logging()

    bot = Bot(
        settings.BOT_API_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_routers(*routers)

    print("Запускаємо бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Зупинка бота...")