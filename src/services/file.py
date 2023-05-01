"""Модуль для работы с файлами."""

from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import UploadFile

from utils.constants import UPLOAD_DIR
from utils.exceptions import WrongFormatError


class FileManager:
    """Класс для обработки файлов."""

    def __init__(self) -> None:
        """Метод инициализирует расширение и путь файла."""
        self._format: str | None = None
        self._path: Path | None = None

    async def _is_correct_file(self, in_file: UploadFile) -> None:
        """
        Метод проверяет расширение файла.

        Args:
            in_file: входной файл
        """
        file_name = in_file.filename
        format = file_name.split('.')[-1]
        match format.lower():
            case 'jpg' | 'png':
                self._path = UPLOAD_DIR / file_name
                self._format = format
            case _:
                raise WrongFormatError("Not supported!")

    async def save(self, in_file) -> Path:
        """
        Метод сохраняет входной объект в файловую систему.

        Args:
            in_file: входной файл

        Returns:
            Путь до файла
        """

        await self._is_correct_file(in_file)
        async with aiofiles.open(self._path, mode="wb") as file:
            while content := await in_file.read(1024):
                await file.write(content)

        return self._path

    async def generate_name(self, prefix: UUID) -> Path:
        """
        Метод создаёт обработанному файлу имя.

        Args:
            prefix: идентификатор объекта

        Returns:
            Путь до файла с новым названием
        """

        file_name = '.'.join([str(prefix), self._format])
        return UPLOAD_DIR / file_name
