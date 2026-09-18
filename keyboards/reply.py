"""Головне reply-меню бота."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_FACT = "🧠 Цікавий факт"
BTN_GPT = "🤖 Чат-бот"
BTN_TALK = "👤 Відома особистість"
BTN_QUIZ = "❓ Квіз"
BTN_TRANSLATE = "🌍 Перекладач"
BTN_VISION = "🖼 Що на фото"

MENU_BUTTONS = frozenset(
    {BTN_FACT, BTN_GPT, BTN_TALK, BTN_QUIZ, BTN_TRANSLATE, BTN_VISION}
)

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_FACT), KeyboardButton(text=BTN_GPT)],
        [KeyboardButton(text=BTN_TALK), KeyboardButton(text=BTN_QUIZ)],
        [KeyboardButton(text=BTN_TRANSLATE), KeyboardButton(text=BTN_VISION)],
    ],
    resize_keyboard=True,
    input_field_placeholder="Обери пункт меню",
)