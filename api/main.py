from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from auth import hash_password
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuVision")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(
    "/auth/register",
    response_model = schemas.UserOut,
    status_code = status.HTTP_201_CREATED,
)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.User).where(models.User.email == user_in.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = models.User(
        email = user_in.email,
        password_hash = hash_password(user_in.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user