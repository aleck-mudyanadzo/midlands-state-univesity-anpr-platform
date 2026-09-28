from fastapi import FastAPI, Depends
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.core.database import get_db

app = FastAPI(title="MSU ANPR Platform API")


@app.get("/")
def root():
    return {"status": "ok", "service": "MSU ANPR Platform API"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    table_names = inspect(db.get_bind()).get_table_names()
    return {"status": "connected", "tables_found": len(table_names)}