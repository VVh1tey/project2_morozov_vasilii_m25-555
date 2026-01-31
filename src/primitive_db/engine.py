import re
import shlex

import prompt
from prettytable import PrettyTable

from .constants import ERROR_MESSAGES, HELP_MESSAGE
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from .decorators import create_cacher
from .utils import (
    ensure_data_dir,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def parse_clause(parts, keyword):
    """Парсит условие."""
    try:
        keyword_index = -1
        for i, part in enumerate(parts):
            if part.lower() == keyword:
                keyword_index = i
                break
        
        if keyword_index == -1:
            return None

        # Ожидаем: <ключ> = <значение>
        key = parts[keyword_index + 1]
        if parts[keyword_index + 2] != "=":
            return None
        value = parts[keyword_index + 3]
        return {key: value}
    except IndexError:
        return None


def parse_values(original_command):
    """Извлекает значения из команды INSERT."""
    match = re.search(r"values\s*\((.*)\)", original_command, re.IGNORECASE)
    if not match:
        return None
    
    values_str = match.group(1)
    # Простое разделение по запятой с очисткой пробелов
    return [v.strip() for v in values_str.split(',')]


def run():
    """Основной цикл программы."""
    ensure_data_dir()
    print("***Примитивная база данных***")
    print(HELP_MESSAGE)

    select_cacher = create_cacher()

    while True:
        original_command_str = prompt.string("Введите команду: ").strip()
        if not original_command_str:
            continue

        try:
            parts = shlex.split(original_command_str)
            command = parts[0].lower()
            args = parts[1:]

            metadata = load_metadata()

            if command == "exit":
                print("Выход из программы.")
                break

            elif command == "help":
                print(HELP_MESSAGE)

            elif command == "create_table":
                if len(args) < 2:
                    print(
                        "Ошибка: Недостаточно аргументов. "
                        "Используйте: create_table <имя> <столбец1:тип> ..."
                    )
                    continue
                table_name, columns = args[0], args[1:]
                success, message = create_table(metadata, table_name, columns)
                print(message)
                if success:
                    save_metadata(metadata)

            elif command == "drop_table":
                if len(args) != 1:
                    print(
                        "Ошибка: Неверное количество аргументов. "
                        "Используйте: drop_table <имя_таблицы>"
                    )
                    continue
                table_name = args[0]
                success, message = drop_table(metadata, table_name)
                print(message)
                if success:
                    save_metadata(metadata)

            elif command == "list_tables":
                print(list_tables(metadata))

            elif command == "insert":
                try:
                    into_index = parts.index("into")
                    parts.index("values") # Проверяем, что values есть в команде
                    table_name = parts[into_index + 1]
                except (ValueError, IndexError):
                    print(
                        "Ошибка: Неверный синтаксис. "
                        "Используйте: insert into <имя_таблицы> values (...)"
                    )
                    continue

                values = parse_values(original_command_str)
                if values is None:
                    print(
                        "Ошибка: Неверный синтаксис для values. "
                        "Убедитесь, что значения в скобках ()."
                    )
                    continue

                table_data = load_table_data(table_name)
                success, message, new_data = insert(
                    metadata, table_data, table_name, values
                )
                print(message)
                if success:
                    save_table_data(table_name, new_data)

            elif command == "select":
                try:
                    from_index = parts.index("from")
                    table_name = parts[from_index + 1]
                except (ValueError, IndexError):
                    print(
                        "Ошибка: Неверный синтаксис. "
                        "Используйте: select from <имя_таблицы> ..."
                    )
                    continue

                where_clause = parse_clause(parts, "where")

                cache_key = f"{table_name}-{where_clause}"

                def db_select():
                    table_data = load_table_data(table_name)
                    return select(table_data, metadata, table_name, where_clause)

                results = select_cacher(cache_key, db_select)

                if results is None:
                    continue

                if not results:
                    print("Нет записей, удовлетворяющих условию.")
                    continue

                if table_name not in metadata:
                    print(f"Ошибка: Не найдены метаданные для таблицы {table_name}")
                    continue

                field_names = [
                    col.split(":")[0] for col in metadata[table_name]
                ]
                table = PrettyTable(field_names=field_names)
                for row in results:
                    table.add_row([row.get(field) for field in field_names])
                print(table)

            elif command == "update":
                try:
                    table_name = parts[1]
                    if "set" not in parts or "where" not in parts:
                        raise ValueError
                except (ValueError, IndexError):
                    print(
                        "Ошибка: Неверный синтаксис. "
                        "Используйте: update <имя_таблицы> set ... where ..."
                    )
                    continue

                set_clause = parse_clause(parts, "set")
                where_clause = parse_clause(parts, "where")

                if not set_clause or not where_clause:
                    print("Ошибка: Неверный синтаксис для SET или WHERE.")
                    continue

                table_data = load_table_data(table_name)
                success, message, new_data = update(
                    table_data, metadata, table_name, set_clause, where_clause
                )
                print(message)
                if success:
                    save_table_data(table_name, new_data)

            elif command == "delete":
                try:
                    from_index = parts.index("from")
                    table_name = parts[from_index + 1]
                    if "where" not in parts:
                        raise ValueError
                except (ValueError, IndexError):
                    print(
                        "Ошибка: Неверный синтаксис. "
                        "Используйте: delete from <имя_таблицы> where ..."
                    )
                    continue

                where_clause = parse_clause(parts, "where")
                if not where_clause:
                    print("Ошибка: Неверный синтаксис для WHERE.")
                    continue

                table_data = load_table_data(table_name)
                success, message, new_data = delete(
                    table_data, metadata, table_name, where_clause
                )
                print(message)
                if success:
                    save_table_data(table_name, new_data)

            elif command == "info":
                if len(args) != 1:
                    print("Ошибка: Используйте: info <имя_таблицы>")
                    continue
                table_name = args[0]
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_exists"].format(table_name))
                    continue

                columns = ", ".join(metadata[table_name])
                num_records = len(load_table_data(table_name))
                print(f"Таблица: {table_name}")
                print(f"Столбцы: {columns}")
                print(f"Количество записей: {num_records}")

            else:
                print(ERROR_MESSAGES["unknown_command"].format(command))
                
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
