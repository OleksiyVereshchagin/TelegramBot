from aiogram import types
from bot import cmd_about, dp, handle_search, answer  # Імпортуємо функцію, яку треба протестувати
import pytest
from unittest.mock import AsyncMock, patch
from bot import add_wishlist_series  # Замість your_module використовуйте правильний шлях до вашого модуля

@pytest.mark.asyncio
async def test_cmd_about():
    # Створення тестового повідомлення
    message = AsyncMock(spec=types.Message)  # Використовуємо AsyncMock
    message.from_user.first_name = "John"
    message.from_user.id = 123456789
    message.text = "About"

    # Мокання асинхронних методів
    message.answer = AsyncMock()

    # Виклик функції обробки команди
    await cmd_about(message)  # Викликаємо команду напряму

    # Перевірка, що метод answer викликано і що в повідомленні є частина тексту про бота
    message.answer.assert_called_once()
    assert "SeriesBot - ваш особистий помічник" in message.answer.call_args[0][0]  # Перевірка наявності частини тексту про бота




@pytest.mark.asyncio
async def test_add_wishlist_series():
    # Параметри для тесту
    user_id = 123456789
    series_name = "Breaking Bad"

    # Мокання execute_query
    with patch('db.execute_query', new_callable=AsyncMock) as mock_execute_query:
        # Викликаємо функцію, яку тестуємо
        await add_wishlist_series(user_id, series_name)

        # Перевіряємо, чи викликана функція execute_query з правильними параметрами
        mock_execute_query.assert_called_once_with(
            "INSERT INTO wishlist_series (user_id, series_name) VALUES ($1, $2) ON CONFLICT DO NOTHING;",
            user_id, series_name
        )

@pytest.mark.asyncio
async def test_unknown_message():
    # Створення тестового повідомлення
    message = AsyncMock(types.Message)
    message.text = "Hello"

    # Мокання методів
    message.reply = AsyncMock()

    # Виклик функції обробки невідомих повідомлень
    await answer(message)

    # Перевірка, що метод reply був викликаний і що в повідомленні є відповідь
    message.reply.assert_called_once()
    assert "Вибачте, я не розумію вашого запиту" in message.reply.call_args[0][0]
