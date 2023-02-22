from typing import List, Optional
from datetime import datetime, time, timedelta
from pydantic import BaseModel


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
