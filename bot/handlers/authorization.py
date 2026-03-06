from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from languages import languages
from database.repository import get_user_language, create_user, edit_user, get_user_by_phone, get_user_by_tg_id


authorization_router = Router()


class AuthorizationState(StatesGroup):
    phone = State()


@authorization_router.message(Command('start'))
async def start_command_handler(message: Message, state: FSMContext):
    lang = await get_user_language(message)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=languages[lang]['send_phone'], request_contact=True)]
        ],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await message.answer(languages[lang]['greeting'], reply_markup=kb)
    await state.set_state(AuthorizationState.phone)


@authorization_router.message(AuthorizationState.phone)
async def phone_state_handler(message: Message, state: FSMContext):
    if not message.contact:
        lang = await get_user_language(message) or 'ru'
        await message.answer(languages[lang]['send_contact_please'])
        return

    if message.contact.user_id != message.from_user.id:
        lang = await get_user_language(message) or 'ru'
        await message.answer(languages[lang]['wrong_contact'])
        return

    phone = message.contact.phone_number
    phone_clean = phone.replace('+', '')
    tg_id = message.from_user.id
    name = message.from_user.full_name

    try:
        user_by_tg = await get_user_by_tg_id(tg_id=tg_id)
        user_by_phone = await get_user_by_phone(phone=phone_clean)

        if user_by_tg:
            updates = {}
            if (user_by_tg.phone or '') != phone_clean:
                updates['phone'] = phone_clean
            if (user_by_tg.name or '') != name:
                updates['name'] = name
            if updates:
                await edit_user(User=user_by_tg, **updates)
        else:
            if user_by_phone:
                updates = {}
                if user_by_phone.tg_id != tg_id:
                    updates['tg_id'] = tg_id
                if (user_by_phone.name or '') != name:
                    updates['name'] = name
                if updates:
                    await edit_user(User=user_by_phone, **updates)
            else:
                await create_user(
                    tg_id=tg_id,
                    language='ru',
                    phone=phone_clean,
                    name=name
                )

        lang = await get_user_language(message) or 'ru'
        menu_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=languages[lang]['menu'])]
            ],
            resize_keyboard=True
        )
        await message.answer(languages[lang]['thanks_for_phone'], reply_markup=menu_kb)
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=languages[lang]['support'], callback_data='support')],
                [InlineKeyboardButton(text=languages[lang]['language_change'], callback_data='language_change')]
            ]
        )
        await message.answer(languages[lang]['menu_activate'], reply_markup=ikb)
        await state.clear()

    except Exception as e:
        print(f"Error in phone_state_handler: {e}")
        lang = await get_user_language(message) or 'ru'
        await message.answer(languages[lang]['error_occurred'])