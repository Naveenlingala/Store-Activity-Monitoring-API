from typing import List, Optional
from datetime import datetime, time, timedelta
from pydantic import BaseModel


class businessHours(BaseModel):
    day : int
    start_time_local : Optional[datetime] = None
    end_time_local : Optional[datetime] = None


class store(BaseModel):
    id: str
    local_timezone: str
    schedule: businessHours
