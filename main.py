from fastapi import FastAPI
from sqlalchemy.orm import Session
from config.database import SessionLocal

app = FastAPI(title="Colonia API Server")
def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()