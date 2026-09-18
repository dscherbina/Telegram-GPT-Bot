"""Випадковий факт від ChatGPT."""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from gpt import ask_prompt
from handlers.common import THINKING
from utils import image_path, load_message

router = Router(name="random_fact")
logger = logging.getLogger(__name__)

MAX_HISTORY = 8

class RandomStates(StatesGroup):
    """Стан сценарію «Випадковий факт»."""
    fact = State()


async def send_fact(message: Message, state: FSMContext) -> None:
    """Запитує факт у моделі та надсилає його з кнопками."""
    data = await state.get_data()
    history: list[str] = data.get("facts_history", [])

    placeholder = await message.answer(THINKING)
    if history:
        avoid = "; ".join(history)
        user_message = (
            f"Розкажи новий факт, якого точно ще не було. "
            f"Не повторюй за змістом ці факти: {avoid}."
        )
    else:
        user_message = "Розкажи новий факт."
    text = await ask_prompt("random", user_message)
    await placeholder.delete()

    history.append(text[:120])
    await state.update_data(facts_history=history[-MAX_HISTORY:])

    await message.answer(text, reply_markup=inline_kb.random_fact_kb)


async def start_random(message: Message, state: FSMContext) -> None:
    """Точка входу сценарію: зображення, текст і перший факт."""
    await state.set_state(RandomStates.fact)
    await state.update_data(facts_history=[])
    await message.answer_photo(
        photo=FSInputFile(image_path("random")),
        caption=load_message("random"),
    )
    await send_fact(message, state)


@router.message(Command("random"))
async def handle_command_random(message: Message, state: FSMContext) -> None:
    """Команда /random."""
    logger.info("Користувач %s запустив /random", message.from_user.id)
    await start_random(message, state)


@router.message(F.text == reply_kb.BTN_FACT)
async def handle_button_random(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Цікавий факт»."""
    logger.info("Користувач %s відкрив /random через кнопку", message.from_user.id)
    await start_random(message, state)


@router.callback_query(F.data == inline_kb.CB_RANDOM_MORE)
async def handle_more(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Хочу ще факт» — працює так само як /random."""
    logger.info("Користувач %s запросив ще один факт", callback.from_user.id)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(RandomStates.fact)
    await send_fact(callback.message, state)