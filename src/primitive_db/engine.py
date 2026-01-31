import shlex

import prompt

from .constants import ERROR_MESSAGES, HELP_MESSAGE
from .core import create_table, drop_table, list_tables
from .utils import ensure_data_dir, load_metadata, save_metadata


def run():
    """Основной цикл программы."""
    ensure_data_dir()
    print("***Примитивная база данных***")
    print(HELP_MESSAGE)

    while True:
        command = prompt.string("Введите команду: ").strip().lower()
        
        if command == "exit":
            print("Выход из программы.")
        try:
            user_input = input("Введите команду: ").strip()
            if not user_input:
                continue
                
            # Разбиваем команду на части с учетом кавычек
            parts = shlex.split(user_input)
            command = parts[0].lower()
            args = parts[1:]
            
            # Загружаем актуальные метаданные
            metadata = load_metadata()
            
            if command == "exit":
                print("Выход из программы.")
                break
                
            elif command == "help":
                print(HELP_MESSAGE)
                
            elif command == "create_table":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов. Используйте: create_table <имя> <столбец1:тип> ...")
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                success, message = create_table(metadata, table_name, columns)
                print(message)
                if success:
                    save_metadata(metadata)
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. Используйте: drop_table <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = drop_table(metadata, table_name)
                print(message)
                if success:
                    save_metadata(metadata)
                    
            elif command == "list_tables":
                result = list_tables(metadata)
                print(result)
                
            else:
                print(ERROR_MESSAGES["unknown_command"].format(command))
                
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
