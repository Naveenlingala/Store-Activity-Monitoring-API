from sqlalchemy import Column, Integer, String, Time, text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import schemas


class Store(Base):
    __tablename__ = "stores"
    id = Column(String, primary_key=True)
    schedule = relationship('BusinessHours', back_populates='store')
    local_timezone  = Column(String, default="America/Chicago")
    hour_info = relationship('Hour', back_populates='store')
    day_info = relationship('Day', back_populates='store')
    week_info = relationship('Week', back_populates='store')

    def __repr__(self) -> str:
        return f'{self.id} {self.schedule}'



class Hour(Base):
    __tablename__ = "hour"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))

    store = relationship('Store', back_populates='hour_info')
    timestamp_local = Column(DateTime)
    status = Column(Integer)

class Day(Base):
    __tablename__ = "day"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='day_info')

    current_date = Column(Date, nullable=False)
    current_day_uptime = Column(DateTime)
    previous_day_uptime = Column(DateTime)

class Week(Base):
    __tablename__ = "Week"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='week_info')

    current_week = Column(Date, nullable=False)
    current_week_uptime = Column(DateTime)
    previous_week_uptime = Column(DateTime)


class BusinessHours(Base):
    __tablename__ = "Business_Hours"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='schedule')
    
    day_id = Column(String, unique=True, nullable=False)
    day = Column(Integer, nullable=False)
    start_time_local = Column(Time, default=text("'00:00:00'"))
    end_time_local = Column(Time, default=text("'23:59:59'"))

    def total_time(self):
        return self.end_time_local - self.start_time_local
    
    def __repr__(self) -> str:
        return f'{self.start_time_local} {self.end_time_local} {self.day}'
    