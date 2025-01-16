from datetime import datetime
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, CheckConstraint, Select, Text
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from pprint import pprint


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    lang: Mapped[str] = mapped_column(Text())
    utc: Mapped[int] = mapped_column(Integer(), nullable=True)
    # state: Mapped[str] = mapped_column(Text(), nullable=True)
    locals: Mapped[List["Delayed"]] = relationship(
        back_populates="delayed_messages",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, lang={self.lang!r}, utc={self.utc!r}, state={self.state!r}, locals={self.locals!r})"


class Delayed(Base):
    __tablename__ = "delayed"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(Text())
    tp: Mapped[int] = mapped_column(Integer())
    time: Mapped[str] = mapped_column(Text())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delayed_messages: Mapped["User"] = relationship(back_populates="locals")


class Users:
    def __init__(self, engine, session):
        self.menu_keyboard = dict()
        self.notif_keyboard = dict()
        # self.state_data = dict()
        self.engine = engine
        self.session = session

    def add_user(self, uid_: int, lang_: str, utc_=0):
        us = User(
            id=uid_,
            lang=lang_,
            utc=utc_
        )
        a = self[uid_]
        if a is None:
            self.session.add(us)
        else:
            a.id = uid_
            a.lang = lang_
            a.utc = utc_
            # a.state = state

        self.session.commit()

    def __getitem__(self, uid):
        return self.session.get(User, uid)

    def add_delayed_message(self, uid, city, tp, tm):
        dl = Delayed(
            city=city,
            tp=tp,
            user_id=uid,
            time=tm
        )
        if len(list(self.session.scalars(
                Select(Delayed)
                        .where(Delayed.user_id == uid)
                        .where(Delayed.city == city)
                        .where(Delayed.tp == tp)
                        .where(Delayed.time == tm)))) == 0:
            self.session.add(dl)
        self.session.commit()

    def del_user(self, uid):
        self.session.delete(self.session.get(User, uid))
        self.session.commit()

    def del_delayed(self, del_id):
        self.session.delete(self.session.get(Delayed, del_id))
        self.session.commit()

    def get_all_delayed_for_time(self, tm):
        return list(self.session.scalars(Select(Delayed).where(Delayed.time == tm)))

    def get_all_delayed_for_us(self, uid):
        return list(self.session.scalars(Select(Delayed).where(Delayed.user_id == uid)))

    def commit(self):
        self.session.commit()


if __name__ == '__main__':
    engine = create_engine(f"sqlite:///{'users.db'}", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        users = Users(engine, session)
        users.add_user(1, "rr")
        users[1].state = "hello"
        session.commit()
        users[1].state = "hello2"
        print(users[1].state)
        users[1].state = "hello3"
