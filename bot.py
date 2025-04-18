import asyncio
import os
import logging
import random

from aiogram.utils import executor
from dotenv import load_dotenv
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import keyboards as kb
from db import (
    remove_watched_series, clear_watched_series, add_wishlist_series,
    get_wishlist_series, remove_wishlist_series, move_to_watched,
    clear_wishlist_series, add_watched_series, series_exists, get_watched_series
)
from utils import get_series_by_genre
from rec import recommend, format_show_info
from search import get_series_by_title, clean_html, translate_text


# Налаштування
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

# Перелік жанрів
GENRES = ['Action', 'Adventure', 'Anime', 'Comedy', 'Crime',
          'Drama', 'Espionage', 'Family', 'Fantasy', 'History', 'Horror', 'Legal',
          'Medical', 'Music', 'Mystery', 'Romance', 'Science-Fiction', 'Sports',
          'Supernatural', 'Thriller', 'War', 'Western']

# Стани для FSM
class SearchState(StatesGroup):
    waiting_for_title = State()  # Чекає на введення назви серіалу під час пошуку

class UserState(StatesGroup):
    waiting_for_count = State()  # Чекає на кількість серіалів

class WatchState(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу для перегляду

class RemoveState(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу для видалення

class Form(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу

class WishlistForm(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу для додавання в бажані

class WishlistRemove(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу для видалення з бажаних

class MoveToWatchedState(StatesGroup):
    waiting_for_series_name = State()  # Чекає на назву серіалу для переміщення до переглянутих

class ClearWishlistState(StatesGroup):
    waiting_for_confirmation = State()  # Чекає підтвердження для очищення списку бажаних

class ClearWatchedState(StatesGroup):
    waiting_for_confirmation = State()  # Стан, коли чекаємо на підтвердження від користувача

# Привітання та стартове меню
#Привітання та стартове меню
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Обробник команди /start.
    Вітання користувача та надання інформації про доступні команди.
    """

    await message.answer(f"Привіт, {message.from_user.first_name}! 👋", reply_markup=kb.main)


# Допомога - доступні команди
@dp.message_handler(text='Help')
async def cmd_help(message: types.Message):
    help_text = (
        "📜 *Опис доступних можливостей:*\n\n"
        "Start - запуск бота\n"
        "Help - допомога\n"
        "About - інформація про бота\n"
        "Recommendations & Search - рекомендації від бота та пошук за назвою\n"
        "Watched List - взаємодія зі списком переглянутих серіалів\n"
        "Watch Later - взаємодія зі списком бажаного до перегляду"
    )
    await message.answer(help_text, parse_mode='Markdown')

# Інформація про бота
@dp.message_handler(text='About')
async def cmd_about(message: types.Message):
    about_text = (
        "SeriesBot - ваш особистий помічник у світі телесеріалів! 🎬\n\n"
        "Цей бот допоможе вам знайти цікаві серіали, отримати рекомендації на основі ваших уподобань, "
        "та управляти списками переглянутих і бажаних серіалів.\n\n"
        "Ви можете шукати серіали за назвою, дізнатися про них більше за допомогою детальних відомостей, "
        "отримати популярні рекомендації або обирати серіали за жанрами, такими як комедії, драми, фантастика та інші.\n\n"
        "SeriesBot використовує інформацію з перевірених джерел, щоб надати вам найактуальнішу та точну інформацію про кожен серіал."
    )
    await message.answer(about_text)

# Меню для рекомендацій та пошуку
@dp.message_handler(text='Recommendations & Search')
async def cmd_recommendation(message: types.Message):
    await message.answer('Виберіть дію:', reply_markup=kb.recommendation_list)

# Меню для перегляду списку переглянутих серіалів
@dp.message_handler(text='Watched List')
async def cmd_watched(message: types.Message):
    await message.answer('Оберіть дію зі списком переглянутих серіалів:', reply_markup=kb.watched_commands_list)

# Меню для перегляду списку бажаних серіалів
@dp.message_handler(text='Watch Later')
async def cmd_wishlist(message: types.Message):
    await message.answer('Виберіть опцію для списку бажаних до перегляду серіалів:', reply_markup=kb.wishlist_commands_list)

# Обробка невідомих повідомлень
@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Вибачте, я не розумію вашого запиту.')

# Функція для створення клавіатури скасування
def cancel_keyboard(callback_data='cancel_popular'):
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Скасувати", callback_data=callback_data))

#Обробляє натискання кнопки "recommend"
@dp.callback_query_handler(lambda c: c.data == 'recommend')
async def handle_recommend(callback_query: types.CallbackQuery):
    await recommend(callback_query.message)  # Передаємо повідомлення з callback_query

    # Закриваємо Inline клавіатуру
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id)
    # Затримка в 5 секунди, щоб користувач побачив повідомлення з рекомендаціями
    await asyncio.sleep(5)
    # Видаляємо старе повідомлення з клавіатурою
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await callback_query.answer()

# Обробляє натискання кнопки "popular"
@dp.callback_query_handler(lambda c: c.data == 'popular')
async def handle_popular(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        "Скільки серіалів ви хочете отримати? (введіть число).\nНатисніть 'Скасувати', щоб вийти.",
        reply_markup=cancel_keyboard()
    )

    # Переміщаємо користувача в стан очікування
    await UserState.waiting_for_count.set()
    # Закриваємо Inline клавіатуру, видаляємо старе повідомлення з клавіатурою та ставимо затримку
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await asyncio.sleep(4)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    # Відповідаємо на callback_query, щоб прибрати індикацію натискання кнопки
    await callback_query.answer()

# Обробляє натискання кнопки 'Скасувати' для виходу з введення кількості серіалів
@dp.callback_query_handler(lambda c: c.data == 'cancel_popular', state=UserState.waiting_for_count)
async def cancel_popular(callback_query: types.CallbackQuery, state: FSMContext):
    # Завершуємо стан, щоб вийти з процесу введення кількості серіалів
    await state.finish()

    await callback_query.message.answer("Процес скасовано. Ви можете спробувати ще раз,"
                                        " натиснувши кнопку рекомендацій.")
    await callback_query.answer()


# Обробник натискання кнопки для пошуку
@dp.callback_query_handler(lambda c: c.data == 'search')
async def handle_search(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await SearchState.waiting_for_title.set()  # Увійти в стан очікування

    # Надсилаємо повідомлення з клавіатурою
    await callback_query.message.answer(
        "Введіть назву серіалу або натисніть 'Скасувати', щоб вийти.",
        reply_markup=cancel_keyboard()
    )

    # Очищуємо стару клавіатуру
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )

    # Плавна пауза для видалення старого повідомлення
    await asyncio.sleep(5)
    await bot.delete_message(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )

# Обробник скасування пошуку
@dp.callback_query_handler(lambda c: c.data == 'cancel_popular', state=SearchState.waiting_for_title)
async def cancel_search(callback_query: types.CallbackQuery, state: FSMContext):
    """Обробляє натискання кнопки 'Скасувати' для виходу з пошуку."""
    await state.finish()  # Завершуємо стан

    # Відповідаємо користувачу та очищуємо індикацію кнопки
    await callback_query.message.answer("Пошук скасовано. Ви можете спробувати ще раз, натиснувши кнопку пошуку.")
    await callback_query.answer()



@dp.callback_query_handler(lambda c: c.data == 'add_watched')
async def handle_add_watched(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    # Задаємо стан очікування введення серіалу
    await WatchState.waiting_for_series_name.set()
    cancel_kb = cancel_keyboard('cancel_add_watched')

    # Надсилаємо повідомлення з клавіатурою
    await callback_query.message.answer(
        "Введіть назву серіалу, щоб додати його до списку переглянутих. "
        "Натисніть 'Скасувати', щоб вийти.",
        reply_markup=cancel_kb
    )

    # Закриваємо Inline клавіатуру у початковому повідомленні
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'cancel_add_watched', state=WatchState.waiting_for_series_name)
async def cancel_add_watched(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.answer("Додавання серіалу скасовано. Ви можете повторити спробу в будь-який час.")
    await callback_query.answer()


# Обробник кнопки "remove_watched"
@dp.callback_query_handler(lambda c: c.data == 'remove_watched')
async def handle_remove_watched(callback_query: types.CallbackQuery):
    # Створюємо клавіатуру з кнопкою "Скасувати"
    cancel_markup = cancel_keyboard('cancel_remove_watched')

    # Відправляємо повідомлення з інструкцією та кнопкою "Скасувати"
    await callback_query.message.answer(
        "Ви обрали видалити серіал зі списку переглянутого.\n"
        "Введіть назву серіалу, який бажаєте видалити, або натисніть 'Скасувати', щоб вийти.",
        reply_markup=cancel_markup
    )

    # Задаємо стан очікування введення назви серіалу
    await RemoveState.waiting_for_series_name.set()

    # Закриваємо Inline клавіатуру
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )

    await callback_query.answer()

# Обробник кнопки "Скасувати" під час видалення серіалу
@dp.callback_query_handler(lambda c: c.data == 'cancel_remove_watched', state=RemoveState.waiting_for_series_name)
async def cancel_remove_watched(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.answer("Видалення серіалу зі списку переглянутого скасовано. Ви можете повторити спробу в будь-який час.")
    await callback_query.answer()


# Обробник кнопки "show_watched"
@dp.callback_query_handler(lambda c: c.data == 'show_watched')
async def handle_show_watched(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Отримуємо переглянуті серіали з бази даних
    watched_series = await get_watched_series(user_id)

    if watched_series:
        # Формуємо список серіалів
        formatted_list = "\n".join([f"○ {series}" for series in watched_series])
        response_text = f"📜 **Ваші переглянуті серіали:**\n\n{formatted_list}"
    else:
        response_text = "😔 Ви ще не додали жодного серіалу до списку переглянутого. Почніть з чогось цікавого!" # Якщо список порожній

    # Відправляємо відповідь користувачу
    await callback_query.message.answer(response_text, parse_mode="Markdown")

    # Закриваємо Inline клавіатуру
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
    )

    # Видаляємо повідомлення з клавіатурою через короткий час
    await asyncio.sleep(0.5)
    await bot.delete_message(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
    )

    await callback_query.answer()

# Обробник кнопки "clear_watched"
@dp.callback_query_handler(lambda c: c.data == 'clear_watched')
async def handle_clear_watched(callback_query: types.CallbackQuery):
    # Переходимо до стану підтвердження
    await ClearWatchedState.waiting_for_confirmation.set()
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Ви впевнені, що хочете очистити ваш список переглянутих серіалів? Відповідайте 'Так' або 'Ні'."
    )

# Обробник відповіді на підтвердження очищення списку переглянутих
@dp.message_handler(state=ClearWatchedState.waiting_for_confirmation)
async def process_clear_watched_confirmation(message: types.Message, state: FSMContext):
    user_response = message.text.lower()

    if user_response == 'так':
        # Очищаємо список переглянутих серіалів у базі даних
        user_id = message.from_user.id
        await clear_watched_series(user_id)

        # Відправляємо повідомлення з підтвердженням
        await message.answer(
            text="🗑️ Ваш список переглянутих серіалів успішно очищено.",
            parse_mode="Markdown"
        )
    elif user_response == 'ні':
        # Якщо користувач відповів 'ні', просто завершуємо стан
        await message.answer(
            text="Очистка списку переглянутих серіалів була скасована."
        )
    else:
        # Якщо відповідь не є 'так' чи 'ні', запитаємо знову
        await message.answer(
            text="Будь ласка, відповідайте 'Так' або 'Ні'."
        )

    # Завершуємо стан
    await state.finish()

# Обробник кнопки " handle_add_wishlist"
@dp.callback_query_handler(lambda c: c.data == 'add_wishlist', state="*")
async def handle_add_wishlist(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Відповідаємо користувачу
    await bot.send_message(
        chat_id=user_id,
        text="Обрано додати серіал до списку бажаного. Введіть назву серіалу:"
    )

    await Form.waiting_for_series_name.set()

    # Додаємо клавіатуру з кнопкою "Скасувати"
    await bot.send_message(
        chat_id=user_id,
        text="Щоб скасувати додавання, натисніть 'Скасувати'.",
        reply_markup=cancel_keyboard('cancel_add_wishlist')
    )

    # Закриваємо Inline клавіатуру повідомлення, яке ініціювало виклик
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id
    )

    # Видаляємо попереднє повідомлення з клавіатурою через короткий час
    await asyncio.sleep(0.5)
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

# Обробник кнопки "Скасувати" для додавання
@dp.callback_query_handler(lambda c: c.data == 'cancel_add_wishlist', state=Form.waiting_for_series_name)
async def cancel_add_wishlist(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.answer(
        "Додавання серіалу до списку бажаного скасовано. Ви можете повторити спробу в будь-який час."
    )
    await callback_query.answer()

# Обробник кнопки "handle_show_wishlist"
@dp.callback_query_handler(lambda c: c.data == 'show_wishlist')
async def handle_show_wishlist(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id, text='Обрано переглянути бажане')

    # Отримуємо список бажаних серіалів користувача
    user_id = callback_query.from_user.id
    wishlist_series = await get_wishlist_series(user_id)

    # Видаляємо дублікати зі списку за допомогою set()
    wishlist_series = list(set(wishlist_series))

    # Якщо є серіали у списку бажаних
    if wishlist_series:
        formatted_list = "\n".join([f"○ {series}" for series in wishlist_series])
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Серіали в списку вподобань:\n{formatted_list}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="😔 У вас немає жодного серіалу в списку вподобань.")

    # Закриваємо Inline клавіатуру
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id)

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await callback_query.answer()


# Кнопка "Скасувати"
cancel_button = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Скасувати", callback_data="cancel_remove_wishlist")
)

@dp.callback_query_handler(lambda c: c.data == 'remove_wishlist', state="*")
async def handle_remove_wishlist(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    await WishlistRemove.waiting_for_series_name.set()
    await bot.send_message(
        chat_id=user_id,
        text="Введіть назву серіалу, який ви хочете видалити зі списку бажаних:",
        reply_markup=cancel_button
    )

    # Закриваємо Inline клавіатуру
    try:
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    except Exception:
        pass  # Ігноруємо помилки, якщо повідомлення вже видалено

    await callback_query.answer()


# Обробник кнопки "Скасувати"
@dp.callback_query_handler(lambda c: c.data == 'cancel_remove_wishlist', state=WishlistRemove.waiting_for_series_name)
async def cancel_remove_wishlist(callback_query: types.CallbackQuery, state: FSMContext):

    # Завершуємо стан
    await state.finish()
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Видалення серіалу зі списку бажаних скасовано. Ви можете повторити спробу в будь-який час."
    )
    await callback_query.answer()


# Обробник кнопки "Перемістити до переглянутих"
@dp.callback_query_handler(lambda c: c.data == 'move_to_watched', state="*")
async def handle_move_to_watched(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await MoveToWatchedState.waiting_for_series_name.set()

    cancel_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Скасувати", callback_data='cancel_move_to_watched')
    )

    # Надсилаємо повідомлення з кнопкою скасування
    print("cancel_button callback_data:", cancel_button.inline_keyboard[0][0].callback_data)  # Перевірка значення callback_data
    await bot.send_message(
        chat_id=user_id,
        text="Введіть назву серіалу, який ви хочете перемістити до переглянутого:",
        reply_markup=cancel_button  # Додаємо кнопку "Скасувати"
    )

    # Закриваємо Inline клавіатуру в попередньому повідомленні
    try:
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    except Exception as e:
        print(f"Error while editing/deleting message: {e}")
    await callback_query.answer()

# Обробник кнопки "Скасувати" для переміщення серіалу до переглянутих
@dp.callback_query_handler(lambda c: c.data == 'cancel_move_to_watched', state=MoveToWatchedState.waiting_for_series_name)
async def cancel_move_to_watched(callback_query: types.CallbackQuery, state: FSMContext):

    await state.finish()
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Переміщення серіалу до списку переглянутих скасовано. Ви можете повторити спробу в будь-який час."
    )
    await callback_query.answer()

# Обробка натискання кнопки для очищення списку бажаних
@dp.callback_query_handler(lambda c: c.data == 'clear_wishlist', state="*")
async def handle_clear_wishlist(callback_query: types.CallbackQuery):
    # Переходимо до стану підтвердження
    await ClearWishlistState.waiting_for_confirmation.set()
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Ви впевнені, що хочете очистити ваш список бажаних серіалів? Відповідайте 'Так' або 'Ні'."
    )


#обробник клавіатури для вибору жанру (частина логіки recomend)
@dp.callback_query_handler(lambda c: c.data in GENRES)  # Обробка вибору жанру
async def handle_genre_selection(callback_query: types.CallbackQuery):
    """Обробляє вибір жанру та надає рекомендації."""
    try:
        genre = callback_query.data
        series = await get_series_by_genre(genre)  # Замініть на вашу асинхронну функцію для отримання серіалів

        if not series:
            await callback_query.message.edit_text("Не знайдено серіалів для цього жанру.")
            return

        random_series = random.sample(series, min(len(series), 3))  # Вибираємо 3 випадкові серіали
        recommendations = "\n\n".join([format_show_info(show) for show in random_series])

        # Відправляємо рекомендації
        await callback_query.message.edit_text(f"Ось кілька серіалів у жанрі {genre}:\n{recommendations}")
    except Exception as e:
        await callback_query.message.edit_text(f"Сталася помилка при обробці кнопки: {str(e)}")


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserState.waiting_for_count)
async def handle_invalid_count(message: types.Message):
    """Обробляє випадки, коли введене значення не є числом."""
    await message.answer("Будь ласка, введіть число, яке вказує кількість серіалів, які ви хочете отримати.")

@dp.message_handler(lambda message: message.text.isdigit(), state=UserState.waiting_for_count)
async def handle_count(message: types.Message, state: FSMContext):
    """Обробляє введення кількості серіалів."""
    # Перевірка, чи введене число
    count = int(message.text)

    # Перевірка на правильність введення числа
    if count <= 0 or count > 45:
        await message.answer('Будь ласка, введіть число від 1 до 45.')
        return  # повертаємось, щоб користувач міг ввести нове число

    # Задаємо API ключ і базову URL-адресу
    api_key = os.getenv('API_KEY')  # Ваш API ключ
    base_url = 'https://api.themoviedb.org/3/tv/popular'

    # Список для зберігання результатів
    total_shows = []

    # Нумерація сторінок для API
    page = 1
    try:
        async with httpx.AsyncClient() as client:
            while len(total_shows) < count:
                # Запит до API
                response = await client.get(f'{base_url}?api_key={api_key}&page={page}')
                response.raise_for_status()  # Перевірка на помилки запиту
                shows = response.json().get('results', [])

                # Фільтруємо серіали за рейтингом
                filtered_shows = [show for show in shows if show.get('vote_average', 0) > 7]
                total_shows.extend(filtered_shows)

                if not shows:  # Якщо більше немає серіалів
                    break

                page += 1

            # Відбираємо лише необхідну кількість серіалів
            total_shows = total_shows[:count]

            # Якщо серіалів не знайдено
            if not total_shows:
                await message.answer('На жаль, популярні серіали не знайдені.')
                return

            # Формуємо список серіалів для відправки
            popular_shows = f"Ось {len(total_shows)} популярних серіалів:\n\n"
            for i, show in enumerate(total_shows, start=1):
                name = show.get('name', 'Невідома назва')
                url = f"https://www.themoviedb.org/tv/{show.get('id')}"
                premiered = show.get('first_air_date', 'Невідома дата прем\'єри')
                rating = show.get('vote_average', 'Невідомий рейтинг')

                popular_shows += (
                    f"{i}. 📺 **{name}**\n"
                    f"🗓️ Дата прем'єри: {premiered}\n"
                    f"⭐️ Рейтинг: {rating}\n"
                    f"🔗 [Посилання на TMDb]({url})\n\n"
                )

            # Відправляємо повідомлення з результатами
            await message.answer(popular_shows, parse_mode='Markdown')

    except httpx.RequestError as e:
        await message.answer('Сталася помилка при отриманні популярних серіалів. Спробуйте ще раз.')
    except Exception as e:
        await message.answer(f'Сталася помилка: {str(e)}')

    # Завершуємо стан користувача
    await state.finish()



# Пошук за назвою
@dp.message_handler(state=SearchState.waiting_for_title)
async def search_series(message: Message, state: FSMContext):
    """Обробляє введення назви серіалу."""
    title = message.text.strip()

    # Перевірка на порожній текст
    if not title:
        await message.answer("Будь ласка, введіть назву серіалу.")
        return

    try:
        # Викликаємо функцію пошуку серіалу
        series_info = await get_series_by_title(title)

        if series_info:
            # Очищаємо опис, перекладаємо та форматуємо відповідь
            description = series_info.get('summary', 'Опис недоступний')
            cleaned_description = clean_html(description)
            translated_description = await translate_text(cleaned_description, target_lang='UK')
            image = series_info.get('image', {}).get('medium',
                                                     'https://via.placeholder.com/200')  # Зображення за замовчуванням
            rating = series_info.get('rating', {}).get('average', 'Невідомо')
            premiered = series_info.get('premiered', 'Невідомо')

            # Якщо опис надто великий (більше 850 символів), обрізаємо його
            if len(translated_description) > 850:
                truncated_description = translated_description[:850]  # Обрізаємо до 850 символів
                # Шукаємо найближчий кінець слова
                if " " in truncated_description:
                    truncated_description = truncated_description.rsplit(" ", 1)[
                        0]  # Знаходимо останнє слово та обрізаємо його
                truncated_description += "..."  # Додаємо три крапки
            else:
                # Якщо опис не перевищує ліміту, використовуємо його повністю
                truncated_description = translated_description

            # Відправляємо повідомлення з серіалом
            await message.answer_photo(
                photo=image,
                caption=(
                    f"📺 <b>{series_info['name']}</b>\n"
                    f"⭐ <b>Рейтинг:</b> {rating}\n"
                    f"📜 <b>Опис:</b> {truncated_description}\n"
                    f"📅 <b>Рік випуску:</b> {premiered}"
                ),
                parse_mode="HTML",
            )

            # Завершуємо стан після успішного пошуку
            await state.finish()
        else:
            # Якщо серіал не знайдений
            await message.answer("Не знайдено серіал за цією назвою. Будь ласка, спробуйте ввести іншу назву:")

    except Exception as e:
        # Обробка помилок
        await message.answer(f"Сталася помилка при пошуку: {e}")


@dp.message_handler(state=WatchState.waiting_for_series_name)
async def process_series_name(message: types.Message, state: FSMContext):
    """Обробляє введену назву серіалу і додає її до списку переглянутих."""

    series_name = message.text.strip()

    if not series_name:
        await message.reply("Будь ласка, введіть правильну назву серіалу.")
        return

    # Перевіряємо, чи існує серіал
    if not await series_exists(series_name):
        await message.reply(f"Серіал '{series_name}' не знайдено. Спробуйте іншу назву.")
        return

    user_id = message.from_user.id
    watched_series = await get_watched_series(user_id)

    if any(series_name.lower() == series.lower() for series in watched_series):
        await message.reply(f"Серіал '{series_name}' вже в списку переглянутого.")
        return

    # Додаємо серіал до переглянутого
    await add_watched_series(user_id, series_name)
    await message.reply(f"Серіал '{series_name}' додано до переглянутого.")

    # Завершуємо стан
    await state.finish()

@dp.message_handler(state=RemoveState.waiting_for_series_name)
async def process_remove_series_name(message: types.Message, state: FSMContext):
    """Обробляє введену назву серіалу для видалення зі списку переглянутого."""
    series_name = message.text.strip()
    user_id = message.from_user.id

    if not series_name:
        await message.reply("Будь ласка, введіть правильну назву серіалу.")
        return

    # Перевіряємо, чи серіал є в списку переглянутих
    watched_series = await get_watched_series(user_id)

    if any(series_name.lower() == series.lower() for series in watched_series):
        # Видаляємо серіал зі списку
        await remove_watched_series(user_id, series_name)
        await message.reply(f"Серіал '{series_name}' успішно видалено зі списку переглянутого.")
        # Завершуємо стан
        await state.finish()
    else:
        await message.reply(f"Серіал '{series_name}' не знайдено у вашому списку переглянутого. Спробуйте ще раз.")
        # Чекаємо на нову назву серіалу
        return


# Обробник введення серіалу
@dp.message_handler(state=Form.waiting_for_series_name)
async def process_series_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    series_name = message.text.strip()

    # Перевірка, чи вказано ім'я серіалу
    if not series_name:
        await message.reply("Будь ласка, вкажіть назву серіалу.")
        return

    # Перевіряємо, чи існує серіал через API (ви можете замінити на свою перевірку)
    if not await series_exists(series_name):
        await message.reply(f"Серіал '{series_name}' не знайдено. Спробуйте іншу назву.")
        return

    # Перевіряємо чи серіал вже є у списку переглянутих
    watched_series = await get_watched_series(user_id)
    if series_name.lower() in [series.lower() for series in watched_series]:
        await message.reply(f"Серіал '{series_name}' вже є у списку переглянутих. Його не можна додати до списку бажаних.")
        return

    # Перевіряємо чи серіал вже є в списку бажаних
    wishlist_series = await get_wishlist_series(user_id)
    if series_name.lower() in [series.lower() for series in wishlist_series]:
        await message.reply(f"Серіал '{series_name}' вже є у списку бажаних.")
        return

    # Додаємо серіал до списку бажаних
    await add_wishlist_series(user_id, series_name)
    await message.reply(f"Серіал '{series_name}' додано до списку бажаних.")

    # Завершуємо стан
    await state.finish()

# Обробка введення серіалу для видалення
@dp.message_handler(state=WishlistRemove.waiting_for_series_name)
async def process_remove_wishlist_series(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    series_name = message.text.strip()

    # Перевірка, чи вказано ім'я серіалу
    if not series_name:
        await message.reply("Будь ласка, вкажіть назву серіалу.")
        return

    # Перевірка, чи серіал є у списку бажаних
    wishlist_series = await get_wishlist_series(user_id)
    if series_name.lower() not in [series.lower() for series in wishlist_series]:
        # Якщо серіал не знайдений у списку бажаних
        await message.reply(f"Серіал '{series_name}' не знайдений у вашому списку бажаних. Спробуйте іншу назву.")
        return  # Залишаємо стан активним для нової спроби

    # Видалення серіалу зі списку бажаних
    await remove_wishlist_series(user_id, series_name)
    await message.reply(f"Серіал '{series_name}' видалено зі списку бажаних.")

    # Завершуємо стан після успішного видалення
    await state.finish()

# Обробка введення серіалу для переміщення
@dp.message_handler(state=MoveToWatchedState.waiting_for_series_name)
async def process_move_to_watched_series(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    series_name = message.text.strip()

    # Перевірка, чи вказано ім'я серіалу
    if not series_name:
        await message.reply("Будь ласка, вкажіть назву серіалу.")
        return

    # Перевірка, чи серіал є у списку бажаних
    wishlist_series = await get_wishlist_series(user_id)
    if series_name.lower() not in [series.lower() for series in wishlist_series]:
        await message.reply(f"Серіал '{series_name}' не знайдений у вашому списку бажаних.Спробуйте іншу назву")
        return

    # Переміщаємо серіал до переглянутих
    await move_to_watched(user_id, series_name)
    await message.reply(f"Серіал '{series_name}' переміщено до переглянутого.")

    # Завершуємо стан після успішного переміщення
    await state.finish()

# Обробка підтвердження очищення
@dp.message_handler(state=ClearWishlistState.waiting_for_confirmation)
async def process_clear_wishlist_confirmation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    confirmation = message.text.strip().lower()

    if confirmation in ['так', 'yes']:
        # Очищення списку
        await clear_wishlist_series(user_id)
        await message.reply("Ваш список серіалів, які бажаєте переглянути, успішно очищено.")
        await state.finish()
    elif confirmation in ['ні', 'no']:
        await message.reply("Очищення скасовано.")
        await state.finish()
    else:
        await message.reply("Будь ласка, відповідайте лише 'Так' або 'Ні'.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)