from aiogram import types
from bot import cmd_about, answer, cmd_start, cmd_help
import pytest
from unittest.mock import AsyncMock, patch
from bot import add_wishlist_series

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


@pytest.mark.asyncio
async def test_cmd_start():
    message = AsyncMock(spec=types.Message)
    message.from_user.first_name = "John"
    message.from_user.id = 123456789
    message.text = "/start"

    message.answer = AsyncMock()

    # Припускаємо, що основне меню є частиною відповіді
    await cmd_start(message)

    message.answer.assert_called_once()
    assert "Привіт, John!" in message.answer.call_args[0][0]  # Перевірка наявності привітання

@pytest.mark.asyncio
async def test_cmd_help():
    # Створення тестового повідомлення
    message = AsyncMock(spec=types.Message)
    message.from_user.first_name = "John"
    message.from_user.id = 123456789
    message.text = "Help"

    # Мокання методу 'answer'
    message.answer = AsyncMock()

    # Виклик функції обробки команди
    await cmd_help(message)

    # Перевірка, що метод 'answer' був викликаний один раз
    message.answer.assert_called_once()

    # Перевірка, що текст відповіді містить правильні команди
    help_text = message.answer.call_args[0][0]
    assert "Start" in help_text, "Команда 'Start' не знайдена в відповіді."
    assert "Help" in help_text, "Команда 'Help' не знайдена в відповіді."
    assert "Recommendations & Search" in help_text, "Команда 'Recommendations & Search' не знайдена в відповіді."

    # Додатково: перевірка наявності інших команд (для більш повної перевірки)
    assert "Watched List" in help_text, "Команда 'Watched List' не знайдена в відповіді."
    assert "Watch Later" in help_text, "Команда 'Watch Later' не знайдена в відповіді."