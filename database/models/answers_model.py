from .base import Base, Fileds
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, ForeignKey 


class AnswerCategory(Base):
    __tablename__ = 'answer_categories'

    id: Mapped[int] = Fileds.ID()
    name_ru: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_ky: Mapped[str] = mapped_column(String(50), nullable=False)

    answers = relationship('Answer', back_populates='category') 

    def __str__(self) -> str:
        return f"Категория - {self.name_ru}"


class Answer(Base):
    __tablename__ = 'answers'

    id: Mapped[int] = Fileds.ID()
    question_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    question_en: Mapped[str] = mapped_column(String(255), nullable=False)
    question_ky: Mapped[str] = mapped_column(String(255), nullable=False)
    answer_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    answer_en: Mapped[str] = mapped_column(String(255), nullable=False)
    answer_ky: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('answer_categories.id', ondelete='CASCADE'), nullable=False)

    category = relationship('AnswerCategory', back_populates='answers')

    def __str__(self) -> str:
        return f"Ответ - {self.question_ru[:60]}..."