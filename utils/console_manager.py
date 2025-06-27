import asyncio
from config.config import Config

def print_help():
    print("\n=== Меню управления ===")
    print("add user <ID> - Добавить пользователя")
    print("add chat <ID> - Добавить чат (кроме основного)")
    print("list          - Показать все доступы")
    print("exit          - Выход")
    print(f"\nОсновной чат (фиксированный): {Config.MAIN_CHAT_ID}")

async def console_manager():
    print(f"\n{'='*30}")
    print(f"Консоль управления ботом")
    print(f"Основной чат: {Config.MAIN_CHAT_ID}")
    print_help()

    while True:
        try:
            cmd = input("\n> ").strip().lower().split()
            if not cmd:
                continue

            if cmd[0] == "exit":
                print("Завершение работы...")
                break

            elif cmd[0] == "help":
                print_help()

            elif cmd[0] == "add" and len(cmd) == 3:
                entity_type, entity_id = cmd[1], cmd[2]
                
                try:
                    entity_id = int(entity_id)
                    if entity_type == "user":
                        Config.add_allowed_user(entity_id)
                        print(f"✅ Пользователь {entity_id} добавлен")
                    elif entity_type == "chat":
                        if entity_id == Config.MAIN_CHAT_ID:
                            print("⚠️ Основной чат нельзя изменить!")
                        else:
                            Config.add_allowed_chat(entity_id)
                            print(f"✅ Чат {entity_id} добавлен")
                    else:
                        print("❌ Используйте 'user' или 'chat'")
                except ValueError:
                    print("❌ ID должен быть числом")

            elif cmd[0] == "list":
                print("\nТекущие разрешения:")
                print(f"• Основной чат: {Config.MAIN_CHAT_ID}")
                print(f"• Доп. чаты: {[c for c in Config.ALLOWED_CHAT_IDS if c != Config.MAIN_CHAT_ID]}")
                print(f"• Пользователи: {Config.ALLOWED_USER_IDS}")
                print(f"• Админы: {Config.ADMIN_USER_IDS}")

            else:
                print("❌ Неизвестная команда. Введите 'help'")

        except Exception as e:
            print(f"⚠️ Ошибка: {str(e)}")

if __name__ == "__main__":
    asyncio.run(console_manager())