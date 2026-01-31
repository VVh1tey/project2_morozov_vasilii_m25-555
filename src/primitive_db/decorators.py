import time
from functools import wraps


def handle_db_errors(func):
    """Декоратор для обработки ошибок базы данных."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    """Фабрика декораторов для подтверждения действия."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                prompt_message = (
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
                confirm = input(prompt_message).lower()
                if confirm == 'y':
                    return func(*args, **kwargs)
                else:
                    print("Операция отменена.")
                    return None
            except KeyboardInterrupt:
                print("\nОперация отменена.")
                return None
        return wrapper
    return decorator


def log_time(func):
    """Декоратор для замера времени выполнения функции."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(
            f"Функция {func.__name__} выполнилась "
            f"за {end_time - start_time:.3f} секунд."
        )
        return result
    return wrapper


def create_cacher():
    """Создает функцию с замыканием для кэширования."""
    cache = {}

    def cache_result(key, value_func):
        """Кэширует результат выполнения функции."""
        if key in cache:
            print("(из кэша)")
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result

    return cache_result
