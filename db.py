import os
import asyncpg
import httpx
from asyncpg import PostgresError

async def add_watched_series(user_id: int, series_name: str):

    existing_series = await get_watched_series(user_id)

    if any(existing_series_name.lower() == series_name.lower() for existing_series_name in existing_series):
        print(f"Серіал {series_name} вже в списку переглянутого.")
        return

    # Виконуємо SQL запит для додавання серіалу
    await execute_query(
        "INSERT INTO watched_series (user_id, series_name) VALUES ($1, $2) ON CONFLICT DO NOTHING;",
        user_id, series_name
    )

async def series_exists(series_name: str) -> bool:
    url = f"https://api.tvmaze.com/search/shows?q={series_name}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            # Логування відповіді
            if response.status_code != 200:
                print(f"Помилка API: код статусу {response.status_code}")
                return False

            data = response.json()
            print(f"Отримані дані від API для '{series_name}': {data}")

        if not data:
            print(f"Серіал '{series_name}' не знайдено у відповіді API.")
            return False

        # Порівнюємо введену назву з отриманою
        for show in data:
            if show['show']['name'].strip().lower() == series_name.strip().lower():
                print(f"Серіал '{series_name}' знайдено в API.")
                return True

        print(f"Серіал '{series_name}' не знайдено серед результатів API.")
        return False
    except Exception as e:
        print(f"Помилка під час виклику API: {e}")
        return False

async def get_watched_series(user_id: int) -> list:
    query = "SELECT series_name FROM watched_series WHERE user_id = $1;"
    return await fetch_query(query, user_id)

async def create_db_connection():
    try:
        # Отримуємо значення з .env
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_host = os.getenv("DB_HOST")

        # Підключення до бази даних
        connection = await asyncpg.connect(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host
        )
        print("Підключення до бази даних успішне!")
        return connection

    except PostgresError as e:
        print(f"Помилка підключення до бази даних: {e}")
        return None

async def execute_query(query: str, *args):
    """Виконати запит до бази даних."""
    conn = await create_db_connection()
    if conn is None:
        print("Не вдалося встановити з'єднання з базою даних.")
        return None
    try:
        return await conn.execute(query, *args)
    except PostgresError as e:
        print(f"Помилка при виконанні запиту: {e}")
    finally:
        await conn.close()

async def fetch_query(query: str, *args):
    conn = await create_db_connection()
    if conn is None:
        return []  # Якщо з'єднання не вдалося, повертаємо пустий список
    try:
        result = await conn.fetch(query, *args)
        return [row['series_name'] for row in result]  # Переконуємося, що беремо 'series_name'
    except PostgresError as e:
        print(f"Помилка при отриманні даних: {e}")
        return []
    finally:
        await conn.close()

async def remove_watched_series(user_id: int, series_name: str):
    await execute_query("DELETE FROM watched_series WHERE user_id = $1 AND series_name ILIKE $2;", user_id, series_name)

async def get_watched_series(user_id: int):
    """Отримує список переглянутих серіалів з БД для конкретного користувача."""
    result = await fetch_query("SELECT series_name FROM watched_series WHERE user_id = $1;", user_id)
    return result  # Повертаємо просто результат, без обробки, оскільки fetch_query вже правильно формує список

async def clear_watched_series(user_id: int):
    """Очищаємо список переглянутих серіалів для конкретного користувача в базі даних."""
    await execute_query("DELETE FROM watched_series WHERE user_id = $1;", user_id)

async def get_wishlist_series(user_id: int):
    # Переконайтесь, що повертаються повні назви серіалів
    return await fetch_query("SELECT series_name FROM wishlist_series WHERE user_id = $1;", user_id)

async def add_wishlist_series(user_id: int, series_name: str):
    """Додає серіал до списку бажаних користувача"""
    await execute_query(
        "INSERT INTO wishlist_series (user_id, series_name) VALUES ($1, $2) ON CONFLICT DO NOTHING;",
        user_id, series_name
    )

async def remove_wishlist_series(user_id: int, series_name: str):
    await execute_query("DELETE FROM wishlist_series WHERE user_id = $1 AND series_name ILIKE $2;", user_id, series_name)

async def move_to_watched(user_id: int, series_name: str):
    await remove_wishlist_series(user_id, series_name)
    await add_watched_series(user_id, series_name)

async def clear_wishlist_series(user_id: int):
    await execute_query("DELETE FROM wishlist_series WHERE user_id = $1;", user_id)