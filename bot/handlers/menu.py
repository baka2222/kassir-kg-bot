from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from aiogram import F
from database.repository import get_user_language, edit_user, get_user_by_tg_id
from languages import languages


menu_router = Router()


@menu_router.message(F.text.in_({'Menu', 'Меню', 'Menyu'}))
async def menu_handler(message: Message):
    current_user = await get_user_by_tg_id(tg_id=message.from_user.id)

    if not current_user:
        await message.answer(languages['ru']['user_not_found'], show_alert=True)
        return
    
    lang = current_user.language

    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=languages[lang]['support'], callback_data='support')],
            [InlineKeyboardButton(text=languages[lang]['language_change'], callback_data='language_change')]
        ]
    )
    await message.answer(languages[lang]['menu_activate'], reply_markup=ikb)


@menu_router.callback_query(F.data == 'language_change')
async def language_change_handler(callback_query: CallbackQuery):
    lang = await get_user_language(callback_query)
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=languages[lang]['lang_russian'], callback_data='lang_ru')],
            [InlineKeyboardButton(text=languages[lang]['lang_english'], callback_data='lang_en')],
            [InlineKeyboardButton(text=languages[lang]['lang_kyrgyz'], callback_data='lang_ky')]
        ]
    )
    
    await callback_query.message.edit_text(languages[lang]['language_change_activate'], reply_markup=ikb)
    await callback_query.answer()


@menu_router.callback_query(F.data.in_({'lang_ru', 'lang_en', 'lang_ky'}))
async def set_language_handler(callback_query: CallbackQuery):
    lang_code = callback_query.data.split('_')[1]
    current_user = await get_user_by_tg_id(tg_id=callback_query.from_user.id)

    if not current_user:
        await callback_query.answer(languages[lang_code]['user_not_found'], show_alert=True)
        return
    
    menu_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=languages[lang_code]['menu'])]
            ],
            resize_keyboard=True
        )

    await edit_user(User=current_user, language=lang_code)
    await callback_query.message.delete()
    await callback_query.message.answer(
        languages[lang_code]['language_set'],
        reply_markup=menu_kb
    )
    await callback_query.answer()
