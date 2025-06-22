# -*- coding: utf-8 -*-
from os import getenv
from io import BytesIO
import asyncio

import pandas as pd
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from dotenv import load_dotenv

from dotenv_check import dotenv_check
from db_handler import db_check, update_stats
from crypt import generate_rsa_keys, encrypt_text, decrypt_text, is_pem_key
from filters import ReplyToPrivateKey, ReplyToPublicKey

dotenv_check()
load_dotenv()
bot: Bot = Bot(token=getenv("BOT_TOKEN"))
admins: list = [int(x) for x in getenv("ADMINS").split(",") if x.strip()] if getenv("ADMINS") else []
db_check()

dp: Dispatcher = Dispatcher()
router: Router = Router()

# Команда /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "Бот шифрования (RSA + AES-GCM)\n\n"
        "<b>Команды:</b>\n"
        "/generate — сгенерировать ключи\n"
        "/help — подробная инструкция\n"
        "/about — информация о шифровании",
        parse_mode="HTML"
    )

# Help command
@router.message(Command("help"))
async def start_command(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "<b>Инструкция по использованию бота</b>\n\n"
        "<b>Генерация ключей:</b>\n"
        "• Используйте команду <code>/generate</code> для создания ключей.\n"
        "• Или загрузите свои ключи в формате <a href=\"https://docs.fileformat.com/ru/web/pem/\">.pem</a>.\n\n"
        "<b>Шифрование и расшифровка:</b>\n"
        "• Ответьте на <b>публичный</b> ключ текстом – бот зашифрует его.\n"
        "• Ответьте на <b>приватный</b> ключ зашифрованным текстом – бот расшифрует его.",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# about command
@router.message(Command("about"))
async def about_command(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "<b>О шифровании RSA + AES-GCM</b>\n\n"
        "Гибридное шифрование объединяет два типа алгоритмов:\n"
        "• <b>RSA</b> — асимметричный алгоритм, используемый для безопасной передачи или шифрования сессионного ключа.\n"
        "• <b>AES-GCM</b> — симметричный алгоритм, обеспечивающий быстрое и надёжное шифрование данных с дополнительной аутентификацией.\n\n"
        "Схема работы:\n"
        "1. RSA используется для защиты сессионного ключа, который генерируется для каждой сессии.\n"
        "2. Полученный сессионный ключ применяется для шифрования данных алгоритмом AES-GCM.\n\n"
        "Для более подробного изучения:\n"
        "• <a href=\"https://ru.wikipedia.org/wiki/RSA\">RSA на Wikipedia</a>\n"
        "• <a href="
        "\"https://ru.wikipedia.org/wiki/AES_(%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82_%D1%88%D0%B8%D1%84%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)"
        "\">AES и режим GCM на Wikipedia</a>\n\n"
        "• <a href=\"https://youtu.be/vooHjWxmcIE?si=YXOj44XRmQf_OuLR\">Объяснение алгоритма RSA (YouTube)</a>\n"
        "• <a href=\"https://youtu.be/-fpVv_T4xwA?si=JXu4V7q-FDjvhcqV\">Объяснение AES-GCM (YouTube)</a>\n"
        "• <a href=\"https://youtu.be/qgofSZFTuVc?si=5Uk7BnaOXFzhjFxD\">Разбор работы шифрования в принципе (YouTube)</a>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# Команда /generate
@router.message(Command("generate"))
async def generate_keys_command(message: types.Message):
    user_id = message.from_user.id
    update_stats(user_id, "generate")
    public_key, private_key = generate_rsa_keys()
    public_key_file = BytesIO(public_key.encode())
    public_key_file.name = "public_key.pem"
    await bot.send_document(
        chat_id=message.chat.id,
        document=types.BufferedInputFile(public_key_file.getvalue(),
        filename="public_key.pem"),
        caption="Публичный ключ"
    )

    private_key_file = BytesIO(private_key.encode())
    private_key_file.name = "private_key.pem"
    await bot.send_document(
        chat_id=message.chat.id,
        document=types.BufferedInputFile(private_key_file.getvalue(),
        filename="private_key.pem"),
        caption="Приватный ключ"
    )

# Ответ текстом на Публичный ключ
@router.message(ReplyToPublicKey(bot))
async def text_encrypt(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    file_id = message.reply_to_message.document.file_id
    file = await bot.get_file(file_id)
    public_key = (await bot.download_file(file.file_path)).read().decode()
    encrypted = encrypt_text(text, public_key)
    update_stats(user_id, "encrypt")
    await bot.send_message(message.chat.id, text=f"<pre>{encrypted}</pre>", parse_mode="HTML")

# Ответ текстом на Приватный ключ
@router.message(ReplyToPrivateKey(bot))
async def text_decrypt(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    file_id = message.reply_to_message.document.file_id
    file = await bot.get_file(file_id)
    private_key = (await bot.download_file(file.file_path)).read().decode()
    decrypted = decrypt_text(text, private_key)
    update_stats(user_id, "decrypt")
    await bot.send_message(message.chat.id, f"<pre>{decrypted}</pre>", parse_mode="HTML")

# Команда /stats (только для админов)
@router.message(Command("stats"))
async def stats_command(message: types.Message):
    user_id = message.from_user.id

    if user_id not in admins:
        await bot.send_message(message.chat.id, "403")
        return
    conn = sqlite3.connect("stats.db")
    df = pd.read_sql_query("SELECT * FROM stats", conn)
    conn.close()

    if df.empty:
        await bot.send_message(message.chat.id, "Статистика пуста")
        return
    excel_file = BytesIO()

    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    await bot.send_document(
        chat_id=message.chat.id,
        document=types.BufferedInputFile(excel_file.getvalue(),
        filename="stats.xlsx"),
        caption="Статистика использования"
    )

async def on_startup() -> None:
    print("Бот запущен")
    for admin in admins:
        await bot.send_message(admin, "Бот запущен")

async def main() -> None:
    dp.startup.register(on_startup)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
