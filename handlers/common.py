"""Спільні хендлери: /start, кнопка «Закінчити», типові відповіді."""
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from utils import image_path, load_message

from aiogram import F

router = Router(name="common")
logger = logging.getLogger(__name__)

THINKING = "⏳ Думаю..."

USER_TEXT = (
    F.text
    & ~F.text.startswith("/")
    & ~F.text.in_(reply_kb.MENU_BUTTONS)
)

async def show_main_menu(message: Message, state: FSMContext) -> None:
    """Скидає будь-який активний сценарій і показує головне меню."""
    await state.clear()
    await message.answer_photo(
        photo=FSInputFile(image_path("main")),
        caption=load_message("main"),
        reply_markup=reply_kb.main_menu_kb,
    )


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    """Команда /start."""
    logger.info("Користувач %s натиснув /start", message.from_user.id)
    await show_main_menu(message, state)


@router.callback_query(F.data == inline_kb.CB_FINISH)
async def handle_finish(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Закінчити»"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    logger.info("Користувач %s завершив сценарій", callback.from_user.id)
    await show_main_menu(callback.message, state)