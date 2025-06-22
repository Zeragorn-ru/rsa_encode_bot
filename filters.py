# -*- coding: utf-8 -*-
from aiogram import types
from aiogram.filters import Filter
from aiogram.enums import ContentType
from aiogram.types import Message


# Кастомные фильтры для проверки на наличие ключа в ответе
class ReplyToPublicKey(Filter):
    def __init__(self, bot) -> None:
        self.bot = bot
    async def __call__(self, message: types.Message) -> bool:
        if not message.reply_to_message or not message.reply_to_message.document:
            return False

            # Проверяем расширение файла
        if not message.reply_to_message.document.file_name.endswith('.pem'):
            return False

        try:
            # Получаем file_id и скачиваем содержимое
            file_id = message.reply_to_message.document.file_id
            file = await self.bot.get_file(file_id)
            file_content = (await self.bot.download_file(file.file_path)).read().decode('utf-8')
            # Проверяем, что это публичный ключ
            return "PUBLIC KEY" in file_content
        except Exception as e:
            print(f"Ошибка при обработке файла в фильтре ReplyToPublicKey: {e}")
            return False


class ReplyToPrivateKey(Filter):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def __call__(self, message: types.Message) -> bool:
        if not message.reply_to_message or not message.reply_to_message.document:
            return False

        # Получаем file_id из документа в ответном сообщении
        file_id = message.reply_to_message.document.file_id
        if not message.reply_to_message.document.file_name.endswith('.pem'):
            return False

        try:
            # Запрашиваем информацию о файле
            file = await self.bot.get_file(file_id)
            # Скачиваем содержимое
            file_content = (await self.bot.download_file(file.file_path)).read().decode('utf-8')
            # Проверяем, что это приватный ключ
            return "PRIVATE KEY" in file_content
        except Exception as e:
            print(f"Ошибка при обработке файла в фильтре ReplyToPrivateKey: {e}")
            return False
