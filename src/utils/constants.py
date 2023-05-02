"""Модуль дефолтных значений."""

from enum import Enum
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / 'downloads'

UPLOAD_DIR.mkdir(exist_ok=True)


class Answer(str, Enum):
    """Класс описывает Response-ответы."""
    DONE_CREATE_TRACK = 'Ваш трек был успешно сохранён!'
    FAIL_CREATE_TRACK = 'По заданным параметрам не удалось создать трек!'
    NOT_EXIST_TRACK = 'Трек с заданным `id` отсутствует!'
    FAIL_PLOT = 'Не удалось построить трек! Проверьте, чтобы расширение изображения было `.png`'
