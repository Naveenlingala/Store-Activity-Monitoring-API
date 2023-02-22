from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, get_db
from sqlalchemy.orm import Session
import schemas
import models

app = FastAPI()

models.Base.metadata.create_all(engine)

print(schemas.store)

@app.post("/register_store", status_code=200)
def register_store(request: schemas.store,  db: Session = Depends(get_db)):

    return HTTPException(status_code=400, detail="Email already registered")
    # time = models.BusinessHours(request.)
    # store = models.Store(id="123456789")
    # store.schedule.append(time)
    # try:
    #     db.add(store)
    #     db.add(time)
    #     db.commit()
    # except:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    # return store
