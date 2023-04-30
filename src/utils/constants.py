from enum import Enum
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / 'downloads'

UPLOAD_DIR.mkdir(exist_ok=True)


class Answer(str, Enum):
    DONE = 'Ваш трэк был успешно сохранён!'
