from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(resize_keyboard=True)
btn_1 = KeyboardButton("Bosh sahifa 🏠")
btn_2 = KeyboardButton("Yordam 🔔")
markup.add(btn_1).add(btn_2)