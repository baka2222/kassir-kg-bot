from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from database.repository import get_user_language
from languages import languages


social_router = Router()


@social_router.callback_query(F.data == 'social')
async def social_handler(callback_query: CallbackQuery):
    lang = await get_user_language(callback_query)

    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='ShowGo', url='https://showgo.uz')],
            [InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/showgo.uz?igsh=bXgyN200aHQ4NTd2')],
            [InlineKeyboardButton(text='Telegram', url='https://t.me/showgouz_official')]
        ]
    )

    await callback_query.message.answer(
        f"{languages[lang]['give_social']} 🌐",
        reply_markup=ikb
    ) 
    await callback_query.answer()