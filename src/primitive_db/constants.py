"""Константы для базы данных."""

# Пути к файлам
DB_META_PATH = "db_meta.json"
DATA_DIR = "data"

# Поддерживаемые типы данных
SUPPORTED_TYPES = {"int", "str", "bool"}

# Автоматические колонки
AUTO_ID_COLUMN = "ID:int"

# Сообщения
HELP_MESSAGE = (
    "Функции:\n"
    "<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу\n"
    "<command> list_tables - показать список всех таблиц\n"
    "<command> drop_table <имя_таблицы> - удалить таблицу\n"
    "<command> insert into <имя_таблицы> values (...) - создать запись\n"
    "<command> select from <имя_таблицы> [where ...] - прочитать записи\n"
    "<command> update <имя_таблицы> set ... where ... - обновить запись\n"
    "<command> delete from <имя_таблицы> where ... - удалить запись\n"
    "<command> info <имя_таблицы> - вывести информацию о таблице\n"
    "<command> exit - выход из программы\n"
    "<command> help - справочная информация"
)

ERROR_MESSAGES = {
    "table_exists": 'Ошибка: Таблица "{}" уже существует.',
    "table_not_exists": 'Ошибка: Таблица "{}" не существует.',
    "invalid_type": (
        'Некорректный тип данных: "{}". Поддерживаемые типы: int, str, bool.'
    ),
    "unknown_command": 'Функции "{}" нет. Попробуйте снова.',
    "invalid_value": 'Некорректное значение: "{}". Попробуйте снова.',
    "wrong_value_count": "Ошибка: Количество значений не соответствует столбцам.",
    "invalid_value_for_type": "Ошибка: Неверное значение '{}' для типа '{}'.",
}