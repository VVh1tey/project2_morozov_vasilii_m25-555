import json
import os

from .constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def ensure_data_dir():
    """Создает директорию для данных если не существует."""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_table_file_path(table_name):
    """Возвращает путь к файлу таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")