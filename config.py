"""Конфігурація застосунку: читання змінних середовища з .env."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Налаштування бота, зібрані з .env."""
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")

    BOT_API_KEY: str = os.getenv("BOT_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "600"))
    OPENAI_TIMEOUT: float = float(os.getenv("OPENAI_TIMEOUT", "30"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "1.0"))

    REQUIRED = ("BOT_API_KEY", "OPENAI_API_KEY")

    def validate(self) -> None:
        """Кидає помилку, якщо не заповнені обов'язкові токени."""
        missing = [name for name in self.REQUIRED if not getattr(self, name)]
        if missing:
            raise RuntimeError(
                f"У .env не заповнені: {', '.join(missing)}. "
                f"Скопіюйте .env.example у .env і додайте токени."
            )


settings = Settings()
settings.validate()