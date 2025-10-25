from aiogram import executor, types
from django.core.management import BaseCommand

from core.apps.bot.handlers import default_handlers_register, catalog_handlers_register, authorization_handlers_register
from core.apps.bot.keyboards import default_kb
from core.apps.bot.loader import dp


async def on_startup(_):
    print("Bot muvaffaqiyatli ishga tushdi!")


class Command(BaseCommand):

    def handle(self, *args, **options):
        default_handlers_register()
        catalog_handlers_register()
        authorization_handlers_register()

        @dp.message_handler(commands=None, regexp=None)
        async def unknown_text(message: types.Message):
            await message.answer("Buyruq topilmadi ☹️\n\n"
                                 "Iltimos, yordam olish uchun Yordam ⭐️ tugmasini bosing",
                                 reply_markup=default_kb.only_help_markup,
                                 )

        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)