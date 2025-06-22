import os

def dotenv_check() -> None:
    # Проверка и создание файла .env
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as file:
            token = input("Введите токен бота: ")
            admins = input("Введите user_id админов через запятую (или оставьте пустым): ")
            file.write(f"BOT_TOKEN={token}\nADMINS={admins.strip()}\n")
        print("Файл .env создан")