from .base import Base, Fileds
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Boolean, Float, BigInteger, DateTime, func, Text, Integer
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum


class OperatorStatusEnum(str, PyEnum):
    online = 'online'
    break_ = 'break'
    offline = 'offline'


class Operator(Base):
    __tablename__ = 'operators'

    id: Mapped[int] = Fileds.ID()
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        default=OperatorStatusEnum.offline.value,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    total_chats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_chats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_concurrent_chats: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = Fileds.CREATED_AT()
    updated_at: Mapped[datetime] = Fileds.UPDATED_AT()

    chats = relationship('OperatorChat', back_populates='operator', cascade='all, delete-orphan')

    @property
    def can_accept_chat(self) -> bool:
        return (self.is_active and 
                self.status == OperatorStatusEnum.online.value and 
                self.active_chats < self.max_concurrent_chats)

    def __str__(self) -> str:
        return f"Оператор {self.name} ({self.status}) - рейтинг {self.rating:.1f}⭐"


class OperatorChat(Base):
    __tablename__ = 'operator_chats'

    id: Mapped[int] = Fileds.ID()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id', ondelete='CASCADE'), nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)  
    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    messages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = Fileds.CREATED_AT()
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = Fileds.CREATED_AT()
    updated_at: Mapped[datetime] = Fileds.UPDATED_AT()

    user = relationship('User', foreign_keys=[user_id])
    operator = relationship('Operator', back_populates='chats')

    def __str__(self) -> str:
        return f"Чат #{self.id} - пользователь {self.user_id} <-> оператор {self.operator_id}"


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[int] = Fileds.ID()
    chat_id: Mapped[int] = mapped_column(ForeignKey('operator_chats.id', ondelete='CASCADE'), nullable=False)
    # sender_id may contain Telegram user IDs (big integers), use BigInteger
    sender_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default='text', nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = Fileds.CREATED_AT()

    def __str__(self) -> str:
        return f"Сообщение в чате {self.chat_id}: {self.content[:50]}..."
