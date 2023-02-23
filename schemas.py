from typing import List, Optional
from datetime import datetime, time
from pydantic import BaseModel, validator


class businessHours(BaseModel):
    day: int
    start_time_local: Optional[time] = None
    end_time_local: Optional[time] = None


class store(BaseModel):
    id: str
    local_timezone: Optional[str] = None
    schedule: Optional[List[businessHours]] = None

    class Config():
        orm_mode = True


class poll(BaseModel):
    id: str
    utc_timestamp: str | datetime
    status: str | int = "inactive"

    @validator("status", pre=True)
    def convert_to_int(cls, v):
        if v == "active":
            return 1
        else:
            return 0

    @validator("utc_timestamp", pre=True)
    def convert_datetime(cls, v):
        try:
            val = datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f %Z")
            return val
        except:
            raise ValueError("Invalid Time")
