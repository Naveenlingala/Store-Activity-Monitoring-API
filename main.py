from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas
import models
import pytz
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

app = FastAPI()

models.Base.metadata.create_all(engine)

# Valid Timezone


def is_valid_timezone(timezone):
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False


@app.put("/register_store")
def register_store(request: schemas.store,  db: Session = Depends(get_db)):
    store = models.Store(id=request.id)
    if is_valid_timezone(request.local_timezone):
        store.local_timezone = request.local_timezone

    # Schedule Iterator
    for weekday in request.schedule:
        if 0 <= weekday.day <= 6:
            week_day = models.BusinessHours(start_time_local=weekday.start_time_local,
                                            end_time_local=weekday.end_time_local, day=weekday.day)
            store.schedule.append(week_day)
            db.add(week_day)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Week Day")

    # Commit Model
    try:
        db.add(store)
        db.commit()
    except SQLAlchemyError as msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(msg.__dict__['orig']))
    return {"Message": "Store Added"}


def get_bussineess(db, store, day):
    try:
        business_hours_record = db.query(models.BusinessHours).options(joinedload(
            models.BusinessHours.store)).filter(models.BusinessHours.day == day).one()
    except:
        business_hours_record = models.BusinessHours(day=day)
        store.schedule.append(business_hours_record)
        db.add(business_hours_record)
        db.commit()
    return business_hours_record


@app.post("/poll/")
def poll(request: schemas.poll, db: Session = Depends(get_db)):
    store = db.query(models.Store).get(request.id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Store Id")
    # Convert UTC to local time zone
    local_timestamp = store.convert_to_local(request.utc_timestamp)

    if not store.week_info:
        week = models.Week(current_week=local_timestamp.date())
        db.add(week)
        store.week_info = week
        db.commit()
    # Create Day if Not Found
    if not store.day_info:
        day = models.Day(current_date=local_timestamp.date())
        db.add(day)
        store.day_info = day
        db.commit()

    store_previous_local_poll = store.previous_poll
    local_timestamp = local_timestamp.replace(tzinfo=None)

    if store_previous_local_poll >= local_timestamp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Timestamp must be greater than {store.previous_poll}")

    # Save TimeStamp
    try:
        hour = models.Hour(timestamp_local=local_timestamp,
                           status=request.status)
        db.add(hour)
        store.hour_info.append(hour)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Timestamp already found")
    # Adjust prev and current value
    store.week_info.adjust_week(local_timestamp)
    store.day_info.adjust_day(local_timestamp)
    db.commit()
    # Calculate
    # Get business object
    business_hours_record = get_bussineess(
        db, store, day=local_timestamp.weekday())

    if request.status == '1' and business_hours_record.check_time_in_busi(local_timestamp):
        difference_days = (local_timestamp.date() - store_previous_local_poll.date()).days # --- check for time
        # Check Difference between previous and current
        # # previous poll not on same day subtract from starting time
        # # 24/7 exception
        print(f'{local_timestamp} ---- {difference_days}')

        if difference_days == 0 or get_bussineess(db, store, day-1):
            uptime_duration = (local_timestamp - store_previous_local_poll)
        else:
            tmp_start_time = local_timestamp
            start_time_local = datetime.combine(
                tmp_start_time, business_hours_record.start_time_local)
            
            uptime_duration = local_timestamp - start_time_local
            

        store.day_info.current_day_uptime += uptime_duration
        store.week_info.current_week_uptime += uptime_duration

    # Update previous poll
    store.previous_poll = local_timestamp
    db.commit()
    # 2023-01-22 12:09:39.388884 UTC
    raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                        detail="Poll Sucessfull")
