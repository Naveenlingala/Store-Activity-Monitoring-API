from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, get_db
from sqlalchemy.orm import Session
import schemas
import models
import pytz
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

models.Base.metadata.create_all(engine)

# Valid Timezone 
def is_valid_timezone(timezone):
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False



@app.post("/register_store", status_code=status.HTTP_201_CREATED)
def register_store(request: schemas.store,  db: Session = Depends(get_db)):

    store = models.Store(id=request.id)

    if is_valid_timezone(request.local_timezone):
        store.local_timezone = request.local_timezone

    # Schedule Iterator
    for weekday in request.schedule:
        week_day = models.BusinessHours(start_time_local=weekday.start_time_local,
            end_time_local=weekday.end_time_local, day = weekday.day, day_id=f'{weekday.day} {request.id}')
        db.add(week_day)
        store.schedule.append(week_day)

    # Commit Model 
    try:
        db.add(store)
        db.commit()
    except SQLAlchemyError as msg:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = str(msg.__dict__['orig']))

    return {"Message": "Store Added"}
