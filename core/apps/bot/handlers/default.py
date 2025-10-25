from aiogram import types
from aiogram.dispatcher.filters import Text
from django.conf import settings
from random import randrange

from core.apps.bot.handlers.authorization import sign_in
from core.apps.bot.keyboards import admin_kb, default_kb
from core.apps.bot.keyboards import sign_inup_kb
from core.apps.bot.loader import bot, dp
from core.apps.bot.models import TelegramUser

HELP_TEXT = """
Assalomu alaykum 👋, men turli xil mahsulotlarni sotish uchun botman! Bizda quyidagi buyruqlar mavjud:

<b>Yordam ⭐️</b> - bot buyruqlari bo'yicha yordam
<b>Ma'lumot 📌</b> - manzil, aloqa ma'lumotlari, ish vaqti
<b>Katalog 🛒</b> - siz sotib olishingiz mumkin bo'lgan mahsulotlar ro'yxati
<b>Admin 👑</b> - administrator menyusi

Ammo boshlashdan oldin, siz <b>ro'yxatdan o'tishingiz yoki</b> profilingizga kirishingiz kerak. 
<b>Ro'yxatdan o'tish ✌️</b> yoki <b>Kirish 👋</b> buyrug'ini bosing.
Agar buni qilmasangiz, ba'zi buyruqlar <b>mavjud bo'lmaydi</b> 🔴

Ushbu botdan foydalanganingizdan xursandmiz ❤️
"""


async def cmd_start(message: types.Message):
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Assalomu alaykum ✋, men turli xil mahsulotlarni sotish uchun botman!\n\n" \
                 "Bu yerda siz xohlagan narsangizni sotib olishingiz mumkin. Menda mavjud " \
                 "mahsulotlar ro'yxatini ko'rish uchun quyida 'Katalog 🛒' buyrug'ini bosing.\n\n" \
                 "Ammo avval <b>siz ro'yxatdan o'tishingiz kerak</b>, " \
                 "aks holda boshqa buyruqlar mavjud bo'lmaydi!\n\n" \
                 "<b>Ro'yxatdan o'tish ✌️</b> yoki <b>Kirish 👋</b> buyrug'ini bosing.",
            reply_markup=sign_inup_kb.markup,
        )
    except:
        await message.reply(
            text="Bot bilan muloqot qilish uchun, "
                 "menga to'g'ridan-to'g'ri xabar yuborishingiz mumkin: "
                 "https://t.me/yourbot",
        )


async def cmd_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=HELP_TEXT, reply_markup=default_kb.markup)


async def cmd_description(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Assalomu alaykum ✋, biz turli xil mahsulotlarni sotadigan kompaniyamiz! "
             "Xizmatimizdan foydalanganingizdan juda xursandmiz ❤️. Biz dushanbadan "
             "jumaga qadar ishlaymiz.\n9:00 dan 21:00 gacha",
    )
    await bot.send_location(
        chat_id=message.chat.id,
        latitude=randrange(1, 100),
        longitude=randrange(1, 100),
    )


async def send_all(message: types.Message):
    if sign_in['current_state']:
        if message.chat.id == settings.ADMIN_ID:
            await message.answer(f"Xabar: <b>{message.text[message.text.find(' '):]}</b> barcha foydalanuvchilarga yuborilmoqda!")
            async for user in TelegramUser.objects.filter(is_registered=True):
                await bot.send_message(chat_id=user.chat_id, text=message.text[message.text.find(' '):])
            await message.answer("Hammaga muvaffaqiyatli yuborildi!")
        else:
            await message.answer("Siz administrator emassiz va xabar yuborolmaysiz!")
    else:
        await message.answer(
            "Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


async def cmd_admin(message: types.Message):
    if sign_in['current_state']:
        if message.chat.id == settings.ADMIN_ID:
            await message.answer(
                "Siz administrator menyusiga kirdingiz 🤴\n\n"
                "Quyida sizga mavjud buyruqlar 💭",
                reply_markup=admin_kb.markup,
            )
        else:
            await message.answer("Siz administrator emassiz va xabar yuborolmaysiz!")
    else:
        await message.answer(
            "Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


async def cmd_home(message: types.Message):
    if sign_in['current_state']:
        if message.chat.id == settings.ADMIN_ID:
            await message.answer("Siz bosh menyuga kirdingiz 🤴", reply_markup=default_kb.markup)
        else:
            await message.answer("Siz administrator emassiz va xabar yuborolmaysiz!")
    else:
        await message.answer(
            "Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


HELP_ADMIN_TEXT = '''
Assalomu alaykum Administrator 🙋\n\n
Hozirda sizda quyidagi buyruqlar mavjud:
- <b>Xabar yuborish:</b> - bu buyruq yordamida siz ushbu botning barcha foydalanuvchilariga xabar yuborishingiz mumkin.
Foydalanish misoli: Xabar yuborish: 'XABAR MATNI'
'''


async def cmd_help_admin(message: types.Message):
    if sign_in['current_state']:
        if message.chat.id == settings.ADMIN_ID:
            await message.answer(text=HELP_ADMIN_TEXT, reply_markup=admin_kb.markup)
        else:
            await message.answer("Siz administrator emassiz va xabar yuborolmaysiz!")
    else:
        await message.answer(
            "Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


def default_handlers_register():
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_help, Text(equals='Yordam ⭐️'))
    dp.register_message_handler(cmd_description, Text(equals="Ma'lumot 📌"))
    dp.register_message_handler(send_all, Text(contains='Xabar yuborish:'))
    dp.register_message_handler(cmd_admin, Text(equals='Admin 👑'))
    dp.register_message_handler(cmd_home, Text(equals='Bosh sahifa 🏠'))
    dp.register_message_handler(cmd_help_admin, Text(equals='Yordam 🔔'))