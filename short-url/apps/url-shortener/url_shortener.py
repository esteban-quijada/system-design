import os
import secrets
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database setup
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ["POSTGRES_HOST"]
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ["POSTGRES_DB"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class URLRecord(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: Request, body: ShortenRequest):
    short_code = secrets.token_urlsafe(6)
    db: Session = SessionLocal()
    try:
        record = URLRecord(short_code=short_code, original_url=str(body.url))
        db.add(record)
        db.commit()
    finally:
        db.close()
    base_url = str(request.base_url)
    return ShortenResponse(
        short_code=short_code,
        short_url=f"{base_url}{short_code}",
    )


@app.get("/{short_code}")
def redirect_url(short_code: str):
    db: Session = SessionLocal()
    try:
        record = db.query(URLRecord).filter(URLRecord.short_code == short_code).first()
    finally:
        db.close()
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=record.original_url)
