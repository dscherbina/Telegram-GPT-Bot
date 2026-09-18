"""Допоміжні функції: доступ до ресурсів."""
from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent / "resources"


def image_path(filename: str) -> Path:
    """Повертає шлях до зображення resources/images/<filename>.jpg."""
    path = RESOURCES_DIR / "images" / f"{filename}.jpg"
    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")
    return path


def load_message(filename: str) -> str:
    """Повертає текст повідомлення з resources/messages."""
    path = RESOURCES_DIR / "messages" / f"{filename}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")
    return path.read_text(encoding="utf-8").strip()


def load_prompt(filename: str) -> str:
    """Повертає системний промпт з resources/prompts."""
    path = RESOURCES_DIR / "prompts" / f"{filename}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")
    return path.read_text(encoding="utf-8").strip()