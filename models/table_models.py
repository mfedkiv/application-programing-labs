from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, Column
from sqlalchemy import Integer, String, DateTime, ForeignKey
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt

from config.config import connection_string

engine = create_engine(connection_string)
Base = declarative_base()
Session = sessionmaker()
session = Session(bind=engine)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    events_host = relationship("Event", back_populates="user_owner")
    events_member = relationship("EventUsers", back_populates="user")
    calendar = relationship("Calendar", back_populates="user")

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.surname = kwargs.get('surname')
        self.username = kwargs.get('username')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=1):
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, username, password):
        user = session.query(User).filter_by(username=username).first()
        if not bcrypt.verify(password, user.password):
            return False
        return user

    def __repr__(self):
        return f"{self.id}, {self.name}, {self.surname}, {self.username}, {self.password}"


class Calendar(Base):
    __tablename__ = "calendar"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    events = relationship("CalendarEvents", back_populates="calendar")
    user = relationship("User", back_populates="calendar")

    def __repr__(self):
        return f"{self.id}, {self.title}, {self.user_id}"


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    owner = Column(Integer, ForeignKey("user.id"), nullable=False)

    user_owner = relationship("User", back_populates="events_host")
    calendars = relationship("CalendarEvents", back_populates="event")
    members = relationship("EventUsers", back_populates="event")

    def __repr__(self):
        return f"{self.id}, {self.title}, {self.date}, {self.owner}"


class EventUsers(Base):
    __tablename__ = "event_users"

    event_id = Column(Integer, ForeignKey("event.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    event = relationship("Event", back_populates="members")
    user = relationship("User", back_populates="events_member")

    def __repr__(self):
        return f"{self.event_id}, {self.user_id}"


class CalendarEvents(Base):
    __tablename__ = "calendar_events"

    calendar_id = Column(Integer, ForeignKey("calendar.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("event.id"), primary_key=True)

    calendar = relationship("Calendar", back_populates="events")
    event = relationship("Event", back_populates="calendars")

    def __repr__(self):
        return f"{self.calendar_id}, {self.event_id}"


class TokenBlockList(Base):
    __tablename__ = "token_block_list"

    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    created_at = Column(DateTime, nullable=False)
