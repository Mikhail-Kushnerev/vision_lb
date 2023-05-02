"""Модель конфигурации кастомных расширений."""


class ErrorBase(Exception):

    def __init__(self, msg):
        self._msg = msg
        super().__init__(self._msg)
