import os
import re
import httpx

async def get_series_by_title(title: str):
    """Отримання серіалу за назвою через API."""
    api_url = "https://api.tvmaze.com/search/shows"
    params = {"q": title}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            results = response.json()
            return results[0]['show'] if results else None
    except httpx.RequestError as e:
        print(f"Error fetching series by title: {e}")
        return None


def clean_html(raw_html: str) -> str:
    """Видалення HTML-тегів із тексту."""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)


async def translate_text(text: str, target_lang: str = 'UK') -> str:
    """Переклад тексту за допомогою DeepL API."""
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        'auth_key': os.getenv('DEEPL_KEY'),
        'text': text,
        'target_lang': target_lang
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=params)
            response.raise_for_status()
            result = response.json()
            return result['translations'][0]['text'] if 'translations' in result else text
    except httpx.RequestError as e:
        print(f"Error in translation: {e}")
        return text


# Функція для обрізання опису до найближчого слова після 850 символів
def truncate_description(description: str, max_length=850):
    # Якщо опис менший або рівний максимальній довжині, повертаємо його без змін
    if len(description) <= max_length:
        return description

    truncated = description[:max_length]

    last_space = truncated.rfind(' ')
    if last_space != -1:
        truncated = truncated[:last_space]

    return truncated + "..."