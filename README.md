# TGB_RSA_AES_GCM

![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fghloc.vercel.app%2Fapi%2FZeragorn-ru%2Frsa_encode_bot%2Fbadge&query=message&style=flat-square&label=Lines)

# Описание

Телеграмм бот позволяющий шифровать сообщения гибридным алгоритмом RSA + AES. Для использования вы отправляете ключи в формате .pem или генерируете их командой /genereate, после чего можете отвечая на них шифровать и расшифровывать сообщения.

# Настройка

Для настройки создайте в папке с ботом .env файл со следующим содержанием:

  BOT_TOKEN=<token>
  ADMINS=<1_admin_user_id>,<2_admin_user_id>,<3_admin_user_id>

