from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

GENRES = ['Action', 'Adventure', 'Anime', 'Comedy', 'Crime',
          'Drama', 'Espionage', 'Family', 'Fantasy', 'History', 'Horror', 'Legal',
          'Medical', 'Music', 'Mystery', 'Romance', 'Science-Fiction', 'Sports',
          'Supernatural', 'Thriller', 'War', 'Western']

def format_show_info(show):
    """Форматує інформацію про серіал для відображення."""
    title = show.get('name', 'Невідома назва')
    genres = ", ".join(show.get('genres', ['Невідомий жанр']))
    premiered = show.get('premiered', 'Невідома дата')
    network = show.get('network', {}).get('name', 'Невідома студія')
    url = show.get('url', '#')

    return (f"🔍 {title}\n"
            f"🎬 Жанри: {genres}\n"
            f"📅 Дата прем'єри: {premiered}\n"
            f"🎥 Студія: {network}\n"
            f"🔗 Посилання: {url}")

async def recommend(message: Message):
    """Запитує у користувача вибір жанру для рекомендацій серіалів."""
    try:
        keyboard = []
        # Розбиваємо жанри на рядки по 2 кнопки
        for i in range(0, len(GENRES), 2):
            row = [
                InlineKeyboardButton(genre, callback_data=genre)
                for genre in GENRES[i:i + 2]
            ]
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        # Відправляємо повідомлення з кнопками
        await message.answer('Будь ласка, виберіть жанр:', reply_markup=reply_markup)
        print("Клавіатура відправлена успішно.")
    except Exception as e:
        print(f"Помилка при виконанні recommend: {e}")