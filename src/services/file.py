from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import UploadFile

from utils.constants import UPLOAD_DIR


class FileManager:
    def __init__(self) -> None:
        self._in_file: UploadFile | None = None
        self._path: Path | None = None

    #TODO: убрать call
    async def __call__(self, file: UploadFile) -> Path:
        await self._is_correct_file(file)
        await self._save()
        return self._path

    async def _is_correct_file(self, in_file: UploadFile) -> None:
        file_name = in_file.filename
        target = file_name.split('.')[-1].lower()
        match target:
            case 'jpg' | 'png':
                self._path = UPLOAD_DIR / file_name
                self._in_file = in_file
            case _:
                #TODO: ADD new module EXCEPTIONS class IncorectFile
                raise "Not supported!"

    async def _save(self) -> None:
        async with aiofiles.open(self._path, mode="wb") as file:
            while content := await self._in_file.read(1024):
                await file.write(content)

        return self._path

    async def generate_name(self, prefix: UUID) -> Path:
        file_name = '.'.join([str(prefix), self._in_file.filename.split('.')[-1]])
        return UPLOAD_DIR / file_name
