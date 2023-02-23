from sqlalchemy import Column, Integer, String, Interval, text, Time, Date, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from database import Base
import pytz
from pytz import timezone
import datetime


class Store(Base):
    __tablename__ = "stores"
    id = Column(String, primary_key=True)
    schedule = relationship('BusinessHours', back_populates='store')
    local_timezone = Column(String, default="America/Chicago")
    hour_info = relationship('Hour', back_populates='store')
    day_info = relationship('Day', back_populates='store', uselist=False)
    week_info = relationship('Week', back_populates='store', uselist=False)
    previous_poll = Column(
        DateTime, default=datetime.datetime(1970, 1, 1, 0, 0, 0, 0))

    def convert_to_local(self, utc_time: DateTime) -> DateTime:
        local_timezone = pytz.timezone(self.local_timezone)
        local_timestamp = utc_time.replace(
            tzinfo=pytz.utc).astimezone(local_timezone)
        return local_timestamp

    def __repr__(self) -> str:
        return f'{self.id} {self.schedule}'


class Hour(Base):
    __tablename__ = "hour"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='hour_info')
    timestamp_local = Column(DateTime)
    my_index = Index('my_index', store_id, timestamp_local, unique=True)
    status = Column(Integer)


class Day(Base):
    __tablename__ = "day"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='day_info', uselist=False)

    current_date = Column(Date, nullable=False)
    current_day_uptime = Column(
        Interval, default=datetime.timedelta(minutes=0))
    previous_day_uptime = Column(
        Interval, default=datetime.timedelta(minutes=0))

    def adjust_day(self, local_timestamp):
        local_timestamp = local_timestamp.date()
        difference_days = (local_timestamp - self.current_date).days
        if difference_days == 1:
            self.previous_day_uptime = self.current_day_uptime
            self.current_day_uptime = datetime.timedelta(minutes=0)
            print("swap day")
        elif difference_days != 0:
            self.previous_day_uptime = datetime.timedelta(minutes=0)
            self.current_day_uptime = datetime.timedelta(minutes=0)

        self.current_date = local_timestamp


class Week(Base):
    __tablename__ = "Week"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='week_info', uselist=False)

    current_week = Column(Date, nullable=False)
    current_week_uptime = Column(
        Interval, default=datetime.timedelta(minutes=0))
    previous_week_uptime = Column(
        Interval, default=datetime.timedelta(minutes=0))

    def current_week_number(self) -> int:
        return self.current_week.isocalendar()[1]

    def adjust_week(self, local_timestamp):
        local_week_number = local_timestamp.isocalendar()[1]
        current_week_number = self.current_week_number()

        # check for previous week // New year edge case
        if local_week_number-1 == current_week_number or (current_week_number == 52 and local_week_number == 1 and local_timestamp.year == self.current_week.year + 1):
            self.previous_week_uptime = self.current_week_uptime
            self.current_week_uptime = datetime.timedelta(minutes=0)
            print("swap week")
        elif local_week_number != current_week_number:
            self.previous_week_uptime = datetime.timedelta(minutes=0)
            self.current_week_uptime = datetime.timedelta(minutes=0)

        self.current_week = local_timestamp.date()


class BusinessHours(Base):
    __tablename__ = "Business_Hours"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='schedule')

    # day_id = Column(String, unique=True, nullable=False)
    day = Column(Integer, nullable=False)
    day_id = Index('day_id', store_id, day, unique=True)

    start_time_local = Column(Time, default=text("'00:00:00'"))
    end_time_local = Column(Time, default=text("'23:59:59'"))

    def check_time_in_busi(self, local_timestamp):
        if self.start_time_local <= local_timestamp.time() <= self.end_time_local:
            return True
        else:
            return False

    def total_time(self):
        my_date = datetime.date.today()
        start = datetime.datetime.combine(my_date, self.start_time_local)
        end = datetime.datetime.combine(my_date, self.end_time_local)
        return (end - start)

    def __repr__(self) -> str:
        return f'{self.start_time_local} {self.end_time_local} {self.day}'
