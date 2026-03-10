from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram.filters import Command
from languages import languages
from database.repository import create_user, get_user_by_tg_id, get_user_by_phone, get_user_language, edit_user


authorization_router = Router()


def _normalize_lang_code(code: str | None) -> str:
    if not code:
        return 'ru'
    code = code.lower()
    if code.startswith('en'):
        return 'en'
    if code.startswith('ky') or code.startswith('uz'):
        return 'ky'
    return 'ru'


@authorization_router.message(Command('start'))
async def start_command_handler(message: Message):
    existing_user = await get_user_by_tg_id(tg_id=message.from_user.id)

    if existing_user:
        lang = existing_user.language
    else:
        lang = _normalize_lang_code('ru')
        await create_user(
            tg_id=message.from_user.id,
            language=lang,
            name=message.from_user.full_name
        )
        existing_user = await get_user_by_tg_id(tg_id=message.from_user.id)

    await message.answer_sticker('CAACAgIAAxkBAAEQqd9ppqYGgpxhWK2uuQ7L3S5d1zqDvAACAQEAAladvQoivp8OuMLmNDoE')

    main_menu_ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🛠️ {languages[lang]['support']}", callback_data='support')],
            [InlineKeyboardButton(text=f"🌐 {languages[lang]['language_change']}", callback_data='language_change')],
            [InlineKeyboardButton(text=f"📢 {languages[lang]['social']}", callback_data='social')]
        ]
    )

    reply_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=languages[lang]['menu'])]],
        resize_keyboard=True
    )

    await message.answer(
        f"🌟 <b>{languages[lang]['welcome']}, {existing_user.name or languages[lang]['friend']}!</b>\n"
        f"{languages[lang]['menu_activate']}",
        reply_markup=main_menu_ikb,
        parse_mode='HTML'
    )
    await message.answer(languages[lang]['menu_tip'], reply_markup=reply_kb)


# NOTE: номера теперь не запрашиваем, поэтому состояние не используется
# async def phone_state_handler(message: Message, state: FSMContext):
#     lang = await get_user_language(message) or 'ru'

#     if message.text and message.text.strip() == languages[lang]['skip_phone']:
#         tg_id = message.from_user.id
#         name = message.from_user.full_name

#         existing_user = await get_user_by_tg_id(tg_id=tg_id)
#         if existing_user:
#             updates = {}
#             if (existing_user.name or '') != name:
#                 updates['name'] = name
#             if updates:
#                 await edit_user(User=existing_user, **updates)
#         else:
#             await create_user(
#                 tg_id=tg_id,
#                 language=lang,
#                 name=name
#             )

#         menu_kb = ReplyKeyboardMarkup(
#             keyboard=[
#                 [KeyboardButton(text=languages[lang]['menu'])]
#             ],
#             resize_keyboard=True
#         )
#         await message.answer(languages[lang]['thanks_for_phone'], reply_markup=menu_kb)
#         ikb = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text=languages[lang]['support'], callback_data='support')],
#                 [InlineKeyboardButton(text=languages[lang]['language_change'], callback_data='language_change')]
#             ]
#         )
#         await message.answer(languages[lang]['menu_activate'], reply_markup=ikb)
#         await state.clear()
#         return

#     if not message.contact:
#         await message.answer(languages[lang]['send_contact_please'])
#         return

#     if message.contact.user_id != message.from_user.id:
#         await message.answer(languages[lang]['wrong_contact'])
#         return

#     phone = message.contact.phone_number
#     phone_clean = phone.replace('+', '')
#     tg_id = message.from_user.id
#     name = message.from_user.full_name

#     try:
#         user_by_tg = await get_user_by_tg_id(tg_id=tg_id)
#         user_by_phone = await get_user_by_phone(phone=phone_clean)

#         if user_by_tg:
#             updates = {}
#             if (user_by_tg.phone or '') != phone_clean:
#                 updates['phone'] = phone_clean
#             if (user_by_tg.name or '') != name:
#                 updates['name'] = name
#             if updates:
#                 await edit_user(User=user_by_tg, **updates)
#         else:
#             if user_by_phone:
#                 updates = {}
#                 if user_by_phone.tg_id != tg_id:
#                     updates['tg_id'] = tg_id
#                 if (user_by_phone.name or '') != name:
#                     updates['name'] = name
#                 if updates:
#                     await edit_user(User=user_by_phone, **updates)
#             else:
#                 await create_user(
#                     tg_id=tg_id,
#                     language='ru',
#                     phone=phone_clean,
#                     name=name
#                 )

#         lang = await get_user_language(message) or 'ru'
#         menu_kb = ReplyKeyboardMarkup(
#             keyboard=[
#                 [KeyboardButton(text=languages[lang]['menu'])]
#             ],
#             resize_keyboard=True
#         )
#         await message.answer(languages[lang]['thanks_for_phone'], reply_markup=menu_kb)
#         ikb = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text=languages[lang]['support'], callback_data='support')],
#                 [InlineKeyboardButton(text=languages[lang]['language_change'], callback_data='language_change')]
#             ]
#         )
#         await message.answer(languages[lang]['menu_activate'], reply_markup=ikb)
#         await state.clear()

#     except Exception as e:
#         print(f"Error in phone_state_handler: {e}")
#         lang = await get_user_language(message) or 'ru'
#         await message.answer(languages[lang]['error_occurred'])