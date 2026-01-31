
from .constants import AUTO_ID_COLUMN, ERROR_MESSAGES, SUPPORTED_TYPES


def create_table(metadata, table_name, columns):
    """Создает новую таблицу."""
    if table_name in metadata:
        return False, ERROR_MESSAGES["table_exists"].format(table_name)
    
    parsed_columns = []
    for column in columns:
        if ':' not in column:
            return False, ERROR_MESSAGES["invalid_value"].format(column)
        
        col_name, col_type = column.split(':', 1)
        if col_type not in SUPPORTED_TYPES:
            return False, ERROR_MESSAGES["invalid_type"].format(col_type)
        
        parsed_columns.append(f"{col_name}:{col_type}")
    
    final_columns = [AUTO_ID_COLUMN] + parsed_columns
    
    metadata[table_name] = final_columns
    
    columns_str = ", ".join(final_columns)
    success_message = f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'
    
    return True, success_message


def drop_table(metadata, table_name):
    """Удаляет таблицу."""
    if table_name not in metadata:
        return False, ERROR_MESSAGES["table_not_exists"].format(table_name)
    
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata):
    """Возвращает список всех таблиц."""
    if not metadata:
        return "Нет созданных таблиц."
    
    tables = "\n".join(f"- {table}" for table in metadata.keys())
    return tables


def validate_column_format(column):
    """Проверяет формат колонки (name:type)."""
    if ':' not in column:
        return False, None, None
    
    name, type_ = column.split(':', 1)
    return True, name.strip(), type_.strip()


def _cast_value(value, target_type):
    """Приводит значение к заданному типу."""
    try:
        if target_type == "int":
            return int(value)
        if target_type == "bool":
            if isinstance(value, str):
                return value.lower() in ["true", "1", "t", "y", "yes"]
            return bool(value)
        if target_type == "str":
            return str(value).strip("'\"")
        return value
    except (ValueError, AttributeError):
        return None


def get_column_type(metadata, table_name, column_name):
    """Получает тип столбца из метаданных."""
    if table_name in metadata:
        # ID - всегда инт тип для упрощения
        if column_name.upper() == "ID":
            return "int"
        for column in metadata[table_name]:
            name, type = column.split(":")
            if name == column_name:
                return type
    return None


def insert(metadata, table_data, table_name, values):
    """Вставляет новую запись в таблицу."""
    if table_name not in metadata:
        return False, ERROR_MESSAGES["table_not_exists"].format(table_name), None

    columns = metadata[table_name]
    #NOTE: -1 
    if len(values) != len(columns) - 1:
        return False, ERROR_MESSAGES["wrong_value_count"], None

    new_record = {}
    for i, column_def in enumerate(columns[1:]):
        col_name, col_type = column_def.split(":")
        value = _cast_value(values[i], col_type)
        if value is None:
            return (
                False,
                ERROR_MESSAGES["invalid_value_for_type"].format(values[i], col_type),
                None,
            )
        new_record[col_name] = value

    new_id = max([record.get("ID", 0) for record in table_data] + [0]) + 1
    new_record["ID"] = new_id

    table_data.append(new_record)
    return (
        True,
        f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".',
        table_data,
    )


def select(table_data, metadata, table_name, where_clause=None):
    """Выбирает записи из таблицы."""
    if not where_clause:
        return table_data

    results = []
    where_key, where_value_str = list(where_clause.items())[0]

    col_type = get_column_type(metadata, table_name, where_key)
    if not col_type:
        return []

    where_value = _cast_value(where_value_str, col_type)

    for record in table_data:
        if where_key in record and record[where_key] == where_value:
            results.append(record)

    return results


def update(table_data, metadata, table_name, set_clause, where_clause):
    """Обновляет записи в таблице."""
    updated_ids = []
    where_key, where_value_str = list(where_clause.items())[0]
    set_key, set_value_str = list(set_clause.items())[0]

    where_col_type = get_column_type(metadata, table_name, where_key)
    set_col_type = get_column_type(metadata, table_name, set_key)

    if not where_col_type or not set_col_type:
        return False, "Один из столбцов в условии не найден.", table_data

    where_value = _cast_value(where_value_str, where_col_type)
    set_value = _cast_value(set_value_str, set_col_type)

    if set_value is None:
        return (
            False,
            ERROR_MESSAGES["invalid_value_for_type"].format(set_value_str, set_col_type),
            table_data,
        )

    for record in table_data:
        if where_key in record and record[where_key] == where_value:
            record[set_key] = set_value
            updated_ids.append(record["ID"])

    if updated_ids:
        ids_str = ", ".join(map(str, updated_ids))
        return (
            True,
            f'Запись(и) с ID {ids_str} в таблице "{table_name}" успешно обновлена.',
            table_data,
        )

    return False, "Не найдено записей для обновления.", table_data


def delete(table_data, metadata, table_name, where_clause):
    """Удаляет записи из таблицы."""
    where_key, where_value_str = list(where_clause.items())[0]
    where_col_type = get_column_type(metadata, table_name, where_key)

    if not where_col_type:
        return False, "Столбец в условии не найден.", table_data

    where_value = _cast_value(where_value_str, where_col_type)

    ids_to_delete = {
        record["ID"]
        for record in table_data
        if where_key in record and record[where_key] == where_value
    }

    if not ids_to_delete:
        return False, "Не найдено записей для удаления.", table_data

    new_table_data = [
        record for record in table_data if record["ID"] not in ids_to_delete
    ]

    deleted_count = len(ids_to_delete)
    id_str = "запись"
    if deleted_count > 1:
        id_str = "записи"

    return True, f"{deleted_count} {id_str} успешно удалено.", new_table_data