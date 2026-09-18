"""Inline-клавіатури та константи callback_data."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CB_FINISH = "common:finish"
CB_RANDOM_MORE = "random:more"

CB_TALK_PREFIX = "talk:person:"

CB_QUIZ_TOPIC_PREFIX = "quiz:topic:"
CB_QUIZ_MORE = "quiz:more"
CB_QUIZ_CHANGE = "quiz:change"

finish_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)

random_fact_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Хочу ще факт", callback_data=CB_RANDOM_MORE)],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)

quiz_result_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Ще питання", callback_data=CB_QUIZ_MORE)],
        [InlineKeyboardButton(text="🔀 Змінити тему", callback_data=CB_QUIZ_CHANGE)],
        [InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)],
    ]
)


def build_choice_kb(
    items: dict[str, str],
    prefix: str,
    row_width: int = 2,
) -> InlineKeyboardMarkup:
    """Збирає клавіатуру вибору зі словника {ключ: підпис}."""
    buttons = [
        InlineKeyboardButton(text=title, callback_data=f"{prefix}{key}")
        for key, title in items.items()
    ]
    rows = [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
    rows.append([InlineKeyboardButton(text="❌ Закінчити", callback_data=CB_FINISH)])
    return InlineKeyboardMarkup(inline_keyboard=rows)