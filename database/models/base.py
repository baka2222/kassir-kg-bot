from sqlalchemy.orm import mapped_column, DeclarativeBase
from sqlalchemy import Integer, Identity
from sqlalchemy import func, DateTime


class Base(DeclarativeBase):
    pass


class Fileds:
    @staticmethod
    def ID():
        return mapped_column(Integer, Identity(always=True), primary_key=True)

    @staticmethod
    def CREATED_AT():
        return mapped_column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def UPDATED_AT():
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )