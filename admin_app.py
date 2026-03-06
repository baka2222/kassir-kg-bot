from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqladmin import Admin, ModelView
from database.engine import engine
from database.models.user_models import User
from database.models.answers_model import Answer, AnswerCategory
from database.models.operator_models import Operator, OperatorChat, ChatMessage, OperatorStatusEnum
from sqladmin.authentication import AuthenticationBackend
from sqladmin.filters import BooleanFilter, StaticValuesFilter
from starlette.requests import Request
from dotenv import load_dotenv
import os
from zoneinfo import ZoneInfo
from datetime import timezone
from wtforms import SelectField as Select


load_dotenv()

app = FastAPI()

SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
ADMIN_USERNAMES = os.getenv("ADMIN_USERNAMES", '').split(",")
ADMIN_PASSWORDS = os.getenv("ADMIN_PASSWORDS", '').split(",")
ADMIN_DICT = dict(zip(ADMIN_USERNAMES, ADMIN_PASSWORDS))

if len(ADMIN_USERNAMES) != len(ADMIN_PASSWORDS):
    raise ValueError("Number of usernames and passwords must match")
ADMIN_DICT = dict(zip(ADMIN_USERNAMES, ADMIN_PASSWORDS))


def format_bishkek(dt):
    if not dt:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(ZoneInfo("Asia/Bishkek")).strftime("%Y-%m-%d | %H:%M:%S")


@app.get("/admin/")
async def redirect_to_users():
    return RedirectResponse(url="/bot/admin/user/list")


class UserAdmin(ModelView, model=User):
    name = "Пользователи бота"
    name_plural = "Пользователи бота"

    column_list = [
        User.id,
        User.name,
        User.language,
        User.phone,
        User.tg_id,
        User.created_at,
        User.updated_at,
    ]

    column_labels = {
        User.id: 'ID',
        User.name: 'Имя',
        User.language: 'Язык',
        User.phone: 'Телефон',
        User.tg_id: 'Telegram ID',
        User.created_at: 'Дата создания',
        User.updated_at: 'Дата обновления',
    }

    column_formatters = {
        User.created_at: lambda obj, col: format_bishkek(obj.created_at),
        User.updated_at: lambda obj, col: format_bishkek(obj.updated_at),
    }

    column_formatters_detail = {
        User.created_at: lambda obj, col: format_bishkek(obj.created_at),
        User.updated_at: lambda obj, col: format_bishkek(obj.updated_at),
    }

    column_searchable_list = [User.name, User.phone, User.tg_id]


class AnswerAdmin(ModelView, model=Answer):
    name = "Ответы на вопросы"
    name_plural = "Ответы на вопросы"
    column_list = [Answer.id, Answer.question_en, Answer.question_ru, Answer.answer_en, Answer.answer_ru, Answer.answer_ky, Answer.question_ky, Answer.category]
    column_labels = {
        Answer.id: 'ID',
        Answer.question_en: 'Вопрос (EN)',
        Answer.question_ru: 'Вопрос (RU)',
        Answer.question_ky: 'Вопрос (KY)',
        Answer.answer_en: 'Ответ (EN)',
        Answer.answer_ru: 'Ответ (RU)',
        Answer.answer_ky: 'Ответ (KY)',
        Answer.category: 'Категория',
    }

    column_formatters = {
        Answer.category: lambda obj, col: f"📁 {obj.category.name_ru}" if obj.category else '❌ Без категории',
        Answer.question_ru: lambda obj, col: obj.question_ru[:50] + "..." if len(obj.question_ru) > 50 else obj.question_ru,
        Answer.answer_ru: lambda obj, col: obj.answer_ru[:50] + "..." if len(obj.answer_ru) > 50 else obj.answer_ru,
    }

    column_formatters_detail = {
        Answer.category: lambda obj, col: f"""
            <div style='padding: 10px; background: #f0f0f0; border-radius: 5px;'>
                <strong>ID:</strong> {obj.category.id}<br>
                <strong>RU:</strong> {obj.category.name_ru}<br>
                <strong>EN:</strong> {obj.category.name_en}<br>
                <strong>KY:</strong> {obj.category.name_ky}
            </div>
        """ if obj.category else 'Без категории',
    }

    column_searchable_list = [
        Answer.question_en, 
        Answer.question_ru, 
        Answer.question_ky, 
        Answer.answer_en, 
        Answer.answer_ru, 
        Answer.answer_ky
    ]
    

class AnswerCategoryAdmin(ModelView, model=AnswerCategory):
    name = "Категории ответов"
    name_plural = "Категории ответов"
    column_list = [AnswerCategory.id, AnswerCategory.name_en, AnswerCategory.name_ru, AnswerCategory.name_ky]
    column_labels = {
        AnswerCategory.id: 'ID',
        AnswerCategory.name_en: 'Название (EN)',
        AnswerCategory.name_ru: 'Название (RU)',
        AnswerCategory.name_ky: 'Название (KY)',
        AnswerCategory.answers: 'Ответы',
    }

    column_formatters_detail = {
        AnswerCategory.answers: lambda obj, col: [ans.question_ru for ans in obj.answers] if obj.answers else 'Нет ответов'
    }

    column_searchable_list = [AnswerCategory.name_en, AnswerCategory.name_ru, AnswerCategory.name_ky]

    form_excluded_columns = ["answers"]


class OperatorAdmin(ModelView, model=Operator):
    name = "Операторы"
    name_plural = "Операторы"
    form_excluded_columns = [
        "created_at", "updated_at", "active_chats", "total_chats"
    ]

    column_list = [
        Operator.id,
        Operator.name,
        Operator.tg_id,
        Operator.status,
        Operator.is_active,
        Operator.rating,
        Operator.active_chats,
        Operator.total_chats,
        Operator.max_concurrent_chats,
        Operator.created_at,
        Operator.updated_at,
    ]

    form_choices = {
        'status': [
            ('online', '🟢 Online'),
            ('break', '🟡 Break'),
            ('offline', '⚫ Offline'),
        ]
    }

    form_overrides = {
        'status': Select
    }
    
    form_args = {
        'status': {
            'choices': [
                ('online', '🟢 Online'),
                ('break', '🟡 Break'),
                ('offline', '⚫ Offline')
            ]
        }
    }

    column_labels = {
        Operator.id: 'ID',
        Operator.name: 'Имя',
        Operator.tg_id: 'Telegram ID',
        Operator.status: 'Статус',
        Operator.is_active: 'Активен',
        Operator.rating: 'Рейтинг',
        Operator.active_chats: 'Активные чаты',
        Operator.total_chats: 'Всего чатов',
        Operator.max_concurrent_chats: 'Макс. чатов',
        Operator.created_at: 'Создан',
        Operator.updated_at: 'Обновлён',
    }

    column_formatters = {
        Operator.status: lambda obj, col: {
            'online': '🟢 Online',
            'break': '🟡 Break',
            'offline': '⚫ Offline'
        }.get(obj.status, obj.status),
        Operator.rating: lambda obj, col: f"{obj.rating:.1f}⭐",
        Operator.is_active: lambda obj, col: '✅' if obj.is_active else '❌',
        Operator.created_at: lambda obj, col: format_bishkek(obj.created_at),
        Operator.updated_at: lambda obj, col: format_bishkek(obj.updated_at),
    }

    column_searchable_list = [Operator.name, Operator.tg_id]
    column_filters = [
        BooleanFilter(Operator.is_active, title="Активен", parameter_name="is_active"),
        StaticValuesFilter(
            Operator.status,
            values=[
                (OperatorStatusEnum.online.value, "🟢 Online"),
                (OperatorStatusEnum.break_.value, "🟡 Break"),
                (OperatorStatusEnum.offline.value, "⚫ Offline"),
            ],
            title="Статус",
            parameter_name="status",
        ),
    ]


class OperatorChatAdmin(ModelView, model=OperatorChat):
    name = "Чаты операторов"
    name_plural = "Чаты операторов"

    can_create = False
    can_edit = False
    # can_delete = False

    column_list = [
        OperatorChat.id,
        OperatorChat.user_id,
        OperatorChat.operator_id,
        OperatorChat.status,
        OperatorChat.user_rating,
        OperatorChat.messages_count,
        OperatorChat.started_at,
        OperatorChat.closed_at,
    ]

    column_labels = {
        OperatorChat.id: 'ID',
        OperatorChat.user_id: 'Пользователь (ID)',
        OperatorChat.operator_id: 'Оператор (ID)',
        OperatorChat.status: 'Статус',
        OperatorChat.user_rating: 'Оценка',
        OperatorChat.messages_count: 'Сообщений',
        OperatorChat.started_at: 'Начат',
        OperatorChat.closed_at: 'Закрыт',
    }

    column_searchable_list = [OperatorChat.status]


class ChatMessageAdmin(ModelView, model=ChatMessage):
    name = "Сообщения чатов"
    name_plural = "Сообщения чатов"

    can_create = False
    can_edit = False
    can_delete = False

    column_list = [
        ChatMessage.id,
        ChatMessage.chat_id,
        ChatMessage.sender_id,
        ChatMessage.message_type,
        ChatMessage.content,
        ChatMessage.is_read,
        ChatMessage.created_at,
    ]

    column_labels = {
        ChatMessage.id: 'ID',
        ChatMessage.chat_id: 'Чат',
        ChatMessage.sender_id: 'Отправитель',
        ChatMessage.message_type: 'Тип',
        ChatMessage.content: 'Текст',
        ChatMessage.is_read: 'Прочитано',
        ChatMessage.created_at: 'Время',
    }

    column_searchable_list = [ChatMessage.content]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if ADMIN_DICT.get(username) == password:
            request.session.update({"token": "ok"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        return request.session.pop("token", None) is not None

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") == "ok"


admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=SECRET_KEY), title='Админ-панель бота')
admin.add_view(UserAdmin)
admin.add_view(AnswerAdmin)
admin.add_view(AnswerCategoryAdmin)
admin.add_view(OperatorAdmin)
admin.add_view(OperatorChatAdmin)
admin.add_view(ChatMessageAdmin)