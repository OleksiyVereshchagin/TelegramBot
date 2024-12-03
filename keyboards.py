from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Головне меню
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Help').add('About').add('Recommendations & Search').add('Watched List').add('Watch Later')

# Меню рекомендацій
recommendation_list = InlineKeyboardMarkup(row_width=2)
recommendation_list.add(InlineKeyboardButton('Get Recommendations', callback_data='recommend'),
                        InlineKeyboardButton('Popular Series', callback_data='popular'),
                        InlineKeyboardButton('Search', callback_data='search'))

# Меню для переглянутих серіалів
watched_commands_list = InlineKeyboardMarkup(row_width=2)
watched_commands_list.add(InlineKeyboardButton('Add to Watched List', callback_data='add_watched'),
                          InlineKeyboardButton('Show Watched List', callback_data='show_watched'),
                          InlineKeyboardButton('Remove Series', callback_data='remove_watched'),
                          InlineKeyboardButton('Clear Watched List', callback_data='clear_watched'))

# Меню для бажаних серіалів
wishlist_commands_list = InlineKeyboardMarkup(row_width=2)
wishlist_commands_list.add(InlineKeyboardButton('Add to Watch Later', callback_data='add_wishlist'),
                           InlineKeyboardButton('Show Watch Later', callback_data='show_wishlist'),
                           InlineKeyboardButton('Remove Series', callback_data='remove_wishlist'),
                           InlineKeyboardButton('Move to Watched List', callback_data='move_to_watched'),
                           InlineKeyboardButton('Clear Watch Later', callback_data='clear_wishlist'))