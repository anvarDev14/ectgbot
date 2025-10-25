import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password, check_password

from core.apps.bot.keyboards import default_kb
from core.apps.bot.keyboards import sign_inup_kb
from core.apps.bot.keyboards.registration_kb import markup, markup_cancel_forgot_password
from core.apps.bot.loader import dp
from core.apps.bot.models import TelegramUser
from core.apps.bot.states import AuthState, SignInState, ForgotPasswordState

new_user = {}
sign_in = {'current_state': False}
update_data = {}

REGISTRATION_TEXT = """
Ro'yxatdan o'tish uchun avval foydalanuvchi nomingizni yozing!

Foydalanuvchi nomi nimalardan iborat bo'lishi kerak?
    - Foydalanuvchi nomi faqat <b>lotin harflaridan</b> iborat bo'lishi kerak!
    - Foydalanuvchi nomi <b>3 ta belgidan ko'p (harf va raqamlar)</b> bo'lishi kerak
    - Foydalanuvchi nomi <b>noyob va takrorlanmaydigan</b> bo'lishi kerak

Foydalanuvchi nomini yuborishdan oldin uni qaytadan tekshiring!
"""


async def command_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(text="Amal muvaffaqiyatli bekor qilindi 🙅‍", reply_markup=sign_inup_kb.markup)


async def process_registration(message: types.Message):
    await message.answer(REGISTRATION_TEXT, reply_markup=markup)
    await AuthState.user_login.set()


async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    if not await check_users_chat_id(chat_id=message.chat.id):
        if not await check_user(login=login):
            if re.match('^[A-Za-z]+$', login) and len(login) > 3:
                async with state.proxy() as data:
                    data['login'] = login
                    new_user['user_login'] = data['login']
                await message.answer("Endi iltimos parolingizni kiriting ✍️", reply_markup=markup)
                await AuthState.user_password.set()
            else:
                await message.answer(
                    "Foydalanuvchi nomi faqat <b>lotin harflaridan iborat bo'lishi va 3 ta belgidan ko'p bo'lishi kerak 🔡</b>\n\n"
                    "Iltimos qaytadan urinib ko'ring ↩️!",
                    reply_markup=markup,
                )
                await AuthState.user_login.set()
        else:
            await message.answer(
                "Bu foydalanuvchi nomi bilan foydalanuvchi <b>allaqachon mavjud</b>, iltimos qaytadan urinib ko'ring ↩️",
                reply_markup=markup,
            )
            await AuthState.user_login.set()
    else:
        await message.answer(
            "Sizning ID'ingiz bilan bir xil foydalanuvchi allaqachon mavjud, iltimos hisobingizga kiring 🫡",
            reply_markup=sign_inup_kb.markup,
        )


async def process_password(message: types.Message, state: FSMContext):
    if len(message.text) > 5 and re.match('^[a-zA-Z0-9]+$', message.text) and \
            any(digit.isdigit() for digit in message.text):
        async with state.proxy() as data:
            data['password'] = message.text
        await message.answer("Iltimos parolni <b>qaytadan</b> kiriting 🔄", reply_markup=markup)
        await AuthState.user_password_2.set()
    else:
        await message.answer(
            "Parol faqat <b>lotin harflaridan</b> iborat bo'lishi "
            "va kamida <b>bitta raqam</b> bo'lishi kerak\n\n"
            "Iltimos qaytadan urinib ko'ring 🔄",
            reply_markup=markup,
        )
        await AuthState.user_password.set()


async def process_password_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password_2'] = message.text
        new_user['user_password'] = data['password_2']
        if data['password'] == data['password_2']:
            new_user['chat_id'] = message.chat.id
            await save_user()
            await state.finish()
            await message.answer(
                "Ro'yxatdan o'tish <b>muvaffaqiyatli</b> amalga oshirildi ✅\n\n"
                "Endi iltimos profilingizga kiring 💝",
                reply_markup=sign_inup_kb.markup,
            )
        else:
            await message.answer(
                "Siz parolni <b>noto'g'ri</b> kiritdingiz ❌\n\n"
                "Iltimos qaytadan urinib ko'ring 🔄",
                reply_markup=markup,
            )
            await AuthState.user_password.set()


async def command_sign_in(message: types.Message):
    await message.answer("Iltimos foydalanuvchi nomingizni kiriting ✨", reply_markup=markup)
    await SignInState.login.set()


async def process_sign_in(message: types.Message, state: FSMContext):
    if await check_user(message.text):
        async with state.proxy() as sign_in_data:
            sign_in_data['login'] = message.text
            sign_in['login'] = sign_in_data['login']
        await message.answer("Endi parolingizni kiritishingiz kerak 🔐", reply_markup=markup_cancel_forgot_password)
        await SignInState.password.set()
    else:
        await message.answer("Bu foydalanuvchi nomi <b>mavjud emas</b>, iltimos qaytadan urinib ko'ring ❌", reply_markup=markup)
        await SignInState.login.set()


async def process_pass(message: types.Message, state: FSMContext):
    async with state.proxy() as sign_in_data:
        sign_in_data['password'] = message.text
        sign_in['password'] = sign_in_data['password']
        sign_in['current_state'] = True
        if await get_password(username=sign_in['login'], password=sign_in['password']):
            await message.answer("Kirish <b>muvaffaqiyatli</b> amalga oshirildi ⭐️", reply_markup=default_kb.markup)
            await state.finish()
        else:
            await message.answer(
                "Parol <b>noto'g'ri</b>, iltimos qaytadan urinib ko'ring 🔄",
                reply_markup=markup_cancel_forgot_password,
            )
            await SignInState.password.set()


async def forgot_password(message: types.Message):
    await message.answer("Parolni o'zgartirish uchun avval foydalanuvchi nomingizni kiriting 🫡", reply_markup=markup)
    await ForgotPasswordState.user_login.set()


async def process_forgot_password_login(message: types.Message, state: FSMContext):
    if await check_login_chat_id(login=message.text, chat_id=message.chat.id):
        await message.answer(
            "Foydalanuvchi nomi <b>muvaffaqiyatli</b> topildi, "
            "va foydalanuvchi ID'si foydalanuvchi nomi bilan mos keladi 🌟\n\n"
            "Endi siz parolingizni <b>o'zgartirishingiz mumkin</b> ✅\n\n"
            "Iltimos <b>yangi parolingizni</b> kiriting ✍️",
            reply_markup=markup,
        )
        update_data['user_login'] = message.text
        await ForgotPasswordState.user_password.set()
    else:
        await message.answer(
            "Siz tekshiruvdan <b>o'tmadingiz</b> ❌\n\n"
            "Buning ikki sababi bo'lishi mumkin:\n"
            "1. Bu foydalanuvchi nomi mavjud emas\n"
            "2. Sizning foydalanuvchi ID'ingiz siz ko'rsatgan foydalanuvchi nomi bilan mos kelmaydi\n\n"
            "Siz <b>qaytadan urinib ko'rishingiz</b> mumkin 🔄",
            reply_markup=sign_inup_kb.markup,
        )
        await state.finish()


async def process_forgot_password_password(message: types.Message, state: FSMContext):
    if len(message.text) > 5 and re.match('^[a-zA-Z0-9]+$', message.text) and \
            any(digit.isdigit() for digit in message.text):
        async with state.proxy() as forgot_password_data:
            forgot_password_data['user_password'] = message.text
            update_data['user_password'] = forgot_password_data['user_password']
        await message.answer("Iltimos parolni <b>qaytadan</b> kiriting 🔄", reply_markup=markup)
        await ForgotPasswordState.user_password_2.set()
    else:
        await message.answer(
            "Parol faqat <b>lotin harflaridan</b> iborat bo'lishi "
            "va kamida <b>bitta raqam</b> bo'lishi kerak\n\n"
            "Iltimos qaytadan urinib ko'ring 🔄",
            reply_markup=markup,
        )
        await ForgotPasswordState.user_password.set()


async def process_forgot_password_password_2(message: types.Message, state: FSMContext):
    async with state.proxy() as forgot_password_data:
        forgot_password_data['user_password_2'] = message.text
        update_data['user_password'] = forgot_password_data['user_password_2']
        if forgot_password_data['user_password'] == forgot_password_data['user_password_2']:
            await update_user_password(login=update_data['user_login'], password=update_data['user_password'])
            await state.finish()
            await message.answer(
                "Parolni o'zgartirish <b>muvaffaqiyatli</b> amalga oshirildi ✅\n\n"
                "Endi iltimos profilingizga kiring 💝",
                reply_markup=sign_inup_kb.markup,
            )
        else:
            await message.answer(
                "Siz parolni <b>noto'g'ri</b> kiritdingiz ❌\n\n"
                "Iltimos qaytadan urinib ko'ring 🔄",
                reply_markup=markup,
            )
            await ForgotPasswordState.user_password.set()


@sync_to_async
def save_user():
    user = TelegramUser.objects.create(
        user_login=new_user['user_login'],
        user_password=make_password(new_user['user_password']),
        is_registered=True,
        chat_id=new_user['chat_id'],
    )
    return user


@sync_to_async
def update_user_password(login, password):
    user = TelegramUser.objects.filter(user_login=login).update(user_password=make_password(password))
    return user


@sync_to_async
def get_password(username, password):
    user = TelegramUser.objects.get(user_login=username)
    if check_password(password, user.user_password):
        return True
    else:
        return False


@sync_to_async
def check_user(login):
    return TelegramUser.objects.filter(user_login=login).exists()


@sync_to_async
def check_login_chat_id(login, chat_id):
    return TelegramUser.objects.filter(user_login=login, chat_id=chat_id).exists()


@sync_to_async
def check_users_chat_id(chat_id):
    return TelegramUser.objects.filter(chat_id=chat_id).exists()


def authorization_handlers_register():
    dp.register_message_handler(command_cancel, Text(equals='Bekor qilish ❌', ignore_case=True), state='*')
    dp.register_message_handler(process_registration, Text(equals="Ro'yxatdan o'tish ✌️"), state='*')
    dp.register_message_handler(process_login, state=AuthState.user_login)
    dp.register_message_handler(process_password, state=AuthState.user_password)
    dp.register_message_handler(process_password_2, state=AuthState.user_password_2)
    dp.register_message_handler(forgot_password, Text(equals='Parolni unutdingizmi? 🆘'), state='*')
    dp.register_message_handler(process_forgot_password_login, state=ForgotPasswordState.user_login)
    dp.register_message_handler(process_forgot_password_password, state=ForgotPasswordState.user_password)
    dp.register_message_handler(process_forgot_password_password_2, state=ForgotPasswordState.user_password_2)
    dp.register_message_handler(command_sign_in, Text(equals='Kirish 👋'))
    dp.register_message_handler(process_sign_in, state=SignInState.login)
    dp.register_message_handler(process_pass, state=SignInState.password)