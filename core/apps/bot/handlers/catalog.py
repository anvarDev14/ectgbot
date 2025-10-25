from aiogram import types
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async

from core.apps.bot.handlers.authorization import sign_in
from core.apps.bot.keyboards import sign_inup_kb
from core.apps.bot.keyboards.catalog_ikb import get_categories, get_subcategories, category_cb, subcategory_cb
from core.apps.bot.keyboards.default_kb import markup
from core.apps.bot.loader import bot, dp
from core.apps.bot.models import Product, SubCategory, Category


async def show_categories(message: types.Message):
    if sign_in['current_state']:
        if await category_exists():
            await bot.send_message(
                chat_id=message.chat.id, text="Iltimos ro'yxatdan kategoriya tanlang 📂",
                reply_markup=await get_categories(),
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id, text="Afsuski, administrator hali hech qanday kategoriya qo'shmagan ☹️",
                reply_markup=markup,
            )
    else:
        await message.answer(
            "Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


async def get_products(query):
    elem = query.data.split(':')
    if await subcategory_products_exists(product_subcategory_id=elem[1]):
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="Mana bu subkategoriyada mavjud mahsulotlar ro'yxati 👇",
        )
        async for product in Product.objects.filter(product_subcategory_id=elem[1]):
            photo_id = product.photo.open('rb').read()
            text = f"Mahsulot 🚀: {product.name}\n\n" \
                   f"Ta'rif 💬: {product.description}\n\n" \
                   f"Narx 💰: {product.price} USD"
            await bot.send_photo(chat_id=query.message.chat.id, photo=photo_id, caption=text)
    else:
        await bot.send_message(
            query.message.chat.id,
            text="Afsuski, bu subkategoriyada hech qanday mahsulot yo'q 🙁",
            reply_markup=markup,
        )


async def show_subcategories(query: types.CallbackQuery):
    if sign_in['current_state']:
        elem = query.data.split(':')
        if await category_subcategory_exists(subcategory_category_id=elem[1]):
            await query.answer(text="Subkategoriyalar")
            await bot.send_message(
                chat_id=query.message.chat.id,
                text="Iltimos ro'yxatdan subkategoriya tanlang ☺️",
                reply_markup=await get_subcategories(elem[1]),
            )
        else:
            await bot.send_message(
                chat_id=query.message.chat.id,
                text="Kechirasiz, bu kategoriyada hech qanday mahsulot yo'q 😔",
                reply_markup=markup,
            )
    else:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


async def show_products(query: types.CallbackQuery):
    if sign_in['current_state']:
        await query.answer("Mahsulotlar katalogi")
        await get_products(query)
    else:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="Siz tizimga kirmagansiz, iltimos profilingizga kirishga harakat qiling ‼️",
            reply_markup=sign_inup_kb.markup,
        )


@sync_to_async
def subcategory_products_exists(product_subcategory_id):
    return Product.objects.filter(product_subcategory=product_subcategory_id).exists()


@sync_to_async
def category_subcategory_exists(subcategory_category_id):
    return SubCategory.objects.filter(subcategory_category_id=subcategory_category_id).exists()


@sync_to_async
def category_exists():
    return Category.objects.all().exists()


def catalog_handlers_register():
    dp.register_message_handler(show_categories, Text(equals='Katalog 🛒'))
    dp.register_callback_query_handler(show_subcategories, category_cb.filter(action='view_categories'))
    dp.register_callback_query_handler(show_products, subcategory_cb.filter(action='view_subcategories'))