from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repository import (
    get_operator_by_tg_id, get_active_chats_by_operator, update_operator_status,
    get_operator_chat, save_chat_message, close_operator_chat, get_user_by_tg_id, get_chat_messages,
    get_active_chat_by_user
)
from aiogram.filters import Command
from languages import languages
from bot.bot import Bot
import html


operator_router = Router()


# FSM для обработки ответов оператора
class OperatorStates(StatesGroup):
    replying_to_chat = State()


# Главное меню оператора
async def show_operator_menu(chat_id: int, bot_obj=None, text_prefix: str = ""):
    """Показать главное меню оператора с кнопками"""
    menu_text = (
        f"{text_prefix}"
        f"🎛️ <b>Панель оператора</b>\n\n"
        f"Выберите действие:"
    )
    
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Мои чаты", callback_data='op_view_chats'),
                InlineKeyboardButton(text="📊 Статус", callback_data='op_status_menu')
            ],
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data='op_profile'),
                InlineKeyboardButton(text="❓ Справка", callback_data='op_help')
            ]
        ]
    )
    
    return menu_text, ikb


@operator_router.message(Command('operator_login'))
async def operator_login_redirect(message: Message):
    """Редирект на новое меню"""
    operator = await get_operator_by_tg_id(message.from_user.id)
    
    if not operator:
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Вы не зарегистрированы как оператор.\n"
            "Свяжитесь с администратором.",
            parse_mode="HTML"
        )
        return
    
    text, ikb = await show_operator_menu(message.chat.id)
    text = f"✅ <b>Добро пожаловать, {operator.name}!</b>\n\n" + text
    
    await message.answer(text, reply_markup=ikb, parse_mode="HTML")




@operator_router.message(F.command('operator_logout'))
async def operator_logout_handler(message: Message):
    operator = await get_operator_by_tg_id(message.from_user.id)
    
    if not operator:
        await message.answer("❌ Вы не зарегистрированы как оператор.")
        return
    
    await update_operator_status(operator, 'offline')
    await message.answer(
        "🔴 <b>Вы вышли из системы</b>\n\n"
        "Статус: <b>Offline</b>",
        parse_mode="HTML"
    )


# Меню выбора статуса
@operator_router.callback_query(F.data == 'op_status_menu')
async def operator_status_menu(callback_query: CallbackQuery):
    operator = await get_operator_by_tg_id(callback_query.from_user.id)
    
    if not operator:
        await callback_query.answer("❌ Оператор не найден.", show_alert=True)
        return
    
    status_icons = {
        'online': '🟢',
        'break': '🟡',
        'offline': '⚫'
    }
    
    current_status = status_icons.get(operator.status, '❓')
    
    text = (
        f"📊 <b>Выберите статус</b>\n\n"
        f"Текущий статус: {current_status} <b>{operator.status.upper()}</b>\n\n"
        f"<i>Когда вы Online, вам будут назначены новые чаты.</i>\n"
        f"<i>На Break вы не получите новых чатов.</i>\n"
        f"<i>Offline означает, что вы не доступны.</i>"
    )
    
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Online",
                    callback_data='op_set_status_online'
                ),
                InlineKeyboardButton(
                    text="🟡 Break",
                    callback_data='op_set_status_break'
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚫ Offline",
                    callback_data='op_set_status_offline'
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Назад",
                    callback_data='op_back_to_menu'
                )
            ]
        ]
    )
    
    await callback_query.message.delete()
    await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
    await callback_query.answer()


# Установка статуса
@operator_router.callback_query(F.data.startswith('op_set_status_'))
async def operator_set_status(callback_query: CallbackQuery):
    status = callback_query.data.split('_')[-1]
    operator = await get_operator_by_tg_id(callback_query.from_user.id)
    
    if not operator:
        await callback_query.answer("❌ Оператор не найден.", show_alert=True)
        return
    
    await update_operator_status(operator, status)
    
    status_messages = {
        'online': '✅ Вы теперь Online. Готовы принимать чаты!',
        'break': '⏸️ Вы на Break. Новые чаты не будут назначены.',
        'offline': '🔴 Вы Offline. Свяжитесь позже.'
    }
    
    await callback_query.answer(status_messages.get(status, "Статус изменён"), show_alert=True)
    
    # Вернуться в меню статуса
    await operator_status_menu(callback_query)


# Просмотр чатов
@operator_router.callback_query(F.data == 'op_view_chats')
async def operator_view_chats(callback_query: CallbackQuery):
    operator = await get_operator_by_tg_id(callback_query.from_user.id)
    
    if not operator:
        await callback_query.answer("❌ Оператор не найден.", show_alert=True)
        return
    
    chats = await get_active_chats_by_operator(operator.id)
    
    if not chats:
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Назад", callback_data='op_back_to_menu')]
            ]
        )
        await callback_query.message.delete()
        await callback_query.message.answer(
            "📭 <b>У вас нет активных чатов</b>\n\n"
            "Когда пользователи подключатся, они появятся здесь.",
            reply_markup=ikb,
            parse_mode="HTML"
        )
        await callback_query.answer()
        return
    
    text = f"📋 <b>Ваши активные чаты ({len(chats)})</b>\n\n"
    buttons = []
    
    for i, chat in enumerate(chats, 1):
        user = chat.user
        text += (
            f"<b>{i}. Чат #{chat.id}</b>\n"
            f"👤 {user.name or user.phone or 'Пользователь'}\n"
            f"📱 {user.phone or '—'}\n"
            f"💬 {chat.messages_count} сообщений\n\n"
        )
        
        buttons.append(
            InlineKeyboardButton(
                text=f"💬 Чат #{chat.id} ({user.name or 'Пользователь'})",
                callback_data=f'op_open_chat_{chat.id}'
            )
        )
    
    # Добавить кнопку назад
    buttons.append(InlineKeyboardButton(text="↩️ Назад", callback_data='op_back_to_menu'))
    
    ikb = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    await callback_query.message.delete()
    await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
    await callback_query.answer()



# Открыть чат
@operator_router.callback_query(F.data.startswith('op_open_chat_'))
async def operator_open_chat(callback_query: CallbackQuery, state: FSMContext):
    try:
        chat_id = int(callback_query.data.split('_')[-1])
        chat = await get_operator_chat(chat_id)
        
        if not chat:
            await callback_query.answer("❌ Чат не найден.", show_alert=True)
            return
        
        operator = await get_operator_by_tg_id(callback_query.from_user.id)
        if not operator or operator.id != chat.operator_id:
            await callback_query.answer("❌ Это не ваш чат.", show_alert=True)
            return
        
        messages = await get_chat_messages(chat_id, offset=0, limit=50)
        user = chat.user
        
        # Форматирование сообщений
        messages_text = ""
        if messages:
            for msg in messages:
                sender = "👤 Пользователь" if msg.sender_id == user.tg_id else "🎙️ Вы"
                timestamp = msg.created_at.strftime('%H:%M')
                if msg.message_type == 'photo':
                    content_display = "📷 Фото"
                else:
                    content_display = msg.content
                messages_text += f"{sender} [{timestamp}]: {content_display}\n"
        else:
            messages_text = "<i>Нет сообщений</i>"
        
        text = (
            f"💬 <b>Чат #{chat.id}</b>\n"
            f"👤 <b>{user.name or 'Неизвестный'}</b>\n"
            f"📱 {user.phone or '—'}\n"
            f"📍 Язык: {user.language.upper()}\n"
            f"⏰ Начат: {chat.started_at.strftime('%H:%M:%S')}\n"
            f"💬 Сообщений: {chat.messages_count}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>История:</b>\n\n"
            f"{messages_text}"
        )
        
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✍️ Ответить", callback_data=f'op_reply_chat_{chat.id}')],
                [InlineKeyboardButton(text="🔄 Обновить", callback_data=f'op_refresh_chat_{chat.id}')],
                [InlineKeyboardButton(text="❌ Закрыть чат", callback_data=f'op_close_chat_{chat.id}')],
                [InlineKeyboardButton(text="↩️ К чатам", callback_data='op_view_chats')]
            ]
        )
        
        # Сохраняем ID чата в состояние на случай если понадобится
        await state.update_data(current_chat_id=chat_id)
        
        await callback_query.message.delete()
        await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@operator_router.callback_query(F.data.startswith('op_refresh_chat_'))
async def operator_refresh_chat(callback_query: CallbackQuery, state: FSMContext):
    try:
        chat_id = int(callback_query.data.split('_')[-1])
        chat = await get_operator_chat(chat_id)
        if not chat:
            await callback_query.answer("❌ Чат не найден.", show_alert=True)
            return
        
        operator = await get_operator_by_tg_id(callback_query.from_user.id)
        if not operator or operator.id != chat.operator_id:
            await callback_query.answer("❌ Это не ваш чат.", show_alert=True)
            return
        
        # Получаем последние сообщения (например, последние 50)
        messages = await get_chat_messages(chat_id, offset=0, limit=50)
        user = chat.user
        
        # Формируем текст истории
        messages_text = ""
        if messages:
            for msg in messages:
                sender = "👤 Пользователь" if msg.sender_id == user.tg_id else "🎙️ Вы"
                timestamp = msg.created_at.strftime('%H:%M')
                if msg.message_type == 'photo':
                    content_display = "📷 Фото"
                else:
                    content_display = msg.content
                messages_text += f"{sender} [{timestamp}]: {content_display}\n"
        else:
            messages_text = "<i>Нет сообщений</i>"
        
        text = (
            f"💬 <b>Чат #{chat.id}</b>\n"
            f"👤 <b>{user.name or 'Неизвестный'}</b>\n"
            f"📱 {user.phone or '—'}\n"
            f"📍 Язык: {user.language.upper()}\n"
            f"⏰ Начат: {chat.started_at.strftime('%H:%M:%S')}\n"
            f"💬 Сообщений: {chat.messages_count}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>История:</b>\n\n"
            f"{messages_text}"
        )
        
        # Та же клавиатура, что и при открытии
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✍️ Ответить", callback_data=f'op_reply_chat_{chat.id}')],
                [InlineKeyboardButton(text="🔄 Обновить", callback_data=f'op_refresh_chat_{chat.id}')],
                [InlineKeyboardButton(text="❌ Закрыть чат", callback_data=f'op_close_chat_{chat.id}')],
                [InlineKeyboardButton(text="↩️ К чатам", callback_data='op_view_chats')]
            ]
        )
        
        await callback_query.message.delete()
        await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
        await callback_query.answer("✅ Чат обновлён")
    except Exception as e:
        await callback_query.answer(f"Изменений нет")


# Ответить на чат
@operator_router.callback_query(F.data.startswith('op_reply_chat_'))
async def operator_reply_chat(callback_query: CallbackQuery, state: FSMContext):
    try:
        chat_id = int(callback_query.data.split('_')[-1])
        
        # Сохраняем ID чата для дальнейшей обработки
        await state.set_state(OperatorStates.replying_to_chat)
        await state.update_data(reply_chat_id=chat_id)
        
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"✍️ <b>Введите ваше сообщение для чата #{chat_id}</b>\n\n"
            f"<i>Просто напишите сообщение текстом.</i>",
            parse_mode="HTML"
        )
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@operator_router.message(OperatorStates.replying_to_chat)
async def operator_send_reply(message: Message, state: FSMContext, bot: Bot):
    if message.photo:
        data = await state.get_data()
        chat_id = data.get('reply_chat_id')
        if not chat_id:
            await message.answer("❌ Ошибка: чат не найден.")
            await state.clear()
            return

        chat = await get_operator_chat(chat_id)
        if not chat or not chat.user:
            await message.answer("❌ Ошибка: чат или пользователь не найден.")
            await state.clear()
            return

        # Ограничение: только одно фото (не альбом)
        if message.media_group_id:
            await message.answer("❌ Пожалуйста, отправляйте по одному фото.")
            return
        
        photo_caption = message.caption or "📷 Фото"

        # Сохраняем запись о фото в БД
        await save_chat_message(
            chat_id=chat_id,
            sender_id=message.from_user.id,
            content="📷 Фото",
            message_type='photo'
        )

        # Отправляем фото пользователю
        file_id = message.photo[-1].file_id
        safe_caption = html.escape(photo_caption)
        await bot.send_photo(chat_id=chat.user.tg_id, photo=file_id, caption=safe_caption, parse_mode="HTML")

        await message.answer("✅ Фото отправлено пользователю.")
        await state.clear()

        # Кнопки для дальнейших действий
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💬 Вернуться к чату", callback_data=f'op_open_chat_{chat_id}')],
                [InlineKeyboardButton(text="📋 К списку чатов", callback_data='op_view_chats')]
            ]
        )
        await message.answer("Что дальше?", reply_markup=ikb)
    elif message.text:
        try:
            data = await state.get_data()
            chat_id = data.get('reply_chat_id')
            
            if not chat_id:
                await message.answer("❌ Ошибка: чат не найден.")
                await state.clear()
                return
            
            # Сохраняем сообщение в БД
            await save_chat_message(
                chat_id=chat_id,
                sender_id=message.from_user.id,
                content=message.text,
                message_type='text'
            )
            
            # Получаем чат с пользователем (убедитесь, что get_operator_chat загружает user)
            chat = await get_operator_chat(chat_id)
            if chat and chat.user:
                await bot.send_message(
                    chat_id=chat.user.tg_id,
                    text=f"{message.text}",
                    parse_mode="HTML"
                )
            else:
                # Логируем проблему – возможно, чат или пользователь не найдены
                print(f"Не удалось отправить сообщение: чат {chat_id} не имеет пользователя")
            
            # Подтверждение оператору
            await message.answer(
                f"✅ <b>Сообщение отправлено!</b>\n\n"
                f"Текст: <i>{message.text[:50]}{'...' if len(message.text) > 50 else ''}</i>",
                parse_mode="HTML"
            )
            
            await state.clear()
            
            ikb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💬 Вернуться к чату", callback_data=f'op_open_chat_{chat_id}')],
                    [InlineKeyboardButton(text="📋 К списку чатов", callback_data='op_view_chats')]
                ]
            )
            await message.answer("Что дальше?", reply_markup=ikb)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке сообщения: {str(e)}")
            await state.clear()
    else:
        await message.answer("❌ Поддерживаются только текстовые сообщения и фото.")
        return


@operator_router.callback_query(F.data.startswith('op_close_chat_'))
async def operator_close_chat(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        chat_id = int(callback_query.data.split('_')[-1])
        chat = await get_operator_chat(chat_id)
        
        if not chat:
            await callback_query.answer("❌ Чат не найден.", show_alert=True)
            return
        
        # Закрываем чат в БД
        closed_chat = await close_operator_chat(chat)
        
        # Сохраняем системное сообщение
        await save_chat_message(
            chat_id,
            callback_query.from_user.id,
            'Оператор закрыл чат',
            'system'
        )
        
        # Уведомляем пользователя, если чат ещё активен
        if chat and chat.user:
            try:
                await bot.send_message(
                    chat_id=chat.user.tg_id,
                    text="🔚 <b>Чат завершён</b>\n\nСпасибо за обращение! Если у вас остались вопросы, вы можете начать новый чат.",
                    parse_mode="HTML"
                )
                # Здесь можно добавить возврат в главное меню или предложение оценки
            except Exception as e:
                # Логируем ошибку, но не прерываем основной流程
                print(f"Не удалось уведомить пользователя {chat.user.tg_id}: {e}")
        
        # Уведомление оператору
        duration_minutes = (closed_chat.closed_at - closed_chat.started_at).total_seconds() / 60
        
        text = (
            f"✅ <b>Чат #{chat_id} закрыт</b>\n\n"
            f"⏱️ Продолжительность: {duration_minutes:.1f} мин\n"
            f"💬 Всего сообщений: {closed_chat.messages_count}\n\n"
            f"Спасибо за помощь пользователю!"
        )
        
        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📋 К списку чатов", callback_data='op_view_chats')],
                [InlineKeyboardButton(text="🏠 В главное меню", callback_data='op_back_to_menu')]
            ]
        )
        
        await callback_query.message.delete()
        await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
        await callback_query.answer("✅ Чат успешно закрыт.")
        
        # Очистить состояние
        await state.clear()
        
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# Профиль оператора
@operator_router.callback_query(F.data == 'op_profile')
async def operator_profile(callback_query: CallbackQuery):
    operator = await get_operator_by_tg_id(callback_query.from_user.id)
    
    if not operator:
        await callback_query.answer("❌ Оператор не найден.", show_alert=True)
        return
    
    status_icon = {
        'online': '🟢',
        'break': '🟡',
        'offline': '⚫'
    }.get(operator.status, '❓')
    
    text = (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"<b>Имя:</b> {operator.name}\n"
        f"<b>Telegram ID:</b> <code>{operator.tg_id}</code>\n"
        f"<b>Статус:</b> {status_icon} {operator.status.upper()}\n"
        f"<b>Рейтинг:</b> ⭐ {operator.rating:.1f}/5.0\n"
        f"<b>Активные чаты:</b> {operator.active_chats}/{operator.max_concurrent_chats}\n"
        f"<b>Всего чатов:</b> {operator.total_chats}\n"
        f"<b>Статус:</b> {'✅ Активен' if operator.is_active else '❌ Неактивен'}"
    )
    
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Назад", callback_data='op_back_to_menu')]
        ]
    )
    
    await callback_query.message.delete()
    await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
    await callback_query.answer()


# Справка
@operator_router.callback_query(F.data == 'op_help')
async def operator_help(callback_query: CallbackQuery):
    text = (
        "❓ <b>Справка для операторов</b>\n\n"
        "<b>Как это работает:</b>\n\n"
        "1️⃣ <b>Статус</b> - установите статус Online, чтобы принимать чаты\n"
        "2️⃣ <b>Чаты</b> - просматривайте список активных чатов\n"
        "3️⃣ <b>Ответы</b> - нажмите 'Ответить' и напишите своё сообщение\n"
        "4️⃣ <b>Закрытие</b> - кнопка 'Закрыть чат' завершает разговор\n\n"
        "<b>Советы:</b>\n"
        "• Регулярно проверяйте новые чаты\n"
        "• Обновляйте профиль в админ-панели\n"
        "• Ставьте правильный статус при перерывах\n"
        "• Будьте вежливы - это влияет на рейтинг\n\n"
        "<b>Команды:</b>\n"
        "/operator_login - Главное меню\n"
        "/operator_logout - Выход"
    )
    
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Назад", callback_data='op_back_to_menu')]
        ]
    )
    
    await callback_query.message.delete()
    await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
    await callback_query.answer()


# Кнопка "Назад" в главное меню
@operator_router.callback_query(F.data == 'op_back_to_menu')
async def operator_back_to_menu(callback_query: CallbackQuery):
    operator = await get_operator_by_tg_id(callback_query.from_user.id)
    
    if not operator:
        await callback_query.answer("❌ Оператор не найден.", show_alert=True)
        return
    
    text, ikb = await show_operator_menu(callback_query.message.chat.id)
    await callback_query.message.delete()
    await callback_query.message.answer(text, reply_markup=ikb, parse_mode="HTML")
    await callback_query.answer()


@operator_router.message(F.text)
async def handle_user_message(message: Message, bot: Bot):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        return  # пользователь не зарегистрирован

    # Проверяем, есть ли активный чат
    active_chat = await get_active_chat_by_user(user.id)
    if not active_chat:
        # Если нет активного чата, можно проигнорировать или отправить стандартный ответ
        return

    # Сохраняем сообщение в БД
    await save_chat_message(
        chat_id=active_chat.id,
        sender_id=message.from_user.id,
        content=message.text,
        message_type='text'
    )

    # Отправляем сообщение оператору
    operator = active_chat.operator
    if operator:
        await bot.send_message(
            chat_id=operator.tg_id,
            text=f"👤 <b>{user.name or user.phone or 'Пользователь'}:</b>\n{message.text}",
            parse_mode="HTML"
        )


@operator_router.message(F.photo)
async def handle_user_photo(message: Message, bot: Bot):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        return

    active_chat = await get_active_chat_by_user(user.id)
    if not active_chat:
        return

    # Ограничение: только одно фото
    if message.media_group_id:
        await message.answer("❌ Пожалуйста, отправляйте по одному фото.")
        return

    # Сохраняем запись в БД
    await save_chat_message(
        chat_id=active_chat.id,
        sender_id=message.from_user.id,
        content="📷 Фото",
        message_type='photo'
    )

    photo_caption = message.caption or "📷 Фото"

    # Отправляем фото оператору с подписью (имя пользователя)
    operator = active_chat.operator
    if operator:
        file_id = message.photo[-1].file_id

        safe_name = html.escape(user.name or user.phone or "Пользователь")
        safe_caption = html.escape(photo_caption)

        final_caption = f"👤 <b>{safe_name}:</b>\n{safe_caption}\n\nОТветьте юзеру - /operator_login" 

        await bot.send_photo(
            chat_id=operator.tg_id,
            photo=file_id,
            caption=final_caption,
            parse_mode="HTML"
        )