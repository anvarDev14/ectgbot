from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btn_1 = KeyboardButton("Ro'yxatdan o'tish ✌️")
btn_2 = KeyboardButton('Kirish 👋')
btn_3 = KeyboardButton('Parolni unutdingizmi? 🆘')
markup.add(btn_1).insert(btn_2).add(btn_3)