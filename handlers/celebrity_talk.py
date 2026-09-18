"""Діалог від імені відомої особистості."""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from gpt import ask_with_system
from handlers.common import THINKING, USER_TEXT
from utils import image_path, load_message

router = Router(name="celebrity_talk")
logger = logging.getLogger(__name__)

PERSONAS = {
    "cobain": "Курт Кобейн, лідер гурту Nirvana",
    "hawking": "Стівен Гокінг, фізик-теоретик",
    "nietzsche": "Фрідріх Ніцше, філософ",
    "queen": "Єлизавета II, королева Великої Британії",
    "tolkien": "Джон Р. Р. Толкін, письменник",
}

PERSONA_TITLES = {
    "cobain": "🎸 Курт Кобейн",
    "hawking": "🔭 Стівен Гокінг",
    "nietzsche": "📖 Фрідріх Ніцше",
    "queen": "👑 Єлизавета II",
    "tolkien": "🧙 Джон Толкін",
}

persona_kb = inline_kb.build_choice_kb(PERSONA_TITLES, inline_kb.CB_TALK_PREFIX)


class TalkStates(StatesGroup):
    """Стани сценарію «Діалог з відомою особистістю»."""

    choosing = State()
    dialog = State()


def build_system_prompt(persona_key: str) -> str:
    """Формує системний промпт під конкретну особистість."""
    bio = PERSONAS[persona_key]
    return (
        f"Ти — {bio}. Відповідай від першої особи, у характерному для цієї "
        f"людини стилі та світогляді. Відповідай українською, 2-5 речень. "
        f"Не вигадуй біографічних фактів, яких не існує."
    )


async def start_talk(message: Message, state: FSMContext) -> None:
    """Точка входу: показує зображення і пропонує обрати особистість."""
    await state.set_state(TalkStates.choosing)
    await message.answer_photo(
        photo=FSInputFile(image_path("talk")),
        caption=load_message("talk"),
        reply_markup=persona_kb,
    )


@router.message(Command("talk"))
async def handle_command_talk(message: Message, state: FSMContext) -> None:
    """Команда /talk."""
    logger.info("Користувач %s запустив /talk", message.from_user.id)
    await start_talk(message, state)


@router.message(F.text == reply_kb.BTN_TALK)
async def handle_button_talk(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Відома особистість»."""
    logger.info("Користувач %s відкрив /talk через кнопку", message.from_user.id)
    await start_talk(message, state)


@router.callback_query(
    TalkStates.choosing, F.data.startswith(inline_kb.CB_TALK_PREFIX)
)
async def handle_persona_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробка вибору особистості: зберігаємо промпт і показуємо фото."""
    persona_key = callback.data.removeprefix(inline_kb.CB_TALK_PREFIX)
    logger.info("Користувач %s обрав особистість: %s", callback.from_user.id, persona_key)
    if persona_key not in PERSONAS:
        await callback.answer("Невідома особистість", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(system_prompt=build_system_prompt(persona_key))
    await state.set_state(TalkStates.dialog)

    await callback.message.answer_photo(
        photo=FSInputFile(image_path(f"talk_{persona_key}")),
        caption=f"Тепер ти спілкуєшся з: {PERSONA_TITLES[persona_key]}\nНапиши своє повідомлення.",
    )


@router.message(TalkStates.dialog, USER_TEXT)
async def handle_talk_message(message: Message, state: FSMContext) -> None:
    """Пересилає повідомлення користувача обраній особистості."""
    logger.info("Користувач %s пише особистості: %s", message.from_user.id, message.text)
    data = await state.get_data()
    system_prompt = data.get("system_prompt")
    if not system_prompt:
        await message.answer("Спершу обери особистість через /talk.")
        return

    placeholder = await message.answer(THINKING)
    text = await ask_with_system(system_prompt, message.text)
    await placeholder.delete()
    await message.answer(text, reply_markup=inline_kb.finish_kb)