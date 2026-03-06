from .engine import async_session
from .models.user_models import User
from .models.answers_model import AnswerCategory, Answer
from .models.operator_models import Operator, OperatorChat, ChatMessage, OperatorStatusEnum
from sqlalchemy import select, or_, and_, update, desc, func
from aiogram.types import Message, CallbackQuery
from typing import Optional, List
from sqlalchemy.orm import joinedload
from utils.dt import now_utc


async def get_user_language(message: Optional[Message] | Optional[CallbackQuery]) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalars().first()
        if user and user.language:
            lang = user.language
        else:
            lang = 'ru'
    return lang


async def edit_user(User: User, **kwargs):
    async with async_session() as session:
        for key, value in kwargs.items():
            setattr(User, key, value)
        session.add(User)
        await session.commit()


async def get_user_by_tg_id(tg_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalars().first()
    

async def get_user_by_phone(phone: str) -> Optional[User]:
    phone = phone.replace('+', '')
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalars().first()
    

async def create_user(**kwargs) -> User:
    async with async_session() as session:
        new_user = User(**kwargs)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    

async def create_category(name_ru: str, name_en: str, name_ky: str) -> AnswerCategory:
    async with async_session() as session:
        new_cat = AnswerCategory(
            name_ru=name_ru,
            name_en=name_en,
            name_ky=name_ky
        )
        session.add(new_cat)
        await session.commit()
        await session.refresh(new_cat)
        return new_cat


async def get_category_by_id(category_id: int) -> Optional[AnswerCategory]:
    async with async_session() as session:
        result = await session.execute(select(AnswerCategory).where(AnswerCategory.id == category_id))
        return result.scalars().first()


async def get_category_by_name(name: str, lang: str = 'ru') -> Optional[AnswerCategory]:
    column = {
        'ru': AnswerCategory.name_ru,
        'en': AnswerCategory.name_en,
        'ky': AnswerCategory.name_ky
    }.get(lang, AnswerCategory.name_ru)

    async with async_session() as session:
        result = await session.execute(select(AnswerCategory).where(column == name))
        return result.scalars().first()


async def list_categories(offset: int = 0, limit: int = 100) -> List[AnswerCategory]:
    async with async_session() as session:
        result = await session.execute(select(AnswerCategory).offset(offset).limit(limit))
        return result.scalars().all()
    

async def list_answer_by_category(category_id: int, offset: int = 0, limit: int = 100) -> List[Answer]:
    async with async_session() as session:
        result = await session.execute(
            select(Answer).where(Answer.category_id == category_id).offset(offset).limit(limit)
        )
        return result.scalars().all()


async def update_category(category: AnswerCategory, **kwargs) -> AnswerCategory:
    async with async_session() as session:
        for key, value in kwargs.items():
            setattr(category, key, value)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


async def delete_category(category: AnswerCategory) -> None:
    async with async_session() as session:
        await session.delete(category)
        await session.commit()


async def create_answer(
    question_ru: str,
    question_en: str,
    question_ky: str,
    answer_ru: str,
    answer_en: str,
    answer_ky: str,
    category_id: int
) -> Answer:
    async with async_session() as session:
        new_answer = Answer(
            question_ru=question_ru,
            question_en=question_en,
            question_ky=question_ky,
            answer_ru=answer_ru,
            answer_en=answer_en,
            answer_ky=answer_ky,
            category_id=category_id
        )
        session.add(new_answer)
        await session.commit()
        await session.refresh(new_answer)
        return new_answer


async def get_answer_by_id(answer_id: int) -> Optional[Answer]:
    async with async_session() as session:
        result = await session.execute(select(Answer).where(Answer.id == answer_id))
        return result.scalars().first()


async def list_answers(offset: int = 0, limit: int = 100) -> List[Answer]:
    async with async_session() as session:
        result = await session.execute(select(Answer).offset(offset).limit(limit))
        return result.scalars().all()


async def get_answers_by_category(category_id: int, offset: int = 0, limit: int = 100) -> List[Answer]:
    async with async_session() as session:
        result = await session.execute(
            select(Answer).where(Answer.category_id == category_id).offset(offset).limit(limit)
        )
        return result.scalars().all()


async def search_answers(query: str, offset: int = 0, limit: int = 50) -> List[Answer]:
    q = f"%{query}%"
    async with async_session() as session:
        stmt = select(Answer).where(
            or_(
                Answer.question_ru.ilike(q),
                Answer.question_en.ilike(q),
                Answer.question_ky.ilike(q),
                Answer.answer_ru.ilike(q),
                Answer.answer_en.ilike(q),
                Answer.answer_ky.ilike(q),
            )
        ).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()


async def update_answer(answer: Answer, **kwargs) -> Answer:
    async with async_session() as session:
        for key, value in kwargs.items():
            setattr(answer, key, value)
        session.add(answer)
        await session.commit()
        await session.refresh(answer)
        return answer


async def delete_answer(answer: Answer) -> None:
    async with async_session() as session:
        await session.delete(answer)
        await session.commit()


async def create_operator(tg_id: int, name: str, bio: str = '') -> Operator:
    async with async_session() as session:
        new_operator = Operator(
            tg_id=tg_id,
            name=name,
            bio=bio
        )
        session.add(new_operator)
        await session.commit()
        await session.refresh(new_operator)
        return new_operator


async def get_operator_by_tg_id(tg_id: int) -> Optional[Operator]:
    async with async_session() as session:
        result = await session.execute(
            select(Operator).where(Operator.tg_id == tg_id)
        )
        return result.scalars().first()


async def get_operator_by_id(operator_id: int) -> Optional[Operator]:
    async with async_session() as session:
        result = await session.execute(
            select(Operator).where(Operator.id == operator_id)
        )
        return result.scalars().first()


async def get_available_operators() -> List[Operator]:
    async with async_session() as session:
        result = await session.execute(
            select(Operator)
            .where(
                and_(
                    Operator.is_active == True,
                    Operator.status == OperatorStatusEnum.online.value,
                    Operator.active_chats < Operator.max_concurrent_chats
                )
            )
            .order_by(desc(Operator.rating), Operator.active_chats)
        )
        return result.scalars().all()


async def get_best_available_operator() -> Optional[Operator]:
    operators = await get_available_operators()
    return operators[0] if operators else None


async def update_operator_status(operator: Operator, status: str) -> Operator:
    async with async_session() as session:
        operator_obj = await session.merge(operator)
        operator_obj.status = status
        await session.commit()
        await session.refresh(operator_obj)
        return operator_obj


async def update_operator(operator: Operator, **kwargs) -> Operator:
    async with async_session() as session:
        operator_obj = await session.merge(operator)
        for key, value in kwargs.items():
            setattr(operator_obj, key, value)
        await session.commit()
        await session.refresh(operator_obj)
        return operator_obj


async def list_operators(offset: int = 0, limit: int = 100) -> List[Operator]:
    async with async_session() as session:
        result = await session.execute(
            select(Operator).offset(offset).limit(limit)
        )
        return result.scalars().all()


async def create_operator_chat(user_id: int, operator_id: int) -> OperatorChat:
    async with async_session() as session:
        new_chat = OperatorChat(
            user_id=user_id,
            operator_id=operator_id,
            status='active'
        )
        session.add(new_chat)
        await session.commit()
        await session.refresh(new_chat)
        
        operator = await get_operator_by_id(operator_id)
        if operator:
            await update_operator(
                operator,
                total_chats=operator.total_chats + 1,
                active_chats=operator.active_chats + 1
            )
        
        return new_chat


async def get_operator_chat(chat_id: int) -> Optional[OperatorChat]:
    async with async_session() as session:
        stmt = (
            select(OperatorChat)
            .options(joinedload(OperatorChat.user))
            .where(OperatorChat.id == chat_id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none() 


async def get_active_chat_by_user(user_id: int) -> Optional[OperatorChat]:
    async with async_session() as session:
        result = await session.execute(
            select(OperatorChat)
            .options(joinedload(OperatorChat.operator))
            .where(
                and_(
                    OperatorChat.user_id == user_id,
                    OperatorChat.status == 'active'
                )
            )
            .order_by(desc(OperatorChat.created_at))
        )
        return result.scalars().first()


async def get_active_chats_by_operator(operator_id: int) -> List[OperatorChat]:
    async with async_session() as session:
        result = await session.execute(
            select(OperatorChat)
            .options(joinedload(OperatorChat.user))  # <-- подгружаем пользователя
            .where(
                and_(
                    OperatorChat.operator_id == operator_id,
                    OperatorChat.status == 'active'
                )
            )
            .order_by(desc(OperatorChat.last_message_at))
        )
        return result.unique().scalars().all()


async def close_operator_chat(chat: OperatorChat, user_rating: Optional[int] = None) -> OperatorChat:
    async with async_session() as session:
        chat_obj = await session.merge(chat)
        chat_obj.status = 'closed'
        chat_obj.closed_at = now_utc()
        if user_rating:
            chat_obj.user_rating = user_rating
        await session.commit()
        await session.refresh(chat_obj)
        
        operator = await get_operator_by_id(chat_obj.operator_id)
        if operator and operator.active_chats > 0:
            new_active = operator.active_chats - 1
            update_data = {'active_chats': new_active}
            
            if user_rating:
                chats = await get_closed_chats_by_operator(chat_obj.operator_id)
                if chats:
                    all_ratings = [c.user_rating or 5 for c in chats] + [user_rating]
                    new_rating = sum(all_ratings) / len(all_ratings)
                    update_data['rating'] = new_rating
            
            await update_operator(operator, **update_data)
        
        return chat_obj



async def get_closed_chats_by_operator(operator_id: int) -> List[OperatorChat]:
    async with async_session() as session:
        result = await session.execute(
            select(OperatorChat).where(
                and_(
                    OperatorChat.operator_id == operator_id,
                    OperatorChat.status == 'closed'
                )
            )
        )
        return result.scalars().all()


async def save_chat_message(chat_id: int, sender_id: int, content: str, message_type: str = 'text') -> ChatMessage:
    async with async_session() as session:
        new_message = ChatMessage(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type
        )
        session.add(new_message)
        
        chat = await session.get(OperatorChat, chat_id)
        if chat:
            chat.last_message_at = now_utc()
            chat.messages_count += 1
        
        await session.commit()
        await session.refresh(new_message)
        return new_message


async def get_chat_messages(chat_id: int, offset: int = 0, limit: int = 50) -> List[ChatMessage]:
    async with async_session() as session:
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
