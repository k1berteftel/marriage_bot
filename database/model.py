from typing import List
from datetime import datetime
from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(VARCHAR)
    name: Mapped[str] = mapped_column(VARCHAR)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    tokens: Mapped[int] = mapped_column(Integer, default=30)
    vip: Mapped[bool] = mapped_column(Boolean, default=False)
    super_vip: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=None, nullable=True)
    vip_end: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=None, nullable=True)
    entry: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.today())
    locale: Mapped[str] = mapped_column(VARCHAR, nullable=True)
    referral: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)  # реферал
    refs: Mapped[int] = mapped_column(BigInteger, default=0)  # Кол-во зашедших рефералов
    income: Mapped[int] = mapped_column(Integer, default=0)  # Общий доход с рефералов
    active: Mapped[int] = mapped_column(Integer, default=1)
    activity: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.today())
    block: Mapped[bool] = mapped_column(Boolean, default=False)


class FormTable(Base):
    __tablename__ = 'forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    name: Mapped[str] = mapped_column(VARCHAR)
    male: Mapped[str] = mapped_column(VARCHAR)
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(VARCHAR)
    profession: Mapped[str] = mapped_column(String)
    education: Mapped[str] = mapped_column(VARCHAR)
    income: Mapped[str] = mapped_column(VARCHAR)
    description: Mapped[str] = mapped_column(String)
    religion: Mapped[str] = mapped_column(VARCHAR)
    second_wife: Mapped[int] = mapped_column(Integer, default=None, unique=False, nullable=True)
    family: Mapped[str] = mapped_column(VARCHAR)
    photos: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), default=None, nullable=True)
    children_count: Mapped[str] = mapped_column(VARCHAR)
    children: Mapped[str] = mapped_column(VARCHAR)
    leave: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    boost: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=None, nullable=True)


class WatchesTable(Base):
    __tablename__ = 'watches'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    form_id: Mapped[int] = mapped_column(BigInteger)
    view: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.today())


class TransactionsTable(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    sum: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String, nullable=True)
    create: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.today())


class RequestsTable(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    sender: Mapped[int] = mapped_column(BigInteger)
    receiver: Mapped[int] = mapped_column(BigInteger)


class ComplainsTable(Base):
    __tablename__ = 'complains'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    form_user_id: Mapped[int] = mapped_column(BigInteger)
    complain: Mapped[str] = mapped_column(String)


class DeeplinksTable(Base):
    __tablename__ = 'deeplinks'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)
    entry: Mapped[int] = mapped_column(BigInteger, default=0)


class AdminsTable(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(VARCHAR)


class OneTimeLinksIdsTable(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)


class ImpressionsModelTable(Base):
    __tablename__ = 'impressions-models'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    male: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, nullable=True)
    max_age: Mapped[int] = mapped_column(Integer, nullable=True)
    city: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    profession: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    education: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    income: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    religion: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    family: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    children_count: Mapped[str] = mapped_column(VARCHAR, nullable=True)
    children: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=True)

    message_id: Mapped[int] = mapped_column(BigInteger)
    keyboard: Mapped[list[list[str]]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    from_chat_id: Mapped[int] = mapped_column(BigInteger)
    users: Mapped[List["UserImpressionsTable"]] = relationship('UserImpressionsTable', lazy="selectin", cascade='delete')


class UserImpressionsTable(Base):
    __tablename__ = 'user-impressions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    impression_id: Mapped[int] = mapped_column(ForeignKey('impressions-models.id'))
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    shown: Mapped[bool] = mapped_column(Boolean)


class OpTable(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(VARCHAR)
    link: Mapped[str] = mapped_column(VARCHAR)


class RatesTable(Base):
    __tablename__ = 'rates'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    amount: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)


class ApplicationsTable(Base):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    photos: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False)
    message_ids: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False)
