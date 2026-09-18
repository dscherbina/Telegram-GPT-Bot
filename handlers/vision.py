"""Розпізнавання зображень через ChatGPT."""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from gpt import ask_about_image
from handlers.common import THINKING
from utils import image_path, load_message

router = Router(name="vision")
logger = logging.getLogger(__name__)


class VisionStates(StatesGroup):
    """Стан сценарію «Розпізнавання зображень»."""

    waiting_photo = State()


@router.message(F.text == reply_kb.BTN_VISION)
async def handle_button_vision(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Що на фото»."""
    logger.info("Користувач %s відкрив розпізнавання фото", message.from_user.id)
    await state.set_state(VisionStates.waiting_photo)
    await message.answer_photo(
        photo=FSInputFile(image_path("vision")),
        caption=load_message("vision"),
    )


@router.message(VisionStates.waiting_photo, F.photo)
async def handle_photo(message: Message, bot) -> None:
    """Обробляє надіслане фото та повертає опис від ChatGPT."""
    logger.info("Користувач %s надіслав фото на розпізнавання", message.from_user.id)
    placeholder = await message.answer(THINKING)

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    text = await ask_about_image(file_bytes.read())
    await placeholder.delete()
    await message.answer(text, reply_markup=inline_kb.finish_kb)