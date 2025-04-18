import os
import aiohttp

async def fetch_from_api(endpoint, params=None):
    """Асинхронна функція для виконання HTTP-запитів до API."""
    url = f"{os.getenv('API_BASE_URL')}/{endpoint}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching data from API: {e}")
            return None

async def get_series_by_genre(genre):
    """Отримує серіали за вибраним жанром."""
    shows = await fetch_from_api("shows")
    if shows:
        return [show for show in shows if genre in show.get('genres', [])]
    return []
