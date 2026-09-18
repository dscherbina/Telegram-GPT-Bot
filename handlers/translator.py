"""Переклад тексту через ChatGPT."""
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

router = Router(name="translator")
logger = logging.getLogger(__name__)

LANGUAGES = {
    "en": "англійську",
    "de": "німецьку",
    "fr": "французьку",
    "es": "іспанську",
    "pl": "польську",
}

LANGUAGE_TITLES = {
    "en": "🇬🇧 Англійська",
    "de": "🇩🇪 Німецька",
    "fr": "🇫🇷 Французька",
    "es": "🇪🇸 Іспанська",
    "pl": "🇵🇱 Польська",
}

language_kb = inline_kb.build_choice_kb(LANGUAGE_TITLES, inline_kb.CB_TR_LANG_PREFIX)


class TranslateStates(StatesGroup):
    """Стани сценарію «Перекладач»."""

    choosing_lang = State()
    translating = State()


async def start_translate(message: Message, state: FSMContext) -> None:
    """Точка входу: показує зображення і пропонує обрати мову."""
    await state.set_state(TranslateStates.choosing_lang)
    await message.answer_photo(
        photo=FSInputFile(image_path("translate")),
        caption=load_message("translate"),
        reply_markup=language_kb,
    )


@router.message(Command("translate"))
async def handle_command_translate(message: Message, state: FSMContext) -> None:
    """Команда /translate."""
    logger.info("Користувач %s запустив /translate", message.from_user.id)
    await start_translate(message, state)


@router.message(F.text == reply_kb.BTN_TRANSLATE)
async def handle_button_translate(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Перекладач»."""
    logger.info("Користувач %s відкрив /translate через кнопку", message.from_user.id)
    await start_translate(message, state)


@router.callback_query(
    TranslateStates.choosing_lang, F.data.startswith(inline_kb.CB_TR_LANG_PREFIX)
)
async def handle_lang_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробка вибору мови перекладу."""
    lang_key = callback.data.removeprefix(inline_kb.CB_TR_LANG_PREFIX)
    if lang_key not in LANGUAGES:
        await callback.answer("Невідома мова", show_alert=True)
        return

    logger.info("Користувач %s обрав мову: %s", callback.from_user.id, lang_key)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(lang_key=lang_key)
    await state.set_state(TranslateStates.translating)
    await callback.message.answer(
        f"Надішли текст, який перекласти на {LANGUAGES[lang_key]}."
    )


@router.message(TranslateStates.translating, USER_TEXT)
async def handle_text_to_translate(message: Message, state: FSMContext) -> None:
    """Перекладає надісланий текст на обрану мову."""
    logger.info("Користувач %s надіслав текст для перекладу", message.from_user.id)
    data = await state.get_data()
    lang_key = data.get("lang_key")
    if not lang_key:
        await message.answer("Спершу обери мову через /translate.")
        return

    system_prompt = (
        f"Ти — професійний перекладач. Переклади текст користувача на "
        f"{LANGUAGES[lang_key]} мову. Виведи ЛИШЕ переклад, без пояснень і "
        f"лапок."
    )
    placeholder = await message.answer(THINKING)
    text = await ask_with_system(system_prompt, message.text)
    await placeholder.delete()
    await message.answer(text, reply_markup=inline_kb.translate_kb)


@router.callback_query(F.data == inline_kb.CB_TR_CHANGE)
async def handle_change_lang(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Змінити мову» — повертає до вибору мови."""
    logger.info("Користувач %s змінює мову перекладу", callback.from_user.id)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(TranslateStates.choosing_lang)
    await callback.message.answer("Обери нову мову:", reply_markup=language_kb)