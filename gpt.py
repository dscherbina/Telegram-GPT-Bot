"""Тонкий асинхронний клієнт до OpenAI Chat Completions."""
import logging
import base64

from openai import AsyncOpenAI, OpenAIError

from config import settings
from utils import load_prompt

logger = logging.getLogger(__name__)

FALLBACK = "😔 Не вдалося звʼязатися з ChatGPT. Спробуй ще раз за хвилину."

_client_kwargs = {
    "api_key": settings.OPENAI_API_KEY,
    "timeout": settings.OPENAI_TIMEOUT,
    "max_retries": 2,
}
if settings.OPENAI_BASE_URL:
    _client_kwargs["base_url"] = settings.OPENAI_BASE_URL

client = AsyncOpenAI(**_client_kwargs)


async def ask(messages: list[dict]) -> str:
    """Надсилає готовий список повідомлень і повертає текст відповіді.

    Мережеві помилки не пробиваються назовні: у разі збою повертається
    FALLBACK, щоб хендлер міг спокійно відповісти користувачеві.
    """
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_completion_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
        )
    except OpenAIError as error:
        logger.error("Помилка OpenAI: %s", error)
        return FALLBACK
    except Exception as error:  # noqa: BLE001 - бот не має падати через API
        logger.exception("Неочікувана помилка при запиті до OpenAI: %s", error)
        return FALLBACK

    if not response.choices:
        logger.error("OpenAI повернув порожній список choices")
        return FALLBACK

    return (response.choices[0].message.content or "").strip() or FALLBACK


async def ask_prompt(prompt_name: str, user_message: str = "") -> str:
    """Формує запит із системним промптом з resources/prompts."""
    messages = [{"role": "system", "content": load_prompt(prompt_name)}]
    if user_message:
        messages.append({"role": "user", "content": user_message})
    return await ask(messages)


async def ask_with_system(system_prompt: str, user_message: str) -> str:
    """Запит із довільним системним промптом (не з файлу)."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    return await ask(messages)

async def ask_about_image(image_bytes: bytes) -> str:
    """Розпізнавання зображення: передає картинку моделі як data-URL."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {"role": "system", "content": load_prompt("vision")},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Що зображено на цій картинці?"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                },
            ],
        },
    ]
    return await ask(messages)