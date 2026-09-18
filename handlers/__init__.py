"""Збірка всіх роутерів проєкту."""
from .celebrity_talk import router as celebrity_talk_router
from .common import router as common_router
from .gpt import router as gpt_router
from .quiz import router as quiz_router
from .random_fact import router as random_fact_router
from .translator import router as translator_router
from .vision import router as vision_router

routers = [
    celebrity_talk_router,
    common_router,
    gpt_router,
    quiz_router,
    random_fact_router,
    translator_router,
    vision_router,
]