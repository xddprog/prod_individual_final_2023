from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nickname: Mapped[str]
    age: Mapped[int]
    description: Mapped[str] = mapped_column(Text)
    country: Mapped[str]
    city: Mapped[str]
    full_address: Mapped[str]

    travels: Mapped[list['Travel']] = relationship(
        back_populates='users',
        uselist=True,
        secondary='user_travels',
        lazy="selectin"
    )


class UserTravel(Base):
    __tablename__ = 'user_travels'
    user_fk: Mapped[str] = mapped_column(ForeignKey('users.user_id'), primary_key=True)
    travel_fk: Mapped[str] = mapped_column(ForeignKey('travels.travel_id'), primary_key=True)


class Travel(Base):
    __tablename__ = 'travels'
    travel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    travel_mode: Mapped[str]
    name: Mapped[str]
    description: Mapped[str] = mapped_column(Text)

    points: Mapped[list['Point']] = relationship(back_populates='', uselist=True, lazy="selectin")
    notes: Mapped[list['Note']] = relationship(back_populates='', uselist=True, lazy="selectin")
    users: Mapped[list['User']] = relationship(
        back_populates='travels',
        uselist=True,
        secondary='user_travels',
        lazy="selectin"
    )


class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    address: Mapped[str]
    travel_fk: Mapped['Travel'] = mapped_column(ForeignKey('travels.travel_id'))

    travel: Mapped['Travel'] = relationship(back_populates='points', uselist=False, lazy="selectin")


class Note(Base):
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(BigInteger)
    author_name: Mapped[str]
    is_private: Mapped[bool]
    name: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    file_id: Mapped[str] = mapped_column(nullable=True)
    created_date: Mapped[datetime]
    content_type: Mapped[str]

    travel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('travels.travel_id'))
    travel_note: Mapped['Travel'] = relationship(back_populates='notes', uselist=False)
