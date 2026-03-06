from aiogram_widgets.pagination import KeyboardPaginator
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram import F
from database.repository import (
    get_user_language, get_answer_by_id, list_categories, list_answer_by_category,
    get_best_available_operator, get_user_by_tg_id, create_operator_chat,
    get_active_chat_by_user, save_chat_message, close_operator_chat
)
from aiogram_widgets.pagination import KeyboardPaginator
from languages import languages
from bot.bot import bot


help_router = Router()


@help_router.callback_query(F.data == 'support')
async def support_handler(callback_query: CallbackQuery):
    lang = await get_user_language(callback_query)
    categories = await list_categories()
    
    buttons = [
        InlineKeyboardButton(
            text=cat.name_ru if lang == 'ru' else cat.name_en if lang == 'en' else cat.name_ky,
            callback_data=f'support_category_{cat.id}'
        )
        for cat in categories
    ]

    if not buttons:
        await callback_query.message.edit_text(languages[lang]['not_exist_category'])
        await callback_query.answer()
        return

    buttons.append(
        InlineKeyboardButton(
            text=languages[lang]['connect_operator'],
            callback_data='connect_operator'
        )
    )

    paginator = KeyboardPaginator(
        router=help_router,
        data=buttons,     
        per_page=5,    
        per_row=1   
    )

    await callback_query.message.edit_text(languages[lang]['what_is_your_answer_cat'], reply_markup=paginator.as_markup())
    await callback_query.answer()


@help_router.callback_query(F.data.startswith('support_category_'))
async def support_category_handler(callback_query: CallbackQuery):
    category_id = callback_query.data.split('_')[-1]
    lang = await get_user_language(callback_query)
    answers = await list_answer_by_category(category_id=int(category_id))

    if not answers:
        await callback_query.message.edit_text(languages[lang]['not_exist_answer'])
        await callback_query.answer()
        return
    
    buttons = [
        InlineKeyboardButton(
            text=ans.question_ru if lang == 'ru' else ans.question_en if lang == 'en' else ans.question_ky,
            callback_data=f'support_answer_{ans.id}'
        )
        for ans in answers
    ]

    buttons.append(
        InlineKeyboardButton(
            text=languages[lang]['connect_operator'],
            callback_data='connect_operator'
        )
    )

    paginator = KeyboardPaginator(
        router=help_router,
        data=buttons,     
        per_page=5,    
        per_row=1   
    )

    await callback_query.message.edit_text(languages[lang]['what_is_your_question'], reply_markup=paginator.as_markup())
    await callback_query.answer()


@help_router.callback_query(F.data.startswith('support_answer_'))
async def support_answer_handler(callback_query: CallbackQuery):
    answer_id = callback_query.data.split('_')[-1]
    lang = await get_user_language(callback_query)
    answer = await get_answer_by_id(answer_id=int(answer_id))

    if not answer:
        await callback_query.message.edit_text(languages[lang]['not_exist_answer'])
        await callback_query.answer()
        return
    
    answer_text = answer.answer_ru if lang == 'ru' else answer.answer_en if lang == 'en' else answer.answer_ky
    
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=languages[lang]['helpful'], callback_data='helpful_answer')
            ], 
            [
                InlineKeyboardButton(text=languages[lang]['not_helpful'], callback_data='connect_operator')
            ]
        ]
    )
    
    await callback_query.message.answer(answer_text)
    await callback_query.message.answer(languages[lang]['is_this_helpful'], reply_markup=ikb)
    await callback_query.answer()


@help_router.callback_query(F.data == 'helpful_answer')
async def helpful_answer_handler(callback_query: CallbackQuery):
    """Пользователь сказал, что ответ был полезен"""
    lang = await get_user_language(callback_query)
    await callback_query.message.delete()
    await callback_query.answer()


@help_router.callback_query(F.data == 'connect_operator')
async def connect_operator_handler(callback_query: CallbackQuery):
    """Подключить пользователя к оператору"""
    user = await get_user_by_tg_id(callback_query.from_user.id)
    lang = await get_user_language(callback_query)
    
    if not user:
        await callback_query.answer(languages[lang]['user_not_found'], show_alert=True)
        return
    
    active_chat = await get_active_chat_by_user(user.id)
    if active_chat:
        await callback_query.message.edit_text(
            f"⚠️ <b>{languages[lang]['active_chat_exists']}</b>\n\n"
            f"{languages[lang]['please_finish_current_chat']}",
            parse_mode="HTML"
        )
        await callback_query.answer()
        return
    
    best_operator = await get_best_available_operator()
    
    if best_operator:
        chat = await create_operator_chat(user.id, best_operator.id)
        await save_chat_message(
            chat.id,
            callback_query.from_user.id,
            f'Пользователь {user.name or user.phone} подключился к чату',
            'system'
        )
        
        await callback_query.message.edit_text(
            f"✅ <b>{languages[lang]['operator_found_success']}</b>\n\n"
            f"👤 <b>{best_operator.name}</b>\n"
            f"⭐ {languages[lang]['operator_rating']} {best_operator.rating:.1f}/5.0\n\n"
            f"{languages[lang]['waiting_operator_message']}",
            parse_mode="HTML"
        )

        await bot.send_message(
            best_operator.tg_id,
            f"📞 Новый чат с пользователем {user.name or user.phone}\n"
            f"📱 Телефон: <a href='tel:{user.phone}'>{user.phone}</a>\n"
            f"Пожалуйста, начните разговор, отправив сообщение в этот чат.\n"
            f"Для просмотра чатов введите /operator_login",
            parse_mode="HTML"
        )
        
        await callback_query.answer()
    else:
        await callback_query.message.edit_text(
            f"⏳ <b>{languages[lang]['all_operators_busy']}</b>\n\n"
            f"{languages[lang]['request_in_queue']}\n\n"
            f"{languages[lang]['try_later']}",
            parse_mode="HTML"
        )
        
        await callback_query.answer()
