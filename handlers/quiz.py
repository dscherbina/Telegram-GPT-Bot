"""Квіз з підрахунком балів."""
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

router = Router(name="quiz")
logger = logging.getLogger(__name__)

TOPICS = {
    "history": "🏛 Історія",
    "science": "🔬 Наука",
    "geography": "🌍 Географія",
    "movies": "🎬 Кіно",
}

MAX_HISTORY = 8

topic_kb = inline_kb.build_choice_kb(TOPICS, inline_kb.CB_QUIZ_TOPIC_PREFIX)

QUESTION_PROMPT = (
    "Ти — ведучий вікторини на тему «{topic}». Постав одне запитання "
    "середньої складності. Виведи ЛИШЕ текст запитання, без варіантів "
    "відповідей і без слова «Питання:». Українською."
)

CHECK_PROMPT = (
    "Ти — суворий, але доброзичливий перевіряючий відповідей у вікторині на "
    "тему «{topic}». Питання було: «{question}». Користувач відповів: "
    "«{answer}». Оціни, чи відповідь правильна по суті (не обов'язково "
    "дослівно). Перший рядок відповіді має бути рівно «ПРАВИЛЬНО» або "
    "«НЕПРАВИЛЬНО». Далі, з нового рядка, коротке пояснення (1-2 речення) "
    "та правильна відповідь, якщо користувач помилився. Українською."
)


class QuizStates(StatesGroup):
    """Стани сценарію «Квіз»."""

    choosing_topic = State()
    answering = State()


async def start_quiz(message: Message, state: FSMContext) -> None:
    """Точка входу: показує зображення і пропонує обрати тему."""
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(score=0, total=0)
    await message.answer_photo(
        photo=FSInputFile(image_path("quiz")),
        caption=load_message("quiz"),
        reply_markup=topic_kb,
    )


async def ask_question(message: Message, state: FSMContext, topic_key: str) -> None:
    """Генерує нове питання по обраній темі та зберігає його в стані."""
    data = await state.get_data()
    history: list[str] = data.get("questions_history", [])

    placeholder = await message.answer(THINKING)
    topic_title = TOPICS[topic_key]
    if history:
        avoid = "; ".join(history)
        user_message = (
            f"Постав нове питання, якого ще не було. "
            f"Не повторюй ці питання: {avoid}."
        )
    else:
        user_message = "Постав питання."
    question = await ask_with_system(
        QUESTION_PROMPT.format(topic=topic_title), user_message
    )
    await placeholder.delete()

    history.append(question[:120])
    await state.update_data(
        topic_key=topic_key,
        question=question,
        questions_history=history[-MAX_HISTORY:],
    )
    await state.set_state(QuizStates.answering)
    await message.answer(f"❓ {question}")


@router.message(Command("quiz"))
async def handle_command_quiz(message: Message, state: FSMContext) -> None:
    """Команда /quiz."""
    logger.info("Користувач %s запустив /quiz", message.from_user.id)
    await start_quiz(message, state)


@router.message(F.text == reply_kb.BTN_QUIZ)
async def handle_button_quiz(message: Message, state: FSMContext) -> None:
    """Кнопка головного меню «Квіз»."""
    logger.info("Користувач %s відкрив /quiz через кнопку", message.from_user.id)
    await start_quiz(message, state)


@router.callback_query(
    QuizStates.choosing_topic, F.data.startswith(inline_kb.CB_QUIZ_TOPIC_PREFIX)
)
async def handle_topic_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробка вибору теми: генеруємо перше питання."""
    topic_key = callback.data.removeprefix(inline_kb.CB_QUIZ_TOPIC_PREFIX)
    if topic_key not in TOPICS:
        await callback.answer("Невідома тема", show_alert=True)
        return

    logger.info("Користувач %s обрав тему квізу: %s", callback.from_user.id, topic_key)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await ask_question(callback.message, state, topic_key)


@router.message(QuizStates.answering, USER_TEXT)
async def handle_answer(message: Message, state: FSMContext) -> None:
    """Перевіряє відповідь користувача через ChatGPT і рахує бали."""
    logger.info("Користувач %s відповідає на квіз: %s", message.from_user.id, message.text)
    data = await state.get_data()
    topic_key = data.get("topic_key")
    question = data.get("question")
    if not topic_key or not question:
        await message.answer("Спершу обери тему через /quiz.")
        return

    placeholder = await message.answer(THINKING)
    verdict = await ask_with_system(
        CHECK_PROMPT.format(
            topic=TOPICS[topic_key], question=question, answer=message.text
        ),
        "Перевір відповідь.",
    )
    await placeholder.delete()

    is_correct = verdict.strip().upper().startswith("ПРАВИЛЬНО")
    score = data.get("score", 0) + (1 if is_correct else 0)
    total = data.get("total", 0) + 1
    await state.update_data(score=score, total=total)

    emoji = "✅" if is_correct else "❌"
    await message.answer(
        f"{emoji} {verdict}\n\n📊 Рахунок: {score}/{total}",
        reply_markup=inline_kb.quiz_result_kb,
    )


@router.callback_query(F.data == inline_kb.CB_QUIZ_MORE)
async def handle_more_question(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Ще питання» — те саме питання на тему."""
    data = await state.get_data()
    topic_key = data.get("topic_key")
    if not topic_key:
        await callback.answer("Спершу обери тему через /quiz.", show_alert=True)
        return

    logger.info("Користувач %s запросив ще питання на тему %s", callback.from_user.id, topic_key)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await ask_question(callback.message, state, topic_key)


@router.callback_query(F.data == inline_kb.CB_QUIZ_CHANGE)
async def handle_change_topic(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Змінити тему» — повертає до вибору теми, рахунок зберігається."""
    logger.info("Користувач %s змінює тему квізу", callback.from_user.id)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(questions_history=[])
    await state.set_state(QuizStates.choosing_topic)
    await callback.message.answer("Обери нову тему:", reply_markup=topic_kb)