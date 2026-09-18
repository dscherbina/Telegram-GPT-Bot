"""Вільний діалог із ChatGPT."""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from aiogram import F

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from gpt import ask_prompt
from handlers.common import THINKING, USER_TEXT
from utils import image_path, load_message

router = Router(name="gpt")
logger = logging.getLogger(__name__)


class GptStates(StatesGroup):
    """Стан сценарію «ChatGPT інтерфейс»."""
    dialog = State()


async def start_gpt(message: Message, state: FSMContext) -> None:
    """Вмикає режим діалогу та показує підготовлене зображення."""
    await state.set_state(GptStates.dialog)
    await message.answer_photo(
        photo=FSInputFile(image_path("gpt")),
        caption=load_message("gpt"),
    )


@router.message(Command("gpt"))
async def handle_command_gpt(message: Message, state: FSMContext) -> None:
    """Команда /gpt."""
    logger.info("Користувач %s запустив /gpt", message.from_user.id)
    await start_gpt(message, state)


@router.message(F.text == reply_kb.BTN_GPT)
async def handle_button_gpt(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Чат-бот»."""
    logger.info("Користувач %s відкрив режим /gpt через кнопку", message.from_user.id)
    await start_gpt(message, state)


@router.message(GptStates.dialog, USER_TEXT)
async def handle_gpt_message(message: Message) -> None:
    """Будь-який текст у режимі /gpt передається моделі."""
    logger.info("Користувач %s: запит до GPT: %s", message.from_user.id, message.text)
    placeholder = await message.answer(THINKING)
    text = await ask_prompt("gpt", message.text)
    await placeholder.delete()
    await message.answer(text, reply_markup=inline_kb.finish_kb)

