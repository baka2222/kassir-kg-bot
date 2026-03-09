from .base import Base, Fileds
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from sqlalchemy import String, BigInteger
from datetime import datetime
from sqlalchemy.types import Enum as SQLAEnum
from enum import Enum as PyEnum


class LanguageEnum(str, PyEnum):
    ru = 'ru'
    en = 'en'
    ky = 'ky'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = Fileds.ID()
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    language: Mapped[LanguageEnum] = mapped_column(
        SQLAEnum(LanguageEnum, native_enum=False), 
        default=LanguageEnum.ru,
        nullable=False
    )
    created_at: Mapped[datetime] = Fileds.CREATED_AT()
    updated_at: Mapped[datetime] = Fileds.UPDATED_AT()

    def __str__(self) -> str:
        return f"Пользователь {self.name or self.phone} (номер: {self.phone}) - язык {self.language.value}"
